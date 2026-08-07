import logging
import os
from pathlib import Path

from infrastructure.storage.retry import with_retry

log = logging.getLogger(__name__)


# Errores transitorios sobre los que vale reintentar. Errores 4xx
# (404, 403, etc.) y FileNotFoundError NO son transitorios.
_RETRYABLE = (ConnectionError, TimeoutError, OSError)


def _is_404(e: BaseException) -> bool:
    """Detecta un 404 del SDK de OCI (status 404 o 'NotFound')."""
    msg = str(e).lower()
    return "404" in msg or "notfound" in msg or "not found" in msg


class OciBucketStorage:
    """OCI Object Storage backed by oci-python-sdk (official Oracle SDK).

    Soporta 3 métodos de auth (en orden de prioridad de _get_client):
    1. OCI_INSTANCE_PRINCIPAL=true (en VM OCI: sin credenciales, recomendado)
    2. OCI_CONFIG_FILE path explícito (CI runners / bastion con config local)
    3. API key via env vars OCI_USER_OCID, OCI_TENANCY_OCID, OCI_FINGERPRINT,
       OCI_PRIVATE_KEY_PATH o OCI_PRIVATE_KEY_CONTENT

    Requiere env vars:
        OCI_NAMESPACE  (Object Storage namespace, ej. 'sergiovillenavergara')
        OCI_BUCKET     (nombre del bucket, ej. 'g9-energy-test-bucket')
        OCI_REGION     (ej. 'santiago-chile-1')
    """

    def __init__(
        self,
        namespace: str | None = None,
        bucket: str | None = None,
        region: str | None = None,
    ):
        missing = []
        self.namespace = namespace or os.environ.get("OCI_NAMESPACE")
        if not self.namespace:
            missing.append("OCI_NAMESPACE")
        self.bucket = bucket or os.environ.get("OCI_BUCKET", "g9-energy-test-bucket")
        self.region = region or os.environ.get("OCI_REGION", "santiago-chile-1")
        if missing:
            raise RuntimeError(
                f"OCI storage requires env vars: {', '.join(missing)}. "
                "Definilas en .env o como variables de entorno."
            )

        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client

        import oci

        config_path = os.environ.get("OCI_CONFIG_FILE")

        if os.environ.get("OCI_INSTANCE_PRINCIPAL", "").lower() == "true":
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            self._client = oci.object_storage.ObjectStorageClient(
                config={}, signer=signer, region=self.region
            )
            log.info("OCI storage: Instance Principal auth")
        elif config_path:
            config = oci.config.from_file(config_path)
            self._client = oci.object_storage.ObjectStorageClient(config)
            log.info("OCI storage: config file %s", config_path)
        else:
            config = {
                "user": os.environ["OCI_USER_OCID"],
                "tenancy": os.environ["OCI_TENANCY_OCID"],
                "fingerprint": os.environ["OCI_FINGERPRINT"],
                "region": self.region,
            }
            key_path = os.environ.get("OCI_PRIVATE_KEY_PATH")
            key_content = os.environ.get("OCI_PRIVATE_KEY_CONTENT")
            if key_path:
                with open(key_path) as f:
                    config["key_content"] = f.read()
            elif key_content:
                config["key_content"] = key_content.replace("\\n", "\n")
            else:
                raise RuntimeError(
                    "OCI auth incomplete: provide OCI_PRIVATE_KEY_PATH "
                    "or OCI_PRIVATE_KEY_CONTENT env var"
                )
            self._client = oci.object_storage.ObjectStorageClient(config)
            log.info("OCI storage: API key auth")

        return self._client

    def upload(self, local_path: str, remote_path: str) -> None:
        def _do():
            client = self._get_client()
            with open(local_path, "rb") as f:
                client.put_object(
                    self.namespace, self.bucket, remote_path, f,
                )

        with_retry(_do, op_name=f"upload:{remote_path}", retryable=_RETRYABLE)

    def download(self, remote_path: str, local_path: str) -> None:
        def _do():
            try:
                client = self._get_client()
                return client.get_object(self.namespace, self.bucket, remote_path)
            except Exception as e:
                if _is_404(e):
                    raise FileNotFoundError(
                        f"OCI object {self.bucket}/{remote_path} not found"
                    ) from e
                raise  # transitorio -> retry

        obj = with_retry(
            _do, op_name=f"download:{remote_path}", retryable=_RETRYABLE
        )
        dst = Path(local_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        with open(dst, "wb") as f:
            f.write(obj.data.content)

    def exists(self, remote_path: str) -> bool:
        def _do() -> bool:
            try:
                client = self._get_client()
                client.head_object(self.namespace, self.bucket, remote_path)
                return True
            except Exception as e:
                if _is_404(e):
                    return False
                raise  # transitorio -> retry

        # exists() nunca debe lanzar; swallow cualquier error no-404.
        try:
            return with_retry(
                _do, op_name=f"exists:{remote_path}", retryable=_RETRYABLE
            )
        except Exception:
            return False

    def delete(self, remote_path: str) -> None:
        def _do():
            try:
                client = self._get_client()
                client.delete_object(self.namespace, self.bucket, remote_path)
            except Exception as e:
                if _is_404(e):
                    raise FileNotFoundError(
                        f"OCI object {self.bucket}/{remote_path} not found"
                    ) from e
                raise

        with_retry(_do, op_name=f"delete:{remote_path}", retryable=_RETRYABLE)

    def list_objects(self, prefix: str) -> list[str]:
        def _do() -> list[str]:
            client = self._get_client()
            out = []
            next_start = None
            while True:
                kwargs = {
                    "namespace_name": self.namespace,
                    "bucket_name": self.bucket,
                    "prefix": prefix,
                    "limit": 1000,
                }
                if next_start:
                    kwargs["start"] = next_start
                resp = client.list_objects(**kwargs)
                for obj in resp.data.objects:
                    out.append(obj.name)
                if resp.data.next_start_with:
                    next_start = resp.data.next_start_with
                else:
                    break
            return out

        return with_retry(_do, op_name=f"list:{prefix}", retryable=_RETRYABLE)

    def head_info(self, remote_path: str) -> dict | None:
        """Devuelve metadata del objeto sin descargar el body.

        Usa head_object (1 request, sin transferencia de body). Esto evita
        descargar 12MB solo para calcular el hash.
        Retorna dict con etag (hex md5), md5 (base64), size.
        None si el objeto no existe.
        """
        def _do() -> dict | None:
            try:
                client = self._get_client()
                resp = client.head_object(
                    namespace_name=self.namespace,
                    bucket_name=self.bucket,
                    object_name=remote_path,
                )
            except Exception as e:
                if _is_404(e):
                    return None
                raise
            try:
                etag = resp.data.etag
                md5_b64 = resp.data.content_md5
                size = resp.data.content_length
            except AttributeError:
                etag = resp.headers.get("etag")
                md5_b64 = resp.headers.get("content-md5")
                size = resp.headers.get("content-length")
            return {
                "etag": etag,
                "md5": md5_b64,
                "size": int(size) if size else None,
            }

        try:
            return with_retry(
                _do, op_name=f"head_info:{remote_path}", retryable=_RETRYABLE
            )
        except Exception:
            return None

    def copy(self, src_remote: str, dst_remote: str) -> None:
        """Copia server-side con copy_object (sin transferir el body)."""
        import oci

        def _do():
            client = self._get_client()
            details = oci.object_storage.models.CopyObjectDetails(
                source_object_name=src_remote,
                destination_object_name=dst_remote,
                destination_namespace=self.namespace,
                destination_bucket=self.bucket,
            )
            try:
                client.copy_object(
                    namespace_name=self.namespace,
                    bucket_name=self.bucket,
                    copy_object_details=details,
                )
            except Exception as e:
                if _is_404(e):
                    raise FileNotFoundError(
                        f"OCI copy {self.bucket}/{src_remote} not found"
                    ) from e
                raise

        with_retry(
            _do, op_name=f"copy:{src_remote}->{dst_remote}", retryable=_RETRYABLE
        )
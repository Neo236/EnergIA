import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)


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
        self.namespace = namespace or os.environ["OCI_NAMESPACE"]
        self.bucket = bucket or os.environ["OCI_BUCKET"]
        self.region = region or os.environ.get("OCI_REGION")

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
        client = self._get_client()
        # Streamea el archivo directamente al SDK sin cargarlo entero en memoria,
        # evitando picos de RAM en datasets/modelos grandes.
        with open(local_path, "rb") as f:
            client.put_object(
                self.namespace,
                self.bucket,
                remote_path,
                f,
            )

    def download(self, remote_path: str, local_path: str) -> None:
        client = self._get_client()
        try:
            obj = client.get_object(self.namespace, self.bucket, remote_path)
        except Exception as e:
            raise FileNotFoundError(
                f"OCI object {self.bucket}/{remote_path} not found"
            ) from e
        dst = Path(local_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        with open(dst, "wb") as f:
            f.write(obj.data.content)

    def exists(self, remote_path: str) -> bool:
        client = self._get_client()
        try:
            client.head_object(self.namespace, self.bucket, remote_path)
            return True
        except Exception:
            return False
"""PARStorage — acceso a OCI Object Storage via Pre-Authenticated Request URL.

No requiere el SDK de OCI ni ninguna credencial. La URL PAR ya lleva
el token embebido y puede hacer GET/PUT/HEAD sobre los objetos del bucket.

Env vars requeridas:
    OCI_PAR_URL  — URL base del PAR, por ejemplo:
        https://objectstorage.sa-santiago-1.oraclecloud.com/p/<token>/b/<bucket>/o/

El URL DEBE terminar con '/o/' (el path de objetos del bucket).
Todos los métodos concatenan el nombre del objeto a esa base.

Limitaciones respecto a OciBucketStorage:
  - upload() hace PUT (requiere PAR con permisos de escritura).
  - delete() no está soportado por PAR (siempre lanza NotImplementedError).
  - list_objects() hace GET sobre el prefix (solo si el PAR tiene permisos de listado).
  - copy() no está soportado por PAR (lanza NotImplementedError).

Para el caso de uso del servicio ML (solo download del modelo) es suficiente.
"""

import logging
import os
from pathlib import Path

import requests

from infrastructure.storage.retry import with_retry

log = logging.getLogger(__name__)

_RETRYABLE = (requests.ConnectionError, requests.Timeout, OSError)
_TIMEOUT_S = 30


def _par_base_url() -> str:
    """Lee y valida OCI_PAR_URL del entorno."""
    url = os.environ.get("OCI_PAR_URL", "").rstrip("/")
    if not url:
        raise RuntimeError(
            "PARStorage requiere la variable de entorno OCI_PAR_URL con la "
            "URL base del Pre-Authenticated Request de OCI Object Storage. "
            "Ejemplo: https://objectstorage.sa-santiago-1.oraclecloud.com"
            "/p/<token>/b/<bucket>/o"
        )
    # Garantizamos que siempre termine en '/o' para concatenar correctamente.
    if not url.endswith("/o"):
        # Si el usuario pegó la URL con '/o/' final ya la limpiamos arriba.
        # Si terminaba en '/o' sin slash también está bien.
        # Si no termina en '/o' algo raro pasó — avisamos pero seguimos.
        log.warning(
            "OCI_PAR_URL no termina en '/o': %s. "
            "Verifica que sea la URL base correcta del PAR.",
            url,
        )
    return url


class PARStorage:
    """OCI Object Storage via Pre-Authenticated Request URL.

    Diseñado para el caso de uso de solo-lectura del servicio ML:
    descarga el modelo entrenado sin necesitar credenciales OCI.
    """

    def __init__(self, par_base_url: str | None = None):
        self._base = (par_base_url or _par_base_url()).rstrip("/")
        log.info("PARStorage inicializado (base URL enmascarada por seguridad).")

    def _url(self, remote_path: str) -> str:
        """Construye la URL completa del objeto dado su path relativo."""
        # remote_path puede ser 'latest/modelo_eficiencia_v1.joblib'
        return f"{self._base}/{remote_path.lstrip('/')}"

    # ------------------------------------------------------------------
    # Operaciones de lectura (las únicas que un PAR de solo-lectura permite)
    # ------------------------------------------------------------------

    def download(self, remote_path: str, local_path: str) -> None:
        def _do():
            url = self._url(remote_path)
            resp = requests.get(url, timeout=_TIMEOUT_S, stream=True)
            if resp.status_code == 404:
                raise FileNotFoundError(
                    f"PAR object not found: {remote_path} (HTTP 404)"
                )
            resp.raise_for_status()
            dst = Path(local_path)
            dst.parent.mkdir(parents=True, exist_ok=True)
            with open(dst, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            log.info("Descargado via PAR: %s -> %s", remote_path, local_path)

        with_retry(_do, op_name=f"par.download:{remote_path}", retryable=_RETRYABLE)

    def exists(self, remote_path: str) -> bool:
        def _do() -> bool:
            url = self._url(remote_path)
            resp = requests.head(url, timeout=_TIMEOUT_S)
            if resp.status_code == 404:
                return False
            resp.raise_for_status()
            return True

        try:
            return with_retry(
                _do, op_name=f"par.exists:{remote_path}", retryable=_RETRYABLE
            )
        except Exception:
            return False

    def head_info(self, remote_path: str) -> dict | None:
        def _do() -> dict | None:
            url = self._url(remote_path)
            resp = requests.head(url, timeout=_TIMEOUT_S)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return {
                "etag": resp.headers.get("etag"),
                "md5": resp.headers.get("content-md5"),
                "size": int(resp.headers["content-length"])
                if "content-length" in resp.headers
                else None,
            }

        try:
            return with_retry(
                _do, op_name=f"par.head_info:{remote_path}", retryable=_RETRYABLE
            )
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Operaciones de escritura (requieren PAR con permisos de escritura)
    # ------------------------------------------------------------------

    def upload(self, local_path: str, remote_path: str) -> None:
        def _do():
            url = self._url(remote_path)
            with open(local_path, "rb") as f:
                resp = requests.put(url, data=f, timeout=_TIMEOUT_S)
            resp.raise_for_status()
            log.info("Subido via PAR: %s -> %s", local_path, remote_path)

        with_retry(_do, op_name=f"par.upload:{remote_path}", retryable=_RETRYABLE)

    # ------------------------------------------------------------------
    # Operaciones no soportadas por PAR
    # ------------------------------------------------------------------

    def delete(self, remote_path: str) -> None:
        raise NotImplementedError(
            "PARStorage no soporta delete(). "
            "Usa OciBucketStorage para operaciones de borrado."
        )

    def list_objects(self, prefix: str) -> list[str]:
        """Lista objetos bajo el prefix via PAR (requiere PAR con permisos de listado).

        OCI devuelve un JSON con la estructura de ListObjects. Si el PAR
        no tiene permisos de listado, retorna lista vacía con un warning.
        """
        def _do() -> list[str]:
            url = f"{self._base}?prefix={prefix}"
            resp = requests.get(url, timeout=_TIMEOUT_S)
            if resp.status_code in (403, 404):
                log.warning(
                    "PAR sin permisos de listado o prefijo inexistente: %s", prefix
                )
                return []
            resp.raise_for_status()
            data = resp.json()
            objects = data.get("objects", [])
            return [obj["name"] for obj in objects if "name" in obj]

        try:
            return with_retry(
                _do, op_name=f"par.list:{prefix}", retryable=_RETRYABLE
            )
        except Exception as e:
            log.warning("par.list_objects falló: %s", e)
            return []

    def copy(self, src_remote: str, dst_remote: str) -> None:
        raise NotImplementedError(
            "PARStorage no soporta copy() server-side. "
            "Usa OciBucketStorage para copias dentro del bucket."
        )

import logging
import os

from infrastructure.storage.local import LocalStorage

log = logging.getLogger(__name__)


def get_storage():
    """Factory: devuelve el backend de storage configurado.

    STORAGE_BACKEND=local (default) → filesystem
    STORAGE_BACKEND=oci            → OCI Object Storage (requiere vars OCI_*)

    Variables adicionales:
      STORAGE_LOCAL_ROOT (default '.')  — directorio raíz para LocalStorage
      OCI_NAMESPACE / OCI_BUCKET / OCI_REGION — ver OciBucketStorage
    """
    backend = os.getenv("STORAGE_BACKEND", "local").lower()

    if backend == "local":
        root = os.getenv("STORAGE_LOCAL_ROOT", ".")
        log.info("Storage backend: local (root=%s)", root)
        return LocalStorage(root=root)

    if backend == "oci":
        from infrastructure.storage.oci import OciBucketStorage

        log.info("Storage backend: OCI Object Storage")
        return OciBucketStorage()

    raise ValueError(
        f"STORAGE_BACKEND desconocido: {backend!r}. Usa 'local' u 'oci'."
    )
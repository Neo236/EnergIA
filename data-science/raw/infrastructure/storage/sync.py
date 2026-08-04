import logging
import os
import sys

from infrastructure.config import Config
from infrastructure.storage import get_storage

log = logging.getLogger(__name__)


def _download_from_storage(storage, remote_path, local_path):
    if os.path.exists(local_path):
        log.info("Artifact ya presente localmente: %s", local_path)
        return False
    log.info("Descargando %s → %s", remote_path, local_path)
    storage.download(remote_path, local_path)
    return True


def ensure_artifacts():
    """Descarga dataset/modelo/métricas desde storage si no existen localmente."""
    storage = get_storage()

    objects = [
        (Config.OUTPUT_JSON_PATH, "data/database_beta.json"),
        (Config.OUTPUT_MODEL_PATH, "data/modelo_eficiencia_v1.joblib"),
        (Config.OUTPUT_METRICAS_PATH, "data/metricas_v1.joblib"),
    ]

    for local_path, remote_path in objects:
        if os.path.exists(local_path):
            continue
        if not storage.exists(remote_path):
            log.warning(
                "Artifact no encontrado ni local ni en storage: %s. "
                "Ejecuta 'make pipeline' para entrenar.",
                remote_path,
            )
            continue
        try:
            _download_from_storage(storage, remote_path, local_path)
        except FileNotFoundError:
            log.warning("Fallo descarga de %s", remote_path)
import logging
import os

from infrastructure.config import Config
from infrastructure.storage import get_storage

log = logging.getLogger(__name__)


def ensure_artifacts():
    """Descarga dataset/modelo/metricas desde storage si no existen localmente.

    Convencion: el archivo vigente vive en `latest/<name>` dentro del bucket.
    El startup descarga ese, no la raiz.
    """
    try:
        storage = get_storage()
    except Exception as e:
        log.warning("No se pudo inicializar storage: %s. Continuando sin bucket.", e)
        return

    objects = [
        (Config.OUTPUT_JSON_PATH, "database_beta.json"),
        (Config.OUTPUT_JSON_PATH.replace(".json", ".csv"), "database_beta.csv"),
        (Config.OUTPUT_MODEL_PATH, "modelo_eficiencia_v1.joblib"),
        (Config.OUTPUT_METRICAS_PATH, "metricas_v1.joblib"),
    ]

    for local_path, remote_name in objects:
        if os.path.exists(local_path):
            log.info("Artifact ya presente localmente: %s", local_path)
            continue
        remote_path = f"latest/{remote_name}"
        if not storage.exists(remote_path):
            log.warning(
                "Artifact no encontrado ni local ni en storage: %s. "
                "Ejecuta 'make pipeline' para entrenar.",
                remote_path,
            )
            continue
        try:
            log.info("Descargando %s -> %s", remote_path, local_path)
            storage.download(remote_path, local_path)
        except FileNotFoundError:
            log.warning("Fallo descarga de %s", remote_path)
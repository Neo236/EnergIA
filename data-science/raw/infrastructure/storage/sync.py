import logging
import os

from infrastructure.config import Config
from infrastructure.storage import get_storage

log = logging.getLogger(__name__)


def ensure_artifacts():
    """Pull dataset/modelo/metricas desde storage (bucket es source of truth).

    Convencion: el archivo vigente vive en `latest/<name>` dentro del bucket.

    Estrategia:
      1. SIEMPRE intenta descargar del bucket y sobrescribir el local.
         Asi una nueva version del modelo en el bucket propaga a todos
         los instances en el siguiente restart.
      2. Si el bucket no es alcanzable (red, falta credenciales) o el
         artifact no existe ahi, mantiene el archivo local como fallback.
         Asi un primer boot sin bucket poblado no rompe el servicio.
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
        remote_path = f"latest/{remote_name}"
        try:
            if not storage.exists(remote_path):
                if os.path.exists(local_path):
                    log.info(
                        "Bucket sin %s; manteniendo local %s",
                        remote_path, local_path,
                    )
                else:
                    log.warning(
                        "Artifact no encontrado ni en bucket ni local: %s. "
                        "Ejecuta 'make pipeline' para entrenar y subir.",
                        remote_path,
                    )
                continue
            log.info("Pulling %s -> %s (overwrite local)", remote_path, local_path)
            storage.download(remote_path, local_path)
        except Exception as e:
            if os.path.exists(local_path):
                log.warning(
                    "Fallo pull de %s: %s. Manteniendo local.",
                    remote_path, e,
                )
            else:
                log.warning(
                    "Fallo pull de %s y no hay local: %s", remote_path, e,
                )
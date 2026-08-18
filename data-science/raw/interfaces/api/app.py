import hashlib
import logging
import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from application.inference import _load_model_cached, clear_model_cache, procesar_solicitud_api
from infrastructure.config import Config
from infrastructure.storage.sync import ensure_artifacts
from interfaces.api.schemas import AnalisisRequest

log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(level=log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)

app = FastAPI(title="EnergiAI - Analisis Energetico", version="1.2.0")
MODEL_PATH = os.getenv("MODEL_PATH", Config.OUTPUT_MODEL_PATH)


def _entrenar_respaldo_local() -> None:
    """Entrena un modelo de respaldo en este mismo proceso, sin publicarlo.

    Reutiliza interfaces.cli.train tal cual (mismo dataset sintetico, misma
    RANDOM_SEED), asi que el resultado es el mismo modelo que produciria
    `make pipeline` a mano. La flag --dry-run es la parte que importa: sin
    ella, train.main() tambien SUBE los artefactos al bucket configurado en
    STORAGE_BACKEND (ver _safe_upload_with_rotation), y Staging y Produccion
    comparten el mismo OCI_PAR_URL - una corrida de respaldo no debe
    reescribir el modelo "oficial" que ambos ambientes leen al arrancar.
    Import local: interfaces.cli.train solo hace falta en este camino de
    excepcion, no en el arranque normal con el bucket disponible.
    """
    from interfaces.cli.train import main as entrenar_dataset_y_modelo

    codigo = entrenar_dataset_y_modelo(["--dry-run"])
    if codigo != 0:
        raise RuntimeError(f"interfaces.cli.train devolvió código {codigo}")


@app.on_event("startup")
def _startup():
    """Startup del servicio ML.

    Orden:
      1. ensure_artifacts(): pull desde el bucket (OCI / PAR / local). El
         bucket es la fuente de verdad; lo que estaba bakeado en el Docker
         image se sobrescribe con la version vigente. Si el bucket no es
         alcanzable, mantenemos lo local como fallback.
      2. Pre-cargar el modelo en memoria del proceso. Asi el primer POST
         no paga el joblib.load (~250ms). El cache es por-path via
         @lru_cache; tests con paths unicos se siguen cargando fresh.
      3. Último recurso: si tras el paso 1 seguimos sin modelo (bucket
         inalcanzable y sin artefacto bakeado en la imagen), entrenar uno
         de respaldo local. Sin este paso, el servicio queda respondiendo
         503 hasta el próximo restart, aunque nadie corra `make pipeline`
         a mano - que es exactamente lo que pasó en Staging.
    """
    # 1. Pull desde el bucket (source of truth)
    try:
        ensure_artifacts()
    except Exception as e:
        log.warning("ensure_artifacts falló al startup: %s. Usando local.", e)

    # 2. Warm model cache
    try:
        _load_model_cached(MODEL_PATH)
        log.info("Modelo pre-cargado en memoria: %s", MODEL_PATH)
        return
    except FileNotFoundError:
        log.warning(
            "Modelo no encontrado en %s tras ensure_artifacts(). "
            "Entrenando un respaldo local antes de aceptar tráfico...",
            MODEL_PATH,
        )

    # 3. Entrenar de respaldo y reintentar la carga.
    try:
        _entrenar_respaldo_local()
        clear_model_cache()
        _load_model_cached(MODEL_PATH)
        log.info("Modelo de respaldo entrenado y cargado: %s", MODEL_PATH)
    except Exception as e:
        log.error(
            "No se pudo entrenar el modelo de respaldo (%s). El servicio "
            "responderá 503 hasta que el bucket esté disponible o se "
            "reinicie el contenedor.",
            e,
        )


@app.get("/")
def root():
    return {"service": "EnergiAI", "status": "ok", "endpoint": "POST /analisis-energetico"}


@app.get("/health")
def health():
    """Vivo Y con modelo cargado - no solo que el proceso responde.

    _load_model_cached está cacheado (@lru_cache): una vez que el modelo
    carga, esta llamada es un lookup en memoria, no vuelve a pagar el
    joblib.load. Mientras siga faltando, cada poll reintenta la carga -
    barato porque la alternativa (reportar "healthy" a ciegas) es la razón
    por la que este endpoint nunca detectó el 503 real en Staging: ni el
    HEALTHCHECK de Docker ni el "Verificar salud" del CD miran otra cosa.
    """
    try:
        _load_model_cached(MODEL_PATH)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail=f"Modelo no encontrado en {MODEL_PATH}. El servicio no puede responder inferencias.",
        )
    return {"status": "healthy"}


@app.get("/model-info")
def model_info():
    """Identidad del modelo activo: hash SHA-256, tamaño, mtime y estado de cache.

    Permite confirmar que el modelo que sirve la API es el que se entrenó y
    publicó en el bucket, sin depender de leer el .joblib a mano ni de comparar
    sidecars. El hash se calcula leyendo el archivo en chunks (memoria acotada).

    Alcance de acceso: este servicio publica su puerto solo en 127.0.0.1 (ver
    docker-compose.yml) y infra/Caddyfile no lo enruta - el proxy manda /api,
    /swagger-ui, /v3/api-docs y /actuator al backend Spring, no al ML. Asi que
    /model-info se consulta DESDE la VM, no desde afuera:

        curl -s localhost:8000/model-info   # produccion
        curl -s localhost:8002/model-info   # staging

    Campos de respuesta:
      model_path       — path relativo usado por el proceso
      sha256           — hash SHA-256 del .joblib en disco
      size_bytes       — tamaño en bytes
      mtime_utc        — ultima modificacion del archivo en UTC ISO-8601
      loaded           — True si el modelo ya esta en el cache @lru_cache
      storage_backend  — valor de STORAGE_BACKEND (local | oci | par)
    """
    path = MODEL_PATH

    # Sin chequeo previo de os.path.exists(): entre ese chequeo y el open()
    # hay una ventana en la que el archivo puede desaparecer (el startup lo
    # reescribe al bajarlo del bucket), y ahi el FileNotFoundError se
    # propagaba como 500. Un solo camino: intentar abrir y traducir el fallo.
    # El mtime y el tamaño salen del mismo descriptor que ya estamos leyendo,
    # via fstat, para que describan exactamente el archivo que se hasheo.
    sha256 = hashlib.sha256()
    size = 0
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                sha256.update(chunk)
                size += len(chunk)
            mtime = os.fstat(f.fileno()).st_mtime
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail=f"Archivo de modelo no encontrado en {path}. "
                   "Ejecuta `make pipeline` o espera el startup del servicio.",
        )

    mtime_utc = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Verificar si el modelo está en el lru_cache sin intentar cargarlo
    cache_info = _load_model_cached.cache_info()
    loaded = cache_info.currsize > 0

    return {
        "model_path": path,
        "sha256": sha256.hexdigest(),
        "size_bytes": size,
        "mtime_utc": mtime_utc,
        "loaded": loaded,
        "storage_backend": os.getenv("STORAGE_BACKEND", "local"),
    }


@app.post("/analisis-energetico")
def analisis_energetico(req: AnalisisRequest):
    input_data = {
        "tipo_inmueble": req.tipo_inmueble,
        "metros_cuadrados": req.metros_cuadrados,
        "antiguedad_vivienda": req.antiguedad_vivienda,
        "zona_fria": req.zona_fria,
        "calidad_aislamiento": req.calidad_aislamiento,
        "fuente_calefaccion": req.fuente_calefaccion,
        "fuente_agua_caliente": req.fuente_agua_caliente,
        "consumo_kwh": req.consumo_kwh,
        "uso_horario_pico": req.uso_horario_pico,
        "horas_alto_consumo": req.horas_alto_consumo,
        "cantidad_equipos": req.cantidad_equipos,
    }

    try:
        return procesar_solicitud_api(input_data, MODEL_PATH)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Modelo no encontrado en {MODEL_PATH}. "
                "Ejecuta `make pipeline` o sube el modelo al bucket."
            ),
        )
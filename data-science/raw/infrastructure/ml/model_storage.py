import joblib

# Nivel de compresion para joblib.dump. 3 (zlib nivel 5-6) reduce el modelo
# de ~12MB a ~4MB con impacto despreciable en tiempo de carga.
JOBLIB_COMPRESS = 3


def save_model(modelo, path: str) -> None:
    joblib.dump(modelo, path, compress=JOBLIB_COMPRESS)


def load_model(path: str):
    return joblib.load(path)


def save_metrics(metricas: dict, path: str) -> None:
    joblib.dump(metricas, path, compress=JOBLIB_COMPRESS)


def load_metrics(path: str) -> dict:
    return joblib.load(path)
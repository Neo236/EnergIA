import joblib


def save_model(modelo, path: str) -> None:
    joblib.dump(modelo, path)


def load_model(path: str):
    return joblib.load(path)


def save_metrics(metricas: dict, path: str) -> None:
    joblib.dump(metricas, path)


def load_metrics(path: str) -> dict:
    return joblib.load(path)
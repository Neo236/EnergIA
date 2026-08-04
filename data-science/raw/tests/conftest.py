import os
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))


@pytest.fixture
def tmp_artifact_dir(tmp_path):
    return tmp_path


@pytest.fixture
def small_dataset():
    from infrastructure.data.simulation import generar_dataset
    return generar_dataset(num_clientes=200, seed=42)


@pytest.fixture
def trained_model(tmp_artifact_dir, small_dataset):
    from application.training import entrenar_y_guardar_modelo

    model_path = tmp_artifact_dir / "modelo.joblib"
    metrics_path = tmp_artifact_dir / "metricas.joblib"
    resultado = entrenar_y_guardar_modelo(
        df=small_dataset,
        output_path=str(model_path),
        metricas_path=str(metrics_path),
        random_seed=42,
    )
    return {
        "modelo": resultado["modelo"],
        "model_path": str(model_path),
        "metrics_path": str(metrics_path),
        "df": small_dataset,
    }


@pytest.fixture
def fastapi_client(monkeypatch, trained_model):
    os.environ["MODEL_PATH"] = trained_model["model_path"]
    from interfaces.api import app as app_module

    monkeypatch.setattr(app_module, "MODEL_PATH", trained_model["model_path"])
    from fastapi.testclient import TestClient

    return TestClient(app_module.app)
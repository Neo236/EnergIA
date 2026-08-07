import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))


# El SDK oficial de OCI (`oci`) no esta en requirements.txt (solo se usa
# cuando STORAGE_BACKEND=oci en produccion). En CI se omite para no
# instalar dependencias innecesarias. Mockeamos el modulo completo
# antes de cualquier import de infrastructure.storage.oci para que los
# tests que importan CopyObjectDetails, ObjectStorageClient, etc. no
# fallen con ModuleNotFoundError.
try:
    import oci  # noqa: F401
    _OCI_AVAILABLE = True
except ImportError:
    _OCI_AVAILABLE = False
    _fake_oci = MagicMock()
    _fake_oci.auth.signers.InstancePrincipalsSecurityTokenSigner = MagicMock()
    _fake_oci.object_storage.ObjectStorageClient = MagicMock()
    _fake_oci.object_storage.models.CopyObjectDetails = MagicMock()
    sys.modules["oci"] = _fake_oci
    sys.modules["oci.auth"] = _fake_oci.auth
    sys.modules["oci.auth.signers"] = _fake_oci.auth.signers
    sys.modules["oci.object_storage"] = _fake_oci.object_storage
    sys.modules["oci.object_storage.models"] = _fake_oci.object_storage.models


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
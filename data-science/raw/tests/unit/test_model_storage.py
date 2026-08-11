import joblib
import pytest
from pathlib import Path

from application.training import CAT_COLS as TRAIN_CAT_COLS
from application.training import FEATURE_COLS as TRAIN_FEATURE_COLS
from application.training import NUM_COLS as TRAIN_NUM_COLS
from infrastructure.config import Config
from infrastructure.ml.model_storage import (
    load_metrics,
    load_model,
    save_metrics,
    save_model,
)


class TestModelStorage:
    def test_save_and_load_model_roundtrip(self, tmp_artifact_dir):
        obj = {"key": "value", "lista": [1, 2, 3]}
        path = tmp_artifact_dir / "m.joblib"
        save_model(obj, str(path))
        loaded = load_model(str(path))
        assert loaded == obj

    def test_save_and_load_metrics_roundtrip(self, tmp_artifact_dir):
        metrics = {"y_test": [0, 1, 0], "y_pred": [0, 1, 1]}
        path = tmp_artifact_dir / "metrics.joblib"
        save_metrics(metrics, str(path))
        loaded = load_metrics(str(path))
        assert loaded == metrics

    def test_load_model_archivo_inexistente_lanza_filenotfound(self, tmp_artifact_dir):
        with pytest.raises(FileNotFoundError):
            load_model(str(tmp_artifact_dir / "no_existe.joblib"))


class TestArtifactConsistency:
    """Guard: el artifact `modelo_eficiencia_v1.joblib` en disco debe ser
    compatible con `application/training.py` actual. Si alguien entrena con
    codigo viejo o commitea un .joblib stale, esto falla en CI antes de
    llegar a produccion.
    """

    ARTIFACT_PATH = (
        Config.OUTPUT_MODEL_PATH
    )  # default: data/modelo_eficiencia_v1.joblib (relativo al cwd)

    def test_artifact_existe(self):
        if not Path(self.ARTIFACT_PATH).exists():
            pytest.skip(
                f"Artifact no encontrado en {self.ARTIFACT_PATH}. "
                "Ejecuta `make pipeline` o `python -m interfaces.cli.train`."
            )

    def test_artifact_cat_cols_match_training(self):
        if not Path(self.ARTIFACT_PATH).exists():
            pytest.skip("Artifact no presente")
        modelo = load_model(self.ARTIFACT_PATH)
        prep = modelo.steps[0][1]
        _, _, cat_cols_disk = prep.transformers[1]
        assert list(cat_cols_disk) == TRAIN_CAT_COLS, (
            f"CAT_COLS del artifact ({list(cat_cols_disk)}) no coinciden con "
            f"application/training.py ({TRAIN_CAT_COLS}). Reentrena el modelo "
            f"con `make pipeline` o `python -m interfaces.cli.train`."
        )

    def test_artifact_num_cols_match_training(self):
        if not Path(self.ARTIFACT_PATH).exists():
            pytest.skip("Artifact no presente")
        modelo = load_model(self.ARTIFACT_PATH)
        prep = modelo.steps[0][1]
        _, _, num_cols_disk = prep.transformers[0]
        assert list(num_cols_disk) == TRAIN_NUM_COLS, (
            f"NUM_COLS del artifact ({list(num_cols_disk)}) no coinciden con "
            f"application/training.py ({TRAIN_NUM_COLS}). Reentrena el modelo."
        )

    def test_artifact_predict_end_to_end(self, small_dataset):
        """Smoke test: el artifact debe poder predecir sobre una fila de muestra
        usando el codigo de inference actual sin lanzar excepciones."""
        from application.inference import _a_fila_modelo
        if not Path(self.ARTIFACT_PATH).exists():
            pytest.skip("Artifact no presente")
        modelo = load_model(self.ARTIFACT_PATH)
        sample = small_dataset.iloc[[0]].drop(columns=["categoria"]).to_dict("records")[0]
        fila = _a_fila_modelo(sample)
        # Si las features no matchean, predict_proba falla con
        # "could not convert string to float" o KeyError.
        probs = modelo.predict_proba(fila)
        assert probs.shape == (1, len(modelo.classes_))
import joblib
import pytest

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
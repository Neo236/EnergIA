import pytest

from infrastructure.validators.artifacts import (
    validar_json,
    validar_metricas,
    validar_modelo,
)


class TestValidarJson:
    def test_json_valido(self, tmp_artifact_dir):
        import json

        path = tmp_artifact_dir / "test.json"
        path.write_text(json.dumps([{"a": 1}, {"b": 2}]))
        result = validar_json(str(path))
        assert result["ok"] is True
        assert result["n"] == 2

    def test_json_inexistente(self, tmp_artifact_dir):
        result = validar_json(str(tmp_artifact_dir / "no.json"))
        assert result["ok"] is False
        assert "NO existe" in result["msg"]

    def test_json_no_es_lista(self, tmp_artifact_dir):
        path = tmp_artifact_dir / "test.json"
        path.write_text('{"a": 1}')
        result = validar_json(str(path))
        assert result["ok"] is False
        assert "lista" in result["msg"]

    def test_json_elementos_no_dict(self, tmp_artifact_dir):
        path = tmp_artifact_dir / "test.json"
        path.write_text('[1, 2, 3]')
        result = validar_json(str(path))
        assert result["ok"] is False


class TestValidarModelo:
    def test_modelo_inexistente(self, tmp_artifact_dir):
        result = validar_modelo(str(tmp_artifact_dir / "no.joblib"))
        assert result["ok"] is False

    def test_modelo_valido(self, tmp_artifact_dir, small_dataset):
        from application.training import entrenar_y_guardar_modelo

        path = tmp_artifact_dir / "model.joblib"
        entrenar_y_guardar_modelo(small_dataset, str(path), str(tmp_artifact_dir / "m.joblib"), 42)
        result = validar_modelo(str(path))
        assert result["ok"] is True
        assert "Pipeline" in result["msg"]

    def test_modelo_no_es_pipeline(self, tmp_artifact_dir):
        import joblib

        path = tmp_artifact_dir / "falso.joblib"
        joblib.dump({"fake": True}, str(path))
        result = validar_modelo(str(path))
        assert result["ok"] is False
        assert "no Pipeline" in result["msg"]


class TestValidarMetricas:
    def test_metricas_inexistentes(self, tmp_artifact_dir):
        result = validar_metricas(str(tmp_artifact_dir / "no.joblib"))
        assert result["ok"] is False

    def test_metricas_con_categoria_eficiente_mayuscula(self, tmp_artifact_dir):
        """Regression test: validar_metricas debe encontrar 'Eficiente' con mayúscula."""
        import joblib
        from sklearn.metrics import classification_report

        y_true = (
            ["Eficiente"] * 50
            + ["Moderado"] * 50
            + ["Ineficiente"] * 50
        )
        y_pred = (
            ["Eficiente"] * 48 + ["Moderado"] * 2
            + ["Moderado"] * 45 + ["Ineficiente"] * 3 + ["Eficiente"] * 2
            + ["Ineficiente"] * 47 + ["Moderado"] * 3
        )
        assert len(y_true) == len(y_pred) == 150

        rep = classification_report(y_true, y_pred, zero_division=0)
        path = tmp_artifact_dir / "met.joblib"
        joblib.dump({"y_test": y_true, "y_pred": y_pred}, str(path))

        result = validar_metricas(str(path))
        assert result["ok"] is True, f"msg: {result['msg']}"
        assert "Eficiente" in result["msg"]
        assert result["f1"] > 0.0

    def test_metricas_case_insensitive_con_target_names(self, tmp_artifact_dir):
        """El parser debe encontrar 'Eficiente' (con mayúscula) cuando el report lo incluye."""
        import joblib
        from sklearn.metrics import classification_report

        y_true = ["Ineficiente", "Eficiente", "Ineficiente", "Eficiente", "Ineficiente"]
        y_pred = ["Ineficiente", "Eficiente", "Ineficiente", "Ineficiente", "Ineficiente"]
        rep = classification_report(y_true, y_pred, zero_division=0)
        path = tmp_artifact_dir / "m.joblib"
        joblib.dump({"y_test": y_true, "y_pred": y_pred}, str(path))

        result = validar_metricas(str(path))
        assert result["ok"] is True, f"msg: {result['msg']}"
        assert result["f1"] > 0.0
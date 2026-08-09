import os

import joblib
import pytest

from application.training import (
    CAT_COLS,
    FEATURE_COLS,
    NUM_COLS,
    TARGET_COL,
    entrenar_y_guardar_modelo,
)


class TestTrainPipeline:
    def test_artifact_creado(self, tmp_artifact_dir, small_dataset):
        model_path = tmp_artifact_dir / "m.joblib"
        metrics_path = tmp_artifact_dir / "met.joblib"
        entrenar_y_guardar_modelo(small_dataset, str(model_path), str(metrics_path), 42)
        assert model_path.exists()
        assert metrics_path.exists()

    def test_modelo_cargable(self, tmp_artifact_dir, small_dataset):
        model_path = tmp_artifact_dir / "m.joblib"
        entrenar_y_guardar_modelo(small_dataset, str(model_path), str(tmp_artifact_dir / "met.joblib"), 42)
        modelo = joblib.load(str(model_path))
        assert hasattr(modelo, "predict")
        assert hasattr(modelo, "predict_proba")

    def test_metricas_contienen_keys(self, tmp_artifact_dir, small_dataset):
        metrics_path = tmp_artifact_dir / "met.joblib"
        entrenar_y_guardar_modelo(
            small_dataset, str(tmp_artifact_dir / "m.joblib"), str(metrics_path), 42
        )
        blob = joblib.load(str(metrics_path))
        assert "y_test" in blob
        assert "y_pred" in blob

    def test_reporte_retorna_string(self, tmp_artifact_dir, small_dataset):
        resultado = entrenar_y_guardar_modelo(
            small_dataset,
            str(tmp_artifact_dir / "m.joblib"),
            str(tmp_artifact_dir / "met.joblib"),
            42,
        )
        assert isinstance(resultado["reporte"], str)
        assert "Eficiente" in resultado["reporte"]
        assert "Moderado" in resultado["reporte"]
        assert "Ineficiente" in resultado["reporte"]

    def test_makedirs_si_directorio_no_existe(self, tmp_artifact_dir, small_dataset):
        """Regression test: train debe crear directorio destino si no existe."""
        nested_dir = tmp_artifact_dir / "no" / "existe" / "todavia"
        model_path = nested_dir / "m.joblib"
        metrics_path = nested_dir / "met.joblib"
        entrenar_y_guardar_modelo(small_dataset, str(model_path), str(metrics_path), 42)
        assert model_path.exists()
        assert metrics_path.exists()


class TestConstants:
    def test_target_col_es_categoria(self):
        assert TARGET_COL == "categoria"

    def test_cat_y_num_sin_solapamiento(self):
        assert set(CAT_COLS).isdisjoint(set(NUM_COLS))

    def test_feature_cols_contiene_todas(self):
        assert set(FEATURE_COLS) == set(CAT_COLS) | set(NUM_COLS)
        assert TARGET_COL not in FEATURE_COLS

    def test_num_cols_son_numericas(self):
        for col in NUM_COLS:
            assert col in {
                "metros_cuadrados", "antiguedad_vivienda",
                "consumo_kwh", "horas_alto_consumo",
                "cantidad_equipos",
            }

    def test_cat_cols_son_categoricas(self):
        for col in CAT_COLS:
            assert col in {
                "tipo_inmueble", "calidad_aislamiento",
                "fuente_calefaccion", "fuente_agua_caliente",
                "zona_fria", "uso_horario_pico",
            }
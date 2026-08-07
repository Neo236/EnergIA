import numpy as np
import pytest

from application.inference import (
    DEFAULTS,
    MODELO_FEATURES,
    _a_fila_modelo,
    procesar_solicitud_api,
)


class TestAFilaModelo:
    def test_retorna_dataframe_con_columnas_ordenadas(self):
        fila = _a_fila_modelo({})
        assert list(fila.columns) == MODELO_FEATURES
        assert fila.shape == (1, len(MODELO_FEATURES))

    def test_usa_defaults_cuando_faltan_keys(self):
        fila = _a_fila_modelo({})
        for feat in MODELO_FEATURES:
            assert fila[feat].iloc[0] == DEFAULTS[feat]

    def test_input_completo_pasa_tal_cual(self):
        # Carga un payload valido: features numericas con un escalar distinto,
        # categoricas con strings validos.
        payload = {feat: float(i) for i, feat in enumerate(MODELO_FEATURES)}
        payload["tipo_inmueble"] = "Casa"
        payload["zona_fria"] = "Si"
        payload["uso_horario_pico"] = "No"
        payload["calidad_aislamiento"] = "Media"
        payload["fuente_calefaccion"] = "Electricidad"
        payload["fuente_agua_caliente"] = "Electricidad"
        fila = _a_fila_modelo(payload)
        for feat in MODELO_FEATURES:
            assert fila[feat].iloc[0] == payload[feat]


class TestProcesarSolicitudApi:
    def test_payload_completo_retorna_categoria(self, trained_model):
        payload = {
            "tipo_inmueble": "Casa",
            "metros_cuadrados": 1200,
            "antiguedad_vivienda": 50,
            "zona_fria": "No",
            "calidad_aislamiento": "Alta",
            "fuente_calefaccion": "Solar",
            "fuente_agua_caliente": "Solar",
            "consumo_kwh": 250.0,
            "uso_horario_pico": "No",
            "horas_alto_consumo": 5,
            "cantidad_equipos": 20,
        }
        result = procesar_solicitud_api(payload, trained_model["model_path"])

        assert "categoria" in result
        assert result["categoria"] in {"Eficiente", "Moderado", "Ineficiente"}
        assert 0.0 <= result["probabilidad"] <= 1.0
        assert "costo_estimado_mensual" in result
        assert result["costo_estimado_mensual"] == pytest.approx(250.0 * 0.75, rel=0.01)
        assert isinstance(result["recomendaciones"], list)

    def test_modelo_inexistente_lanza_filenotfound(self, tmp_artifact_dir):
        payload = {"consumo_kwh": 100}
        with pytest.raises(FileNotFoundError):
            procesar_solicitud_api(payload, str(tmp_artifact_dir / "no.joblib"))

    def test_payload_minimo_solo_consumo(self, trained_model):
        payload = {"consumo_kwh": 200}
        result = procesar_solicitud_api(payload, trained_model["model_path"])
        assert "categoria" in result
        assert result["categoria"] in {"Eficiente", "Moderado", "Ineficiente"}

    def test_costo_usa_tarifa_de_config(self, trained_model, monkeypatch):
        """Validar que cambiar TARIFA_KWH en Config impacta el costo."""
        from infrastructure import config as cfg_module

        monkeypatch.setattr(cfg_module.Config, "TARIFA_KWH", 1.50)

        payload = {"consumo_kwh": 100}
        result = procesar_solicitud_api(payload, trained_model["model_path"])
        assert result["costo_estimado_mensual"] == pytest.approx(150.0, rel=0.01)

    def test_categoria_invalida_del_modelo_lanza_valueerror(
        self, trained_model, monkeypatch
    ):
        """Si el modelo devuelve una clase fuera del set cerrado, raise."""
        class _ModeloRoto:
            classes_ = np.array(["Eficiente", "Moderado", "Kryptonita"])
            def predict_proba(self, X):
                return np.array([[0.1, 0.2, 0.7]])

        monkeypatch.setattr(
            "application.inference.load_model", lambda path: _ModeloRoto()
        )
        with pytest.raises(ValueError, match="categoria no soportada"):
            procesar_solicitud_api({"consumo_kwh": 100}, "dummy")

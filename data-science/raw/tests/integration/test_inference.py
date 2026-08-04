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

    def test_alias_consumo_electrico_a_consumo_kwh(self):
        fila = _a_fila_modelo({"consumo_electrico_kwh": 999.9})
        assert fila["consumo_kwh"].iloc[0] == 999.9

    def test_usa_defaults_cuando_faltan_keys(self):
        fila = _a_fila_modelo({})
        for feat in MODELO_FEATURES:
            assert fila[feat].iloc[0] == DEFAULTS[feat]


class TestProcesarSolicitudApi:
    def test_payload_completo_retorna_categoria(self, trained_model):
        payload = {
            "tipo_inmueble": "Casa",
            "metros_cuadrados": 1200,
            "antiguedad_vivienda": 50,
            "zona_fria": False,
            "calidad_aislamiento": "Alta",
            "fuente_calefaccion": "Solar",
            "fuente_agua_caliente": "Solar",
            "consumo_kwh": 250.0,
            "uso_horario_pico": False,
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

    def test_payload_alias_consumo_electrico(self, trained_model):
        payload = {"consumo_electrico_kwh": 100, "cantidad_equipos": 5}
        result = procesar_solicitud_api(payload, trained_model["model_path"])
        assert "categoria" in result

    def test_payload_minimo_solo_consumo(self, trained_model):
        payload = {"consumo_kwh": 200}
        result = procesar_solicitud_api(payload, trained_model["model_path"])
        assert "categoria" in result
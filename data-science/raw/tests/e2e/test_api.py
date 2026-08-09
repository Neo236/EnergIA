import pytest

from interfaces.api.schemas import AnalisisRequest


# 6 obligatorias + 5 opcionales (ver docstring de AnalisisRequest)
PAYLOAD_COMPLETO = {
    # --- obligatorias ---
    "consumo_kwh": 363.4,
    "tipo_inmueble": "Departamento",
    "uso_horario_pico": "Si",
    "fuente_calefaccion": "Solar",
    "fuente_agua_caliente": "Electricidad",
    "zona_fria": "No",
    # --- opcionales ---
    "metros_cuadrados": 1269,
    "antiguedad_vivienda": 61,
    "calidad_aislamiento": "Muy Baja",
    "horas_alto_consumo": 14,
    "cantidad_equipos": 19,
}

# Solo las 6 obligatorias, las 5 opcionales se imputan por default
PAYLOAD_MINIMO = {
    "consumo_kwh": 250.0,
    "tipo_inmueble": "Casa",
    "uso_horario_pico": "No",
    "fuente_calefaccion": "Electricidad",
    "fuente_agua_caliente": "Electricidad",
    "zona_fria": "No",
}


class TestApiEndponts:
    def test_root(self, fastapi_client):
        r = fastapi_client.get("/")
        assert r.status_code == 200
        body = r.json()
        assert body["service"] == "EnergiAI"
        assert body["status"] == "ok"

    def test_health(self, fastapi_client):
        r = fastapi_client.get("/health")
        assert r.status_code == 200
        assert r.json() == {"status": "healthy"}

    def test_analisis_energetico_exitoso(self, fastapi_client):
        r = fastapi_client.post("/analisis-energetico", json=PAYLOAD_COMPLETO)
        assert r.status_code == 200
        body = r.json()
        assert body["categoria"] in {"Eficiente", "Moderado", "Ineficiente"}
        assert 0.0 <= body["probabilidad"] <= 1.0
        assert body["costo_estimado_mensual"] == pytest.approx(363.4 * 0.75, rel=0.01)
        assert isinstance(body["recomendaciones"], list)
        assert len(body["recomendaciones"]) >= 1

    def test_analisis_energetico_payload_minimo(self, fastapi_client):
        """Solo las 6 obligatorias deben ser suficientes."""
        r = fastapi_client.post("/analisis-energetico", json=PAYLOAD_MINIMO)
        assert r.status_code == 200
        body = r.json()
        assert body["categoria"] in {"Eficiente", "Moderado", "Ineficiente"}
        # costo = consumo_kwh * 0.75
        assert body["costo_estimado_mensual"] == pytest.approx(250.0 * 0.75, rel=0.01)
        assert isinstance(body["recomendaciones"], list)

    def test_analisis_energetico_opcional_default(self, fastapi_client):
        """Si omito los 5 opcionales, debe usar los defaults Pydantic."""
        payload = {
            "consumo_kwh": 200.0,
            "tipo_inmueble": "Casa",
            "uso_horario_pico": "No",
            "fuente_calefaccion": "Electricidad",
            "fuente_agua_caliente": "Electricidad",
            "zona_fria": "No",
            # metros_cuadrados omitido -> default 1000.0
            # antiguedad_vivienda omitido -> default 50
            # calidad_aislamiento omitido -> default "Media"
            # horas_alto_consumo omitido -> default 8
            # cantidad_equipos omitido -> default 15
        }
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 200

    def test_analisis_energetico_tipo_inmueble_invalido(self, fastapi_client):
        r = fastapi_client.post("/analisis-energetico", json=PAYLOAD_COMPLETO | {"tipo_inmueble": "Garaje"})
        assert r.status_code == 422
        body = r.json()
        assert "detail" in body
        assert any(
            err["loc"][-1] == "tipo_inmueble"
            for err in body["detail"]
        )

    def test_analisis_energetico_horas_invalidas(self, fastapi_client):
        r = fastapi_client.post("/analisis-energetico", json=PAYLOAD_COMPLETO | {"horas_alto_consumo": 30})
        assert r.status_code == 422

    def test_analisis_energetico_aislamiento_invalido(self, fastapi_client):
        r = fastapi_client.post("/analisis-energetico", json=PAYLOAD_COMPLETO | {"calidad_aislamiento": "Super Alta"})
        assert r.status_code == 422

    # ---- Faltan obligatorias (debe rechazarse con 422) ----

    def test_falta_obligatorio_consumo_kwh(self, fastapi_client):
        payload = {k: v for k, v in PAYLOAD_MINIMO.items() if k != "consumo_kwh"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 422

    def test_falta_obligatorio_tipo_inmueble(self, fastapi_client):
        payload = {k: v for k, v in PAYLOAD_MINIMO.items() if k != "tipo_inmueble"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 422

    def test_falta_obligatorio_uso_horario_pico(self, fastapi_client):
        payload = {k: v for k, v in PAYLOAD_MINIMO.items() if k != "uso_horario_pico"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 422

    def test_falta_obligatorio_fuente_calefaccion(self, fastapi_client):
        payload = {k: v for k, v in PAYLOAD_MINIMO.items() if k != "fuente_calefaccion"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 422

    def test_falta_obligatorio_fuente_agua_caliente(self, fastapi_client):
        payload = {k: v for k, v in PAYLOAD_MINIMO.items() if k != "fuente_agua_caliente"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 422

    def test_falta_obligatorio_zona_fria(self, fastapi_client):
        payload = {k: v for k, v in PAYLOAD_MINIMO.items() if k != "zona_fria"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 422


class TestSchemaDefaults:
    """Tests unitarios del schema Pydantic sin pasar por FastAPI."""

    def test_defaults_correctos(self):
        req = AnalisisRequest.model_validate(PAYLOAD_MINIMO)
        # defaults aplicados a los 5 opcionales
        assert req.metros_cuadrados == 1000.0
        assert req.antiguedad_vivienda == 50
        assert req.calidad_aislamiento == "Media"
        assert req.horas_alto_consumo == 8
        assert req.cantidad_equipos == 15

    def test_seis_obligatorias(self):
        req = AnalisisRequest.model_validate(PAYLOAD_MINIMO)
        assert req.consumo_kwh == 250.0
        assert req.tipo_inmueble == "Casa"
        assert req.uso_horario_pico == "No"
        assert req.fuente_calefaccion == "Electricidad"
        assert req.fuente_agua_caliente == "Electricidad"
        assert req.zona_fria == "No"

    def test_payload_vacio_falla(self):
        with pytest.raises(ValueError):
            AnalisisRequest.model_validate({})

    def test_consumo_negativo_falla(self):
        with pytest.raises(ValueError):
            AnalisisRequest.model_validate({**PAYLOAD_MINIMO, "consumo_kwh": -1})

    def test_horas_fuera_de_rango_falla(self):
        with pytest.raises(ValueError):
            AnalisisRequest.model_validate({**PAYLOAD_MINIMO, "horas_alto_consumo": 25})

    def test_cantidad_equipos_negativa_falla(self):
        with pytest.raises(ValueError):
            AnalisisRequest.model_validate({**PAYLOAD_MINIMO, "cantidad_equipos": -1})


class TestApiFileNotFound:
    def test_sin_modelo_devuelve_503(self, monkeypatch, tmp_artifact_dir):
        import os
        os.environ["MODEL_PATH"] = str(tmp_artifact_dir / "no_existe.joblib")

        from fastapi.testclient import TestClient
        from interfaces.api import app as app_module

        monkeypatch.setattr(app_module, "MODEL_PATH", str(tmp_artifact_dir / "no_existe.joblib"))
        client = TestClient(app_module.app)

        r = client.post("/analisis-energetico", json=PAYLOAD_COMPLETO)
        assert r.status_code == 503
        assert "make pipeline" in r.json()["detail"].lower() or "modelo" in r.json()["detail"].lower()
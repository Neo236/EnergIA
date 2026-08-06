import pytest

from interfaces.api.schemas import AnalisisRequest


PAYLOAD_COMPLETO = {
    "consumo_kwh": 363.4,
    "uso_horario_pico": True,
    "cantidad_equipos": 19,
    "tipo_inmueble": "Departamento",
    "horas_alto_consumo": 14,
    "calidad_aislamiento": "Muy Baja",
    "metros_cuadrados": 1269,
    "antiguedad_vivienda": 61,
    "zona_fria": False,
    "fuente_calefaccion": "Solar",
    "fuente_agua_caliente": "Electricidad",
}

PAYLOAD_MINIMO = {
    "consumo_kwh": 250.0,
    "tipo_inmueble": "Casa",
    "cantidad_equipos": 8,
    "horas_alto_consumo": 4,
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
        """Solo los 4 campos obligatorios deben ser suficientes."""
        r = fastapi_client.post("/analisis-energetico", json=PAYLOAD_MINIMO)
        assert r.status_code == 200
        body = r.json()
        assert body["categoria"] in {"Eficiente", "Moderado", "Ineficiente"}
        # costo = consumo_kwh * 0.75
        assert body["costo_estimado_mensual"] == pytest.approx(250.0 * 0.75, rel=0.01)
        assert isinstance(body["recomendaciones"], list)

    def test_analisis_energetico_opcional_default(self, fastapi_client):
        """Si omito un opcional, debe usar el default Pydantic."""
        payload = {
            "consumo_kwh": 200.0,
            "tipo_inmueble": "Casa",
            "cantidad_equipos": 5,
            "horas_alto_consumo": 3,
            # metros_cuadrados omitido -> default 1000.0
            # antiguedad_vivienda omitido -> default 50
            # zona_fria omitido -> default False
            # calidad_aislamiento omitido -> default "Media"
            # fuente_* omitido -> default "Electricidad"
            # uso_horario_pico omitido -> default False
        }
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 200

    def test_analisis_energetico_tipo_inmueble_invalido(self, fastapi_client):
        payload = {**PAYLOAD_COMPLETO, "tipo_inmueble": "Garaje"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 422
        body = r.json()
        assert "detail" in body
        assert any(
            err["loc"][-1] == "tipo_inmueble"
            for err in body["detail"]
        )

    def test_analisis_energetico_horas_invalidas(self, fastapi_client):
        payload = {**PAYLOAD_COMPLETO, "horas_alto_consumo": 30}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 422

    def test_analisis_energetico_aislamiento_invalido(self, fastapi_client):
        payload = {**PAYLOAD_COMPLETO, "calidad_aislamiento": "Super Alta"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 422

    def test_falta_obligatorio_consumo_kwh(self, fastapi_client):
        r = fastapi_client.post("/analisis-energetico", json={
            "tipo_inmueble": "Casa", "cantidad_equipos": 5, "horas_alto_consumo": 3
        })
        assert r.status_code == 422

    def test_falta_obligatorio_tipo_inmueble(self, fastapi_client):
        r = fastapi_client.post("/analisis-energetico", json={
            "consumo_kwh": 100, "cantidad_equipos": 5, "horas_alto_consumo": 3
        })
        assert r.status_code == 422

    def test_falta_obligatorio_cantidad_equipos(self, fastapi_client):
        r = fastapi_client.post("/analisis-energetico", json={
            "consumo_kwh": 100, "tipo_inmueble": "Casa", "horas_alto_consumo": 3
        })
        assert r.status_code == 422

    def test_falta_obligatorio_horas_alto_consumo(self, fastapi_client):
        r = fastapi_client.post("/analisis-energetico", json={
            "consumo_kwh": 100, "tipo_inmueble": "Casa", "cantidad_equipos": 5
        })
        assert r.status_code == 422


class TestSchemaDefaults:
    """Tests unitarios del schema Pydantic sin pasar por FastAPI."""

    def test_defaults_correctos(self):
        req = AnalisisRequest.model_validate(PAYLOAD_MINIMO)
        # defaults aplicados a los opcionales
        assert req.metros_cuadrados == 1000.0
        assert req.antiguedad_vivienda == 50
        assert req.zona_fria is False
        assert req.calidad_aislamiento == "Media"
        assert req.fuente_calefaccion == "Electricidad"
        assert req.fuente_agua_caliente == "Electricidad"
        assert req.uso_horario_pico is False

    def test_cuatro_obligatorias(self):
        req = AnalisisRequest.model_validate(PAYLOAD_MINIMO)
        assert req.consumo_kwh == 250.0
        assert req.tipo_inmueble == "Casa"
        assert req.cantidad_equipos == 8
        assert req.horas_alto_consumo == 4

    def test_payload_vacio_falla(self):
        with pytest.raises(ValueError):
            AnalisisRequest.model_validate({})

    def test_consumo_negativo_falla(self):
        with pytest.raises(ValueError):
            AnalisisRequest.model_validate({**PAYLOAD_MINIMO, "consumo_kwh": -1})

    def test_horas_fuera_de_rango_falla(self):
        with pytest.raises(ValueError):
            AnalisisRequest.model_validate({**PAYLOAD_MINIMO, "horas_alto_consumo": 25})


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

import pytest


PAYLOAD_VALIDO = {
    "consumo_electrico_kwh": 363.4,
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
        r = fastapi_client.post("/analisis-energetico", json=PAYLOAD_VALIDO)
        assert r.status_code == 200
        body = r.json()
        assert body["categoria"] in {"Eficiente", "Moderado", "Ineficiente"}
        assert 0.0 <= body["probabilidad"] <= 1.0
        assert body["costo_estimado_mensual"] == pytest.approx(363.4 * 0.75, rel=0.01)
        assert isinstance(body["recomendaciones"], list)
        assert len(body["recomendaciones"]) >= 1

    def test_analisis_energetico_tipo_inmueble_invalido(self, fastapi_client):
        payload = {**PAYLOAD_VALIDO, "tipo_inmueble": "Garaje"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 422
        body = r.json()
        assert "detail" in body
        assert any(
            err["loc"][-1] == "tipo_inmueble"
            for err in body["detail"]
        )

    def test_analisis_energetico_horas_invalidas(self, fastapi_client):
        payload = {**PAYLOAD_VALIDO, "horas_alto_consumo": 30}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 422

    def test_analisis_energetico_aislamiento_invalido(self, fastapi_client):
        payload = {**PAYLOAD_VALIDO, "calidad_aislamiento": "Super Alta"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 422

    def test_campos_requeridos_faltantes(self, fastapi_client):
        r = fastapi_client.post("/analisis-energetico", json={"consumo_electrico_kwh": 100})
        assert r.status_code == 422


class TestApiFileNotFound:
    def test_sin_modelo_devuelve_503(self, monkeypatch, tmp_artifact_dir):
        import os
        os.environ["MODEL_PATH"] = str(tmp_artifact_dir / "no_existe.joblib")

        from fastapi.testclient import TestClient
        from interfaces.api import app as app_module

        monkeypatch.setattr(app_module, "MODEL_PATH", str(tmp_artifact_dir / "no_existe.joblib"))
        client = TestClient(app_module.app)

        r = client.post("/analisis-energetico", json=PAYLOAD_VALIDO)
        assert r.status_code == 503
        assert "make pipeline" in r.json()["detail"].lower() or "modelo" in r.json()["detail"].lower()
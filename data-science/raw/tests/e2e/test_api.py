import hashlib
import os
from pathlib import Path

import pytest

from interfaces.api.schemas import AnalisisRequest


# 6 obligatorias + 5 opcionales (ver docstring de AnalisisRequest)
PAYLOAD_COMPLETO = {
    # --- obligatorias ---
    "consumo_kwh": 363.4,
    "tipo_inmueble": "Departamento",
    "uso_horario_pico": True,
    "fuente_calefaccion": "Solar",
    "fuente_agua_caliente": "Electricidad",
    "zona_fria": False,
    # --- opcionales ---
    "metros_cuadrados": 1269,
    "antiguedad_vivienda": 61,
    "calidad_aislamiento": "Muy Baja",
    "horas_alto_consumo": 14,
    "cantidad_equipos": 19,
}

# Solo las 4 obligatorias (alineadas con @NotNull del backend);
# las 7 opcionales se imputan por default en el ML.
PAYLOAD_MINIMO = {
    "consumo_kwh": 250.0,
    "tipo_inmueble": "Casa",
    "horas_alto_consumo": 4,
    "cantidad_equipos": 10,
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

    def test_model_info(self, fastapi_client, trained_model):
        """El hash reportado debe ser el del .joblib real, no uno arbitrario.

        Es la garantia que sostiene el informe de certificacion: si este
        endpoint devolviera un hash que no corresponde al archivo en disco,
        identificar la version del modelo desplegado dejaria de ser posible.
        """
        ruta = Path(trained_model["model_path"])
        esperado = hashlib.sha256(ruta.read_bytes()).hexdigest()

        r = fastapi_client.get("/model-info")
        assert r.status_code == 200
        body = r.json()
        assert body["sha256"] == esperado
        assert body["size_bytes"] == ruta.stat().st_size
        assert body["model_path"] == str(ruta)
        assert body["mtime_utc"].endswith("Z")
        assert isinstance(body["loaded"], bool)
        assert body["storage_backend"] == os.getenv("STORAGE_BACKEND", "local")

    def test_model_info_sin_modelo(self, fastapi_client, monkeypatch, tmp_path):
        """Sin archivo de modelo el endpoint responde 503, no 500.

        Mismo criterio que /health: la ausencia del artefacto es
        indisponibilidad temporal del servicio, no un error del cliente ni una
        falla interna. Cubre tambien el camino sin chequeo previo de
        os.path.exists() - el FileNotFoundError del open() se traduce a 503.
        """
        from interfaces.api import app as app_module

        monkeypatch.setattr(app_module, "MODEL_PATH", str(tmp_path / "no-existe.joblib"))

        r = fastapi_client.get("/model-info")
        assert r.status_code == 503
        assert "no encontrado" in r.json()["detail"]

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
        """Si omito los 7 opcionales, debe usar los defaults Pydantic."""
        payload = {
            "consumo_kwh": 200.0,
            "tipo_inmueble": "Casa",
            "horas_alto_consumo": 6,
            "cantidad_equipos": 12,
            # uso_horario_pico omitido -> default False
            # zona_fria omitido -> default False
            # fuente_calefaccion omitido -> default "Electricidad"
            # fuente_agua_caliente omitido -> default "Electricidad"
            # metros_cuadrados omitido -> default 1000.0
            # antiguedad_vivienda omitido -> default 50
            # calidad_aislamiento omitido -> default "Media"
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
        """uso_horario_pico es opcional en backend (DatosRegistroConsumo
        sin @NotNull) y en ML (default False). Jackson con NON_NULL lo
        omite cuando es null; el ML debe imputar el default."""
        payload = {k: v for k, v in PAYLOAD_MINIMO.items() if k != "uso_horario_pico"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 200
        assert r.json()["categoria"] in {"Eficiente", "Moderado", "Ineficiente"}

    def test_falta_obligatorio_fuente_calefaccion(self, fastapi_client):
        """fuente_calefaccion opcional; default 'Electricidad'."""
        payload = {k: v for k, v in PAYLOAD_MINIMO.items() if k != "fuente_calefaccion"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 200

    def test_falta_obligatorio_fuente_agua_caliente(self, fastapi_client):
        """fuente_agua_caliente opcional; default 'Electricidad'."""
        payload = {k: v for k, v in PAYLOAD_MINIMO.items() if k != "fuente_agua_caliente"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 200

    def test_falta_obligatorio_zona_fria(self, fastapi_client):
        """zona_fria opcional; default False."""
        payload = {k: v for k, v in PAYLOAD_MINIMO.items() if k != "zona_fria"}
        r = fastapi_client.post("/analisis-energetico", json=payload)
        assert r.status_code == 200


class TestSchemaDefaults:
    """Tests unitarios del schema Pydantic sin pasar por FastAPI."""

    def test_defaults_correctos(self):
        """Los 7 opcionales imputan sus defaults cuando el front no los manda
        (caso real: backend con @JsonInclude(NON_NULL) los omite del JSON)."""
        req = AnalisisRequest.model_validate(PAYLOAD_MINIMO)
        assert req.uso_horario_pico is False
        assert req.zona_fria is False
        assert req.fuente_calefaccion == "Electricidad"
        assert req.fuente_agua_caliente == "Electricidad"
        assert req.metros_cuadrados == 1000.0
        assert req.antiguedad_vivienda == 50
        assert req.calidad_aislamiento == "Media"

    def test_cuatro_obligatorias(self):
        """Consumo_kwh, tipo_inmueble, horas_alto_consumo, cantidad_equipos
        son las 4 obligatorias (alineadas con @NotNull del backend)."""
        req = AnalisisRequest.model_validate(PAYLOAD_MINIMO)
        assert req.consumo_kwh == 250.0
        assert req.tipo_inmueble == "Casa"
        assert req.horas_alto_consumo == 4
        assert req.cantidad_equipos == 10

    def test_siete_opcionales_aplican_defaults(self):
        """Los 7 opcionales del backend deben imputar defaults consistentes."""
        req = AnalisisRequest.model_validate(PAYLOAD_MINIMO)
        assert req.uso_horario_pico is False
        assert req.zona_fria is False
        assert req.fuente_calefaccion == "Electricidad"
        assert req.fuente_agua_caliente == "Electricidad"
        assert req.metros_cuadrados == 1000.0
        assert req.antiguedad_vivienda == 50
        assert req.calidad_aislamiento == "Media"

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


class TestBackendContract:
    """Validacion del contrato HTTP backend (Spring) -> ML (FastAPI).

    Reproduce payloads reales del backend (ver
    `backend/.../client/MlClient.java` y
    `backend/.../dto/DatosRegistroConsumo.java`). El backend serializa con
    Jackson + `@JsonInclude(NON_NULL)`, asi que campos opcionales con null
    simplemente se omiten del JSON.
    """

    def test_payload_completo_del_backend(self, fastapi_client):
        """Lo que Jackson serializa cuando el front lleno los 11 campos."""
        r = fastapi_client.post("/analisis-energetico", json=PAYLOAD_COMPLETO)
        assert r.status_code == 200
        body = r.json()
        assert set(body) >= {"categoria", "probabilidad",
                             "costo_estimado_mensual", "recomendaciones"}

    def test_payload_minimo_solo_obligatorios_back(self, fastapi_client):
        """Caso real: front lleno solo los 4 obligatorios del backend.
        Jackson NON_NULL omite los 7 opcionales. ML debe imputar defaults
        y devolver 200."""
        r = fastapi_client.post("/analisis-energetico", json=PAYLOAD_MINIMO)
        assert r.status_code == 200
        body = r.json()
        assert body["categoria"] in {"Eficiente", "Moderado", "Ineficiente"}

    def test_payload_backend_con_tipo_inmueble_invalido(self, fastapi_client):
        """Enum no soportado: el back lo rechaza antes pero el ML tambien."""
        r = fastapi_client.post(
            "/analisis-energetico",
            json={**PAYLOAD_MINIMO, "tipo_inmueble": "Garaje"},
        )
        assert r.status_code == 422

    def test_payload_backend_consumo_fuera_de_rango(self, fastapi_client):
        """1500 kWh excede DecimalMax=1000 del backend; documenta el limite
        que el ML tambien enforce (le=1000)."""
        r = fastapi_client.post(
            "/analisis-energetico",
            json={**PAYLOAD_MINIMO, "consumo_kwh": 1500.0},
        )
        assert r.status_code == 422

    def test_payload_backend_metros_cuadrados_invalido(self, fastapi_client):
        """Backend @Min(26) para metros_cuadrados; ML enforza lo mismo."""
        r = fastapi_client.post(
            "/analisis-energetico",
            json={**PAYLOAD_MINIMO, "metros_cuadrados": 10},
        )
        assert r.status_code == 422
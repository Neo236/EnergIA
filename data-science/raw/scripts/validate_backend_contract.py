"""Valida el contrato HTTP entre el backend (Spring) y el servicio ML (FastAPI).

El backend Java envia al servicio ML exactamente lo que Jackson serializa
desde `DatosRegistroConsumo` (ver
`backend/.../client/MlClient.java:27-72` y
`backend/.../dto/DatosRegistroConsumo.java`). Este script reproduce ese
payload y lo postea al endpoint, verificando que la API ML lo acepte y
devuelva la forma esperada.

Por que existe: el contrato se rompe silenciosamente cuando cambia un tipo,
un enum o un rango de validacion sin que la otra parte se entere. Estos
test detectan el drift antes de llegar a produccion.

Uso:
    python scripts/validate_backend_contract.py            # TestClient in-process
    python scripts/validate_backend_contract.py --url http://ml-service:8000
    python scripts/validate_backend_contract.py --json    # output parseable
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

# Permite ejecutar este script directamente (sin pytest): agrega la raiz
# del proyecto a sys.path para que `from interfaces.api import ...` funcione.
_RAIZ = Path(__file__).resolve().parents[1]
if str(_RAIZ) not in sys.path:
    sys.path.insert(0, str(_RAIZ))

from fastapi.testclient import TestClient

from interfaces.api import app as app_module


log = logging.getLogger("validate_backend")


# ---------------------------------------------------------------------------
# Payloads: replican exactamente lo que Jackson serializa desde
# DatosRegistroConsumo. Tipos y valores validados contra el codigo del back.
# ---------------------------------------------------------------------------

def payload_completo() -> dict[str, Any]:
    """Todos los 11 campos presentes, valores realistas.

    Equivalente a un POST del backend cuando el front lleno el formulario
    completo y todos los opcionales llegaron con valor.
    """
    return {
        # obligatorios
        "consumo_kwh": 450.5,        # Double
        "cantidad_equipos": 8,       # Integer
        "tipo_inmueble": "Casa",     # enum display case
        "uso_horario_pico": True,    # Boolean
        "horas_alto_consumo": 6,     # Integer
        # opcionales (con valor)
        "metros_cuadrados": 30,      # Integer (backend), ML espera float
        "antiguedad_vivienda": 34,   # Integer
        "zona_fria": False,          # Boolean
        "calidad_aislamiento": "Media",      # enum
        "fuente_calefaccion": "Solar",       # enum
        "fuente_agua_caliente": "Electricidad",  # enum
    }


def payload_minimo() -> dict[str, Any]:
    """Backend con @JsonInclude(NON_NULL) omite los nulls.

    Resultado: solo los 4 obligatorios del backend serializan. La API ML
    imputa defaults para los 7 opcionales (uso_horario_pico=False,
    zona_fria=False, fuente_calefaccion='Electricidad',
    fuente_agua_caliente='Electricidad', metros_cuadrados=1000.0,
    antiguedad_vivienda=50, calidad_aislamiento='Media').
    """
    return {
        "consumo_kwh": 250.0,
        "cantidad_equipos": 15,
        "tipo_inmueble": "Casa",
        "horas_alto_consumo": 4,
        # uso_horario_pico: omitido por Jackson (null en el DTO)
        # zona_fria: omitido
        # metros_cuadrados: omitido
        # antiguedad_vivienda: omitido
        # calidad_aislamiento: omitido
        # fuente_calefaccion: omitido
        # fuente_agua_caliente: omitido
    }


def payload_consumo_kwh_1_min() -> dict[str, Any]:
    """Caso borde: backend DecimalMin=1.0 permite el minimo."""
    return {
        "consumo_kwh": 1.0,
        "cantidad_equipos": 1,
        "tipo_inmueble": "Pyme",
        "horas_alto_consumo": 0,
    }


def payload_fuera_de_rango() -> dict[str, Any]:
    """Caso borde: 1001 kWh excede el DecimalMax=1000 del backend.
    Como este payload simula un bypass del @Valid del back, la API ML
    debe rechazarlo (le=1000). Documenta el contrato esperado."""
    return {
        "consumo_kwh": 1500.0,
        "cantidad_equipos": 5,
        "tipo_inmueble": "Casa",
        "horas_alto_consumo": 5,
    }


def payload_enum_invalido() -> dict[str, Any]:
    """Caso borde: enum que el backend rechaza pero documenta el comportamiento
    de la API ML si el contrato se rompe aguas abajo."""
    return {
        "consumo_kwh": 100.0,
        "cantidad_equipos": 3,
        "tipo_inmueble": "Garaje",   # no existe
        "horas_alto_consumo": 4,
    }


def payload_metros_invalido() -> dict[str, Any]:
    """Caso borde: backend @Min(26) para metros_cuadrados."""
    return {
        "consumo_kwh": 100.0,
        "cantidad_equipos": 3,
        "tipo_inmueble": "Casa",
        "horas_alto_consumo": 4,
        "metros_cuadrados": 10,  # < 26, debe rechazarse
    }


# ---------------------------------------------------------------------------
# Escenarios: cada uno declara expected_status y campos de respuesta esperados
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Scenario:
    name: str
    payload: dict[str, Any]
    expected_status: int
    expected_keys: tuple[str, ...] = ()
    description: str = ""


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        name="completo",
        description="11 campos, todos con valor",
        payload=payload_completo(),
        expected_status=200,
        expected_keys=(
            "categoria", "probabilidad",
            "costo_estimado_mensual", "recomendaciones",
        ),
    ),
    Scenario(
        name="minimo_solo_obligatorios_back",
        description="Backend con NON_NULL omite los 7 opcionales; ML imputa defaults",
        payload=payload_minimo(),
        expected_status=200,
        expected_keys=(
            "categoria", "probabilidad",
            "costo_estimado_mensual", "recomendaciones",
        ),
    ),
    Scenario(
        name="min_consumo_kwh_1",
        description="borde inferior DecimalMin 1.0 del backend",
        payload=payload_consumo_kwh_1_min(),
        expected_status=200,
        expected_keys=(
            "categoria", "probabilidad",
            "costo_estimado_mensual", "recomendaciones",
        ),
    ),
    Scenario(
        name="consumo_kwh_fuera_de_rango",
        description="1500 kWh excede limite; API ML debe rechazar",
        payload=payload_fuera_de_rango(),
        expected_status=422,
    ),
    Scenario(
        name="enum_tipo_inmueble_invalido",
        description="tipo_inmueble='Garaje' no existe; API ML debe rechazar",
        payload=payload_enum_invalido(),
        expected_status=422,
    ),
    Scenario(
        name="metros_cuadrados_invalido",
        description="10 < 26 (backend @Min(26)); API ML debe rechazar",
        payload=payload_metros_invalido(),
        expected_status=422,
    ),
)


def _run_scenario(client: TestClient, scenario: Scenario) -> dict[str, Any]:
    """Ejecuta un escenario contra el cliente. Devuelve un dict con el
    resultado estructurado para reporte."""
    start = time.perf_counter()
    response = client.post("/analisis-energetico", json=scenario.payload)
    elapsed_ms = (time.perf_counter() - start) * 1000

    body: Any
    try:
        body = response.json()
    except Exception:
        body = response.text

    passed = response.status_code == scenario.expected_status
    if passed and scenario.expected_keys:
        passed = isinstance(body, dict) and all(k in body for k in scenario.expected_keys)

    missing_keys: list[str] = []
    if isinstance(body, dict) and scenario.expected_keys:
        missing_keys = [k for k in scenario.expected_keys if k not in body]

    return {
        "scenario": scenario.name,
        "description": scenario.description,
        "expected_status": scenario.expected_status,
        "actual_status": response.status_code,
        "passed": passed,
        "elapsed_ms": round(elapsed_ms, 2),
        "missing_keys": missing_keys,
        "body": body,
    }


def validate(client: TestClient, scenarios: tuple[Scenario, ...] = SCENARIOS) -> list[dict[str, Any]]:
    return [_run_scenario(client, s) for s in scenarios]


def format_report_text(results: list[dict[str, Any]]) -> str:
    lines = ["=" * 72, "BACKEND -> ML CONTRACT VALIDATION", "=" * 72]
    for r in results:
        marker = "PASS" if r["passed"] else "FAIL"
        lines.append(
            f"[{marker}] {r['scenario']:<40} "
            f"status={r['actual_status']} "
            f"(expected {r['expected_status']}) "
            f"{r['elapsed_ms']}ms"
        )
        if r["description"]:
            lines.append(f"        {r['description']}")
        if r["missing_keys"]:
            lines.append(f"        missing keys: {r['missing_keys']}")
        if not r["passed"]:
            lines.append(f"        body: {json.dumps(r['body'], ensure_ascii=False)[:300]}")

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    lines.append("-" * 72)
    lines.append(f"RESULT: {passed}/{total} escenarios pasaron")
    return "\n".join(lines)


def format_report_json(results: list[dict[str, Any]]) -> str:
    passed = sum(1 for r in results if r["passed"])
    payload = {
        "passed": passed,
        "total": len(results),
        "all_passed": passed == len(results),
        "scenarios": [
            {
                "scenario": r["scenario"],
                "description": r["description"],
                "expected_status": r["expected_status"],
                "actual_status": r["actual_status"],
                "passed": r["passed"],
                "elapsed_ms": r["elapsed_ms"],
                "missing_keys": r["missing_keys"],
            }
            for r in results
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument(
        "--url",
        default="",
        help=(
            "URL del servicio ML (ej: http://ml-service:8000). "
            "Si esta vacio, usa TestClient in-process."
        ),
    )
    p.add_argument(
        "--json", action="store_true", dest="json_output",
        help="output en formato JSON parseable",
    )
    p.add_argument(
        "--train-if-missing", action="store_true",
        help=(
            "Si el modelo no esta disponible, entrena uno pequeno en un "
            "directorio temporal antes de validar. Util para CI/dev."
        ),
    )
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def _ensure_model_for_in_process() -> str:
    """Garantiza que haya un modelo entrenado para TestClient in-process.

    Si MODEL_PATH no existe, entrena uno pequeno en /tmp y actualiza
    `app_module.MODEL_PATH`. Devuelve el path del modelo.
    """
    from pathlib import Path
    import tempfile

    from application.training import entrenar_y_guardar_modelo
    from infrastructure.data.simulation import generar_dataset

    model_path = Path(getattr(app_module, "MODEL_PATH", "data/modelo_eficiencia_v1.joblib"))
    if model_path.exists():
        return str(model_path)

    log.warning("Modelo no encontrado en %s; entrenando uno pequeno en /tmp", model_path)
    tmpdir = Path(tempfile.mkdtemp(prefix="validate_backend_"))
    new_model = tmpdir / "modelo.joblib"
    new_metrics = tmpdir / "metricas.joblib"
    df = generar_dataset(num_clientes=300, seed=42)
    entrenar_y_guardar_modelo(
        df=df,
        output_path=str(new_model),
        metricas_path=str(new_metrics),
        random_seed=42,
    )
    app_module.MODEL_PATH = str(new_model)
    log.info("Modelo entrenado en %s", new_model)
    return str(new_model)


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.url:
        import requests
        log.info("Usando requests contra %s", args.url)

        class _RequestsClient:
            def __init__(self, base_url: str) -> None:
                self.base_url = base_url.rstrip("/")
                self.session = requests.Session()

            def post(self, path: str, json: dict[str, Any]) -> Any:
                resp = self.session.post(
                    f"{self.base_url}{path}", json=json, timeout=30
                )
                return resp

        client: Any = _RequestsClient(args.url)
    else:
        log.info("Usando TestClient in-process")
        if args.train_if_missing:
            _ensure_model_for_in_process()
        client = TestClient(app_module.app)

    results = validate(client)
    output = format_report_json(results) if args.json_output else format_report_text(results)
    print(output)

    all_passed = all(r["passed"] for r in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

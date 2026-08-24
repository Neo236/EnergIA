"""Verifica el contrato entre el dataset local (generado por Python) y el
consumidor Colab (notebook EDA).

Fuente de verdad: el codigo Python
  - infrastructure/data/simulation.py   (genera el dataset)
  - domain/scoring.py                   (reglas IEE + categoria)
  - interfaces/api/schemas.py           (contrato API)

La notebook Colab (`raw/notebooks/data_colab.ipynb`) es un consumidor
EDA: descarga `database_beta.json` desde la rama `develop` y hace
analisis / visualizacion / tests estadisticos.

Este modulo valida que el archivo `database_beta.json` que el pipeline
Python produce tiene las 13 columnas y los tipos exactos que la
notebook espera consumir. Si alguien renombra una columna, cambia un
tipo, o agrega/quita una feature en `simulation.py`, este check falla
con un mensaje claro indicando que el contrato se rompio.

Exit codes:
  0 -> contrato OK (o warning menor)
  1 -> contrato violado (cambio breaking)
  2 -> artefacto faltante (ejecuta `make pipeline` primero)

Uso:
  python -m interfaces.cli.verify_notebook_contract
  python -m interfaces.cli.verify_notebook_contract --json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import pandas as pd


log = logging.getLogger("verify_notebook_contract")


# Contrato canonico del dataset. Single source of truth para este check.
# Debe coincidir con:
#   - infrastructure/data/simulation.py  (lo que se genera)
#   - domain/scoring.py                  (uso de las columnas)
#   - interfaces/api/schemas.py          (AnalisisRequest)
#   - raw/notebooks/data_colab.ipynb     (lo que la notebook consume)
EXPECTED_COLUMNS: dict[str, str] = {
    # string identifier
    "hogar_id": "string",
    # categoricas (orden NO importa para el schema)
    "tipo_inmueble": "string",
    "calidad_aislamiento": "string",
    "fuente_calefaccion": "string",
    "fuente_agua_caliente": "string",
    # bool-like: string "Si"/"No" (la notebook hace .map a True/False)
    "zona_fria": "string:Si/No",
    "uso_horario_pico": "string:Si/No",
    # numericas enteras
    "metros_cuadrados": "int",
    "antiguedad_vivienda": "int",
    "horas_alto_consumo": "int",
    "cantidad_equipos": "int",
    # numerica float
    "consumo_kwh": "float",
    # target
    "categoria": "string:{Eficiente,Moderado,Ineficiente}",
}

EXPECTED_CATEGORIES = {"Eficiente", "Moderado", "Ineficiente"}


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    detail: str = ""


@dataclass(frozen=True)
class ContractReport:
    dataset_path: str
    dataset_exists: bool
    shape: tuple[int, int] | None
    checks: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.ok for c in self.checks)

    def to_dict(self) -> dict:
        return {
            "dataset_path": self.dataset_path,
            "dataset_exists": self.dataset_exists,
            "shape": list(self.shape) if self.shape else None,
            "passed": self.passed,
            "checks": [asdict(c) for c in self.checks],
        }


def _check_dtype(series: pd.Series, expected: str) -> tuple[bool, str]:
    """Valida dtype segun la especificacion del contrato."""
    kind = series.dtype.kind
    if expected.startswith("string"):
        if kind not in ("O", "U", "S"):
            return False, f"dtype.kind={kind!r}, esperaba string"
        # Validadores extra segun el subtipo
        if expected == "string:Si/No":
            vals = set(series.unique())
            if not vals.issubset({"Si", "No"}):
                return False, f"valores fuera de {{'Si','No'}}: {vals}"
        elif expected.startswith("string:{") and expected.endswith("}"):
            allowed = set(expected[len("string:{") : -1].split(","))
            vals = set(series.unique())
            if not vals.issubset(allowed):
                return False, f"valores fuera de {allowed}: {vals}"
        return True, ""
    if expected == "int":
        if kind != "i":
            return False, f"dtype.kind={kind!r}, esperaba int"
        return True, ""
    if expected == "float":
        if kind != "f":
            return False, f"dtype.kind={kind!r}, esperaba float"
        return True, ""
    return False, f"dtype esperado desconocido: {expected!r}"


def verify(dataset_path: Path) -> ContractReport:
    """Ejecuta todas las checks del contrato sobre `dataset_path`.

    Returns:
        ContractReport con el resultado de cada check individual.
    """
    if not dataset_path.exists():
        return ContractReport(
            dataset_path=str(dataset_path),
            dataset_exists=False,
            shape=None,
            checks=[CheckResult(
                "dataset_exists",
                False,
                f"Dataset no encontrado en {dataset_path}. "
                "Ejecuta `make pipeline` para regenerarlo.",
            )],
        )

    df = pd.read_json(dataset_path)
    checks: list[CheckResult] = []

    # 1. Columnas: existen todas las esperadas, no hay extras.
    expected = set(EXPECTED_COLUMNS.keys())
    actual = set(df.columns)
    missing = expected - actual
    extra = actual - expected
    if missing or extra:
        checks.append(CheckResult(
            "columns_match",
            False,
            f"missing={sorted(missing) or '[]'}, extra={sorted(extra) or '[]'}",
        ))
    else:
        checks.append(CheckResult("columns_match", True, "13/13 columnas OK"))

    # 2. Dtype por columna.
    for col, expected_dtype in EXPECTED_COLUMNS.items():
        if col not in df.columns:
            continue  # ya reportado arriba
        ok, detail = _check_dtype(df[col], expected_dtype)
        checks.append(CheckResult(f"dtype:{col}", ok, detail))

    # 3. hogar_id unico.
    if "hogar_id" in df.columns:
        nunique = df["hogar_id"].nunique()
        nrows = len(df)
        checks.append(CheckResult(
            "hogar_id_unique",
            nunique == nrows,
            f"{nunique}/{nrows} unicos",
        ))

    # 4. categoria ∈ contrato.
    if "categoria" in df.columns:
        cats = set(df["categoria"].unique())
        checks.append(CheckResult(
            "categoria_in_contract",
            cats.issubset(EXPECTED_CATEGORIES),
            f"encontrados: {sorted(cats)}",
        ))

    # 5. Sin nulos en columnas que la notebook usa directamente.
    if not df.empty:
        null_cols = [c for c in df.columns if df[c].isnull().any()]
        checks.append(CheckResult(
            "no_nulls",
            not null_cols,
            f"columnas con nulos: {null_cols}" if null_cols else "sin nulos",
        ))

    return ContractReport(
        dataset_path=str(dataset_path),
        dataset_exists=True,
        shape=(len(df), len(df.columns)),
        checks=checks,
    )


def _build_arg_parser() -> argparse.ArgumentParser:
    from infrastructure.config import Config
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "--dataset",
        type=Path,
        default=Path(Config.OUTPUT_JSON_PATH),
        help="Path al dataset JSON a verificar",
    )
    p.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Imprime el reporte en JSON parseable",
    )
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    report = verify(args.dataset)

    if args.json_output:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        log.info("Dataset: %s", report.dataset_path)
        log.info("Shape: %s", report.shape)
        log.info("Resultado: %s", "OK" if report.passed else "FAIL")
        for c in report.checks:
            symbol = "OK " if c.ok else "FAIL"
            line = f"  [{symbol}] {c.name}"
            if c.detail:
                line += f"  ({c.detail})"
            log.info(line)

    if not report.dataset_exists:
        return 2
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())

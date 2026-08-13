"""Tests del modulo verify_notebook_contract.

Cubre el contrato entre el dataset local (generado por Python) y el
consumidor Colab (notebook EDA). No requiere red ni artefactos
externos: trabaja con JSONs y DataFrames sintéticos en tmp_path.
"""

import json

import pandas as pd
import pytest

from interfaces.cli.verify_notebook_contract import (
    EXPECTED_CATEGORIES,
    EXPECTED_COLUMNS,
    ContractReport,
    _check_dtype,
    main,
    verify,
)


def _make_valid_df(rows: int = 50) -> pd.DataFrame:
    # uso 100.5 (no entero) para que pd.read_json infiera float64;
    # si uso 100.0, pandas lo red round-trip a int64 y rompe el contrato.
    return pd.DataFrame({
        "hogar_id": [f"Hogar_{i:04d}" for i in range(1, rows + 1)],
        "tipo_inmueble": ["Casa"] * rows,
        "metros_cuadrados": pd.Series([100] * rows, dtype="int64"),
        "antiguedad_vivienda": pd.Series([10] * rows, dtype="int64"),
        "zona_fria": pd.Series(["Si"] * rows, dtype="object"),
        "calidad_aislamiento": ["Media"] * rows,
        "fuente_calefaccion": ["Electricidad"] * rows,
        "fuente_agua_caliente": ["Electricidad"] * rows,
        "consumo_kwh": pd.Series([100.5] * rows, dtype="float64"),
        "uso_horario_pico": pd.Series(["No"] * rows, dtype="object"),
        "horas_alto_consumo": pd.Series([5] * rows, dtype="int64"),
        "cantidad_equipos": pd.Series([10] * rows, dtype="int64"),
        "categoria": ["Moderado"] * rows,
    })


class TestCheckDtype:
    def test_string_passing(self):
        s = pd.Series(["a", "b"], dtype="object")
        ok, _ = _check_dtype(s, "string")
        assert ok

    def test_string_subtype_sino_passing(self):
        s = pd.Series(["Si", "No"], dtype="object")
        ok, _ = _check_dtype(s, "string:Si/No")
        assert ok

    def test_string_subtype_sino_fails_on_other(self):
        s = pd.Series(["Si", "Quizas"], dtype="object")
        ok, detail = _check_dtype(s, "string:Si/No")
        assert not ok
        assert "Quizas" in detail

    def test_string_subtype_categoria_passing(self):
        s = pd.Series(["Eficiente", "Moderado", "Ineficiente"], dtype="object")
        ok, _ = _check_dtype(s, "string:{Eficiente,Moderado,Ineficiente}")
        assert ok

    def test_string_subtype_categoria_fails_on_unknown(self):
        s = pd.Series(["Eficiente", "Rara"], dtype="object")
        ok, _ = _check_dtype(s, "string:{Eficiente,Moderado,Ineficiente}")
        assert not ok

    def test_int_passing(self):
        s = pd.Series([1, 2, 3], dtype="int64")
        ok, _ = _check_dtype(s, "int")
        assert ok

    def test_int_fails_on_float(self):
        s = pd.Series([1.0, 2.0], dtype="float64")
        ok, detail = _check_dtype(s, "int")
        assert not ok
        assert "int" in detail

    def test_float_passing(self):
        s = pd.Series([1.0, 2.0], dtype="float64")
        ok, _ = _check_dtype(s, "float")
        assert ok

    def test_float_fails_on_int(self):
        s = pd.Series([1, 2], dtype="int64")
        ok, _ = _check_dtype(s, "float")
        assert not ok

    def test_unknown_dtype_spec(self):
        s = pd.Series([1, 2])
        ok, detail = _check_dtype(s, "weird_type")
        assert not ok
        assert "desconocido" in detail


class TestVerify:
    def test_dataset_inexistente(self, tmp_path):
        path = tmp_path / "no_existe.json"
        report = verify(path)
        assert not report.dataset_exists
        assert not report.passed
        assert any(c.name == "dataset_exists" for c in report.checks)

    def test_dataset_valido(self, tmp_path):
        path = tmp_path / "ok.json"
        _make_valid_df(50).to_json(path, orient="records")
        report = verify(path)
        assert report.dataset_exists
        assert report.shape == (50, 13)
        assert report.passed
        assert all(c.ok for c in report.checks)

    def test_columna_faltante(self, tmp_path):
        path = tmp_path / "missing.json"
        df = _make_valid_df(10).drop(columns=["consumo_kwh"])
        df.to_json(path, orient="records")
        report = verify(path)
        assert not report.passed
        cols_check = next(c for c in report.checks if c.name == "columns_match")
        assert not cols_check.ok
        assert "consumo_kwh" in cols_check.detail

    def test_columna_extra(self, tmp_path):
        path = tmp_path / "extra.json"
        df = _make_valid_df(10)
        df["columna_rara"] = 1
        df.to_json(path, orient="records")
        report = verify(path)
        assert not report.passed
        cols_check = next(c for c in report.checks if c.name == "columns_match")
        assert not cols_check.ok
        assert "columna_rara" in cols_check.detail

    def test_dtype_incorrecto_zona_fria_bool(self, tmp_path):
        path = tmp_path / "bool.json"
        df = _make_valid_df(10)
        df["zona_fria"] = True
        df.to_json(path, orient="records")
        report = verify(path)
        assert not report.passed
        bad = next(c for c in report.checks
                   if c.name == "dtype:zona_fria")
        assert not bad.ok

    def test_categoria_fuera_de_contrato(self, tmp_path):
        path = tmp_path / "cat_invalida.json"
        df = _make_valid_df(10)
        df.loc[0, "categoria"] = "Rara"
        df.to_json(path, orient="records")
        report = verify(path)
        assert not report.passed
        bad = next(c for c in report.checks
                   if c.name == "categoria_in_contract")
        assert not bad.ok

    def test_hogar_id_duplicado(self, tmp_path):
        path = tmp_path / "dup.json"
        df = _make_valid_df(10)
        df.loc[1, "hogar_id"] = df.loc[0, "hogar_id"]
        df.to_json(path, orient="records")
        report = verify(path)
        assert not report.passed
        dup = next(c for c in report.checks
                   if c.name == "hogar_id_unique")
        assert not dup.ok

    def test_nulos_detectados(self, tmp_path):
        path = tmp_path / "nulls.json"
        df = _make_valid_df(10)
        df.loc[0, "consumo_kwh"] = None
        df.to_json(path, orient="records")
        report = verify(path)
        assert not report.passed
        nulls = next(c for c in report.checks if c.name == "no_nulls")
        assert not nulls.ok
        assert "consumo_kwh" in nulls.detail

    def test_expected_columns_completas(self):
        """El contrato declarado incluye las 13 columnas."""
        assert len(EXPECTED_COLUMNS) == 13
        assert "hogar_id" in EXPECTED_COLUMNS
        assert "categoria" in EXPECTED_COLUMNS
        assert "consumo_kwh" in EXPECTED_COLUMNS
        assert EXPECTED_CATEGORIES == {"Eficiente", "Moderado", "Ineficiente"}

    def test_report_to_dict_serializable(self, tmp_path):
        path = tmp_path / "ok.json"
        _make_valid_df(5).to_json(path, orient="records")
        report = verify(path)
        d = report.to_dict()
        # JSON-serializable
        json.dumps(d)
        assert "checks" in d
        assert "passed" in d
        assert d["passed"] is True


class TestMain:
    def test_main_exit_0_ok(self, tmp_path, monkeypatch):
        path = tmp_path / "ok.json"
        _make_valid_df(5).to_json(path, orient="records")
        rc = main(["--dataset", str(path)])
        assert rc == 0

    def test_main_exit_1_broken(self, tmp_path):
        path = tmp_path / "broken.json"
        df = _make_valid_df(5).drop(columns=["consumo_kwh"])
        df.to_json(path, orient="records")
        rc = main(["--dataset", str(path)])
        assert rc == 1

    def test_main_exit_2_missing(self, tmp_path):
        rc = main(["--dataset", str(tmp_path / "nope.json")])
        assert rc == 2

    def test_main_json_output(self, tmp_path, capsys):
        path = tmp_path / "ok.json"
        _make_valid_df(5).to_json(path, orient="records")
        rc = main(["--dataset", str(path), "--json"])
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["passed"] is True
        assert rc == 0

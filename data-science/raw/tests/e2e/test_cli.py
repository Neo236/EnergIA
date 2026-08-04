import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = str(Path(__file__).resolve().parents[2])


def _run_cli(*args, cwd=None, env=None):
    full_env = os.environ.copy()
    full_env["PYTHONPATH"] = REPO_ROOT
    if env:
        full_env.update(env)
    return subprocess.run(
        [sys.executable, "-m", *args],
        cwd=cwd or REPO_ROOT,
        env=full_env,
        capture_output=True,
        text=True,
        timeout=120,
    )


class TestCliTrain:
    def test_train_crea_artefactos_en_dir_custom(self, tmp_path, monkeypatch):
        monkeypatch.setenv("OUTPUT_JSON_PATH", str(tmp_path / "data" / "db.json"))
        monkeypatch.setenv("OUTPUT_MODEL_PATH", str(tmp_path / "data" / "modelo.joblib"))
        monkeypatch.setenv("OUTPUT_METRICAS_PATH", str(tmp_path / "data" / "metricas.joblib"))
        monkeypatch.setenv("NUM_CLIENTES", "100")

        result = _run_cli("interfaces.cli.train")
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert (tmp_path / "data" / "db.json").exists()
        assert (tmp_path / "data" / "modelo.joblib").exists()
        assert (tmp_path / "data" / "metricas.joblib").exists()


class TestCliValidate:
    def test_validate_sobre_artefactos_invalidos(self, tmp_path, monkeypatch):
        monkeypatch.setenv("OUTPUT_JSON_PATH", str(tmp_path / "no.json"))
        monkeypatch.setenv("OUTPUT_MODEL_PATH", str(tmp_path / "no.joblib"))
        monkeypatch.setenv("OUTPUT_METRICAS_PATH", str(tmp_path / "no_met.joblib"))

        result = _run_cli("interfaces.cli.validate")
        assert result.returncode == 1
        assert "FAIL" in result.stdout or "NO existe" in result.stdout

    def test_validate_sobre_artefactos_validos(self, tmp_path, monkeypatch):
        monkeypatch.setenv("NUM_CLIENTES", "100")
        monkeypatch.setenv("OUTPUT_JSON_PATH", str(tmp_path / "db.json"))
        monkeypatch.setenv("OUTPUT_MODEL_PATH", str(tmp_path / "modelo.joblib"))
        monkeypatch.setenv("OUTPUT_METRICAS_PATH", str(tmp_path / "metricas.joblib"))

        train_result = _run_cli("interfaces.cli.train")
        assert train_result.returncode == 0

        validate_result = _run_cli("interfaces.cli.validate")
        assert validate_result.returncode == 0
        assert "PASS" in validate_result.stdout
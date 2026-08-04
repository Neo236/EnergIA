import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = str(Path(__file__).resolve().parents[2])


def _run_cli(*args, cwd=None, env=None, monkeypatch=None):
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


def _cli_env_from_monkeypatch(monkeypatch) -> dict:
    """Captura env vars modificadas por monkeypatch para pasarlas al subprocess."""
    keys = [
        "OUTPUT_JSON_PATH", "OUTPUT_MODEL_PATH", "OUTPUT_METRICAS_PATH",
        "NUM_CLIENTES", "RANDOM_SEED", "STORAGE_BACKEND", "STORAGE_LOCAL_ROOT",
        "OCI_NAMESPACE", "OCI_BUCKET", "OCI_REGION",
    ]
    return {k: os.environ[k] for k in keys if k in os.environ}


class TestCliTrain:
    def test_train_crea_artefactos_en_dir_custom(self, tmp_path, monkeypatch):
        monkeypatch.setenv("OUTPUT_JSON_PATH", str(tmp_path / "data" / "db.json"))
        monkeypatch.setenv("OUTPUT_MODEL_PATH", str(tmp_path / "data" / "modelo.joblib"))
        monkeypatch.setenv("OUTPUT_METRICAS_PATH", str(tmp_path / "data" / "metricas.joblib"))
        monkeypatch.setenv("NUM_CLIENTES", "100")
        monkeypatch.setenv("STORAGE_BACKEND", "local")
        monkeypatch.setenv("STORAGE_LOCAL_ROOT", str(tmp_path))

        result = _run_cli("interfaces.cli.train", env=_cli_env_from_monkeypatch(monkeypatch))
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert (tmp_path / "data" / "db.json").exists()
        assert (tmp_path / "data" / "modelo.joblib").exists()
        assert (tmp_path / "data" / "metricas.joblib").exists()


class TestCliValidate:
    def test_validate_sobre_artefactos_invalidos(self, tmp_path, monkeypatch):
        monkeypatch.setenv("OUTPUT_JSON_PATH", str(tmp_path / "no.json"))
        monkeypatch.setenv("OUTPUT_MODEL_PATH", str(tmp_path / "no.joblib"))
        monkeypatch.setenv("OUTPUT_METRICAS_PATH", str(tmp_path / "no_met.joblib"))
        # STORAGE_LOCAL_ROOT apunta a tmp_path para que uploads/downloads no
        # contaminen data-science/raw/data/ y no vean artefactos stale de otros tests.
        monkeypatch.setenv("STORAGE_BACKEND", "local")
        monkeypatch.setenv("STORAGE_LOCAL_ROOT", str(tmp_path))

        result = _run_cli(
            "interfaces.cli.validate",
            env=_cli_env_from_monkeypatch(monkeypatch),
        )
        assert result.returncode == 1, f"stdout: {result.stdout}\nstderr: {result.stderr}"
        assert "FAIL" in result.stdout or "NO existe" in result.stdout

    def test_validate_sobre_artefactos_validos(self, tmp_path, monkeypatch):
        monkeypatch.setenv("NUM_CLIENTES", "100")
        monkeypatch.setenv("OUTPUT_JSON_PATH", str(tmp_path / "db.json"))
        monkeypatch.setenv("OUTPUT_MODEL_PATH", str(tmp_path / "modelo.joblib"))
        monkeypatch.setenv("OUTPUT_METRICAS_PATH", str(tmp_path / "metricas.joblib"))
        monkeypatch.setenv("STORAGE_BACKEND", "local")
        monkeypatch.setenv("STORAGE_LOCAL_ROOT", str(tmp_path))

        env = _cli_env_from_monkeypatch(monkeypatch)

        train_result = _run_cli("interfaces.cli.train", env=env)
        assert train_result.returncode == 0, f"stderr: {train_result.stderr}"

        validate_result = _run_cli("interfaces.cli.validate", env=env)
        assert validate_result.returncode == 0, f"stdout: {validate_result.stdout}"
        assert "PASS" in validate_result.stdout
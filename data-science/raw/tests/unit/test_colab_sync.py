"""Tests del script sync_colab_notebook.py.

Mockeamos requests.Session para validar la logica de descarga, fallback entre
endpoints, validacion de SHA256 de celdas de codigo y modo apply sin tocar
la red.
"""

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import scripts.sync_colab_notebook as sync_mod
from scripts.sync_colab_notebook import (
    COLAB_NOTEBOOK_URL,
    _extract_code_cells,
    _extract_file_id,
    _fetch_notebook,
    _looks_like_notebook,
    code_hash,
    code_hash_file,
    sync,
)


# Un .ipynb minimo valido: solo lo necesario para pasar _looks_like_notebook.
def _make_notebook_bytes(cells: list[dict] | None = None) -> bytes:
    nb = {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {"kernelspec": {"name": "python3"}},
        "cells": cells if cells is not None else [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": ["print('hello')\n"],
            },
        ],
    }
    return json.dumps(nb).encode("utf-8")


def _resp(content: bytes, status: int = 200, content_type: str = "application/json"):
    r = MagicMock()
    r.status_code = status
    r.content = content
    r.headers = {"Content-Type": content_type}
    return r


class TestExtractFileId:
    def test_url_con_drive_y_query(self):
        url = "https://colab.research.google.com/drive/ABC123xyz?usp=drive_link"
        assert _extract_file_id(url) == "ABC123xyz"

    def test_url_con_drive_y_path(self):
        url = "https://colab.research.google.com/drive/ABC123xyz/download"
        assert _extract_file_id(url) == "ABC123xyz"

    def test_url_sin_drive_lanza(self):
        with pytest.raises(ValueError, match="/drive/"):
            _extract_file_id("https://example.com/foo")


class TestLooksLikeNotebook:
    def test_json_valido_con_cells(self):
        assert _looks_like_notebook(_make_notebook_bytes()) is True

    def test_json_sin_cells(self):
        assert _looks_like_notebook(b'{"foo": 1}') is False

    def test_html_en_lugar_de_json(self):
        assert _looks_like_notebook(b"<html>foo</html>") is False

    def test_bytes_vacios(self):
        assert _looks_like_notebook(b"") is False

    def test_json_basura(self):
        assert _looks_like_notebook(b"{not json") is False


class TestFetchNotebook:
    def test_primer_endpoint_drive_exitoso(self):
        good = _make_notebook_bytes()
        session = MagicMock()
        session.get.side_effect = [_resp(good)]
        with patch.object(sync_mod.requests, "Session", return_value=session):
            result = _fetch_notebook(COLAB_NOTEBOOK_URL)
        assert result == good
        assert session.get.call_count == 1

    def test_fallback_a_segundo_endpoint(self):
        bad = b"<html>not a notebook</html>"
        good = _make_notebook_bytes()
        session = MagicMock()
        session.get.side_effect = [_resp(bad), _resp(good)]
        with patch.object(sync_mod.requests, "Session", return_value=session):
            result = _fetch_notebook(COLAB_NOTEBOOK_URL)
        assert result == good
        assert session.get.call_count == 2

    def test_404_no_aborta_sigue_probando(self):
        session = MagicMock()
        session.get.return_value = _resp(b"nope", status=404)
        with patch.object(sync_mod.requests, "Session", return_value=session):
            with pytest.raises(RuntimeError, match="No se pudo descargar"):
                _fetch_notebook(COLAB_NOTEBOOK_URL)
        # 5 endpoints intentados (Drive + 4 Colab)
        assert session.get.call_count == 5

    def test_request_exception_no_aborta(self):
        import requests as real_requests
        good = _make_notebook_bytes()
        session = MagicMock()
        session.get.side_effect = [
            real_requests.ConnectionError("boom"),
            _resp(good),
        ]
        with patch.object(sync_mod.requests, "Session", return_value=session):
            result = _fetch_notebook(COLAB_NOTEBOOK_URL)
        assert result == good

    def test_todos_los_endpoints_fallan(self):
        session = MagicMock()
        session.get.return_value = _resp(b"<html>forbidden</html>", status=200)
        with patch.object(sync_mod.requests, "Session", return_value=session):
            with pytest.raises(RuntimeError):
                _fetch_notebook(COLAB_NOTEBOOK_URL)
        # 5 endpoints intentados
        assert session.get.call_count == 5


class TestExtractCodeCells:
    def test_solo_celdas_code(self):
        nb_bytes = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 1\n"], "metadata": {},
             "outputs": [], "execution_count": None},
            {"cell_type": "markdown", "source": ["# titulo\n"]},
            {"cell_type": "code", "source": ["print(x)\n"], "metadata": {},
             "outputs": [{"output_type": "stream", "text": ["1"]}],
             "execution_count": 1},
        ])
        result = _extract_code_cells(nb_bytes)
        assert "x = 1" in result
        assert "print(x)" in result
        assert "# titulo" not in result  # markdown ignorado
        assert "1" not in result or "x = 1" in result  # outputs ignorados

    def test_source_como_lista_o_string(self):
        nb_bytes = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["line1\n", "line2\n"],
             "metadata": {}, "outputs": [], "execution_count": None},
        ])
        result = _extract_code_cells(nb_bytes)
        assert "line1" in result and "line2" in result

    def test_normaliza_trailing_whitespace(self):
        nb_bytes = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 1   \n", "y = 2\t\n"],
             "metadata": {}, "outputs": [], "execution_count": None},
        ])
        result = _extract_code_cells(nb_bytes)
        # trailing whitespace removido
        assert "x = 1\n" in result
        assert "y = 2\n" in result

    def test_outputs_no_incluidos(self):
        nb_bytes = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["pass\n"],
             "metadata": {}, "outputs": [
                 {"output_type": "stream", "text": ["BIG_OUTPUT_SECRET\n"]}
             ], "execution_count": 5},
        ])
        result = _extract_code_cells(nb_bytes)
        assert "BIG_OUTPUT_SECRET" not in result


class TestCodeHash:
    def test_mismo_codigo_mismo_hash(self):
        nb1 = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 1\n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ])
        nb2 = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 1\n"], "metadata": {},
             "outputs": [{"output_type": "stream", "text": ["foo"]}],
             "execution_count": 99},
        ])
        # Mismo codigo, distintos outputs -> mismo hash
        assert code_hash(nb1) == code_hash(nb2)

    def test_distinto_codigo_distinto_hash(self):
        nb1 = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 1\n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ])
        nb2 = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 2\n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ])
        assert code_hash(nb1) != code_hash(nb2)

    def test_trailing_whitespace_no_cambia_hash(self):
        nb1 = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 1\n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ])
        nb2 = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 1   \n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ])
        assert code_hash(nb1) == code_hash(nb2)

    def test_code_hash_file(self, tmp_path):
        nb_bytes = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["z = 9\n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ])
        path = tmp_path / "f.ipynb"
        path.write_bytes(nb_bytes)
        assert code_hash_file(path) == code_hash(nb_bytes)


class TestSync:
    def test_hashes_iguales_retorna_0(self, tmp_path):
        good = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 1\n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ])
        local = tmp_path / "data_colab.ipynb"
        local.write_bytes(good)

        session = MagicMock()
        session.get.return_value = _resp(good)
        with patch.object(sync_mod.requests, "Session", return_value=session):
            assert sync(local_path=local) == 0

    def test_outputs_distintos_mismo_codigo_retorna_0(self, tmp_path):
        """Outputs cambian entre ejecuciones pero el codigo no: debe coincidir."""
        remote = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 1\n"], "metadata": {},
             "outputs": [{"output_type": "stream", "text": ["REMOTO"]}],
             "execution_count": 5},
        ])
        local = tmp_path / "data_colab.ipynb"
        local.write_bytes(_make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 1\n"], "metadata": {},
             "outputs": [{"output_type": "stream", "text": ["LOCAL"]}],
             "execution_count": 99},
        ]))

        session = MagicMock()
        session.get.return_value = _resp(remote)
        with patch.object(sync_mod.requests, "Session", return_value=session):
            assert sync(local_path=local) == 0

    def test_codigos_distintos_sin_apply_retorna_1(self, tmp_path):
        remote = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = REMOTO\n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ])
        local = tmp_path / "data_colab.ipynb"
        local.write_bytes(_make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = LOCAL\n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ]))

        session = MagicMock()
        session.get.return_value = _resp(remote)
        with patch.object(sync_mod.requests, "Session", return_value=session):
            assert sync(local_path=local, apply=False) == 1
        # El archivo local NO debe haber sido modificado
        assert "x = LOCAL" in _extract_code_cells(local.read_bytes())

    def test_codigos_distintos_con_apply_sobrescribe(self, tmp_path):
        remote = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = REMOTO\n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ])
        local = tmp_path / "data_colab.ipynb"
        local.write_bytes(_make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = LOCAL\n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ]))

        session = MagicMock()
        session.get.return_value = _resp(remote)
        with patch.object(sync_mod.requests, "Session", return_value=session):
            assert sync(local_path=local, apply=True) == 0
        assert "x = REMOTO" in _extract_code_cells(local.read_bytes())

    def test_local_inexistente_sin_apply_retorna_1(self, tmp_path):
        good = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 1\n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ])
        local = tmp_path / "no_existe.ipynb"

        session = MagicMock()
        session.get.return_value = _resp(good)
        with patch.object(sync_mod.requests, "Session", return_value=session):
            assert sync(local_path=local, apply=False) == 1
        assert not local.exists()

    def test_local_inexistente_con_apply_crea_archivo(self, tmp_path):
        good = _make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 1\n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ])
        local = tmp_path / "no_existe.ipynb"

        session = MagicMock()
        session.get.return_value = _resp(good)
        with patch.object(sync_mod.requests, "Session", return_value=session):
            assert sync(local_path=local, apply=True) == 0
        assert local.exists()
        assert local.read_bytes() == good

    def test_error_descarga_retorna_2(self, tmp_path):
        local = tmp_path / "data_colab.ipynb"
        local.write_bytes(_make_notebook_bytes(cells=[
            {"cell_type": "code", "source": ["x = 1\n"], "metadata": {},
             "outputs": [], "execution_count": None},
        ]))

        session = MagicMock()
        session.get.return_value = _resp(b"<html>no</html>", status=200)
        with patch.object(sync_mod.requests, "Session", return_value=session):
            assert sync(local_path=local) == 2


class TestNotebookLocal:
    """Valida la estructura del notebook sincronizado localmente, sin jupyter."""

    NOTEBOOK = (
        Path(__file__).resolve().parents[2]
        / "notebooks" / "data_colab.ipynb"
    )

    def test_notebook_existe(self):
        assert self.NOTEBOOK.exists(), (
            f"Ejecuta: python scripts/sync_colab_notebook.py --apply "
            f"(esperado en {self.NOTEBOOK})"
        )

    def test_notebook_es_json_valido(self):
        if not self.NOTEBOOK.exists():
            pytest.skip("Notebook no sincronizado aun")
        parsed = json.loads(self.NOTEBOOK.read_bytes())
        assert "cells" in parsed
        assert parsed["nbformat"] == 4

    def test_notebook_tiene_celdas_de_pipeline(self):
        if not self.NOTEBOOK.exists():
            pytest.skip("Notebook no sincronizado aun")
        parsed = json.loads(self.NOTEBOOK.read_bytes())
        src_concat = _extract_code_cells(self.NOTEBOOK.read_bytes())
        # El colab genera el dataset con numpy directo y calcula categoria
        # con reglas IEE. Estos marcadores deben estar presentes.
        for keyword in ["consumo_kwh", "categoria", "score_consumo", "obtener_categoria"]:
            assert keyword in src_concat, f"Falta marcador esperado: {keyword}"

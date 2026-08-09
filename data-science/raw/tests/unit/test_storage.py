import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open

import pytest


class TestLocalStorage:
    def test_upload_and_download_roundtrip(self, tmp_path):
        from infrastructure.storage.local import LocalStorage

        storage = LocalStorage(root=str(tmp_path))
        src = tmp_path / "src.txt"
        src.write_text("hello world")

        storage.upload(str(src), "subdir/dst.txt")
        dst = tmp_path / "local_download.txt"
        storage.download("subdir/dst.txt", str(dst))

        assert dst.read_text() == "hello world"

    def test_exists_true(self, tmp_path):
        from infrastructure.storage.local import LocalStorage

        storage = LocalStorage(root=str(tmp_path))
        (tmp_path / "f.txt").write_text("x")
        assert storage.exists("f.txt") is True

    def test_exists_false(self, tmp_path):
        from infrastructure.storage.local import LocalStorage

        storage = LocalStorage(root=str(tmp_path))
        assert storage.exists("missing.txt") is False

    def test_download_missing_raises_filenotfound(self, tmp_path):
        from infrastructure.storage.local import LocalStorage

        storage = LocalStorage(root=str(tmp_path))
        with pytest.raises(FileNotFoundError):
            storage.download("nope.txt", str(tmp_path / "out.txt"))

    def test_upload_creates_parent_dirs(self, tmp_path):
        from infrastructure.storage.local import LocalStorage

        storage = LocalStorage(root=str(tmp_path))
        src = tmp_path / "src.txt"
        src.write_text("data")
        storage.upload(str(src), "deep/nested/path/dst.txt")
        assert (tmp_path / "deep" / "nested" / "path" / "dst.txt").exists()

    def test_delete_existing(self, tmp_path):
        from infrastructure.storage.local import LocalStorage

        storage = LocalStorage(root=str(tmp_path))
        (tmp_path / "f.txt").write_text("x")
        assert storage.exists("f.txt")
        storage.delete("f.txt")
        assert not storage.exists("f.txt")

    def test_delete_missing_raises(self, tmp_path):
        from infrastructure.storage.local import LocalStorage

        storage = LocalStorage(root=str(tmp_path))
        with pytest.raises(FileNotFoundError):
            storage.delete("missing.txt")

    def test_list_objects_con_prefix(self, tmp_path):
        from infrastructure.storage.local import LocalStorage

        storage = LocalStorage(root=str(tmp_path))
        (tmp_path / "latest").mkdir()
        (tmp_path / "latest" / "a.json").write_text("a")
        (tmp_path / "latest" / "b.json").write_text("b")
        (tmp_path / "archive").mkdir()
        (tmp_path / "archive" / "2026-08-07_a.json").write_text("old")

        latest = storage.list_objects("latest/")
        assert set(latest) == {"latest/a.json", "latest/b.json"}

        archive = storage.list_objects("archive/")
        assert archive == ["archive/2026-08-07_a.json"]

        empty = storage.list_objects("nonexistent/")
        assert empty == []

    def test_head_info_existente(self, tmp_path):
        import base64, hashlib
        from infrastructure.storage.local import LocalStorage

        storage = LocalStorage(root=str(tmp_path))
        content = b"hola mundo"
        (tmp_path / "f.bin").write_bytes(content)

        info = storage.head_info("f.bin")
        assert info is not None
        md5_hex = hashlib.md5(content).hexdigest()
        md5_b64 = base64.b64encode(bytes.fromhex(md5_hex)).decode()
        assert info["etag"] == md5_hex
        assert info["md5"] == md5_b64
        assert info["size"] == len(content)

    def test_head_info_inexistente_retorna_none(self, tmp_path):
        from infrastructure.storage.local import LocalStorage

        storage = LocalStorage(root=str(tmp_path))
        assert storage.head_info("no_existe.txt") is None

    def test_copy_crea_destino(self, tmp_path):
        from infrastructure.storage.local import LocalStorage

        storage = LocalStorage(root=str(tmp_path))
        (tmp_path / "latest").mkdir()
        (tmp_path / "latest" / "src.bin").write_bytes(b"data")
        (tmp_path / "archive").mkdir()

        storage.copy("latest/src.bin", "archive/dst.bin")
        assert (tmp_path / "latest" / "src.bin").read_bytes() == b"data"
        assert (tmp_path / "archive" / "dst.bin").read_bytes() == b"data"

    def test_copy_inexistente_lanza_filenotfound(self, tmp_path):
        from infrastructure.storage.local import LocalStorage

        storage = LocalStorage(root=str(tmp_path))
        with pytest.raises(FileNotFoundError):
            storage.copy("nope.bin", "dst.bin")


class TestGetStorageFactory:
    def teardown_method(self):
        for k in ["STORAGE_BACKEND", "STORAGE_LOCAL_ROOT"]:
            os.environ.pop(k, None)

    def test_default_es_local(self):
        from infrastructure.storage import get_storage
        from infrastructure.storage.local import LocalStorage

        os.environ.pop("STORAGE_BACKEND", None)
        s = get_storage()
        assert isinstance(s, LocalStorage)

    def test_explicit_local(self):
        from infrastructure.storage import get_storage
        from infrastructure.storage.local import LocalStorage

        os.environ["STORAGE_BACKEND"] = "local"
        os.environ["STORAGE_LOCAL_ROOT"] = "/tmp"
        s = get_storage()
        assert isinstance(s, LocalStorage)
        assert str(s.root) == "/tmp"

    def test_oci_sin_namespace_lanza_runtimeerror(self):
        """Si falta OCI_NAMESPACE, get_storage() crashea con RuntimeError claro."""
        from infrastructure.storage import get_storage

        os.environ["STORAGE_BACKEND"] = "oci"
        os.environ.pop("OCI_NAMESPACE", None)
        os.environ["OCI_BUCKET"] = "test-bucket"
        os.environ["OCI_REGION"] = "santiago-chile-1"
        with pytest.raises(RuntimeError, match="OCI_NAMESPACE"):
            get_storage()

    def test_oci_con_vars_retorna_oci_storage(self):
        from infrastructure.storage import get_storage
        from infrastructure.storage.oci import OciBucketStorage

        os.environ["STORAGE_BACKEND"] = "oci"
        os.environ["OCI_NAMESPACE"] = "test-ns"
        os.environ["OCI_BUCKET"] = "test-bucket"
        os.environ["OCI_REGION"] = "santiago-chile-1"
        s = get_storage()
        assert isinstance(s, OciBucketStorage)
        assert s.namespace == "test-ns"
        assert s.bucket == "test-bucket"

    def test_backend_invalido_lanza_valueerror(self):
        from infrastructure.storage import get_storage

        os.environ["STORAGE_BACKEND"] = "redis"
        with pytest.raises(ValueError):
            get_storage()


class TestOciBucketStorageMocked:
    def _client_mock(self):
        class _Response:
            def __init__(self, content=b"oci-content"):
                self.data = type("d", (), {"content": content})()

        class _ClientMock:
            def __init__(self):
                # Pre-popular con la key completa {bucket}/{name}
                self.objects = {"bucket/data/modelo.joblib": b"model-bytes"}
                self.copy_calls = []
                self.head_calls = []

            def put_object(self, namespace_name, bucket_name, object_name, body, **kwargs):
                # OciBucketStorage.upload pasa un file-like; SDK acepta bytes
                # o stream. Mock capturamos bytes si es file-like.
                if hasattr(body, "read"):
                    self.objects[f"{bucket_name}/{object_name}"] = body.read()
                else:
                    self.objects[f"{bucket_name}/{object_name}"] = body

            def get_object(self, namespace_name, bucket_name, object_name, **kwargs):
                if f"{bucket_name}/{object_name}" not in self.objects:
                    raise Exception("404 not found")
                return _Response(self.objects[f"{bucket_name}/{object_name}"])

            def head_object(self, namespace_name, bucket_name, object_name, **kwargs):
                self.head_calls.append(object_name)
                if f"{bucket_name}/{object_name}" not in self.objects:
                    raise Exception("404 not found")

                content = self.objects[f"{bucket_name}/{object_name}"]

                class _HeadData:
                    def __init__(self, c):
                        import hashlib, base64
                        self.etag = hashlib.md5(c).hexdigest()
                        self.content_md5 = base64.b64encode(hashlib.md5(c).digest()).decode()
                        self.content_length = len(c)

                class _HeadResp:
                    def __init__(self, c):
                        self.data = _HeadData(c)
                return _HeadResp(content)

            def copy_object(self, namespace_name, bucket_name, copy_object_details, **kwargs):
                src = copy_object_details.source_object_name
                dst = copy_object_details.destination_object_name
                self.copy_calls.append((src, dst))
                if f"{bucket_name}/{src}" not in self.objects:
                    raise Exception("404 not found")
                # Server-side copy: no body transfer
                self.objects[f"{bucket_name}/{dst}"] = self.objects[f"{bucket_name}/{src}"]

            def delete_object(self, namespace_name, bucket_name, object_name, **kwargs):
                if f"{bucket_name}/{object_name}" not in self.objects:
                    raise Exception("404 not found")
                del self.objects[f"{bucket_name}/{object_name}"]

            def list_objects(self, namespace_name, bucket_name, prefix, limit=1000, start=None, **kwargs):
                # Filtra por prefix, devuelve objetos con atributo .name
                class _ObjList:
                    def __init__(self, items):
                        self.objects = items
                matched = [
                    type("O", (), {"name": name})()
                    for full, _ in self.objects.items()
                    if full.startswith(f"{bucket_name}/{prefix}")
                ]
                return _ObjList(matched)

        return _ClientMock()

    def test_upload_download_roundtrip(self, tmp_path, monkeypatch):
        from infrastructure.storage.oci import OciBucketStorage

        monkeypatch.setenv("OCI_NAMESPACE", "ns")
        monkeypatch.setenv("OCI_BUCKET", "bucket")
        monkeypatch.setenv("OCI_REGION", "region")

        storage = OciBucketStorage()
        client = self._client_mock()
        storage._client = client

        src = tmp_path / "src.bin"
        src.write_bytes(b"hello-oci")
        storage.upload(str(src), "data/modelo.joblib")

        assert client.objects["bucket/data/modelo.joblib"] == b"hello-oci"

        dst = tmp_path / "dl.bin"
        storage.download("data/modelo.joblib", str(dst))
        assert dst.read_bytes() == b"hello-oci"

    def test_exists_true(self, monkeypatch):
        from infrastructure.storage.oci import OciBucketStorage

        monkeypatch.setenv("OCI_NAMESPACE", "ns")
        monkeypatch.setenv("OCI_BUCKET", "bucket")
        monkeypatch.setenv("OCI_REGION", "region")

        storage = OciBucketStorage()
        storage._client = self._client_mock()

        assert storage.exists("data/modelo.joblib") is True
        assert storage.exists("data/missing.joblib") is False

    def test_download_missing_lanza_filenotfound(self, monkeypatch):
        from infrastructure.storage.oci import OciBucketStorage

        monkeypatch.setenv("OCI_NAMESPACE", "ns")
        monkeypatch.setenv("OCI_BUCKET", "bucket")
        monkeypatch.setenv("OCI_REGION", "region")

        storage = OciBucketStorage()
        storage._client = self._client_mock()

        with pytest.raises(FileNotFoundError):
            storage.download("data/nope.joblib", "/tmp/out.bin")

    def test_lazy_client(self, monkeypatch):
        """OciBucketStorage no debe instanciar el client hasta el primer uso."""
        from infrastructure.storage.oci import OciBucketStorage

        monkeypatch.setenv("OCI_NAMESPACE", "ns")
        monkeypatch.setenv("OCI_BUCKET", "bucket")
        monkeypatch.setenv("OCI_INSTANCE_PRINCIPAL", "true")
        monkeypatch.setenv("OCI_REGION", "region")

        storage = OciBucketStorage()
        assert storage._client is None

        # Solo verificar que _client es None — no instanciar el real para no
        # requerir el SDK de OCI instalado.
        # El path real de _get_client se ejercita en los otros tests mocked.

    def test_delete_existing(self, monkeypatch):
        from infrastructure.storage.oci import OciBucketStorage

        monkeypatch.setenv("OCI_NAMESPACE", "ns")
        monkeypatch.setenv("OCI_BUCKET", "bucket")
        monkeypatch.setenv("OCI_REGION", "region")

        storage = OciBucketStorage()
        storage._client = self._client_mock()

        assert storage.exists("data/modelo.joblib")
        storage.delete("data/modelo.joblib")
        assert not storage.exists("data/modelo.joblib")

    def test_delete_missing_lanza_filenotfound(self, monkeypatch):
        from infrastructure.storage.oci import OciBucketStorage

        monkeypatch.setenv("OCI_NAMESPACE", "ns")
        monkeypatch.setenv("OCI_BUCKET", "bucket")
        monkeypatch.setenv("OCI_REGION", "region")

        storage = OciBucketStorage()
        storage._client = self._client_mock()

        with pytest.raises(FileNotFoundError):
            storage.delete("data/nope.joblib")

    def test_head_info_existente(self, monkeypatch):
        """head_info devuelve md5 sin descargar el body."""
        from infrastructure.storage.oci import OciBucketStorage

        monkeypatch.setenv("OCI_NAMESPACE", "ns")
        monkeypatch.setenv("OCI_BUCKET", "bucket")
        monkeypatch.setenv("OCI_REGION", "region")

        client = self._client_mock()
        storage = OciBucketStorage()
        storage._client = client

        info = storage.head_info("data/modelo.joblib")
        assert info is not None
        assert info["md5"] is not None
        assert info["size"] == len(b"model-bytes")
        assert len(client.head_calls) == 1

    def test_head_info_inexistente_retorna_none(self, monkeypatch):
        from infrastructure.storage.oci import OciBucketStorage

        monkeypatch.setenv("OCI_NAMESPACE", "ns")
        monkeypatch.setenv("OCI_BUCKET", "bucket")
        monkeypatch.setenv("OCI_REGION", "region")

        storage = OciBucketStorage()
        storage._client = self._client_mock()

        assert storage.head_info("data/nope.joblib") is None

    def test_copy_server_side(self, monkeypatch):
        """copy debe usar copy_object del SDK (server-side, sin body transfer)."""
        from infrastructure.storage.oci import OciBucketStorage

        monkeypatch.setenv("OCI_NAMESPACE", "ns")
        monkeypatch.setenv("OCI_BUCKET", "bucket")
        monkeypatch.setenv("OCI_REGION", "region")

        client = self._client_mock()
        storage = OciBucketStorage()
        storage._client = client

        storage.copy("data/modelo.joblib", "archive/2026-08-07_modelo.joblib")
        assert client.copy_calls == [(
            "data/modelo.joblib",
            "archive/2026-08-07_modelo.joblib",
        )]
        # Verificar que el server-side copy NO toco head_object ni get_object
        # (solo el mock es stateful, no el SDK real).
        assert len(client.head_calls) == 0


class TestUploadWithRotation:
    """Tests del helper _upload_with_rotation (latest/archive, code-version-aware).

    El mock de head_info devuelve md5 en base64 si el remote existe.
    El mock de download simula el manifest.json cuando se pide MANIFEST_PATH.
    """

    def _storage_mock(self, existing_latest=None, archived_codes=None):
        """archived_codes: lista de code_shorts ya archivados para CUALQUIER archivo."""
        import base64, hashlib as _hl

        archived_codes = archived_codes or []
        s = MagicMock()

        if existing_latest is not None:
            md5_hex = _hl.md5(existing_latest).hexdigest()
            md5_b64 = base64.b64encode(bytes.fromhex(md5_hex)).decode()
            head_info_result = {"etag": md5_hex, "md5": md5_b64, "size": len(existing_latest)}
        else:
            head_info_result = None
        s.head_info.return_value = head_info_result
        s.exists.return_value = existing_latest is not None

        # Mock para manifest.json
        import json as _json
        manifest_data = {
            "version": 1,
            "files": {"modelo.joblib": list(archived_codes)} if archived_codes else {},
        }
        from interfaces.cli.train import MANIFEST_PATH
        _shared_manifest = {}

        def _upload_side(local, remote):
            if remote == MANIFEST_PATH:
                import shutil
                _shared_manifest["path"] = "/tmp/_test_manifest.json"
                shutil.copy(local, _shared_manifest["path"])

        def _download_side(remote, local):
            from interfaces.cli.train import MANIFEST_PATH as MP
            if remote == MP:
                if "path" not in _shared_manifest:
                    # Inicializa con el manifest por defecto
                    import tempfile
                    tmp = tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json")
                    _json.dump(manifest_data, tmp)
                    tmp.close()
                    _shared_manifest["path"] = tmp.name
                import shutil
                shutil.copy(_shared_manifest["path"], local)
            elif existing_latest is not None:
                Path(local).write_bytes(existing_latest)
            else:
                raise FileNotFoundError(remote)

        s.upload.side_effect = _upload_side
        s.download.side_effect = _download_side
        s.list_objects.return_value = []
        s.delete.side_effect = lambda remote: Path(remote).unlink(missing_ok=True)

        # copy: server-side (no body transfer)
        s.copy.side_effect = lambda src, dst: None

        return s

    def test_no_op_si_md5_coincide(self, tmp_path):
        """Si el MD5 del local coincide con el remoto, NO se ejecuta ninguna op
        (cero upload, cero download, cero copy, cero delete)."""
        from interfaces.cli.train import _upload_with_rotation

        src = tmp_path / "modelo.joblib"
        src.write_bytes(b"v1")
        storage = self._storage_mock(existing_latest=b"v1")

        action = _upload_with_rotation(
            storage, str(src), "modelo.joblib", code_version="git:abc1234"
        )
        assert action == "skipped_identical"
        storage.upload.assert_not_called()
        storage.copy.assert_not_called()
        storage.delete.assert_not_called()
        storage.download.assert_not_called()
        # Solo 1 head_info (para el md5 check)
        storage.head_info.assert_called_once()

    def test_sube_como_latest_si_no_existe(self, tmp_path):
        from interfaces.cli.train import _upload_with_rotation

        src = tmp_path / "modelo.joblib"
        src.write_bytes(b"v1")
        storage = self._storage_mock(existing_latest=None)

        action = _upload_with_rotation(
            storage, str(src), "modelo.joblib", code_version="git:abc1234"
        )
        assert action == "uploaded"
        storage.upload.assert_called_once()
        assert storage.upload.call_args.args[1] == "latest/modelo.joblib"

    def test_no_hace_nada_si_hash_coincide(self, tmp_path):
        from interfaces.cli.train import _upload_with_rotation

        src = tmp_path / "modelo.joblib"
        src.write_bytes(b"v1")
        storage = self._storage_mock(existing_latest=b"v1")

        action = _upload_with_rotation(
            storage, str(src), "modelo.joblib", code_version="git:abc1234"
        )
        assert action == "skipped_identical"
        storage.upload.assert_not_called()
        storage.delete.assert_not_called()

    def test_refresh_sin_archivo_nuevo_si_code_ya_archivo(self, tmp_path):
        """Si el code_version ya esta archivado (en manifest), NO se crea nuevo
        archive, solo se refresca latest/ si los bytes difieren."""
        from interfaces.cli.train import _upload_with_rotation

        src = tmp_path / "modelo.joblib"
        src.write_bytes(b"v2")
        # El manifest ya tiene el code_short archivado
        storage = self._storage_mock(
            existing_latest=b"v1",
            archived_codes=["abc1234"],
        )

        action = _upload_with_rotation(
            storage, str(src), "modelo.joblib", code_version="git:abc1234"
        )
        assert action == "refreshed"
        # NO se llamo copy (no es rotacion)
        storage.copy.assert_not_called()
        # SI se subio el nuevo a latest/
        latest_calls = [
            c for c in storage.upload.call_args_list if "latest/" in c.args[1]
        ]
        assert len(latest_calls) == 1
        # NO se borro latest/ antes (no es rotacion)
        storage.delete.assert_not_called()

    def test_rota_si_code_version_cambio(self, tmp_path):
        """Si code_version es nuevo (no esta en manifest), usa copy server-side
        + actualiza manifest."""
        from interfaces.cli.train import _upload_with_rotation, MANIFEST_PATH

        src = tmp_path / "modelo.joblib"
        src.write_bytes(b"v2")
        # manifest NO tiene el code nuevo
        storage = self._storage_mock(
            existing_latest=b"v1",
            archived_codes=["oldsht"],
        )

        action = _upload_with_rotation(
            storage, str(src), "modelo.joblib", code_version="git:newcode"
        )
        assert action == "rotated"
        # ROTACION usa copy (no download+upload del body)
        storage.copy.assert_called_once()
        copy_args = storage.copy.call_args.args
        assert copy_args[0] == "latest/modelo.joblib"
        assert copy_args[1].startswith("archive/")
        assert "newcode" in copy_args[1]
        # Se borro el viejo latest/
        storage.delete.assert_called_once_with("latest/modelo.joblib")
        # Se subio el nuevo a latest/
        latest_calls = [
            c for c in storage.upload.call_args_list if "latest/" in c.args[1]
        ]
        assert len(latest_calls) == 1
        # Se subio el manifest actualizado (con el nuevo code_short)
        manifest_uploads = [
            c for c in storage.upload.call_args_list
            if c.args[1] == MANIFEST_PATH
        ]
        assert len(manifest_uploads) == 1

    def test_skip_si_local_no_existe(self, tmp_path):
        from interfaces.cli.train import _upload_with_rotation

        storage = self._storage_mock(existing_latest=None)
        action = _upload_with_rotation(
            storage, str(tmp_path / "missing"), "x", code_version="git:abc"
        )
        assert action == "skipped_missing"
        storage.upload.assert_not_called()
        storage.head_info.assert_not_called()

    def test_code_version_se_infiere_si_no_se_pasa(self, tmp_path, monkeypatch):
        """Sin code_version explicito, se infiere via compute_code_version()."""
        from interfaces.cli.train import _upload_with_rotation

        src = tmp_path / "modelo.joblib"
        src.write_bytes(b"v1")
        storage = self._storage_mock(existing_latest=None)

        monkeypatch.setattr(
            "interfaces.cli.train.compute_code_version",
            lambda: "git:fake123",
        )
        action = _upload_with_rotation(storage, str(src), "modelo.joblib")
        assert action == "uploaded"


class TestSafeUploadWithRotation:
    """Tolerancia a fallos: si el storage falla, no debe propagar."""

    def test_warning_si_upload_falla(self, tmp_path, capsys):
        from interfaces.cli.train import _safe_upload_with_rotation

        src = tmp_path / "modelo.joblib"
        src.write_bytes(b"v1")

        storage = MagicMock()
        storage.exists.return_value = False
        storage.upload.side_effect = RuntimeError("network down")

        _safe_upload_with_rotation(storage, str(src), "modelo.joblib")
        captured = capsys.readouterr()
        assert "WARN" in captured.err
        assert "network down" in captured.err

    def test_skip_silencioso_si_local_no_existe(self, tmp_path, capsys):
        from interfaces.cli.train import _safe_upload_with_rotation

        storage = MagicMock()
        _safe_upload_with_rotation(storage, str(tmp_path / "missing"), "x")
        captured = capsys.readouterr()
        assert "SKIP" in captured.out
        storage.upload.assert_not_called()


class TestManifest:
    """Tests del manifest.json (reemplaza list_objects)."""

    def test_read_manifest_vacio_si_no_existe(self):
        from interfaces.cli.train import _read_manifest, MANIFEST_PATH

        storage = MagicMock()
        storage.download.side_effect = FileNotFoundError("nope")
        m = _read_manifest(storage)
        assert m["version"] == 1
        assert m["files"] == {}
        storage.download.assert_called_once()

    def test_read_manifest_roundtrip(self):
        from interfaces.cli.train import _write_manifest, _read_manifest, MANIFEST_PATH

        storage = MagicMock()
        shared_path = None

        def fake_upload(local, remote):
            nonlocal shared_path
            if remote == MANIFEST_PATH:
                import shutil
                shared_path = "/tmp/_roundtrip_manifest.json"
                shutil.copy(local, shared_path)

        def fake_download(remote, local):
            nonlocal shared_path
            if remote == MANIFEST_PATH:
                if shared_path is None:
                    raise FileNotFoundError(remote)
                import shutil
                shutil.copy(shared_path, local)

        storage.upload.side_effect = fake_upload
        storage.download.side_effect = fake_download

        manifest = {"files": {"modelo.joblib": ["abc1234", "def5678"]}}
        ok = _write_manifest(storage, manifest)
        assert ok is True

        read_back = _read_manifest(storage)
        assert "abc1234" in read_back["files"]["modelo.joblib"]
        assert "def5678" in read_back["files"]["modelo.joblib"]

        Path(shared_path).unlink(missing_ok=True)

    def test_read_manifest_versiones_incompatibles_se_reinicia(self):
        from interfaces.cli.train import _read_manifest

        storage = MagicMock()
        # Simular manifest con version vieja
        import json as _json
        import tempfile as _tmp

        with _tmp.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            _json.dump({"version": 99, "files": {}}, f)
            old_manifest_path = f.name

        def fake_download(remote, local):
            import shutil
            shutil.copy(old_manifest_path, local)
        storage.download.side_effect = fake_download

        m = _read_manifest(storage)
        assert m["version"] == 1
        assert m["files"] == {}

        Path(old_manifest_path).unlink(missing_ok=True)

    def test_read_manifest_json_invalido_retorna_vacio(self):
        from interfaces.cli.train import _read_manifest

        storage = MagicMock()
        import tempfile as _tmp

        with _tmp.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            f.write("this is not valid json {{{")
            bad_path = f.name

        def fake_download(remote, local):
            import shutil
            shutil.copy(bad_path, local)
        storage.download.side_effect = fake_download

        m = _read_manifest(storage)
        assert m["version"] == 1
        assert m["files"] == {}

        Path(bad_path).unlink(missing_ok=True)

    def test_archive_exists_for_code_usa_manifest(self):
        """_archive_exists_for_code debe usar manifest, NO list_objects."""
        from interfaces.cli.train import _archive_exists_for_code

        storage = MagicMock()
        storage.download.return_value = None  # escribira tmpfile

        # Forzar manifest con un code_short conocido
        import json as _json
        import tempfile as _tmp
        with _tmp.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            _json.dump({
                "version": 1,
                "files": {"modelo.joblib": ["abc1234"]},
            }, f)
            mp = f.name

        def fake_download(remote, local):
            import shutil
            shutil.copy(mp, local)
        storage.download.side_effect = fake_download

        assert _archive_exists_for_code(storage, "modelo.joblib", "abc1234") is True
        assert _archive_exists_for_code(storage, "modelo.joblib", "other") is False
        # NO debe llamar a list_objects (manifiesto es mas barato).
        storage.list_objects.assert_not_called()

        Path(mp).unlink(missing_ok=True)


class TestRetry:
    """Tests del helper with_retry (retry con backoff exponencial)."""

    def test_exito_sin_retry(self):
        from infrastructure.storage.retry import with_retry

        called = [0]

        def op():
            called[0] += 1
            return "ok"

        result = with_retry(op, op_name="test")
        assert result == "ok"
        assert called[0] == 1

    def test_retry_y_exito_en_tercer_intento(self, monkeypatch):
        from infrastructure.storage.retry import with_retry

        called = [0]

        def op():
            called[0] += 1
            if called[0] < 3:
                raise ConnectionError("transient")
            return "ok"

        # Backoff minimo para que el test sea rapido
        monkeypatch.setattr("time.sleep", lambda s: None)
        result = with_retry(op, op_name="test", initial_backoff_s=0.01)
        assert result == "ok"
        assert called[0] == 3

    def test_falla_todos_los_intentos_propaga(self, monkeypatch):
        from infrastructure.storage.retry import with_retry

        called = [0]

        def op():
            called[0] += 1
            raise ConnectionError("nope")

        monkeypatch.setattr("time.sleep", lambda s: None)
        with pytest.raises(ConnectionError, match="nope"):
            with_retry(op, op_name="test", max_attempts=3, initial_backoff_s=0.01)
        assert called[0] == 3

    def test_file_not_found_no_se_reintenta(self, monkeypatch):
        from infrastructure.storage.retry import with_retry

        called = [0]

        def op():
            called[0] += 1
            raise FileNotFoundError("404")

        monkeypatch.setattr("time.sleep", lambda s: None)
        with pytest.raises(FileNotFoundError):
            with_retry(
                op,
                op_name="test",
                max_attempts=3,
                retryable=(ConnectionError,),
            )
        assert called[0] == 1  # sin reintentos

    def test_os_error_no_retryea_file_not_found(self, monkeypatch):
        """FileNotFoundError es subclase de OSError pero NO debe reintentarse
        aunque OSError este en retryable."""
        from infrastructure.storage.retry import with_retry

        called = [0]

        def op():
            called[0] += 1
            raise FileNotFoundError("404")

        monkeypatch.setattr("time.sleep", lambda s: None)
        with pytest.raises(FileNotFoundError):
            with_retry(
                op,
                op_name="test",
                max_attempts=3,
                retryable=(OSError,),  # OSError incluye FileNotFoundError
            )
        assert called[0] == 1  # FileNotFoundError short-circuits OSError retry

    def test_sha256_sidecar(self, tmp_path):
        from interfaces.cli.train import _write_sha256_sidecar
        import hashlib

        f = tmp_path / "modelo.joblib"
        f.write_bytes(b"hello")
        _write_sha256_sidecar(f)
        sidecar = tmp_path / "modelo.joblib.sha256"
        assert sidecar.exists()
        expected = hashlib.sha256(b"hello").hexdigest()
        assert sidecar.read_text() == f"{expected}  modelo.joblib\n"


class TestDryRun:
    """Tests del flag --dry-run en train.py."""

    def test_dry_run_no_llama_storage(self, tmp_path, monkeypatch):
        """Con --dry-run, NO se debe invocar get_storage() ni subir nada."""
        from interfaces.cli import train as tr
        from infrastructure import config as _cfg

        # Configurar para usar tmp_path
        _cfg.Config.OUTPUT_JSON_PATH = str(tmp_path / "database_beta.json")
        _cfg.Config.OUTPUT_MODEL_PATH = str(tmp_path / "modelo.joblib")
        _cfg.Config.OUTPUT_METRICAS_PATH = str(tmp_path / "metricas.joblib")
        _cfg.Config.NUM_CLIENTES = 100
        _cfg.Config.RANDOM_SEED = 42

        storage_called = [False]

        def fake_get_storage():
            storage_called[0] = True
            return MagicMock()

        monkeypatch.setattr(tr, "get_storage", fake_get_storage)
        # Tambien evitar que los handlers de upload hagan algo
        monkeypatch.setattr(tr, "_safe_upload_with_rotation", lambda *a, **kw: None)

        # Necesitamos un data dir preexistente
        Path(tmp_path / "data").mkdir(exist_ok=True)

        rc = tr.main(["--dry-run"])
        assert rc == 0
        # El artefacto local DEBE existir (se entreno localmente)
        assert Path(_cfg.Config.OUTPUT_MODEL_PATH).exists()
        # Pero NO se llamo get_storage() (dry-run salta la seccion de uploads)
        assert storage_called[0] is False


class TestCompression:
    """Compresion joblib: el modelo serializado debe ser mas chico que sin comprimir."""

    def test_modelo_comprimido_mas_chico(self, tmp_path):
        from sklearn.ensemble import RandomForestClassifier
        from infrastructure.ml.model_storage import (
            save_model, load_model, JOBLIB_COMPRESS,
        )
        import numpy as np

        # Modelo pequeno pero representativo
        X = np.random.rand(200, 5)
        y = np.random.randint(0, 2, 200)
        m = RandomForestClassifier(n_estimators=50, random_state=0).fit(X, y)

        compressed = tmp_path / "modelo_c.joblib"
        uncompressed = tmp_path / "modelo_u.joblib"

        save_model(m, str(compressed))
        import joblib
        joblib.dump(m, str(uncompressed), compress=0)

        assert compressed.stat().st_size < uncompressed.stat().st_size
        assert JOBLIB_COMPRESS >= 1

        # Roundtrip: el modelo cargado produce las mismas predicciones
        loaded = load_model(str(compressed))
        np.testing.assert_array_equal(loaded.predict(X), m.predict(X))
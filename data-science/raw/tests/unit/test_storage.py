import os
import tempfile
from pathlib import Path

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

    def test_oci_sin_vars_lanza_keyerror(self):
        from infrastructure.storage import get_storage

        os.environ["STORAGE_BACKEND"] = "oci"
        for k in ["OCI_NAMESPACE", "OCI_BUCKET", "OCI_REGION"]:
            os.environ.pop(k, None)
        with pytest.raises(KeyError):
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

            def put_object(self, namespace, bucket, name, body):
                self.objects[f"{bucket}/{name}"] = body

            def get_object(self, namespace, bucket, name):
                if f"{bucket}/{name}" not in self.objects:
                    raise Exception("404 not found")
                return _Response(self.objects[f"{bucket}/{name}"])

            def head_object(self, namespace, bucket, name):
                if f"{bucket}/{name}" not in self.objects:
                    raise Exception("404 not found")
                return None

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
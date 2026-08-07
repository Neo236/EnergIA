import base64
import hashlib
import shutil
from pathlib import Path
from typing import Protocol


class Storage(Protocol):
    def upload(self, local_path: str, remote_path: str) -> None: ...
    def download(self, remote_path: str, local_path: str) -> None: ...
    def exists(self, remote_path: str) -> bool: ...
    def delete(self, remote_path: str) -> None: ...
    def list_objects(self, prefix: str) -> list[str]: ...
    def head_info(self, remote_path: str) -> dict | None: ...
    def copy(self, src_remote: str, dst_remote: str) -> None: ...


class LocalStorage:
    """Filesystem-backed storage. Default en dev/CI/tests."""

    def __init__(self, root: str = "."):
        self.root = Path(root).resolve()

    def _resolve(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.root / p
        return p

    def upload(self, local_path: str, remote_path: str) -> None:
        src = Path(local_path)
        dst = self._resolve(remote_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())

    def download(self, remote_path: str, local_path: str) -> None:
        src = self._resolve(remote_path)
        if not src.exists():
            raise FileNotFoundError(f"Storage object not found: {remote_path}")
        dst = Path(local_path)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())

    def exists(self, remote_path: str) -> bool:
        return self._resolve(remote_path).exists()

    def delete(self, remote_path: str) -> None:
        path = self._resolve(remote_path)
        if not path.exists():
            raise FileNotFoundError(f"Storage object not found: {remote_path}")
        path.unlink()

    def list_objects(self, prefix: str) -> list[str]:
        base = self._resolve(prefix)
        if not base.exists():
            return []
        out = []
        if base.is_file():
            return [prefix]
        for p in base.rglob("*"):
            if p.is_file():
                rel = p.relative_to(self.root).as_posix()
                out.append(rel)
        return out

    def head_info(self, remote_path: str) -> dict | None:
        """Devuelve {etag, md5, size} sin descargar el body.

        md5 esta en base64 (compatible con content-md5 de OCI).
        None si el objeto no existe.
        """
        path = self._resolve(remote_path)
        if not path.exists():
            return None
        raw = path.read_bytes()
        md5_hex = hashlib.md5(raw).hexdigest()
        return {
            "etag": md5_hex,
            "md5": base64.b64encode(bytes.fromhex(md5_hex)).decode(),
            "size": path.stat().st_size,
        }

    def copy(self, src_remote: str, dst_remote: str) -> None:
        """Copia server-side (local: shutil.copy2)."""
        src = self._resolve(src_remote)
        if not src.exists():
            raise FileNotFoundError(f"Storage object not found: {src_remote}")
        dst = self._resolve(dst_remote)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
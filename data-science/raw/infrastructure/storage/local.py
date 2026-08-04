from pathlib import Path
from typing import Protocol


class Storage(Protocol):
    def upload(self, local_path: str, remote_path: str) -> None: ...
    def download(self, remote_path: str, local_path: str) -> None: ...
    def exists(self, remote_path: str) -> bool: ...


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
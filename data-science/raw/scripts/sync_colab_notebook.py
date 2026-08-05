"""Sincroniza el notebook de Colab que actua como fuente de verdad del dataset.

Descarga el notebook publico desde Google Drive (el Colab notebook vive en
Drive subyacente), valida su integridad via SHA256 contra el archivo local
y reporta (o sobrescribe) diferencias.

El hash se calcula sobre las **celdas de codigo** del notebook (no sobre el
archivo entero), porque los outputs y execution_count cambian entre
ejecuciones pero la logica es la misma. Asi, dos versiones "limpias" del
mismo notebook producen el mismo hash.

Uso:
    python scripts/sync_colab_notebook.py            # solo check (default)
    python scripts/sync_colab_notebook.py --apply    # descarga y sobrescribe
    python scripts/sync_colab_notebook.py --print    # imprime hash remoto

Requisitos: requests (en requirements.txt).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from pathlib import Path
from typing import Iterable

import requests

# URL publica del notebook fuente de verdad (semana 1 - Constanza / Nahuel).
COLAB_NOTEBOOK_URL = (
    "https://colab.research.google.com/drive/"
    "1LiisJEOadkTdBZ8nLMKb_T2a3El3nLJi?usp=drive_link"
)

# Ruta destino: el archivo que el test de paridad consume.
DEFAULT_LOCAL_PATH = (
    Path(__file__).resolve().parents[1] / "notebooks" / "data_colab.ipynb"
)

# Endpoints a intentar, en orden.
# - Drive /uc?export=download&id={ID}: descarga el .ipynb real desde Drive
#   subyacente (el notebook de Colab esta almacenado alli). Es el unico
#   endpoint publico estable.
# - Los endpoints Colab directos (/download, ?format=ipynb, etc.) devuelven
#   HTML y se mantienen como fallback por si Drive cambia su politica.
DOWNLOAD_ENDPOINTS_TEMPLATE = (
    "https://drive.google.com/uc?export=download&id={file_id}",
    "https://colab.research.google.com/drive/{file_id}/download?format=ipynb",
    "https://colab.research.google.com/drive/{file_id}/download",
    "https://colab.research.google.com/drive/{file_id}?format=ipynb",
    "https://colab.research.google.com/notebooks/{file_id}.ipynb",
)

REQUEST_TIMEOUT = 60  # segundos


def _extract_file_id(url: str) -> str:
    """Extrae el FILE_ID de una URL tipo /drive/{ID}?... o /drive/{ID}/..."""
    needle = "/drive/"
    idx = url.find(needle)
    if idx == -1:
        raise ValueError(f"URL no contiene /drive/: {url}")
    tail = url[idx + len(needle):]
    file_id = tail.split("?")[0].split("/")[0]
    if not file_id:
        raise ValueError(f"No se pudo extraer FILE_ID de: {url}")
    return file_id


def _looks_like_notebook(content: bytes) -> bool:
    """Heuristica barata: el .ipynb valido es JSON con clave 'cells'."""
    if not content or not content.lstrip().startswith(b"{"):
        return False
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return False
    return isinstance(parsed, dict) and "cells" in parsed


def _candidate_urls(file_id: str) -> Iterable[str]:
    return (tpl.format(file_id=file_id) for tpl in DOWNLOAD_ENDPOINTS_TEMPLATE)


def _fetch_notebook(url: str) -> bytes:
    """Descarga el notebook desde la URL publica. Raise si falla."""
    log = logging.getLogger("sync_colab")
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "energiai-sync/1.0 "
            "(+https://github.com/No-Country-simulation/G9-LATAM-TEAM-09)"
        ),
        "Accept": "*/*",
    })

    for endpoint in _candidate_urls(_extract_file_id(url)):
        log.info("Probando endpoint: %s", endpoint)
        try:
            resp = session.get(
                endpoint, timeout=REQUEST_TIMEOUT, allow_redirects=True
            )
        except requests.RequestException as e:
            log.warning("Fallo request a %s: %s", endpoint, e)
            continue
        if resp.status_code != 200:
            log.warning("HTTP %s desde %s", resp.status_code, endpoint)
            continue
        body = resp.content
        if _looks_like_notebook(body):
            log.info("Notebook descargado (%d bytes) desde %s", len(body), endpoint)
            return body
        log.warning(
            "Respuesta no parece un .ipynb valido (%d bytes, content-type=%s)",
            len(body),
            resp.headers.get("Content-Type", "?"),
        )
    raise RuntimeError(
        "No se pudo descargar el notebook desde ningun endpoint conocido. "
        "Exporta manualmente desde Colab (File > Download .ipynb) y copialo a "
        f"{DEFAULT_LOCAL_PATH}."
    )


def _extract_code_cells(notebook_bytes: bytes) -> str:
    """Devuelve la concatenacion de las celdas de codigo (sin outputs).

    Esto es lo que usamos como 'fuente de verdad' del notebook, porque los
    outputs y execution_count cambian entre ejecuciones pero la logica es
    la misma.
    """
    nb = json.loads(notebook_bytes)
    cells = nb.get("cells", [])
    parts = []
    for cell in cells:
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", [])
        if isinstance(src, list):
            src = "".join(src)
        parts.append(src)
    # Normaliza whitespace al final de cada linea para tolerar trailing
    # espacios que pueden variar entre exportacion Drive y Colab UI.
    normalized = "\n".join(re.sub(r"\s+$", "", line) for line in "\n".join(parts).split("\n"))
    return normalized


def code_hash(notebook_bytes: bytes) -> str:
    """SHA256 de las celdas de codigo del notebook (no del archivo entero)."""
    return hashlib.sha256(_extract_code_cells(notebook_bytes).encode("utf-8")).hexdigest()


def code_hash_file(path: Path) -> str:
    return code_hash(path.read_bytes())


def sync(url: str = COLAB_NOTEBOOK_URL,
         local_path: Path = DEFAULT_LOCAL_PATH,
         apply: bool = False,
         logger: logging.Logger | None = None) -> int:
    """Compara el codigo del notebook remoto vs local.

    Returns:
        0 si coinciden (o se aplico con exito),
        1 si difieren (sin apply),
        2 si hubo error de descarga.
    """
    log = logger or logging.getLogger("sync_colab")
    log.info("Source URL: %s", url)
    log.info("Local path: %s", local_path)

    try:
        remote_bytes = _fetch_notebook(url)
    except Exception as e:
        log.error("%s", e)
        return 2

    remote_hash = code_hash(remote_bytes)
    log.info("Remote code SHA256: %s", remote_hash)

    if not local_path.exists():
        log.warning("Archivo local NO existe: %s", local_path)
        if apply:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(remote_bytes)
            log.info("Archivo local creado desde la version remota.")
            return 0
        log.info("Use --apply para crearlo desde la version remota.")
        return 1

    local_hash = code_hash_file(local_path)
    log.info("Local  code SHA256: %s", local_hash)

    if remote_hash == local_hash:
        log.info("OK - el codigo del notebook coincide con la version remota.")
        return 0

    log.warning(
        "DIFERENCIA detectada en el codigo del notebook. "
        "Revisar el diff antes de aplicar."
    )
    if apply:
        local_path.write_bytes(remote_bytes)
        log.info("Archivo local sobrescrito con la version remota.")
        return 0
    log.info("Use --apply para sobrescribir.")
    return 1


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--url", default=COLAB_NOTEBOOK_URL,
                   help="URL publica del notebook en Colab")
    p.add_argument("--local", default=str(DEFAULT_LOCAL_PATH), type=Path,
                   help="Ruta local del archivo .ipynb")
    p.add_argument("--apply", action="store_true",
                   help="Sobrescribe el archivo local si hay diferencias")
    p.add_argument("--print", action="store_true", dest="print_hash",
                   help="Solo imprime el hash de codigo remoto y sale")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    log = logging.getLogger("sync_colab")

    if args.print_hash:
        try:
            body = _fetch_notebook(args.url)
        except Exception as e:
            log.error("%s", e)
            return 2
        print(code_hash(body))
        return 0

    return sync(url=args.url, local_path=args.local, apply=args.apply, logger=log)


if __name__ == "__main__":
    sys.exit(main())

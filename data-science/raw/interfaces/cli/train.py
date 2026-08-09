import base64
import hashlib
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from application.training import entrenar_y_guardar_modelo
from infrastructure.config import Config
from infrastructure.data.simulation import generar_dataset
from infrastructure.storage import get_storage

log = logging.getLogger(__name__)


# Prefijos dentro del bucket. latest/ es el archivo vigente; archive/
# guarda los snapshots anteriores SOLO cuando la logica del codigo cambia
# (no cuando solo cambia el seed/datos).
REMOTE_PREFIX_LATEST = "latest"
REMOTE_PREFIX_ARCHIVE = "archive"
MANIFEST_PATH = f"{REMOTE_PREFIX_ARCHIVE}/manifest.json"
MANIFEST_VERSION = 1


def compute_code_version() -> str:
    """Devuelve un identificador del codigo que produjo este entrenamiento.

    Prioridad:
      1. git HEAD short SHA (si estamos en un repo).
      2. SHA256 sobre los archivos fuente de training/dominio (fallback).

    La idea: dos corridas con mismo code_version son "el mismo modelo".
    Cambios de seed/datos dentro del mismo codigo NO generan archives.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5, check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return f"git:{result.stdout.strip()}"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: hash de los archivos fuente del pipeline de ML.
    repo_root = Path(__file__).resolve().parents[3]
    src_files = [
        "application/training.py",
        "application/inference.py",
        "domain/scoring.py",
        "domain/recommendations.py",
        "infrastructure/data/simulation.py",
        "infrastructure/config.py",
    ]
    h = hashlib.sha256()
    for rel in src_files:
        path = repo_root / rel
        if path.exists():
            h.update(rel.encode())
            h.update(path.read_bytes())
    return f"src:{h.hexdigest()[:12]}"


def _md5_b64(path: Path) -> str:
    """MD5 del archivo en base64 (formato OCI content-md5)."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return base64.b64encode(h.digest()).decode()


def _write_sha256_sidecar(path: Path) -> None:
    """Escribe `<path>.sha256` con el hash hex SHA256 del archivo.

    Util para verificar integridad al descargar desde el bucket.
    Formato: `<hex>  <basename>\n` (estilo `sha256sum`).
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    sidecar = path.with_suffix(path.suffix + ".sha256")
    sidecar.write_text(f"{h.hexdigest()}  {path.name}\n")


def _empty_manifest() -> dict:
    return {"version": MANIFEST_VERSION, "files": {}}


def _read_manifest(storage) -> dict:
    """Descarga y parsea el manifest desde el bucket.

    Si no existe, retorna un manifest vacio. Si esta corrupto, loguea
    warning y retorna vacio (fail-safe: prefiero re-archivar a perder
    la capacidad de detectar archives).
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            tmp_path = tmp.name
        try:
            storage.download(MANIFEST_PATH, tmp_path)
        except FileNotFoundError:
            return _empty_manifest()
        try:
            with open(tmp_path) as f:
                data = json.load(f)
            if data.get("version") != MANIFEST_VERSION:
                log.warning(
                    "Manifest version %s != esperado %s; re-creando",
                    data.get("version"), MANIFEST_VERSION,
                )
                return _empty_manifest()
            if "files" not in data or not isinstance(data["files"], dict):
                return _empty_manifest()
            return data
        except (json.JSONDecodeError, OSError) as e:
            log.warning("Manifest corrupto, recreando vacio: %s", e)
            return _empty_manifest()
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    except Exception as e:
        log.warning("No se pudo leer manifest: %s", e)
        return _empty_manifest()


def _write_manifest(storage, manifest: dict) -> bool:
    """Sube el manifest al bucket. Retorna True si subio OK.

    Tolerante a fallos: si falla, no rompe el pipeline (el siguiente
    upload lo regenera desde cero).
    """
    manifest.setdefault("version", MANIFEST_VERSION)
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json", encoding="utf-8"
        ) as tmp:
            json.dump(manifest, tmp, indent=2, ensure_ascii=False, sort_keys=True)
            tmp_path = tmp.name
        try:
            storage.upload(tmp_path, MANIFEST_PATH)
            return True
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    except Exception as e:
        log.warning("No se pudo escribir manifest: %s", e)
        return False


def _archive_exists_for_code(
    storage, remote_name: str, code_short: str
) -> bool:
    """True si el manifest registra un archive con este code_short para este file.

    Reemplaza el `list_objects` previo (1 LIST por upload) por 1 GET a
    manifest.json (mas barato en OCI cuando hay muchos archives).
    """
    manifest = _read_manifest(storage)
    return code_short in manifest["files"].get(remote_name, [])


def _record_archive(storage, remote_name: str, code_short: str, remote_archive_path: str) -> None:
    """Agrega una entrada al manifest y lo sube. Best-effort."""
    manifest = _read_manifest(storage)
    manifest["files"].setdefault(remote_name, [])
    if code_short not in manifest["files"][remote_name]:
        manifest["files"][remote_name].append(code_short)
    # Mantener metadata liviana: solo code_shorts + el path del ultimo archive.
    manifest["files"].setdefault("_last_archive", {})
    manifest["files"]["_last_archive"][remote_name] = remote_archive_path
    _write_manifest(storage, manifest)


def _upload_with_rotation(
    storage,
    local_path: str,
    remote_name: str,
    code_version: str | None = None,
) -> str:
    """Sube `local_path` respetando latest/archive con code-version-awareness.

    Optimizaciones de costo (sobre todo relevantes para OCI):
      - Usa `head_info` para comparar MD5 sin descargar el body.
      - Usa `copy` server-side para archivar (sin transferir el body).
      - No sube NADA si el contenido remoto coincide (md5 match).

    Reglas:
      - Si NO existe `latest/<name>`: subir como latest (nuevo archivo, sin archive).
      - Si existe latest/ y MD5 coincide con el local: skip (no opera en el bucket).
      - Si existe latest/ y difiere, pero el code_version actual ya fue archivado:
        refrescar latest/ (1 PUT), sin archive.
      - Si existe latest/, difiere, y code_version es nuevo: copy server-side
        de latest/ -> archive, delete latest, upload new (3 ops, 0 body transfer).

    Retorna: "uploaded" | "skipped_identical" | "refreshed" | "rotated".
    """
    src = Path(local_path)
    if not src.exists():
        log.warning("Local artifact no existe: %s", local_path)
        return "skipped_missing"

    if code_version is None:
        code_version = compute_code_version()
    code_short = code_version.split(":", 1)[1][:7] if ":" in code_version else code_version[:7]

    remote_latest = f"{REMOTE_PREFIX_LATEST}/{remote_name}"

    # Compute local MD5 una sola vez (cheap, streaming).
    local_md5_b64 = _md5_b64(src)

    # Metadata del remoto SIN descargar el body (1 HEAD, 0 body transfer).
    remote_info = storage.head_info(remote_latest)

    if remote_info is not None and remote_info.get("md5") == local_md5_b64:
        log.info(
            "Sin cambios en %s (md5 coincide, 0 ops en bucket)", remote_latest
        )
        return "skipped_identical"

    # Contenido difiere o no existe remoto -> decision de rotacion.
    if remote_info is not None:
        if _archive_exists_for_code(storage, remote_name, code_short):
            log.info(
                "Codigo %s ya archivado; refrescando latest/ sin nuevo snapshot",
                code_short,
            )
            storage.upload(local_path, remote_latest)
            return "refreshed"

        # Codigo nuevo: copy server-side (no body transfer), delete, upload.
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
        remote_archive = f"{REMOTE_PREFIX_ARCHIVE}/{ts}_{code_short}_{remote_name}"
        log.info(
            "Rotando %s -> %s (nuevo code_version=%s, copy server-side)",
            remote_latest, remote_archive, code_short,
        )
        try:
            storage.copy(remote_latest, remote_archive)
            storage.delete(remote_latest)
            storage.upload(local_path, remote_latest)
        except Exception:
            log.exception("Fallo archivando %s", remote_latest)
            raise
        # Best-effort: actualizar manifest con el nuevo archive.
        _record_archive(storage, remote_name, code_short, remote_archive)
        return "rotated"

    # No existe latest/ -> primer upload.
    storage.upload(local_path, remote_latest)
    return "uploaded"


def _safe_upload_with_rotation(
    storage, local_path: str, remote_name: str, code_version: str | None = None
) -> None:
    """Wrapper tolerante: loguea el fallo pero no propaga.

    Tambien emite metricas estructuradas (action, bytes, duration_ms) para
    observabilidad y monitoreo de costos.
    """
    if not os.path.exists(local_path):
        print(f"[SKIP] {local_path} no existe localmente")
        return
    bytes_size = Path(local_path).stat().st_size
    started = time.monotonic()
    try:
        action = _upload_with_rotation(storage, local_path, remote_name, code_version)
        duration_ms = (time.monotonic() - started) * 1000
        print(f"[OK] {action}: latest/{remote_name}")
        log.info(
            "storage_upload op=%s action=%s bytes=%d duration_ms=%.1f",
            remote_name, action, bytes_size, duration_ms,
            extra={
                "remote_name": remote_name,
                "action": action,
                "bytes": bytes_size,
                "duration_ms": duration_ms,
            },
        )
    except Exception as e:
        duration_ms = (time.monotonic() - started) * 1000
        print(
            f"[WARN] No se pudo subir {remote_name} al storage: {e}. "
            "El proceso continua sin el bucket.",
            file=sys.stderr,
        )
        log.warning(
            "storage_upload_failed op=%s bytes=%d duration_ms=%.1f error=%s",
            remote_name, bytes_size, duration_ms, e,
        )


def main(argv: list[str] | None = None) -> int:
    """Entrena y sube artefactos al bucket.

    Con --dry-run: entrena localmente y simula las decisiones de upload
    contra el bucket (si esta disponible) sin hacer PUT/GET reales.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Entrena y persiste el modelo")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Entrena localmente pero NO sube ni descarga del bucket",
    )
    args = parser.parse_args(argv)
    dry_run = args.dry_run

    print(f"[INFO] Num clientes={Config.NUM_CLIENTES} seed={Config.RANDOM_SEED}")
    if dry_run:
        print("[DRY-RUN] No se haran uploads ni downloads del bucket")

    df = generar_dataset(Config.NUM_CLIENTES, Config.RANDOM_SEED)

    counts = df["categoria"].value_counts()
    pct = (counts / counts.sum() * 100).round(2)
    print(f"[INFO] Distribucion categoria (%):\n{pct.to_string()}")

    Path(Config.OUTPUT_JSON_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(Config.OUTPUT_MODEL_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(Config.OUTPUT_METRICAS_PATH).parent.mkdir(parents=True, exist_ok=True)

    df.to_json(Config.OUTPUT_JSON_PATH, orient="records", force_ascii=False, indent=4)
    print(f"[OK] JSON exportado: {Config.OUTPUT_JSON_PATH} ({len(df)} registros)")
    _write_sha256_sidecar(Path(Config.OUTPUT_JSON_PATH))

    csv_path = Path(Config.OUTPUT_JSON_PATH).with_suffix(".csv")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[OK] CSV exportado: {csv_path}")
    _write_sha256_sidecar(csv_path)

    print("[INFO] Entrenando pipeline...")
    resultado = entrenar_y_guardar_modelo(
        df=df,
        output_path=Config.OUTPUT_MODEL_PATH,
        metricas_path=Config.OUTPUT_METRICAS_PATH,
        random_seed=Config.RANDOM_SEED,
    )
    print(f"[OK] Modelo exportado: {Config.OUTPUT_MODEL_PATH}")
    _write_sha256_sidecar(Path(Config.OUTPUT_MODEL_PATH))
    print(f"[OK] Metricas persistidas: {Config.OUTPUT_METRICAS_PATH}")
    _write_sha256_sidecar(Path(Config.OUTPUT_METRICAS_PATH))

    if dry_run:
        print("\n[DRY-RUN] Entrenamiento completado. Saltando uploads.")
        print("\n[REPORTE DE CLASIFICACION]")
        print(resultado["reporte"])
        return 0

    # Subir artefactos al storage (si esta configurado). Tolerante a fallos:
    # si no hay bucket o falla la red, el pipeline no se rompe.
    backend = os.getenv("STORAGE_BACKEND", "local").lower()
    if backend == "oci":
        try:
            storage = get_storage()
        except Exception as e:
            print(f"[WARN] No se pudo inicializar storage OCI: {e}", file=sys.stderr)
            storage = None
    else:
        storage = get_storage()

    if storage is not None:
        code_version = compute_code_version()
        print(f"[INFO] code_version={code_version}")
        _safe_upload_with_rotation(storage, Config.OUTPUT_JSON_PATH, "database_beta.json", code_version)
        _safe_upload_with_rotation(storage, str(csv_path), "database_beta.csv", code_version)
        _safe_upload_with_rotation(
            storage, Config.OUTPUT_MODEL_PATH, "modelo_eficiencia_v1.joblib", code_version
        )
        _safe_upload_with_rotation(
            storage, Config.OUTPUT_METRICAS_PATH,
            "metricas_v1.joblib", code_version,
        )

    print("\n[REPORTE DE CLASIFICACION]")
    print(resultado["reporte"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
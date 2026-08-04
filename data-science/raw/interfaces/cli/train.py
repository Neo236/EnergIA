import os
import sys
from pathlib import Path

from application.training import entrenar_y_guardar_modelo
from infrastructure.config import Config
from infrastructure.data.simulation import generar_dataset
from infrastructure.storage import get_storage


def _upload_artifact(storage, local_path, remote_path):
    if not os.path.exists(local_path):
        return
    print(f"[UPLOAD] {local_path} → {remote_path}")
    storage.upload(local_path, remote_path)


def main() -> int:
    print(f"[INFO] Num clientes={Config.NUM_CLIENTES} seed={Config.RANDOM_SEED}")

    df = generar_dataset(Config.NUM_CLIENTES, Config.RANDOM_SEED)

    counts = df["categoria"].value_counts()
    pct = (counts / counts.sum() * 100).round(2)
    print(f"[INFO] Distribución categoria (%):\n{pct.to_string()}")

    Path(Config.OUTPUT_JSON_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(Config.OUTPUT_MODEL_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(Config.OUTPUT_METRICAS_PATH).parent.mkdir(parents=True, exist_ok=True)

    df.to_json(Config.OUTPUT_JSON_PATH, orient="records", indent=4)
    print(f"[OK] JSON exportado: {Config.OUTPUT_JSON_PATH} ({len(df)} registros)")

    print("[INFO] Entrenando pipeline...")
    resultado = entrenar_y_guardar_modelo(
        df=df,
        output_path=Config.OUTPUT_MODEL_PATH,
        metricas_path=Config.OUTPUT_METRICAS_PATH,
        random_seed=Config.RANDOM_SEED,
    )
    print(f"[OK] Modelo exportado: {Config.OUTPUT_MODEL_PATH}")
    print(f"[OK] Métricas persistidas: {Config.OUTPUT_METRICAS_PATH}")

    storage = get_storage()
    try:
        _upload_artifact(storage, Config.OUTPUT_JSON_PATH, "data/database_beta.json")
        _upload_artifact(storage, Config.OUTPUT_MODEL_PATH, "data/modelo_eficiencia_v1.joblib")
        _upload_artifact(storage, Config.OUTPUT_METRICAS_PATH, "data/metricas_v1.joblib")
        print(f"[OK] Artefactos subidos a storage ({os.getenv('STORAGE_BACKEND', 'local')})")
    except Exception as e:
        print(f"[WARN] Fallo upload storage: {e}", file=sys.stderr)

    print("\n[REPORTE DE CLASIFICACIÓN]")
    print(resultado["reporte"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
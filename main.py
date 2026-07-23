import pandas as pd

from config import Config
from src.data_simulation import generar_datos_base
from src.model import entrenar_y_guardar_modelo
from src.rules import asignar_categoria


def _consolidar(hogar: pd.DataFrame, consumo: pd.DataFrame, equipamientos: pd.DataFrame) -> pd.DataFrame:
    return (hogar.merge(consumo, on="id_cliente")
                 .merge(equipamientos, on="id_cliente"))


def main() -> int:
    print(f"[INFO] Num clientes={Config.NUM_CLIENTES} seed={Config.RANDOM_SEED}")

    hogar, consumo, equip = generar_datos_base(Config.NUM_CLIENTES, Config.RANDOM_SEED)
    df = _consolidar(hogar, consumo, equip)

    df = asignar_categoria(df, Config.UMBRAL_EFICIENTE, Config.UMBRAL_MODERADO)

    df_limpio = df.dropna(subset=["categoria"]).reset_index(drop=True)

    counts = df_limpio["categoria"].value_counts()
    pct = (counts / counts.sum() * 100).round(2)
    print(f"[INFO] Distribución (%):\n{pct.to_string()}")

    df_limpio.to_json(Config.OUTPUT_JSON_PATH, orient="records", indent=4)
    print(f"[OK] JSON exportado: {Config.OUTPUT_JSON_PATH} ({len(df_limpio)} registros)")

    print("[INFO] Entrenando pipeline...")
    resultado = entrenar_y_guardar_modelo(
        df=df_limpio,
        output_path=Config.OUTPUT_MODEL_PATH,
        metricas_path=Config.OUTPUT_METRICAS_PATH,
        random_seed=Config.RANDOM_SEED,
    )
    print(f"[OK] Modelo exportado: {Config.OUTPUT_MODEL_PATH}")
    print(f"[OK] Métricas persistidas: {Config.OUTPUT_METRICAS_PATH}")

    print("\n[REPORTE DE CLASIFICACIÓN]")
    print(resultado["reporte"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

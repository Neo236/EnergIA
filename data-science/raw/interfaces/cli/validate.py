import sys

from infrastructure.config import Config
from infrastructure.validators.artifacts import (
    validar_json,
    validar_metricas,
    validar_modelo,
)


def main():
    print("=" * 70)
    print("VALIDACIÓN DE ARTEFACTOS - MVP EFICIENCIA ENERGÉTICA")
    print("=" * 70)

    r1 = validar_json(Config.OUTPUT_JSON_PATH)
    print(f"\n[VAL 1] JSON {Config.OUTPUT_JSON_PATH}")
    print(f"  ok={r1['ok']}  {r1['msg']}")

    r2 = validar_modelo(Config.OUTPUT_MODEL_PATH)
    print(f"\n[VAL 2] Modelo {Config.OUTPUT_MODEL_PATH}")
    print(f"  ok={r2['ok']}  {r2['msg']}")

    r3 = validar_metricas(Config.OUTPUT_METRICAS_PATH)
    print(f"\n[VAL 3] Métricas classification_report")
    print(r3["reporte"].rstrip())
    print(f"  ok={r3['ok']}  {r3['msg']}")

    print("\n" + "=" * 70)
    all_ok = r1["ok"] and r2["ok"] and r3["ok"]
    print(f"RESULTADO GLOBAL: {'PASS' if all_ok else 'FAIL'}")
    print("=" * 70)
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
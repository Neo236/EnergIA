import json
import os
import sys
import joblib
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline

from config import Config


def validar_json(path: str) -> dict:
    if not os.path.exists(path):
        return {"ok": False, "msg": f"NO existe: {path}"}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        return {"ok": False, "msg": "Raíz no es lista."}
    if not all(isinstance(x, dict) for x in data):
        return {"ok": False, "msg": "No todos los elementos son dicts."}
    return {"ok": True, "msg": f"Lista de {len(data)} dicts.", "n": len(data)}


def validar_modelo(path: str) -> dict:
    if not os.path.exists(path):
        return {"ok": False, "msg": f"NO existe: {path}"}
    obj = joblib.load(path)
    if not isinstance(obj, Pipeline):
        return {"ok": False, "msg": f"Tipo={type(obj).__name__}, no Pipeline."}
    steps = list(obj.named_steps.keys())
    return {"ok": True, "msg": f"Pipeline válido. Steps: {steps}", "pipeline": obj}


def validar_metricas(path: str) -> dict:
    if not os.path.exists(path):
        return {"ok": False, "msg": f"NO existe: {path}", "reporte": ""}
    blob = joblib.load(path)
    y_test = blob["y_test"]
    y_pred = blob["y_pred"]
    reporte = classification_report(y_test, y_pred, zero_division=0)

    f1_eficiente = 0.0
    for line in reporte.splitlines():
        parts = line.split()
        if parts and parts[0] == "eficiente":
            f1_eficiente = float(parts[3])
            break

    ok = f1_eficiente > 0.0
    return {
        "ok": ok,
        "msg": f"f1-score(eficiente)={f1_eficiente:.4f} (>0.00 esperado)",
        "reporte": reporte,
        "f1": f1_eficiente,
    }


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

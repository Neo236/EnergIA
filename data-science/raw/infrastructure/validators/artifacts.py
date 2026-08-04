import json
import os

import joblib
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline


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
        if parts and parts[0].lower() == "eficiente":
            f1_eficiente = float(parts[3])
            break

    ok = f1_eficiente > 0.0
    return {
        "ok": ok,
        "msg": f"f1-score(Eficiente)={f1_eficiente:.4f} (>0.00 esperado)",
        "reporte": reporte,
        "f1": f1_eficiente,
    }
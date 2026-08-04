def calcular_score_eficiencia(input_data: dict) -> float:
    consumo = float(input_data.get("consumo_kwh",
                                    input_data.get("consumo_electrico_kwh", 0)))
    aislamiento = str(input_data.get("calidad_aislamiento", "Media")).lower()
    fuente_cal = str(input_data.get("fuente_calefaccion", "Otros"))
    fuente_agua = str(input_data.get("fuente_agua_caliente", "Otros"))
    zona_fria = bool(input_data.get("zona_fria", False))
    horas_alto = int(input_data.get("horas_alto_consumo", 0))
    cantidad_equipos = int(input_data.get("cantidad_equipos", 0))

    score = (
        -0.02 * consumo
        + (10 if "muy alta" in aislamiento else
           6 if "alta" in aislamiento else
           0 if "media" in aislamiento else
           -5 if "baja" in aislamiento and "muy" not in aislamiento else -10)
        + (10 if fuente_cal == "Solar" else 0 if fuente_cal == "Otros" else -4)
        + (4 if fuente_agua == "Solar" else 0 if fuente_agua == "Otros" else -2)
        - (8 if zona_fria else 0)
        - 0.05 * horas_alto
        - 0.06 * cantidad_equipos
    )
    return score


def asignar_categoria_por_score(score: float, cuantiles: tuple[float, float]) -> str:
    q_inef, q_ef = cuantiles
    if score >= q_ef:
        return "Eficiente"
    if score >= q_inef:
        return "Moderado"
    return "Ineficiente"
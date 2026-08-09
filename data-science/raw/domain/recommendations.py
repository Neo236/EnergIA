from domain.scoring import es_si


def calcular_recomendaciones(input_data: dict) -> list[str]:
    recs: list[str] = []

    consumo = float(input_data.get("consumo_kwh", 0))

    if consumo > 700:
        recs.append("Tu consumo eléctrico es muy elevado. "
                    "Considera revisar electrodomésticos de alto consumo y aislación térmica.")
    elif consumo > 450:
        recs.append("Tu consumo eléctrico está por encima del promedio. "
                    "Audita el uso de calefacción y electrodomésticos en horario punta.")

    aislamiento = str(input_data.get("calidad_aislamiento", "Media")).lower()
    if "muy baja" in aislamiento or "muy_baja" in aislamiento:
        recs.append("Mejorar el aislamiento térmico de tu hogar reducirá "
                    "drásticamente la necesidad de climatización.")
    elif "baja" in aislamiento and "muy" not in aislamiento:
        recs.append("Refuerza puertas y ventanas: una aislación Media reduce ~30% el gasto en climatización.")

    fuente_cal = str(input_data.get("fuente_calefaccion", "Otros"))
    if fuente_cal == "Electricidad":
        recs.append("Evalúa migrar la calefacción a Solar o Gas: la electricidad es la fuente más cara del dataset.")
    elif fuente_cal == "Otros":
        recs.append("Considera sistemas de calefacción más eficientes (Solar o bomba de calor).")

    if es_si(input_data.get("zona_fria", False)):
        recs.append("Vivir en zona fría incrementa el consumo. Prioriza aislación y calefacción eficiente.")

    horas_alto = int(input_data.get("horas_alto_consumo", 0))
    if horas_alto > 14:
        recs.append("Tienes más de 14h diarias de alto consumo. Centraliza el uso en horarios de menor demanda para optimizar tu tarifa.")

    cantidad_equipos = int(input_data.get("cantidad_equipos", 0))
    if cantidad_equipos > 70:
        recs.append("Tienes una gran cantidad de equipos eléctricos. Reemplaza los más antiguos por clase A+: el ahorro a 5 años supera la inversión.")

    antiguedad = int(input_data.get("antiguedad_vivienda", 0))
    if antiguedad > 80:
        recs.append("Vivienda con más de 80 años: revisa instalación eléctrica y aislación; suele haber pérdidas ocultas.")

    if not recs:
        recs.append("Tu hogar está bien calibrado. Mantén hábitos de consumo eficientes.")
    return recs
import numpy as np
import pandas as pd


TIPO_INMUEBLE = ["Casa", "Departamento", "Comercio", "Pyme"]
TIPO_INMUEBLE_PROBS = [0.3525, 0.2980, 0.1970, 0.1525]

CALIDAD_AISLAMIENTO = ["Muy Alta", "Alta", "Media", "Baja", "Muy Baja"]
CALIDAD_AISLAMIENTO_PROBS = [0.1220, 0.1965, 0.3380, 0.2055, 0.1380]

FUENTE = ["Electricidad", "Solar", "Otros"]
FUENTE_PROBS = [0.4505, 0.3630, 0.1865]

CATEGORIA = ["Eficiente", "Moderado", "Ineficiente"]


def generar_dataset(num_clientes: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    hogar_id = np.array([f"Hogar_{i:04d}" for i in range(1, num_clientes + 1)])

    tipo_inmueble = rng.choice(TIPO_INMUEBLE, size=num_clientes, p=TIPO_INMUEBLE_PROBS)

    metros_cuadrados = np.round(
        rng.normal(1048, 576, num_clientes).clip(26, 2000)
    ).astype(int)

    antiguedad_vivienda = np.round(
        rng.normal(77, 43, num_clientes).clip(0, 150)
    ).astype(int)

    zona_fria = rng.choice([True, False], size=num_clientes, p=[0.5, 0.5])

    calidad_aislamiento = rng.choice(
        CALIDAD_AISLAMIENTO, size=num_clientes, p=CALIDAD_AISLAMIENTO_PROBS
    )

    fuente_calefaccion = rng.choice(FUENTE, size=num_clientes, p=FUENTE_PROBS)

    fuente_agua_caliente = rng.choice(FUENTE, size=num_clientes, p=FUENTE_PROBS)

    uso_horario_pico = rng.choice([True, False], size=num_clientes, p=[0.5, 0.5])

    horas_alto_consumo = np.round(
        rng.normal(12, 7, num_clientes).clip(0, 24)
    ).astype(int)

    cantidad_equipos = np.round(
        rng.normal(51, 29, num_clientes).clip(1, 100)
    ).astype(int)

    base_consumo = (
        0.05 * metros_cuadrados
        + 1.5 * antiguedad_vivienda * 0.3
        + zona_fria.astype(int) * 80
        + (calidad_aislamiento == "Muy Baja").astype(int) * 120
        + (calidad_aislamiento == "Baja").astype(int) * 70
        + (calidad_aislamiento == "Media").astype(int) * 30
        + (fuente_calefaccion == "Electricidad").astype(int) * 110
        + (fuente_calefaccion == "Otros").astype(int) * 40
        + uso_horario_pico.astype(int) * 60
        + 0.6 * horas_alto_consumo
        + 3.2 * cantidad_equipos
        + rng.normal(0, 60, num_clientes)
    )
    consumo_kwh = np.round(base_consumo.clip(0.2, 999.9), 1)

    puntaje_eficiencia = (
        -0.02 * consumo_kwh
        + (calidad_aislamiento == "Muy Alta").astype(int) * 25
        + (calidad_aislamiento == "Alta").astype(int) * 15
        + (calidad_aislamiento == "Media").astype(int) * 5
        + (fuente_calefaccion == "Solar").astype(int) * 18
        + (fuente_agua_caliente == "Solar").astype(int) * 8
        - uso_horario_pico.astype(int) * 6
        - 0.04 * antiguedad_vivienda
        - 0.02 * metros_cuadrados
        - 0.06 * cantidad_equipos
        + rng.normal(0, 5, num_clientes)
    )

    cuantiles = np.quantile(puntaje_eficiencia, [0.20, 0.83])
    categoria = np.where(
        puntaje_eficiencia >= cuantiles[1], "Eficiente",
        np.where(puntaje_eficiencia >= cuantiles[0], "Moderado", "Ineficiente")
    )

    return pd.DataFrame({
        "hogar_id": hogar_id,
        "tipo_inmueble": tipo_inmueble,
        "metros_cuadrados": metros_cuadrados,
        "antiguedad_vivienda": antiguedad_vivienda,
        "zona_fria": zona_fria,
        "calidad_aislamiento": calidad_aislamiento,
        "fuente_calefaccion": fuente_calefaccion,
        "fuente_agua_caliente": fuente_agua_caliente,
        "consumo_kwh": consumo_kwh,
        "uso_horario_pico": uso_horario_pico,
        "horas_alto_consumo": horas_alto_consumo,
        "cantidad_equipos": cantidad_equipos,
        "categoria": categoria,
    })
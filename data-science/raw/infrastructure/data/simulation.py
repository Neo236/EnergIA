"""Generador del dataset sintetico de hogares.

FUENTE DE VERDAD de la generacion del dataset. La notebook Colab es un
consumidor EDA de este output (descarga `database_beta.json` desde la
rama `develop`), no genera nada.

Decisiones de diseno:
- API legacy de NumPy (`np.random.seed`) fijada por compatibilidad con
  el notebook historico del equipo (no es relevante para la notebook
  nueva, que solo consume el JSON publicado).
- Parametros centralizados en `infrastructure.config.Config`.
- `zona_fria` y `uso_horario_pico` se mantienen como string "Si"/"No".
  La notebook hace `.map({"Si": True, "No": False})` al consumir, y el
  pipeline de ML los trata como categoricos
  (ver `application/training.py` CAT_COLS).
- `categoria` se calcula desde `domain.scoring.calcular_iee_y_categoria`
  para garantizar coherencia con las reglas IEE.
- El contrato (columnas, tipos) que este generador produce esta
  validado contra el consumidor (notebook Colab) en
  `tests/unit/test_simulation.py::TestSchemaContractWithNotebook` y
  mediante el target `make verify-notebook-contract`.
"""

import numpy as np
import pandas as pd

from domain.scoring import calcular_iee_y_categoria
from infrastructure.config import Config


def generar_dataset(num_clientes: int = Config.NUM_CLIENTES,
                    seed: int = Config.RANDOM_SEED) -> pd.DataFrame:
    # Reproducibilidad: API legacy de NumPy (identica a data_colab.ipynb)
    np.random.seed(seed)

    hogar_id = ["Hogar_" + str(i).zfill(4) for i in range(1, num_clientes + 1)]

    tipo_inmueble = np.random.choice(
        a=list(Config.TIPO_INMUEBLE),
        size=num_clientes,
        replace=True,
        p=list(Config.TIPO_INMUEBLE_PROBS),
    )

    metros_cuadrados = np.random.randint(
        low=Config.MIN_M2,
        high=Config.MAX_M2 + 1,
        size=num_clientes,
    )

    antiguedad_vivienda = np.random.randint(
        low=Config.MIN_ANTIGUEDAD,
        high=Config.MAX_ANTIGUEDAD + 1,
        size=num_clientes,
    )

    zona_fria = np.random.choice(
        a=["Si", "No"],
        size=num_clientes,
        replace=True,
        p=list(Config.P_ZONA_FRIA),
    )

    calidad_aislamiento = np.random.choice(
        a=list(Config.CALIDAD_AISLAMIENTO),
        size=num_clientes,
        replace=True,
        p=list(Config.CALIDAD_AISLAMIENTO_PROBS),
    )

    fuente_calefaccion = np.random.choice(
        a=list(Config.FUENTE),
        size=num_clientes,
        replace=True,
        p=list(Config.FUENTE_PROBS),
    )

    fuente_agua_caliente = np.random.choice(
        a=list(Config.FUENTE),
        size=num_clientes,
        replace=True,
        p=list(Config.FUENTE_PROBS),
    )

    consumo_kwh = np.round(
        np.random.uniform(
            low=Config.CONSUMO_KWH_INF,
            high=Config.CONSUMO_KWH_SUP,
            size=num_clientes,
        ),
        1,
    )
    consumo_kwh = np.maximum(consumo_kwh, Config.CONSUMO_KWH_INF)

    uso_horario_pico = np.random.choice(
        a=["Si", "No"],
        size=num_clientes,
        replace=True,
        p=list(Config.P_HORARIO_PICO),
    )

    horas_alto_consumo = np.random.randint(
        low=Config.MIN_CANTIDAD_HORAS,
        high=Config.MAX_CANTIDAD_HORAS + 1,
        size=num_clientes,
    )

    cantidad_equipos = np.random.randint(
        low=Config.CANTIDAD_EQUIPOS_INF,
        high=Config.CANTIDAD_EQUIPOS_SUP + 1,
        size=num_clientes,
    )

    df = pd.DataFrame({
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
    })

    assert df.shape == (num_clientes, 12), f"Dimension inesperada: {df.shape}"
    assert df["hogar_id"].is_unique, "hogar_id duplicados"

    df["categoria"] = calcular_iee_y_categoria(df)

    assert df.shape == (num_clientes, 13), f"Dimension con categoria: {df.shape}"
    assert len(df) == len(df["categoria"]), (
        "La cantidad de categorias no coincide con la cantidad de registros."
    )
    assert not df.isnull().any().any(), (
        "El dataset final contiene valores nulos."
    )
    assert df["hogar_id"].is_unique, (
        "Existen valores duplicados en hogar_id."
    )
    assert set(df["categoria"].unique()).issubset(
        {"Eficiente", "Moderado", "Ineficiente"}
    ), f"Categorias invalidas: {df['categoria'].unique()}"

    return df


# Re-exports para compatibilidad con callers que importaban desde aqui.
# Las constantes canonicas viven en infrastructure.config.Config.
TIPO_INMUEBLE = Config.TIPO_INMUEBLE
CALIDAD_AISLAMIENTO = Config.CALIDAD_AISLAMIENTO
FUENTE = Config.FUENTE

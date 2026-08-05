"""Scoring IEE (Indice de Eficiencia Energetica).

Replica literal de la logica del notebook `notebooks/data_colab.ipynb`
(Fase 4: Cortes Fijos + Funciones score_* + Fase 5: Clasificacion Final).

Reglas de corte:
    Eficiente     -> puntaje > 70
    Moderado      -> 50 <= puntaje <= 70
    Ineficiente   -> puntaje < 50
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Cortes fijos (mismos valores que data_colab.ipynb Fase 4)
# ---------------------------------------------------------------------------
BINS_CONSUMO = np.linspace(0.1, 1000, 4)
BINS_HORAS = np.linspace(0, 24, 4)
BINS_EQUIPOS = np.linspace(1, 100, 4)
BINS_M2 = np.linspace(26, 2000, 4)
BINS_ANTIGUEDAD = np.linspace(0, 150, 5)


# ---------------------------------------------------------------------------
# Helpers de coercion (acepta int 0/1, bool o string "Si"/"No")
# ---------------------------------------------------------------------------
def _es_si(x):
    """True si el valor representa "Si" (int 1, bool True, o string "Si")."""
    if isinstance(x, str):
        return x == "Si"
    return bool(x)


# ---------------------------------------------------------------------------
# Dimensiones del IEE
# ---------------------------------------------------------------------------
def score_consumo(df: pd.DataFrame) -> pd.Series:
    """Dimension consumo (0-100). Pico=False suma +20; alto consumo resta."""
    score_kwh = pd.cut(
        df["consumo_kwh"],
        bins=BINS_CONSUMO,
        labels=[60, 40, 20],
        include_lowest=True,
    ).astype(int)

    score_pico = np.where(df["uso_horario_pico"].apply(_es_si), 0, 20)

    score_horas = pd.cut(
        df["horas_alto_consumo"],
        bins=BINS_HORAS,
        labels=[20, 13, 7],
        include_lowest=True,
    ).astype(int)

    return score_kwh + score_pico + score_horas


def score_eficiencia(df: pd.DataFrame) -> pd.Series:
    """Dimension eficiencia energetica del hogar (0-100)."""
    score_aislamiento = df["calidad_aislamiento"].map({
        "Muy Alta": 40,
        "Alta": 32,
        "Media": 24,
        "Baja": 16,
        "Muy Baja": 8,
    }).fillna(0)

    score_calefaccion = df["fuente_calefaccion"].map({
        "Solar": 30,
        "Otros": 15,
        "Electricidad": 5,
    }).fillna(0)

    score_agua = df["fuente_agua_caliente"].map({
        "Solar": 30,
        "Otros": 15,
        "Electricidad": 5,
    }).fillna(0)

    return score_aislamiento + score_calefaccion + score_agua


def score_equipamiento(df: pd.DataFrame) -> pd.Series:
    """Dimension equipamiento (0-100). Solo depende de cantidad_equipos."""
    return pd.cut(
        df["cantidad_equipos"],
        bins=BINS_EQUIPOS,
        labels=[100, 67, 33],
        include_lowest=True,
    ).astype(int)


def score_contexto(df: pd.DataFrame) -> pd.Series:
    """Dimension contexto del hogar (0-100)."""
    score_tipo = df["tipo_inmueble"].map({
        "Casa": 30,
        "Departamento": 20,
        "Comercio": 10,
        "Pyme": 5,
    }).fillna(0)

    score_m2 = pd.cut(
        df["metros_cuadrados"],
        bins=BINS_M2,
        labels=[30, 20, 10],
        include_lowest=True,
    ).astype(int)

    score_antiguedad = pd.cut(
        df["antiguedad_vivienda"],
        bins=BINS_ANTIGUEDAD,
        labels=[20, 15, 10, 5],
        include_lowest=True,
    ).astype(int)

    score_zona = np.where(df["zona_fria"].apply(_es_si), 20, 0)

    return score_tipo + score_m2 + score_antiguedad + score_zona


# ---------------------------------------------------------------------------
# IEE y categoria final
# ---------------------------------------------------------------------------
PESOS = {
    "consumo": 0.40,
    "eficiencia": 0.30,
    "contexto": 0.20,
    "equipamiento": 0.10,
}


def calcular_iee(df: pd.DataFrame) -> pd.Series:
    """Calcula el IEE combinando las 4 dimensiones con los pesos del colab."""
    return (
        score_consumo(df) * PESOS["consumo"]
        + score_eficiencia(df) * PESOS["eficiencia"]
        + score_contexto(df) * PESOS["contexto"]
        + score_equipamiento(df) * PESOS["equipamiento"]
    )


def obtener_categoria(puntaje: pd.Series) -> pd.Series:
    """Asignacion de categoria final segun los cortes del colab."""
    condiciones = [
        puntaje > 70,
        (puntaje >= 50) & (puntaje <= 70),
        puntaje < 50,
    ]
    categorias = ["Eficiente", "Moderado", "Ineficiente"]
    return pd.Series(
        np.select(condiciones, categorias, default="Sin clasificar"),
        index=puntaje.index,
    )


def calcular_iee_y_categoria(df: pd.DataFrame) -> pd.Series:
    """Wrapper: devuelve la columna `categoria` para un DataFrame de hogares."""
    return obtener_categoria(calcular_iee(df))

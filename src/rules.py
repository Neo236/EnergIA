import numpy as np
import pandas as pd


def _score_consumo(df: pd.DataFrame) -> pd.Series:
    c = df["consumo_total_kwh"]
    score = np.where(c <= 150, 50,
             np.where(c <= 250, 32,
              np.where(c <= 350, 18,
               np.where(c <= 500, 8, 0))))
    return pd.Series(score, index=df.index)


def _score_vivienda(df: pd.DataFrame) -> pd.Series:
    score = np.where(df["tipo_vivienda"] == "departamento", 13,
             np.where(df["tipo_vivienda"] == "casa", 10, 6))
    return pd.Series(score, index=df.index)


def _score_renovable(df: pd.DataFrame) -> pd.Series:
    score = np.where(df["energia_renovable"] == "si", 15, 3)
    return pd.Series(score, index=df.index)


def _score_eficiencia(df: pd.DataFrame) -> pd.Series:
    e = df["eficiencia_promedio"]
    score = np.where(e == "A_plus", 22,
             np.where(e == "A", 14,
              np.where(e == "B", 6, 2)))
    return pd.Series(score, index=df.index)


def _score_equipamiento(df: pd.DataFrame) -> pd.Series:
    q = df["cant_electrodomesticos"]
    score = np.where(q <= 4, 14,
             np.where(q <= 8, 8,
              np.where(q <= 12, 3, 0)))
    return pd.Series(score, index=df.index)


def _score_calefaccion(df: pd.DataFrame) -> pd.Series:
    h = df["calefaccion"]
    score = np.where(h == "ninguna", 12,
             np.where(h == "gas", 9, 3))
    return pd.Series(score, index=df.index)


def _score_superficie(df: pd.DataFrame) -> pd.Series:
    s = df["superficie_m2"]
    score = np.where(s <= 50, 8,
             np.where(s <= 100, 5,
              np.where(s <= 150, 2, 0)))
    return pd.Series(score, index=df.index)


def _calcular_puntaje(df: pd.DataFrame) -> pd.Series:
    return (
        _score_consumo(df)
        + _score_vivienda(df)
        + _score_renovable(df)
        + _score_eficiencia(df)
        + _score_equipamiento(df)
        + _score_calefaccion(df)
        + _score_superficie(df)
    )


def asignar_categoria(df: pd.DataFrame, umbral_eficiente: int, umbral_moderado: int) -> pd.DataFrame:
    df = df.copy()
    df["puntaje"] = _calcular_puntaje(df)
    categoria = np.where(df["puntaje"] >= umbral_eficiente, "eficiente",
                 np.where(df["puntaje"] >= umbral_moderado, "moderado", "ineficiente"))
    df["categoria"] = categoria
    return df

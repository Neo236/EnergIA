import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Pipeline / artefactos
    NUM_CLIENTES = int(os.getenv("NUM_CLIENTES", "2000"))
    RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))
    OUTPUT_JSON_PATH = os.getenv("OUTPUT_JSON_PATH", "data/database_beta.json")
    OUTPUT_MODEL_PATH = os.getenv("OUTPUT_MODEL_PATH", "data/modelo_eficiencia_v1.joblib")
    OUTPUT_METRICAS_PATH = os.getenv("OUTPUT_METRICAS_PATH", "data/metricas_v1.joblib")

    # Tarifa de referencia (alineada con data_sources.md y semana-1.md)
    TARIFA_KWH = float(os.getenv("TARIFA_KWH", "0.75"))

    # Distribuciones del dataset (replican data_colab.ipynb Fase 1)
    TIPO_INMUEBLE = ("Casa", "Departamento", "Comercio", "Pyme")
    TIPO_INMUEBLE_PROBS = (0.35, 0.30, 0.20, 0.15)

    CALIDAD_AISLAMIENTO = ("Muy Alta", "Alta", "Media", "Baja", "Muy Baja")
    CALIDAD_AISLAMIENTO_PROBS = (0.12, 0.23, 0.35, 0.18, 0.12)

    FUENTE = ("Electricidad", "Solar", "Otros")
    FUENTE_PROBS = (0.45, 0.35, 0.20)

    P_ZONA_FRIA = (0.4, 0.6)        # ("Si", "No")
    P_HORARIO_PICO = (0.6, 0.4)     # ("Si", "No")

    # Rangos numericos del dataset
    MIN_M2 = 26
    MAX_M2 = 2000
    MIN_ANTIGUEDAD = 0
    MAX_ANTIGUEDAD = 150
    CONSUMO_KWH_INF = 0.1
    CONSUMO_KWH_SUP = 1000
    MIN_CANTIDAD_HORAS = 0
    MAX_CANTIDAD_HORAS = 24
    CANTIDAD_EQUIPOS_INF = 1
    CANTIDAD_EQUIPOS_SUP = 100

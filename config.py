import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    NUM_CLIENTES = int(os.getenv("NUM_CLIENTES", "2000"))
    RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))
    OUTPUT_JSON_PATH = os.getenv("OUTPUT_JSON_PATH", "data/database_beta.json")
    OUTPUT_MODEL_PATH = os.getenv("OUTPUT_MODEL_PATH", "data/modelo_eficiencia_v1.joblib")
    OUTPUT_METRICAS_PATH = os.getenv("OUTPUT_METRICAS_PATH", "data/metricas_v1.joblib")
    UMBRAL_EFICIENTE = int(os.getenv("UMBRAL_EFICIENTE", "80"))
    UMBRAL_MODERADO = int(os.getenv("UMBRAL_MODERADO", "50"))

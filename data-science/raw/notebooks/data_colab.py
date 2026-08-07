# Librerias
import pandas as pd
import numpy as np

# Reproducibilidad
np.random.seed(42)

# Parámetros iniciales
num_hogares = 2000
min_m2 = 26
max_m2 = 2000
min_antiguedad = 0
max_antiguedad = 150
consumo_kwh_inf = 1
consumo_kwh_sup = 1000
min_cantidad_horas = 0
max_cantidad_horas = 24
cantidad_equipos_inf = 1
cantidad_equipos_sup = 100

# Probabilidades
p_tipo_inmueble = [0.35, 0.30, 0.20, 0.15]
p_calidad_aislamiento = [0.12, 0.23, 0.35, 0.18, 0.12]
p_fuente_calefaccion = [0.45, 0.35, 0.20]
p_fuente_agua = [0.45, 0.35, 0.20]
p_zona_fria = [0.4, 0.6]
p_horario_pico = [0.6, 0.4]

# Variable hogar_id
hogar_id = ["Hogar_" + str(i).zfill(4) for i in range(1, num_hogares + 1)]

# Variable tipo_inmueble
tipo_inmueble = np.random.choice(
    a=['Casa', 'Departamento', 'Comercio', 'Pyme'],
    size=num_hogares,
    replace=True,
    p=p_tipo_inmueble
)

# Variable metros_cuadrados
metros_cuadrados = np.random.randint(
    low=min_m2,
    high=max_m2 + 1,
    size=num_hogares
)

# Variable antiguedad_vivienda
antiguedad_vivienda = np.random.randint(
    low=min_antiguedad,
    high=max_antiguedad +1,
    size=num_hogares
)

# Variable zona_fria
zona_fria = np.random.choice(
    a=['Si', 'No'],
    size=num_hogares,
    replace=True,
    p=p_zona_fria)

# Variable calidad_aislamiento
calidad_aislamiento = np.random.choice(
    a=['Muy Baja', 'Baja', 'Media', 'Alta', 'Muy Alta'],
    size=num_hogares,
    replace=True,
    p=p_calidad_aislamiento)

# Variable fuente_calefaccion
fuente_calefaccion = np.random.choice(
    a=['Electricidad', 'Solar', 'Otros'],
    size=num_hogares,
    replace=True,
    p=p_fuente_calefaccion)

# Variable fuente_agua
fuente_agua_caliente = np.random.choice(
    a=['Electricidad', 'Solar', 'Otros'],
    size=num_hogares,
    replace=True,
    p=p_fuente_agua)

# Creación de la tabla Hogar

df_hogar = pd.DataFrame({
    'hogar_id': hogar_id,
    'tipo_inmueble': tipo_inmueble,
    'metros_cuadrados': metros_cuadrados,
    'antiguedad_vivienda': antiguedad_vivienda,
    'zona_fria': zona_fria,
    'calidad_aislamiento': calidad_aislamiento,
    'fuente_calefaccion': fuente_calefaccion,
    'fuente_agua_caliente': fuente_agua_caliente,
})

df_hogar.head()

# Variable consumo_id
consumo_id = [
    "Consumo_" + str(i).zfill(4)
    for i in range(1, num_hogares + 1)]

# Variable consumo_kwh
consumo_kwh = np.round(
    np.random.uniform(
        low=consumo_kwh_inf,
        high=consumo_kwh_sup,
        size=num_hogares
    ),
    1
)

# Protección adicional según el mínimo contractual
consumo_kwh = np.maximum(
    consumo_kwh,
    consumo_kwh_inf
)

# Variable uso_horario_pico
uso_horario_pico = np.random.choice(
    a=['Si', 'No'],
    size=num_hogares,
    replace=True,
    p=p_horario_pico
)

# Variable horas_alto_consumo
horas_alto_consumo = np.random.randint(
    low=min_cantidad_horas,
    high=max_cantidad_horas +1,
    size=num_hogares
)

# Variable cantidad_equipos
cantidad_equipos = np.random.randint(
    low=cantidad_equipos_inf,
    high=cantidad_equipos_sup +1,
    size=num_hogares)


# Creación de la tabla Consumo

df_consumo = pd.DataFrame({
    'consumo_id': consumo_id,
    'hogar_id': df_hogar['hogar_id'],
    'consumo_kwh': consumo_kwh,
    'uso_horario_pico': uso_horario_pico,
    'horas_alto_consumo': horas_alto_consumo,
    'cantidad_equipos': cantidad_equipos
})

df_consumo.head()

# Base para clasificación
base_clasificacion = pd.merge(df_hogar, df_consumo, on='hogar_id', how='inner', validate='one_to_one')
base_clasificacion.head()

# Consumo eléctrico: 3 intervalos
bins_consumo = np.linspace(
    consumo_kwh_inf,
    consumo_kwh_sup,
    4
)

# Horas de alto consumo: 3 intervalos
bins_horas = np.linspace(
    min_cantidad_horas,
    max_cantidad_horas,
    4
)

# Cantidad de equipos: 3 intervalos
bins_equipos = np.linspace(
    cantidad_equipos_inf,
    cantidad_equipos_sup,
    4
)

# Metros cuadrados: 3 intervalos
bins_m2 = np.linspace(
    min_m2,
    max_m2,
    4
)

# Antigüedad de la vivienda: 4 intervalos
bins_antiguedad = np.linspace(
    min_antiguedad,
    max_antiguedad,
    5
)

# Dimensión consumo
# consumo_kwh:           60
# uso_horario_pico:      20
# horas_alto_consumo:    20
# Total:                100

def score_consumo(df):

    score_kwh = pd.cut(
        df["consumo_kwh"],
        bins=bins_consumo,
        labels=[60, 40, 20],
        include_lowest=True
    ).astype(int)

    score_pico = np.where(df["uso_horario_pico"] == "Si", 0, 20)

    score_horas = pd.cut(
        df["horas_alto_consumo"],
        bins=bins_horas,
        labels=[20, 13, 7],
        include_lowest=True
    ).astype(int)

    return score_kwh + score_pico + score_horas

# Dimensión eficiencia
# Repartición: 40, 30, 30 = 100
# calidad_aislamiento:      40
# fuente_calefaccion:       30
# fuente_agua_caliente:     30
# Total:                   100

def score_eficiencia(df):
  score_aislamiento = df['calidad_aislamiento'].map({
      'Muy Alta': 40,
      'Alta': 32,
      'Media': 24,
      'Baja': 16,
      'Muy Baja': 8
  }).fillna(0)

  score_calefaccion = df['fuente_calefaccion'].map({
      'Solar': 30,
      'Otros': 15,
      'Electricidad': 5
  }).fillna(0)

  score_agua = df['fuente_agua_caliente'].map({
      'Solar': 30,
      'Otros': 15,
      'Electricidad': 5
  }).fillna(0)

  return score_aislamiento + score_calefaccion + score_agua

# Dimensión equipamiento

def score_equipamiento(df):

    score_equipos = pd.cut(
        df["cantidad_equipos"],
        bins=bins_equipos,
        labels=[100, 67, 33],
        include_lowest=True
    ).astype(int)

    return score_equipos

# Dimensión contexto
# tipo_inmueble:          30
# metros_cuadrados:       30
# antiguedad_vivienda:    20
# zona_fria:              20

def score_contexto(df):

  score_tipo = df['tipo_inmueble'].map({
        'Casa': 30,
        'Departamento': 20,
        'Comercio': 10,
        'Pyme': 5,
    }).fillna(0)

  score_m2 = pd.cut(
        df["metros_cuadrados"],
        bins=bins_m2,
        labels=[30, 20, 10],
        include_lowest=True
    ).astype(int)

  score_antiguedad = pd.cut(
        df["antiguedad_vivienda"],
        bins=bins_antiguedad,
        labels=[20, 15, 10, 5],
        include_lowest=True
    ).astype(int)

  score_zona = np.where(df["zona_fria"] == "No", 20, 0)

  return score_tipo + score_m2 + score_antiguedad + score_zona

puntaje_consumo = score_consumo(base_clasificacion) * 0.4
puntaje_eficiencia = score_eficiencia(base_clasificacion) * 0.3
puntaje_contexto = score_contexto(base_clasificacion) * 0.2
puntaje_equipamiento = score_equipamiento(base_clasificacion) * 0.1

puntaje = (
  puntaje_consumo +
  puntaje_eficiencia +
  puntaje_contexto +
  puntaje_equipamiento
)

def obtener_categoria(puntaje):
    condiciones = [
        puntaje > 70,
        (puntaje >= 50) & (puntaje <= 70),
        puntaje < 50
    ]

    categorias = [
        'Eficiente',
        'Moderado',
        'Ineficiente'
    ]

    return np.select(
        condiciones,
        categorias,
        default='Sin clasificar'
    )

categoria = obtener_categoria(puntaje)

# Creación de la tabla Database final

df_final = (
    df_hogar
    .merge(df_consumo, on="hogar_id", how="inner", validate="one_to_one").drop(columns=['consumo_id'])
)

assert len(df_final) == len(categoria), (
    "La cantidad de categorías no coincide con "
    "la cantidad de registros."
)

df_final['categoria'] = categoria

assert df_final.shape == (num_hogares, 13), (
    f"Dimensión inesperada: {df_final.shape}"
)

assert not df_final.isnull().any().any(), (
    "El dataset final contiene valores nulos."
)

assert df_final["hogar_id"].is_unique, (
    "Existen valores duplicados en hogar_id."
)

assert df_final["categoria"].isin([
    "Eficiente",
    "Moderado",
    "Ineficiente"
]).all(), (
    "Existen categorías inválidas."
)

print(f"Dimensión del dataset final: {df_final.shape}")
df_final.head()

# Exportación del Dataset

csv_output = "energy_consumption.csv"
json_output = "energy_consumption.json"

df_final.to_csv(
    csv_output,
    index=False,
    encoding="utf-8",
)

df_final.to_json(
    json_output,
    orient="records",
    force_ascii=False,
    indent=4,
)

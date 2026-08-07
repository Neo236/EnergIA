"""Schemas Pydantic para la API de analisis energetico.

Obligatorias (6) - datos que el usuario tiene a mano o decide conscientemente:
    - consumo_kwh: lo que ve en su factura.
    - tipo_inmueble: tipo de vivienda (Casa, Depto, Comercio, Pyme).
    - uso_horario_pico: si su consumo principal cae en horario punta (18-23hs).
    - fuente_calefaccion: como calefacciona el hogar (Electricidad | Solar | Otros).
    - fuente_agua_caliente: fuente del agua caliente.
    - zona_fria: vive en una zona climatica fria. Marcada como obligatoria
      por consistencia con el resto de las fuentes energeticas, aunque el
      EDA muestra que aporta poca varianza al score final (ver nota).

Opcionales (5) - datos que el usuario suele no conocer con precision:
    - metros_cuadrados: superficie aproximada del inmueble.
    - antiguedad_vivienda: anos estimados del inmueble.
    - calidad_aislamiento: Muy Alta | Alta | Media | Baja | Muy Baja.
    - horas_alto_consumo: horas diarias estimadas de uso de alto consumo.
    - cantidad_equipos: cantidad de equipos/electrodomesticos.

Las constantes DEFAULT_* son la FUENTE UNICA de los defaults.
`application.inference.DEFAULTS` las importa y arma el dict de defaults
para el modelo. Si cambias un valor aqui, se propaga automaticamente.
"""

from typing import Literal

from pydantic import BaseModel, Field

TipoInmueble = Literal["Casa", "Departamento", "Comercio", "Pyme"]
CalidadAislamiento = Literal["Muy Alta", "Alta", "Media", "Baja", "Muy Baja"]
FuenteEnergia = Literal["Electricidad", "Solar", "Otros"]
SiNo = Literal["Si", "No"]


# Defaults para campos opcionales. FUENTE UNICA: importado por
# application.inference para construir su dict DEFAULTS.
DEFAULT_METROS_CUADRADOS = 1000.0
DEFAULT_ANTIGUEDAD_VIVIENDA = 50
DEFAULT_CALIDAD_AISLAMIENTO = "Media"
DEFAULT_HORAS_ALTO_CONSUMO = 8
DEFAULT_CANTIDAD_EQUIPOS = 15


class AnalisisRequest(BaseModel):
    """Request del endpoint POST /analisis-energetico.

    6 campos obligatorios (input del usuario). 5 opcionales con defaults
    sensatos (contexto del hogar que el modelo sabe imputar).
    """

    # --- OBLIGATORIOS ---
    consumo_kwh: float = Field(
        ...,
        ge=0,
        description="Consumo mensual en kWh (de la factura).",
    )
    tipo_inmueble: TipoInmueble = Field(
        ...,
        description="Tipo de vivienda: Casa | Departamento | Comercio | Pyme.",
    )
    uso_horario_pico: SiNo = Field(
        ...,
        description="Uso principal en horario punta (18-23hs): Si | No.",
    )
    fuente_calefaccion: FuenteEnergia = Field(
        ...,
        description="Fuente de calefaccion: Electricidad | Solar | Otros.",
    )
    fuente_agua_caliente: FuenteEnergia = Field(
        ...,
        description="Fuente de agua caliente: Electricidad | Solar | Otros.",
    )
    zona_fria: SiNo = Field(
        ...,
        description="Vive en zona climatica fria: Si | No.",
    )

    # --- OPCIONALES (con default) ---
    metros_cuadrados: float = Field(
        default=DEFAULT_METROS_CUADRADOS,
        ge=0,
        description="Superficie del inmueble en m^2. Default: 1000.",
    )
    antiguedad_vivienda: int = Field(
        default=DEFAULT_ANTIGUEDAD_VIVIENDA,
        ge=0,
        description="Anos de antiguedad de la vivienda. Default: 50.",
    )
    calidad_aislamiento: CalidadAislamiento = Field(
        default=DEFAULT_CALIDAD_AISLAMIENTO,
        description=(
            "Calidad del aislamiento termico: "
            "Muy Alta | Alta | Media | Baja | Muy Baja. Default: Media."
        ),
    )
    horas_alto_consumo: int = Field(
        default=DEFAULT_HORAS_ALTO_CONSUMO,
        ge=0,
        le=24,
        description="Horas diarias aproximadas de uso de equipos de alto consumo. Default: 8.",
    )
    cantidad_equipos: int = Field(
        default=DEFAULT_CANTIDAD_EQUIPOS,
        ge=0,
        description="Cantidad de electrodomesticos/equipos electricos del hogar. Default: 15.",
    )
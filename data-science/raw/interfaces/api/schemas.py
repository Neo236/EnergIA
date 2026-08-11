"""Schemas Pydantic para la API de analisis energetico.

Obligatorias (4) - datos que el backend exige y el ML necesita para clasificar:
    - consumo_kwh: lo que ve en su factura.
    - tipo_inmueble: tipo de vivienda (Casa, Depto, Comercio, Pyme).
    - horas_alto_consumo: horas diarias estimadas de uso de alto consumo.
    - cantidad_equipos: cantidad de equipos/electrodomesticos.

Opcionales con default (7) - el backend los trata como opcionales
(`DatosRegistroConsumo` no los marca @NotNull) y usa Jackson
`@JsonInclude(NON_NULL)` para omitir nulls del JSON. Por eso el ML debe
saber imputar defaults consistentes con el dataset de entrenamiento:
    - uso_horario_pico: True si su consumo principal cae en horario punta (18-23hs).
    - zona_fria: True si vive en una zona climatica fria. Marcada como
      opcional por consistencia con el resto de las fuentes energeticas;
      el EDA muestra que aporta poca varianza al score final (ver nota).
    - fuente_calefaccion: como calefacciona el hogar (Electricidad | Solar | Otros).
    - fuente_agua_caliente: fuente del agua caliente.
    - metros_cuadrados: superficie aproximada del inmueble.
    - antiguedad_vivienda: anos estimados del inmueble.
    - calidad_aislamiento: Muy Alta | Alta | Media | Baja | Muy Baja.

Las constantes DEFAULT_* son la FUENTE UNICA de los defaults.
`application.inference.DEFAULTS` las importa y arma el dict de defaults
para el modelo. Si cambias un valor aqui, se propaga automaticamente.
"""

from typing import Literal

from pydantic import BaseModel, Field

TipoInmueble = Literal["Casa", "Departamento", "Comercio", "Pyme"]
CalidadAislamiento = Literal["Muy Alta", "Alta", "Media", "Baja", "Muy Baja"]
FuenteEnergia = Literal["Electricidad", "Solar", "Otros"]


# Defaults para campos opcionales. FUENTE UNICA: importado por
# application.inference para construir su dict DEFAULTS.
DEFAULT_METROS_CUADRADOS = 1000.0
DEFAULT_ANTIGUEDAD_VIVIENDA = 50
DEFAULT_CALIDAD_AISLAMIENTO = "Media"
DEFAULT_HORAS_ALTO_CONSUMO = 8
DEFAULT_CANTIDAD_EQUIPOS = 15
DEFAULT_USO_HORARIO_PICO = False
DEFAULT_ZONA_FRIA = False
DEFAULT_FUENTE_CALEFACCION = "Electricidad"
DEFAULT_FUENTE_AGUA_CALIENTE = "Electricidad"


class AnalisisRequest(BaseModel):
    """Request del endpoint POST /analisis-energetico.

    4 campos obligatorios (input del usuario, alineados con backend @NotNull).
    7 opcionales con defaults sensatos (el backend los marca opcionales;
    cuando el front no los llena, Jackson con NON_NULL los omite y el ML
    imputa el default correspondiente).
    """

    # --- OBLIGATORIOS (alineados con backend @NotNull) ---
    consumo_kwh: float = Field(
        ...,
        ge=1,                    # alineado con backend @DecimalMin("1.0")
        le=1000,                 # alineado con backend @DecimalMax("1000.0")
        description="Consumo mensual en kWh (de la factura).",
    )
    tipo_inmueble: TipoInmueble = Field(
        ...,
        description="Tipo de vivienda: Casa | Departamento | Comercio | Pyme.",
    )
    horas_alto_consumo: int = Field(
        ...,
        ge=0,
        le=24,
        description="Horas diarias aproximadas de uso de equipos de alto consumo.",
    )
    cantidad_equipos: int = Field(
        ...,
        ge=1,
        le=100,
        description="Cantidad de electrodomesticos/equipos electricos del hogar.",
    )

    # --- OPCIONALES con default (alineados con backend, sin @NotNull) ---
    uso_horario_pico: bool = Field(
        default=DEFAULT_USO_HORARIO_PICO,
        description=(
            "True si el consumo principal cae en horario punta (18-23hs). "
            f"Default: {DEFAULT_USO_HORARIO_PICO}."
        ),
    )
    zona_fria: bool = Field(
        default=DEFAULT_ZONA_FRIA,
        description=(
            "True si vive en una zona climatica fria. "
            f"Default: {DEFAULT_ZONA_FRIA}."
        ),
    )
    fuente_calefaccion: FuenteEnergia = Field(
        default=DEFAULT_FUENTE_CALEFACCION,
        description=(
            "Fuente de calefaccion: Electricidad | Solar | Otros. "
            f"Default: {DEFAULT_FUENTE_CALEFACCION}."
        ),
    )
    fuente_agua_caliente: FuenteEnergia = Field(
        default=DEFAULT_FUENTE_AGUA_CALIENTE,
        description=(
            "Fuente de agua caliente: Electricidad | Solar | Otros. "
            f"Default: {DEFAULT_FUENTE_AGUA_CALIENTE}."
        ),
    )
    metros_cuadrados: float = Field(
        default=DEFAULT_METROS_CUADRADOS,
        ge=26,
        le=2000,
        description="Superficie del inmueble en m^2. Default: 1000.",
    )
    antiguedad_vivienda: int = Field(
        default=DEFAULT_ANTIGUEDAD_VIVIENDA,
        ge=0,
        le=150,
        description="Anos de antiguedad de la vivienda. Default: 50.",
    )
    calidad_aislamiento: CalidadAislamiento = Field(
        default=DEFAULT_CALIDAD_AISLAMIENTO,
        description=(
            "Calidad del aislamiento termico: "
            "Muy Alta | Alta | Media | Baja | Muy Baja. Default: Media."
        ),
    )
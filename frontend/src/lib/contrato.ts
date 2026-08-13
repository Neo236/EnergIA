/* ============================================================
   Contrato V2 — FUENTE ÚNICA del front.

   Espejo de DatosRegistroConsumo (entrada) y DatosRegistroAnalisis
   (salida) del back-end Spring Boot. Si el contrato del back cambia,
   se toca solo este archivo.

   El front habla con la API de Java, nunca con el servicio de ML.
   Las diferencias entre ambos esquemas las resuelve el back-end.

   Novedad respecto de V1.2: la API ahora persiste cada análisis y lo
   devuelve con `id` (UUID v7) y `fecha`. Eso es lo que hace que un
   resultado tenga URL propia y sobreviva a una recarga.
   ============================================================ */

export const ENDPOINT = '/api/v1/analisis-energetico'

/* Tarifa usada para mostrar la referencia por kWh y la proyección anual.

   ADVERTENCIA: el back-end NO devuelve la tarifa. `costo_estimado_mensual`
   lo calcula el modelo de ML con su propio criterio, que no conocemos. Esta
   constante es una referencia del front y puede no explicar exactamente el
   costo mostrado a su lado. Decisión tomada a conciencia para no bloquear
   el front en un cambio de back-end; si algún día la API expone el consumo
   o la tarifa, hay que derivarla de ahí y borrar esta constante. */
export const TARIFA_KWH = 0.75

export const TIPOS_INMUEBLE = ['Casa', 'Departamento', 'Comercio', 'Pyme'] as const
export const CALIDADES_AISLAMIENTO = ['Muy Alta', 'Alta', 'Media', 'Baja', 'Muy Baja'] as const
export const FUENTES_ENERGIA = ['Solar', 'Electricidad', 'Otros'] as const

export type TipoInmueble = (typeof TIPOS_INMUEBLE)[number]
export type CalidadAislamiento = (typeof CALIDADES_AISLAMIENTO)[number]
export type FuenteEnergia = (typeof FUENTES_ENERGIA)[number]

export type Categoria = 'Eficiente' | 'Moderado' | 'Ineficiente'

/** Lo que se carga en el formulario. Los opcionales pueden faltar: el back aplica su defecto. */
export interface Solicitud {
  consumo_kwh: number
  tipo_inmueble: TipoInmueble
  cantidad_equipos: number
  horas_alto_consumo: number

  metros_cuadrados?: number
  antiguedad_vivienda?: number
  zona_fria?: boolean
  calidad_aislamiento?: CalidadAislamiento
  fuente_calefaccion?: FuenteEnergia
  fuente_agua_caliente?: FuenteEnergia
  uso_horario_pico?: boolean
}

/** Respuesta 200 de POST y de GET /{id}. */
export interface Analisis {
  /** UUID v7 asignado al persistir. Es la clave de la URL del resultado. */
  id: string
  /** ISO-8601 sin zona, tal como lo serializa LocalDateTime. */
  fecha: string
  categoria: Categoria
  probabilidad: number
  costo_estimado_mensual: number
  recomendaciones: string[]
}

/* ---------- errores ---------- */

/** Espejo de DatosErrorCampo. */
export interface DetalleError {
  campo: string
  mensaje: string
}

/** Espejo de DatosErrorRespuesta. */
export interface RespuestaError {
  timestamp?: string
  status: number
  error?: string
  mensaje: string
  detalles?: DetalleError[]
}

export class ErrorApi extends Error {
  readonly respuesta: RespuestaError
  constructor(respuesta: RespuestaError) {
    super(respuesta.mensaje)
    this.name = 'ErrorApi'
    this.respuesta = respuesta
  }
}

/* ---------- descripción de los campos ----------

   Las etiquetas y los textos de ayuda son los del diseño, palabra por
   palabra. Los campos sin `ayuda` no la llevan en el diseño tampoco:
   los tres desplegables comunican su defecto dentro del propio valor. */

type Base = {
  nombre: keyof Solicitud
  etiqueta: string
  requerido: boolean
  ayuda?: string
}

export type Campo =
  | (Base & { tipo: 'numero'; min: number; max: number; unidad?: string; defecto?: number; decimal?: boolean })
  | (Base & { tipo: 'contador'; min: number; max: number; defecto?: number })
  | (Base & { tipo: 'deslizador'; min: number; max: number; unidad: string })
  | (Base & { tipo: 'opciones'; valores: readonly string[]; etiquetasCortas?: Record<string, string> })
  | (Base & { tipo: 'seleccion'; valores: readonly string[]; defecto: string })
  | (Base & { tipo: 'booleano'; defecto: boolean })

/** Los 4 obligatorios, en el orden en que se muestran. */
export const CAMPOS_REQUERIDOS: Campo[] = [
  {
    nombre: 'consumo_kwh', etiqueta: 'Consumo mensual', tipo: 'numero', requerido: true,
    min: 1, max: 1000, unidad: 'kWh', decimal: true,
    ayuda: 'Figura en tu factura de luz · entre 1 y 1000 kWh',
  },
  {
    nombre: 'tipo_inmueble', etiqueta: 'Tipo de inmueble', tipo: 'opciones', requerido: true,
    valores: TIPOS_INMUEBLE,
    // El chip dice «Depto.» por espacio; al back viaja «Departamento».
    etiquetasCortas: { Departamento: 'Depto.' },
  },
  {
    nombre: 'cantidad_equipos', etiqueta: 'Cantidad de equipos', tipo: 'contador', requerido: true,
    min: 1, max: 100, defecto: 10,
    ayuda: 'Electrodomésticos enchufados · 1 a 100',
  },
  {
    nombre: 'horas_alto_consumo', etiqueta: 'Horas de alto consumo por día', tipo: 'deslizador', requerido: true,
    min: 0, max: 24, unidad: 'h',
  },
]

/** Los 7 opcionales. El `defecto` es el valor que aplica el back si no se envían. */
export const CAMPOS_OPCIONALES: Campo[] = [
  {
    nombre: 'metros_cuadrados', etiqueta: 'Metros cuadrados', tipo: 'numero', requerido: false,
    min: 26, max: 2000, unidad: 'm²', defecto: 1000,
    ayuda: 'Superficie habitable · entre 26 y 2000 · por defecto 1000',
  },
  {
    nombre: 'antiguedad_vivienda', etiqueta: 'Antigüedad de la vivienda', tipo: 'numero', requerido: false,
    min: 0, max: 150, unidad: 'años', defecto: 50,
    ayuda: 'Años desde la construcción · entre 0 y 150 · por defecto 50',
  },
  {
    nombre: 'zona_fria', etiqueta: 'Zona fría', tipo: 'booleano', requerido: false, defecto: false,
    ayuda: 'Zona climática considerada fría · por defecto No',
  },
  {
    nombre: 'calidad_aislamiento', etiqueta: 'Calidad del aislamiento', tipo: 'seleccion', requerido: false,
    valores: CALIDADES_AISLAMIENTO, defecto: 'Media',
  },
  {
    nombre: 'fuente_calefaccion', etiqueta: 'Fuente de calefacción', tipo: 'seleccion', requerido: false,
    valores: FUENTES_ENERGIA, defecto: 'Electricidad',
  },
  {
    nombre: 'fuente_agua_caliente', etiqueta: 'Fuente de agua caliente', tipo: 'seleccion', requerido: false,
    valores: FUENTES_ENERGIA, defecto: 'Electricidad',
  },
  {
    nombre: 'uso_horario_pico', etiqueta: 'Uso en horario pico', tipo: 'booleano', requerido: false, defecto: false,
    ayuda: 'Franja de 18 a 23 h · por defecto No',
  },
]

export const CAMPOS: Campo[] = [...CAMPOS_REQUERIDOS, ...CAMPOS_OPCIONALES]

/** Valores con los que arranca el formulario, iguales a los del diseño. */
export const VALORES_INICIALES = {
  consumo_kwh: '420',
  tipo_inmueble: 'Casa' as TipoInmueble,
  cantidad_equipos: 10,
  horas_alto_consumo: 12,
} as const

/** Completa una solicitud parcial con los defectos que aplicaría el back. */
export function conDefectos(solicitud: Solicitud): Record<string, unknown> {
  const completo: Record<string, unknown> = { ...solicitud }
  for (const campo of CAMPOS_OPCIONALES) {
    if (completo[campo.nombre] === undefined && 'defecto' in campo) {
      completo[campo.nombre] = campo.defecto
    }
  }
  return completo
}

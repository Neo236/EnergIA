/* ============================================================
   Contrato V1.2 — FUENTE ÚNICA del front.
   Espejo de DatosRegistroConsumo del back-end (Spring Boot).
   Si el contrato cambia, se toca solo este archivo.

   Nota: el front habla con la API de Java, no con el servicio de ML.
   El ML tiene su propio esquema y las diferencias entre ambos las
   resuelve el back-end.
   ============================================================ */

export const ENDPOINT = '/api/v1/analisis-energetico'
export const TARIFA_KWH = 0.75

export const TIPOS_INMUEBLE = ['Casa', 'Departamento', 'Comercio', 'Pyme'] as const
export const CALIDADES_AISLAMIENTO = ['Muy Alta', 'Alta', 'Media', 'Baja', 'Muy Baja'] as const
export const FUENTES_ENERGIA = ['Solar', 'Electricidad', 'Otros'] as const

export type TipoInmueble = (typeof TIPOS_INMUEBLE)[number]
export type CalidadAislamiento = (typeof CALIDADES_AISLAMIENTO)[number]
export type FuenteEnergia = (typeof FUENTES_ENERGIA)[number]

export type Categoria = 'Eficiente' | 'Moderado' | 'Ineficiente'

/** Lo que el usuario carga. Los opcionales pueden faltar: el back aplica su default. */
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

/** Respuesta 200. La API no devuelve identificador ni fecha (PA-19). */
export interface Analisis {
  categoria: Categoria
  probabilidad: number
  costo_estimado_mensual: number
  recomendaciones: string[]
}

/** Formato uniforme de error del back-end (DatosErrorRespuesta). */
export interface DetalleError {
  campo: string
  mensaje: string
}

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

/* ---------- descripción de los campos, para la interfaz ---------- */

type Base = {
  nombre: keyof Solicitud
  etiqueta: string
  requerido: boolean
  ayuda: string
}

export type Campo =
  | (Base & { tipo: 'numero'; min: number; max: number; unidad?: string; defecto?: number; decimal?: boolean })
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
    etiquetasCortas: { Departamento: 'Depto.' },
    ayuda: 'Valores del contrato: Casa · Departamento · Comercio · Pyme',
  },
  {
    nombre: 'cantidad_equipos', etiqueta: 'Cantidad de equipos', tipo: 'numero', requerido: true,
    min: 1, max: 100, ayuda: 'Entre 1 y 100',
  },
  {
    nombre: 'horas_alto_consumo', etiqueta: 'Horas de alto consumo por día', tipo: 'numero', requerido: true,
    min: 0, max: 24, unidad: 'h', ayuda: 'De 0 a 24 horas',
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
    ayuda: 'Muy Alta · Alta · Media · Baja · Muy Baja',
  },
  {
    nombre: 'fuente_calefaccion', etiqueta: 'Fuente de calefacción', tipo: 'seleccion', requerido: false,
    valores: FUENTES_ENERGIA, defecto: 'Electricidad',
    ayuda: 'Solar · Electricidad · Otros',
  },
  {
    nombre: 'fuente_agua_caliente', etiqueta: 'Fuente de agua caliente', tipo: 'seleccion', requerido: false,
    valores: FUENTES_ENERGIA, defecto: 'Electricidad',
    ayuda: 'Solar · Electricidad · Otros',
  },
  {
    nombre: 'uso_horario_pico', etiqueta: 'Uso en horario pico', tipo: 'booleano', requerido: false, defecto: false,
    ayuda: 'Franja de 18 a 23 h · por defecto No',
  },
]

export const CAMPOS: Campo[] = [...CAMPOS_REQUERIDOS, ...CAMPOS_OPCIONALES]

/** Completa una solicitud parcial con los defaults que aplicaría el back. */
export function conDefectos(solicitud: Solicitud): Record<string, unknown> {
  const completo: Record<string, unknown> = { ...solicitud }
  for (const campo of CAMPOS_OPCIONALES) {
    if (completo[campo.nombre] === undefined) {
      completo[campo.nombre] = 'defecto' in campo ? campo.defecto : undefined
    }
  }
  return completo
}

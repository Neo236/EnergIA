/* ============================================================
   Validación de la entrada del formulario.

   Vive acá y no dentro del componente por dos razones. La primera es que
   se pueda probar: son reglas puras, sin estado ni DOM, y eran la lógica
   sin cubrir más grande del front-end.

   La segunda pesa más. Estos rangos son una COPIA de las restricciones
   del DTO de Java (`DatosRegistroConsumo`), y dos copias de una misma
   regla se separan en silencio: si alguien cambia un límite en el
   back-end, el front sigue aceptando el valor viejo y el usuario se
   entera por un 400 en vez de por un mensaje al lado del campo. Tener los
   rangos en una constante nombrada no impide esa deriva, pero la vuelve
   visible y comparable de un vistazo.
   ============================================================ */

import type {
  CalidadAislamiento, FuenteEnergia, Solicitud, TipoInmueble,
} from './contrato'
import { mensajeDeCampo } from './mensajes'

export type Errores = Partial<Record<keyof Solicitud, string>>

/**
 * Espejo de las restricciones de `DatosRegistroConsumo` en el back-end.
 * Si estas cifras dejan de coincidir con las anotaciones de Java, el
 * front-end está mintiendo sobre lo que la API acepta.
 */
export const RANGOS = {
  consumo_kwh:         { min: 1,  max: 1000 },
  cantidad_equipos:    { min: 1,  max: 100 },
  horas_alto_consumo:  { min: 0,  max: 24 },
  metros_cuadrados:    { min: 26, max: 2000 },
  antiguedad_vivienda: { min: 0,  max: 150 },
} as const

/** Lo que el formulario tiene en pantalla, antes de convertirse en Solicitud. */
export interface EntradaFormulario {
  /** Texto crudo: el usuario puede escribir coma decimal, o nada. */
  consumo: string
  equipos: number
  horas: number
  /** Opcionales: cadena vacía significa «no lo completó». */
  metros: string
  antiguedad: string
  tipo: TipoInmueble
  zonaFria: boolean
  aislamiento: CalidadAislamiento
  calefaccion: FuenteEnergia
  agua: FuenteEnergia
  horarioPico: boolean
}

/** Acepta coma o punto decimal: en español se escribe «420,5». */
function aNumero(texto: string): number {
  return Number(texto.replace(',', '.'))
}

function fueraDeRango(valor: number, rango: { min: number; max: number }): boolean {
  return Number.isNaN(valor) || valor < rango.min || valor > rango.max
}

/**
 * Valida contra los rangos del contrato antes de gastar una llamada a la API.
 *
 * Devuelve la solicitud lista para enviar solo si no hay errores; nunca
 * ambas cosas. Así el llamador no puede enviar por accidente una solicitud
 * construida a partir de datos inválidos.
 */
export function validarEntrada(
  entrada: EntradaFormulario,
): { errores: Errores; solicitud: Solicitud | null } {
  const e: Errores = {}

  const nConsumo = aNumero(entrada.consumo)
  if (entrada.consumo.trim() === '' || fueraDeRango(nConsumo, RANGOS.consumo_kwh)) {
    e.consumo_kwh = mensajeDeCampo('consumo_kwh', 'Valor fuera de rango')
  }
  if (fueraDeRango(entrada.equipos, RANGOS.cantidad_equipos)) {
    e.cantidad_equipos = mensajeDeCampo('cantidad_equipos', 'Valor fuera de rango')
  }
  if (fueraDeRango(entrada.horas, RANGOS.horas_alto_consumo)) {
    e.horas_alto_consumo = mensajeDeCampo('horas_alto_consumo', 'Valor fuera de rango')
  }

  const nMetros = entrada.metros.trim() === '' ? undefined : Number(entrada.metros)
  if (nMetros !== undefined && fueraDeRango(nMetros, RANGOS.metros_cuadrados)) {
    e.metros_cuadrados = mensajeDeCampo('metros_cuadrados', 'Valor fuera de rango')
  }

  const nAntiguedad = entrada.antiguedad.trim() === '' ? undefined : Number(entrada.antiguedad)
  if (nAntiguedad !== undefined && fueraDeRango(nAntiguedad, RANGOS.antiguedad_vivienda)) {
    e.antiguedad_vivienda = mensajeDeCampo('antiguedad_vivienda', 'Valor fuera de rango')
  }

  if (Object.keys(e).length > 0) return { errores: e, solicitud: null }

  /* Los opcionales solo viajan si se completaron: omitirlos es lo que hace
     que el back-end aplique su propio valor por defecto. Mandarlos en null
     no es lo mismo — el DTO los rechazaría. */
  const solicitud: Solicitud = {
    consumo_kwh: nConsumo,
    tipo_inmueble: entrada.tipo,
    cantidad_equipos: entrada.equipos,
    horas_alto_consumo: entrada.horas,
    ...(nMetros !== undefined ? { metros_cuadrados: nMetros } : {}),
    ...(nAntiguedad !== undefined ? { antiguedad_vivienda: nAntiguedad } : {}),
    zona_fria: entrada.zonaFria,
    calidad_aislamiento: entrada.aislamiento,
    fuente_calefaccion: entrada.calefaccion,
    fuente_agua_caliente: entrada.agua,
    uso_horario_pico: entrada.horarioPico,
  }
  return { errores: {}, solicitud }
}

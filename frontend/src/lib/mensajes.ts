/* ============================================================
   Textos de error para el usuario.

   Regla: los mensajes de la API están escritos para quien desarrolla, no
   para quien usa la aplicación. "El servicio de Machine Learning rechazó
   los datos de entrada (HTTP 422)" menciona un servicio interno y un
   código HTTP con los que el usuario no puede hacer nada.

   Por eso:
   - Por campo → texto nuestro, que enuncia el requisito. Si el campo no
     está en el mapa, cae al mensaje de la API: nunca perdemos información
     ni ocultamos una validación que no habíamos previsto.
   - General  → siempre texto nuestro.
   - El mensaje crudo de la API queda disponible como detalle técnico.
   ============================================================ */

import type { Solicitud } from './contrato'

/** Enuncian el requisito, así sirven tanto para "vacío" como "fuera de rango". */
const POR_CAMPO: Partial<Record<keyof Solicitud, string>> = {
  consumo_kwh: 'Ingresá el consumo que figura en tu factura, entre 1 y 1000 kWh.',
  tipo_inmueble: 'Elegí uno de los cuatro tipos.',
  cantidad_equipos: 'Ingresá cuántos equipos tenés, entre 1 y 100.',
  horas_alto_consumo: 'Elegí un valor entre 0 y 24 horas.',
  metros_cuadrados: 'La superficie debe estar entre 26 y 2000 m².',
  antiguedad_vivienda: 'La antigüedad debe estar entre 0 y 150 años.',
  calidad_aislamiento: 'Elegí una de las opciones de la lista.',
  fuente_calefaccion: 'Elegí una de las opciones de la lista.',
  fuente_agua_caliente: 'Elegí una de las opciones de la lista.',
}

export function mensajeDeCampo(campo: string, mensajeApi: string): string {
  return POR_CAMPO[campo as keyof Solicitud] ?? mensajeApi
}

export interface TextoAviso {
  titulo: string
  texto: string
  advertencia: boolean
}

/**
 * status 400 sin `detalles[]` llega cuando el back-end no pudo procesar la
 * solicitud por un motivo que no es de campo — hoy, el rechazo del servicio
 * de ML. No es culpa de lo que cargó el usuario, así que el texto no debe
 * sugerirle que revise sus datos.
 */
export function textoDeAviso(status: number): TextoAviso {
  switch (status) {
    case 0:
      return {
        titulo: 'No pudimos conectarnos',
        texto: 'Revisá tu conexión e intentá de nuevo. Tus datos siguen cargados.',
        advertencia: true,
      }
    case 400:
      return {
        titulo: 'No pudimos procesar el análisis',
        texto: 'El servidor no pudo completar el análisis con estos datos. Probá de nuevo en unos segundos — tus datos siguen cargados.',
        advertencia: false,
      }
    case 503:
      return {
        titulo: 'El análisis no está disponible ahora',
        texto: 'El servicio que calcula tu perfil no responde en este momento. Probá de nuevo en unos minutos — tus datos siguen cargados.',
        advertencia: true,
      }
    default:
      return {
        titulo: 'No pudimos completar el análisis',
        texto: 'El servidor respondió con un error. Podés intentar de nuevo en unos segundos — tus datos siguen cargados.',
        advertencia: false,
      }
  }
}

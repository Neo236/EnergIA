/* ============================================================
   Textos de error para quien usa la aplicación.

   Regla: los mensajes de la API están escritos para quien desarrolla.
   «El servicio de Machine Learning rechazó los datos de entrada (HTTP 422)»
   menciona un servicio interno y un código HTTP con los que el usuario no
   puede hacer nada.

   Por eso:
   - Por campo → texto nuestro, que enuncia el requisito. Si el campo no
     está en el mapa, cae al mensaje de la API: nunca perdemos información
     ni ocultamos una validación que no habíamos previsto.
   - General  → siempre texto nuestro.

   Tratamiento: tuteo, igual que las 33 pantallas del diseño («Completa
   cuatro datos obligatorios», «Descubre cuánto puedes ahorrar»). El
   frontend anterior usaba voseo y quedaba desalineado.
   ============================================================ */

import type { Solicitud } from './contrato'

/** Enuncian el requisito, así sirven tanto para «vacío» como para «fuera de rango». */
const POR_CAMPO: Partial<Record<keyof Solicitud, string>> = {
  consumo_kwh: 'Ingresa el consumo que figura en tu factura, entre 1 y 1000 kWh.',
  tipo_inmueble: 'Elige uno de los cuatro tipos.',
  cantidad_equipos: 'Ingresa cuántos equipos tienes, entre 1 y 100.',
  horas_alto_consumo: 'Elige un valor entre 0 y 24 horas.',
  metros_cuadrados: 'La superficie debe estar entre 26 y 2000 m².',
  antiguedad_vivienda: 'La antigüedad debe estar entre 0 y 150 años.',
  calidad_aislamiento: 'Elige una de las opciones de la lista.',
  fuente_calefaccion: 'Elige una de las opciones de la lista.',
  fuente_agua_caliente: 'Elige una de las opciones de la lista.',
}

export function mensajeDeCampo(campo: string, mensajeApi: string): string {
  return POR_CAMPO[campo as keyof Solicitud] ?? mensajeApi
}

export interface TextoAviso {
  titulo: string
  texto: string
  /** true = tono ámbar (algo pasajero); false = tono rojo (algo falló). */
  advertencia: boolean
}

/**
 * Aviso que encabeza el formulario cuando el envío no prosperó.
 *
 * Un 400 sin `detalles[]` llega cuando el back-end no pudo procesar la
 * solicitud por un motivo que no es de campo — hoy, el rechazo del servicio
 * de ML. No es culpa de lo que cargó el usuario, así que el texto no debe
 * sugerirle que revise sus datos.
 */
export function textoDeAviso(status: number): TextoAviso {
  switch (status) {
    case 0:
      return {
        titulo: 'No pudimos conectarnos',
        texto: 'Revisa tu conexión e intenta de nuevo — tus datos siguen cargados.',
        advertencia: true,
      }
    case 400:
      return {
        titulo: 'No pudimos procesar el análisis',
        texto: 'El servidor no pudo completar el análisis con estos datos. Prueba de nuevo en unos segundos — tus datos siguen cargados.',
        advertencia: false,
      }
    case 503:
      return {
        titulo: 'El análisis no está disponible ahora',
        texto: 'El servicio que calcula tu perfil no responde en este momento. Prueba de nuevo en unos minutos — tus datos siguen cargados.',
        advertencia: true,
      }
    default:
      return {
        titulo: 'No pudimos completar el análisis',
        texto: 'El servidor respondió con un error. Puedes intentar de nuevo en unos segundos — tus datos siguen cargados.',
        advertencia: false,
      }
  }
}

/**
 * Pantalla completa cuando se abre /analisis/:id y no hay nada ahí.
 *
 * El diseño planteaba esta pantalla para explicar que los análisis no se
 * guardaban. Desde que se persisten, el motivo real es otro: el enlace está
 * mal, o el análisis ya no está. El texto acompaña ese cambio.
 */
export function textoDeAnalisisAusente(status: number): TextoAviso {
  if (status === 404) {
    return {
      titulo: 'No encontramos ese análisis',
      texto: 'El enlace puede estar incompleto o el análisis ya no está disponible. Puedes hacer uno nuevo en un minuto.',
      advertencia: true,
    }
  }
  return {
    titulo: 'No pudimos recuperar el análisis',
    texto: 'Hubo un problema al buscar este resultado. Prueba de nuevo en unos segundos.',
    advertencia: false,
  }
}

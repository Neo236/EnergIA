/* ============================================================
   Capa de transporte.

   Dos operaciones, que son las dos que expone el back-end:
     POST /api/v1/analisis-energetico       → crea y persiste un análisis
     GET  /api/v1/analisis-energetico/{id}  → lo recupera por su UUID

   La aplicación habla siempre con la API. Hubo un modo simulado que
   resolvía las dos operaciones en el navegador para poder trabajar sin
   levantar el back-end; se retiró porque reimplementaba la clasificación
   del modelo en TypeScript, y esa segunda versión podía separarse de la
   real sin que nada lo señalara.
   ============================================================ */

import { ENDPOINT, ErrorApi, type Analisis, type RespuestaError, type Solicitud } from './contrato'

/** Falla de red: ni siquiera llegamos al servidor. status 0 lo distingue de un error HTTP. */
function errorDeRed(): ErrorApi {
  return new ErrorApi({ status: 0, mensaje: 'No se pudo establecer la conexión con el servidor' })
}

/**
 * Normaliza cualquier respuesta no-2xx al formato de error del back-end.
 * Si el cuerpo no es el JSON esperado — por ejemplo un 502 con HTML de nginx —
 * se completa con lo que diga el status, para no perder la causa.
 */
function errorDeRespuesta(respuesta: Response, cuerpo: unknown): ErrorApi {
  const parcial = (cuerpo ?? {}) as Partial<RespuestaError>
  return new ErrorApi({
    status: parcial.status ?? respuesta.status,
    error: parcial.error ?? respuesta.statusText,
    mensaje: parcial.mensaje ?? `Error ${respuesta.status}`,
    ...(parcial.detalles ? { detalles: parcial.detalles } : {}),
    ...(parcial.timestamp ? { timestamp: parcial.timestamp } : {}),
  })
}

async function leerCuerpo(respuesta: Response): Promise<unknown> {
  return respuesta.json().catch(() => null)
}

/** Crea un análisis. Devuelve el registro persistido, ya con id y fecha. */
export async function analizar(solicitud: Solicitud): Promise<Analisis> {
  let respuesta: Response
  try {
    respuesta = await fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(solicitud),
    })
  } catch {
    throw errorDeRed()
  }

  const cuerpo = await leerCuerpo(respuesta)
  if (!respuesta.ok) throw errorDeRespuesta(respuesta, cuerpo)
  return cuerpo as Analisis
}

/** Recupera un análisis por su id. Un 404 significa que no existe o expiró. */
export async function obtenerAnalisis(id: string): Promise<Analisis> {
  let respuesta: Response
  try {
    respuesta = await fetch(`${ENDPOINT}/${encodeURIComponent(id)}`)
  } catch {
    throw errorDeRed()
  }

  const cuerpo = await leerCuerpo(respuesta)
  if (!respuesta.ok) throw errorDeRespuesta(respuesta, cuerpo)
  return cuerpo as Analisis
}

/* ============================================================
   Capa de transporte.

   Dos operaciones, que son las dos que expone el back-end:
     POST /api/v1/analisis-energetico       → crea y persiste un análisis
     GET  /api/v1/analisis-energetico/{id}  → lo recupera por su UUID

   El modo se resuelve al compilar con VITE_API_MODO. En `mock` no se
   toca la red: sirve para desarrollar sin levantar el back. No hay
   interruptor en pantalla — esto es la aplicación, no una demostración.
   ============================================================ */

import { ENDPOINT, ErrorApi, type Analisis, type RespuestaError, type Solicitud } from './contrato'
import { analizarSimulado, obtenerSimulado } from './mock'

export type ModoApi = 'mock' | 'real'

export const MODO_API: ModoApi = import.meta.env.VITE_API_MODO === 'real' ? 'real' : 'mock'

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

async function analizarReal(solicitud: Solicitud): Promise<Analisis> {
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

async function obtenerReal(id: string): Promise<Analisis> {
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

/** Crea un análisis. Devuelve el registro persistido, ya con id y fecha. */
export function analizar(solicitud: Solicitud): Promise<Analisis> {
  return MODO_API === 'real' ? analizarReal(solicitud) : analizarSimulado(solicitud)
}

/** Recupera un análisis por su id. Un 404 significa que no existe o expiró. */
export function obtenerAnalisis(id: string): Promise<Analisis> {
  return MODO_API === 'real' ? obtenerReal(id) : obtenerSimulado(id)
}

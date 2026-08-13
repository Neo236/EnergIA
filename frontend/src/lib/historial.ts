/* ============================================================
   Historial local de análisis.

   Guarda un registro mínimo de cada análisis en localStorage para que
   el usuario pueda volver a sus resultados sin recordar la URL.

   Se guarda solo lo necesario para pintar la fila del historial
   (id, fecha, categoría, costo). El análisis completo —recomendaciones,
   confianza, etc.— se sigue pidiendo al back-end cuando el usuario abre
   la URL individual.

   El historial está acotado a MAX_ENTRADAS. Si se llena, las más viejas
   se descartan silenciosamente.
   ============================================================ */

import { useState } from 'react'

import type { Analisis, Categoria } from './contrato'

export interface EntradaHistorial {
  id: string
  fecha: string
  categoria: Categoria
  costo_estimado_mensual: number
}

const CLAVE_HISTORIAL = 'energiai:historial'
const MAX_ENTRADAS = 20

function leer(): EntradaHistorial[] {
  try {
    return JSON.parse(localStorage.getItem(CLAVE_HISTORIAL) ?? '[]') as EntradaHistorial[]
  } catch {
    return []
  }
}

function escribir(entradas: EntradaHistorial[]): void {
  try {
    localStorage.setItem(CLAVE_HISTORIAL, JSON.stringify(entradas))
  } catch {
    // Modo privado o almacenamiento lleno: se ignora silenciosamente.
    // El análisis ya fue devuelto y la URL sigue funcionando; solo no
    // va a aparecer en el historial local.
  }
}

/**
 * Añade o actualiza un análisis en el historial.
 * Si ya existe un registro con el mismo id, lo mueve al primer lugar
 * (el más reciente) sin duplicarlo.
 */
export function registrarEnHistorial(analisis: Analisis): void {
  const entrada: EntradaHistorial = {
    id: analisis.id,
    fecha: analisis.fecha,
    categoria: analisis.categoria,
    costo_estimado_mensual: analisis.costo_estimado_mensual,
  }
  const previas = leer().filter((e) => e.id !== analisis.id)
  escribir([entrada, ...previas].slice(0, MAX_ENTRADAS))
}

/**
 * Hook que expone el historial y las operaciones para modificarlo.
 * El estado es local al componente: un cambio en otro tab solo se ve
 * tras recargar la página, lo cual es aceptable para este caso de uso.
 */
export function useHistorial() {
  const [entradas, setEntradas] = useState<EntradaHistorial[]>(leer)

  /** Borra una o varias entradas de una sola pasada.
      Ojo si se te ocurre "simplificar" esto llamando a esta función en un
      loop por cada id: cada llamada leería `entradas` del mismo closure
      obsoleto, y solo la última sobrevive — se pierden todas las
      anteriores salvo la última del lote. Por eso el filtro es uno solo,
      contra el Set completo. */
  function borrarSeleccionadas(ids: Set<string>): void {
    const siguientes = entradas.filter((e) => !ids.has(e.id))
    escribir(siguientes)
    setEntradas(siguientes)
  }

  function borrarTodo(): void {
    escribir([])
    setEntradas([])
  }

  return { entradas, borrarSeleccionadas, borrarTodo }
}

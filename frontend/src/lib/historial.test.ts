import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'

import type { Analisis } from './contrato'
import { registrarEnHistorial, useHistorial } from './historial'

const CLAVE = 'energia:historial'

function analisis(id: string, fecha = '2026-08-13T12:00:00Z'): Analisis {
  return {
    id,
    fecha,
    categoria: 'Moderado',
    probabilidad: 0.65,
    costo_estimado_mensual: 100,
    recomendaciones: [],
  }
}

beforeEach(() => {
  localStorage.clear()
})

describe('registrarEnHistorial', () => {
  it('agrega una entrada nueva al principio', () => {
    registrarEnHistorial(analisis('a'))
    registrarEnHistorial(analisis('b'))
    const guardado = JSON.parse(localStorage.getItem(CLAVE) ?? '[]')
    expect(guardado.map((e: { id: string }) => e.id)).toEqual(['b', 'a'])
  })

  it('mueve una entrada existente al frente en vez de duplicarla', () => {
    registrarEnHistorial(analisis('a'))
    registrarEnHistorial(analisis('b'))
    registrarEnHistorial(analisis('a'))
    const guardado = JSON.parse(localStorage.getItem(CLAVE) ?? '[]')
    expect(guardado.map((e: { id: string }) => e.id)).toEqual(['a', 'b'])
    expect(guardado).toHaveLength(2)
  })

  it('descarta las más viejas al superar MAX_ENTRADAS (20)', () => {
    for (let i = 0; i < 21; i++) {
      registrarEnHistorial(analisis(`id-${i}`))
    }
    const guardado = JSON.parse(localStorage.getItem(CLAVE) ?? '[]')
    expect(guardado).toHaveLength(20)
    // La más nueva (id-20) sobrevive; la más vieja (id-0) se descartó.
    expect(guardado[0].id).toBe('id-20')
    expect(guardado.some((e: { id: string }) => e.id === 'id-0')).toBe(false)
  })
})

describe('useHistorial().borrarSeleccionadas', () => {
  it('borra varias entradas seleccionadas en una sola pasada', () => {
    registrarEnHistorial(analisis('a'))
    registrarEnHistorial(analisis('b'))
    registrarEnHistorial(analisis('c'))

    const { result } = renderHook(() => useHistorial())
    expect(result.current.entradas).toHaveLength(3)

    act(() => {
      result.current.borrarSeleccionadas(new Set(['a', 'c']))
    })

    expect(result.current.entradas.map((e) => e.id)).toEqual(['b'])
    const guardado = JSON.parse(localStorage.getItem(CLAVE) ?? '[]')
    expect(guardado.map((e: { id: string }) => e.id)).toEqual(['b'])
  })

  it('no pierde borrados al no depender de un closure obsoleto', () => {
    // Regresión explícita del bug que se evitó a propósito: llamar a una
    // versión "borrar de a uno" en un loop, dentro de un mismo handler,
    // perdería todo menos el último borrado porque cada llamada cerraría
    // sobre el mismo `entradas` desactualizado. borrarSeleccionadas evita
    // esto filtrando una sola vez contra el Set completo.
    for (let i = 0; i < 5; i++) registrarEnHistorial(analisis(`id-${i}`))

    const { result } = renderHook(() => useHistorial())
    expect(result.current.entradas).toHaveLength(5)

    act(() => {
      result.current.borrarSeleccionadas(new Set(['id-0', 'id-1', 'id-2', 'id-3']))
    })

    expect(result.current.entradas.map((e) => e.id)).toEqual(['id-4'])
  })
})

describe('useHistorial().borrarTodo', () => {
  it('vacía el historial completo', () => {
    registrarEnHistorial(analisis('a'))
    registrarEnHistorial(analisis('b'))

    const { result } = renderHook(() => useHistorial())

    act(() => {
      result.current.borrarTodo()
    })

    expect(result.current.entradas).toEqual([])
    expect(localStorage.getItem(CLAVE)).toBe('[]')
  })
})

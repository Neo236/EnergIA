import { afterEach, describe, expect, it, vi } from 'vitest'

import { fechaLegible, fechaRelativa, pesos, porcentaje } from './formato'

describe('pesos', () => {
  it('formatea con separador de miles y coma decimal', () => {
    expect(pesos(3780)).toBe('$ 3.780,00')
    expect(pesos(315)).toBe('$ 315,00')
    expect(pesos(0)).toBe('$ 0,00')
  })
})

describe('porcentaje', () => {
  it('convierte una proporción a entero redondeado', () => {
    expect(porcentaje(0.65)).toBe(65)
    expect(porcentaje(0.654)).toBe(65)
    expect(porcentaje(0.656)).toBe(66)
  })
})

describe('fechaLegible', () => {
  it('formatea fecha y hora en español', () => {
    expect(fechaLegible('2026-08-13T09:30:00')).toBe('13 de agosto, 09:30 h')
  })

  it('devuelve string vacío para una fecha inválida', () => {
    expect(fechaLegible('no-es-una-fecha')).toBe('')
  })

  it('trunca fracciones de segundo de más de 3 dígitos sin invalidar la fecha', () => {
    // La columna `fecha` es TIMESTAMP de Postgres (microsegundos): el
    // backend puede mandar hasta 6 decimales. El formato Date Time String
    // de ECMA-262 solo garantiza soporte para 3 — sin el truncado en
    // comoFechaUtc esto queda a merced de la lenidad de cada motor JS.
    expect(fechaLegible('2026-08-13T09:30:00.123456')).toBe('13 de agosto, 09:30 h')
    expect(fechaLegible('2026-08-13T09:30:00.123456789')).toBe('13 de agosto, 09:30 h')
  })

  it('respeta una zona horaria explícita si el string ya la trae', () => {
    // 09:30 en -03:00 equivale a 12:30 UTC (zona del proceso de test).
    expect(fechaLegible('2026-08-13T09:30:00-03:00')).toBe('13 de agosto, 12:30 h')
  })
})

describe('fechaRelativa', () => {
  const AHORA = new Date('2026-08-13T12:00:00Z')

  afterEach(() => {
    vi.useRealTimers()
  })

  it('"Hace un momento" para menos de 45 segundos', () => {
    vi.setSystemTime(AHORA)
    expect(fechaRelativa('2026-08-13T11:59:20Z')).toBe('Hace un momento')
  })

  it('minutos, en singular y plural', () => {
    vi.setSystemTime(AHORA)
    expect(fechaRelativa('2026-08-13T11:59:00Z')).toBe('Hace 1 minuto')
    expect(fechaRelativa('2026-08-13T11:55:00Z')).toBe('Hace 5 minutos')
  })

  it('horas, en singular y plural', () => {
    vi.setSystemTime(AHORA)
    expect(fechaRelativa('2026-08-13T11:00:00Z')).toBe('Hace 1 hora')
    expect(fechaRelativa('2026-08-13T09:00:00Z')).toBe('Hace 3 horas')
  })

  it('"Ayer a las HH:MM h" para el día anterior', () => {
    // Tiene que pasar las 24 h para salir del bucket de "horas" (ver el
    // orden de los if en fechaRelativa) y redondear a 1 día.
    vi.setSystemTime(AHORA)
    expect(fechaRelativa('2026-08-12T10:00:00Z')).toBe('Ayer a las 10:00 h')
  })

  it('"Hace N días" antes de la semana', () => {
    vi.setSystemTime(AHORA)
    expect(fechaRelativa('2026-08-10T12:00:00Z')).toBe('Hace 3 días')
  })

  it('cae a la fecha absoluta pasada una semana', () => {
    vi.setSystemTime(AHORA)
    expect(fechaRelativa('2026-08-01T09:30:00Z')).toBe('Análisis del 1 de agosto, 09:30 h')
  })

  it('devuelve string vacío para una fecha inválida', () => {
    vi.setSystemTime(AHORA)
    expect(fechaRelativa('no-es-una-fecha')).toBe('')
  })
})

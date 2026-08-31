import { describe, expect, it } from 'vitest'
import { RANGOS, validarEntrada, type EntradaFormulario } from './validacion'

/* Entrada válida mínima. Cada test cambia solo el campo que le interesa, así
   un fallo señala una regla y no una combinación. */
const VALIDA: EntradaFormulario = {
  consumo: '420',
  equipos: 10,
  horas: 12,
  metros: '',
  antiguedad: '',
  tipo: 'Casa',
  zonaFria: false,
  aislamiento: 'Media',
  calefaccion: 'Electricidad',
  agua: 'Electricidad',
  horarioPico: false,
}

const con = (cambios: Partial<EntradaFormulario>) => ({ ...VALIDA, ...cambios })

describe('validarEntrada', () => {
  it('acepta una entrada válida y arma la solicitud', () => {
    const { errores, solicitud } = validarEntrada(VALIDA)
    expect(errores).toEqual({})
    expect(solicitud).toMatchObject({
      consumo_kwh: 420,
      cantidad_equipos: 10,
      horas_alto_consumo: 12,
      tipo_inmueble: 'Casa',
    })
  })

  it('nunca devuelve solicitud junto con errores', () => {
    const { errores, solicitud } = validarEntrada(con({ consumo: '0' }))
    expect(Object.keys(errores).length).toBeGreaterThan(0)
    expect(solicitud).toBeNull()
  })

  it('acumula todos los errores, no solo el primero', () => {
    const { errores } = validarEntrada(con({ consumo: '0', equipos: 0, horas: 99 }))
    expect(Object.keys(errores).sort()).toEqual([
      'cantidad_equipos', 'consumo_kwh', 'horas_alto_consumo',
    ])
  })
})

/* Los límites son donde viven los errores de rango: un `<` donde iba un `<=`
   solo se nota exactamente en el borde. */
describe('límites de los campos obligatorios', () => {
  const casos = [
    ['consumo_kwh', RANGOS.consumo_kwh, (v: number) => con({ consumo: String(v) })],
    ['cantidad_equipos', RANGOS.cantidad_equipos, (v: number) => con({ equipos: v })],
    ['horas_alto_consumo', RANGOS.horas_alto_consumo, (v: number) => con({ horas: v })],
  ] as const

  it.each(casos)('%s acepta exactamente el mínimo y el máximo', (campo, rango, hacer) => {
    expect(validarEntrada(hacer(rango.min)).errores[campo]).toBeUndefined()
    expect(validarEntrada(hacer(rango.max)).errores[campo]).toBeUndefined()
  })

  it.each(casos)('%s rechaza justo por debajo y justo por encima', (campo, rango, hacer) => {
    expect(validarEntrada(hacer(rango.min - 1)).errores[campo]).toBeDefined()
    expect(validarEntrada(hacer(rango.max + 1)).errores[campo]).toBeDefined()
  })
})

describe('campos opcionales', () => {
  it('vacíos no son un error y se omiten de la solicitud', () => {
    const { errores, solicitud } = validarEntrada(con({ metros: '', antiguedad: '' }))
    expect(errores).toEqual({})
    // Omitidos, no en null: el back-end aplica su valor por defecto cuando la
    // clave no viaja, pero rechazaria un null explicito.
    expect(solicitud).not.toHaveProperty('metros_cuadrados')
    expect(solicitud).not.toHaveProperty('antiguedad_vivienda')
  })

  it('completados sí se validan', () => {
    expect(validarEntrada(con({ metros: '10' })).errores.metros_cuadrados).toBeDefined()
    expect(validarEntrada(con({ antiguedad: '200' })).errores.antiguedad_vivienda).toBeDefined()
  })

  it('completados y válidos viajan en la solicitud', () => {
    const { solicitud } = validarEntrada(con({ metros: '80', antiguedad: '15' }))
    expect(solicitud).toMatchObject({ metros_cuadrados: 80, antiguedad_vivienda: 15 })
  })

  it.each([
    ['metros_cuadrados', RANGOS.metros_cuadrados, (v: number) => con({ metros: String(v) })],
    ['antiguedad_vivienda', RANGOS.antiguedad_vivienda, (v: number) => con({ antiguedad: String(v) })],
  ] as const)('%s respeta sus límites', (campo, rango, hacer) => {
    expect(validarEntrada(hacer(rango.min)).errores[campo]).toBeUndefined()
    expect(validarEntrada(hacer(rango.max)).errores[campo]).toBeUndefined()
    expect(validarEntrada(hacer(rango.min - 1)).errores[campo]).toBeDefined()
    expect(validarEntrada(hacer(rango.max + 1)).errores[campo]).toBeDefined()
  })
})

describe('entrada de texto del consumo', () => {
  it('acepta coma decimal, que es como se escribe en español', () => {
    expect(validarEntrada(con({ consumo: '420,5' })).solicitud?.consumo_kwh).toBe(420.5)
  })

  it('acepta punto decimal', () => {
    expect(validarEntrada(con({ consumo: '420.5' })).solicitud?.consumo_kwh).toBe(420.5)
  })

  it.each(['', '   ', 'abc', '-'])('rechaza %o', (texto) => {
    expect(validarEntrada(con({ consumo: texto })).errores.consumo_kwh).toBeDefined()
  })
})

/* Estos rangos son una copia de las anotaciones de DatosRegistroConsumo en el
   back-end. El test no puede leer el Java, pero sí dejar las cifras escritas
   una segunda vez: si alguien cambia RANGOS sin cambiar el DTO, esto falla y
   obliga a mirar las dos puntas. */
describe('paridad con el contrato del back-end', () => {
  it('los rangos son los del DTO de Java', () => {
    expect(RANGOS).toEqual({
      consumo_kwh:         { min: 1,  max: 1000 },
      cantidad_equipos:    { min: 1,  max: 100 },
      horas_alto_consumo:  { min: 0,  max: 24 },
      metros_cuadrados:    { min: 26, max: 2000 },
      antiguedad_vivienda: { min: 0,  max: 150 },
    })
  })
})

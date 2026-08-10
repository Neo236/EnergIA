const moneda = new Intl.NumberFormat('es-AR', {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
})

export const pesos = (valor: number): string => `$ ${moneda.format(valor)}`

export const porcentaje = (proporcion: number): number => Math.round(proporcion * 100)

const MESES = [
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
]

/** La API no devuelve fecha (PA-19): se deriva en el cliente y se rotula como tal. */
export function fechaLegible(fecha: Date): string {
  const hh = String(fecha.getHours()).padStart(2, '0')
  const mm = String(fecha.getMinutes()).padStart(2, '0')
  return `Análisis del ${fecha.getDate()} de ${MESES[fecha.getMonth()]}, ${hh}:${mm} h`
}

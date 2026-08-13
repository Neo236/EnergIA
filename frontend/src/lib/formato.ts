/* ============================================================
   Formato de números y fechas para mostrar.

   Formato latinoamericano: coma decimal y punto de millar, tal como
   aparece en el diseño ($ 315,00 · $ 3.780,00).
   ============================================================ */

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

/**
 * La fecha viene del back-end como LocalDateTime («2026-08-10T11:45:00»),
 * sin zona horaria. Se interpreta como hora local, que es lo que espera
 * quien lo lee.
 *
 * Antes se derivaba en el cliente porque la API no la devolvía; desde que
 * los análisis se persisten, la fecha es la real del análisis y por eso
 * sigue siendo correcta al abrir un enlace guardado días después.
 */
export function fechaLegible(iso: string): string {
  const fecha = new Date(iso)
  if (Number.isNaN(fecha.getTime())) return ''
  const hh = String(fecha.getHours()).padStart(2, '0')
  const mm = String(fecha.getMinutes()).padStart(2, '0')
  return `Análisis del ${fecha.getDate()} de ${MESES[fecha.getMonth()]}, ${hh}:${mm} h`
}

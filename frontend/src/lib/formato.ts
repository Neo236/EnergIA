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
 * La fecha viene del back-end como LocalDateTime («2026-08-13T12:22:00»),
 * sin zona horaria. El JVM del backend corre sin TZ configurado (ver
 * backend/Dockerfile), así que esa hora es UTC aunque el string no lo diga.
 *
 * `new Date(iso)` sobre un string SIN offset lo interpreta como hora LOCAL
 * del navegador — exactamente al revés de lo que es. Por eso se le agrega
 * 'Z' antes de parsear, salvo que ya traiga su propia zona.
 *
 * Es un parche del lado del cliente: lo correcto es que el back-end migre
 * a OffsetDateTime y mande la zona en la respuesta (ver docs de la charla
 * sobre CD). El día que lo haga, el string ya va a traer 'Z' o un offset
 * propio, y esta función lo deja pasar tal cual — no hace falta tocar el
 * front cuando eso pase.
 *
 * Una vez parseada como UTC, cualquier getHours()/getDate()/etc. de abajo
 * ya devuelve la hora LOCAL de quien mira la pantalla, sin importar en qué
 * zona horaria esté — es como funciona Date en JS: guarda un instante
 * absoluto, y son los getters no-UTC los que lo traducen a la zona del
 * dispositivo. No hace falta detectarla a mano.
 */
function comoFechaUtc(iso: string): Date | null {
  const CON_ZONA = /(Z|[+-]\d{2}:?\d{2})$/
  const normalizado = CON_ZONA.test(iso) ? iso : `${iso}Z`
  const fecha = new Date(normalizado)
  return Number.isNaN(fecha.getTime()) ? null : fecha
}

/** Fecha y hora absolutas, en el formato «13 de agosto, 09:30 h». Para
    componer dentro de otra frase: `análisis del ${fechaLegible(iso)}`. */
export function fechaLegible(iso: string): string {
  const fecha = comoFechaUtc(iso)
  if (!fecha) return ''
  const hh = String(fecha.getHours()).padStart(2, '0')
  const mm = String(fecha.getMinutes()).padStart(2, '0')
  return `${fecha.getDate()} de ${MESES[fecha.getMonth()]}, ${hh}:${mm} h`
}

/**
 * Igual que fechaLegible, pero relativa cuando es reciente — "Hace 5
 * minutos", "Ayer a las 14:30 h" — que es como se lee justo después de
 * analizar. Pasada una semana cae a la fecha absoluta con el mismo
 * "Análisis del ..." que se usaba siempre: un enlace guardado hace meses
 * no gana nada con "hace 53 días".
 */
export function fechaRelativa(iso: string): string {
  const fecha = comoFechaUtc(iso)
  if (!fecha) return ''

  const segundos = Math.round((Date.now() - fecha.getTime()) / 1000)
  if (segundos < 45) return 'Hace un momento'
  if (segundos < 3600) {
    const min = Math.round(segundos / 60)
    return `Hace ${min} ${min === 1 ? 'minuto' : 'minutos'}`
  }
  if (segundos < 86400) {
    const horas = Math.round(segundos / 3600)
    return `Hace ${horas} ${horas === 1 ? 'hora' : 'horas'}`
  }
  const dias = Math.round(segundos / 86400)
  if (dias === 1) {
    const hh = String(fecha.getHours()).padStart(2, '0')
    const mm = String(fecha.getMinutes()).padStart(2, '0')
    return `Ayer a las ${hh}:${mm} h`
  }
  if (dias < 7) return `Hace ${dias} días`
  return `Análisis del ${fechaLegible(iso)}`
}

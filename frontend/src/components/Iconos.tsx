/* ============================================================
   Iconografía.

   Estilo outline, trazo 1.5px y esquinas redondeadas, según las notas de
   diseño. (Los vectores dibujados en Figma usan 2px: la regla escrita y
   el dibujo no coinciden. Seguimos la regla escrita, que es la que el
   sistema declara.)

   Todos heredan el color con `currentColor` y se dimensionan con la
   propiedad `tamano`, así una misma pieza sirve en varios contextos.
   ============================================================ */

interface PropsIcono {
  tamano?: number
  className?: string
}

const trazo = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.5,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
}

/** Rayo de la marca. Es el único relleno: funciona como logotipo, no como icono. */
export function IconoRayo({ tamano = 16, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" className={className}>
      <path d="M13.5 2 4 13.5h6L9.5 22 20 10.5h-6.5z" />
    </svg>
  )
}

export function IconoFlecha({ tamano = 16, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" aria-hidden="true" className={className} {...trazo}>
      <path d="m6 9 6 6 6-6" />
    </svg>
  )
}

/** Triángulo de advertencia. Se usa en errores del servidor y en el veredicto negativo. */
export function IconoAlerta({ tamano = 20, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" aria-hidden="true" className={className} {...trazo}>
      <path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z" />
      <path d="M12 9v4" />
      <path d="M12 17h.01" />
    </svg>
  )
}

/** Círculo informativo, para el 503: el servicio no está, pero nada falló del lado del usuario. */
export function IconoCirculo({ tamano = 20, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" aria-hidden="true" className={className} {...trazo}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 8v5" />
      <path d="M12 16h.01" />
    </svg>
  )
}

/** Tilde para el veredicto eficiente: un triángulo de alerta ahí diría lo contrario. */
export function IconoTilde({ tamano = 20, className }: PropsIcono) {
  return (
    <svg width={tamano} height={tamano} viewBox="0 0 24 24" aria-hidden="true" className={className} {...trazo}>
      <path d="m4 12.5 5 5L20 6.5" />
    </svg>
  )
}

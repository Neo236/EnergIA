import type { ReactNode } from 'react'

interface Props {
  nombre: string
  etiqueta: string
  ayuda: string
  error?: string
  /** Cuando la etiqueta rotula un grupo (tarjetas, switch) y no un input. */
  comoGrupo?: boolean
  /** Se muestra alineado a la derecha de la etiqueta (p. ej. el valor de un slider). */
  valor?: ReactNode
  children: ReactNode
  className?: string
}

/**
 * Envoltorio común: etiqueta, control, y debajo la ayuda — o el error, que
 * la reemplaza. Centraliza el patrón para que ningún campo lo implemente
 * distinto y para que `aria-describedby` siempre apunte a algo.
 */
export function Campo({ nombre, etiqueta, ayuda, error, comoGrupo, valor, children, className }: Props) {
  const idAyuda = `ayuda-${nombre}`
  const clases = ['field', error ? 'has-error' : '', className].filter(Boolean).join(' ')

  const cabecera = valor
    ? (
      <div className="label-row">
        {comoGrupo
          ? <span className="label" id={`etiqueta-${nombre}`}>{etiqueta}</span>
          : <label className="label" htmlFor={nombre}>{etiqueta}</label>}
        <output className="label-row__value" htmlFor={nombre}>{valor}</output>
      </div>
    )
    : comoGrupo
      ? <span className="label" id={`etiqueta-${nombre}`}>{etiqueta}</span>
      : <label className="label" htmlFor={nombre}>{etiqueta}</label>

  return (
    <div className={clases} data-field={nombre}>
      {cabecera}
      {children}
      {error
        ? <p className="error" role="alert">{error}</p>
        : <p className="help" id={idAyuda}>{ayuda}</p>}
    </div>
  )
}

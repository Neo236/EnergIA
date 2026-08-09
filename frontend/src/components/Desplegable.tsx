import { useId, type ReactNode } from 'react'

interface Props {
  titulo: string
  resumen?: string
  ayuda?: string
  abierto: boolean
  onToggle: (abierto: boolean) => void
  /** `panel` da fondo propio al contenido (bloque de opcionales de P-01). */
  variante?: 'panel' | 'plano'
  children: ReactNode
}

export function Desplegable({ titulo, resumen, ayuda, abierto, onToggle, variante = 'panel', children }: Props) {
  const id = useId()

  return (
    <div className={variante === 'plano' ? 'opt opt--flat' : 'opt'}>
      <button
        type="button"
        className="opt__head"
        aria-expanded={abierto}
        aria-controls={id}
        onClick={() => onToggle(!abierto)}
      >
        <span className="opt__title">{titulo}</span>
        <span className="opt__meta">
          {resumen && <span className="opt__count">{resumen}</span>}
          <span className="opt__chev" aria-hidden="true" />
        </span>
      </button>

      {ayuda && <p className="help">{ayuda}</p>}

      <div className="opt__body" id={id} hidden={!abierto}>
        {children}
      </div>
    </div>
  )
}

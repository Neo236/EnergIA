import { Campo } from './Campo'

/* ─────────────── entrada numérica con unidad ─────────────── */

interface EntradaProps {
  nombre: string
  etiqueta: string
  ayuda: string
  error?: string
  valor: string
  onChange: (valor: string) => void
  min: number
  max: number
  unidad?: string
  decimal?: boolean
  /** Se muestra como placeholder: comunica qué se envía si se deja vacío. */
  defecto?: number
}

export function EntradaNumero(p: EntradaProps) {
  return (
    <Campo nombre={p.nombre} etiqueta={p.etiqueta} ayuda={p.ayuda} error={p.error}>
      <div className="control">
        <input
          className="input"
          id={p.nombre}
          name={p.nombre}
          type="number"
          inputMode={p.decimal ? 'decimal' : 'numeric'}
          min={p.min}
          max={p.max}
          step={p.decimal ? 0.1 : 1}
          placeholder={p.defecto !== undefined ? String(p.defecto) : '0'}
          value={p.valor}
          onChange={(e) => p.onChange(e.target.value)}
          aria-describedby={`ayuda-${p.nombre}`}
          aria-invalid={p.error ? true : undefined}
        />
        {p.unidad && <span className="control__unit">{p.unidad}</span>}
      </div>
    </Campo>
  )
}

/* ─────────────── tarjetas de opción única ─────────────── */

interface TarjetasProps {
  nombre: string
  etiqueta: string
  ayuda: string
  error?: string
  valores: readonly string[]
  etiquetasCortas?: Record<string, string>
  valor: string
  onChange: (valor: string) => void
}

export function TarjetasOpcion(p: TarjetasProps) {
  return (
    <fieldset className={['field', p.error ? 'has-error' : ''].filter(Boolean).join(' ')} data-field={p.nombre}>
      <legend className="label">{p.etiqueta}</legend>
      <div className="cards">
        {p.valores.map((v) => (
          <label className="cardopt" key={v}>
            <input
              type="radio"
              name={p.nombre}
              value={v}
              checked={p.valor === v}
              onChange={() => p.onChange(v)}
            />
            <span>{p.etiquetasCortas?.[v] ?? v}</span>
          </label>
        ))}
      </div>
      {p.error
        ? <p className="error" role="alert">{p.error}</p>
        : <p className="help">{p.ayuda}</p>}
    </fieldset>
  )
}

/* ─────────────── stepper ─────────────── */

interface StepperProps {
  nombre: string
  etiqueta: string
  ayuda: string
  error?: string
  valor: string
  onChange: (valor: string) => void
  min: number
  max: number
}

export function Stepper(p: StepperProps) {
  const actual = Number(p.valor || 0)
  const mover = (paso: number) => p.onChange(String(Math.min(p.max, Math.max(p.min, actual + paso))))

  return (
    <Campo nombre={p.nombre} etiqueta={p.etiqueta} ayuda={p.ayuda} error={p.error} className="field--half">
      <div className="stepper">
        <button
          type="button" className="stepper__btn" aria-label="Restar un equipo"
          disabled={actual <= p.min} onClick={() => mover(-1)}
        >−</button>
        <input
          className="stepper__value" id={p.nombre} name={p.nombre} type="number"
          inputMode="numeric" min={p.min} max={p.max}
          value={p.valor} onChange={(e) => p.onChange(e.target.value)}
          aria-describedby={`ayuda-${p.nombre}`} aria-invalid={p.error ? true : undefined}
        />
        <button
          type="button" className="stepper__btn" aria-label="Sumar un equipo"
          disabled={actual >= p.max} onClick={() => mover(1)}
        >+</button>
      </div>
    </Campo>
  )
}

/* ─────────────── deslizador ─────────────── */

interface DeslizadorProps {
  nombre: string
  etiqueta: string
  error?: string
  valor: number
  onChange: (valor: number) => void
  min: number
  max: number
  unidad: string
}

export function Deslizador(p: DeslizadorProps) {
  const relleno = `${((p.valor - p.min) / (p.max - p.min)) * 100}%`

  return (
    <div className={['field', p.error ? 'has-error' : ''].filter(Boolean).join(' ')} data-field={p.nombre}>
      <div className="label-row">
        <label className="label" htmlFor={p.nombre}>{p.etiqueta}</label>
        <output className="label-row__value" htmlFor={p.nombre}>{p.valor} {p.unidad}</output>
      </div>
      <input
        className="range" id={p.nombre} name={p.nombre} type="range"
        min={p.min} max={p.max} step={1}
        value={p.valor} onChange={(e) => p.onChange(Number(e.target.value))}
        style={{ '--fill': relleno } as React.CSSProperties}
        aria-invalid={p.error ? true : undefined}
      />
      <div className="ticks">
        <span>{p.min} {p.unidad}</span>
        <span>{Math.round((p.min + p.max) / 2)} {p.unidad}</span>
        <span>{p.max} {p.unidad}</span>
      </div>
      {p.error && <p className="error" role="alert">{p.error}</p>}
    </div>
  )
}

/* ─────────────── selección ─────────────── */

interface SeleccionProps {
  nombre: string
  etiqueta: string
  ayuda: string
  error?: string
  valores: readonly string[]
  defecto: string
  valor: string
  onChange: (valor: string) => void
}

export function Seleccion(p: SeleccionProps) {
  return (
    <Campo nombre={p.nombre} etiqueta={p.etiqueta} ayuda={p.ayuda} error={p.error}>
      <div className="control control--select">
        <select
          className="select" id={p.nombre} name={p.nombre}
          value={p.valor} onChange={(e) => p.onChange(e.target.value)}
          aria-describedby={`ayuda-${p.nombre}`} aria-invalid={p.error ? true : undefined}
        >
          <option value="">{p.defecto} (por defecto)</option>
          {p.valores.map((v) => <option key={v} value={v}>{v}</option>)}
        </select>
      </div>
    </Campo>
  )
}

/* ─────────────── interruptor ─────────────── */

interface InterruptorProps {
  nombre: string
  etiqueta: string
  ayuda: string
  error?: string
  valor: boolean
  onChange: (valor: boolean) => void
}

export function Interruptor(p: InterruptorProps) {
  return (
    <Campo nombre={p.nombre} etiqueta={p.etiqueta} ayuda={p.ayuda} error={p.error} comoGrupo>
      <div className="switch-row">
        <button
          type="button" className="switch" id={p.nombre}
          role="switch" aria-checked={p.valor} aria-labelledby={`etiqueta-${p.nombre}`}
          onClick={() => p.onChange(!p.valor)}
        >
          <span className="switch__dot" />
        </button>
        <span className="switch__state">{p.valor ? 'Sí' : 'No'}</span>
      </div>
    </Campo>
  )
}

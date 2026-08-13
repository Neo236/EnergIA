/* ============================================================
   Campos de formulario.

   Un componente por tipo de control, igual que la sección «Campos de
   formulario» del sistema de diseño: Texto, Contador, Opciones,
   Desplegable, Deslizador e Interruptor.

   Dos reglas transversales, tomadas del diseño:
   - El error REEMPLAZA a la ayuda, no se suma. Así la fila no cambia de
     alto al fallar la validación y el formulario no salta.
   - Todo control queda asociado a su etiqueta y anuncia su ayuda o su
     error con aria-describedby, de modo que un lector de pantalla lea lo
     mismo que se ve.
   ============================================================ */

import { useId, type ReactNode } from 'react'

import { IconoFlecha } from './Iconos'

/* ---------- envoltura común ---------- */

interface PropsEnvoltura {
  id: string
  etiqueta: string
  requerido?: boolean
  ayuda?: string
  error?: string
  children: ReactNode
  /** Cuando el control no es un único elemento enfocable (chips, interruptor). */
  comoGrupo?: boolean
}

function Envoltura({ id, etiqueta, requerido, ayuda, error, children, comoGrupo }: PropsEnvoltura) {
  const idAuxiliar = `${id}-aux`
  const auxiliar = error
    ? <p className="campo__error" id={idAuxiliar} role="alert">{error}</p>
    : ayuda
      ? <p className="campo__ayuda" id={idAuxiliar}>{ayuda}</p>
      : null

  const titulo = (
    <>
      {etiqueta}
      {requerido && <span className="campo__obligatorio" aria-hidden="true"> *</span>}
    </>
  )

  if (comoGrupo) {
    return (
      <div className="campo" role="group" aria-labelledby={`${id}-etiqueta`} aria-describedby={auxiliar ? idAuxiliar : undefined}>
        <span className="campo__etiqueta" id={`${id}-etiqueta`}>{titulo}</span>
        {children}
        {auxiliar}
      </div>
    )
  }

  return (
    <div className="campo">
      <label className="campo__etiqueta" htmlFor={id}>{titulo}</label>
      {children}
      {auxiliar}
    </div>
  )
}

function propsAuxiliares(id: string, ayuda?: string, error?: string) {
  return {
    'aria-describedby': error || ayuda ? `${id}-aux` : undefined,
    'aria-invalid': error ? true : undefined,
  }
}

/* ---------- Texto ---------- */

interface PropsTexto {
  etiqueta: string
  valor: string
  onCambio: (valor: string) => void
  unidad?: string
  requerido?: boolean
  ayuda?: string
  error?: string
  decimal?: boolean
}

export function CampoTexto({ etiqueta, valor, onCambio, unidad, requerido, ayuda, error, decimal }: PropsTexto) {
  const id = useId()
  return (
    <Envoltura id={id} etiqueta={etiqueta} requerido={requerido} ayuda={ayuda} error={error}>
      <div className={`entrada${error ? ' entrada--error' : ''}`}>
        <input
          id={id}
          className="entrada__campo"
          /* inputMode en vez de type=number: evita las flechitas del navegador,
             que en el diseño no existen, y en móvil abre el teclado correcto. */
          inputMode={decimal ? 'decimal' : 'numeric'}
          value={valor}
          onChange={(e) => onCambio(e.target.value)}
          {...propsAuxiliares(id, ayuda, error)}
        />
        {unidad && <span className="entrada__unidad" aria-hidden="true">{unidad}</span>}
      </div>
    </Envoltura>
  )
}

/* ---------- Contador ---------- */

interface PropsContador {
  etiqueta: string
  valor: number
  onCambio: (valor: number) => void
  min: number
  max: number
  requerido?: boolean
  ayuda?: string
  error?: string
}

export function CampoContador({ etiqueta, valor, onCambio, min, max, requerido, ayuda, error }: PropsContador) {
  const id = useId()
  const acotar = (n: number) => Math.min(max, Math.max(min, n))

  return (
    <Envoltura id={id} etiqueta={etiqueta} requerido={requerido} ayuda={ayuda} error={error}>
      <div className="contador">
        <button
          type="button" className="contador__boton"
          onClick={() => onCambio(acotar(valor - 1))}
          disabled={valor <= min}
          aria-label={`Restar uno a ${etiqueta.toLowerCase()}`}
        >−</button>

        <input
          id={id}
          className="contador__valor"
          inputMode="numeric"
          value={String(valor)}
          onChange={(e) => {
            const n = Number(e.target.value.replace(/\D/g, ''))
            if (!Number.isNaN(n)) onCambio(n)
          }}
          onBlur={() => onCambio(acotar(valor))}
          {...propsAuxiliares(id, ayuda, error)}
        />

        <button
          type="button" className="contador__boton"
          onClick={() => onCambio(acotar(valor + 1))}
          disabled={valor >= max}
          aria-label={`Sumar uno a ${etiqueta.toLowerCase()}`}
        >+</button>
      </div>
    </Envoltura>
  )
}

/* ---------- Opciones (chips) ---------- */

interface PropsOpciones {
  etiqueta: string
  valores: readonly string[]
  valor: string
  onCambio: (valor: string) => void
  etiquetasCortas?: Record<string, string>
  requerido?: boolean
  ayuda?: string
  error?: string
}

export function CampoOpciones({ etiqueta, valores, valor, onCambio, etiquetasCortas, requerido, ayuda, error }: PropsOpciones) {
  const id = useId()
  return (
    <Envoltura id={id} etiqueta={etiqueta} requerido={requerido} ayuda={ayuda} error={error} comoGrupo>
      <div className="opciones">
        {valores.map((opcion) => (
          <button
            key={opcion}
            type="button"
            className="opcion"
            aria-pressed={valor === opcion}
            onClick={() => onCambio(opcion)}
          >
            {/* La etiqueta corta es solo visual: al back viaja el valor del contrato. */}
            {etiquetasCortas?.[opcion] ?? opcion}
          </button>
        ))}
      </div>
    </Envoltura>
  )
}

/* ---------- Desplegable ---------- */

interface PropsDesplegable {
  etiqueta: string
  valores: readonly string[]
  valor: string
  onCambio: (valor: string) => void
  defecto?: string
  ayuda?: string
  error?: string
}

export function CampoDesplegable({ etiqueta, valores, valor, onCambio, defecto, ayuda, error }: PropsDesplegable) {
  const id = useId()
  return (
    <Envoltura id={id} etiqueta={etiqueta} ayuda={ayuda} error={error}>
      <select
        id={id}
        className="desplegable"
        value={valor}
        onChange={(e) => onCambio(e.target.value)}
        {...propsAuxiliares(id, ayuda, error)}
      >
        {valores.map((opcion) => (
          <option key={opcion} value={opcion}>
            {/* El diseño comunica el defecto dentro del propio valor. Se rotula
                solo mientras el valor elegido sigue siendo el de por defecto. */}
            {opcion === defecto ? `${opcion} (por defecto)` : opcion}
          </option>
        ))}
      </select>
    </Envoltura>
  )
}

/* ---------- Deslizador ---------- */

interface PropsDeslizador {
  etiqueta: string
  valor: number
  onCambio: (valor: number) => void
  min: number
  max: number
  unidad: string
  requerido?: boolean
  ayuda?: string
  error?: string
}

export function CampoDeslizador({ etiqueta, valor, onCambio, min, max, unidad, requerido, ayuda, error }: PropsDeslizador) {
  const id = useId()
  const relleno = ((valor - min) / (max - min)) * 100

  return (
    <div className="campo">
      <div className="deslizador__cabecera">
        <label className="campo__etiqueta" htmlFor={id}>
          {etiqueta}
          {requerido && <span className="campo__obligatorio" aria-hidden="true"> *</span>}
        </label>
        <span className="deslizador__valor">{valor} {unidad}</span>
      </div>

      <input
        id={id}
        type="range"
        className="deslizador__pista"
        min={min} max={max} step={1}
        value={valor}
        onChange={(e) => onCambio(Number(e.target.value))}
        style={{ ['--relleno' as string]: `${relleno}%` }}
        {...propsAuxiliares(id, ayuda, error)}
      />

      <div className="deslizador__limites" aria-hidden="true">
        <span>{min} {unidad}</span>
        <span>{max} {unidad}</span>
      </div>

      {error
        ? <p className="campo__error" id={`${id}-aux`} role="alert">{error}</p>
        : ayuda ? <p className="campo__ayuda" id={`${id}-aux`}>{ayuda}</p> : null}
    </div>
  )
}

/* ---------- Interruptor ---------- */

interface PropsInterruptor {
  etiqueta: string
  valor: boolean
  onCambio: (valor: boolean) => void
  ayuda?: string
  error?: string
}

export function CampoInterruptor({ etiqueta, valor, onCambio, ayuda, error }: PropsInterruptor) {
  const id = useId()
  return (
    <Envoltura id={id} etiqueta={etiqueta} ayuda={ayuda} error={error} comoGrupo>
      <div className="interruptor">
        <button type="button" className="interruptor__opcion" aria-pressed={valor} onClick={() => onCambio(true)}>Sí</button>
        <button type="button" className="interruptor__opcion" aria-pressed={!valor} onClick={() => onCambio(false)}>No</button>
      </div>
    </Envoltura>
  )
}

/* ---------- Acordeón ---------- */

interface PropsAcordeon {
  titulo: string
  insignia?: string
  nota?: string
  abierto: boolean
  onAlternar: () => void
  children: ReactNode
}

export function Acordeon({ titulo, insignia, nota, abierto, onAlternar, children }: PropsAcordeon) {
  const id = useId()
  return (
    <div className="acordeon">
      <button
        type="button"
        className="acordeon__cabecera"
        aria-expanded={abierto}
        aria-controls={`${id}-cuerpo`}
        onClick={onAlternar}
      >
        <span className="acordeon__titulo">{titulo}</span>
        {insignia && <span className="insignia insignia--neutra">{insignia}</span>}
        <IconoFlecha className="acordeon__flecha" />
      </button>

      {abierto && (
        <div className="acordeon__cuerpo" id={`${id}-cuerpo`}>
          {nota && <p className="acordeon__nota">{nota}</p>}
          {children}
        </div>
      )}
    </div>
  )
}

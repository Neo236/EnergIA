import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'

import { CAMPOS, type Analisis, type Categoria, type Solicitud } from '../lib/contrato'
import { fechaLegible, pesos, porcentaje } from '../lib/formato'
import { Desplegable } from '../components/Desplegable'
import { useTitulo } from '../lib/useTitulo'

/** Ícono además del color: el veredicto nunca se comunica solo con color (RNF-03). */
const ICONO: Record<Categoria, string> = {
  Eficiente: '▼',
  Moderado: '◆',
  Ineficiente: '▲',
}

interface EstadoNavegacion {
  analisis?: Analisis
  solicitud?: Solicitud
}

export function Resultado() {
  useTitulo('Resultado del análisis')

  const navegar = useNavigate()
  const { state } = useLocation() as { state: EstadoNavegacion | null }
  const [resumenAbierto, setResumenAbierto] = useState(false)
  // La fecha se fija al montar: la API no la devuelve (PA-19).
  const [fecha] = useState(() => new Date())

  // Se puede llegar acá sin datos (recarga, enlace directo). No hay forma de
  // recuperarlos: la respuesta no trae identificador y no hay persistencia.
  if (!state?.analisis || !state.solicitud) {
    return <Navigate to="/" replace />
  }

  const { analisis, solicitud } = state
  const pct = porcentaje(analisis.probabilidad)
  const valores: Record<string, unknown> = { ...solicitud }

  return (
    <div className="col">
      <section className="block" aria-labelledby="t-veredicto">
        <p className="eyebrow" id="t-veredicto">Veredicto</p>
        <p className="verdict" data-cat={analisis.categoria}>
          <span className="verdict__icon" aria-hidden="true">{ICONO[analisis.categoria]}</span>
          <span className="verdict__text">{analisis.categoria}</span>
        </p>

        <div className="conf">
          <div className="conf__row">
            <span className="label">Confianza del modelo</span>
            <span className="conf__value">{pct} %</span>
          </div>
          <div
            className="conf__bar"
            role="progressbar"
            aria-label="Confianza del modelo"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={pct}
          >
            <span className="conf__fill" style={{ width: `${pct}%` }} />
          </div>
          <div className="ticks"><span>Baja</span><span>Alta</span></div>
        </div>

        <p className="help">{fechaLegible(fecha)}</p>
      </section>

      <section className="card cost" aria-labelledby="t-costo">
        <p className="eyebrow" id="t-costo">Costo estimado</p>
        <p className="cost__amount">{pesos(analisis.costo_estimado_mensual)} / mes</p>
        <p className="help">Tarifa de referencia: $ 0,75/kWh</p>
        <p className="cost__year">Proyección anual: {pesos(analisis.costo_estimado_mensual * 12)}</p>
      </section>

      {analisis.recomendaciones.length > 0 && (
        <section className="block" aria-labelledby="t-recos">
          <p className="eyebrow" id="t-recos">Recomendaciones</p>
          <ul className="recos">
            {analisis.recomendaciones.map((r) => <li key={r}>{r}</li>)}
          </ul>
        </section>
      )}

      <Desplegable
        titulo="Qué analizamos · 4 obligatorios + 7 opcionales"
        abierto={resumenAbierto}
        onToggle={setResumenAbierto}
        variante="plano"
      >
        <dl className="resumen">
          {CAMPOS.map((campo) => {
            const enviado = valores[campo.nombre] !== undefined
            const valor = enviado ? valores[campo.nombre] : ('defecto' in campo ? campo.defecto : undefined)

            const legible =
              campo.tipo === 'booleano' ? (valor ? 'Sí' : 'No')
                : campo.tipo === 'numero' && campo.unidad ? `${valor} ${campo.unidad}`
                  : campo.nombre === 'consumo_kwh' ? `${valor} kWh`
                    : String(valor)

            return (
              <div key={campo.nombre} style={{ display: 'contents' }}>
                <dt>{campo.etiqueta}</dt>
                <dd className={enviado ? undefined : 'is-default'}>
                  {legible}{enviado ? '' : ' · por defecto'}
                </dd>
              </div>
            )
          })}
        </dl>
      </Desplegable>

      <button type="button" className="btn btn--block" onClick={() => navegar('/')}>
        Nuevo análisis
      </button>
    </div>
  )
}

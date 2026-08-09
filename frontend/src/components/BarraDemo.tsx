import { useLayoutEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import type { ModoApi } from '../lib/api'
import type { ModoDemo } from '../lib/mock'

const RESPUESTAS: { valor: ModoDemo; etiqueta: string }[] = [
  { valor: 'ok', etiqueta: '200' },
  { valor: 'sin-recomendaciones', etiqueta: '200 sin recomendaciones' },
  { valor: '400', etiqueta: '400 del ML' },
  { valor: '500', etiqueta: '500' },
  { valor: '503', etiqueta: '503' },
]

interface Props {
  modoApi: ModoApi
  onCambiarModoApi: (modo: ModoApi) => void
  modoDemo: ModoDemo
  onCambiarModoDemo: (modo: ModoDemo) => void
}

/**
 * Panel de demostración. Permite mostrar cualquier estado sin depender de
 * que el back-end lo produzca justo cuando hace falta.
 *
 * El modo se cambia en vivo: con la API real conectada se puede pasar a
 * simulado, forzar un 503, y volver — sin reconstruir ni redesplegar.
 *
 * ⚠️ Es una herramienta de demostración. Antes de un lanzamiento real hay
 * que quitarla junto con lib/mock.ts, o dejarla detrás de un parámetro.
 */
export function BarraDemo({ modoApi, onCambiarModoApi, modoDemo, onCambiarModoDemo }: Props) {
  const navegar = useNavigate()
  const [abierta, setAbierta] = useState(true)
  const barra = useRef<HTMLElement>(null)

  // Reserva en el layout el alto real de la barra: es fija y en pantallas
  // angostas ocupa varias líneas, así que taparía el pie.
  //
  // Se mide de dos formas, y las dos hacen falta:
  //
  // - Por dependencia, después de cada repintado: cubre los cambios que
  //   provoca la propia barra (plegarla, cambiar de modo). Va en un
  //   useLayoutEffect para que el ajuste ocurra antes de que el navegador
  //   pinte y no se vea un salto.
  // - Con ResizeObserver: cubre lo que React no sabe, como que el texto se
  //   envuelva en otra línea al angostar la ventana. A 360 px la barra pasa
  //   de 44 a 120 px, y sin esto el pie quedaría tapado.
  useLayoutEffect(() => {
    const elemento = barra.current
    if (!elemento) return

    const reservar = (alto: number) => {
      document.documentElement.style.setProperty('--espacio-demo', `${Math.round(alto)}px`)
    }

    reservar(elemento.getBoundingClientRect().height)

    const observador = new ResizeObserver(([entrada]) => {
      reservar(entrada.borderBoxSize?.[0]?.blockSize ?? entrada.target.getBoundingClientRect().height)
    })
    observador.observe(elemento)

    // El valor no se limpia al desmontar: en modo estricto React monta,
    // desmonta y vuelve a montar, y borrarlo dejaría el layout sin reserva
    // hasta la siguiente medición.
    return () => observador.disconnect()
  }, [abierta, modoApi])

  return (
    <aside className="demobar" aria-label="Panel de demostración" ref={barra}>
      <div className="demobar__fila">
        <span className="demobar__tag">Demo</span>

        <div className="demobar__modos" role="group" aria-label="Origen de las respuestas">
          <button
            type="button"
            className={modoApi === 'real' ? 'chip is-on' : 'chip'}
            aria-pressed={modoApi === 'real'}
            onClick={() => onCambiarModoApi('real')}
          >
            API real
          </button>
          <button
            type="button"
            className={modoApi === 'mock' ? 'chip is-on' : 'chip'}
            aria-pressed={modoApi === 'mock'}
            onClick={() => onCambiarModoApi('mock')}
          >
            Simulado
          </button>
        </div>

        <button
          type="button"
          className="demobar__plegar"
          aria-expanded={abierta}
          onClick={() => setAbierta((a) => !a)}
        >
          {abierta ? 'Ocultar' : 'Mostrar opciones'}
        </button>
      </div>

      {abierta && (
        <div className="demobar__fila">
          {modoApi === 'mock' ? (
            <>
              <span className="demobar__hint">Forzar la próxima respuesta:</span>
              <div className="demobar__opts">
                {RESPUESTAS.map((r) => (
                  <button
                    key={r.valor}
                    type="button"
                    className={modoDemo === r.valor ? 'chip is-on' : 'chip'}
                    aria-pressed={modoDemo === r.valor}
                    onClick={() => onCambiarModoDemo(r.valor)}
                  >
                    {r.etiqueta}
                  </button>
                ))}
              </div>
            </>
          ) : (
            <span className="demobar__hint">
              Las respuestas vienen del back-end. Pasá a «Simulado» para forzar un estado.
            </span>
          )}

          <button
            type="button"
            className="chip"
            onClick={() => navegar('/ruta-que-no-existe')}
          >
            Ver 404
          </button>
        </div>
      )}
    </aside>
  )
}

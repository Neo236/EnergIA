/* ============================================================
   Cromo de la aplicación: navegación, pie y armazón.

   Van juntos porque en el sistema de diseño también van juntos — son el
   grupo «Cromo», la parte que no cambia entre pantallas.

   El armazón resuelve además dos cosas que una aplicación de una sola
   página no da gratis y un sitio con recarga completa sí:

   1. El scroll no vuelve arriba al navegar. Viniendo de un formulario
      largo, el resultado aparecería scrolleado a la mitad.
   2. El foco se queda donde estaba, así que un lector de pantalla no
      anuncia que cambió la página: sigue creyendo que está en el
      formulario. Mover el foco al contenido principal es lo que hace que
      la navegación sea perceptible sin ver la pantalla.
   ============================================================ */

import { useEffect, useRef } from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'

import { IconoRayo } from '../components/Iconos'

function Navegacion() {
  return (
    <header className="navegacion">
      <Link className="navegacion__marca" to="/">
        <span className="navegacion__logo" aria-hidden="true"><IconoRayo tamano={16} /></span>
        <span>Energi<span className="navegacion__marca-ai">AI</span></span>
      </Link>
      <Link className="navegacion__enlace" to="/">Analizar</Link>
      <Link className="navegacion__enlace" to="/historial">Historial</Link>
    </header>
  )
}

function Pie() {
  return (
    <footer className="pie">
      <span>Equipo G9 · Hackathon ONE</span>
      <span className="pie__enlaces">
        <a
          className="pie__enlace"
          href="https://github.com/No-Country-simulation/G9-LATAM-TEAM-09"
          target="_blank"
          rel="noreferrer"
        >Repositorio</a>
        <span aria-hidden="true">·</span>
        <a className="pie__enlace" href="/swagger-ui/index.html">API</a>
      </span>
    </footer>
  )
}

export function Layout() {
  const { pathname } = useLocation()
  const principal = useRef<HTMLElement>(null)

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' })
    principal.current?.focus({ preventScroll: true })
  }, [pathname])

  return (
    <div className="pagina">
      <Navegacion />
      {/* tabIndex -1: recibe el foco por código, pero no entra en el
          recorrido del tabulador. */}
      <main className="pagina__centro" tabIndex={-1} ref={principal}>
        <Outlet />
      </main>
      <Pie />
    </div>
  )
}

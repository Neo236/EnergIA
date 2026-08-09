import { useEffect, useRef } from 'react'
import { Outlet, useLocation } from 'react-router-dom'

import { Navbar } from './Navbar'
import { Footer } from './Footer'

/**
 * Navbar y pie son comunes a todas las rutas; solo cambia el centro.
 *
 * Además resuelve dos cosas que en una aplicación de una sola página no
 * pasan solas, y que un sitio con recarga completa daría gratis:
 *
 * 1. El scroll no vuelve arriba al navegar. Viniendo de un formulario
 *    largo, el resultado aparecería scrolleado a la mitad.
 * 2. El foco se queda donde estaba, así que un lector de pantalla no
 *    anuncia que cambió la página: sigue creyendo que está en el
 *    formulario. Mover el foco al contenido principal es lo que hace que
 *    la navegación sea perceptible sin ver la pantalla.
 */
export function Layout() {
  const { pathname } = useLocation()
  const principal = useRef<HTMLElement>(null)

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' })
    principal.current?.focus({ preventScroll: true })
  }, [pathname])

  return (
    <>
      <Navbar />
      {/* tabIndex -1: recibe el foco por código, pero no entra en el
          recorrido del tabulador. */}
      <main className="page" tabIndex={-1} ref={principal}>
        <Outlet />
      </main>
      <Footer />
    </>
  )
}

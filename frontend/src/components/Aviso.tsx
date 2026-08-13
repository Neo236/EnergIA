/* ============================================================
   Tarjeta de aviso.

   Sirve en dos situaciones que el diseño resuelve con la misma pieza:
   encabezando el formulario cuando el envío falló (Error 500 / 503), y
   como pantalla completa cuando no hay nada que mostrar (404, análisis
   inexistente).

   El tono lo decide `advertencia`: ámbar para lo pasajero — no hay
   conexión, el servicio no responde — y rojo para lo que falló de verdad.
   Nunca se comunica solo con color: el icono cambia de forma junto con él.
   ============================================================ */

import type { ReactNode } from 'react'

import { IconoAlerta, IconoCirculo } from './Iconos'

interface Props {
  titulo: string
  texto: string
  advertencia?: boolean
  children?: ReactNode
}

export function Aviso({ titulo, texto, advertencia = false, children }: Props) {
  const Icono = advertencia ? IconoCirculo : IconoAlerta

  return (
    <section className={`aviso${advertencia ? ' aviso--advertencia' : ''}`} role="alert">
      <div className="aviso__cabecera">
        <span className="aviso__icono">
          <Icono />
        </span>
        <h2 className="aviso__titulo">{titulo}</h2>
      </div>
      <p className="aviso__texto">{texto}</p>
      {children}
    </section>
  )
}

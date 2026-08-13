/* ============================================================
   Botón.

   Espejo del componente `Boton` del sistema: tres tipos × cuatro estados.
   Los estados no son propiedades acá: `hover`, `foco` e `inactivo` los
   resuelve CSS con :hover, :focus-visible y :disabled, que es como el
   navegador ya los conoce. La propiedad `tipo` es la única que viaja.
   ============================================================ */

import type { ButtonHTMLAttributes, ReactNode } from 'react'

type Tipo = 'primario' | 'secundario' | 'terciario'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  tipo?: Tipo
  ancho?: boolean
  children: ReactNode
}

export function Boton({ tipo = 'primario', ancho = false, className, children, ...resto }: Props) {
  const clases = ['boton', `boton--${tipo}`]
  if (ancho) clases.push('boton--ancho')
  if (className) clases.push(className)

  return (
    <button type="button" className={clases.join(' ')} {...resto}>
      {children}
    </button>
  )
}

import { useEffect } from 'react'

const BASE = 'EnergiAI'

/**
 * En una aplicación de una sola página el título no cambia solo. Con
 * varias pestañas abiertas todas dirían lo mismo, y en el 404 el título
 * seguiría afirmando que todo está bien.
 */
export function useTitulo(seccion?: string) {
  useEffect(() => {
    document.title = seccion ? `${seccion} · ${BASE}` : BASE
  }, [seccion])
}

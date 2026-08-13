import { Route, Routes } from 'react-router-dom'

import { Layout } from './layout/Layout'
import { Analizar } from './pages/Analizar'
import { Historial } from './pages/Historial'
import { Resultado } from './pages/Resultado'
import { NoEncontrado } from './pages/NoEncontrado'

/**
 * Cuatro rutas, una por pantalla del diseño:
 *   /              P-01 ingreso de datos
 *   /analisis/:id  P-02 resultado, con URL propia y compartible
 *   /historial     P-03 historial local de análisis
 *   *              P-04 la dirección no existe
 *
 * El caso «el análisis no está» no es una ruta aparte: es un estado de
 * /analisis/:id, porque la URL es válida y lo que falta es el contenido.
 */
export function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Analizar />} />
        <Route path="analisis/:id" element={<Resultado />} />
        <Route path="historial" element={<Historial />} />
        <Route path="*" element={<NoEncontrado />} />
      </Route>
    </Routes>
  )
}

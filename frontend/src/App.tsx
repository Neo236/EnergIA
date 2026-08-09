import { useState } from 'react'
import { Route, Routes } from 'react-router-dom'

import { Layout } from './layout/Layout'
import { Analizar } from './pages/Analizar'
import { Resultado } from './pages/Resultado'
import { NoEncontrado } from './pages/NoEncontrado'
import { BarraDemo } from './components/BarraDemo'
import { MODO_INICIAL, type ModoApi } from './lib/api'
import type { ModoDemo } from './lib/mock'

export function App() {
  // Viven acá y no en la página para que sobrevivan a la navegación.
  const [modoApi, setModoApi] = useState<ModoApi>(MODO_INICIAL)
  const [modoDemo, setModoDemo] = useState<ModoDemo>('ok')

  return (
    <>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Analizar modoApi={modoApi} modoDemo={modoDemo} />} />
          <Route path="resultado" element={<Resultado />} />
          <Route path="analisis/:id" element={<NoEncontrado />} />
          <Route path="*" element={<NoEncontrado />} />
        </Route>
      </Routes>

      <BarraDemo
        modoApi={modoApi}
        onCambiarModoApi={setModoApi}
        modoDemo={modoDemo}
        onCambiarModoDemo={setModoDemo}
      />
    </>
  )
}

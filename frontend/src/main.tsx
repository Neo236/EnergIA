import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'

import { App } from './App'
import { LimiteDeError } from './components/LimiteDeError'
import './styles/tokens.css'
import './styles/app.css'

const contenedor = document.getElementById('root')
if (!contenedor) throw new Error('No se encontró el elemento #root')

createRoot(contenedor).render(
  <StrictMode>
    <LimiteDeError>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </LimiteDeError>
  </StrictMode>,
)

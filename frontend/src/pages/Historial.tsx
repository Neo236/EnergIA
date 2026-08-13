/* ============================================================
   P-03 · Historial de análisis.

   Lista los análisis guardados en localStorage, ordenados del más
   reciente al más antiguo. Cada entrada tiene un link directo al
   resultado (/analisis/:id) y un botón para eliminarla del historial.

   El historial es local al browser: si el usuario cambia de dispositivo
   o limpia el almacenamiento, desaparece. La URL del resultado sigue
   funcionando siempre que el análisis exista en la base de datos.
   ============================================================ */

import { useState } from 'react'
import { Link } from 'react-router-dom'

import { Aviso } from '../components/Aviso'
import { Boton } from '../components/Boton'
import { fechaLegible, fechaRelativa, pesos } from '../lib/formato'
import { useHistorial, type EntradaHistorial } from '../lib/historial'
import type { Categoria } from '../lib/contrato'

const BADGE_CLASE: Record<Categoria, string> = {
  Eficiente:   'historial__badge historial__badge--eficiente',
  Moderado:    'historial__badge historial__badge--moderado',
  Ineficiente: 'historial__badge historial__badge--ineficiente',
}

function IconoX() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
      <path d="M11 3L3 11M3 3l8 8" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" />
    </svg>
  )
}

interface ItemProps {
  entrada: EntradaHistorial
  onBorrar: () => void
}

function ItemHistorial({ entrada, onBorrar }: ItemProps) {
  const [confirmando, setConfirmando] = useState(false)

  return (
    <li className="tarjeta historial__item">
      <div className="historial__item-principal">
        <span className={BADGE_CLASE[entrada.categoria]}>{entrada.categoria}</span>
        <span className="historial__fecha">{fechaRelativa(entrada.fecha)}</span>
        <span className="historial__costo">{pesos(entrada.costo_estimado_mensual)} / mes</span>
      </div>

      <div className="historial__item-acciones">
        <Link to={`/analisis/${entrada.id}`}>
          <Boton tipo="secundario">Ver resultado</Boton>
        </Link>

        {confirmando ? (
          <span className="historial__inline-confirmacion">
            <button
              type="button"
              className="historial__accion-texto historial__accion-texto--destructivo"
              onClick={() => { onBorrar(); setConfirmando(false) }}
            >
              Eliminar
            </button>
            <span aria-hidden="true"> · </span>
            <button
              type="button"
              className="historial__accion-texto"
              onClick={() => setConfirmando(false)}
            >
              Cancelar
            </button>
          </span>
        ) : (
          <button
            type="button"
            className="historial__borrar-entrada"
            aria-label={`Eliminar del historial: análisis del ${fechaLegible(entrada.fecha)}`}
            title="Eliminar del historial"
            onClick={() => setConfirmando(true)}
          >
            <IconoX />
          </button>
        )}
      </div>
    </li>
  )
}

export function Historial() {
  const { entradas, borrarEntrada, borrarTodo } = useHistorial()
  const [confirmandoBorrarTodo, setConfirmandoBorrarTodo] = useState(false)

  if (entradas.length === 0) {
    return (
      <div className="columna columna--aviso">
        <Aviso
          titulo="Sin análisis guardados"
          texto="Tus próximos análisis aparecerán acá, ordenados del más reciente al más antiguo."
          advertencia
        >
          <Link to="/"><Boton tipo="primario" ancho>Hacer un análisis</Boton></Link>
        </Aviso>
      </div>
    )
  }

  return (
    <div className="columna">
      <div className="historial">
        <div className="historial__cabecera">
          <h1 className="titulo-hero">Historial</h1>
          <p className="bajada">
            {entradas.length} {entradas.length === 1 ? 'análisis guardado' : 'análisis guardados'}
          </p>
        </div>

        <ul className="historial__lista">
          {entradas.map((entrada) => (
            <ItemHistorial
              key={entrada.id}
              entrada={entrada}
              onBorrar={() => borrarEntrada(entrada.id)}
            />
          ))}
        </ul>

        <div className="historial__pie">
          {confirmandoBorrarTodo ? (
            <span className="historial__inline-confirmacion historial__inline-confirmacion--pie">
              <span className="historial__confirmacion-texto">¿Borrar todo el historial?</span>
              <button
                type="button"
                className="historial__accion-texto historial__accion-texto--destructivo"
                onClick={() => { borrarTodo(); setConfirmandoBorrarTodo(false) }}
              >
                Sí, borrar todo
              </button>
              <span aria-hidden="true"> · </span>
              <button
                type="button"
                className="historial__accion-texto"
                onClick={() => setConfirmandoBorrarTodo(false)}
              >
                Cancelar
              </button>
            </span>
          ) : (
            <button
              type="button"
              className="historial__accion-texto historial__borrar-todo"
              onClick={() => setConfirmandoBorrarTodo(true)}
            >
              Borrar historial
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

/* ============================================================
   P-03 · Historial de análisis.

   Lista los análisis guardados en localStorage, ordenados del más
   reciente al más antiguo. Cada entrada tiene un link directo al
   resultado (/analisis/:id) y una casilla para seleccionarla.

   Borrado unificado en un solo mecanismo: seleccionar (o no) y confirmar.
   Sin selección, "Borrar historial" borra todo. Con selección, se
   convierte en "Borrar (N)" y borra solo lo tildado. Las dos rutas piden
   confirmación de la misma manera.

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

interface ItemProps {
  entrada: EntradaHistorial
  seleccionado: boolean
  onCambiarSeleccion: () => void
}

function ItemHistorial({ entrada, seleccionado, onCambiarSeleccion }: ItemProps) {
  return (
    <li className="tarjeta historial__item">
      <div className="historial__item-contenido">
        <label className="historial__seleccionar">
          <input
            type="checkbox"
            className="historial__casilla"
            checked={seleccionado}
            onChange={onCambiarSeleccion}
            aria-label={`Seleccionar análisis del ${fechaLegible(entrada.fecha)}`}
          />
        </label>

        <div className="historial__item-principal">
          <span className={BADGE_CLASE[entrada.categoria]}>{entrada.categoria}</span>
          <span className="historial__fecha">{fechaRelativa(entrada.fecha)}</span>
          <span className="historial__costo">{pesos(entrada.costo_estimado_mensual)} / mes</span>
        </div>
      </div>

      <div className="historial__item-acciones">
        <Link to={`/analisis/${entrada.id}`}>
          <Boton tipo="secundario">Ver resultado</Boton>
        </Link>
      </div>
    </li>
  )
}

export function Historial() {
  const { entradas, borrarSeleccionadas, borrarTodo } = useHistorial()
  const [seleccionados, setSeleccionados] = useState<Set<string>>(new Set())
  const [confirmando, setConfirmando] = useState(false)

  function alternarSeleccion(id: string): void {
    setSeleccionados((previos) => {
      const siguientes = new Set(previos)
      if (siguientes.has(id)) siguientes.delete(id)
      else siguientes.add(id)
      return siguientes
    })
  }

  function confirmar(): void {
    if (seleccionados.size > 0) {
      borrarSeleccionadas(seleccionados)
      setSeleccionados(new Set())
    } else {
      borrarTodo()
    }
    setConfirmando(false)
  }

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

  const cantidadSeleccionada = seleccionados.size
  const haySeleccion = cantidadSeleccionada > 0

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
              seleccionado={seleccionados.has(entrada.id)}
              onCambiarSeleccion={() => alternarSeleccion(entrada.id)}
            />
          ))}
        </ul>

        <div className="historial__pie">
          {confirmando ? (
            <span className="historial__inline-confirmacion historial__inline-confirmacion--pie">
              <span className="historial__confirmacion-texto">
                {haySeleccion
                  ? `¿Borrar ${cantidadSeleccionada} ${cantidadSeleccionada === 1 ? 'análisis seleccionado' : 'análisis seleccionados'}?`
                  : '¿Borrar todo el historial?'}
              </span>
              <button
                type="button"
                className="historial__accion-texto historial__accion-texto--destructivo"
                onClick={confirmar}
              >
                {haySeleccion ? 'Sí, borrar' : 'Sí, borrar todo'}
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
              className="historial__accion-texto historial__borrar-todo"
              onClick={() => setConfirmando(true)}
            >
              {haySeleccion ? `Borrar (${cantidadSeleccionada})` : 'Borrar historial'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

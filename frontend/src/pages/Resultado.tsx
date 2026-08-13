/* ============================================================
   P-02 · Resultado del análisis.

   Vive en /analisis/{id}. Si se llega desde el formulario, el análisis
   viaja en el estado de la navegación y se pinta sin esperar; si se llega
   por un enlace pegado o tras recargar, se pide al back-end.

   Esa es la diferencia de fondo con la versión anterior del front: el
   resultado dejó de existir solo en memoria y pasó a tener URL propia.
   ============================================================ */

import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'

import { Aviso } from '../components/Aviso'
import { Boton } from '../components/Boton'
import { Acordeon } from '../components/Campos'
import { IconoAlerta, IconoTilde } from '../components/Iconos'
import { obtenerAnalisis } from '../lib/api'
import { registrarEnHistorial } from '../lib/historial'
import { TARIFA_KWH, ErrorApi, type Analisis, type Categoria } from '../lib/contrato'
import { fechaRelativa, pesos, porcentaje } from '../lib/formato'
import { textoDeAnalisisAusente, type TextoAviso } from '../lib/mensajes'

const CLASE_POR_CATEGORIA: Record<Categoria, string> = {
  Eficiente: 'veredicto--eficiente',
  Moderado: 'veredicto--moderado',
  Ineficiente: 'veredicto--ineficiente',
}

function IconoDeVeredicto({ categoria }: { categoria: Categoria }) {
  /* Un triángulo de advertencia sobre un veredicto positivo diría lo
     contrario de lo que el veredicto afirma. */
  return categoria === 'Eficiente' ? <IconoTilde /> : <IconoAlerta />
}

export function Resultado() {
  const { id = '' } = useParams()
  const ubicacion = useLocation()
  const precargado = (ubicacion.state as { analisis?: Analisis } | null)?.analisis

  const [analisis, setAnalisis] = useState<Analisis | null>(
    precargado && precargado.id === id ? precargado : null,
  )
  const [fallo, setFallo] = useState<TextoAviso | null>(null)
  const [cargando, setCargando] = useState(!analisis)

  useEffect(() => {
    if (analisis || !id) return
    let vigente = true

    setCargando(true)
    obtenerAnalisis(id)
      .then((datos) => { if (vigente) setAnalisis(datos) })
      .catch((error) => {
        if (!vigente) return
        const status = error instanceof ErrorApi ? error.respuesta.status : 500
        setFallo(textoDeAnalisisAusente(status))
      })
      .finally(() => { if (vigente) setCargando(false) })

    return () => { vigente = false }
  }, [id, analisis])

  /* Registrar en historial local cada vez que tengamos el análisis,
     independientemente de si llegó por precarga o por fetch. */
  useEffect(() => {
    if (analisis) registrarEnHistorial(analisis)
  }, [analisis])

  if (cargando) {
    return (
      <div className="columna columna--aviso">
        <p className="resultado__aviso" role="status">Buscando el análisis...</p>
      </div>
    )
  }

  if (fallo || !analisis) {
    const texto = fallo ?? textoDeAnalisisAusente(404)
    return (
      <div className="columna columna--aviso">
        <Aviso titulo={texto.titulo} texto={texto.texto} advertencia={texto.advertencia}>
          <Link to="/"><Boton tipo="primario" ancho>Hacer un análisis</Boton></Link>
        </Aviso>
      </div>
    )
  }

  const confianza = porcentaje(analisis.probabilidad)
  const anual = analisis.costo_estimado_mensual * 12

  return (
    <div className="columna columna--resultado">
      <div className="resultado">
        <h1 className="rotulo">Resultado del análisis</h1>

        <div className="resultado__grilla">
          <div className="resultado__columna">
            <section className={`veredicto ${CLASE_POR_CATEGORIA[analisis.categoria]}`}>
              <div className="veredicto__fila">
                <span className="veredicto__icono"><IconoDeVeredicto categoria={analisis.categoria} /></span>
                <h2 className="veredicto__etiqueta">{analisis.categoria.toUpperCase()}</h2>
              </div>
              <p className="veredicto__texto">
                El modelo clasificó tu consumo como {analisis.categoria.toLowerCase()} a partir de los
                datos que ingresaste.
              </p>
            </section>

            <section className="confianza">
              <div className="confianza__fila">
                <h3 className="confianza__etiqueta">Confianza del modelo</h3>
                <span className="confianza__valor">{confianza} %</span>
              </div>
              <div
                className="confianza__pista"
                role="meter"
                aria-valuenow={confianza} aria-valuemin={0} aria-valuemax={100}
                aria-label="Confianza del modelo"
              >
                <div className="confianza__barra" style={{ width: `${confianza}%` }} />
              </div>
              <p className="confianza__ayuda">Indica qué tan seguro está el modelo de esta clasificación.</p>
            </section>

            <section className="tarjeta costo">
              <div className="costo__cabecera">
                <span className="costo__acento" aria-hidden="true" />
                <div>
                  <p className="costo__rotulo">Costo estimado</p>
                  <p className="costo__monto">{pesos(analisis.costo_estimado_mensual)} / mes</p>
                </div>
              </div>
              <div className="costo__detalles">
                <div className="costo__detalle">
                  <span className="costo__detalle-rotulo">Tarifa de referencia</span>
                  <span className="costo__detalle-valor">{pesos(TARIFA_KWH)} / kWh</span>
                </div>
                <div className="costo__detalle">
                  <span className="costo__detalle-rotulo">Proyección anual estimada</span>
                  <span className="costo__detalle-valor costo__detalle-valor--destacado">{pesos(anual)} / año</span>
                </div>
              </div>
            </section>
          </div>

          <div className="resultado__columna">
            <section className="tarjeta recomendaciones">
              <h3 className="rotulo">Recomendaciones</h3>
              {analisis.recomendaciones.length > 0
                ? (
                  <ul className="recomendaciones__lista">
                    {analisis.recomendaciones.map((texto, i) => (
                      <li className="recomendaciones__item" key={i}>
                        <span className="recomendaciones__vineta" aria-hidden="true">•</span>
                        <span>{texto}</span>
                      </li>
                    ))}
                  </ul>
                )
                : (
                  <p className="recomendaciones__vacio">
                    No tenemos recomendaciones específicas para este perfil. Completa los datos
                    adicionales del formulario para obtener un análisis más preciso.
                  </p>
                )}
            </section>

            <DatosUsados />

            <p className="resultado__aviso">
              {fechaRelativa(analisis.fecha)} · Guarda el enlace de esta página para volver al resultado
            </p>

            <Link to="/"><Boton tipo="secundario" ancho>Nuevo análisis</Boton></Link>
            <Link to="/historial"><Boton tipo="terciario" ancho>Ver historial</Boton></Link>
          </div>
        </div>
      </div>
    </div>
  )
}

/** El diseño deja este acordeón cerrado; el contenido explica de dónde sale el veredicto. */
function DatosUsados() {
  const [abierto, setAbierto] = useState(false)
  return (
    <Acordeon
      titulo="Qué datos usamos para este análisis"
      abierto={abierto}
      onAlternar={() => setAbierto((v) => !v)}
    >
      <p className="acordeon__nota">
        El veredicto se calcula con los cuatro datos obligatorios —consumo mensual, tipo de inmueble,
        cantidad de equipos y horas de alto consumo— más los siete opcionales que hayas completado.
        Los que dejaste vacíos se reemplazan por el valor por defecto de cada campo.
      </p>
    </Acordeon>
  )
}

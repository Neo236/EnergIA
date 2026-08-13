/* ============================================================
   P-01 · Ingreso de datos.

   Una sola pantalla con cuatro estados, tal como el diseño los plantea:
   inicial, validación con errores, datos adicionales desplegado, y
   enviando (el formulario intacto detrás de un velo).

   Al enviar con éxito se navega a /analisis/{id}. El análisis viaja en el
   estado de la navegación para que el resultado se pinte al instante, pero
   la URL basta por sí sola: quien la abra de nuevo lo trae del back-end.
   ============================================================ */

import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import { Aviso } from '../components/Aviso'
import { Boton } from '../components/Boton'
import { Cargando } from '../components/Cargando'
import {
  Acordeon, CampoContador, CampoDeslizador, CampoDesplegable,
  CampoInterruptor, CampoOpciones, CampoTexto,
} from '../components/Campos'
import { analizar } from '../lib/api'
import {
  CALIDADES_AISLAMIENTO, CAMPOS_OPCIONALES, CAMPOS_REQUERIDOS, FUENTES_ENERGIA,
  TIPOS_INMUEBLE, VALORES_INICIALES, ErrorApi, defectoComoPlaceholder,
  type CalidadAislamiento, type FuenteEnergia, type Solicitud, type TipoInmueble,
} from '../lib/contrato'
import { mensajeDeCampo, textoDeAviso, type TextoAviso } from '../lib/mensajes'

type Errores = Partial<Record<keyof Solicitud, string>>

/** Los campos opcionales, para saber si hay que abrir el acordeón al fallar. */
const NOMBRES_OPCIONALES = CAMPOS_OPCIONALES.map((c) => c.nombre)

function campoPorNombre(nombre: keyof Solicitud) {
  return [...CAMPOS_REQUERIDOS, ...CAMPOS_OPCIONALES].find((c) => c.nombre === nombre)!
}

export function Analizar() {
  const navegar = useNavigate()

  /* --- obligatorios: arrancan con los valores del diseño --- */
  const [consumo, setConsumo] = useState<string>(VALORES_INICIALES.consumo_kwh)
  const [tipo, setTipo] = useState<TipoInmueble>(VALORES_INICIALES.tipo_inmueble)
  const [equipos, setEquipos] = useState<number>(VALORES_INICIALES.cantidad_equipos)
  const [horas, setHoras] = useState<number>(VALORES_INICIALES.horas_alto_consumo)

  /* --- opcionales: vacíos, porque no completarlos es la opción válida --- */
  const [metros, setMetros] = useState('')
  const [antiguedad, setAntiguedad] = useState('')
  const [zonaFria, setZonaFria] = useState(false)
  const [aislamiento, setAislamiento] = useState<CalidadAislamiento>('Media')
  const [calefaccion, setCalefaccion] = useState<FuenteEnergia>('Electricidad')
  const [agua, setAgua] = useState<FuenteEnergia>('Electricidad')
  const [horarioPico, setHorarioPico] = useState(false)

  const [opcionalesAbiertos, setOpcionalesAbiertos] = useState(false)
  const [errores, setErrores] = useState<Errores>({})
  const [aviso, setAviso] = useState<TextoAviso | null>(null)
  const [enviando, setEnviando] = useState(false)

  const cantidadErrores = Object.keys(errores).length

  /** Valida contra los rangos del contrato antes de gastar una llamada. */
  function validar(): { errores: Errores; solicitud: Solicitud | null } {
    const e: Errores = {}

    const nConsumo = Number(consumo.replace(',', '.'))
    if (consumo.trim() === '' || Number.isNaN(nConsumo) || nConsumo < 1 || nConsumo > 1000) {
      e.consumo_kwh = mensajeDeCampo('consumo_kwh', 'Valor fuera de rango')
    }
    if (equipos < 1 || equipos > 100) {
      e.cantidad_equipos = mensajeDeCampo('cantidad_equipos', 'Valor fuera de rango')
    }
    if (horas < 0 || horas > 24) {
      e.horas_alto_consumo = mensajeDeCampo('horas_alto_consumo', 'Valor fuera de rango')
    }

    const nMetros = metros.trim() === '' ? undefined : Number(metros)
    if (nMetros !== undefined && (Number.isNaN(nMetros) || nMetros < 26 || nMetros > 2000)) {
      e.metros_cuadrados = mensajeDeCampo('metros_cuadrados', 'Valor fuera de rango')
    }
    const nAntiguedad = antiguedad.trim() === '' ? undefined : Number(antiguedad)
    if (nAntiguedad !== undefined && (Number.isNaN(nAntiguedad) || nAntiguedad < 0 || nAntiguedad > 150)) {
      e.antiguedad_vivienda = mensajeDeCampo('antiguedad_vivienda', 'Valor fuera de rango')
    }

    if (Object.keys(e).length > 0) return { errores: e, solicitud: null }

    /* Los opcionales solo viajan si se completaron: omitirlos es lo que
       hace que el back aplique su propio valor por defecto. */
    const solicitud: Solicitud = {
      consumo_kwh: nConsumo,
      tipo_inmueble: tipo,
      cantidad_equipos: equipos,
      horas_alto_consumo: horas,
      ...(nMetros !== undefined ? { metros_cuadrados: nMetros } : {}),
      ...(nAntiguedad !== undefined ? { antiguedad_vivienda: nAntiguedad } : {}),
      zona_fria: zonaFria,
      calidad_aislamiento: aislamiento,
      fuente_calefaccion: calefaccion,
      fuente_agua_caliente: agua,
      uso_horario_pico: horarioPico,
    }
    return { errores: {}, solicitud }
  }

  /* El evento es opcional: el mismo envío lo dispara el formulario y el
     botón «Reintentar» del aviso, que no está dentro de un <form>. */
  async function enviar(evento?: FormEvent) {
    evento?.preventDefault()
    setAviso(null)

    const { errores: e, solicitud } = validar()
    if (!solicitud) {
      setErrores(e)
      if (Object.keys(e).some((c) => NOMBRES_OPCIONALES.includes(c as keyof Solicitud))) {
        setOpcionalesAbiertos(true)
      }
      return
    }

    setErrores({})
    setEnviando(true)
    try {
      const analisis = await analizar(solicitud)
      navegar(`/analisis/${analisis.id}`, { state: { analisis } })
    } catch (error) {
      if (error instanceof ErrorApi) {
        const detalles = error.respuesta.detalles
        if (detalles?.length) {
          const porCampo: Errores = {}
          for (const d of detalles) {
            porCampo[d.campo as keyof Solicitud] = mensajeDeCampo(d.campo, d.mensaje)
          }
          setErrores(porCampo)
          if (detalles.some((d) => NOMBRES_OPCIONALES.includes(d.campo as keyof Solicitud))) {
            setOpcionalesAbiertos(true)
          }
        } else {
          setAviso(textoDeAviso(error.respuesta.status))
        }
      } else {
        setAviso(textoDeAviso(500))
      }
    } finally {
      setEnviando(false)
    }
  }

  return (
    <>
      <div className="columna">
        {aviso && (
          <Aviso titulo={aviso.titulo} texto={aviso.texto} advertencia={aviso.advertencia}>
            <Boton tipo="primario" ancho onClick={() => void enviar()}>
              Reintentar
            </Boton>
          </Aviso>
        )}

        <section className="seccion-intro">
          {cantidadErrores > 0
            ? <span className="insignia insignia--alerta">
                {cantidadErrores === 1 ? '1 campo con errores' : `${cantidadErrores} campos con errores`}
              </span>
            : <span className="insignia">Uso libre · sin registro</span>}

          <h1 className="titulo-hero">Descubre cuánto puedes ahorrar en tu factura de luz</h1>
          <p className="bajada">
            Completa cuatro datos obligatorios —y, si quieres, siete opcionales— y recibe tu perfil
            energético, el costo estimado y recomendaciones.
          </p>
        </section>

        <form className="tarjeta-formulario" onSubmit={enviar} noValidate>
          <p className="rotulo">Formulario de consumo</p>

          <div className="formulario__filas">
            <CampoTexto
              etiqueta="Consumo mensual"
              valor={consumo} onCambio={setConsumo}
              unidad="kWh" decimal requerido
              ayuda={campoPorNombre('consumo_kwh').ayuda}
              error={errores.consumo_kwh}
            />

            <CampoOpciones
              etiqueta="Tipo de inmueble"
              valores={TIPOS_INMUEBLE}
              valor={tipo} onCambio={(v) => setTipo(v as TipoInmueble)}
              etiquetasCortas={{ Departamento: 'Depto.' }}
              requerido
              error={errores.tipo_inmueble}
            />

            <div className="formulario__par">
              <CampoContador
                etiqueta="Cantidad de equipos"
                valor={equipos} onCambio={setEquipos}
                min={1} max={100} requerido
                ayuda={campoPorNombre('cantidad_equipos').ayuda}
                error={errores.cantidad_equipos}
              />
              <CampoDeslizador
                etiqueta="Horas de alto consumo por día"
                valor={horas} onCambio={setHoras}
                min={0} max={24} unidad="h" requerido
                error={errores.horas_alto_consumo}
              />
            </div>

            <Acordeon
              titulo="Datos adicionales (opcional)"
              insignia="7 campos"
              nota="Mejoran la precisión · Si no los completas, se usan los valores por defecto de cada campo."
              abierto={opcionalesAbiertos}
              onAlternar={() => setOpcionalesAbiertos((v) => !v)}
            >
              <div className="grilla-opcionales">
                <CampoTexto
                  etiqueta="Metros cuadrados"
                  valor={metros} onCambio={setMetros} unidad="m²"
                  placeholder={defectoComoPlaceholder('metros_cuadrados')}
                  ayuda={campoPorNombre('metros_cuadrados').ayuda}
                  error={errores.metros_cuadrados}
                />
                <CampoTexto
                  etiqueta="Antigüedad de la vivienda"
                  valor={antiguedad} onCambio={setAntiguedad} unidad="años"
                  placeholder={defectoComoPlaceholder('antiguedad_vivienda')}
                  ayuda={campoPorNombre('antiguedad_vivienda').ayuda}
                  error={errores.antiguedad_vivienda}
                />
                <CampoInterruptor
                  etiqueta="Zona fría"
                  valor={zonaFria} onCambio={setZonaFria}
                  ayuda={campoPorNombre('zona_fria').ayuda}
                />
                <CampoDesplegable
                  etiqueta="Calidad del aislamiento"
                  valores={CALIDADES_AISLAMIENTO} defecto="Media"
                  valor={aislamiento} onCambio={(v) => setAislamiento(v as CalidadAislamiento)}
                  error={errores.calidad_aislamiento}
                />
                <CampoDesplegable
                  etiqueta="Fuente de calefacción"
                  valores={FUENTES_ENERGIA} defecto="Electricidad"
                  valor={calefaccion} onCambio={(v) => setCalefaccion(v as FuenteEnergia)}
                  error={errores.fuente_calefaccion}
                />
                <CampoDesplegable
                  etiqueta="Fuente de agua caliente"
                  valores={FUENTES_ENERGIA} defecto="Electricidad"
                  valor={agua} onCambio={(v) => setAgua(v as FuenteEnergia)}
                  error={errores.fuente_agua_caliente}
                />
                <CampoInterruptor
                  etiqueta="Uso en horario pico"
                  valor={horarioPico} onCambio={setHorarioPico}
                  ayuda={campoPorNombre('uso_horario_pico').ayuda}
                />
              </div>
            </Acordeon>
          </div>

          <Boton tipo="primario" ancho type="submit" disabled={enviando}>
            {enviando ? 'Analizando...' : 'Analizar mi consumo'}
          </Boton>
        </form>

        <section className="seccion-como-funciona">
          <h2 className="rotulo">Cómo funciona</h2>
          <ol className="lista-pasos">
            <li className="paso">
              <span className="paso__numero" aria-hidden="true">1</span>
              <span>
                <span className="paso__titulo">Ingresas tus datos</span><br />
                <span className="paso__texto">Solo necesitas el total de kWh de tu factura</span>
              </span>
            </li>
            <li className="paso">
              <span className="paso__numero" aria-hidden="true">2</span>
              <span>
                <span className="paso__titulo">El modelo los analiza</span><br />
                <span className="paso__texto">Clasifica tu perfil de consumo</span>
              </span>
            </li>
            <li className="paso">
              <span className="paso__numero" aria-hidden="true">3</span>
              <span>
                <span className="paso__titulo">Recibes tu resultado</span><br />
                <span className="paso__texto">Veredicto, costo estimado y recomendaciones</span>
              </span>
            </li>
          </ol>
        </section>
      </div>

      {enviando && <Cargando />}
    </>
  )
}

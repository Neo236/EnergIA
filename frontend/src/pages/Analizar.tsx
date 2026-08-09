import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { analizar, type ModoApi } from '../lib/api'
import { ErrorApi, type RespuestaError, type Solicitud, type TipoInmueble, type CalidadAislamiento, type FuenteEnergia } from '../lib/contrato'
import { mensajeDeCampo } from '../lib/mensajes'
import { useTitulo } from '../lib/useTitulo'
import type { ModoDemo } from '../lib/mock'
import { Aviso } from '../components/Aviso'
import { Desplegable } from '../components/Desplegable'
import { Deslizador, EntradaNumero, Interruptor, Seleccion, Stepper, TarjetasOpcion } from '../components/Controles'
import { CALIDADES_AISLAMIENTO, FUENTES_ENERGIA, TIPOS_INMUEBLE } from '../lib/contrato'

/** Los numéricos viven como texto: distingue "vacío" de 0 y deja que valide el back. */
interface Formulario {
  consumo_kwh: string
  tipo_inmueble: string
  cantidad_equipos: string
  horas_alto_consumo: number
  metros_cuadrados: string
  antiguedad_vivienda: string
  zona_fria: boolean
  calidad_aislamiento: string
  fuente_calefaccion: string
  fuente_agua_caliente: string
  uso_horario_pico: boolean
}

const INICIAL: Formulario = {
  consumo_kwh: '',
  tipo_inmueble: 'Casa',
  cantidad_equipos: '10',
  horas_alto_consumo: 12,
  metros_cuadrados: '',
  antiguedad_vivienda: '',
  zona_fria: false,
  calidad_aislamiento: '',
  fuente_calefaccion: '',
  fuente_agua_caliente: '',
  uso_horario_pico: false,
}

/** Arma el payload mínimo: los obligatorios y solo los opcionales que se tocaron. */
function aSolicitud(f: Formulario): Solicitud {
  const s: Solicitud = {
    consumo_kwh: f.consumo_kwh === '' ? (undefined as unknown as number) : Number(f.consumo_kwh),
    tipo_inmueble: f.tipo_inmueble as TipoInmueble,
    cantidad_equipos: f.cantidad_equipos === '' ? (undefined as unknown as number) : Number(f.cantidad_equipos),
    horas_alto_consumo: f.horas_alto_consumo,
  }
  if (f.metros_cuadrados !== '') s.metros_cuadrados = Number(f.metros_cuadrados)
  if (f.antiguedad_vivienda !== '') s.antiguedad_vivienda = Number(f.antiguedad_vivienda)
  if (f.zona_fria) s.zona_fria = true
  if (f.calidad_aislamiento !== '') s.calidad_aislamiento = f.calidad_aislamiento as CalidadAislamiento
  if (f.fuente_calefaccion !== '') s.fuente_calefaccion = f.fuente_calefaccion as FuenteEnergia
  if (f.fuente_agua_caliente !== '') s.fuente_agua_caliente = f.fuente_agua_caliente as FuenteEnergia
  if (f.uso_horario_pico) s.uso_horario_pico = true
  return s
}

const OPCIONALES = [
  'metros_cuadrados', 'antiguedad_vivienda', 'zona_fria',
  'calidad_aislamiento', 'fuente_calefaccion', 'fuente_agua_caliente', 'uso_horario_pico',
]

interface Props {
  modoApi: ModoApi
  modoDemo: ModoDemo
}

export function Analizar({ modoApi, modoDemo }: Props) {
  useTitulo('Analizar tu consumo')

  const navegar = useNavigate()
  const [form, setForm] = useState<Formulario>(INICIAL)
  const [errores, setErrores] = useState<Record<string, string>>({})
  const [aviso, setAviso] = useState<RespuestaError | null>(null)
  const [enviando, setEnviando] = useState(false)
  const [opcionalesAbiertos, setOpcionalesAbiertos] = useState(false)

  /**
   * Lleva el foco al primer campo con error. Tiene que ir en un efecto: si
   * se consultara el DOM justo después de `setErrores`, React todavía no
   * repintó y la clase `has-error` no existe — el foco se quedaría donde
   * estaba y el usuario tendría que buscar el error a mano.
   */
  useEffect(() => {
    if (Object.keys(errores).length === 0) return
    const primero = document.querySelector<HTMLElement>('.field.has-error')
    if (!primero) return
    primero.scrollIntoView({ block: 'center' })
    primero.querySelector<HTMLElement>('input, select, .switch')?.focus({ preventScroll: true })
  }, [errores])

  /** Al corregir un campo, su error desaparece sin esperar a reenviar. */
  function actualizar<C extends keyof Formulario>(campo: C, valor: Formulario[C]) {
    setForm((f) => ({ ...f, [campo]: valor }))
    setErrores((e) => {
      if (!(campo in e)) return e
      const { [campo as string]: _, ...resto } = e
      return resto
    })
  }

  async function enviar(evento?: React.FormEvent) {
    evento?.preventDefault()
    setAviso(null)
    setErrores({})
    setEnviando(true)

    const solicitud = aSolicitud(form)

    try {
      const analisis = await analizar(solicitud, { modoApi, modoDemo })
      navegar('/resultado', { state: { analisis, solicitud } })
    } catch (e) {
      if (e instanceof ErrorApi && e.respuesta.status === 400 && e.respuesta.detalles?.length) {
        // Texto nuestro para los campos que conocemos; el de la API para
        // cualquier validación que no hayamos previsto.
        const mapa: Record<string, string> = {}
        for (const d of e.respuesta.detalles) mapa[d.campo] = mensajeDeCampo(d.campo, d.mensaje)
        setErrores(mapa)

        if (Object.keys(mapa).some((c) => OPCIONALES.includes(c))) setOpcionalesAbiertos(true)
      } else if (e instanceof ErrorApi) {
        setAviso(e.respuesta)
      } else {
        setAviso({ status: 500, mensaje: 'Error inesperado en la aplicación' })
      }
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="col">
      {aviso && <Aviso respuesta={aviso} onReintentar={() => void enviar()} />}

      <div className="intro">
        <h1 className="intro__title">Descubrí cuánto podés ahorrar en tu factura de luz</h1>
        <p className="intro__lead">
          Cargá cuatro datos obligatorios —y, si querés, siete opcionales— y recibí tu perfil
          energético, el costo estimado y recomendaciones.
        </p>
        <p className="pill">Uso libre · sin registro</p>
      </div>

      <form id="form" className={enviando ? 'card card--dashed is-busy' : 'card card--dashed'} onSubmit={(e) => void enviar(e)} noValidate>
        <p className="eyebrow">Formulario de consumo</p>

        <EntradaNumero
          nombre="consumo_kwh" etiqueta="Consumo mensual"
          ayuda="Figura en tu factura de luz · entre 1 y 1000 kWh"
          error={errores.consumo_kwh} valor={form.consumo_kwh}
          onChange={(v) => actualizar('consumo_kwh', v)}
          min={1} max={1000} unidad="kWh" decimal
        />

        <TarjetasOpcion
          nombre="tipo_inmueble" etiqueta="Tipo de inmueble"
          ayuda="Valores del contrato: Casa · Departamento · Comercio · Pyme"
          error={errores.tipo_inmueble} valores={TIPOS_INMUEBLE}
          etiquetasCortas={{ Departamento: 'Depto.' }}
          valor={form.tipo_inmueble} onChange={(v) => actualizar('tipo_inmueble', v)}
        />

        <Stepper
          nombre="cantidad_equipos" etiqueta="Cantidad de equipos" ayuda="Entre 1 y 100"
          error={errores.cantidad_equipos} valor={form.cantidad_equipos}
          onChange={(v) => actualizar('cantidad_equipos', v)} min={1} max={100}
        />

        <Deslizador
          nombre="horas_alto_consumo" etiqueta="Horas de alto consumo por día"
          error={errores.horas_alto_consumo} valor={form.horas_alto_consumo}
          onChange={(v) => actualizar('horas_alto_consumo', v)} min={0} max={24} unidad="h"
        />

        <Desplegable
          titulo="Datos adicionales (opcional)"
          resumen="7 campos · mejoran la precisión del modelo"
          ayuda="El análisis funciona sin ellos · si no los tocás se envían los valores por defecto"
          abierto={opcionalesAbiertos}
          onToggle={setOpcionalesAbiertos}
        >
          <div className="grid2">
            <EntradaNumero
              nombre="metros_cuadrados" etiqueta="Metros cuadrados"
              ayuda="Superficie habitable · entre 26 y 2000 · por defecto 1000"
              error={errores.metros_cuadrados} valor={form.metros_cuadrados}
              onChange={(v) => actualizar('metros_cuadrados', v)}
              min={26} max={2000} unidad="m²" defecto={1000}
            />
            <EntradaNumero
              nombre="antiguedad_vivienda" etiqueta="Antigüedad de la vivienda"
              ayuda="Años desde la construcción · entre 0 y 150 · por defecto 50"
              error={errores.antiguedad_vivienda} valor={form.antiguedad_vivienda}
              onChange={(v) => actualizar('antiguedad_vivienda', v)}
              min={0} max={150} unidad="años" defecto={50}
            />
            <Interruptor
              nombre="zona_fria" etiqueta="Zona fría"
              ayuda="Zona climática considerada fría · por defecto No"
              error={errores.zona_fria} valor={form.zona_fria}
              onChange={(v) => actualizar('zona_fria', v)}
            />
            <Seleccion
              nombre="calidad_aislamiento" etiqueta="Calidad del aislamiento"
              ayuda="Muy Alta · Alta · Media · Baja · Muy Baja"
              error={errores.calidad_aislamiento} valores={CALIDADES_AISLAMIENTO} defecto="Media"
              valor={form.calidad_aislamiento} onChange={(v) => actualizar('calidad_aislamiento', v)}
            />
            <Seleccion
              nombre="fuente_calefaccion" etiqueta="Fuente de calefacción"
              ayuda="Solar · Electricidad · Otros"
              error={errores.fuente_calefaccion} valores={FUENTES_ENERGIA} defecto="Electricidad"
              valor={form.fuente_calefaccion} onChange={(v) => actualizar('fuente_calefaccion', v)}
            />
            <Seleccion
              nombre="fuente_agua_caliente" etiqueta="Fuente de agua caliente"
              ayuda="Solar · Electricidad · Otros"
              error={errores.fuente_agua_caliente} valores={FUENTES_ENERGIA} defecto="Electricidad"
              valor={form.fuente_agua_caliente} onChange={(v) => actualizar('fuente_agua_caliente', v)}
            />
            <Interruptor
              nombre="uso_horario_pico" etiqueta="Uso en horario pico"
              ayuda="Franja de 18 a 23 h · por defecto No"
              error={errores.uso_horario_pico} valor={form.uso_horario_pico}
              onChange={(v) => actualizar('uso_horario_pico', v)}
            />
          </div>
          <p className="note">
            Contrato V1.2 · si no los completás, se envían los valores por defecto que muestra cada campo.
          </p>
        </Desplegable>
      </form>

      <button type="submit" form="form" className={enviando ? 'btn btn--block is-busy' : 'btn btn--block'} disabled={enviando}>
        <span className="btn__spinner" aria-hidden="true" />
        <span className="btn__label">{enviando ? 'Analizando…' : 'Analizar mi consumo'}</span>
      </button>
      {enviando && <p className="note note--center">Los controles quedan inactivos y conservan sus valores.</p>}

      <section className="howto" aria-label="Cómo funciona">
        <p className="eyebrow">Cómo funciona</p>
        <ol className="howto__steps">
          <li className="howto__step"><span className="howto__num">1</span> Ingresás tus datos</li>
          <li className="howto__step"><span className="howto__num">2</span> Un modelo los analiza</li>
          <li className="howto__step"><span className="howto__num">3</span> Recibís tu resultado</li>
        </ol>
      </section>
    </div>
  )
}

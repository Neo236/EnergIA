/* ============================================================
   Respuesta simulada. Permite demostrar P-01/P-02 sin depender de que
   el back-end y el servicio de ML estén integrados.

   ⚠️ El puntaje NO es el del modelo real: es un sustituto para que el
   veredicto reaccione a lo que se carga en vez de devolver siempre lo
   mismo. El modelo entrenado usa una lógica IEE distinta, así que las
   categorías pueden no coincidir con las de la API real.
   ============================================================ */

import {
  CAMPOS_OPCIONALES, TARIFA_KWH, ErrorApi,
  type Analisis, type Categoria, type DetalleError, type Solicitud,
} from './contrato'
import { CAMPOS } from './contrato'

const LATENCIA_MS = 900

export type ModoDemo = 'ok' | 'sin-recomendaciones' | '400' | '500' | '503'

const PESO_AISLAMIENTO: Record<string, number> = {
  'Muy Alta': 10, Alta: 6, Media: 0, Baja: -5, 'Muy Baja': -10,
}
const PESO_CALEFACCION: Record<string, number> = { Solar: 10, Otros: 0, Electricidad: -4 }
const PESO_AGUA: Record<string, number> = { Solar: 4, Otros: 0, Electricidad: -2 }

function completar(solicitud: Solicitud): Record<string, unknown> {
  const v: Record<string, unknown> = { ...solicitud }
  for (const campo of CAMPOS_OPCIONALES) {
    if (v[campo.nombre] === undefined && 'defecto' in campo) v[campo.nombre] = campo.defecto
  }
  return v
}

function puntaje(v: Record<string, unknown>): number {
  return (
    -0.02 * Number(v.consumo_kwh) +
    (PESO_AISLAMIENTO[String(v.calidad_aislamiento)] ?? 0) +
    (PESO_CALEFACCION[String(v.fuente_calefaccion)] ?? 0) +
    (PESO_AGUA[String(v.fuente_agua_caliente)] ?? 0) -
    (v.zona_fria ? 8 : 0) -
    (v.uso_horario_pico ? 6 : 0) -
    0.05 * Number(v.horas_alto_consumo) -
    0.06 * Number(v.cantidad_equipos)
  )
}

function clasificar(p: number): Categoria {
  if (p >= -4) return 'Eficiente'
  if (p >= -18) return 'Moderado'
  return 'Ineficiente'
}

function confianza(p: number, categoria: Categoria): number {
  const borde =
    categoria === 'Eficiente' ? Math.abs(p + 4)
      : categoria === 'Ineficiente' ? Math.abs(p + 18)
        : Math.min(Math.abs(p + 4), Math.abs(p + 18))
  return Math.round((0.58 + Math.min(borde / 22, 1) * 0.37) * 10000) / 10000
}

function recomendaciones(v: Record<string, unknown>): string[] {
  const r: string[] = []
  const consumo = Number(v.consumo_kwh)

  if (consumo > 700) {
    r.push('Tu consumo eléctrico es muy elevado. Revisá los electrodomésticos de alto consumo y la aislación térmica.')
  } else if (consumo > 450) {
    r.push('Tu consumo está por encima del promedio. Auditá el uso de calefacción y de equipos en horario pico.')
  }
  if (v.calidad_aislamiento === 'Muy Baja') {
    r.push('Mejorar el aislamiento térmico reducirá drásticamente la necesidad de climatización.')
  } else if (v.calidad_aislamiento === 'Baja') {
    r.push('Reforzá puertas y ventanas: pasar a una aislación media reduce cerca del 30 % del gasto en climatización.')
  }
  if (v.fuente_calefaccion === 'Electricidad') {
    r.push('Evaluá migrar la calefacción a solar: la electricidad es la fuente más cara del análisis.')
  } else if (v.fuente_calefaccion === 'Otros') {
    r.push('Considerá un sistema de calefacción más eficiente, como solar o bomba de calor.')
  }
  if (v.zona_fria) r.push('Vivir en zona fría incrementa el consumo. Priorizá aislación y calefacción eficiente.')
  if (Number(v.horas_alto_consumo) > 14) {
    r.push('Tenés más de 14 h diarias de alto consumo. Centralizá el uso en horarios de menor demanda.')
  }
  if (Number(v.cantidad_equipos) > 70) {
    r.push('Tenés muchos equipos conectados. Reemplazar los más antiguos por clase A+ se paga solo a cinco años.')
  }
  if (Number(v.antiguedad_vivienda) > 80) {
    r.push('Vivienda de más de 80 años: revisá la instalación eléctrica y la aislación, suele haber pérdidas ocultas.')
  }
  if (r.length === 0) r.push('Tu hogar está bien calibrado. Mantené los hábitos de consumo actuales.')
  return r.slice(0, 5)
}

/** Réplica de las validaciones del DTO, para producir un 400 realista. */
function validar(solicitud: Solicitud): DetalleError[] {
  const detalles: DetalleError[] = []
  const valores: Record<string, unknown> = { ...solicitud }

  for (const campo of CAMPOS) {
    const valor = valores[campo.nombre]

    if (valor === undefined || valor === null || valor === '') {
      if (campo.requerido) detalles.push({ campo: campo.nombre, mensaje: 'No puede estar vacío' })
      continue
    }
    if (campo.tipo === 'numero') {
      const n = Number(valor)
      if (Number.isNaN(n)) detalles.push({ campo: campo.nombre, mensaje: 'Debe ser un número' })
      else if (n < campo.min || n > campo.max) {
        detalles.push({ campo: campo.nombre, mensaje: `Debe estar entre ${campo.min} y ${campo.max}` })
      }
    } else if ((campo.tipo === 'opciones' || campo.tipo === 'seleccion') && !campo.valores.includes(String(valor))) {
      detalles.push({ campo: campo.nombre, mensaje: `Valor no válido para ${campo.etiqueta}` })
    }
  }
  return detalles
}

function error(status: number, error: string, mensaje: string, detalles?: DetalleError[]): ErrorApi {
  return new ErrorApi({
    timestamp: new Date().toISOString().slice(0, 19),
    status, error, mensaje,
    ...(detalles ? { detalles } : {}),
  })
}

export function analizarSimulado(solicitud: Solicitud, modo: ModoDemo): Promise<Analisis> {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const detalles = validar(solicitud)
      if (detalles.length > 0) {
        return reject(error(400, 'BAD_REQUEST', 'Errores de validacion en los datos de entrada', detalles))
      }
      if (modo === '400') {
        return reject(error(400, 'BAD_REQUEST',
          'El servicio de Machine Learning rechazó los datos de entrada (HTTP 422)'))
      }
      if (modo === '500') {
        return reject(error(500, 'INTERNAL_SERVER_ERROR', 'Ocurrió un error inesperado en el servidor'))
      }
      if (modo === '503') {
        return reject(error(503, 'SERVICE_UNAVAILABLE', 'El servicio de análisis no está disponible'))
      }

      const v = completar(solicitud)
      const p = puntaje(v)
      const categoria = clasificar(p)

      resolve({
        categoria,
        probabilidad: confianza(p, categoria),
        costo_estimado_mensual: Math.round(Number(v.consumo_kwh) * TARIFA_KWH * 100) / 100,
        recomendaciones: modo === 'sin-recomendaciones' ? [] : recomendaciones(v),
      })
    }, LATENCIA_MS)
  })
}

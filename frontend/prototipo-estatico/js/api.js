/* ============================================================
   EnergiAI · capa de API

   HOY:      analizar() resuelve contra un mock local.
   MAÑANA:   poner MODO = 'real'. No hay que tocar nada más:
             el mock ya devuelve exactamente las formas del
             contrato V1.2 (200) y de DatosErrorRespuesta
             (400 con detalles[], 500 y 503).
   ============================================================ */

window.EnergiAI = window.EnergiAI || {};

EnergiAI.api = (function () {
  'use strict';

  var MODO = 'mock';          // 'mock' | 'real'
  var LATENCIA_MS = 900;
  var forzar = 'ok';          // lo maneja la barra de demo

  var schema = EnergiAI.schema;

  /* ---------- errores con la forma de DatosErrorRespuesta ---------- */

  function errorRespuesta(status, error, mensaje, detalles) {
    var e = new Error(mensaje);
    e.respuesta = {
      timestamp: new Date().toISOString().slice(0, 19),
      status: status,
      error: error,
      mensaje: mensaje
    };
    if (detalles) e.respuesta.detalles = detalles;
    return e;
  }

  /* ---------- validación equivalente a la del DTO ---------- */

  function validar(payload) {
    var detalles = [];

    schema.campos.forEach(function (c) {
      var tiene = Object.prototype.hasOwnProperty.call(payload, c.nombre);
      var v = payload[c.nombre];

      if (!tiene || v === null || v === '') {
        if (c.requerido) detalles.push({ campo: c.nombre, mensaje: 'No puede estar vacío' });
        return;
      }
      if (c.tipo === 'numero') {
        if (typeof v !== 'number' || isNaN(v)) {
          detalles.push({ campo: c.nombre, mensaje: 'Debe ser un número' });
        } else if (v < c.min || v > c.max) {
          detalles.push({ campo: c.nombre, mensaje: c.mensaje });
        }
      } else if (c.tipo === 'enum' && c.valores.indexOf(v) === -1) {
        detalles.push({ campo: c.nombre, mensaje: c.mensaje });
      }
    });

    return detalles;
  }

  /* ---------- modelo simulado ----------
     Réplica del puntaje con el que data-science etiqueta el
     dataset (infrastructure/data/simulation.py). No es el
     RandomForest: es un sustituto para poder demostrar.       */

  var PESO_AISLAMIENTO = { 'Muy Alta': 10, 'Alta': 6, 'Media': 0, 'Baja': -5, 'Muy Baja': -10 };
  var PESO_CALEFACCION = { 'Solar': 10, 'Otros': 0, 'Electricidad': -4 };
  var PESO_AGUA = { 'Solar': 4, 'Otros': 0, 'Electricidad': -2 };

  function puntaje(v) {
    return -0.02 * v.consumo_kwh
      + (PESO_AISLAMIENTO[v.calidad_aislamiento] || 0)
      + (PESO_CALEFACCION[v.fuente_calefaccion] || 0)
      + (PESO_AGUA[v.fuente_agua_caliente] || 0)
      - (v.zona_fria ? 8 : 0)
      - (v.uso_horario_pico ? 6 : 0)
      - 0.05 * v.horas_alto_consumo
      - 0.06 * v.cantidad_equipos;
  }

  function clasificar(p) {
    if (p >= -4) return 'Eficiente';
    if (p >= -18) return 'Moderado';
    return 'Ineficiente';
  }

  function confianza(p, categoria) {
    var borde = categoria === 'Eficiente' ? Math.abs(p + 4)
      : categoria === 'Ineficiente' ? Math.abs(p + 18)
        : Math.min(Math.abs(p + 4), Math.abs(p + 18));
    var c = 0.58 + Math.min(borde / 22, 1) * 0.37;
    return Math.round(c * 10000) / 10000;
  }

  function recomendaciones(v) {
    var r = [];
    if (v.consumo_kwh > 700) {
      r.push('Tu consumo eléctrico es muy elevado. Revisá los electrodomésticos de alto consumo y la aislación térmica.');
    } else if (v.consumo_kwh > 450) {
      r.push('Tu consumo está por encima del promedio. Auditá el uso de calefacción y de equipos en horario pico.');
    }
    if (v.calidad_aislamiento === 'Muy Baja') {
      r.push('Mejorar el aislamiento térmico reducirá drásticamente la necesidad de climatización.');
    } else if (v.calidad_aislamiento === 'Baja') {
      r.push('Reforzá puertas y ventanas: pasar a una aislación media reduce cerca del 30 % del gasto en climatización.');
    }
    if (v.fuente_calefaccion === 'Electricidad') {
      r.push('Evaluá migrar la calefacción a solar: la electricidad es la fuente más cara del análisis.');
    } else if (v.fuente_calefaccion === 'Otros') {
      r.push('Considerá un sistema de calefacción más eficiente, como solar o bomba de calor.');
    }
    if (v.zona_fria) {
      r.push('Vivir en zona fría incrementa el consumo. Priorizá aislación y calefacción eficiente.');
    }
    if (v.horas_alto_consumo > 14) {
      r.push('Tenés más de 14 h diarias de alto consumo. Centralizá el uso en horarios de menor demanda.');
    }
    if (v.cantidad_equipos > 70) {
      r.push('Tenés muchos equipos conectados. Reemplazar los más antiguos por clase A+ se paga solo a cinco años.');
    }
    if (v.antiguedad_vivienda > 80) {
      r.push('Vivienda de más de 80 años: revisá la instalación eléctrica y la aislación, suele haber pérdidas ocultas.');
    }
    if (!r.length) r.push('Tu hogar está bien calibrado. Mantené los hábitos de consumo actuales.');
    return r.slice(0, 5);
  }

  function responder(payload) {
    var v = schema.conDefectos(payload);
    var p = puntaje(v);
    var categoria = clasificar(p);
    return {
      categoria: categoria,
      probabilidad: confianza(p, categoria),
      costo_estimado_mensual: Math.round(v.consumo_kwh * schema.tarifaKwh * 100) / 100,
      recomendaciones: forzar === 'sin-recos' ? [] : recomendaciones(v)
    };
  }

  /* ---------- transporte ---------- */

  function mock(payload) {
    return new Promise(function (resolve, reject) {
      setTimeout(function () {
        var detalles = validar(payload);
        if (detalles.length) {
          return reject(errorRespuesta(400, 'BAD_REQUEST',
            'Errores de validacion en los datos de entrada', detalles));
        }
        if (forzar === '500') {
          return reject(errorRespuesta(500, 'INTERNAL_SERVER_ERROR',
            'Ocurrió un error inesperado en el servidor'));
        }
        if (forzar === '503') {
          return reject(errorRespuesta(503, 'SERVICE_UNAVAILABLE',
            'El servicio de análisis no está disponible'));
        }
        resolve(responder(payload));
      }, LATENCIA_MS);
    });
  }

  function real(payload) {
    return fetch(schema.endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(function (res) {
      return res.json().catch(function () { return null; }).then(function (cuerpo) {
        if (res.ok) return cuerpo;
        var e = new Error((cuerpo && cuerpo.mensaje) || 'Error ' + res.status);
        e.respuesta = cuerpo || { status: res.status, error: res.statusText, mensaje: e.message };
        throw e;
      });
    });
  }

  return {
    analizar: function (payload) { return MODO === 'real' ? real(payload) : mock(payload); },
    forzar: function (modo) { forzar = modo; },
    esMock: function () { return MODO === 'mock'; }
  };
})();

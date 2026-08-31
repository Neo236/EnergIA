/* ============================================================
   EnergIA · schema — FUENTE ÚNICA del contrato V1.2
   Si el contrato cambia, se toca solo este archivo.
   requerido:false + defecto  →  el campo es opcional y el
   back-end aplica ese valor si no se envía.
   ============================================================ */

window.EnergIA = window.EnergIA || {};

EnergIA.schema = {
  endpoint: '/api/v1/analisis-energetico',
  tarifaKwh: 0.75,

  campos: [
    /* ── obligatorios ── */
    {
      nombre: 'consumo_kwh', etiqueta: 'Consumo mensual', tipo: 'numero',
      requerido: true, min: 1, max: 1000, decimal: true,
      mensaje: 'Debe estar entre 1 y 1000'
    },
    {
      nombre: 'tipo_inmueble', etiqueta: 'Tipo de inmueble', tipo: 'enum',
      requerido: true, valores: ['Casa', 'Departamento', 'Comercio', 'Pyme'],
      mensaje: 'Debe ser Casa, Departamento, Comercio o Pyme'
    },
    {
      nombre: 'cantidad_equipos', etiqueta: 'Cantidad de equipos', tipo: 'numero',
      requerido: true, min: 1, max: 100,
      mensaje: 'Debe estar entre 1 y 100'
    },
    {
      nombre: 'horas_alto_consumo', etiqueta: 'Horas de alto consumo por día', tipo: 'numero',
      requerido: true, min: 0, max: 24, unidad: 'h',
      mensaje: 'Debe estar entre 0 y 24'
    },

    /* ── opcionales con valor por defecto ── */
    {
      nombre: 'metros_cuadrados', etiqueta: 'Metros cuadrados', tipo: 'numero',
      requerido: false, defecto: 1000, min: 26, max: 2000, unidad: 'm²',
      mensaje: 'Debe estar entre 26 y 2000'
    },
    {
      nombre: 'antiguedad_vivienda', etiqueta: 'Antigüedad de la vivienda', tipo: 'numero',
      requerido: false, defecto: 50, min: 0, max: 150, unidad: 'años',
      mensaje: 'Debe estar entre 0 y 150'
    },
    {
      nombre: 'zona_fria', etiqueta: 'Zona fría', tipo: 'booleano',
      requerido: false, defecto: false
    },
    {
      nombre: 'calidad_aislamiento', etiqueta: 'Calidad del aislamiento', tipo: 'enum',
      requerido: false, defecto: 'Media',
      valores: ['Muy Alta', 'Alta', 'Media', 'Baja', 'Muy Baja'],
      mensaje: 'Valor de aislamiento no válido'
    },
    {
      nombre: 'fuente_calefaccion', etiqueta: 'Fuente de calefacción', tipo: 'enum',
      requerido: false, defecto: 'Electricidad',
      valores: ['Solar', 'Electricidad', 'Otros'],
      mensaje: 'Valor de fuente no válido'
    },
    {
      nombre: 'fuente_agua_caliente', etiqueta: 'Fuente de agua caliente', tipo: 'enum',
      requerido: false, defecto: 'Electricidad',
      valores: ['Solar', 'Electricidad', 'Otros'],
      mensaje: 'Valor de fuente no válido'
    },
    {
      nombre: 'uso_horario_pico', etiqueta: 'Uso en horario pico', tipo: 'booleano',
      requerido: false, defecto: false
    }
  ]
};

EnergIA.schema.porNombre = EnergIA.schema.campos.reduce(function (acc, c) {
  acc[c.nombre] = c;
  return acc;
}, {});

/** Completa un payload parcial con los valores por defecto del contrato. */
EnergIA.schema.conDefectos = function (payload) {
  var completo = {};
  EnergIA.schema.campos.forEach(function (c) {
    completo[c.nombre] = Object.prototype.hasOwnProperty.call(payload, c.nombre)
      ? payload[c.nombre]
      : c.defecto;
  });
  return completo;
};

/* ============================================================
   EnergiAI · aplicación (P-01 / P-02)
   Estados cubiertos, igual que el wireframe v2.2:
   inicial · opcionales desplegados · enviando · validación 400
   · error 500 · servicio no disponible 503 · resultado
   · resultado sin recomendaciones
   ============================================================ */

(function () {
  'use strict';

  var schema = EnergiAI.schema;
  var api = EnergiAI.api;

  var $ = function (id) { return document.getElementById(id); };
  var moneda = new Intl.NumberFormat('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  var form = $('form');
  var p01 = $('p01');
  var p02 = $('p02');
  var btnAnalizar = $('btn-analizar');
  var aviso = $('aviso');

  var ultimoPayload = null;

  var sinMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)');
  var mov = function () { return sinMovimiento.matches ? 'auto' : 'smooth'; };

  /** La barra de demo es fija y en móvil ocupa dos líneas: le reservamos su alto real. */
  function ajustarEspacioDemo() {
    var barra = document.querySelector('.demobar');
    if (barra) document.body.style.paddingBottom = (barra.offsetHeight + 12) + 'px';
  }

  /* ─────────────── controles ─────────────── */

  function initStepper() {
    var input = $('cantidad_equipos');
    var botones = Array.prototype.slice.call(document.querySelectorAll('.stepper__btn'));

    function sincronizarLimites() {
      var v = Number(input.value || 0);
      botones.forEach(function (b) {
        var paso = Number(b.dataset.step);
        b.disabled = (paso < 0 && v <= 1) || (paso > 0 && v >= 100);
      });
    }

    botones.forEach(function (b) {
      b.addEventListener('click', function () {
        var paso = Number(b.dataset.step);
        var actual = Number(input.value || 0);
        input.value = Math.min(100, Math.max(1, actual + paso));
        sincronizarLimites();
        limpiarErrorDe(input.closest('[data-field]'));
      });
    });

    input.addEventListener('input', sincronizarLimites);
    sincronizarLimites();
  }

  function initSlider() {
    var range = $('horas_alto_consumo');
    var out = $('horas_out');
    function pintar() {
      out.textContent = range.value + ' h';
      range.style.setProperty('--fill', (range.value / 24 * 100) + '%');
    }
    range.addEventListener('input', pintar);
    pintar();
  }

  function initSwitches() {
    Array.prototype.forEach.call(document.querySelectorAll('.switch'), function (sw) {
      var estado = document.querySelector('[data-state-for="' + sw.id + '"]');
      sw.addEventListener('click', function () {
        var activo = sw.getAttribute('aria-checked') === 'true';
        sw.setAttribute('aria-checked', String(!activo));
        estado.textContent = !activo ? 'Sí' : 'No';
        limpiarErrorDe(sw.closest('[data-field]'));
      });
    });
  }

  function initDesplegable(idBoton, idCuerpo) {
    var boton = $(idBoton);
    var cuerpo = $(idCuerpo);
    boton.addEventListener('click', function () {
      var abierto = boton.getAttribute('aria-expanded') === 'true';
      boton.setAttribute('aria-expanded', String(!abierto));
      cuerpo.hidden = abierto;
    });
  }

  function abrirOpcionales() {
    $('opt-toggle').setAttribute('aria-expanded', 'true');
    $('opt-body').hidden = false;
  }

  /* ─────────────── lectura del formulario ─────────────── */

  function numeroONulo(id) {
    var v = $(id).value.trim();
    return v === '' ? null : Number(v);
  }

  /** Arma el payload mínimo: los 4 obligatorios y solo los
      opcionales que el usuario efectivamente tocó. */
  function leerPayload() {
    var p = {};

    var consumo = numeroONulo('consumo_kwh');
    if (consumo !== null) p.consumo_kwh = consumo;

    var tipo = form.querySelector('input[name="tipo_inmueble"]:checked');
    if (tipo) p.tipo_inmueble = tipo.value;

    var equipos = numeroONulo('cantidad_equipos');
    if (equipos !== null) p.cantidad_equipos = equipos;

    p.horas_alto_consumo = Number($('horas_alto_consumo').value);

    ['metros_cuadrados', 'antiguedad_vivienda'].forEach(function (n) {
      var v = numeroONulo(n);
      if (v !== null) p[n] = v;
    });

    ['calidad_aislamiento', 'fuente_calefaccion', 'fuente_agua_caliente'].forEach(function (n) {
      var v = $(n).value;
      if (v !== '') p[n] = v;
    });

    ['zona_fria', 'uso_horario_pico'].forEach(function (n) {
      if ($(n).getAttribute('aria-checked') === 'true') p[n] = true;
    });

    return p;
  }

  /* ─────────────── errores de validación ─────────────── */

  function limpiarErrores() {
    Array.prototype.forEach.call(form.querySelectorAll('.field.has-error'), function (f) {
      f.classList.remove('has-error');
    });
    Array.prototype.forEach.call(form.querySelectorAll('.error'), function (e) { e.remove(); });
    Array.prototype.forEach.call(form.querySelectorAll('.help[hidden]'), function (h) {
      h.hidden = false;
    });
    Array.prototype.forEach.call(form.querySelectorAll('[aria-invalid]'), function (c) {
      c.removeAttribute('aria-invalid');
    });
  }

  /** Quita la marca de error de un campo en cuanto el usuario lo corrige. */
  function limpiarErrorDe(campo) {
    if (!campo || !campo.classList.contains('has-error')) return;
    campo.classList.remove('has-error');

    var err = campo.querySelector('.error');
    if (err) err.remove();

    var ayuda = campo.querySelector('.help[hidden]');
    if (ayuda) ayuda.hidden = false;

    var control = campo.querySelector('[aria-invalid]');
    if (control) control.removeAttribute('aria-invalid');
  }

  function pintarErrores(detalles) {
    limpiarErrores();
    var primero = null;
    var hayOpcional = false;

    detalles.forEach(function (d) {
      var campo = form.querySelector('[data-field="' + d.campo + '"]');
      if (!campo) return;

      campo.classList.add('has-error');
      var control = campo.querySelector('input, select, .switch');
      if (control) control.setAttribute('aria-invalid', 'true');

      var ayuda = campo.querySelector('.help');
      if (ayuda) ayuda.hidden = true;

      var msg = document.createElement('p');
      msg.className = 'error';
      msg.setAttribute('role', 'alert');
      msg.textContent = d.mensaje;
      campo.appendChild(msg);

      var def = schema.porNombre[d.campo];
      if (def && !def.requerido) hayOpcional = true;
      if (!primero) primero = campo;
    });

    if (hayOpcional) abrirOpcionales();
    if (primero) {
      var foco = primero.querySelector('input, select, .switch');
      if (foco) foco.focus({ preventScroll: true });
      primero.scrollIntoView({ behavior: mov(), block: 'center' });
    }
  }

  /* ─────────────── aviso 500 / 503 ─────────────── */

  var AVISOS = {
    500: {
      titulo: 'No pudimos completar el análisis',
      texto: 'El servidor respondió con un error. Podés intentar de nuevo en unos segundos — tus datos siguen cargados.',
      advertencia: false
    },
    503: {
      titulo: 'El análisis no está disponible ahora',
      texto: 'El servicio del modelo no responde en este momento. Probá de nuevo en unos minutos — tus datos siguen cargados.',
      advertencia: true
    }
  };

  function mostrarAviso(status) {
    var a = AVISOS[status] || AVISOS[500];
    $('aviso-title').textContent = a.titulo;
    $('aviso-text').textContent = a.texto;
    aviso.classList.toggle('is-warning', a.advertencia);
    aviso.hidden = false;
    aviso.scrollIntoView({ behavior: mov(), block: 'center' });
  }

  function ocultarAviso() { aviso.hidden = true; }

  /* ─────────────── estado de envío ─────────────── */

  function ocupado(activo) {
    form.classList.toggle('is-busy', activo);
    btnAnalizar.classList.toggle('is-busy', activo);
    btnAnalizar.disabled = activo;
    btnAnalizar.querySelector('.btn__label').textContent = activo ? 'Analizando…' : 'Analizar mi consumo';
    $('nota-enviando').hidden = !activo;
  }

  /* ─────────────── P-02 ─────────────── */

  var ICONO = { Eficiente: '▼', Moderado: '◆', Ineficiente: '▲' };

  function fechaLegible(d) {
    var meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
      'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
    var hh = String(d.getHours()).padStart(2, '0');
    var mm = String(d.getMinutes()).padStart(2, '0');
    return 'Análisis del ' + d.getDate() + ' de ' + meses[d.getMonth()] + ', ' + hh + ':' + mm + ' h';
  }

  function valorLegible(campo, valor) {
    if (campo.tipo === 'booleano') return valor ? 'Sí' : 'No';
    if (campo.unidad) return valor + ' ' + campo.unidad;
    if (campo.nombre === 'consumo_kwh') return valor + ' kWh';
    return String(valor);
  }

  function pintarResumen(payload) {
    var dl = $('resumen');
    dl.textContent = '';
    schema.campos.forEach(function (c) {
      var usado = Object.prototype.hasOwnProperty.call(payload, c.nombre);
      var valor = usado ? payload[c.nombre] : c.defecto;

      var dt = document.createElement('dt');
      dt.textContent = c.etiqueta;
      var dd = document.createElement('dd');
      dd.textContent = valorLegible(c, valor) + (usado ? '' : ' · por defecto');
      if (!usado) dd.className = 'is-default';

      dl.appendChild(dt);
      dl.appendChild(dd);
    });
  }

  function mostrarResultado(res, payload) {
    var pct = Math.round(res.probabilidad * 100);

    $('verdict').dataset.cat = res.categoria;
    $('verdict-icon').textContent = ICONO[res.categoria] || '◆';
    $('verdict-text').textContent = res.categoria;

    $('conf-value').textContent = pct + ' %';
    $('conf-fill').style.width = pct + '%';
    $('conf-bar-wrap').setAttribute('aria-valuenow', String(pct));

    $('fecha').textContent = fechaLegible(new Date());

    $('cost-amount').textContent = '$ ' + moneda.format(res.costo_estimado_mensual) + ' / mes';
    $('cost-year').textContent = 'Proyección anual: $ ' + moneda.format(res.costo_estimado_mensual * 12);

    var lista = $('recos');
    lista.textContent = '';
    (res.recomendaciones || []).forEach(function (r) {
      var li = document.createElement('li');
      li.textContent = r;
      lista.appendChild(li);
    });
    $('recos-block').hidden = !(res.recomendaciones && res.recomendaciones.length);

    pintarResumen(payload);

    p01.hidden = true;
    p02.hidden = false;
    window.scrollTo(0, 0);
    p02.focus();
  }

  /* ─────────────── envío ─────────────── */

  function enviar() {
    ocultarAviso();
    limpiarErrores();
    ultimoPayload = leerPayload();
    ocupado(true);

    api.analizar(ultimoPayload)
      .then(function (res) {
        ocupado(false);
        mostrarResultado(res, ultimoPayload);
      })
      .catch(function (err) {
        ocupado(false);
        var r = err.respuesta || {};
        if (r.status === 400 && r.detalles) pintarErrores(r.detalles);
        else mostrarAviso(r.status);
      });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    enviar();
  });

  $('btn-reintentar').addEventListener('click', enviar);

  $('btn-nuevo').addEventListener('click', function () {
    p02.hidden = true;
    p01.hidden = false;
    ocultarAviso();
    limpiarErrores();
    window.scrollTo(0, 0);
  });

  /* ─────────────── barra de demo ─────────────── */

  /* limpia el error del campo apenas el usuario lo corrige */
  form.addEventListener('input', function (e) { limpiarErrorDe(e.target.closest('[data-field]')); });
  form.addEventListener('change', function (e) { limpiarErrorDe(e.target.closest('[data-field]')); });

  $('demobar-opts').addEventListener('click', function (e) {
    var chip = e.target.closest('.chip');
    if (!chip) return;
    Array.prototype.forEach.call(this.querySelectorAll('.chip'), function (c) {
      c.classList.toggle('is-on', c === chip);
    });
    api.forzar(chip.dataset.mock);
  });

  /* ─────────────── arranque ─────────────── */

  initStepper();
  initSlider();
  initSwitches();
  initDesplegable('opt-toggle', 'opt-body');
  initDesplegable('resumen-toggle', 'resumen-body');

  ajustarEspacioDemo();
  window.addEventListener('resize', ajustarEspacioDemo);
})();

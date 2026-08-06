# EnergiAI · Front-End mínimo (P-01 / P-02)

Mockup navegable de las dos pantallas comprometidas, con **respuestas simuladas en el cliente**.
Sirve para validar el formulario y los estados antes de conectar la API real.

- Sin build, sin dependencias, sin `node_modules`: HTML + CSS + JS.
- Estructura y proporciones tomadas del wireframe v2.2 en Figma.
- La paleta es **temporal**: vive completa en `css/tokens.css`.

## Correr en local

Abrí `index.html` en el navegador. No necesita servidor.

Si preferís servirlo:

```bash
npx serve .
```

## Estructura

| Archivo | Qué contiene |
|---|---|
| `index.html` | Marcado de P-01 y P-02 |
| `css/tokens.css` | Neutrales del wireframe + **paleta temporal** |
| `css/app.css` | Estilos de componentes y layout responsive |
| `js/schema.js` | **Fuente única del contrato V1.2**: 11 campos, rangos, enums y defaults |
| `js/api.js` | Transporte. Hoy mock; `MODO = 'real'` lo apunta a la API |
| `js/app.js` | Estado, render y los ocho estados de pantalla |

## Contrato V1.2

`POST /api/v1/analisis-energetico`

**Obligatorios (4):** `consumo_kwh` (1–1000) · `tipo_inmueble` (Casa · Departamento · Comercio · Pyme) ·
`cantidad_equipos` (1–100) · `horas_alto_consumo` (0–24)

**Opcionales (7), con el valor por defecto que se aplica si no se envían:**

| Campo | Default | Rango / valores |
|---|---|---|
| `metros_cuadrados` | `1000` | 26–2000 |
| `antiguedad_vivienda` | `50` | 0–150 |
| `zona_fria` | `false` | booleano |
| `calidad_aislamiento` | `Media` | Muy Alta · Alta · Media · Baja · Muy Baja |
| `fuente_calefaccion` | `Electricidad` | Solar · Electricidad · Otros |
| `fuente_agua_caliente` | `Electricidad` | Solar · Electricidad · Otros |
| `uso_horario_pico` | `false` | booleano |

El formulario arma el **payload mínimo**: manda los 4 obligatorios y solo los opcionales que el
usuario tocó. Cada campo opcional muestra su valor por defecto en el control.

## Estados cubiertos

Los ocho del wireframe: inicial · opcionales desplegados · enviando · validación 400 con
`detalles[campo · mensaje]` · error 500 · servicio no disponible 503 · resultado · resultado sin
recomendaciones.

La **barra de demo** de abajo fuerza la próxima respuesta (200, 200 sin recomendaciones, 500, 503).
Los errores 400 salen solos de la validación real. **Esa barra se elimina al conectar la API.**

## Pasar a la API real

1. En `js/api.js`, `MODO = 'real'`.
2. Borrar la barra de demo de `index.html` y su bloque en `app.js`.

El mock ya devuelve las formas exactas del contrato —incluido `DatosErrorRespuesta` con
`detalles[]`— así que no hay que tocar `app.js` para el camino feliz.

## Pendientes conocidos

- El DTO de Spring (`DatosRegistroConsumo`) todavía marca los 11 campos con `@NotNull`, y
  `schemas.py` del servicio ML exige 9 de 11 y espera `consumo_electrico_kwh` en lugar de
  `consumo_kwh`. Con eso vigente, el payload mínimo devuelve 400/422.
- El modelo simulado de `api.js` replica el puntaje con el que data-science etiqueta el dataset,
  no el RandomForest entrenado.

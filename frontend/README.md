# EnergIA · Front-End

Aplicación de las dos pantallas comprometidas: **P-01** (ingreso de datos) y
**P-02** (resultado del análisis), más una pantalla de no encontrado.

**Vite + React 19 + TypeScript.** Compila a estáticos: la imagen de producción
no lleva Node, solo nginx y los archivos.

## Arrancar

```bash
npm install
npm run dev
```

Queda en `http://localhost:5173`, y **necesita el back-end corriendo**: la
aplicación habla siempre con la API.

El front la consume en el **mismo origen** (`/api/v1/…`), así que no hay URL
base ni CORS. En desarrollo el proxy del servidor de Vite cumple el papel que en
el despliegue cumple el servicio `proxy` del Compose; `VITE_API_DESTINO` le dice
a dónde reenviar.

```bash
# contra un back-end local en :8080 (el valor por defecto)
npm run dev

# contra un back-end en otro puerto
VITE_API_DESTINO=http://127.0.0.1:9090 npm run dev
```

> Lo más simple para tener todo arriba es `docker compose up -d` en la raíz del
> repositorio, y usar `npm run dev` solo para iterar sobre el front.

Ver [`.env.example`](.env.example).

## Estructura

```
src/
├── main.tsx · App.tsx        arranque y rutas
├── layout/                   Navbar · Footer · Layout (comunes a todas las rutas)
├── pages/                    Analizar (P-01) · Resultado (P-02) · NoEncontrado
├── components/               controles del formulario, desplegable, aviso
├── lib/
│   ├── contrato.ts           ← FUENTE ÚNICA del contrato V1.2
│   ├── api.ts                transporte HTTP contra la API
│   └── formato.ts            moneda, porcentaje, fecha
└── styles/                   tokens.css (paleta) · app.css
```

El prototipo estático en HTML puro que precedió a esta aplicación se retiró del
repositorio: quedó superado por completo. Sigue disponible en el tag `v1.0-hackathon`.

## Rutas

| Ruta | Pantalla |
|---|---|
| `/` | P-01 · ingreso de datos |
| `/resultado` | P-02 · resultado. Sin datos redirige a `/` |
| `/analisis/:id` | Siempre no encontrado — ver abajo |
| cualquier otra | No encontrado |

`/analisis/:id` existe a propósito aunque hoy siempre falle: **la API no
devuelve identificador y no hay persistencia**, así que ningún análisis se
puede recuperar por enlace. La ruta documenta el hueco en vez de esconderlo.
El día que la respuesta traiga un id, solo falta implementar la búsqueda.

## Contrato V1.2

`POST /api/v1/analisis-energetico` — espejo de `DatosRegistroConsumo` del
back-end. El front habla con la API de Java, no con el servicio de ML.

**Obligatorios (4):** `consumo_kwh` (1–1000) · `tipo_inmueble` · `cantidad_equipos`
(1–100) · `horas_alto_consumo` (0–24)

**Opcionales (7)**, con el valor por defecto que aplica el back si no se envían:
`metros_cuadrados` (1000) · `antiguedad_vivienda` (50) · `zona_fria` (false) ·
`calidad_aislamiento` (Media) · `fuente_calefaccion` (Electricidad) ·
`fuente_agua_caliente` (Electricidad) · `uso_horario_pico` (false)

El formulario arma el **payload mínimo**: manda los obligatorios y solo los
opcionales que el usuario tocó. Cada opcional muestra su valor por defecto en
el propio control.

## Estados cubiertos

Inicial · opcionales desplegados · enviando · validación 400 con
`detalles[campo, mensaje]` · error del servidor · servicio no disponible ·
resultado · resultado sin recomendaciones · no encontrado.

## Estado de la integración

La llamada real funciona: el back-end **acepta el payload mínimo de 4 campos**.
Lo que hoy falla está aguas abajo — entre el back-end y el servicio de ML — y
llega al front como un error que la interfaz muestra correctamente. Cuando esa
integración se resuelva, empieza a llegar el 200 sin cambios acá.

## Comandos

| | |
|---|---|
| `npm run dev` | Servidor de desarrollo con proxy a la API |
| `npm run build` | Verifica tipos y compila a `dist/` |
| `npm run typecheck` | Solo verificación de tipos |
| `npm run preview` | Sirve `dist/` para revisar el build |

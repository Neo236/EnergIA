# Instrucciones para agentes

Contexto del proyecto para asistentes de IA. Este es el archivo canónico:
`CLAUDE.md` y `.github/copilot-instructions.md` apuntan acá, así que **editá
solo este**.

## Qué es esto

**EnergIA** clasifica el perfil de eficiencia energética de una vivienda o
comercio con un modelo de scikit-learn, estima su costo mensual y devuelve
recomendaciones. Tres servicios: front en React, API en Spring Boot, e
inferencia en FastAPI, con PostgreSQL detrás.

Nació como **EnergiAI** en el Hackathon ONE (equipo de ocho personas) y continúa
como proyecto propio. El historial y la autoría del equipo se conservan enteros.

## Convenciones

- **El código y la documentación están en español.** Nombres de clases, métodos,
  variables, ramas y mensajes de commit. `AnalisisEnergeticoService`, no
  `EnergyAnalysisService`. Mantené ese idioma.
- **Mensajes de commit:** `tipo(alcance): descripción en minúscula`, y un cuerpo
  que explique **por qué**, no qué. Mirá el historial reciente: los mensajes son
  largos a propósito y esa es la vara.
- **No agregues trailers de coautoría de agentes** (`Co-Authored-By:` apuntando a
  un asistente de IA) en los commits. Es una decisión explícita del proyecto.
- **Ramas:** `main` está protegida. Se trabaja en `feature/*`, `fix/*` o
  `chore/*` y se entra por Pull Request con la integración continua en verde.

## Trampas conocidas

Estas cosas parecen errores y no lo son. Cambiarlas rompe el sistema.

### `PROXY_BIND` no debe ser `0.0.0.0`

Docker publica sus puertos con reglas propias de iptables en la cadena FORWARD,
que las reglas de un firewall de host sobre INPUT no cubren. Un bind a `0.0.0.0`
queda alcanzable desde toda la red local aunque el firewall afirme lo contrario.
Se ata a la interfaz concreta por la que debe entrar el tráfico. En local, `127.0.0.1`.

### La tipografía Inter se sirve desde el propio origen

No la muevas a Google Fonts. Una CSP razonable (`style-src 'self'`,
`font-src 'self' data:`) bloquea la hoja de terceros y la aplicación cae a la
fuente de respaldo, perdiendo la tipografía del sistema de diseño. Los archivos
viven en `frontend/public/fonts/` y son de fuente variable — dos archivos
cubren los cuatro pesos.

### El `Dockerfile` del front debe copiar `public/`

Si falta, **el build no falla**: construye sin esos archivos, y después nginx
responde `/favicon.svg` y `/fonts/*.woff2` con el `index.html` del SPA por su
`try_files` — un `200` con `content-type: text/html`. Con `nosniff` delante,
el navegador rechaza la fuente y la `@font-face` queda en estado `error`. El
`200` hace que el síntoma despiste.

### El `.joblib` del modelo se versiona a propósito

`data-science/data/latest/` contiene el modelo entrenado, con una excepción
explícita al `*.joblib` del `.gitignore`. **No lo borres** por "limpiar
binarios": es la única copia, y el servicio lo lee desde ahí
(`STORAGE_LOCAL_ROOT=/app/data`). Sin él, el `ml-service` reentrena al arrancar
—tarda y produce un modelo equivalente pero no idéntico al que se sirve hoy.

### No agregues CORS

El front y la API comparten origen: el servicio `proxy` del Compose sirve la
aplicación en la raíz y enruta `/api/*` al backend. Si aparece un error de CORS,
el problema es el ruteo del proxy, no la falta de cabeceras.

### No reintroduzcas un modo simulado en el frontend

Existió uno: resolvía las dos operaciones de la API en el navegador para poder
trabajar sin levantar el back-end. Se retiró por dos motivos.

Reimplementaba la clasificación del modelo en TypeScript —sus propios umbrales,
su propio cálculo de confianza— y esa segunda versión podía separarse del
scikit-learn sin que nada lo señalara.

Y la aplicación llegó a estar desplegada compilada contra él. El síntoma no se
parecía a un fallo: el formulario respondía y la interfaz se veía perfecta, pero
los números eran inventados y los enlaces compartidos daban «no encontramos ese
análisis». Levantar el stack entero es un comando; ese es el camino.

### El CD verifica, no solo construye

`.github/workflows/cd.yml` corre en un runner propio al mergear a `main`. No
termina cuando `docker compose up` devuelve cero: después comprueba contra el
stack ya desplegado que el modelo se haya cargado del repositorio, que los
estáticos salgan con su tipo real y que un análisis de referencia devuelva lo
esperado. Si algo falla, vuelve solo al commit anterior.

Esos pasos no son ceremonia: cada uno corresponde a un fallo que ocurrió y que
un `up` exitoso no habría detectado. No los quites al tocar el flujo.

El análisis de verificación viaja con la cabecera `X-EnergIA-Sonda` para que no
se persista. Sin eso, cada despliegue dejaría una fila de basura.

### No existe un endpoint `DELETE`, y es a propósito

Sin un concepto de identidad no hay forma de saber que un análisis "es tuyo".
Exponer un borrado irreversible en una API pública sin autorización sería un
problema de seguridad. El historial del navegador (`localStorage`) solo quita la
fila de la lista local.

## Antes de dar algo por terminado

- Backend: `cd backend/analisis-energetico-api && ./mvnw test`
- Frontend: `npm --prefix frontend test` y `npm --prefix frontend run build`
- ML: `cd data-science/raw && python -m pytest`

Si el cambio se ve en el navegador, verificalo ahí — no alcanza con que compile.

## Dónde leer más

- [`docs/architecture/README.md`](./docs/architecture/README.md) — cómo se
  conectan las piezas y por qué
- [`docs/DESPLIEGUE.md`](./docs/DESPLIEGUE.md) — ejecución local y producción
- [`CONTRIBUTING.md`](./CONTRIBUTING.md) — flujo de trabajo

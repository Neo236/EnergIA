# 🚀 Despliegue

## Ejecución local

Solo hace falta Docker. Java, Node y Python corren dentro de los contenedores.

```bash
docker compose up --build -d
```

La aplicación queda en **http://localhost:8088** — front y API bajo el mismo
origen, igual que en producción.

Para bajarla:

```bash
docker compose down
```

Agregando `-v` se borra también el volumen de la base.

### Desarrollo servicio por servicio

Cuando conviene iterar rápido sobre una sola pieza:

**Front-end** (recarga en caliente, sin Docker):

```bash
npm --prefix frontend install && npm --prefix frontend run dev
```

Arranca en `http://localhost:5173`. Necesita el back-end corriendo: la
aplicación habla siempre con la API, no trae datos simulados. `VITE_API_DESTINO`
en `frontend/.env` indica a dónde reenviar `/api`.

**Back-end:**

```bash
cd backend/analisis-energetico-api && ./mvnw spring-boot:run
```

**Servicio de ML:**

```bash
cd data-science/raw
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn interfaces.api.app:app --reload --port 8000
```

> Necesita **Python 3.10**: `requirements.txt` está pinneado para esa versión y
> sobre una más nueva pip se pone a compilar numpy y scikit-learn desde código
> fuente, sin decir por qué. El entorno virtual tampoco es ceremonia — esas
> versiones fijas pisarían las de otros proyectos de la misma máquina.
>
> En Windows, `python` suele abrir la tienda de aplicaciones en vez de ejecutar
> nada; ahí el intérprete es `py`.

### Tests

**Back-end:**

```bash
cd backend/analisis-energetico-api && ./mvnw test
```

> Verás varias líneas `ERROR` en la salida y **es lo esperado**: hay tests que
> ejercitan a propósito los caminos de fallo — el detector de motor de
> persistencia equivocado, el manejador global de excepciones. Lo que importa es
> el `BUILD SUCCESS` del final.

**Front-end** (el `install` hace falta en un clon nuevo):

```bash
npm --prefix frontend install
npm --prefix frontend test
```

**Servicio de ML** — el camino corto es Docker, y evita una trampa:

```bash
cd data-science/raw
./scripts/run_tests_in_docker.sh
```

> `requirements.txt` está pinneado para **Python 3.10**, y lo dice en su primera
> línea. Instalarlo sobre un intérprete más nuevo no falla con un mensaje claro:
> pip no encuentra ruedas precompiladas para esas versiones exactas de numpy,
> pandas y scikit-learn, y se pone a compilarlas desde código fuente. Puede
> tardar mucho o quedarse sin terminar, sin que quede claro por qué.
>
> El script de arriba levanta una imagen con Python 3.10, así que la versión del
> intérprete deja de depender de la máquina.
>
> En Windows corre desde **WSL**, no desde Git Bash: este último entrega rutas
> POSIX que Docker Desktop no resuelve. Sin WSL, el equivalente a mano funciona
> igual porque usa rutas relativas:
>
> ```bash
> cd data-science
> docker build -f raw/Dockerfile.test -t energia-tests .
> docker run --rm energia-tests
> ```

Si preferís correrlos nativos, necesitás **Python 3.10** y un entorno virtual:

```bash
cd data-science/raw
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest
```

El entorno virtual no es ceremonia: esas versiones fijas pisarían las que
tengan otros proyectos de la misma máquina.

---

## Producción

El stack se despliega con Docker Compose y publica un solo puerto, en la
interfaz que indique `PROXY_BIND`. Qué hay delante —un proxy inverso que
termine TLS, un balanceador, nada— es decisión del alojamiento: la aplicación
no lo asume.

### Dónde vive

Estas rutas son las del servidor donde corre hoy, no un requisito del proyecto:
el stack funciona desde cualquier directorio. Se documentan porque el flujo de
despliegue las usa.

| Ruta | Qué hay |
|------|---------|
| `~/projects/EnergIA/` | El clon de `main`. Acá viven el `docker-compose.yml` y el `.env` |
| `~/deployments/energIA/backups/` | Los volcados de `pg_dump` |
| `~/gh-runner-energia/` | El runner de GitHub Actions |

Los respaldos van deliberadamente **fuera** del clon: son datos de esa máquina,
no del proyecto, y tienen que sobrevivir a un `git reset --hard` o a reclonar el
repositorio — que es justamente lo que hace el flujo de despliegue.

### Actualizar

**Automático.** Al mergear a `main`, el flujo `.github/workflows/cd.yml` se
ejecuta en el runner de este servidor: trae los cambios, respalda la base,
reconstruye, espera a que el stack responda y **verifica lo desplegado**. Si
algo falla, vuelve solo al commit anterior y lo relevanta.

Solo se dispara si cambió algo desplegable — un cambio de documentación no
reinicia el servicio. Para forzarlo sin commitear (por ejemplo tras editar el
`.env`, que no está en el repositorio): **Actions → Despliegue → Run workflow**.

A mano, si hiciera falta:

```bash
cd ~/projects/EnergIA && git pull && docker compose up -d --build
docker compose ps && curl -sI https://energia.neo236.fun | head -1
```

> **Por qué el CD verifica y no solo construye.** Que `docker compose up`
> termine sin error no dice que el sistema sirva: puede quedar un contenedor
> viejo en pie, o un `.env` desactualizado. El flujo repite contra el stack ya
> desplegado las mismas comprobaciones que el CI hace sobre uno efímero — que el
> modelo se cargó del repositorio, que los estáticos salen con su tipo real y
> que un análisis de referencia devuelve lo esperado.
>
> Ese análisis viaja con la cabecera `X-EnergIA-Sonda`, así que **no se
> persiste**: sin eso, cada despliegue dejaría una fila de basura en la base.

### Variables de entorno

El archivo `.env` vive en el servidor, junto al `docker-compose.yml`, con
permisos `600`. **No va al repositorio.**

| Variable | Valor | Para qué |
|----------|-------|----------|
| `STORAGE_BACKEND` | `local` | El modelo se lee del repositorio, sin servicios externos |
| `PROXY_BIND` | interfaz de entrada | Dónde escucha el único puerto publicado — ver abajo |
| `PROXY_PORT` | `8088` | El único puerto que se publica |
| `POSTGRES_DB` · `POSTGRES_USER` | `energia` | Base de datos |
| `POSTGRES_PASSWORD` | *(generado)* | `openssl rand -base64 36` |
| `TOKEN_SONDA_SALUD` | *(generado)* | Token de la sonda de verificación |

> ⚠️ **`PROXY_BIND` no debe ser `0.0.0.0` en un servidor compartido.** Docker
> publica sus puertos con reglas propias de iptables en la cadena FORWARD, que
> las reglas de un firewall de host sobre INPUT no cubren: el puerto quedaría
> alcanzable desde toda la red local aunque `ufw status` afirme lo contrario.
> Atado a una interfaz concreta, el puerto solo existe ahí.
>
> En local, el valor por defecto es `127.0.0.1` y no hace falta tocarlo.

### Verificar que el modelo cargó del repositorio

Al arrancar, el `ml-service` debe leer el `.joblib` versionado, no reentrenar:

```bash
docker compose logs ml-service | grep -i modelo
```

La línea esperada es `Modelo pre-cargado en memoria`. Si en cambio aparece que
está entrenando, el archivo de `data-science/data/latest/` no llegó a la imagen.

---

## Respaldos

Cada análisis recibe una URL propia y compartible, y la aplicación lo dice en
pantalla. Esa promesa vale lo que valga el volumen de PostgreSQL: si se pierde,
**todos los enlaces compartidos devuelven «no encontramos ese análisis»**.

`infra/respaldo.sh` hace un `pg_dump` comprimido y conserva los últimos 14. Se
instala una vez como timer de systemd de usuario:

```bash
mkdir -p ~/.config/systemd/user
cp infra/systemd/energia-respaldo.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now energia-respaldo.timer
```

> Requiere `loginctl enable-linger <usuario>` para que corra sin sesión abierta.
> Comprobalo con `loginctl show-user <usuario> --property=Linger`.

Verificar y operar:

```bash
systemctl --user list-timers energia-respaldo.timer   # cuándo corre
systemctl --user start energia-respaldo.service       # corre ahora
journalctl --user -u energia-respaldo.service -n 20   # qué pasó
```

### Restaurar

Un respaldo que nunca se restauró no es un respaldo. La prueba, sobre una base
descartable para no tocar la real:

```bash
docker compose exec -T db psql -U energia -d postgres -c "CREATE DATABASE prueba_restore;"
zcat ~/deployments/energIA/backups/energia-AAAAMMDD-HHMMSS.sql.gz \
  | docker compose exec -T db psql -U energia -d prueba_restore
docker compose exec -T db psql -U energia -d prueba_restore -c "SELECT count(*) FROM analisis_energetico;"
docker compose exec -T db psql -U energia -d postgres -c "DROP DATABASE prueba_restore;"
```

Para restaurar **de verdad**, el mismo volcado va contra la base real con el
stack detenido salvo la base:

```bash
docker compose stop backend
zcat <respaldo> | docker compose exec -T db psql -U energia -d energia
docker compose start backend
```

---

## Diagnóstico

| Síntoma | Dónde mirar |
|---------|-------------|
| Un servicio no levanta | `docker compose ps` y `docker compose logs <servicio>` |
| La API responde 502 | El backend no alcanza al `ml-service`: `docker compose logs ml-service` |
| Un archivo de `public/` da 404 | El `Dockerfile` del front debe copiar `public/`; ver [arquitectura](./architecture/README.md) |
| El sitio no responde desde afuera | Probar desde el origen que el firewall permite, no desde el propio servidor: un `curl` local puede fallar aunque el servicio esté bien |

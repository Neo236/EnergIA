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

Arranca en `http://localhost:5173` con `VITE_API_MODO=mock`, o sea con datos
simulados y sin necesidad de que el backend esté levantado. Para apuntar a una
API real, `VITE_API_MODO=real`.

**Back-end:**

```bash
cd backend/analisis-energetico-api && ./mvnw spring-boot:run
```

**Servicio de ML:**

```bash
cd data-science/raw
python -m pip install -r requirements.txt
python -m uvicorn interfaces.api.app:app --reload --port 8000
```

### Tests

```bash
cd backend/analisis-energetico-api && ./mvnw test   # backend
npm --prefix frontend test                          # frontend
```

El servicio de ML necesita además las dependencias de test, que no van en la
imagen de producción:

```bash
cd data-science/raw
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m pytest
```

---

## Producción

La aplicación corre en un servidor propio, detrás de un proxy de borde que
termina TLS y aplica WAF y límites de tasa. El servidor **no está expuesto a
internet**: el borde lo alcanza por un túnel WireGuard.

### Actualizar

El despliegue es **manual y deliberado**. Son tres comandos en el servidor:

```bash
cd ~/projects/EnergIA && git pull && docker compose up -d --build
```

Y la verificación:

```bash
docker compose ps && curl -sI https://energia.neo236.fun | head -1
```

> **No hay despliegue continuo.** El proyecto tuvo tres flujos de CD durante el
> hackathon que desplegaban a una VM con un runner propio; esa infraestructura ya
> no existe y los flujos fueron retirados. Para un proyecto que cambia poco, un
> `git pull` explícito es más simple de razonar que un pipeline que hay que
> mantener. La integración continua (build y tests en cada PR) **sí** sigue
> activa.

### Variables de entorno

El archivo `.env` vive en el servidor, junto al `docker-compose.yml`, con
permisos `600`. **No va al repositorio.**

| Variable | Valor | Para qué |
|----------|-------|----------|
| `STORAGE_BACKEND` | `local` | El modelo se lee del repositorio, sin servicios externos |
| `PROXY_BIND` | IP del túnel | Interfaz donde escucha el único puerto publicado — ver abajo |
| `PROXY_PORT` | `8088` | El único puerto que se publica |
| `POSTGRES_DB` · `POSTGRES_USER` | `energia` | Base de datos |
| `POSTGRES_PASSWORD` | *(generado)* | `openssl rand -base64 36` |
| `TOKEN_SONDA_SALUD` | *(generado)* | Token de la sonda de verificación |

> ⚠️ **`PROXY_BIND` no debe ser `0.0.0.0` en un servidor compartido.** Docker
> publica sus puertos con reglas propias de iptables en la cadena FORWARD, que
> las reglas de un firewall de host sobre INPUT no cubren: el puerto quedaría
> alcanzable desde toda la red local aunque `ufw status` afirme lo contrario.
> Atado a la IP del túnel, el puerto solo existe en esa interfaz.
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

## Diagnóstico

| Síntoma | Dónde mirar |
|---------|-------------|
| Un servicio no levanta | `docker compose ps` y `docker compose logs <servicio>` |
| La API responde 502 | El backend no alcanza al `ml-service`: `docker compose logs ml-service` |
| Un archivo de `public/` da 404 | El `Dockerfile` del front debe copiar `public/`; ver [arquitectura](./architecture/README.md) |
| El sitio no responde desde afuera | Probar desde el borde, no desde el servidor: la regla del firewall solo permite el origen del túnel |

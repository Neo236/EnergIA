# ==========================================
# Front-End EnergIA — Vite + React + TypeScript
#
# Multi-etapa: se compila con Node y se sirve con nginx. La imagen final
# no lleva Node ni node_modules — solo los estáticos y el servidor.
# ==========================================

# ---------- etapa de build ----------
FROM node:24-alpine AS build

WORKDIR /app

# package*.json antes que el código: mientras las dependencias no cambien,
# Docker reutiliza la capa de `npm ci`, que es la parte lenta del build en
# una VM de 2 OCPUs.
COPY package.json package-lock.json ./
RUN npm ci

COPY tsconfig*.json vite.config.ts index.html ./
COPY src/ ./src/

# public/ va tal cual a la raiz de dist/ sin pasar por el bundler: es la via
# para los archivos que se piden por ruta fija desde index.html (favicon,
# fuentes). Faltaba, y el sintoma es enganoso — Vite no falla, simplemente
# construye sin ellos, y despues nginx responde esas rutas con el index.html
# del SPA por su `try_files`. El navegador recibe un text/html donde esperaba
# una fuente y, como el proxy manda `X-Content-Type-Options: nosniff`, la
# descarta: la @font-face queda en estado "error" y el sitio cae a la fuente
# de respaldo. El favicon venia roto por esto mismo en todos los despliegues
# en contenedor.
COPY public/ ./public/

# VITE_API_MODO se resuelve en tiempo de compilación (Vite lo inserta en el
# bundle), así que se elige acá y no en runtime.
#
# El valor por defecto es `real`, y el motivo importa: durante un tiempo fue
# `mock`, y una imagen construida sin pasar el argumento producía una
# aplicación que fabricaba sus resultados en el navegador. Eso no se parece a
# un error — el formulario responde, muestra un análisis, la interfaz se ve
# perfecta. Lo único que delata el problema es que los números son inventados
# y que los enlaces compartidos dan "no encontramos ese análisis".
#
# Un valor por defecto que convierte un despliegue roto en uno aparentemente
# sano es peor que no tener valor por defecto. Para desarrollar sin backend
# está `npm run dev`, que lee el .env del frontend.
ARG VITE_API_MODO=real
ENV VITE_API_MODO=${VITE_API_MODO}

RUN npm run build

# ---------- etapa de servicio ----------
# Base fijada por digest y no por etiqueta. `1.27-alpine` es móvil: los
# mantenedores publican parches bajo el mismo nombre, así que el mismo
# Dockerfile puede producir imágenes distintas en dos días. Con el digest,
# reconstruir un commit viejo da exactamente la misma imagen — que es lo
# que hace confiable el rollback.
#
# Es el digest del índice multi-arquitectura (verificado: idéntico en amd64
# y arm64), así que sirve tanto en el CI x86 como en la VM ARM.
#
# Para actualizar y recibir parches de seguridad:
#   docker pull nginxinc/nginx-unprivileged:1.27-alpine
#   docker image inspect nginxinc/nginx-unprivileged:1.27-alpine \
#     --format '{{index .RepoDigests 0}}'
FROM nginxinc/nginx-unprivileged:1.27-alpine@sha256:65e3e85dbaed8ba248841d9d58a899b6197106c23cb0ff1a132b7bfe0547e4c0

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 8080

# La imagen de Alpine no trae curl; busybox wget sí.
#
# 127.0.0.1 y no `localhost`: dentro del contenedor, localhost resuelve
# primero a ::1 y nginx solo escucha en IPv4 (0.0.0.0:8080), así que el
# chequeo fallaba con "Connection refused" aunque el sitio respondiera
# perfecto. El contenedor quedaba marcado unhealthy sin estarlo.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q --spider http://127.0.0.1:8080/ || exit 1

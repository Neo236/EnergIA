#!/usr/bin/env bash
#
# Despliega EnergIA en el servidor, desde un commit.
#
#   ./infra/desplegar.sh
#
# Lo corre el administrador de la flota en el servidor, sobre una copia del
# commit que se despliega (no sobre un clon de trabajo): el arbol de ese commit
# queda en ~/deployments/energia/codigo/, sin permiso de escritura, y el stack
# corre desde ahi. Cambiar algo es otro commit y otro despliegue.
#
# Antes de correrlo tienen que estar, mandados por el administrador:
#   ~/deployments/energia/variables.env   lo que no es secreto (PROXY_BIND...)
#   /run/secretos/energia/                los secretos, en memoria, un archivo
#                                         por secreto (POSTGRES_PASSWORD,
#                                         TOKEN_SONDA_SALUD) y .listo
#
# Respalda la base, construye las imagenes del commit, levanta el stack y
# verifica lo desplegado (las mismas comprobaciones que la CI). Si algo falla,
# vuelve a lo que estaba. Ver docs/DESPLIEGUE.md.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${ENERGIA_DESPLIEGUE:-$HOME/deployments/energia}"
SECRETOS=/run/secretos/energia
CLON_VIEJO="$HOME/projects/EnergIA"   # de donde corria antes (la primera vez)
UNIDADES="$HOME/.config/systemd/user"

falla() { echo "ERROR: $*" >&2; exit 1; }

commit="$(git -C "$REPO" rev-parse --short HEAD)"
[ -z "$(git -C "$REPO" status --porcelain)" ] || falla "hay cambios sin commitear: se despliega un commit"
[ -f "$DEST/variables.env" ] || falla "falta $DEST/variables.env (lo manda el administrador con los secretos)"
[ -e "$SECRETOS/.listo" ] || falla "faltan los secretos en $SECRETOS (los manda el administrador)"
for s in POSTGRES_PASSWORD TOKEN_SONDA_SALUD; do
    [ -s "$SECRETOS/$s" ] || falla "falta el secreto $s"
done
# Un secreto en las variables le ganaria al archivo (y quedaria en disco).
if grep -qE '^(POSTGRES_PASSWORD|DB_PASSWORD|TOKEN_SONDA_SALUD)=' "$DEST/variables.env"; then
    falla "variables.env tiene un secreto: va solo en $SECRETOS"
fi
echo "EnergIA $commit -> $DEST"

# --- Respaldar antes de tocar nada --------------------------------------------
# Si el despliegue sale mal, el rollback del codigo es volver a la carpeta
# anterior; el de los datos solo existe si alguien lo hizo antes.
mkdir -p "$DEST"; chmod 700 "$DEST"
if [ -d "$HOME/deployments/energIA/backups" ] && [ ! -e "$DEST/backups" ]; then
    # Donde quedaban los volcados cuando el stack corria desde el clon.
    mv "$HOME/deployments/energIA/backups" "$DEST/backups"
    rmdir "$HOME/deployments/energIA" 2>/dev/null || true
    echo "Volcados anteriores movidos a $DEST/backups"
fi
if [ -d "$DEST/codigo" ]; then
    ENERGIA_DESPLIEGUE="$DEST" "$DEST/codigo/infra/respaldo.sh" "$DEST/backups"
elif [ -f "$CLON_VIEJO/.env" ]; then
    ENERGIA_DESPLIEGUE="$CLON_VIEJO" "$REPO/infra/respaldo.sh" "$DEST/backups"
fi

# --- El codigo del commit, sin escritura ---------------------------------------
nuevo="$DEST/codigo.nuevo"
[ ! -e "$nuevo" ] || { chmod -R u+w "$nuevo"; rm -rf "$nuevo"; }
mkdir "$nuevo"
git -C "$REPO" archive HEAD | tar -x -C "$nuevo"
printf '%s\n' "$commit" > "$nuevo/VERSION"
chmod -R a-w "$nuevo"
if [ -d "$DEST/codigo.anterior" ]; then chmod -R u+w "$DEST/codigo.anterior"; rm -rf "$DEST/codigo.anterior"; fi
[ ! -d "$DEST/codigo" ] || mv "$DEST/codigo" "$DEST/codigo.anterior"
mv "$nuevo" "$DEST/codigo"
[ ! -f "$DEST/.env" ] || cp -p "$DEST/.env" "$DEST/.env.anterior"
(
    umask 077
    {
        echo "# Lo arma infra/desplegar.sh ($commit). No se edita: se cambia en el administrador."
        cat "$DEST/variables.env"
        echo
        echo "COMPOSE_FILE=codigo/docker-compose.yml:codigo/infra/docker-compose.secretos.yml"
        echo "SECRETOS_ENERGIA=$SECRETOS"
        echo "BACKEND_TAG=$commit"
        echo "ML_TAG=$commit"
        echo "FRONTEND_TAG=$commit"
    } > "$DEST/.env"
)

# --- Las unidades: el stack arranca cuando llegan los secretos -----------------
mkdir -p "$UNIDADES"
install -m 644 "$DEST"/codigo/infra/systemd/energia.service "$DEST"/codigo/infra/systemd/energia-secretos.path \
    "$DEST"/codigo/infra/systemd/energia-respaldo.service "$DEST"/codigo/infra/systemd/energia-respaldo.timer "$UNIDADES/"
systemctl --user daemon-reload
systemctl --user enable energia-secretos.path energia-respaldo.timer >/dev/null

# --- Volver a lo que estaba, si algo de lo que sigue falla ---------------------
volver() {
    trap - ERR
    set +e
    echo "El despliegue fallo. Volviendo a lo que estaba." >&2
    (cd "$DEST" && docker compose logs --tail=80) >&2 || true
    if [ -d "$DEST/codigo.anterior" ]; then
        chmod -R u+w "$DEST/codigo"; rm -rf "$DEST/codigo"
        mv "$DEST/codigo.anterior" "$DEST/codigo"
        mv "$DEST/.env.anterior" "$DEST/.env"
        systemctl --user restart energia.service
        echo "Volvio a $(cat "$DEST/codigo/VERSION")." >&2
    else
        # La primera vez: el stack corria desde el clon, con sus imagenes :latest.
        systemctl --user disable --now energia-secretos.path >/dev/null 2>&1 || true
        (cd "$CLON_VIEJO" && docker compose up -d --force-recreate)
        echo "Volvio al stack del clon ($CLON_VIEJO)." >&2
    fi
    exit 1
}
trap volver ERR

# --- Construir y levantar --------------------------------------------------------
(cd "$DEST" && docker compose build)
systemctl --user restart energia.service
systemctl --user start energia-secretos.path

# --- Verificar lo desplegado (como la CI, ahora contra el que quedo sirviendo) ---
# Desde adentro de la red de Compose: el puerto publicado solo admite el origen
# del borde, y un curl desde este servidor se descartaria.
en_red() { docker run --rm --network energia_energia-network curlimages/curl:latest "$@"; }
for i in $(seq 1 30); do
    if en_red -fsS --max-time 5 http://proxy:8088/actuator/health/readiness > /dev/null 2>&1; then
        echo "Responde tras ~$((i * 10))s."; break
    fi
    [ "$i" -lt 30 ] || { echo "El stack no respondio en 5 minutos." >&2; false; }
    sleep 10
done
(cd "$DEST" && docker compose logs ml-service) | grep -q "Modelo pre-cargado en memoria" \
    || { echo "El servicio de ML no cargo el modelo del repositorio." >&2; false; }
echo "  modelo: cargado de data/latest/"
tipo=$(en_red -fsS -o /dev/null -w '%{content_type}' http://proxy:8088/fonts/inter-latin.woff2)
case "$tipo" in
    font/woff2*) echo "  estaticos: $tipo" ;;
    *) echo "  fuente servida como '$tipo': public/ no llego a la imagen." >&2; false ;;
esac
# El analisis de verificacion es una sonda: no se persiste. Con el token del
# archivo en memoria; si no llego al backend, la respuesta trae id.
respuesta=$(en_red -fsS --max-time 30 -X POST http://proxy:8088/api/v1/analisis-energetico \
    -H 'Content-Type: application/json' -H "X-EnergIA-Sonda: $(cat "$SECRETOS/TOKEN_SONDA_SALUD")" \
    -d '{"consumo_kwh":420,"cantidad_equipos":10,"tipo_inmueble":"Casa",
         "uso_horario_pico":false,"horas_alto_consumo":12,"zona_fria":false,
         "calidad_aislamiento":"Media","fuente_calefaccion":"Electricidad",
         "fuente_agua_caliente":"Electricidad"}')
case "$respuesta" in
    *'"categoria":"Moderado"'*) echo "  analisis de referencia: correcto" ;;
    *) echo "  analisis inesperado: $respuesta" >&2; false ;;
esac
if grep -qE '"id":"[0-9a-f-]{36}"' <<< "$respuesta"; then
    echo "  la sonda se guardo: el token no llego al backend" >&2; false
fi
echo "  sonda: no se guardo"

trap - ERR
printf '%s\ndesplegado el %s\n' "$commit" "$(date '+%F %T')" > "$DEST/VERSION"
(cd "$DEST" && docker compose ps --format 'table {{.Service}}\t{{.Status}}')
echo "EnergIA $commit desplegado."

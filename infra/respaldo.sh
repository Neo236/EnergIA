#!/usr/bin/env bash
#
# Respalda la base de datos de EnergIA.
#
#   ./infra/respaldo.sh [directorio-destino]
#
# Por que existe: cada analisis recibe una URL propia y compartible, y la
# aplicacion lo dice en pantalla ("guarda el enlace de esta pagina para volver
# al resultado"). Esa promesa vale lo que valga el volumen de PostgreSQL — si
# se pierde, todos los enlaces compartidos devuelven "no encontramos ese
# analisis". Un volcado diario es lo que separa una promesa de una intencion.
#
# Se instala como timer de systemd de usuario; ver infra/systemd/ y
# docs/DESPLIEGUE.md.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Por defecto, junto al despliegue y no dentro del repositorio: los volcados son
# datos de esta maquina, no del proyecto.
DESTINO="${1:-$(cd "$REPO/.." && pwd)/backups}"
CONSERVAR=14

cd "$REPO"

# Las credenciales viven en el .env del servidor, no en el repositorio.
if [ ! -f .env ]; then
    echo "No se encontro $REPO/.env" >&2
    exit 1
fi
# shellcheck disable=SC1091
set -a; . ./.env; set +a

USUARIO="${POSTGRES_USER:-energia}"
BASE="${POSTGRES_DB:-energia}"

mkdir -p "$DESTINO"
ARCHIVO="$DESTINO/energia-$(date +%Y%m%d-%H%M%S).sql.gz"

# Se escribe primero a un temporal y se renombra al final. Si el volcado se
# corta a la mitad —el contenedor se reinicia, se llena el disco— lo que queda
# es un archivo .parcial y no un respaldo truncado con nombre de valido, que es
# la clase de respaldo que solo se descubre inservible el dia que se necesita.
TEMPORAL="$ARCHIVO.parcial"
trap 'rm -f "$TEMPORAL"' EXIT

if ! docker compose exec -T db pg_dump -U "$USUARIO" -d "$BASE" | gzip > "$TEMPORAL"; then
    echo "pg_dump fallo" >&2
    exit 1
fi

# Un volcado vacio significa que algo salio mal aunque pg_dump devolviera 0.
if [ ! -s "$TEMPORAL" ]; then
    echo "El volcado quedo vacio" >&2
    exit 1
fi

mv "$TEMPORAL" "$ARCHIVO"
trap - EXIT

echo "Respaldo: $ARCHIVO ($(du -h "$ARCHIVO" | cut -f1))"

# Rotacion. `ls -t` ordena por fecha de modificacion, mas fiable que el nombre.
sobrantes=$(ls -t "$DESTINO"/energia-*.sql.gz 2>/dev/null | tail -n "+$((CONSERVAR + 1))" || true)
if [ -n "$sobrantes" ]; then
    echo "$sobrantes" | while IFS= read -r viejo; do
        rm -f "$viejo"
        echo "Eliminado por rotacion: $(basename "$viejo")"
    done
fi

total=$(find "$DESTINO" -maxdepth 1 -name 'energia-*.sql.gz' | wc -l)
echo "Respaldos conservados: $total (tope $CONSERVAR)"

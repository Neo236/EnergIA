#!/usr/bin/env bash
#
# Verifica el EnergIA desplegado desde adentro de la red del stack (las mismas
# comprobaciones que la CI). La corre energia-verificar.service, que el motor de
# despliegues de la flota pide después de levantar una versión nueva: si falla,
# el motor vuelve solo a la anterior (despliegue.yaml, docs/DESPLIEGUE.md).
#
# Desde adentro porque el puerto publicado solo admite el origen del borde.
set -euo pipefail
DIR="${ENERGIA_DESPLIEGUE:-$HOME/deployments/energia}"
SECRETOS="${SECRETOS_ENERGIA:-/run/secretos/energia}"
cd "$DIR"
dc() { docker compose --env-file variables.env --env-file .env "$@"; }
en_red() { docker run --rm --network energia_energia-network curlimages/curl:8.21.0 "$@"; }

for i in $(seq 1 30); do
    if en_red -fsS --max-time 5 http://proxy:8088/actuator/health/readiness > /dev/null 2>&1; then
        echo "Responde tras ~$((i * 10))s."; break
    fi
    [ "$i" -lt 30 ] || { echo "El stack no respondio en 5 minutos." >&2; exit 1; }
    sleep 10
done

dc logs ml-service | grep -q "Modelo pre-cargado en memoria" \
    || { echo "El servicio de ML no cargo el modelo del repositorio." >&2; exit 1; }
echo "  modelo: cargado de data/latest/"

tipo=$(en_red -fsS -o /dev/null -w '%{content_type}' http://proxy:8088/fonts/inter-latin.woff2)
case "$tipo" in
    font/woff2*) echo "  estaticos: $tipo" ;;
    *) echo "  fuente servida como '$tipo': public/ no llego a la imagen." >&2; exit 1 ;;
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
    *) echo "  analisis inesperado: $respuesta" >&2; exit 1 ;;
esac
if grep -qE '"id":"[0-9a-f-]{36}"' <<< "$respuesta"; then
    echo "  la sonda se guardo: el token no llego al backend" >&2; exit 1
fi
echo "  sonda: no se guardo"

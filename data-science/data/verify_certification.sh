#!/usr/bin/env bash
# verify_certification.sh
#
# Verifica que el modelo servido cumple la certificacion. Falla
# (exit 1) si alguno de los chequeos no pasa.
#
# Uso:
#   ./data-science/data/verify_certification.sh
#
# Asume que el servicio ML esta corriendo en http://127.0.0.1:8000
# con STORAGE_BACKEND=local. Para staging/produccion, cambiar URL.
#
# Variables de entorno:
#   ML_SERVICE_URL     default http://127.0.0.1:8000
#   BINDING_FILE       default data-science/data/MODEL_BINDING.sha256
#   SKIP_LOCAL_FILES   si "1", skipea checks de archivos locales
#                     (CHECKSUMS + MODEL_BINDING) — util en CI donde
#                     el checkout no tiene los .joblib (gitignored)
#   CURL_TIMEOUT       timeout en segundos para todos los curl
#                     (default: 10s). Si el servicio cuelga, el
#                     script no se cuelga con el.
#
# Tipos de checks:
#   - LOCAL FILE CHECKS (CHECKSUMS, MODEL_BINDING): validan que los
#     archivos en disco matchean el binding. Solo tienen sentido donde
#     los .joblib existen localmente (despues de entrenar).
#   - CONTAINER CHECKS (/health, /model-info, golden profiles):
#     validan que el modelo servido se comporta como el certificacion
#     exige. Son los checks minimos en cualquier entorno (CI, staging,
#     produccion).

# NO usar `set -e` global: queremos ejecutar TODOS los checks incluso
# si uno falla, para ver el resumen completo al final.

URL="${ML_SERVICE_URL:-http://127.0.0.1:8000}"
BINDING_FILE="${BINDING_FILE:-data-science/data/MODEL_BINDING.sha256}"
DATA_DIR="data-science/data"
SKIP_LOCAL="${SKIP_LOCAL_FILES:-0}"
CURL_TIMEOUT="${CURL_TIMEOUT:-10}"
PASS=0
FAIL=0
SKIP=0
declare -a FAILURES=()

# --- Pre-flight: dependencias ------------------------------------------------

section_preflight() {
    echo ""
    echo "=== Pre-flight (dependencias) ==="
    for tool in curl sha256sum python3 awk grep; do
        if command -v "$tool" >/dev/null 2>&1; then
            echo "  [OK]   $tool disponible"
        else
            echo "  [FAIL] $tool no encontrado en PATH"
            FAIL=$((FAIL + 1))
            FAILURES+=("$tool no instalado")
        fi
    done
    # Si una dependencia falta, abortar: los checks daran resultados raros.
    if [ $FAIL -gt 0 ]; then
        echo ""
        echo "Faltan dependencias. Abortando."
        exit 2
    fi
}

# --- Helpers ----------------------------------------------------------------

check_pass() {
    echo "  [OK]   $1"
    PASS=$((PASS + 1))
}

check_fail() {
    local msg="$1"
    echo "  [FAIL] $msg"
    FAIL=$((FAIL + 1))
    FAILURES+=("$msg")
}

check_skip() {
    echo "  [SKIP] $1"
    SKIP=$((SKIP + 1))
}

section() {
    echo ""
    echo "=== $1 ==="
}

# Truncar respuestas grandes para evitar leaks en logs de FAIL.
truncate_response() {
    local s="$1"
    local max="${2:-200}"
    if [ "${#s}" -gt "$max" ]; then
        echo "${s:0:$max}...[truncado ${#s} bytes]"
    else
        echo "$s"
    fi
}

# --- Check 1: hashes locales (CHECKSUMS.sha256) -----------------------------
# IMPORTANTE: exit code 0 + cada archivo OK explicitamente.
# Antes verificaba "grep : OK" lo que aproba con 1 OK + 1 FAILED.

section "1. Dataset canonico (CHECKSUMS.sha256)"
if [ "$SKIP_LOCAL" = "1" ]; then
    check_skip "CHECKSUMS.sha256 (SKIP_LOCAL_FILES=1)"
else
    cd "$DATA_DIR"
    CHECKSUM_OUT=$(sha256sum -c CHECKSUMS.sha256 2>&1)
    CHECKSUM_EXIT=$?
    if [ $CHECKSUM_EXIT -eq 0 ]; then
        CSV_OK=$(echo "$CHECKSUM_OUT" | grep -c "database_beta.csv: OK" || true)
        JSON_OK=$(echo "$CHECKSUM_OUT" | grep -c "database_beta.json: OK" || true)
        if [ "$CSV_OK" -eq 1 ] && [ "$JSON_OK" -eq 1 ]; then
            check_pass "database_beta.csv OK"
            check_pass "database_beta.json OK"
        else
            check_fail "exit 0 pero faltan lineas OK (CSV=$CSV_OK, JSON=$JSON_OK)"
        fi
    else
        check_fail "sha256sum -c CHECKSUMS.sha256 fallo (exit=$CHECKSUM_EXIT): $(truncate_response "$CHECKSUM_OUT")"
    fi
    cd - > /dev/null
fi

# --- Check 2: binding modelo+dataset+metricas -------------------------------

section "2. Binding modelo+dataset+metricas (MODEL_BINDING.sha256)"
BIND_MODEL_SHA=""
if [ "$SKIP_LOCAL" = "1" ]; then
    check_skip "MODEL_BINDING.sha256 (SKIP_LOCAL_FILES=1)"
else
    cd "$DATA_DIR"
    BIND_OUT=$(sha256sum -c MODEL_BINDING.sha256 2>&1)
    BIND_EXIT=$?
    if [ $BIND_EXIT -eq 0 ]; then
        for f in modelo_eficiencia_v1.joblib metricas_v1.joblib database_beta.json database_beta.csv; do
            if echo "$BIND_OUT" | grep -q "$f: OK"; then
                check_pass "$f OK"
            else
                check_fail "$f falta o no es OK en MODEL_BINDING.sha256"
            fi
        done
        # Parsear SOLO lineas de datos (formato "<hash>  <file>", 2 espacios).
        # grep simple matchea tambien las lineas de comentario que mencionan
        # "modelo_eficiencia_v1.joblib" en el texto explicativo, devolviendo
        # "# ..." como primer campo. Eso rompe la comparacion posterior.
        BIND_MODEL_SHA=$(grep -v '^#' MODEL_BINDING.sha256 | awk '$2 == "modelo_eficiencia_v1.joblib" {print $1}')
    else
        check_fail "sha256sum -c MODEL_BINDING.sha256 fallo (exit=$BIND_EXIT): $(truncate_response "$BIND_OUT")"
    fi
    cd - > /dev/null
fi

# --- Check 3: servicio vivo (/health) ---------------------------------------

section "3. Servicio vivo (/health)"
HEALTH_RESP=$(curl -s --max-time "$CURL_TIMEOUT" -w "\nHTTP_CODE:%{http_code}" "$URL/health" 2>&1)
HEALTH_CODE=$(echo "$HEALTH_RESP" | grep "HTTP_CODE:" | cut -d: -f2)
HEALTH_BODY=$(echo "$HEALTH_RESP" | grep -v "HTTP_CODE:")
if [ "$HEALTH_CODE" = "200" ] && echo "$HEALTH_BODY" | grep -q '"status":"healthy"'; then
    check_pass "/health -> 200 + status=healthy"
else
    check_fail "/health no respondio 200/healthy (code=$HEALTH_CODE, body=$(truncate_response "$HEALTH_BODY"))"
fi

# --- Check 4: identidad del modelo servido (/model-info) ---------------------

section "4. Identidad del modelo servido (/model-info)"
MODEL_RESP=$(curl -s --max-time "$CURL_TIMEOUT" -w "\nHTTP_CODE:%{http_code}" "$URL/model-info" 2>&1)
MODEL_CODE=$(echo "$MODEL_RESP" | grep "HTTP_CODE:" | cut -d: -f2)
MODEL_BODY=$(echo "$MODEL_RESP" | grep -v "HTTP_CODE:")
if [ "$MODEL_CODE" = "200" ]; then
    # Usar un unico python3 que falle si el body no es JSON valido.
    PARSED=$(echo "$MODEL_BODY" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('sha256', ''))
    print(d.get('model_path', ''))
    print(d.get('loaded', ''))
    print(d.get('size_bytes', ''))
except Exception as e:
    sys.stderr.write('JSON parse error: %s\n' % e)
    sys.exit(1)
" 2>&1)
    PARSE_EXIT=$?
    if [ $PARSE_EXIT -ne 0 ]; then
        check_fail "/model-info devolvio 200 pero body no es JSON: $(truncate_response "$MODEL_BODY")"
    else
        SERVED_SHA=$(echo "$PARSED" | sed -n '1p')
        SERVED_PATH=$(echo "$PARSED" | sed -n '2p')
        SERVED_LOADED=$(echo "$PARSED" | sed -n '3p')
        SERVED_SIZE=$(echo "$PARSED" | sed -n '4p')

        check_pass "/model-info -> 200 (path=$SERVED_PATH, loaded=$SERVED_LOADED, size=$SERVED_SIZE bytes)"

        # Comparacion SHA binding vs servido:
        if [ -n "$BIND_MODEL_SHA" ] && [ -n "$SERVED_SHA" ]; then
            if [ "$SERVED_SHA" = "$BIND_MODEL_SHA" ]; then
                check_pass "sha256 servido == binding ($SERVED_SHA)"
            else
                check_fail "sha256 servido ($SERVED_SHA) != binding ($BIND_MODEL_SHA) — modelo no es el certificado"
            fi
        elif [ "$SKIP_LOCAL" = "1" ]; then
            check_skip "comparacion SHA binding vs servido (SKIP_LOCAL_FILES=1, sin binding cargado)"
        else
            check_fail "no se pudo comparar SHA (binding o servicio no disponibles)"
        fi
    fi
else
    check_fail "/model-info no respondio 200 (code=$MODEL_CODE, body=$(truncate_response "$MODEL_BODY"))"
fi

# --- Check 5: 3 perfiles golden ---------------------------------------------

section "5. 3 perfiles golden (consumir /analisis-energetico)"

# Perfil 1: esperado Eficiente
P1='{"consumo_kwh":180,"tipo_inmueble":"Casa","horas_alto_consumo":4,"cantidad_equipos":10,"uso_horario_pico":false,"zona_fria":false,"fuente_calefaccion":"Solar","fuente_agua_caliente":"Solar","metros_cuadrados":80,"antiguedad_vivienda":5,"calidad_aislamiento":"Muy Alta"}'
P1_RESP=$(curl -s --max-time "$CURL_TIMEOUT" -X POST "$URL/analisis-energetico" -H "Content-Type: application/json" -d "$P1" 2>&1)
P1_PARSED=$(echo "$P1_RESP" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('categoria', ''))
    print(d.get('probabilidad', ''))
except Exception:
    sys.exit(1)
" 2>/dev/null)
P1_CAT=$(echo "$P1_PARSED" | sed -n '1p')
P1_PROB=$(echo "$P1_PARSED" | sed -n '2p')
if [ "$P1_CAT" = "Eficiente" ]; then
    check_pass "Perfil 1 (esperado Eficiente) -> categoria=$P1_CAT, prob=$P1_PROB"
else
    check_fail "Perfil 1 esperaba Eficiente, obtuvo '$P1_CAT' (resp=$(truncate_response "$P1_RESP"))"
fi

# Perfil 2: esperado Moderado
P2='{"consumo_kwh":420,"tipo_inmueble":"Departamento","horas_alto_consumo":8,"cantidad_equipos":15,"uso_horario_pico":false,"zona_fria":false,"fuente_calefaccion":"Electricidad","fuente_agua_caliente":"Electricidad","metros_cuadrados":100,"antiguedad_vivienda":40,"calidad_aislamiento":"Media"}'
P2_RESP=$(curl -s --max-time "$CURL_TIMEOUT" -X POST "$URL/analisis-energetico" -H "Content-Type: application/json" -d "$P2" 2>&1)
P2_PARSED=$(echo "$P2_RESP" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('categoria', ''))
    print(d.get('probabilidad', ''))
except Exception:
    sys.exit(1)
" 2>/dev/null)
P2_CAT=$(echo "$P2_PARSED" | sed -n '1p')
P2_PROB=$(echo "$P2_PARSED" | sed -n '2p')
if [ "$P2_CAT" = "Moderado" ]; then
    check_pass "Perfil 2 (esperado Moderado) -> categoria=$P2_CAT, prob=$P2_PROB"
else
    check_fail "Perfil 2 esperaba Moderado, obtuvo '$P2_CAT' (resp=$(truncate_response "$P2_RESP"))"
fi

# Perfil 3: esperado Ineficiente
P3='{"consumo_kwh":780,"tipo_inmueble":"Casa","horas_alto_consumo":18,"cantidad_equipos":35,"uso_horario_pico":true,"zona_fria":true,"fuente_calefaccion":"Electricidad","fuente_agua_caliente":"Electricidad","metros_cuadrados":200,"antiguedad_vivienda":80,"calidad_aislamiento":"Muy Baja"}'
P3_RESP=$(curl -s --max-time "$CURL_TIMEOUT" -X POST "$URL/analisis-energetico" -H "Content-Type: application/json" -d "$P3" 2>&1)
P3_PARSED=$(echo "$P3_RESP" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('categoria', ''))
    print(d.get('probabilidad', ''))
except Exception:
    sys.exit(1)
" 2>/dev/null)
P3_CAT=$(echo "$P3_PARSED" | sed -n '1p')
P3_PROB=$(echo "$P3_PARSED" | sed -n '2p')
if [ "$P3_CAT" = "Ineficiente" ]; then
    check_pass "Perfil 3 (esperado Ineficiente) -> categoria=$P3_CAT, prob=$P3_PROB"
else
    check_fail "Perfil 3 esperaba Ineficiente, obtuvo '$P3_CAT' (resp=$(truncate_response "$P3_RESP"))"
fi

# --- Resumen ----------------------------------------------------------------

echo ""
echo "=== RESUMEN ==="
echo "Checks OK:   $PASS"
echo "Checks SKIP: $SKIP"
echo "Checks FAIL: $FAIL"
if [ $FAIL -gt 0 ]; then
    echo ""
    echo "FAILURES:"
    for f in "${FAILURES[@]}"; do
        echo "  - $f"
    done
    exit 1
fi
echo ""
echo "Certificacion VERIFICADA. Exit 0."
exit 0
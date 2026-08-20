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

set -u  # falla en variable sin definir, pero NO abortar en error
        # (queremos ver todos los checks incluso si uno falla)

URL="${ML_SERVICE_URL:-http://127.0.0.1:8000}"
BINDING_FILE="${BINDING_FILE:-data-science/data/MODEL_BINDING.sha256}"
DATA_DIR="data-science/data"
PASS=0
FAIL=0
declare -a FAILURES=()

# --- Helpers ----------------------------------------------------------------

check_pass() {
    echo "  [OK]   $1"
    PASS=$((PASS + 1))
}

check_fail() {
    echo "  [FAIL] $1"
    FAIL=$((FAIL + 1))
    FAILURES+=("$1")
}

section() {
    echo ""
    echo "=== $1 ==="
}

# --- Check 1: hashes locales (CHECKSUMS.sha256) -----------------------------
# IMPORTANTE: comprobar AMBOS archivos y verificar exit code 0 de sha256sum.
# Antes verificaba solo "grep : OK" lo que aprueba con 1 OK + 1 FAILED.

section "1. Dataset canónico (CHECKSUMS.sha256)"
cd "$DATA_DIR"
CHECKSUM_OUT=$(sha256sum -c CHECKSUMS.sha256 2>&1)
CHECKSUM_EXIT=$?
if [ $CHECKSUM_EXIT -eq 0 ]; then
    # Exit 0 = todos OK. Validamos tambien cada archivo individualmente.
    CSV_OK=$(echo "$CHECKSUM_OUT" | grep -c "database_beta.csv: OK" || true)
    JSON_OK=$(echo "$CHECKSUM_OUT" | grep -c "database_beta.json: OK" || true)
    if [ "$CSV_OK" -eq 1 ] && [ "$JSON_OK" -eq 1 ]; then
        check_pass "database_beta.csv OK"
        check_pass "database_beta.json OK"
    else
        check_fail "exit 0 pero faltan lineas OK (CSV=$CSV_OK, JSON=$JSON_OK)"
    fi
else
    check_fail "sha256sum -c CHECKSUMS.sha256 fallo (exit=$CHECKSUM_EXIT)"
    echo "$CHECKSUM_OUT" | sed 's/^/         /'
fi
cd - > /dev/null

# --- Check 2: binding modelo+dataset+metricas -------------------------------

section "2. Binding modelo+dataset+metricas (MODEL_BINDING.sha256)"
cd "$DATA_DIR"
BIND_OUT=$(sha256sum -c MODEL_BINDING.sha256 2>&1)
BIND_EXIT=$?
if [ $BIND_EXIT -eq 0 ]; then
    # Validar cada uno de los 4 archivos explicitamente.
    for f in modelo_eficiencia_v1.joblib metricas_v1.joblib database_beta.json database_beta.csv; do
        if echo "$BIND_OUT" | grep -q "$f: OK"; then
            check_pass "$f OK"
        else
            check_fail "$f falta o no es OK en MODEL_BINDING.sha256"
        fi
    done
    BIND_MODEL_SHA=$(grep modelo_eficiencia_v1.joblib MODEL_BINDING.sha256 | awk '{print $1}')
else
    check_fail "sha256sum -c MODEL_BINDING.sha256 fallo (exit=$BIND_EXIT)"
    echo "$BIND_OUT" | sed 's/^/         /'
    BIND_MODEL_SHA=""
fi
cd - > /dev/null

# --- Check 3: servicio vivo (/health) ---------------------------------------

section "3. Servicio vivo (/health)"
HEALTH_RESP=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$URL/health" 2>&1)
HEALTH_CODE=$(echo "$HEALTH_RESP" | grep "HTTP_CODE:" | cut -d: -f2)
HEALTH_BODY=$(echo "$HEALTH_RESP" | grep -v "HTTP_CODE:")
if [ "$HEALTH_CODE" = "200" ] && echo "$HEALTH_BODY" | grep -q '"status":"healthy"'; then
    check_pass "/health -> 200 + status=healthy"
else
    check_fail "/health no respondio 200/healthy (code=$HEALTH_CODE, body=$HEALTH_BODY)"
fi

# --- Check 4: identidad del modelo servido (/model-info) ---------------------

section "4. Identidad del modelo servido (/model-info)"
MODEL_RESP=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$URL/model-info" 2>&1)
MODEL_CODE=$(echo "$MODEL_RESP" | grep "HTTP_CODE:" | cut -d: -f2)
MODEL_BODY=$(echo "$MODEL_RESP" | grep -v "HTTP_CODE:")
if [ "$MODEL_CODE" = "200" ]; then
    SERVED_SHA=$(echo "$MODEL_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('sha256', ''))" 2>/dev/null)
    SERVED_PATH=$(echo "$MODEL_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('model_path', ''))" 2>/dev/null)
    SERVED_LOADED=$(echo "$MODEL_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('loaded', ''))" 2>/dev/null)
    SERVED_SIZE=$(echo "$MODEL_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('size_bytes', ''))" 2>/dev/null)

    check_pass "/model-info -> 200 (path=$SERVED_PATH, loaded=$SERVED_LOADED, size=$SERVED_SIZE bytes)"

    if [ -n "$BIND_MODEL_SHA" ] && [ "$SERVED_SHA" = "$BIND_MODEL_SHA" ]; then
        check_pass "sha256 servido ($SERVED_SHA) == binding ($BIND_MODEL_SHA)"
    elif [ -n "$BIND_MODEL_SHA" ]; then
        check_fail "sha256 servido ($SERVED_SHA) != binding ($BIND_MODEL_SHA)"
    else
        check_fail "no se pudo comparar SHA (binding no disponible)"
    fi
else
    check_fail "/model-info no respondio 200 (code=$MODEL_CODE)"
fi

# --- Check 5: 3 perfiles golden ---------------------------------------------

section "5. 3 perfiles golden (consumir /analisis-energetico)"

# Perfil 1: esperado Eficiente
P1='{"consumo_kwh":180,"tipo_inmueble":"Casa","horas_alto_consumo":4,"cantidad_equipos":10,"uso_horario_pico":false,"zona_fria":false,"fuente_calefaccion":"Solar","fuente_agua_caliente":"Solar","metros_cuadrados":80,"antiguedad_vivienda":5,"calidad_aislamiento":"Muy Alta"}'
P1_RESP=$(curl -s -X POST "$URL/analisis-energetico" -H "Content-Type: application/json" -d "$P1" 2>&1)
P1_CAT=$(echo "$P1_RESP" | python3 -c "import sys, json; print(json.load(sys.stdin).get('categoria', ''))" 2>/dev/null)
P1_PROB=$(echo "$P1_RESP" | python3 -c "import sys, json; print(json.load(sys.stdin).get('probabilidad', ''))" 2>/dev/null)
if [ "$P1_CAT" = "Eficiente" ]; then
    check_pass "Perfil 1 (esperado Eficiente) -> categoria=$P1_CAT, prob=$P1_PROB"
else
    check_fail "Perfil 1 esperaba Eficiente, obtuvo '$P1_CAT' (resp=$P1_RESP)"
fi

# Perfil 2: esperado Moderado
P2='{"consumo_kwh":420,"tipo_inmueble":"Departamento","horas_alto_consumo":8,"cantidad_equipos":15,"uso_horario_pico":false,"zona_fria":false,"fuente_calefaccion":"Electricidad","fuente_agua_caliente":"Electricidad","metros_cuadrados":100,"antiguedad_vivienda":40,"calidad_aislamiento":"Media"}'
P2_RESP=$(curl -s -X POST "$URL/analisis-energetico" -H "Content-Type: application/json" -d "$P2" 2>&1)
P2_CAT=$(echo "$P2_RESP" | python3 -c "import sys, json; print(json.load(sys.stdin).get('categoria', ''))" 2>/dev/null)
P2_PROB=$(echo "$P2_RESP" | python3 -c "import sys, json; print(json.load(sys.stdin).get('probabilidad', ''))" 2>/dev/null)
if [ "$P2_CAT" = "Moderado" ]; then
    check_pass "Perfil 2 (esperado Moderado) -> categoria=$P2_CAT, prob=$P2_PROB"
else
    check_fail "Perfil 2 esperaba Moderado, obtuvo '$P2_CAT' (resp=$P2_RESP)"
fi

# Perfil 3: esperado Ineficiente
P3='{"consumo_kwh":780,"tipo_inmueble":"Casa","horas_alto_consumo":18,"cantidad_equipos":35,"uso_horario_pico":true,"zona_fria":true,"fuente_calefaccion":"Electricidad","fuente_agua_caliente":"Electricidad","metros_cuadrados":200,"antiguedad_vivienda":80,"calidad_aislamiento":"Muy Baja"}'
P3_RESP=$(curl -s -X POST "$URL/analisis-energetico" -H "Content-Type: application/json" -d "$P3" 2>&1)
P3_CAT=$(echo "$P3_RESP" | python3 -c "import sys, json; print(json.load(sys.stdin).get('categoria', ''))" 2>/dev/null)
P3_PROB=$(echo "$P3_RESP" | python3 -c "import sys, json; print(json.load(sys.stdin).get('probabilidad', ''))" 2>/dev/null)
if [ "$P3_CAT" = "Ineficiente" ]; then
    check_pass "Perfil 3 (esperado Ineficiente) -> categoria=$P3_CAT, prob=$P3_PROB"
else
    check_fail "Perfil 3 esperaba Ineficiente, obtuvo '$P3_CAT' (resp=$P3_RESP)"
fi

# --- Resumen ----------------------------------------------------------------

echo ""
echo "=== RESUMEN ==="
echo "Checks OK:   $PASS"
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
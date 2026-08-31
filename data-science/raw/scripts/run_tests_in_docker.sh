#!/usr/bin/env bash
# Build + run de la suite de tests del ml-service en Docker.
#
# Contexto de build: data-science/ (padre de raw/), igual que el Dockerfile
# de produccion usado por docker-compose.yml.
#
# Uso:
#   ./scripts/run_tests_in_docker.sh                 # solo tests
#   ./scripts/run_tests_in_docker.sh --sync          # sincroniza colab primero
#   ./scripts/run_tests_in_docker.sh --rebuild       # rebuild sin cache
#   ./scripts/run_tests_in_docker.sh --sync --rebuild # combinables en cualquier orden
#
# Requisitos: Docker accesible desde este shell.
#   - Linux/macOS: docker nativo.
#   - WSL: Docker Desktop > Settings > Resources > WSL Integration > Enable.
set -euo pipefail

# scripts/ -> raw/ -> data-science/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_CONTEXT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCKERFILE="$SCRIPT_DIR/../Dockerfile.test"

# Resolver binario docker: preferir 'docker' (Linux nativo / WSL con
# integracion activa), fallback a docker.exe (Docker Desktop Windows).
if command -v docker >/dev/null 2>&1; then
    DOCKER="docker"
elif [ -x "/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe" ]; then
    DOCKER="/mnt/c/Program Files/Docker/Docker/resources/bin/docker.exe"
else
    echo "[ERROR] Docker no encontrado." >&2
    echo "  - Linux/macOS: instala docker engine y asegurate que 'docker' este en PATH." >&2
    echo "  - WSL: Docker Desktop > Settings > Resources > WSL Integration > Enable." >&2
    echo "  - Windows: inicia Docker Desktop y verifica que el daemon este corriendo." >&2
    exit 1
fi

IMAGE_TAG="energia-tests:latest"
BUILD_FLAGS=()

# Detectar flags en cualquier posicion usando match de substring sobre "$*".
# Asi da igual el orden: ./script.sh --sync --rebuild ==
#                       ./script.sh --rebuild --sync.
if [[ " $* " == *" --rebuild "* ]]; then
    BUILD_FLAGS+=(--no-cache)
fi

# Verificar que el daemon responde antes de gastar tiempo en el build.
if ! "$DOCKER" info >/dev/null 2>&1; then
    echo "[ERROR] Docker daemon no responde." >&2
    echo "  En WSL: confirma que Docker Desktop este corriendo y que la distro WSL" >&2
    echo "  tenga la integracion habilitada (Settings > Resources > WSL Integration)." >&2
    exit 1
fi

echo "[INFO] Building $IMAGE_TAG (context=$BUILD_CONTEXT, docker=$DOCKER)"
"$DOCKER" build -f "$DOCKERFILE" -t "$IMAGE_TAG" "${BUILD_FLAGS[@]}" "$BUILD_CONTEXT"

# Montar raw/ como volumen para que la sincronizacion del notebook desde
# dentro del contenedor quede reflejada en el host (para inspection post-run).
RAW_DIR="$SCRIPT_DIR/.."
CMD_ARGS=(pytest -v)
if [[ " $* " == *" --sync "* ]]; then
    CMD_ARGS=(bash -c "pytest -v")
fi

echo "[INFO] Running tests..."
"$DOCKER" run --rm -v "$RAW_DIR:/app" "$IMAGE_TAG" "${CMD_ARGS[@]}"

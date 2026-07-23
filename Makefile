.PHONY: help install run pipeline demo serve test clean freeze init-env docker-build docker-run

help:
	@echo "Targets:"
	@echo "  install       pip install -r requirements.txt"
	@echo "  init-env      cp .env.example .env (si no existe)"
	@echo "  run           alias de 'pipeline' (ejecuta main.py)"
	@echo "  pipeline      genera dataset, entrena y guarda artefactos en data/"
	@echo "  demo          smoke test de inferencia (python src/inference.py)"
	@echo "  serve         levanta FastAPI en :8000 (uvicorn app:app)"
	@echo "  test          ejecuta validacion.py sobre los artefactos"
	@echo "  freeze        regenera requirements.txt con pip freeze"
	@echo "  docker-build  build de la imagen para OCI (python:3.10-slim)"
	@echo "  docker-run    ejecuta el contenedor exponiendo :8000"
	@echo "  clean         borra __pycache__, .pyc y artefactos en data/ (preserva .gitkeep)"

install:
	python3 -m pip install -r requirements.txt

init-env:
	@test -f .env || cp .env.example .env

run: pipeline

pipeline:
	python3 main.py

demo:
	python3 src/inference.py

serve:
	python3 -m uvicorn app:app --host 0.0.0.0 --port 8000

test:
	python3 validacion.py

freeze:
	python3 -m pip freeze > requirements.txt

docker-build:
	docker build -t energiai:1.0 .

docker-run:
	docker run --rm -p 8000:8000 energiai:1.0

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find data -mindepth 1 ! -name '.gitkeep' -delete

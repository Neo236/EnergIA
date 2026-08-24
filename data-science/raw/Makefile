.PHONY: help install run pipeline demo serve test verify-notebook-contract clean freeze init-env docker-build docker-run

help:
	@echo "Targets:"
	@echo "  install                    pip install -r requirements.txt"
	@echo "  init-env                   cp .env.example .env (si no existe)"
	@echo "  run                        alias de 'pipeline' (ejecuta interfaces.cli.train)"
	@echo "  pipeline                   genera dataset, entrena y guarda artefactos en data/"
	@echo "  demo                       smoke test de inferencia (python application/inference.py)"
	@echo "  serve                      levanta FastAPI en :8000 (uvicorn interfaces.api.app:app)"
	@echo "  test                       ejecuta interfaces.cli.validate sobre los artefactos"
	@echo "  verify-notebook-contract   valida que database_beta.json tiene el schema que la notebook Colab consume"
	@echo "  freeze                     regenera requirements.txt con pip freeze"
	@echo "  docker-build               build de la imagen para OCI (python:3.10-slim)"
	@echo "  docker-run                 ejecuta el contenedor exponiendo :8000"
	@echo "  clean                      borra __pycache__, .pyc y artefactos en data/ (preserva .gitkeep)"

install:
	python3 -m pip install -r requirements.txt

init-env:
	@test -f .env || cp .env.example .env

run: pipeline

pipeline:
	python3 -m interfaces.cli.train

demo:
	python3 -m application.inference

serve:
	python3 -m uvicorn interfaces.api.app:app --host 0.0.0.0 --port 8000

test:
	python3 -m interfaces.cli.validate

verify-notebook-contract:
	python3 -m interfaces.cli.verify_notebook_contract

freeze:
	python3 -m pip freeze > requirements.txt

docker-build:
	docker build -t energiai:1.0 -f ../Dockerfile ..

docker-run:
	docker run --rm -p 8000:8000 energiai:1.0

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@test ! -d data || find data -mindepth 1 ! -name '.gitkeep' -delete

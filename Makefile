.PHONY: install run test clean

install:
	python3 -m pip install -r requirements.txt

run:
	python3 main.py

test:
	python3 validacion.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find data -mindepth 1 ! -name '.gitkeep' -delete

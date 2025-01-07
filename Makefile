PORT=80

run:
	poetry run python render.py

min:
	poetry run htmlmin _build/index.html _build/index.html

poetry:
	pipx install poetry

poetry-install:
	poetry install --no-root

prod: poetry poetry-install run min
ci: poetry-install run

docker-build:
	docker build -t opengaming/osgameclones .

docker-run:
	-docker rm -f osgameclones-site
	docker run -d -p${PORT}:80 --name osgameclones-site opengaming/osgameclones

.PHONY:
	run prod docker-build docker-run

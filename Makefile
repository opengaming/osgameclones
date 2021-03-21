PORT=80

run:
	pipenv run ./render.py

prod:
	./render.py && htmlmin _build/index.html _build/index.html

docker-build:
	docker build -t opengaming/osgameclones .

docker-run:
	-docker rm -f osgameclones-site
	docker run -d -p${PORT}:80 --name osgameclones-site opengaming/osgameclones

.PHONY:
	run prod docker-build docker-run

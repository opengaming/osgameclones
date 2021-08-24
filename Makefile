PORT=80

run:
	pipenv run ./render.py

prod:
	pipenv run render.py && htmlmin _build/index.html _build/index.html
	pykwalify_webform schema/games.yaml _build/add_game.html _build/_add_form "" --name="Add game" --static_url=/_add_form
	pykwalify_webform schema/originals.yaml _build/add_original.html _build/_add_form "" --name="Add original game" --static_url=/_add_form

docker-build:
	docker build -t opengaming/osgameclones .

docker-run:
	-docker rm -f osgameclones-site
	docker run -d -p${PORT}:80 --name osgameclones-site opengaming/osgameclones

.PHONY:
	run prod docker-build docker-run

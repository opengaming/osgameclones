run:
	pipenv run ./render.py

prod:
	./render.py && htmlmin _build/index.html _build/index.html

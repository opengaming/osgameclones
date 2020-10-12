run:
	cyrax

prod:
	cyrax && htmlmin _build/index.html _build/index.html

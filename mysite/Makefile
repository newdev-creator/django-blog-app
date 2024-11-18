migrate:
	python3 manage.py migrate

makemigrations:
	python3 manage.py makemigrations

runserver:
	python3 manage.py runserver

start: migrate runserver

shell:
	python3 manage.py shell

dumpdata:
	python3 manage.py dumpdata --indent=2 --output=mysite_data.json

docker:
	docker start edb52e3b5305
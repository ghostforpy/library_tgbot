.SILENT:

local: compiletranslates
	docker-compose up --remove-orphans $(SERVICE)

local_web: compiletranslates
	docker-compose up --remove-orphans django $(SERVICE)

local_django: compiletranslates
	docker-compose up  --remove-orphans django celeryworker celeryworker_msg celerybeat flower $(SERVICE)

local_django_build:
	docker-compose up --build --remove-orphans django celeryworker celeryworker_msg celerybeat flower $(SERVICE)

local_bot:
	docker-compose up --remove-orphans bot $(SERVICE)

local_build:
	docker-compose build

db:
	docker-compose up --remove-orphans -d postgres

down:
	docker-compose down

make_migrations_local:
	docker-compose run --rm django python manage.py makemigrations && sudo chown ghost:ghost -R ./

empty_migration:
	docker-compose run --rm django python manage.py makemigrations --empty $(APP) && sudo chown ghost:ghost -R ./

migrate_production:
	sudo docker-compose -f production.yml run --rm django python manage.py migrate

production:
	sudo docker-compose -f production.yml up --build -d --remove-orphans --scale celeryworker=3

down_prod:
	sudo docker-compose -f production.yml down

backup_db:
	./backup_db_production.sh

manage_local:
	docker-compose run --rm django ./manage.py $(COMMAND)

local_shell:
	docker-compose run --rm django ./manage.py shell

create_superuser_local:
	docker-compose run --rm django ./manage.py createsuperuser

startapp_local:
	docker-compose run --rm django ./manage.py startapp $(APP) && sudo chown ghost:ghost -R ./

manage_production:
	sudo docker-compose -f production.yml run --rm django ./manage.py $(COMMAND)

production_shell:
	sudo docker-compose -f production.yml run --rm django ./manage.py shell

production_build:
	sudo docker-compose -f production.yml build

create_superuser_production:
	sudo docker-compose -f production.yml run --rm django ./manage.py createsuperuser

production_logs:
	sudo docker-compose -f production.yml logs -f

make_translates:
	django-admin makemessages --locale=uz --ignore=smartup/* -i venv

compiletranslates:
	django-admin compilemessages

clear_docker_images:
	./clear_docker_images.sh

generate_randoms:
	python3 gen_randoms.py
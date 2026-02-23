#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Aguardando o PostgreSQL..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL iniciado"
fi

# Rodar migrações
echo "Aplicando migrações..."
python manage.py migrate

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --no-input --clear

# Iniciar Gunicorn
echo "Iniciando Gunicorn..."
exec gunicorn modos.wsgi:application --bind 0.0.0.0:8000
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

# ==================================================
# ADICIONADO: Compilar o CSS do Tailwind
# ==================================================
echo "Instalando dependências do Tailwind (Node.js)..."
python manage.py tailwind install --no-input

echo "Compilando o Tailwind CSS para produção..."
python manage.py tailwind build
# ==================================================

# Coletar arquivos estáticos (Agora vai pegar o CSS recém-criado)
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --no-input --clear

# Iniciar Gunicorn
echo "Iniciando Gunicorn..."
exec gunicorn modos.wsgi:application --bind 0.0.0.0:8000
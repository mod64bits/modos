# Usar imagem oficial do Python leve
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Definir variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instalar dependências do sistema e Node.js (para Tailwind)
RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn psycopg2-binary

# Copiar o projeto
COPY . .

# Instalar dependências do Tailwind e compilar o CSS
# Nota: Certifique-se de que o nome do seu app tailwind no settings é 'theme' ou ajuste abaixo
RUN python manage.py tailwind install
RUN python manage.py tailwind build

# Copiar e dar permissão ao script de entrada
COPY ./entrypoint.prod.sh .
RUN chmod +x /app/entrypoint.prod.sh

# Executar script de entrada
ENTRYPOINT ["/app/entrypoint.prod.sh"]
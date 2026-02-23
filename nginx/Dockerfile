FROM nginx:1.25-alpine

# Remove a configuração padrão do Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Copia o nosso arquivo de configuração para a pasta correta
COPY nginx.conf /etc/nginx/conf.d
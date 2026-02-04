#!/bin/bash

# Скрипт для первоначального получения SSL сертификата
# Использование: ./init-ssl.sh your-email@example.com

if [ -z "$1" ]; then
    echo "Использование: ./init-ssl.sh your-email@example.com"
    exit 1
fi

EMAIL=$1
DOMAIN="tahfiz.site"

echo "==> Копируем временный nginx конфиг..."
cp nginx/nginx-init.conf nginx/nginx.conf.bak
cp nginx/nginx-init.conf nginx/nginx.conf

echo "==> Запускаем nginx..."
docker-compose up -d nginx

echo "==> Получаем SSL сертификат..."
docker-compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

echo "==> Восстанавливаем основной nginx конфиг..."
cp nginx/nginx.conf.bak nginx/nginx.conf
rm nginx/nginx.conf.bak

echo "==> Перезапускаем nginx с SSL..."
docker-compose restart nginx

echo "==> Готово! SSL сертификат установлен."

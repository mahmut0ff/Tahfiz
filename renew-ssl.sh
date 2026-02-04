#!/bin/bash

# Скрипт для обновления SSL сертификата
# Добавь в cron: 0 3 * * * /path/to/project/renew-ssl.sh >> /var/log/certbot-renew.log 2>&1

docker-compose run --rm certbot renew
docker-compose exec nginx nginx -s reload

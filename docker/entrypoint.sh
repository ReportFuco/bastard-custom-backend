#!/bin/sh
set -e

if [ "$DB_ENGINE" = "postgres" ]; then
  echo "Esperando PostgreSQL en ${POSTGRES_HOST}:${POSTGRES_PORT:-5432}..."
  while ! nc -z "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}"; do
    sleep 1
  done
  echo "PostgreSQL disponible."
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"

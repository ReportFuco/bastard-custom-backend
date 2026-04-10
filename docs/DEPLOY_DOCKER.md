# DEPLOY_DOCKER.md

Guía breve para correr `backend-tienda-online` con Docker + PostgreSQL.

## 1. Preparar variables

```bash
cp .env.example .env
```

Edita al menos:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `POSTGRES_PASSWORD`

## 2. Levantar servicios

```bash
docker compose up -d --build
```

Esto levanta:
- `db` → PostgreSQL 16
- `web` → Django + Gunicorn

## 3. Ver logs

```bash
docker compose logs -f
```

## 4. Reiniciar

```bash
docker compose restart
```

## 5. Bajar stack

```bash
docker compose down
```

## 6. Borrar también volumen de base de datos

```bash
docker compose down -v
```

⚠️ Esto elimina la data persistida del contenedor Postgres.

## Notas

- `entrypoint.sh` espera a PostgreSQL, corre migraciones y `collectstatic` automáticamente.
- La app queda expuesta en el puerto `8000`.
- PostgreSQL queda expuesto en `5432`.
- Para producción conviene poner Nginx o un proxy reverso delante.

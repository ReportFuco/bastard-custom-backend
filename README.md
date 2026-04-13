# backend-tienda-online

Backend base para una tienda online genérica construido con Django + Django REST Framework.

## Estado actual

Proyecto en etapa de construcción como base reusable para múltiples tiendas.

Módulos presentes:
- `users`
- `products`
- `cart`
- `orders`
- `inventory`
- `promotions`

Módulos más avanzados hoy:
- `users`
- `products`
- `cart`

## Requisitos

- Python 3.12+
- pip
- virtualenv recomendado
- Docker / Docker Compose recomendado para entorno con PostgreSQL

## Instalación local rápida

### Opción A: local simple con SQLite

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

Si quieres usar SQLite en local, cambia en `.env`:

```env
DB_ENGINE=sqlite
```

### Opción B: Docker + PostgreSQL

```bash
cp .env.example .env
docker compose up -d --build
```

Ver guía breve en:
- `docs/DEPLOY_DOCKER.md`

## Variables de entorno

Variables principales:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_LANGUAGE_CODE`
- `DJANGO_TIME_ZONE`
- `DB_ENGINE`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `SQLITE_NAME`

Ver ejemplo en `.env.example`.

## API actual

Base path:
- `/api/`

Endpoints relevantes en usuarios/auth:
- `POST /api/users/auth/register/`
- `POST /api/users/auth/login/`
- `POST /api/users/auth/refresh/`
- `GET/PATCH /api/users/me/`
- `GET /api/users/regions/`
- `GET /api/users/comunas/`
- CRUD `/api/users/direcciones/`

Endpoints relevantes de catálogo/carrito:
- `GET /api/products/`
- `GET /api/products/{slug}/`
- `GET /api/products/categorias/`
- `GET /api/cart/`
- `GET /api/cart/history/`
- `POST /api/cart/items/`
- `PATCH /api/cart/items/{item_id}/`
- `DELETE /api/cart/items/{item_id}/`
- `DELETE /api/cart/clear/`

Endpoints relevantes de órdenes/checkout:
- `GET /api/orders/`
- `GET /api/orders/{id}/`
- `POST /api/orders/checkout/`

Endpoints de inventario (solo admin):
- `GET /api/inventory/items/`
- `GET /api/inventory/movimientos/`

Endpoints de promociones (público):
- `GET /api/promotions/bands/`

Más detalle en:
- `docs/API.md`

## Roadmap corto

### Fase 1
- ordenar settings
- mover secretos a variables de entorno
- corregir consistencia de apps
- agregar documentación base

### Fase 2
- autenticación y usuarios
- registro/login/perfil
- permisos base
- direcciones, regiones y comunas

### Fase 3
- carrito y catálogo
- validaciones
- mejora de endpoints
- filtros por categoría y precio
- base de operación para checkout

### Fase 4
- órdenes e inventario real
- flujo checkout
- manejo de stock

### Infraestructura
- PostgreSQL por contenedor propio
- Dockerización del backend
- despliegue transportable para múltiples tiendas

## Observaciones

- El proyecto ya soporta SQLite o PostgreSQL según variables de entorno.
- Para producción, usar PostgreSQL, `DJANGO_DEBUG=False` y una `DJANGO_SECRET_KEY` segura.
- Para producción conviene agregar reverse proxy (Nginx/Caddy) por delante.

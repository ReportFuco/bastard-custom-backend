# backend-tienda-online

Backend base para una tienda online genérica construido con Django + Django REST Framework.

## Estado actual

Proyecto en etapa de ordenamiento inicial.

Módulos presentes:
- `users`
- `products`
- `cart`
- `orders`
- `inventory`

Hoy el módulo más avanzado es `products`. Los demás módulos se están preparando para una implementación más completa.

## Requisitos

- Python 3.12+
- pip
- virtualenv recomendado

## Instalación local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## Variables de entorno

Este proyecto lee configuración desde variables de entorno.

Variables principales:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_LANGUAGE_CODE`
- `DJANGO_TIME_ZONE`
- `SQLITE_NAME`

Ver ejemplo en `.env.example`.

## API actual

Base path:
- `/api/`

Rutas hoy conectadas:
- `/api/users/`
- `/api/products/`
- `/api/cart/`
- `/api/inventory/`

Endpoints relevantes en usuarios/auth:
- `POST /api/users/auth/register/`
- `POST /api/users/auth/login/`
- `POST /api/users/auth/refresh/`
- `GET/PATCH /api/users/me/`
- `GET /api/users/regions/`
- `GET /api/users/comunas/`
- CRUD `/api/users/direcciones/`

Nota: la implementación se está completando por fases.

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

## Observaciones

- Actualmente la base de datos por defecto es SQLite para desarrollo.
- Para producción se recomienda migrar a PostgreSQL.
- Antes de desplegar, asegúrate de desactivar `DJANGO_DEBUG` y usar una `DJANGO_SECRET_KEY` segura.
a base de datos por defecto es SQLite para desarrollo.
- Para producción se recomienda migrar a PostgreSQL.
- Antes de desplegar, asegúrate de desactivar `DJANGO_DEBUG` y usar una `DJANGO_SECRET_KEY` segura.

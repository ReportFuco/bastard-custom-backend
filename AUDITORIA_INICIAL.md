# Auditoría inicial — backend-tienda-online

Fecha: 2026-04-10

## Resumen ejecutivo

El proyecto tiene una base útil para un backend e-commerce en Django + DRF, pero hoy está en estado de esqueleto parcial. La parte más avanzada es `products`; el resto de módulos clave (`users`, `cart`, `orders`, `inventory`) está incompleto o sin exponer endpoints.

## Hallazgos principales

### 1) Configuración y seguridad
- `SECRET_KEY` hardcodeada en `config/settings.py`.
- `DEBUG = True` fijo.
- `ALLOWED_HOSTS` limitado y pensado para desarrollo/ngrok.
- Base de datos por defecto: SQLite.
- `LANGUAGE_CODE='en-us'`, `TIME_ZONE='UTC'` sin adaptación al contexto del proyecto.

### 2) Autenticación
- `REST_FRAMEWORK` declara `TokenAuthentication`.
- No está instalada la app `rest_framework.authtoken`.
- No existen endpoints de login, registro, logout, perfil ni refresh.
- No hay permisos por rol ni políticas explícitas.

### 3) Apps y consistencia interna
- `inventory` aparece en rutas (`api/urls.py`) pero no en `INSTALLED_APPS`.
- `orders` existe como app pero su ruta está comentada.
- `inventory/models.py`, `orders/models.py`, `views.py`, `tests.py` están vacíos.
- `users/urls.py`, `cart/urls.py`, `inventory/urls.py` están vacíos.

### 4) Dominio funcional
#### products
- Es el módulo más sólido.
- Tiene modelos, admin, serializers y endpoints read-only.
- Falta exponer slug/categoría más claramente y revisar naming (`description` mezclado con español).

#### users
- Tiene `User` custom y modelos de región/comuna/dirección.
- No tiene serializers, endpoints ni flujo de autenticación.
- `REQUIRED_FIELDS = ["email"]` está bien, pero falta revisar si `USERNAME_FIELD` debe seguir siendo `username` o pasar a `email`.

#### cart
- Tiene modelos de carrito e ítems.
- No tiene endpoints ni lógica para agregar/quitar/actualizar items.
- `updated_at` usa `auto_now_add=True`; probablemente debería ser `auto_now=True`.

#### orders
- No existe implementación real todavía.

#### inventory
- No existe implementación real todavía.

### 5) Calidad y mantenibilidad
- No hay `README.md`.
- No hay `.env.example`.
- No hay separación dev/prod de settings.
- No hay tests reales.
- No hay documentación de API.

## Riesgos actuales
- Riesgo de seguridad si se despliega tal como está.
- Riesgo de deuda técnica si se empiezan a agregar features sin cerrar auth, permisos y dominio de órdenes.
- Riesgo de inconsistencias funcionales entre stock, carrito y órdenes al no existir un modelo transaccional definido.

## Roadmap recomendado

### Fase 1 — Estabilización técnica
1. Preparar settings por entorno.
2. Mover secretos a variables de entorno.
3. Corregir `INSTALLED_APPS`, `ALLOWED_HOSTS`, `DEBUG`.
4. Agregar `README.md` y `.env.example`.
5. Definir convenciones de nombres (es/es, singular/plural, slugs, etc.).

### Fase 2 — Auth y usuarios
1. Elegir estrategia de auth (recomendado: JWT con SimpleJWT).
2. Endpoints: registro, login, refresh, perfil, direcciones.
3. Permisos base por usuario autenticado/admin.

### Fase 3 — Catálogo y carrito
1. Endpoints completos de categorías/productos.
2. Carrito: ver, agregar ítem, actualizar cantidad, eliminar ítem, limpiar carrito.
3. Validaciones de disponibilidad.

### Fase 4 — Inventario y órdenes
1. Diseñar modelo de stock.
2. Diseñar `Order`, `OrderItem`, estados y snapshots de precio.
3. Flujo checkout desde carrito a orden.
4. Reserva/descuento de stock.

### Fase 5 — Calidad y producción
1. Tests mínimos por módulo.
2. Documentación de API.
3. PostgreSQL.
4. Hardening y despliegue.

## Recomendación inmediata

No conviene saltar directo a órdenes. Primero hay que cerrar:
1. configuración,
2. autenticación,
3. consistencia de apps,
4. contrato base de catálogo/carrito.

## Próximo paso sugerido
Implementar Fase 1 completa y dejar el proyecto listo para empezar Fase 2 sin arrastrar deuda innecesaria.

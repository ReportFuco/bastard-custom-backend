# API.md

Resumen actualizado de la API de `backend-tienda-online` para frontend e integraciones.

Base URL:
- `/api/`

Autenticación:
- JWT Bearer Token
- En endpoints protegidos usar:
  - `Authorization: Bearer <access_token>`

---

## Auth / Usuarios

### Registro
- `POST /api/users/auth/register/`

Body ejemplo:
```json
{
  "username": "francisco",
  "email": "francisco@mail.com",
  "first_name": "Francisco",
  "last_name": "Arancibia",
  "password": "12345678",
  "password_confirm": "12345678"
}
```

### Login
- `POST /api/users/auth/login/`

Body ejemplo:
```json
{
  "username": "francisco",
  "password": "12345678"
}
```

Respuesta esperada:
```json
{
  "refresh": "...",
  "access": "..."
}
```

### Refresh token
- `POST /api/users/auth/refresh/`

Body:
```json
{
  "refresh": "..."
}
```

### Perfil autenticado
- `GET /api/users/me/`
- `PATCH /api/users/me/`

---

## Regiones / Comunas / Direcciones

### Regiones
- `GET /api/users/regions/`

### Comunas
- `GET /api/users/comunas/`
- `GET /api/users/comunas/?region_id=1`

### Direcciones del usuario
- `GET /api/users/direcciones/`
- `POST /api/users/direcciones/`
- `PATCH /api/users/direcciones/{id}/`
- `DELETE /api/users/direcciones/{id}/`

Body ejemplo para crear dirección:
```json
{
  "label": "Casa",
  "direccion": "Av. Siempre Viva 123",
  "comuna": 10,
  "is_default": true
}
```

---

## Productos

### Listado de productos
- `GET /api/products/`

Filtros disponibles:
- `q` (nombre, descripción o categoría)
- `categoria` (slug de categoría)
- `precio_min`
- `precio_max`

Ejemplos:
- `GET /api/products/?q=polera`
- `GET /api/products/?categoria=ropa`
- `GET /api/products/?precio_min=10000&precio_max=30000`

### Detalle de producto
- `GET /api/products/{slug}/`
- Incluye `tabla_nutricional` (si existe para el producto).

### Catálogos auxiliares
- `GET /api/products/categorias/`
- `GET /api/products/subcategorias/`
- `GET /api/products/marcas/`

---

## Carrito

Todos los endpoints de carrito requieren usuario autenticado.

### Ver carrito actual
- `GET /api/cart/`
- Siempre devuelve el carrito activo del usuario (se crea si no existe).

### Historial de carritos
- `GET /api/cart/history/`
- Devuelve carritos del usuario (activo y cerrados).

### Agregar item al carrito
- `POST /api/cart/items/`

Body:
```json
{
  "producto_id": 1,
  "cantidad": 2
}
```

### Actualizar cantidad de un item
- `PATCH /api/cart/items/{item_id}/`

Body:
```json
{
  "cantidad": 4
}
```

### Eliminar item del carrito
- `DELETE /api/cart/items/{item_id}/`

### Vaciar carrito
- `DELETE /api/cart/clear/`

---

## Órdenes / Checkout

Todos los endpoints de órdenes requieren usuario autenticado.

### Listado de órdenes
- `GET /api/orders/`

### Detalle de orden
- `GET /api/orders/{id}/`
- Incluye dirección referenciada desde `users.Direccion`:
  - `direccion_envio_id`
  - `direccion_etiqueta`
  - `direccion`
  - `comuna`
  - `region`

### Checkout desde carrito
- `POST /api/orders/checkout/`

Body ejemplo:
```json
{
  "direccion_id": 1,
  "notes": "Entregar en conserjería"
}
```

`direccion_id` es opcional:
- Si no se envía, se usa la dirección predeterminada del usuario.
- Si el usuario no tiene direcciones, el checkout responde error y debe crear una en `/api/users/direcciones/`.

Header opcional (idempotencia):
- `Idempotency-Key: <clave-unica>` (máximo 64 caracteres)

Qué hace:
- Toma el carrito activo del usuario.
- Valida stock disponible.
- Descuenta inventario.
- Registra movimientos de inventario por cada producto descontado.
- Calcula costo de envío en backend.
- Genera una orden.
- Guarda snapshot de dirección.
- Guarda snapshot de productos y precios.
- Marca ese carrito como `checked_out` y crea un nuevo carrito `active`.

---

## Inventario (solo admin)

Estos endpoints requieren usuario admin.

### Items de inventario
- `GET /api/inventory/items/`

Campos relevantes de respuesta:
- `producto_id`
- `producto_nombre`
- `producto_slug`
- `cantidad_disponible`
- `cantidad_reservada`
- `cantidad_total`
- `en_stock`
- `actualizado_en`

### Movimientos de inventario
- `GET /api/inventory/movimientos/`

Filtros opcionales:
- `producto_id`
- `tipo`

Tipos soportados:
- `entrada`
- `salida`
- `ajuste`
- `reserva`
- `liberacion`

Campos relevantes de respuesta:
- `item_inventario_id`
- `producto_id`
- `producto_nombre`
- `tipo`
- `cantidad`
- `cantidad_anterior`
- `cantidad_posterior`
- `motivo`
- `referencia`
- `creado_por_id`
- `creado_por_username`
- `creado_en`

### Proveedores
- `GET /api/inventory/proveedores/`
- `POST /api/inventory/proveedores/`
- `GET /api/inventory/proveedores/{id}/`
- `PUT /api/inventory/proveedores/{id}/`
- `PATCH /api/inventory/proveedores/{id}/`
- `DELETE /api/inventory/proveedores/{id}/`

Filtro opcional en listado:
- `q` (nombre de proveedor)

Body ejemplo para crear proveedor:
```json
{
  "nombre_proveedor": "Distribuidora Norte SPA",
  "contacto_proveedor": "+56 9 9123 4567",
  "email_contacto": "contacto@distribuidoranorte.cl",
  "activo": true
}
```

Nota:
- `contacto_proveedor` se normaliza a formato `569XXXXXXXX` en backend.

### Producto-Proveedor
- `GET /api/inventory/producto-proveedores/`
- `POST /api/inventory/producto-proveedores/`
- `GET /api/inventory/producto-proveedores/{id}/`
- `PUT /api/inventory/producto-proveedores/{id}/`
- `PATCH /api/inventory/producto-proveedores/{id}/`
- `DELETE /api/inventory/producto-proveedores/{id}/`

Filtros opcionales en listado:
- `producto_id`
- `proveedor_id`

Body ejemplo para crear relación:
```json
{
  "producto": 1,
  "proveedor": 3,
  "codigo_proveedor": "SKU-PRV-001",
  "costo_compra": "12990.00",
  "tiempo_reposicion_dias": 7,
  "activo": true
}
```

Regla:
- No se permiten duplicados para la misma combinación `producto + proveedor`.

---

## Estado actual

Implementado:
- Auth JWT base.
- Perfil de usuario.
- Direcciones.
- Catálogo de productos (categorías, subcategorías y marcas).
- Carrito funcional.
- Checkout con control de stock.
- Inventario en español.
- Historial de movimientos de inventario.
- Proveedores y relación producto-proveedor.

Pendiente:
- Integración de pagos.
- Estados avanzados de fulfillment.
- Documentación OpenAPI/Swagger.

---

## Nota para frontend

Convención sugerida:
- Guardar `access` token en memoria o almacenamiento seguro.
- Usar `refresh` para renovar sesión.
- Tratar `slug` como identificador público de producto.
- Refrescar carrito después de cada operación de add/update/delete.

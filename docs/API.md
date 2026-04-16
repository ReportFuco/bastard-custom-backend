# API.md

Resumen actualizado de la API de `bastard-custom-backend` para frontend e integraciones.

Base URL:
- `/api/`

Autenticacion:
- JWT Bearer Token
- En endpoints protegidos usar:
  - `Authorization: Bearer <access_token>`

Formato general:
- Respuestas en JSON
- No hay paginacion global configurada en DRF
- La API usa nombres de campos reales del backend, varios en espanol

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
  "phone_number": "56991234567",
  "password": "12345678",
  "password_confirm": "12345678"
}
```

Notas:
- `password` y `password_confirm` deben coincidir
- `email` debe ser unico
- `phone_number` se normaliza en backend a formato chileno `569XXXXXXXX`

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

Campos de perfil:
- `id`
- `username`
- `email` (solo lectura)
- `first_name`
- `last_name`
- `phone_number`
- `is_customer` (solo lectura)

---

## Regiones / Comunas / Direcciones

### Regiones
- `GET /api/users/regions/`

Respuesta por item:
```json
{
  "id": 1,
  "nombre": "Metropolitana"
}
```

### Comunas
- `GET /api/users/comunas/`
- `GET /api/users/comunas/?region_id=1`

Notas:
- `region_id` debe ser numerico

Respuesta por item:
```json
{
  "id": 10,
  "nombre": "Las Condes",
  "region": {
    "id": 1,
    "nombre": "Metropolitana"
  }
}
```

### Direcciones del usuario
- `GET /api/users/direcciones/`
- `POST /api/users/direcciones/`
- `GET /api/users/direcciones/{id}/`
- `PATCH /api/users/direcciones/{id}/`
- `DELETE /api/users/direcciones/{id}/`

Body ejemplo para crear direccion:
```json
{
  "etiqueta": "Casa",
  "direccion": "Av. Siempre Viva",
  "numero": "123",
  "comuna": 10,
  "es_predeterminada": true
}
```

Respuesta por item:
```json
{
  "id": 1,
  "etiqueta": "Casa",
  "direccion": "Av. Siempre Viva",
  "numero": "123",
  "comuna": 10,
  "comuna_nombre": "Las Condes",
  "region_nombre": "Metropolitana",
  "es_predeterminada": true,
  "creado_en": "2026-04-16T12:00:00Z",
  "actualizado_en": "2026-04-16T12:00:00Z"
}
```

Notas:
- Los nombres correctos de campos son `etiqueta` y `es_predeterminada`
- `direccion` representa la calle o via principal
- `numero` guarda la numeracion o complemento corto
- Si una direccion se guarda con `es_predeterminada=true`, el backend desmarca la direccion predeterminada anterior del mismo usuario

---

## Productos

### Listado de productos
- `GET /api/products/`

Filtros disponibles:
- `q` (nombre, descripcion, categoria, subcategoria o marca)
- `categoria` (slug de categoria)
- `subcategoria` (slug de subcategoria)
- `marca` (slug de marca)
- `precio_min`
- `precio_max`

Ejemplos:
- `GET /api/products/?q=polera`
- `GET /api/products/?categoria=ropa`
- `GET /api/products/?subcategoria=poleras`
- `GET /api/products/?marca=nike`
- `GET /api/products/?precio_min=10000&precio_max=30000`

Validaciones:
- `precio_min` y `precio_max` deben ser numericos
- `precio_min` no puede ser mayor que `precio_max`

Respuesta por item:
```json
{
  "id": 1,
  "nombre": "Producto",
  "slug": "producto",
  "categoria_id": 2,
  "categoria_nombre": "Ropa",
  "categoria_slug": "ropa",
  "marca_id": 3,
  "marca_nombre": "Marca",
  "marca_slug": "marca",
  "subcategoria_id": 4,
  "subcategoria_nombre": "Poleras",
  "subcategoria_slug": "poleras",
  "precio": "19990.00",
  "precio_lista": "24990.00",
  "precio_oferta": "19990.00",
  "moneda": "CLP",
  "description": "Descripcion",
  "imagen_principal": {
    "imagen": "/media/productos/item.jpg",
    "nombre": "Vista principal"
  }
}
```

### Detalle de producto
- `GET /api/products/{slug}/`

Respuesta relevante:
- Todo lo del listado, mas:
  - `precio_info`
  - `tabla_nutricional`
  - `variantes_color`
  - `imagenes`
  - `created_at`
  - `updated_at`

Ejemplo parcial:
```json
{
  "id": 1,
  "nombre": "Producto",
  "slug": "producto",
  "precio": "19990.00",
  "precio_info": {
    "precio_lista": "24990.00",
    "precio_oferta": "19990.00",
    "precio_final": "19990.00",
    "moneda": "CLP",
    "activo": true,
    "vigencia_desde": null,
    "vigencia_hasta": null
  },
  "tabla_nutricional": null,
  "variantes_color": [
    {
      "color": "#FFFFFF",
      "nombre": "Blanco"
    }
  ],
  "imagenes": [
    {
      "imagen": "/media/productos/item.jpg",
      "nombre": "Vista principal"
    }
  ]
}
```

Nota:
- Al consultar detalle se incrementa el contador de vistas del producto

### Catalogos auxiliares
- `GET /api/products/categorias/`
- `GET /api/products/subcategorias/`
- `GET /api/products/marcas/`

Filtros soportados:
- Categorias:
  - `q`
- Subcategorias:
  - `q`
  - `categoria` (slug de categoria)
- Marcas:
  - `q`

---

## Promociones

### Franjas promocionales activas
- `GET /api/promotions/bands/`

Devuelve solo promociones activas y vigentes segun fecha.

Respuesta por item:
```json
{
  "id": 1,
  "titulo": "Envio gratis",
  "mensaje": "En compras sobre $50.000",
  "etiqueta_cta": "Ver productos",
  "url_cta": "/catalogo",
  "color_fondo": "#CAFD00",
  "color_texto": "#1A2200",
  "activa": true,
  "fecha_inicio": null,
  "fecha_fin": null,
  "prioridad": 10,
  "creado_en": "2026-04-16T12:00:00Z",
  "actualizado_en": "2026-04-16T12:00:00Z",
  "title": "Envio gratis",
  "message": "En compras sobre $50.000",
  "ctaLabel": "Ver productos",
  "ctaUrl": "/catalogo",
  "backgroundColor": "#CAFD00",
  "textColor": "#1A2200"
}
```

Nota:
- El endpoint expone tanto claves en espanol como aliases pensados para frontend (`title`, `message`, `ctaLabel`, etc.)
- Este enpoint va dirigido a la franja superior

---

## Carrito

Todos los endpoints de carrito requieren usuario autenticado.

### Ver carrito actual
- `GET /api/cart/`

Notas:
- Siempre devuelve el carrito `active` del usuario
- Si no existe, se crea automaticamente

### Historial de carritos
- `GET /api/cart/history/`

Notas:
- Devuelve todos los carritos del usuario ordenados por fecha de creacion descendente
- Puede incluir estados `active`, `checked_out` y `abandoned`

### Agregar item al carrito
- `POST /api/cart/items/`

Body:
```json
{
  "producto_id": 1,
  "cantidad": 2
}
```

Notas:
- Si el producto ya existe en el carrito activo, el backend suma la cantidad
- Devuelve `201` si crea un item nuevo
- Devuelve `200` si el item ya existia y solo actualiza cantidad

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

### Respuesta del carrito
```json
{
  "id": 1,
  "status": "active",
  "checked_out_at": null,
  "created_at": "2026-04-16T12:00:00Z",
  "updated_at": "2026-04-16T12:00:00Z",
  "total_items": 3,
  "total": "39980.00",
  "items": [
    {
      "id": 7,
      "producto": {
        "id": 1,
        "nombre": "Producto",
        "slug": "producto",
        "precio": "19990.00",
        "categoria_nombre": "Ropa"
      },
      "cantidad": 2,
      "subtotal": "39980.00"
    }
  ]
}
```

---

## Ordenes / Checkout

Todos los endpoints de ordenes requieren usuario autenticado.

### Listado de ordenes
- `GET /api/orders/`

Notas:
- Usuario comun: solo ve sus ordenes
- Admin: ve todas las ordenes

### Detalle de orden
- `GET /api/orders/{id}/`

Campos principales:
- `id`
- `status`
- `subtotal`
- `shipping_cost`
- `total`
- `notes`
- `direccion_envio_id`
- `direccion_etiqueta`
- `direccion`
- `direccion_numero`
- `comuna`
- `region`
- `items`
- `created_at`
- `updated_at`

Item de orden:
- `id`
- `product`
- `product_name`
- `product_slug`
- `unit_price`
- `quantity`
- `line_total`

### Checkout desde carrito
- `POST /api/orders/checkout/`

Body ejemplo:
```json
{
  "direccion_id": 1,
  "notes": "Entregar en conserjeria"
}
```

`direccion_id` es opcional:
- Si se envia, debe pertenecer al usuario autenticado
- Si no se envia, el backend intenta usar la direccion predeterminada
- Si no existe direccion predeterminada, usa la ultima direccion del usuario por `actualizado_en`
- Si el usuario no tiene direcciones, responde error y debe crear una en `/api/users/direcciones/`

Header opcional de idempotencia:
- `Idempotency-Key: <clave-unica>`
- Maximo 64 caracteres
- Si se repite la misma clave para el mismo usuario, el backend devuelve la orden ya creada

Que hace el checkout:
- Toma el carrito activo del usuario
- Valida que el carrito no este vacio
- Valida que no existan productos inactivos
- Valida stock disponible
- Calcula costo de envio en backend
- Genera la orden y sus items
- Descuenta inventario
- Registra movimientos de inventario por cada descuento
- Marca el carrito como `checked_out`
- Crea un nuevo carrito `active`

Regla actual de envio:
- Si `subtotal >= 50000.00`, `shipping_cost = 0.00`
- Si `subtotal < 50000.00`, `shipping_cost = 2990.00`

Importante:
- La orden guarda referencia a `users.Direccion` mediante `direccion_envio`
- El serializer expone campos planos de direccion (`direccion`, `direccion_numero`, `comuna`, `region`, etc.) leidos desde esa relacion
- No hay snapshot inmutable de direccion en el modelo actual

Errores esperables:
- Carrito vacio
- Productos inactivos en el carrito
- Stock insuficiente
- `Idempotency-Key` demasiado larga
- Usuario sin direcciones

---

## Inventario (solo admin)

Estos endpoints requieren usuario admin.

### Items de inventario
- `GET /api/inventory/items/`

Campos relevantes de respuesta:
- `id`
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
- `id`
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
  "contacto_proveedor": "56991234567",
  "email_contacto": "contacto@distribuidoranorte.cl",
  "sitio_web": "https://distribuidoranorte.cl",
  "direccion": "Av. Apoquindo 1234, Las Condes, Santiago",
  "latitud": -33.414539,
  "longitud": -70.581815,
  "activo": true
}
```

Notas:
- `contacto_proveedor` se normaliza a formato `569XXXXXXXX`
- `sitio_web`, `direccion`, `latitud` y `longitud` son opcionales
- `latitud` debe estar entre `-90` y `90`
- `longitud` debe estar entre `-180` y `180`

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

Body ejemplo para crear relacion:
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
- No se permiten duplicados para la misma combinacion `producto + proveedor`

---

## Estado actual

Implementado:
- Auth JWT base
- Perfil de usuario
- Direcciones
- Catalogo de productos
- Franjas promocionales publicas
- Carrito funcional
- Checkout con control de stock
- Inventario
- Historial de movimientos de inventario
- Proveedores y relacion producto-proveedor

Pendiente:
- Integracion de pagos
- Estados avanzados de fulfillment
- Documentacion OpenAPI/Swagger

---

## Nota para frontend

Convenciones sugeridas:
- Guardar `access` token en memoria o almacenamiento seguro
- Usar `refresh` para renovar sesion
- Tratar `slug` como identificador publico de producto
- Refrescar carrito despues de cada operacion de add/update/delete
- No asumir paginacion
- No traducir nombres de campos al consumir endpoints de escritura: usar exactamente los nombres del contrato (`etiqueta`, `es_predeterminada`, `direccion_id`, etc.)

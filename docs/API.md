# API.md

Resumen breve de la API actual de `backend-tienda-online` para dar contexto al frontend.

Base URL:
- `/api/`

Autenticación:
- JWT Bearer Token
- En endpoints protegidos usar header:
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

Respuesta ejemplo:
```json
{
  "id": 1,
  "username": "francisco",
  "email": "francisco@mail.com",
  "first_name": "Francisco",
  "last_name": "Arancibia",
  "is_customer": true
}
```

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
- `q` → búsqueda por nombre, descripción o categoría
- `categoria` → slug de categoría
- `precio_min`
- `precio_max`

Ejemplos:
- `GET /api/products/?q=polera`
- `GET /api/products/?categoria=ropa`
- `GET /api/products/?precio_min=10000&precio_max=30000`

Respuesta ejemplo:
```json
[
  {
    "id": 1,
    "nombre": "Polera Negra",
    "slug": "polera-negra",
    "categoria_id": 2,
    "categoria_nombre": "Ropa",
    "categoria_slug": "ropa",
    "precio": "19990.00",
    "description": "Polera algodón premium",
    "created_at": "2026-04-10T12:00:00Z",
    "updated_at": "2026-04-10T12:10:00Z"
  }
]
```

### Detalle de producto
- `GET /api/products/{slug}/`

### Categorías
- `GET /api/products/categorias/`

---

## Carrito

Todos los endpoints de carrito requieren usuario autenticado.

### Ver carrito actual
- `GET /api/cart/`

Respuesta ejemplo:
```json
{
  "id": 1,
  "created_at": "2026-04-10T12:00:00Z",
  "updated_at": "2026-04-10T12:10:00Z",
  "total_items": 3,
  "total": "59970.00",
  "items": [
    {
      "id": 7,
      "producto": {
        "id": 1,
        "nombre": "Polera Negra",
        "slug": "polera-negra",
        "precio": "19990.00",
        "categoria_nombre": "Ropa"
      },
      "cantidad": 3,
      "subtotal": "59970.00"
    }
  ]
}
```

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

## Estado actual / pendientes

Implementado:
- auth JWT base
- perfil usuario
- direcciones
- catálogo de productos
- categorías
- carrito funcional

Pendiente:
- órdenes
- inventario real
- checkout
- pagos
- documentación más formal tipo OpenAPI/Swagger

---

## Nota para frontend

Convención sugerida para el front:
- guardar `access` token en memoria o almacenamiento seguro
- usar `refresh` para renovar sesión
- tratar `slug` como identificador público de producto
- refrescar carrito después de cada operación de add/update/delete

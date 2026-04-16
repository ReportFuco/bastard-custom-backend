# CLAUDE.md

Guia para implementar el frontend contra este backend sin romper el contrato de la API.

## Objetivo

El frontend debe consumir el backend existente tal como esta hoy. La prioridad no es inventar contratos nuevos sino respetar rutas, nombres de campos y reglas de negocio reales.

Documento fuente del contrato:
- `docs/API.md`

Base URL:
- `/api/`

Autenticacion:
- JWT Bearer
- Header requerido en endpoints protegidos:
  - `Authorization: Bearer <access_token>`

---

## Reglas clave para frontend

1. Usar los nombres de campos exactos del backend.

No renombrar al enviar payloads. Ejemplos correctos:
- Direcciones: `etiqueta`, `direccion`, `numero`, `comuna`, `es_predeterminada`
- Checkout: `direccion_id`, `notes`
- Carrito: `producto_id`, `cantidad`

Ejemplos incorrectos:
- `label`
- `is_default`
- `shippingAddressId`
- `productId`

2. Separar claramente lectura y escritura.

Hay endpoints que devuelven aliases pensados para UI, pero el payload de escritura sigue usando nombres del backend. Ejemplo:
- Promociones devuelve `title` y tambien `titulo`
- Direcciones devuelven `comuna_nombre` y `region_nombre`, pero al crear se envia `comuna`

3. No asumir snapshot de direccion en ordenes.

La orden referencia una `Direccion` existente. Si en el futuro backend cambia una direccion, el frontend no debe asumir que la orden guarda una copia historica inmutable.

4. No asumir paginacion.

Actualmente DRF no tiene paginacion global configurada. Los listados devuelven arrays completos.

5. Prepararse para errores de validacion de DRF.

Los errores pueden venir como:
- `{ "detail": "..." }`
- `{ "campo": ["..."] }`
- `{ "campo": "..." }`
- `{ "items": [...] }` en errores de stock o productos invalidos

El frontend debe mostrar mensajes robustos sin depender de un solo formato.

---

## Modulos a implementar

## 1. Auth

Endpoints:
- `POST /api/users/auth/register/`
- `POST /api/users/auth/login/`
- `POST /api/users/auth/refresh/`
- `GET /api/users/me/`
- `PATCH /api/users/me/`

Recomendaciones:
- Guardar `access` y `refresh`
- Reintentar una vez con refresh ante `401`
- Si refresh falla, cerrar sesion y limpiar estado local

Modelo sugerido en frontend:
```ts
type AuthTokens = {
  access: string;
  refresh: string;
};

type Me = {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  is_customer: boolean;
};
```

---

## 2. Direcciones, regiones y comunas

Endpoints:
- `GET /api/users/regions/`
- `GET /api/users/comunas/`
- `GET /api/users/comunas/?region_id=<id>`
- `GET /api/users/direcciones/`
- `POST /api/users/direcciones/`
- `GET /api/users/direcciones/{id}/`
- `PATCH /api/users/direcciones/{id}/`
- `DELETE /api/users/direcciones/{id}/`

Contrato importante:
- `direccion` se envia como calle o via principal
- `numero` guarda la numeracion o complemento corto
- `comuna` se envia como ID
- `es_predeterminada` controla la direccion default
- Si se marca una direccion como predeterminada, backend desmarca la anterior

Modelo sugerido:
```ts
type Direccion = {
  id: number;
  etiqueta: string;
  direccion: string;
  numero: string;
  comuna: number;
  comuna_nombre: string;
  region_nombre: string;
  es_predeterminada: boolean;
  creado_en: string;
  actualizado_en: string;
};
```

UX sugerida:
- Selector cascada `region -> comuna`
- Al editar, usar los nombres exactos del contrato
- Mostrar chip o badge para `es_predeterminada`

---

## 3. Catalogo de productos

Endpoints:
- `GET /api/products/`
- `GET /api/products/{slug}/`
- `GET /api/products/categorias/`
- `GET /api/products/subcategorias/`
- `GET /api/products/marcas/`

Filtros que si existen:
- `q`
- `categoria`
- `subcategoria`
- `marca`
- `precio_min`
- `precio_max`

No inventar filtros que el backend no soporte.

Modelo sugerido para cards:
```ts
type ProductCard = {
  id: number;
  nombre: string;
  slug: string;
  categoria_id: number | null;
  categoria_nombre: string | null;
  categoria_slug: string | null;
  marca_id: number | null;
  marca_nombre: string | null;
  marca_slug: string | null;
  subcategoria_id: number | null;
  subcategoria_nombre: string | null;
  subcategoria_slug: string | null;
  precio: string;
  precio_lista: string | null;
  precio_oferta: string | null;
  moneda: string;
  description: string;
  imagen_principal: {
    imagen: string;
    nombre: string;
  } | null;
};
```

Reglas de UI:
- Usar `slug` para navegar al detalle
- Mostrar `precio_oferta` si existe y si difiere de `precio_lista`
- No asumir que siempre habra `imagen_principal`
- No asumir que siempre habra `tabla_nutricional`
- `variantes_color` es informativo en detalle

---

## 4. Promociones

Endpoint:
- `GET /api/promotions/bands/`

Uso sugerido:
- Cargar en layout principal o home
- Consumir preferentemente los aliases frontend:
  - `title`
  - `message`
  - `ctaLabel`
  - `ctaUrl`
  - `backgroundColor`
  - `textColor`

Modelo sugerido:
```ts
type PromotionBand = {
  id: number;
  title: string;
  message: string;
  ctaLabel: string;
  ctaUrl: string;
  backgroundColor: string;
  textColor: string;
};
```

Nota:
- El backend ya filtra solo promociones activas y vigentes

---

## 5. Carrito

Endpoints:
- `GET /api/cart/`
- `GET /api/cart/history/`
- `POST /api/cart/items/`
- `PATCH /api/cart/items/{item_id}/`
- `DELETE /api/cart/items/{item_id}/`
- `DELETE /api/cart/clear/`

Contrato importante:
- `GET /api/cart/` crea el carrito activo si no existe
- `POST /api/cart/items/` suma cantidad si el producto ya estaba agregado
- El backend devuelve el carrito completo despues de agregar, actualizar, eliminar o vaciar

Modelo sugerido:
```ts
type CartItem = {
  id: number;
  producto: {
    id: number;
    nombre: string;
    slug: string;
    precio: string;
    categoria_nombre: string;
  };
  cantidad: number;
  subtotal: string;
};

type Cart = {
  id: number;
  status: "active" | "checked_out" | "abandoned";
  checked_out_at: string | null;
  created_at: string;
  updated_at: string;
  total_items: number;
  total: string;
  items: CartItem[];
};
```

Flujo recomendado:
- Al iniciar sesion, pedir `GET /api/cart/`
- Despues de cada mutacion, reemplazar el estado local por la respuesta completa del backend
- No recalcular totales en frontend como fuente de verdad

---

## 6. Checkout y ordenes

Endpoints:
- `GET /api/orders/`
- `GET /api/orders/{id}/`
- `POST /api/orders/checkout/`

Payload de checkout:
```json
{
  "direccion_id": 1,
  "notes": "Entregar en conserjeria"
}
```

Contrato importante:
- `direccion_id` es opcional
- Si falta, backend intenta resolver direccion automaticamente
- `Idempotency-Key` es recomendable para evitar doble compra por doble click o retry

Recomendacion critica:
- Generar una `Idempotency-Key` unica por intento de checkout y enviarla en header

Ejemplo:
```ts
headers: {
  Authorization: `Bearer ${token}`,
  "Idempotency-Key": checkoutAttemptId,
}
```

Errores de checkout que hay que tratar bien:
- carrito vacio
- sin direcciones
- productos inactivos
- stock insuficiente
- error de validacion de direccion

Modelo sugerido:
```ts
type OrderItem = {
  id: number;
  product: number;
  product_name: string;
  product_slug: string;
  unit_price: string;
  quantity: number;
  line_total: string;
};

type Order = {
  id: number;
  status: "pending" | "confirmed" | "paid" | "shipped" | "delivered" | "canceled";
  subtotal: string;
  shipping_cost: string;
  total: string;
  notes: string;
  direccion_envio_id: number | null;
  direccion_etiqueta: string | null;
  direccion: string | null;
  direccion_numero: string | null;
  comuna: string | null;
  region: string | null;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
};
```

UX sugerida para checkout:
- Mostrar direccion seleccionada
- Mostrar `subtotal`, `shipping_cost` y `total` desde backend
- Bloquear doble submit mientras la compra esta en progreso
- Si hay error de stock, mostrar detalle por item si backend lo envia

---

## 7. Inventario y admin

Estos endpoints son para vistas administrativas.

Endpoints:
- `GET /api/inventory/items/`
- `GET /api/inventory/movimientos/`
- `GET/POST/PUT/PATCH/DELETE /api/inventory/proveedores/...`
- `GET/POST/PUT/PATCH/DELETE /api/inventory/producto-proveedores/...`

Regla:
- Solo mostrarlos en frontend si el usuario efectivamente tiene acceso admin

---

## Estrategia de cliente API

Implementar una capa unica de cliente HTTP.

Minimo recomendado:
- `get`
- `post`
- `patch`
- `put`
- `delete`
- inyeccion automatica de bearer token
- refresh token centralizado
- normalizacion basica de errores

No dispersar `fetch()` o `axios` por toda la app.

---

## Criterios para avanzar sin romper el backend

1. Cada formulario debe basarse en el payload real documentado en `docs/API.md`.
2. Cada pantalla debe tipar respuesta real del backend antes de renderizar.
3. No crear mapeos silenciosos de nombres entre UI y API en campos criticos.
4. En checkout y carrito, tomar siempre la respuesta del backend como fuente de verdad.
5. Ante dudas, revisar primero `docs/API.md` y luego serializers/views del backend.

---

## Prioridad de implementacion sugerida

1. Auth y sesion JWT
2. Catalogo de productos
3. Carrito
4. Direcciones
5. Checkout
6. Historial de ordenes
7. Promociones
8. Vistas admin si aplican

---

## Checklist rapido para cada integracion

- La ruta coincide exactamente con `docs/API.md`
- El metodo HTTP es correcto
- Los nombres de campos del request son exactos
- Se envia bearer token si corresponde
- Se manejan errores `detail` y errores por campo
- El tipado de respuesta coincide con el contrato real
- No se asumen campos que el backend no envia

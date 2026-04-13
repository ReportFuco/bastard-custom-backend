from django import forms

from .models import Order, OrderItem


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"
        labels = {
            "user": "Usuario",
            "idempotency_key": "Clave de idempotencia",
            "status": "Estado",
            "subtotal": "Subtotal",
            "shipping_cost": "Costo de envío",
            "total": "Total",
            "notes": "Notas",
            "direccion_envio": "Dirección de envío",
            "created_at": "Creado en",
            "updated_at": "Actualizado en",
        }


class OrderItemAdminForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = "__all__"
        labels = {
            "order": "Orden",
            "product": "Producto",
            "product_name": "Nombre de producto",
            "product_slug": "Slug del producto",
            "unit_price": "Precio unitario",
            "quantity": "Cantidad",
            "line_total": "Total línea",
        }

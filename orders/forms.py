from django import forms

from .models import Order, OrderItem


class OrderAdminForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        if not self.instance.pk:
            return cleaned_data

        previous_status = self.instance.status
        next_status = cleaned_data.get("status", previous_status)
        if previous_status == Order.Status.CANCELED and next_status != Order.Status.CANCELED:
            self.add_error("status", "Una orden cancelada no puede volver a un estado activo.")
        return cleaned_data

    class Meta:
        model = Order
        fields = "__all__"
        labels = {
            "user": "Usuario",
            "idempotency_key": "Clave de idempotencia",
            "status": "Estado",
            "subtotal": "Subtotal",
            "shipping_cost": "Costo de envio",
            "total": "Total",
            "notes": "Notas",
            "stock_reingresado": "Stock reingresado",
            "direccion_envio": "Direccion de envio",
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
            "line_total": "Total linea",
        }

from django import forms

from .models import Producto, Subcategoria, Categorias, Marca


class ProductoAdminForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].queryset = Categorias.objects.filter(activo=True).order_by("nombre")
        self.fields["marca"].queryset = Marca.objects.filter(activo=True).order_by("nombre")
        self.fields["subcategoria"].queryset = Subcategoria.objects.none()

        categoria_id = None
        if self.is_bound:
            categoria_id = self.data.get("categoria")
        elif self.instance and self.instance.pk and self.instance.categoria_id:
            categoria_id = self.instance.categoria_id

        if categoria_id:
            self.fields["subcategoria"].queryset = Subcategoria.objects.filter(
                categoria_id=categoria_id,
            ).order_by("nombre")

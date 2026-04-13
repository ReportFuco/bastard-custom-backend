from django import forms

from .models import FranjaPromocional


class FranjaPromocionalAdminForm(forms.ModelForm):
    class Meta:
        model = FranjaPromocional
        fields = "__all__"
        widgets = {
            "color_fondo": forms.TextInput(attrs={"type": "color"}),
            "color_texto": forms.TextInput(attrs={"type": "color"}),
        }

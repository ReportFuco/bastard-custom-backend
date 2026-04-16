from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import Comuna, Direccion, Region, User
from .phone import normalize_chile_phone_number


class UserAdminCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "phone_number")

    def clean_phone_number(self):
        value = self.cleaned_data.get("phone_number", "")
        try:
            return normalize_chile_phone_number(value)
        except ValidationError as exc:
            raise forms.ValidationError(exc.message) from exc


class UserAdminChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"

    def clean_phone_number(self):
        value = self.cleaned_data.get("phone_number", "")
        try:
            return normalize_chile_phone_number(value)
        except ValidationError as exc:
            raise forms.ValidationError(exc.message) from exc


class DireccionAdminForm(forms.ModelForm):
    region = forms.ModelChoiceField(
        queryset=Region.objects.order_by("nombre"),
        required=False,
        label="Region",
    )

    class Meta:
        model = Direccion
        fields = ["usuario", "etiqueta", "direccion", "numero", "region", "comuna", "es_predeterminada"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["comuna"].queryset = Comuna.objects.none()

        region_id = None

        if self.is_bound:
            region_id = self.data.get("region")
        elif self.instance and self.instance.pk and self.instance.comuna_id:
            region_id = self.instance.comuna.region_id

        if region_id:
            self.fields["region"].initial = region_id
            self.fields["comuna"].queryset = Comuna.objects.filter(region_id=region_id).order_by("nombre")

    def clean(self):
        cleaned_data = super().clean()
        region = cleaned_data.get("region")
        comuna = cleaned_data.get("comuna")

        if comuna and region and comuna.region_id != region.id:
            self.add_error("comuna", "La comuna seleccionada no pertenece a la region.")

        return cleaned_data

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Region, Comuna, Direccion
from .phone import normalize_chile_phone_number

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value.lower()

    def validate_phone_number(self, value):
        try:
            return normalize_chile_phone_number(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message) from exc

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.email = user.email.lower()
        user.set_password(password)
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "phone_number", "is_customer"]
        read_only_fields = ["id", "email", "is_customer"]

    def validate_phone_number(self, value):
        try:
            return normalize_chile_phone_number(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message) from exc


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["id", "nombre"]


class ComunaSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    region_id = serializers.PrimaryKeyRelatedField(
        source="region",
        queryset=Region.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Comuna
        fields = ["id", "nombre", "region", "region_id"]


class DireccionSerializer(serializers.ModelSerializer):
    comuna_nombre = serializers.CharField(source="comuna.nombre", read_only=True)
    region_nombre = serializers.CharField(source="comuna.region.nombre", read_only=True)

    class Meta:
        model = Direccion
        fields = [
            "id",
            "etiqueta",
            "direccion",
            "comuna",
            "comuna_nombre",
            "region_nombre",
            "es_predeterminada",
            "creado_en",
            "actualizado_en",
        ]
        read_only_fields = ["id", "creado_en", "actualizado_en"]

    def validate(self, attrs):
        if self.instance is None and not attrs.get("comuna"):
            raise serializers.ValidationError({"comuna": "Este campo es obligatorio."})
        return attrs

    def create(self, validated_data):
        usuario = self.context["request"].user
        es_predeterminada = validated_data.get("es_predeterminada", False)
        if es_predeterminada:
            Direccion.objects.filter(usuario=usuario, es_predeterminada=True).update(es_predeterminada=False)
        return Direccion.objects.create(usuario=usuario, **validated_data)

    def update(self, instance, validated_data):
        es_predeterminada = validated_data.get("es_predeterminada", instance.es_predeterminada)
        if es_predeterminada:
            Direccion.objects.filter(
                usuario=instance.usuario,
                es_predeterminada=True,
            ).exclude(pk=instance.pk).update(es_predeterminada=False)
        return super().update(instance, validated_data)

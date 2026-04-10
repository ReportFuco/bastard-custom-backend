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
            "label",
            "direccion",
            "comuna",
            "comuna_nombre",
            "region_nombre",
            "is_default",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        if self.instance is None and not attrs.get("comuna"):
            raise serializers.ValidationError({"comuna": "Este campo es obligatorio."})
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        is_default = validated_data.get("is_default", False)
        if is_default:
            Direccion.objects.filter(user=user, is_default=True).update(is_default=False)
        return Direccion.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        is_default = validated_data.get("is_default", instance.is_default)
        if is_default:
            Direccion.objects.filter(user=instance.user, is_default=True).exclude(pk=instance.pk).update(is_default=False)
        return super().update(instance, validated_data)

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Region, Comuna, Direccion
from .serializers import (
    UserRegisterSerializer,
    UserProfileSerializer,
    RegionSerializer,
    ComunaSerializer,
    DireccionSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


class PublicTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class PublicTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DireccionViewSet(viewsets.ModelViewSet):
    serializer_class = DireccionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = (
            Direccion.objects
            .select_related("comuna", "comuna__region", "user")
            .order_by("-is_default", "label")
        )

        if self.request.user.is_superuser:
            return queryset

        return queryset.filter(user=self.request.user)


class RegionListView(generics.ListAPIView):
    queryset = Region.objects.all().order_by("nombre")
    serializer_class = RegionSerializer
    permission_classes = [permissions.AllowAny]


class ComunaListView(generics.ListAPIView):
    serializer_class = ComunaSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Comuna.objects.select_related("region").order_by("nombre")
        region_id = self.request.query_params.get("region_id")
        if region_id:
            if not region_id.isdigit():
                raise ValidationError({"region_id": "region_id debe ser numerico."})
            queryset = queryset.filter(region_id=region_id)
        return queryset

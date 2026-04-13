from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, permissions

from .models import FranjaPromocional
from .serializers import FranjaPromocionalSerializer


class FranjaPromocionalListView(generics.ListAPIView):
    serializer_class = FranjaPromocionalSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        ahora = timezone.now()
        return (
            FranjaPromocional.objects
            .filter(activa=True)
            .filter(Q(fecha_inicio__isnull=True) | Q(fecha_inicio__lte=ahora))
            .filter(Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=ahora))
            .order_by("-prioridad", "-actualizado_en")
        )

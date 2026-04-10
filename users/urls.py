from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import RegisterView, ProfileView, DireccionViewSet, RegionListView, ComunaListView

router = DefaultRouter()
router.register(r"direcciones", DireccionViewSet, basename="direcciones")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", ProfileView.as_view(), name="profile"),
    path("regions/", RegionListView.as_view(), name="regions-list"),
    path("comunas/", ComunaListView.as_view(), name="comunas-list"),
    path("", include(router.urls)),
]

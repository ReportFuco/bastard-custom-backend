from django.urls import path

from .views import FranjaPromocionalListView

urlpatterns = [
    path("bands/", FranjaPromocionalListView.as_view(), name="promotions-bands"),
]

from django.urls import path
from .views import route_optimizer

urlpatterns = [
    path("route/", route_optimizer, name="route_optimizer"),
]
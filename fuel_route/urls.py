from django.urls import path
from .views import FuelRouteView, HomeView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('route/', FuelRouteView.as_view(), name='fuel-route'),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EstateViewSet

router = DefaultRouter()
router.register(r'estate', EstateViewSet, basename='estate')

urlpatterns = [
    path('', include(router.urls)),
]

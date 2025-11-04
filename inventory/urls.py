from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserItemViewSet, EquipmentSlotsViewSet, ItemViewSet

router = DefaultRouter()
router.register(r"items", ItemViewSet, basename="items")
router.register(r"useritems", UserItemViewSet, basename="user-items")
router.register(r"equipment", EquipmentSlotsViewSet, basename="equipment")

urlpatterns = [
    path("", include(router.urls)),
]

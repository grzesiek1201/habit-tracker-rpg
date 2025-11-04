from rest_framework import viewsets, permissions
from inventory.models import Item, UserItem, EquipmentSlots
from inventory.serializers import (
    ItemSerializer,
    UserItemSerializer,
    EquipmentSlotsSerializer,
)


class ItemViewSet(viewsets.ModelViewSet):
    """ViewSet for browsing all available items (shop or database)."""

    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class UserItemViewSet(viewsets.ModelViewSet):
    """ViewSet for user's inventory (items owned by the logged-in user)."""

    serializer_class = UserItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter only items belonging to the logged-in user."""
        return UserItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically assign the logged-in user when creating an item."""
        serializer.save(user=self.request.user)


class EquipmentSlotsViewSet(viewsets.ModelViewSet):
    """ViewSet for managing equipment slots (equipped items)."""

    serializer_class = EquipmentSlotsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only the current user's equipment slots."""
        return EquipmentSlots.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Ensure the equipment slots are tied to the logged-in user."""
        serializer.save(user=self.request.user)

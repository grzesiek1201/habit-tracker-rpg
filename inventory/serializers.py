from rest_framework import serializers
from .models import Item, UserItem, EquipmentSlots


class ItemSerializer(serializers.ModelSerializer):
    """Display of the available items (in shop or database)."""

    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "description",
            "level",
            "rarity",
            "value",
            "bonuses",
            "consumable",
            "equipable",
            "type",
        ]


class UserItemSerializer(serializers.ModelSerializer):
    """Serializer for user's owned items (inventory)."""

    item = ItemSerializer(read_only=True)

    class Meta:
        model = UserItem
        fields = ["id", "item", "quantity", "is_equipped", "durability", "acquired_at"]
        read_only_fields = ["is_equipped", "acquired_at"]
        extra_kwargs = {
            "quantity": {"min_value": 1},
            "durability": {"min_value": 0, "max_value": 100},
        }

    def validate(self, data):
        item = data.get("item")
        if item and not item.equipable and data.get("is_equipped"):
            raise serializers.ValidationError("This item cannot be equipped.")
        return data


class EquipmentSlotsSerializer(serializers.ModelSerializer):
    """Serializer displaying all currently equipped items in each slot."""

    equipped_items = serializers.SerializerMethodField()

    class Meta:
        model = EquipmentSlots
        fields = ["equipped_items"]

    def get_equipped_items(self, obj):
        return {
            slot: UserItemSerializer(getattr(obj, slot)).data
            if getattr(obj, slot)
            else None
            for slot in EquipmentSlots.SLOTS
        }

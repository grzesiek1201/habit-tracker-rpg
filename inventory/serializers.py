from rest_framework import serializers
from inventory.models import Item, UserItem, EquipmentSlots
from user.models import Character


# --- ITEM SERIALIZER ---
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


# --- USER ITEM SERIALIZER ---
class UserItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)  # pokazuje dane o przedmiocie
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(), source='item', write_only=True
    )

    class Meta:
        model = UserItem
        fields = ['id', 'item', 'item_id', 'quantity', 'is_equipped', 'character']


# --- EQUIPMENT SLOTS SERIALIZER ---
class EquipmentSlotsSerializer(serializers.ModelSerializer):
    weapon = ItemSerializer(read_only=True)
    armor = ItemSerializer(read_only=True)
    accessory = ItemSerializer(read_only=True)

    class Meta:
        model = EquipmentSlots
        fields = ['id', 'character', 'weapon', 'armor', 'accessory']


# --- CHARACTER SERIALIZER ---
class CharacterSerializer(serializers.ModelSerializer):
    items = UserItemSerializer(many=True, read_only=True, source='useritem_set')
    equipment = EquipmentSlotsSerializer(read_only=True)

    class Meta:
        model = Character
        fields = [
            'id', 'user', 'name', 'level', 'exp', 'coins', 'health', 
            'strength', 'agility', 'intelligence', 'vitality',
            'items', 'equipment'
        ]

from rest_framework import serializers
from inventory.models import Item, UserItem, EquipmentSlots
from users.models import Character

# --- ITEM SERIALIZER ---
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


# --- USER ITEM SERIALIZER ---
class UserItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
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

    current_hp_percent = serializers.SerializerMethodField()
    current_mana_percent = serializers.SerializerMethodField()

    class Meta:
        model = Character
        fields = [
            'id',
            'user',
            'current_level',
            'current_exp',
            'current_hp',
            'max_hp',
            'current_hp_percent',
            'current_mana',
            'max_mana',
            'current_mana_percent',
            'strength',
            'dexterity',
            'intelligence',
            'vigor',
            'unallocated_stat_points',
            'items',
            'equipment',
        ]

    def get_current_hp_percent(self, obj):
        if obj.max_hp > 0:
            return int(obj.current_hp / obj.max_hp * 100)
        return 0

    def get_current_mana_percent(self, obj):
        if obj.max_mana > 0:
            return int(obj.current_mana / obj.max_mana * 100)
        return 0

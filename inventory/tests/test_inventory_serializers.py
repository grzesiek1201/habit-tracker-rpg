import pytest
from django.contrib.auth import get_user_model
from inventory.models import Item, UserItem, EquipmentSlots
from inventory.serializers import ItemSerializer, UserItemSerializer, EquipmentSlotsSerializer
from users.models import Character
from users.serializers import CharacterSerializer

User = get_user_model()


@pytest.mark.django_db
def test_item_serializer_create():
    data = {
        "name": "Sword",
        "description": "A test sword",
        "level": 1,
        "rarity": "common",
        "value": 100.0,
        "bonuses": {"strength": 5},
        "consumable": False,
        "equipable": True,
        "type": "weapon",
    }
    serializer = ItemSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    item = serializer.save()
    assert item.name == "Sword"
    assert item.bonuses["strength"] == 5


@pytest.mark.django_db
def test_useritem_serializer_read_and_write(create_user):
    user = create_user("player1")
    item = Item.objects.create(name="Helmet", value=50, equipable=True)

    # Create via serializer using item_id
    data = {"item_id": item.id, "quantity": 2}
    serializer = UserItemSerializer(data=data, context={"request": None})
    assert serializer.is_valid(), serializer.errors
    user_item = serializer.save(user=user)

    assert user_item.user == user
    assert user_item.item == item
    assert user_item.quantity == 2

    # Read serializer includes nested item
    serialized = UserItemSerializer(user_item)
    assert serialized.data["item"]["name"] == "Helmet"
    assert serialized.data["quantity"] == 2


@pytest.mark.django_db
def test_equipmentslots_serializer_read_only_fields(create_user):
    user = create_user("player2")
    character = Character.objects.create(user=user, current_level=1)
    weapon_item = Item.objects.create(name="Sword", value=100, equipable=True)
    armor_item = Item.objects.create(name="Armor", value=150, equipable=True)
    accessory_item = Item.objects.create(name="Ring", value=50, equipable=True)

    weapon_ui = UserItem.objects.create(user=user, item=weapon_item)
    armor_ui = UserItem.objects.create(user=user, item=armor_item)
    accessory_ui = UserItem.objects.create(user=user, item=accessory_item)

    slots = EquipmentSlots.objects.create(
        character=character,
        weapon=weapon_ui,
        armor=armor_ui,
        accessory=accessory_ui,
    )

    serializer = EquipmentSlotsSerializer(slots)
    data = serializer.data
    assert data["weapon"]["name"] == "Sword"
    assert data["armor"]["name"] == "Armor"
    assert data["accessory"]["name"] == "Ring"


@pytest.mark.django_db
def test_character_serializer_includes_items_and_equipment(create_user):
    user = create_user("hero")
    character = Character.objects.create(
        user=user,
        current_level=5,
        current_exp=120,
        current_hp=80,
        max_hp=100,
        current_mana=30,
        max_mana=50,
        strength=10,
        dexterity=8,
        intelligence=7,
        vigor=5,
        unallocated_stat_points=2,
    )

    # Add UserItem
    sword = Item.objects.create(name="Sword", value=100, equipable=True)
    user_item = UserItem.objects.create(user=user, item=sword)

    # Add EquipmentSlots
    slots = EquipmentSlots.objects.create(character=character, weapon=user_item)

    serializer = CharacterSerializer(character)
    data = serializer.data

    # Check basic fields
    assert data["current_level"] == 5
    assert data["current_hp_percent"] == 80
    assert data["current_mana_percent"] == 60

    # Check nested items
    assert len(data["items"]) == 1
    assert data["items"][0]["item"]["name"] == "Sword"

    # Check nested equipment
    assert data["equipment"]["weapon"]["name"] == "Sword"

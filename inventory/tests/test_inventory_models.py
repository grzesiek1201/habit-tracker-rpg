import pytest
from django.contrib.auth import get_user_model
from inventory.models import Item, UserItem, EquipmentSlots

User = get_user_model()


@pytest.mark.django_db
def test_create_item():
    item = Item.objects.create(
        name="Sword of Testing",
        description="A sword used for testing.",
        level=5,
        rarity="rare",
        value=150.00,
        bonuses={"strength": 10},
        consumable=False,
        equipable=True,
        type="weapon"
    )
    assert item.id is not None
    assert item.name == "Sword of Testing"
    assert item.bonuses["strength"] == 10
    assert item.equipable is True


@pytest.mark.django_db
def test_create_user_item():
    user = User.objects.create_user(username="tester", password="password")
    item = Item.objects.create(
        name="Helmet",
        description="A helmet",
        value=50,
        bonuses={},
        equipable=True
    )
    user_item = UserItem.objects.create(user=user, item=item, quantity=2)

    assert user_item.id is not None
    assert user_item.quantity == 2
    assert user_item.is_equipped is False


@pytest.mark.django_db
def test_equip_unequip_user_item():
    user = User.objects.create_user(username="tester2", password="password")
    item = Item.objects.create(
        name="Shield",
        description="A shield",
        value=70,
        bonuses={},
        equipable=True
    )
    user_item = UserItem.objects.create(user=user, item=item)

    # Equip
    user_item.equip()
    assert user_item.is_equipped is True

    # Unequip
    user_item.unequip()
    assert user_item.is_equipped is False


@pytest.mark.django_db
def test_equip_non_equipable_item_raises():
    user = User.objects.create_user(username="tester3", password="password")
    item = Item.objects.create(
        name="Potion",
        description="Healing",
        value=30,
        equipable=False
    )
    user_item = UserItem.objects.create(user=user, item=item)

    with pytest.raises(ValueError):
        user_item.equip()

@pytest.mark.django_db
def test_create_equipment_slots():
    user = User.objects.create_user(username="player1", password="pass")
    slots = EquipmentSlots.objects.create(user=user)
    assert slots.user.username == "player1"
    assert slots.get_equipped_items() == {}

@pytest.mark.django_db
def test_assign_items_to_slots():
    user = User.objects.create_user(username="player2", password="pass")
    item1 = Item.objects.create(name="Helmet", equipable=True, value=100)
    item2 = Item.objects.create(name="Sword", equipable=True, type="weapon", value=200)

    user_item1 = UserItem.objects.create(user=user, item=item1)
    user_item2 = UserItem.objects.create(user=user, item=item2)

    slots = EquipmentSlots.objects.create(user=user)
    slots.head = user_item1
    slots.weapon = user_item2
    user_item1.is_equipped = True
    user_item1.save()
    user_item2.is_equipped = True
    user_item2.save()
    slots.save()

    equipped = slots.get_equipped_items()
    assert equipped["head"] == user_item1
    assert equipped["weapon"] == user_item2

@pytest.mark.django_db
def test_str_representation():
    user = User.objects.create_user(username="player3", password="pass")
    slots = EquipmentSlots.objects.create(user=user)
    assert str(slots) == f"Equipment slots for {user.username}"
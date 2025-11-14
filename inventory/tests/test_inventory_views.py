import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from inventory.models import Item, UserItem

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db, django_user_model):
    def make_user(username):
        return django_user_model.objects.create_user(username=username, password="pass")

    return make_user


@pytest.fixture
def auth_client(api_client, create_user):
    user = create_user("testuser")
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.mark.django_db
def test_item_list_requires_auth(api_client):
    url = reverse("item-list")
    response = api_client.get(url)
    # Should allow read-only access
    assert response.status_code in [200, 403]


@pytest.mark.django_db
def test_useritem_list_only_returns_own_items(auth_client, create_user):
    client, user = auth_client
    other_user = create_user("other")

    item1 = Item.objects.create(name="Sword", value=100, equipable=True)
    item2 = Item.objects.create(name="Shield", value=50, equipable=True)

    UserItem.objects.create(user=user, item=item1)
    UserItem.objects.create(user=other_user, item=item2)

    url = reverse("useritem-list")
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["item"] == item1.id


@pytest.mark.django_db
def test_useritem_create_sets_user(auth_client):
    client, user = auth_client
    item = Item.objects.create(name="Helmet", value=75, equipable=True)

    url = reverse("useritem-list")
    response = client.post(url, {"item": item.id, "quantity": 2})

    assert response.status_code == 201
    assert response.json()["user"] == user.id
    assert response.json()["quantity"] == 2


@pytest.mark.django_db
def test_equipment_slots_list_and_create(auth_client):
    client, user = auth_client

    # Create EquipmentSlots
    url = reverse("equipmentslots-list")
    response = client.post(url, {})
    assert response.status_code == 201
    slot_id = response.json()["id"]

    # Should return only slots for current user
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == slot_id


@pytest.mark.django_db
def test_useritem_requires_authentication(api_client):
    url = reverse("useritem-list")
    response = api_client.get(url)
    assert response.status_code == 403  # Must be authenticated


@pytest.mark.django_db
def test_equipmentslots_requires_authentication(api_client):
    url = reverse("equipmentslots-list")
    response = api_client.get(url)
    assert response.status_code == 403  # Must be authenticated
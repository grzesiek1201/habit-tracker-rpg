import pytest
from rest_framework import status
from rest_framework.test import APIClient
from estate.models import Estate


@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_authenticated_user_can_create_estate(authenticated_client):
    data = {
        "house": 2,
        "sawmill": 3,
        "quarry": 1,
        "iron_mine": 1,
        "healing_pool": 0,
        "training_buddy": 0,
    }
    response = authenticated_client.post("/api/estate/", data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Estate.objects.count() == 1
    estate = Estate.objects.first()
    assert estate.user.email == "test@example.com"


@pytest.mark.django_db
def test_unauthenticated_user_cannot_create_estate(client):
    data = {
        "house": 2,
        "sawmill": 2,
        "quarry": 2,
        "iron_mine": 1,
        "healing_pool": 0,
        "training_buddy": 0,
    }
    response = client.post("/api/estate/", data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_estate_detail_authenticated(authenticated_client, estate):
    response = authenticated_client.get(f"/api/estate/{estate.id}/")
    assert response.status_code == status.HTTP_200_OK
    assert "wood" in response.data


@pytest.mark.django_db
def test_estate_patch_updates_levels(authenticated_client, estate):
    payload = {"house": estate.house + 1}
    response = authenticated_client.patch(f"/api/estate/{estate.id}/", payload)
    assert response.status_code == status.HTTP_200_OK
    estate.refresh_from_db()
    assert estate.house == payload["house"]


@pytest.mark.django_db
def test_readonly_fields_cannot_be_updated(authenticated_client, estate):
    payload = {"wood": 9999}
    response = authenticated_client.patch(f"/api/estate/{estate.id}/", payload)
    estate.refresh_from_db()
    assert estate.wood != 9999

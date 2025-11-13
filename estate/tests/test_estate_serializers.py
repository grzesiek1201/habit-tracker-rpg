import pytest
from estate.models import Estate
from estate.serializers import EstateSerializer


@pytest.mark.django_db
def test_estate_serializer_create_links_user(user):
    data = {
        "house": 1,
        "sawmill": 1,
        "quarry": 1,
        "iron_mine": 1,
        "healing_pool": 0,
        "training_buddy": 0,
    }
    serializer = EstateSerializer(data=data, context={"request": type("req", (), {"user": user})})
    assert serializer.is_valid(), serializer.errors
    instance = serializer.save()
    assert instance.user == user
    assert isinstance(instance, Estate)


@pytest.mark.django_db
def test_estate_serializer_prevents_downgrade(estate):
    data = {"house": estate.house - 1}  # downgrade attempt
    serializer = EstateSerializer(instance=estate, data=data, partial=True)
    assert not serializer.is_valid()
    assert "Cannot downgrade building level." in str(serializer.errors)

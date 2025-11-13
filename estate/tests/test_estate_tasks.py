import pytest
from unittest.mock import patch
from estate.tasks import daily_estate_production
from estate.models import Estate


@pytest.mark.django_db
def test_daily_estate_production_calls_produce_resources(monkeypatch, estate):
    """Ensure the task calls produce_resources() for every Estate."""
    called = {"count": 0}

    def mock_produce_resources(self):
        called["count"] += 1

    monkeypatch.setattr(Estate, "produce_resources", mock_produce_resources)

    daily_estate_production()

    assert called["count"] == Estate.objects.count()


@pytest.mark.django_db
def test_daily_estate_production_increases_resources(estate):
    """Check if the task actually increases stored resources."""
    estate.wood = 10
    estate.iron = 5
    estate.stone = 2
    estate.save()

    daily_estate_production()
    estate.refresh_from_db()

    assert estate.wood > 10
    assert estate.iron > 5
    assert estate.stone > 2


@pytest.mark.django_db
@patch("estate.models.Estate.produce_resources")
def test_daily_estate_production_error_tolerance(mock_produce, estate):
    """Ensure task does not crash if one estate fails."""
    mock_produce.side_effect = Exception("Production error")

    # Should not raise, even if some estates fail
    daily_estate_production()
    assert mock_produce.called

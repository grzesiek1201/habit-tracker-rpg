import pytest
from estate.models import Estate


@pytest.mark.django_db
def test_produce_resources_increases_based_on_buildings(estate):
    initial_wood, initial_iron, initial_stone = estate.wood, estate.iron, estate.stone

    estate.sawmill = 3
    estate.iron_mine = 2
    estate.quarry = 4
    estate.bonus_wood = 10   # +10%
    estate.bonus_iron = 0
    estate.bonus_stone = 50  # +50%
    estate.save()

    estate.produce_resources()
    estate.refresh_from_db()

    assert estate.wood > initial_wood
    assert estate.iron > initial_iron
    assert estate.stone > initial_stone

    assert round(estate.wood - initial_wood, 1) == 3.3
    assert estate.iron - initial_iron == 2
    assert estate.stone - initial_stone == 6


@pytest.mark.django_db
def test_apply_bonuses_recalculates_correctly(estate):
    estate.house = 2
    estate.healing_pool = 3
    estate.training_buddy = 4
    estate.save()

    estate.apply_bonuses()
    estate.refresh_from_db()

    assert estate.bonus_hp == 2 * 5 + 3 * 10
    assert estate.bonus_exp == 4 * 2


@pytest.mark.django_db
def test_estate_str_returns_username(estate):
    assert str(estate) == f"Estate of {estate.user.username}"

from django.core.validators import MinValueValidator
from django.db import models


class Estate(models.Model):
    house = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=1)
    sawmill = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=1)
    quarry = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=1)
    iron_mine = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=1)
    house = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=1)
    house = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=1)


class Estate_bonuses(models.Model):

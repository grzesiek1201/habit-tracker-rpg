from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from users.models import User


class Estate(models.Model):
    """Represents a player's estate with buildings, resources, and bonuses."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="estate")

    # Building levels
    house = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=1)
    sawmill = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=1)
    quarry = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=1)
    iron_mine = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=1)
    healing_pool = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)
    training_buddy = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], default=0)

    # Resources
    wood = models.PositiveIntegerField(default=0)
    iron = models.PositiveIntegerField(default=0)
    stone = models.PositiveIntegerField(default=0)

    # Bonuses
    bonus_hp = models.IntegerField(default=0)
    bonus_exp = models.IntegerField(default=0)
    bonus_wood = models.IntegerField(default=0)
    bonus_iron = models.IntegerField(default=0)
    bonus_stone = models.IntegerField(default=0)

    # Production control
    last_production = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Estate"
        verbose_name_plural = "Estates"

    def __str__(self):
        return f"Estate of {self.user.username}"

    # -------------------------------------------------------
    # LOGIC
    # -------------------------------------------------------
    def can_produce_today(self) -> bool:
        """Check if resources can be produced again today."""
        if not self.last_production:
            return True
        return timezone.now() - self.last_production >= timedelta(days=1)

    def produce_resources(self):
        """Produce resources once per day based on building levels and bonuses."""
        if not self.can_produce_today():
            raise ValueError("Resources can only be produced once per day.")

        self.wood += int(self.sawmill * (1 + self.bonus_wood / 100))
        self.iron += int(self.iron_mine * (1 + self.bonus_iron / 100))
        self.stone += int(self.quarry * (1 + self.bonus_stone / 100))
        self.last_production = timezone.now()
        self.save()

    def apply_bonuses(self):
        """Recalculate bonuses based on building levels."""
        self.bonus_hp = self.house * 5 + self.healing_pool * 10
        self.bonus_exp = self.training_buddy * 2
        self.save()

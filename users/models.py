from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models import Index, UniqueConstraint
from django.db.models.functions import Lower


# ===================================================
# USER MODEL
# ===================================================
class User(AbstractUser):
    """Custom user model """

    email = models.EmailField(blank=False, unique=True)
    previous_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

    def clean(self):
        """Ensure lowercase email and strip whitespace."""
        super().clean()
        if self.email:
            self.email = self.email.lower().strip()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        constraints = [
            UniqueConstraint(Lower("email"), name="unique_lower_email"),
        ]
        indexes = [
            Index(Lower("email"), name="idx_lower_email"),
        ]


# ===================================================
# CHARACTER MODEL
# ===================================================
class Character(models.Model):
    """Represents an RPG character linked to a user account."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="character")

    # RPG attributes
    current_hp = models.IntegerField(validators=[MinValueValidator(0)], default=10)
    max_hp = models.IntegerField(default=10)
    current_exp = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    current_level = models.IntegerField(default=1)

    # Avatar / profile
    avatar_picture = models.ImageField(upload_to="avatars/", null=True, blank=True)

    # Estate bonuses
    estate_bonus_hp = models.IntegerField(default=0)
    estate_bonus_exp = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s character (lvl {self.current_level})"

    @transaction.atomic
    def gain_exp(self, amount: int) -> None:
        """Increase experience and handle level-up logic."""
        if amount < 0:
            raise ValueError("EXP amount must be non-negative.")
        self.current_exp += amount
        while self.current_exp >= self.exp_to_next_level():
            self.current_exp -= self.exp_to_next_level()
            self.current_level += 1
            self.max_hp += 10
            self.current_hp = self.max_hp
        self.save()

    def exp_to_next_level(self) -> int:
        """Level-up formula."""
        return 100 * self.current_level

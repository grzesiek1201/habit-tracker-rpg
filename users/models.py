from django.contrib.auth.models import AbstractUser
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
    profile_picture = models.ImageField(upload_to="profile_picture/", null=True, blank=True)

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
    current_mana= models.IntegerField(validators=[MinValueValidator(0)], default=10)
    max_hp = models.IntegerField(default=10)
    max_mana =models.IntegerField(default=10)
    current_exp = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    current_level = models.IntegerField(default=1)
    strength = models.IntegerField(validators=[MinValueValidator(0)], default=1)
    dexterity = models.IntegerField(validators=[MinValueValidator(0)], default=1)
    intelligence = models.IntegerField(validators=[MinValueValidator(0)], default=1)
    vigor = models.IntegerField(validators=[MinValueValidator(0)], default=1)
    unallocated_stat_points = models.IntegerField(default=0)

    # Avatar / profile
    avatar_picture = models.ImageField(upload_to="avatars/", null=True, blank=True)

    # Estate bonuses
    estate_bonus_hp = models.IntegerField(default=0)
    estate_bonus_exp = models.IntegerField(default=0)


    def __str__(self):
        return f"{self.user.username}'s character (lvl {self.current_level})"

    @transaction.atomic
    def allocate_stat_points(self, str_points: int, dex_points: int, int_points: int):
        """
        Manual stat allocation by player.
        """
        total = str_points + dex_points + int_points
        if total > self.unallocated_stat_points:
            raise ValueError("Not enough unallocated stat points.")
        if str_points < 0 or dex_points < 0 or int_points < 0:
            raise ValueError("Stat points cannot be negative.")

        # Apply points
        self.strength += str_points
        self.dexterity += dex_points
        self.intelligence += int_points
        self.vigor += int_points
        self.max_mana += int_points * 5  # INT bonus

        # Decrease unallocated points
        self.unallocated_stat_points -= total
        self.save()

    def exp_to_next_level(self) -> int:
        """Level-up formula."""
        return 100 * self.current_level

    def regen_daily_mana(self):
        """Regenerate 50% of max mana daily."""
        regen_amount = int(self.max_mana * 0.5)
        self.current_mana = min(self.current_mana + regen_amount, self.max_mana)
        self.save()
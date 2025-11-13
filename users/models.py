from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.db.models import Index, UniqueConstraint
from django.db.models.functions import Lower


# ===================================================
# USER MODEL
# ===================================================
class User(AbstractUser):
    """Custom user model with lowercase unique email."""

    email = models.EmailField(unique=True)
    previous_login = models.DateTimeField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profile_picture/", null=True, blank=True)

    def __str__(self):
        return self.username

    def clean(self):
        """Normalize email to lowercase."""
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
    """Represents an RPG character linked to a user."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="character")

    # RPG stats
    current_hp = models.PositiveIntegerField(default=10)
    current_mana = models.PositiveIntegerField(default=10)
    max_hp = models.PositiveIntegerField(default=10)
    max_mana = models.PositiveIntegerField(default=10)
    current_exp = models.PositiveIntegerField(default=0)
    current_level = models.PositiveIntegerField(default=1)
    strength = models.PositiveIntegerField(default=1)
    dexterity = models.PositiveIntegerField(default=1)
    intelligence = models.PositiveIntegerField(default=1)
    vigor = models.PositiveIntegerField(default=1)
    unallocated_stat_points = models.PositiveIntegerField(default=0)

    # Estate bonuses
    estate_bonus_hp = models.IntegerField(default=0)
    estate_bonus_exp = models.IntegerField(default=0)

    # Avatar
    avatar_picture = models.ImageField(upload_to="avatars/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s character (lvl {self.current_level})"

    # ------------------------------
    # GAME LOGIC METHODS
    # ------------------------------
    @transaction.atomic
    def allocate_stat_points(self, str_points: int, dex_points: int, int_points: int, vigor_points: int = 0):
        """Allocate stat points safely within transaction."""
        total = str_points + dex_points + int_points + vigor_points
        if total > self.unallocated_stat_points:
            raise ValueError("Not enough unallocated stat points.")
        if any(p < 0 for p in [str_points, dex_points, int_points, vigor_points]):
            raise ValueError("Stat points cannot be negative.")

        self.strength += str_points
        self.dexterity += dex_points
        self.intelligence += int_points
        self.vigor += vigor_points

        # Derived bonuses
        self.max_mana += int_points * 5
        self.max_hp += vigor_points * 10

        self.unallocated_stat_points -= total
        self.save()

    def exp_to_next_level(self) -> int:
        """XP required for next level-up."""
        return int(100 * (self.current_level ** 1.5))

    @transaction.atomic
    def gain_exp(self, amount: int):
        """Increase EXP and handle level-ups."""
        if amount <= 0:
            return
        self.current_exp += amount

        while self.current_exp >= self.exp_to_next_level():
            self.current_exp -= self.exp_to_next_level()
            self.current_level += 1
            self.unallocated_stat_points += 3  # or formula
            self.max_hp += 5
            self.max_mana += 3

        self.save()

    def regen_daily_mana(self):
        """Regenerate 50% of max mana daily."""
        regen_amount = int(self.max_mana * 0.5)
        self.current_mana = min(self.current_mana + regen_amount, self.max_mana)
        self.save()

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db.models import UniqueConstraint, Index
from django.db.models.functions import Lower


class User(AbstractUser):
    """ Custom user model for the habit tracker RPG with RPG attributes
    """
    #User attributes
    email = models.EmailField(blank=False)
    previous_login = models.DateTimeField(null=True, blank=True)
    #RPG attributes
    current_hp = models.IntegerField(validators=[MinValueValidator(0)], default=10)
    max_hp = models.IntegerField(default=10)
    current_exp = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    current_level = models.IntegerField(default=1)
    avatar_picture = models.ImageField(upload_to='avatars/', null=True, blank=True)

    # Estate bonuses
    estate_bonus_hp = models.IntegerField(default=0)
    estate_bonus_exp = models.IntegerField(default=0)

    def __str__(self):
        return self.username

    def gain_exp(self, amount: int):
        """
        Increases the user's experience points and level up if needed.
        Level up heals the user to full health.
        """
        self.current_exp += amount
        while self.current_exp >= self.exp_to_next_level():
            self.current_exp -= self.exp_to_next_level()
            self.current_level += 1
            self.max_hp += 10
            self.current_hp = self.max_hp
        self.save()

    def exp_to_next_level(self) -> int:
        """
        leveling up formula
        """
        return 100 * self.current_level
    
    class Meta:
        constraints = [
            UniqueConstraint(
                Lower("email"),
                name="unique_lower_email",
            ),
        ]
        indexes = [
            Index(Lower("email"), name="idx_lower_email"),
        ]
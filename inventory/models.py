from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Item(models.Model):
    ITEM_TYPES = [
        ("weapon", "Weapon"),
        ("armor", "Armor"),
        ("potion", "Potion"),
        ("misc", "Miscellaneous"),
    ]
    RARITY_CHOICES = [
        ("common", "Common"),
        ("uncommon", "Uncommon"),
        ("rare", "Rare"),
        ("epic", "Epic"),
        ("legendary", "Legendary"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    level = models.PositiveIntegerField(default=1)
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default="common")
    value = models.DecimalField(max_digits=10, decimal_places=2)
    bonuses = models.JSONField(default=dict)
    consumable = models.BooleanField(default=False)
    equipable = models.BooleanField(default=False)
    type = models.CharField(max_length=20, choices=ITEM_TYPES, default="misc")

    def __str__(self):
        return self.name


class UserItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inventory")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    is_equipped = models.BooleanField(default=False)
    durability = models.PositiveIntegerField(default=100)
    acquired_at = models.DateTimeField(auto_now_add=True)

    def equip(self):
        if not self.item.equipable:
            raise ValueError("This item cannot be equipped.")
        if self.is_equipped:
            raise ValueError("This item is already equipped.")
        self.is_equipped = True
        self.save()

    def unequip(self):
        self.is_equipped = False
        self.save()

    def __str__(self):
        return f"{self.user.username} - {self.item.name}"

    class Meta:
        unique_together = ("user", "item")


class EquipmentSlots(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="equipment"
    )
    head = models.ForeignKey(
        "UserItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_head",
    )
    chest = models.ForeignKey(
        "UserItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_chest",
    )
    legs = models.ForeignKey(
        "UserItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_legs",
    )
    feet = models.ForeignKey(
        "UserItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_feet",
    )
    hands = models.ForeignKey(
        "UserItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_hands",
    )
    neck = models.ForeignKey(
        "UserItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_neck",
    )
    ring = models.ForeignKey(
        "UserItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_ring",
    )
    weapon = models.ForeignKey(
        "UserItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_weapon",
    )
    shield = models.ForeignKey(
        "UserItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipped_as_shield",
    )

    SLOTS = [
        "head",
        "chest",
        "legs",
        "feet",
        "hands",
        "neck",
        "ring",
        "weapon",
        "shield",
    ]

    def get_equipped_items(self):
        return {slot: getattr(self, slot) for slot in self.SLOTS if getattr(self, slot)}

    def __str__(self):
        return f"Equipment slots for {self.user.username}"

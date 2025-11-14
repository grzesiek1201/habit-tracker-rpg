from django.contrib import admin
from inventory.models import Item, UserItem, EquipmentSlots


# --- Item Admin ---
@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "rarity", "level", "value", "equipable", "consumable")
    list_filter = ("type", "rarity", "equipable", "consumable")
    search_fields = ("name", "description")
    ordering = ("type", "rarity", "level")
    readonly_fields = ("id",)


# --- UserItem Admin ---
@admin.register(UserItem)
class UserItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "item", "quantity", "is_equipped", "durability", "acquired_at")
    list_filter = ("is_equipped", "item__type", "item__rarity")
    ordering = ("-acquired_at",)
    readonly_fields = ("id", "acquired_at")


# --- EquipmentSlots Admin ---
@admin.register(EquipmentSlots)
class EquipmentSlotsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "head",
        "chest",
        "legs",
        "feet",
        "hands",
        "neck",
        "ring",
        "weapon",
        "shield",
    )
    readonly_fields = ("id",)

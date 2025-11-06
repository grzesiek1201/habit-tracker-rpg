from django.contrib import admin
from django.utils.timezone import now

from .models import User, Character


# ==============================
# Inline: show Character stats inside User view
# ==============================
class CharacterInline(admin.StackedInline):
    model = Character
    can_delete = False
    verbose_name_plural = "Character"
    readonly_fields = (
        "current_level",
        "current_exp",
        "max_hp",
        "current_hp",
    )


# ==============================
# Admin customization for User model
# ==============================
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # Displayed columns in the user list
    list_display = (
        "username",
        "email",
        "is_active",
        "is_staff",
        "last_login",
        "previous_login",
        "date_joined",
        "get_level",
        "days_since_joined",
    )

    # Filters on the right side panel
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        "date_joined",
    )

    # Fields searchable in admin
    search_fields = (
        "username",
        "email",
        "character__current_level",
    )

    # Default ordering
    ordering = ("-last_login",)

    # Read-only fields
    readonly_fields = (
        "last_login",
        "previous_login",
        "date_joined",
    )

    # Inline for Character
    inlines = [CharacterInline]

    # ==============================
    # Custom fieldsets
    # ==============================
    fieldsets = (
        ("Basic Info", {"fields": ("username", "email", "password")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Login History", {"fields": ("last_login", "previous_login", "date_joined")}),
    )

    # ==============================
    # Custom actions
    # ==============================
    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Reset EXP for linked characters")
    def reset_exp(self, request, queryset):
        for user in queryset:
            if hasattr(user, "character"):
                user.character.current_exp = 0
                user.character.save()

    actions = ["deactivate_users", "reset_exp"]

    # ==============================
    # Custom display methods
    # ==============================
    def get_level(self, obj):
        """Show user's current level if linked to a character."""
        return getattr(obj.character, "current_level", "-")

    get_level.short_description = "Level"

    def days_since_joined(self, obj):
        """Show how many days have passed since registration."""
        return (now() - obj.date_joined).days

    days_since_joined.short_description = "Days since joined"

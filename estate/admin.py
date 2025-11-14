from django.contrib import admin
from estate.models import Estate

@admin.action(description="Produce resources now")
def produce_resources(modeladmin, request, queryset):
    for estate in queryset:
        try:
            estate.produce_resources()
        except ValueError as e:
            modeladmin.message_user(request, f"{estate}: {e}", level='error')

@admin.action(description="Apply bonuses now")
def apply_bonuses(modeladmin, request, queryset):
    for estate in queryset:
        estate.apply_bonuses()
        modeladmin.message_user(request, f"Bonuses applied for {estate}")

@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'house', 'sawmill', 'quarry', 'iron_mine', 'healing_pool', 'training_buddy',
        'wood', 'iron', 'stone', 'bonus_hp', 'bonus_exp', 'bonus_wood', 'bonus_iron', 'bonus_stone',
        'last_production'
    )
    list_filter = ('house', 'sawmill', 'quarry', 'iron_mine', 'healing_pool', 'training_buddy')
    search_fields = ('user__username',)
    readonly_fields = (
        'wood', 'iron', 'stone', 'bonus_hp', 'bonus_exp', 'bonus_wood', 'bonus_iron', 'bonus_stone',
        'last_production'
    )
    actions = [produce_resources, apply_bonuses]

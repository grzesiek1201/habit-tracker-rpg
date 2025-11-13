from rest_framework import serializers
from estate.models import Estate


class EstateSerializer(serializers.ModelSerializer):
    """Serializer for estate data. Ensures user linkage and safe updates."""

    class Meta:
        model = Estate
        fields = [
            "id",
            "house",
            "sawmill",
            "quarry",
            "iron_mine",
            "healing_pool",
            "training_buddy",
            "wood",
            "iron",
            "stone",
            "bonus_hp",
            "bonus_exp",
            "bonus_wood",
            "bonus_iron",
            "bonus_stone",
        ]
        read_only_fields = [
            "wood", "iron", "stone",
            "bonus_hp", "bonus_exp", "bonus_wood", "bonus_iron", "bonus_stone",
        ]

    def create(self, validated_data):
        """Ensure the estate is linked to the authenticated user."""
        user = self.context["request"].user
        estate = Estate.objects.create(user=user, **validated_data)
        return estate

    def validate(self, attrs):
        """Optional domain validation: prevent level downgrade."""
        instance = getattr(self, "instance", None)
        if instance:
            for field in ["house", "sawmill", "quarry", "iron_mine", "healing_pool", "training_buddy"]:
                if attrs.get(field, getattr(instance, field)) < getattr(instance, field):
                    raise serializers.ValidationError({field: "Cannot downgrade building level."})
        return attrs

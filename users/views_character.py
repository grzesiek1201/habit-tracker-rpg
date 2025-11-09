from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from users.models import Character
from users.serializers import CharacterSerializer


class CharacterViewSet(viewsets.ModelViewSet):
    """
    ViewSet handling character operations:
    - CRUD for Character model
    - Manual stat allocation
    - Restore HP/Mana
    """
    queryset = Character.objects.all()
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Limit access to the authenticated user's character."""
        return Character.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Ensure the character is linked to the logged-in user."""
        serializer.save(user=self.request.user)

    # --------------------------------------------
    # Custom actions
    # --------------------------------------------

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def allocate_stats(self, request, pk=None):
        """
        Manually distribute stat points to STR/DEX/INT/VIG.
        Example body:
        {
            "strength": 2,
            "dexterity": 1,
            "intelligence": 0,
            "vigor": 2
        }
        """
        character = self.get_object()
        data = request.data

        try:
            str_points = int(data.get("strength", 0))
            dex_points = int(data.get("dexterity", 0))
            int_points = int(data.get("intelligence", 0))
            vig_points = int(data.get("vigor", 0))
        except (TypeError, ValueError):
            return Response(
                {"detail": "All stat values must be integers."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total = str_points + dex_points + int_points + vig_points
        if total <= 0:
            return Response(
                {"detail": "At least one point must be allocated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                if total > character.unallocated_stat_points:
                    return Response(
                        {"detail": "Not enough unallocated stat points."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Update stats
                character.strength += str_points
                character.dexterity += dex_points
                character.intelligence += int_points
                character.vigor += vig_points

                # Apply derived bonuses
                character.max_mana += int_points * 5
                character.max_hp += vig_points * 5

                character.unallocated_stat_points -= total
                character.save()

            return Response(
                {"detail": "Stats allocated successfully."},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"detail": f"Error allocating stats: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def restore(self, request, pk=None):
        """
        Fully restore HP and Mana (e.g., after resting).
        """
        character = self.get_object()
        character.current_hp = character.max_hp
        character.current_mana = character.max_mana
        character.save()
        return Response(
            {"detail": "Character fully restored."},
            status=status.HTTP_200_OK,
        )

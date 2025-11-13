from rest_framework import permissions, viewsets
from estate.models import Estate
from estate.serializers import EstateSerializer


class EstateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user estate."""

    serializer_class = EstateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only the authenticated user's estate."""
        user = self.request.user
        if user.is_authenticated:
            return Estate.objects.filter(user=user)
        return Estate.objects.none()

    def perform_create(self, serializer):
        """Link the estate to the current user."""
        serializer.save(user=self.request.user)

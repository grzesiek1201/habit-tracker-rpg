from rest_framework import generics, status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.models import User
from users.serializers import (
    ChangePasswordSerializer,
    UserCreateSerializer,
    UserReadSerializer,
    UserUpdateSerializer,
)


class UserCreateView(generics.CreateAPIView):
    """View for user registration."""
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"


class LoginView(TokenObtainPairView):
    """JWT login view (return access + refresh tokens)."""
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"


class RefreshView(TokenRefreshView):
    """View for refreshing access token using a refresh token."""
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "refresh"


class MeView(RetrieveAPIView):
    """Returns data for the currently authenticated user."""
    serializer_class = UserReadSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ProfileUpdateView(UpdateAPIView):
    """Allows user to update their email or avatar."""
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Allows the user to change their password and invalidates all active tokens."""
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "change_password"

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]

        # Verify old password
        if not user.check_password(old_password):
            return Response(
                {"detail": "Invalid old password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update password
        user.set_password(serializer.validated_data["new_password1"])
        user.save()

        # Blacklist all active tokens (force logout on all devices)
        tokens = OutstandingToken.objects.filter(user=user)
        for token in tokens:
            try:
                BlacklistedToken.objects.get_or_create(token=token)
            except Exception:
                pass  # Ignore already blacklisted tokens

        return Response({"detail": "Password changed successfully."}, status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    """Logs out the user by blacklisting the refresh token."""
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "logout"

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"detail": "Missing refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Attempt to blacklist the provided refresh token
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_205_RESET_CONTENT)


class CharacterViewSet(viewsets.ModelViewSet):
    """
    Manage game characters. Each user has one character.
    """
    serializer_class = CharacterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return only current user's character(s)
        return Character.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Ensure character is bound to the authenticated user
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def allocate_stats(self, request, pk=None):
        """Manually allocate stat points (STR, DEX, INT, VIG)."""
        character = self.get_object()
        data = request.data

        strength = int(data.get("strength", 0))
        dexterity = int(data.get("dexterity", 0))
        intelligence = int(data.get("intelligence", 0))
        vigor = int(data.get("vigor", 0))

        total = strength + dexterity + intelligence + vigor
        if total > character.unallocated_stat_points:
            return Response(
                {"detail": "Not enough unallocated stat points."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Apply allocation
        character.strength += strength
        character.dexterity += dexterity
        character.intelligence += intelligence
        character.vigor += vigor
        character.unallocated_stat_points -= total

        # Update dependent stats
        character.max_mana = 50 + (character.intelligence * 5)
        character.max_hp = 100 + (character.vigor * 5)
        character.save()

        return Response(CharacterSerializer(character).data)
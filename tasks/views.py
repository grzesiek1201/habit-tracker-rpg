from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tasks.enums import HabitType, TasksStatus, TasksStrength
from tasks.models import Daily, Habit, Todo
from tasks.serializers import DailySerializer, HabitSerializer, TodoSerializer


class HabitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user habits (good or bad).
    Supports filtering by type, status, and strength.
    """

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["type", "status", "strength"]
    search_fields = ["name", "notes"]
    ordering_fields = ["created_at", "name", "strength"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return habits for the authenticated user only"""
        return Habit.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically assign the habit to the current user"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="complete")
    @transaction.atomic
    def complete_habit(self, request, pk=None):
        """
        Mark a habit as completed and apply rewards/penalties.
        - Good habit: gain EXP (10), increase strength
        - Bad habit: lose HP (5), decrease strength
        """
        habit = self.get_object()

        if habit.type == HabitType.GOOD:
            # Reward for completing a good habit
            request.user.gain_exp(10)
            habit.strength = self._increase_strength(habit.strength)
            message = "Good habit completed! +10 EXP"
        elif habit.type == HabitType.BAD:
            # Penalty for doing a bad habit
            request.user.current_hp = max(0, request.user.current_hp - 5)
            request.user.save()
            habit.strength = self._decrease_strength(habit.strength)
            message = "Bad habit recorded. -5 HP"
        else:
            return Response({"detail": "Invalid habit type."}, status=status.HTTP_400_BAD_REQUEST)

        habit.save()

        return Response(
            {
                "detail": message,
                "habit": HabitSerializer(habit).data,
                "user": {
                    "current_hp": request.user.current_hp,
                    "max_hp": request.user.max_hp,
                    "current_exp": request.user.current_exp,
                    "current_level": request.user.current_level,
                },
            },
            status=status.HTTP_200_OK,
        )

    def _increase_strength(self, current_strength):
        """Increase habit strength by one level"""
        strength_order = [
            TasksStrength.FRAGILE,
            TasksStrength.WEAK,
            TasksStrength.STABLE,
            TasksStrength.STRONG,
            TasksStrength.UNBREAKABLE,
        ]
        try:
            current_index = strength_order.index(current_strength)
            if current_index < len(strength_order) - 1:
                return strength_order[current_index + 1]
        except (ValueError, IndexError):
            pass
        return current_strength

    def _decrease_strength(self, current_strength):
        """Decrease habit strength by one level"""
        strength_order = [
            TasksStrength.FRAGILE,
            TasksStrength.WEAK,
            TasksStrength.STABLE,
            TasksStrength.STRONG,
            TasksStrength.UNBREAKABLE,
        ]
        try:
            current_index = strength_order.index(current_strength)
            if current_index > 0:
                return strength_order[current_index - 1]
        except (ValueError, IndexError):
            pass
        return current_strength


class DailyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing daily recurring tasks.
    Supports filtering by status, repeats pattern, and active/inactive state.
    """

    serializer_class = DailySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["status", "repeats", "repeat_on"]
    search_fields = ["name", "notes"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return daily tasks for the authenticated user only"""
        return Daily.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically assign the daily task to the current user"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="complete")
    @transaction.atomic
    def complete_daily(self, request, pk=None):
        """
        Mark a daily task as completed and reward EXP.
        Daily tasks give +15 EXP and increase strength.
        """
        daily = self.get_object()

        # Check if already completed
        if daily.status == TasksStatus.COMPLETED:
            return Response(
                {"detail": "Daily task already completed for today."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reward user
        request.user.gain_exp(15)

        # Increase strength
        daily.strength = self._increase_strength(daily.strength)
        daily.status = TasksStatus.COMPLETED
        daily.save()

        return Response(
            {
                "detail": "Daily task completed! +15 EXP",
                "daily": DailySerializer(daily).data,
                "user": {
                    "current_hp": request.user.current_hp,
                    "max_hp": request.user.max_hp,
                    "current_exp": request.user.current_exp,
                    "current_level": request.user.current_level,
                },
            },
            status=status.HTTP_200_OK,
        )

    def _increase_strength(self, current_strength):
        """Increase daily strength by one level"""
        strength_order = [
            TasksStrength.FRAGILE,
            TasksStrength.WEAK,
            TasksStrength.STABLE,
            TasksStrength.STRONG,
            TasksStrength.UNBREAKABLE,
        ]
        try:
            current_index = strength_order.index(current_strength)
            if current_index < len(strength_order) - 1:
                return strength_order[current_index + 1]
        except (ValueError, IndexError):
            pass
        return current_strength


class TodoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing one-time todo tasks.
    Supports filtering by completion status and due date.
    """

    serializer_class = TodoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["is_completed"]
    search_fields = ["name", "notes"]
    ordering_fields = ["created_at", "due_date", "name"]
    ordering = ["due_date", "-created_at"]

    def get_queryset(self):
        """Return todos for the authenticated user only"""
        queryset = Todo.objects.filter(user=self.request.user)

        # Optional filtering for active/planned/completed
        filter_type = self.request.query_params.get("filter", None)
        if filter_type == "active":
            queryset = queryset.filter(is_completed=False)
        elif filter_type == "completed":
            queryset = queryset.filter(is_completed=True)
        elif filter_type == "planned":
            from django.utils import timezone

            queryset = queryset.filter(is_completed=False, due_date__gt=timezone.now().date())

        return queryset

    def perform_create(self, serializer):
        """Automatically assign the todo to the current user"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="complete")
    @transaction.atomic
    def complete_todo(self, request, pk=None):
        """
        Mark a todo as completed and reward EXP.
        Todo tasks give +20 EXP and increase strength.
        """
        todo = self.get_object()

        # Check if already completed
        if todo.is_completed:
            return Response(
                {"detail": "Todo already completed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reward user
        request.user.gain_exp(20)

        # Increase strength and mark as completed
        todo.strength = self._increase_strength(todo.strength)
        todo.is_completed = True
        todo.save()

        return Response(
            {
                "detail": "Todo completed! +20 EXP",
                "todo": TodoSerializer(todo).data,
                "user": {
                    "current_hp": request.user.current_hp,
                    "max_hp": request.user.max_hp,
                    "current_exp": request.user.current_exp,
                    "current_level": request.user.current_level,
                },
            },
            status=status.HTTP_200_OK,
        )

    def _increase_strength(self, current_strength):
        """Increase todo strength by one level"""
        strength_order = [
            TasksStrength.FRAGILE,
            TasksStrength.WEAK,
            TasksStrength.STABLE,
            TasksStrength.STRONG,
            TasksStrength.UNBREAKABLE,
        ]
        try:
            current_index = strength_order.index(current_strength)
            if current_index < len(strength_order) - 1:
                return strength_order[current_index + 1]
        except (ValueError, IndexError):
            pass
        return current_strength

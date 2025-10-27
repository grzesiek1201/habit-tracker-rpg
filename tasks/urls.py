from django.urls import include, path
from rest_framework.routers import DefaultRouter

from tasks.views import DailyViewSet, HabitViewSet, TodoViewSet

router = DefaultRouter()
router.register(r"habits", HabitViewSet, basename="habit")
router.register(r"dailies", DailyViewSet, basename="daily")
router.register(r"todos", TodoViewSet, basename="todo")

urlpatterns = [
    path("", include(router.urls)),
]

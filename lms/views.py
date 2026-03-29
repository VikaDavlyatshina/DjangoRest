from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from lms.models import Course, Lesson
from lms.paginators import CoursePagination
from lms.serializers import (CourseDetailSerializer, CourseSerializer,
                             LessonSerializer)
from users.models import Payments
from users.permissions import IsModerator, IsOwner

# Create your views here.

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Получить список курсов"
))
class CourseViewSet(ModelViewSet):
    """ViewSet для управления курсами"""

    queryset = Course.objects.all()
    pagination_class = CoursePagination

    def get_serializer_class(self):
        """Динамический выбор сериализатора"""
        if self.action == "list":
            return CourseSerializer

        if self.action == "retrieve":
            if self._has_full_access(self.request.user, self.get_object()):
                return CourseDetailSerializer

        return CourseSerializer

    def _has_full_access(self, user, course):
        """
        Проверяет доступ к полной версии курса (урокам).
        Доступ имеют: модераторы, владельцы, покупатели.
        """
        if not user or not user.is_authenticated:
            return False

        if user.groups.filter(name="Moderators").exists():
            return True

        if course.owner == user:
            return True

        return Payments.objects.filter(user=user, paid_course=course).exists()

    def get_queryset(self):
        """
        Возвращает курсы для списка "Мои курсы":
        - Свои курсы (владелец)
        - Купленные курсы (есть платёж)
        """
        user = self.request.user

        if not user.is_authenticated:
            return Course.objects.none()

        if user.groups.filter(name="Moderators").exists():
            return Course.objects.all()

        owned = Course.objects.filter(owner=user)

        purchased_ids = Payments.objects.filter(
            user=user, paid_course__isnull=False
        ).values_list("paid_course", flat=True)

        return owned | Course.objects.filter(id__in=purchased_ids)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), (~IsModerator)()]

        elif self.action in ["update", "partial_update"]:
            return [IsAuthenticated(), (IsModerator | IsOwner)()]

        elif self.action == "destroy":
            return [IsAuthenticated(), IsOwner()]

        elif self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]

        return super().get_permissions()


class LessonCreateAPIView(generics.CreateAPIView):
    """Создание нового урока."""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, ~IsModerator]  # Только обычные пользователи

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    """Получение списка всех уроков."""

    serializer_class = LessonSerializer
    pagination_class = CoursePagination

    def get_queryset(self):
        user = self.request.user

        # Модератор видит всё
        if user.groups.filter(name="Moderators").exists():
            return Lesson.objects.all()

        # Обычный пользователь — только свои курсы
        return Lesson.objects.filter(owner=user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Получение детальной информации о конкретном уроке."""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner | IsModerator]


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Обновление существующего урока."""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner | IsModerator]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока."""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwner]

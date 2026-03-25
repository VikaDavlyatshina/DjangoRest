from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from lms.models import Course, Lesson
from lms.serializers import (CourseDetailSerializer, CourseSerializer,
                             LessonSerializer)
from users.models import Subscription
from users.permissions import IsModerator, IsOwner

# Create your views here.


class CourseViewSet(ModelViewSet):
    """" ViewSet для управления курсами """

    queryset = Course.objects.all()

    def get_serializer_class(self):
        """
        Динамический выбор сериализатора.
        - Для списка (list) → CourseSerializer (без уроков)
        - Для детального просмотра (retrieve):
            - Если пользователь купил курс → CourseDetailSerializer (с уроками)
            - Если пользователь модератор → CourseDetailSerializer (с уроками)
            - Если пользователь владелец → CourseDetailSerializer (с уроками)
            - Иначе → CourseSerializer (без уроков)
        """
        # Для списка используем базовый сериализатор
        if self.action == 'list':
            return CourseSerializer

        # Для детального просмотра
        if self.action == 'retrieve':
            request = self.request
            course = self.get_object()  # текущий курс

            # Проверяем, есть ли доступ к полной версии
            has_full_access = self._has_full_access(request.user, course)

            if has_full_access:
                return CourseDetailSerializer

        return CourseSerializer

    def _has_full_access(self, user, course):
        """
        Проверяет, имеет ли пользователь доступ к полной версии курса.
        """
        # Неавторизованные не имеют доступа
        if not user or not user.is_authenticated:
            return False

        # Модераторы имеют доступ
        if user.groups.filter(name='Moderators').exists():
            return True

        # Владелец курса имеет доступ
        if course.owner == user:
            return True

        # Пользователь купил курс? (проверяем Payment)
        has_paid = Subscription.objects.filter(
            user=user,
            course=course
        ).exists()

        return has_paid

    def get_queryset(self):
        user = self.request.user

        # Модератор видит всё
        if user.groups.filter(name="Moderators").exists():
            return Course.objects.all()

        # Обычный пользователь — только свои курсы
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        course = serializer.save()
        course.owner = self.request.user
        course.save()

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
    permission_classes = [~IsModerator]  # Только обычные пользователи

    def perform_create(self, serializer):
        new_lesson = serializer.save()
        new_lesson.owner = self.request.user
        new_lesson.save()


class LessonListAPIView(generics.ListAPIView):
    """Получение списка всех уроков."""

    serializer_class = LessonSerializer

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

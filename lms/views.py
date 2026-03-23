from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from lms.models import Course, Lesson
from lms.serializers import (CourseDetailSerializer, CourseSerializer,
                             LessonSerializer)

from users.permissions import IsModerator, IsOwner

# Create your views here.


class CourseViewSet(ModelViewSet):
    """ViewSet-класс для курсов"""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

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

class CourseRetrieveAPIView(generics.RetrieveAPIView):
    """
    Получение детальной информации о курсе.
    Включает количество уроков и список всех уроков.
    """

    serializer_class = CourseDetailSerializer
    queryset = Course.objects.all()



class LessonCreateAPIView(generics.CreateAPIView):
    """Создание нового урока."""

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [~IsModerator]    # Только обычные пользователи

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

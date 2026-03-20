from rest_framework import generics, viewsets

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer

# Create your views here.


class CourseViewSet(viewsets.ModelViewSet):
    """ ViewSet для модели Course. Предоставляет полный набор CRUD операций"""
    serializer_class = CourseSerializer
    queryset = Course.objects.all()


class LessonCreateAPIView(generics.CreateAPIView):
    """Создание нового урока."""
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonListAPIView(generics.ListAPIView):
    """Получение списка всех уроков."""
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Получение детальной информации о конкретном уроке."""
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Обновление существующего урока."""
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()


class LessonDestroyAPIView(generics.DestroyAPIView):
    """ Удаление урока."""
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()

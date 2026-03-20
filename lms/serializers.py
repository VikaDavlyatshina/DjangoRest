from rest_framework import serializers

from lms.models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для модели Course.
    Используется для базового вывода информации о курсе.
    """

    class Meta:
        model = Course
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson.
    Используется для вывода информации об уроке.
    """

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детальной информации о курсе.
    Добавляет вычисляемое поле lessons_count с количеством уроков.
    """

    # Объявляем поле, значение которого будет вычисляться динамически
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ("id", "title", "description", "lessons_count", "lessons")

    def get_lessons_count(self, instance):
        """Возвращает количество уроков в курсе"""
        # instance - Текущий курс, курс, который сериализуем
        # instance.lessons - Все уроки этого курса
        # instance.lessons.count() - Вызываем метод count() для подсчёта количества

        return instance.lessons.count()

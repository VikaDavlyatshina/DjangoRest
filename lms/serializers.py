from rest_framework import serializers

from lms.models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для модели Course.
    Используется для базового вывода информации о курсе.
    """

    owner_email = serializers.EmailField(source='owner.email', read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "owner_email"]
        read_only_fields = ["id", "owner_email"]


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Lesson.
    Используется для вывода информации об уроке.
    """

    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Lesson
        fields = ["id", "title", "description", "link", "course", "course_title", "owner_email"]
        read_only_fields = ["id", "owner_email", "course_title"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')

        # Если пользователь не владелец и не модератор — скрываем email
        if request and request.user != instance.owner and not request.user.groups.filter(name='Moderators').exists():
            data.pop('owner_email', None)

        return data


class CourseDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детальной информации о курсе.
    Добавляет вычисляемое поле lessons_count с количеством уроков.
    """

    # Объявляем поле, значение которого будет вычисляться динамически
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "owner_email", "lessons_count", "lessons"]
        read_only_fields = ["id", "owner_email", "lessons_count", "lessons"]

    def get_lessons_count(self, instance):
        """Возвращает количество уроков в курсе"""
        # instance - Текущий курс, курс, который сериализуем
        # instance.lessons - Все уроки этого курса
        # instance.lessons.count() - Вызываем метод count() для подсчёта количества

        return instance.lessons.count()

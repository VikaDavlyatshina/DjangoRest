from django.db import models

# Create your models here.


class Course(models.Model):
    """Модель для Курса"""

    title = models.CharField(
        max_length=100,
        verbose_name="Название курса",
        help_text="Введите название курса",
    )
    preview = models.ImageField(
        upload_to="lms/course_photos",
        verbose_name="Превью курса",
        help_text="Добавьте фотографию для превью курса",
        blank=True, null=True,
    )
    description = models.TextField(
        verbose_name="Описание курса", help_text="Введите описание курса",
        blank=True, null=True,
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Модель для Урока"""

    title = models.CharField(
        max_length=100,
        verbose_name='Название урока',
        help_text='Введите название урока',
    )
    preview = models.ImageField(
        verbose_name='Превью урока', help_text='Добавьте фотографию для превью урока',
        upload_to='lms/lesson_photos',
        blank=True,  # можно не заполнять в формах
        null=True,  # можно хранить NULL в БД
    )
    description = models.TextField(
        verbose_name='Описание урока', help_text='Введите описание урока',
        blank=True, null=True,
    )
    link = models.URLField(
        verbose_name='Ссылка на видео урока', help_text='Укажите ссылку на видео урока',
        blank=True,   # если ссылка может быть необязательной
        null=True,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,  # При удалении курса, удалятся все уроки
        verbose_name='Курс',
        help_text='Введите название курса',
        related_name='lessons',  # Позволяет получать все уроки Курса: course.lessons.all()
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'

    def __str__(self):
        return self.title

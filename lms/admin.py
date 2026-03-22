from django.contrib import admin

from lms.models import Course, Lesson


# Register your models here.

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Настройка отображения курсов в админке.
    """

    # Поля, которые отображаются в списке
    list_display = ('id', 'title', 'owner', 'description')

    # Поля, по которым можно фильтровать
    list_filter = ('title', 'owner')

    # Поля, по которым можно искать
    search_fields = ('title', 'description')

    # Поля, которые можно редактировать прямо в списке
    list_editable = ('title',)

    # Сортировка по умолчанию
    ordering = ('-id',)  # минус означает по убыванию

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """
    Настройка отображения уроков в админке.
    """

    # Поля, которые отображаются в списке
    list_display = ('id', 'title', 'owner', 'description', 'link')

    # Поля, по которым можно фильтровать
    list_filter = ('title', 'owner')

    # Поля, по которым можно искать
    search_fields = ('title', 'description')

    # Поля, которые можно редактировать прямо в списке
    list_editable = ('title',)

    # Сортировка по умолчанию
    ordering = ('-id',)  # минус означает по убыванию
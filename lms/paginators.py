from rest_framework.pagination import PageNumberPagination


class CoursePagination(PageNumberPagination):
    """Пагинатор для курсов"""

    page_size = 10  # По умолчанию 10 элементов на странице
    page_size_query_param = "page_size"  # Параметр для изменения размера страницы
    max_page_size = 100  # Максимальный размер страницы


class LessonPagination(PageNumberPagination):
    """Пагинатор для уроков"""

    page_size = 10  # По умолчанию 10 элементов на странице
    page_size_query_param = "page_size"  # Параметр для изменения размера страницы
    max_page_size = 100  # Максимальный размер страницы

import re

from rest_framework.serializers import ValidationError


class YouTubeLinkValidator:
    """Валидатор для проверки, что ссылка ведёт на YouTube через HTTPS"""

    # Регулярка с VERBOSE — можно разбить на строки и добавить комментарии
    YOUTUBE_PATTERN = re.compile(
        r"""
        ^                       # начало строки
        https://                # протокол HTTPS
        (?:www\.)?              # опционально: www.
        (?:                     # группа без захвата для доменов
            youtube\.com        # вариант 1: youtube.com
            |                   # или
            youtu\.be           # вариант 2: youtu.be
        )
        /                       # обязательный слеш после домена
        .+                      # хотя бы один символ (ID видео)
        $                       # конец строки
    """,
        re.VERBOSE,
    )

    def __call__(self, value):
        # Пустую ссылку пропускаем (поле необязательное)
        if not value:
            return value

        # Проверяем непустую ссылку
        if not self.YOUTUBE_PATTERN.match(str(value)):
            raise ValidationError(
                "Разрешены только ссылки на YouTube (youtube.com или youtu.be). "
                "Пример: https://www.youtube.com/watch?v=abc123"
            )

        return value

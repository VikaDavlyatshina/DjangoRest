import re
from rest_framework.serializers import ValidationError


class YouTubeLinkValidator:
    """Валидатор для проверки, что ссылка ведёт на YouTube через HTTPS"""

    # Регулярка с VERBOSE — можно разбить на строки и добавить комментарии
    YOUTUBE_PATTERN = re.compile(r'''
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
    ''', re.VERBOSE)

    def __init__(self, field=None):
        self.field = field

    def __call__(self, value):
        # Если валидируем поле в объекте
        if self.field:
            url = value.get(self.field) if isinstance(value, dict) else value
        else:
            url = value

        # Пустую ссылку пропускаем
        if not url:
            return value

        # Проверяем непустую ссылку
        if not self.YOUTUBE_PATTERN.match(str(url)):
            raise ValidationError(
                "Ссылка должна вести на YouTube (youtube.com или youtu.be)"
            )

        return value
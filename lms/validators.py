import re
from rest_framework.serializers import ValidationError



class YouTubeLinkValidator:
    """Валидатор для проверки, что ссылка ведёт на YouTube через Https"""

    def __init__(self, field=None):
        self.field = field

    def __call__(self, value):
        if self.field:
            url = value.get(self.field)
        else:
            url = value

        # Регулярное выражение для проверки YouTube-ссылки
        # ^https://     - строка должна начинаться с https://
        # (www\.)?      - опциональная группа (www. может быть или нет)
        # (youtube\.com|youtu\.be) - домен YouTube
        # /             - обязательный слеш после домена
        youtube_regex = r'^https://(www\.)?(youtube\.com|youtu\.be)/'
        if not re.match(youtube_regex, str(url)):
            raise ValidationError("Ссылка должна вести на YouTube")
        return value
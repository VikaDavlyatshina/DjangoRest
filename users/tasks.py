from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from users.models import User


@shared_task
def block_inactive_users():
    """Блокирует пользователей, которые не активны более 30 дней"""
    thirty_days_ago = timezone.now() - timedelta(days=30)

    inactive_users = User.objects.filter(
        # только активные аккаунты
        is_active=True,
        # последний вход был ДО 30 дней назад
        last_login__lt=thirty_days_ago,
        # исключаем пользователей, которые никогда не входили
        last_login__isnull=False,
    )

    # Считаем кол-во пользователей
    count = inactive_users.count()
    inactive_users.update(is_active=False)

    return f"Заблокировано неактивных пользователей: {count} "

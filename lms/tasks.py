from datetime import timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from config import settings
from lms.models import Course
from users.models import Subscription


@shared_task
def should_notify_about_update(course):
    """Проверяет, прошло ли 4 часа после обновления"""

    if not course.updated_at:
        return True

    # Вычисляем, сколько времени прошло с последнего обновления
    time_since_update = timezone.now() - course.updated_at

    # Проверяем, прошло ли 4 часа
    return time_since_update >= timedelta(hours=4)


@shared_task
def send_course_update_notifications(course_id):
    """Отправляет рассылку об обновлении курса или урока."""

    try:
        # Находим курс
        course = Course.objects.get(id=course_id)

        if not should_notify_about_update(course):
            # Вычисляем, сколько времени прошло
            time_since = timezone.now() - course.updated_at
            hours_since = time_since.total_seconds() / 3600

            return f"Уведомление отложено (прошло {hours_since:.1f} часа(ов) с последнего обновления, нужно 4)"

        # Находим подписанных пользователей
        subscriptions = Subscription.objects.filter(course=course)

        # Если у курса нет подписчиков
        if not subscriptions.exists():
            print(f"У курса {course.title} нет подписчиков")

        # Отправляем письмо каждому подписчику
        for subscription in subscriptions:
            user = subscription.user
            # Вызываем отдельную задачу для отправки письма
            send_update_email_to_user.delay(
                user_email=user.email,
                course_title=course.title,
                course_id=course_id,
            )

        # Обновляем время после отправки
        course.updated_at = timezone.now()
        course.save(update_fields=['updated_at'])

        return f"Запущена отправка {subscriptions.count()} уведомлений о курсе {course.title}"

    except Course.DoesNotExist:
        print(f"Курс c ID {course_id} не найден")


@shared_task
def send_update_email_to_user(user_email, course_title, course_id):
    """Отправляет одно письмо одному пользователю"""

    try:
        # Создаём HTML письмо
        html_message = render_to_string(
            "emails/course_update_email.html",
            {
                "user_email": user_email,
                "course_title": course_title,
                "course_id": course_id,
            },
        )

        plain_message = strip_tags(html_message)

        send_mail(
            subject=f"Курс {course_title} был обновлён!",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return f"Письмо отправлено {user_email}"

    except Exception as e:
        return f"Ошибка при отправке письма {user_email}: {str(e)}"

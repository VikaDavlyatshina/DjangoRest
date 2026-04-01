from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from config import settings
from lms.models import Course
from users.models import Subscription


@shared_task
def send_course_update_notifications(course_id):
    """Отправляет рассылку об обновлении курса или урока"""

    try:
        # Находим курс
        course = Course.objects.get(id=course_id)

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
                user_name=user.get_full_name() or user.email,
                course_title=course.title,
                course_id=course_id,
            )
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

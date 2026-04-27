from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson
from users.models import Subscription, User

# Create your tests here.


class LessonTestCase(APITestCase):
    """Тесты для CRUD операций с уроками"""

    def setUp(self):
        """Подготовка данных перед каждым тестом. Выполняется автоматически"""

        # Создаём пользователей

        # Обычный пользователь
        self.user = User.objects.create(
            email="user@example.com",
            password="test123",
            first_name="Тест",
            last_name="Пользователь",
        )

        # Модератор
        self.moderator = User.objects.create(
            email="moderator@example.com",
            password="test123",
            first_name="Модератор",
        )
        # Добавляем модератора в группу
        moderator_group, created = Group.objects.get_or_create(name="Moderators")
        self.moderator.groups.add(moderator_group)

        # Создаём тестовый курс
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание тестового курса",
            owner=self.user,
        )

        # Создаём тестовый урок
        self.lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Описание тестового урока",
            link="https://www.youtube.com/watch?v=abc123",
            course=self.course,
            owner=self.user,
        )

    # ==================== ТЕСТЫ СОЗДАНИЯ ====================

    def test_create_lesson_unauthenticated(self):
        """
        Неавторизованный пользователь НЕ может создать урок.
        """

        url = "/api/lms/lessons/create/"
        data = {
            "title": "Новый урок",
            "link": "https://www.youtube.com/watch?v=xyz789",
            "course": self.course.id,
        }

        response = self.client.post(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Неавторизованный пользователь не должен создавать уроки",
        )

    def test_create_lesson_moderator(self):
        """Модератор не может создать урок."""

        # Авторизация
        self.client.force_authenticate(user=self.moderator)

        url = "/api/lms/lessons/create/"
        data = {
            "title": "Новый урок",
            "link": "https://www.youtube.com/watch?v=xyz789",
            "course": self.course.id,
        }

        response = self.client.post(url, data)

        # Проверяем статус
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Модератор не может создавать уроки",
        )

    def test_create_lesson_authenticated(self):
        """Авторизованный пользователь может создать урок."""

        # Авторизация
        self.client.force_authenticate(user=self.user)

        url = "/api/lms/lessons/create/"
        data = {
            "title": "Новый урок",
            "link": "https://www.youtube.com/watch?v=xyz789",
            "course": self.course.id,
        }

        response = self.client.post(url, data)

        # Проверяем статус
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Авторизованный пользователь должен создавать уроки",
        )

        # Проверяем, что урок добавился в БД
        self.assertEqual(
            Lesson.objects.count(), 2, "Количество уроков должно увеличиться на 1"
        )

        # Проверяем владельца через БД
        new_lesson = Lesson.objects.latest("id")
        self.assertEqual(new_lesson.owner, self.user)

    def test_create_lesson_invalid_url(self):
        """
        Нельзя создать урок с не-YouTube ссылкой.
        """

        self.client.force_authenticate(user=self.user)

        url = "/api/lms/lessons/create/"
        data = {
            "title": "Плохой урок",
            "link": "https://rutube.ru/video/456",
            "course": self.course.id,
        }

        response = self.client.post(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Не-YouTube ссылки должны отклоняться",
        )

        self.assertIn("link", response.data, "Ошибка должна быть в поле 'link'")

    # ==================== ТЕСТЫ ОБНОВЛЕНИЯ ====================

    def test_update_lesson_owner(self):
        """
        Владелец может обновить свой урок.
        """
        self.client.force_authenticate(user=self.user)

        url = f"/api/lms/lessons/{self.lesson.id}/update/"
        data = {"title": "Обновлённый урок"}

        response = self.client.patch(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Владелец должен обновлять свой урок",
        )

        # Обновляем объект из базы
        self.lesson.refresh_from_db()
        self.assertEqual(
            self.lesson.title, "Обновлённый урок", "Название урока должно измениться"
        )

    def test_update_lesson_not_owner(self):
        """
        Не-владелец не может обновить чужой урок.
        """
        # Создаём другого пользователя
        other_user = User.objects.create_user(
            email="other@example.com", password="test123"
        )
        self.client.force_authenticate(user=other_user)

        url = f"/api/lms/lessons/{self.lesson.id}/update/"
        data = {"title": "Попытка взлома"}

        response = self.client.patch(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Не-владелец не должен обновлять чужие уроки",
        )

        # ==================== ТЕСТЫ УДАЛЕНИЯ ====================

    def test_delete_lesson_owner(self):
        """
        Владелец может удалить свой урок.
        """
        self.client.force_authenticate(user=self.user)

        url = f"/api/lms/lessons/{self.lesson.id}/delete/"

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Владелец должен удалять свой урок",
        )

        self.assertEqual(Lesson.objects.count(), 0, "Урок должен быть удалён из базы")

    def test_delete_lesson_moderator(self):
        """
        Модератор не может удалить урок
        """

        self.client.force_authenticate(user=self.moderator)

        url = f"/api/lms/lessons/{self.lesson.id}/delete/"

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Модератор не должен удалять уроки",
        )


class SubscriptionTestCase(APITestCase):
    """
    Тесты для функционала подписки.

    Проверяет:
    - Подписку на курс
    - Отписку от курса
    - Признак подписки в курсе
    - Доступ неавторизованных
    """

    def setUp(self):
        """Подготовка данных"""

        self.user = User.objects.create_user(
            email="user@example.com", password="test123"
        )

        self.course = Course.objects.create(
            title="Тестовый курс", description="Для проверки подписки", owner=self.user
        )

    def test_subscribe_to_course(self):
        """
        Пользователь Может подписаться на курс.
        """
        self.client.force_authenticate(user=self.user)

        url = "/api/users/subscriptions/"
        data = {"course_id": self.course.id}

        response = self.client.post(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Подписка должна проходить успешно",
        )

        self.assertTrue(
            response.data["is_subscribed"], "Признак подписки должен быть True"
        )

        # Проверяем, что запись в БД создалась
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists(),
            "Запись подписки должна быть в базе данных",
        )

    def test_unsubscribe_from_course(self):
        """
        Пользователь Может отписаться от курса.
        """
        # Сначала подписываемся
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)

        url = "/api/users/subscriptions/"
        data = {"course_id": self.course.id}

        response = self.client.post(url, data)

        self.assertEqual(
            response.status_code, status.HTTP_200_OK, "Отписка должна проходить успешно"
        )

        self.assertFalse(
            response.data["is_subscribed"], "Признак подписки должен быть False"
        )

        # Проверяем, что запись удалилась
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists(),
            "Запись подписки должна быть удалена из базы",
        )

    def test_subscribe_unauthenticated(self):
        """
        Неавторизованный пользователь не может подписаться.
        """
        url = "/api/users/subscriptions/"
        data = {"course_id": self.course.id}

        response = self.client.post(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Неавторизованный пользователь не должен подписываться",
        )

    def test_subscribe_invalid_course(self):
        """
        Подписка на несуществующий курс.
        """
        self.client.force_authenticate(user=self.user)

        url = "/api/users/subscriptions/"
        data = {"course_id": 99999}  # Несуществующий ID

        response = self.client.post(url, data)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Несуществующий курс должен возвращать 404",
        )

    def test_course_has_subscription_flag(self):
        """При подписке признак is_subscribed отображается в ответе."""

        self.client.force_authenticate(user=self.user)

        url = "/api/users/subscriptions/"
        data = {"course_id": self.course.id}

        # Подписываемся
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_subscribed"])

        # Проверяем, что в списке подписок is_subscribed = True
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Находим курс в списке
        for item in response.data.get("results", []):
            if item.get("id") == self.course.id:
                self.assertTrue(item.get("is_subscribed"))
                break

        # Отписываемся
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_subscribed"])

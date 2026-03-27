from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course
from users.models import Payments, Subscription, User
from users.permissions import IsSelfOrReadOnly
from users.serializers import (PaymentCreateSerializer, PaymentSerializer,
                               SubscriptionSerializer, UserCreateSerializer,
                               UserSerializer)


class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя (доступна всем)"""

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    # Разрешаем регистрацию всем
    permission_classes = [permissions.AllowAny]


class UserListView(generics.ListAPIView):
    """Список всех пользователей (только чтение)"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    Просмотр, редактирование и удаление профиля пользователя.

    GET /users/<id>/     - просмотр (любой авторизованный)
    PUT /users/<id>/     - полное обновление (только владелец)
    PATCH /users/<id>/   - частичное обновление (только владелец)
    DELETE /users/<id>/  - удаление (владелец или администратор)
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelfOrReadOnly]


class PaymentCreateAPIView(generics.CreateAPIView):
    """Создание платежа"""

    serializer_class = PaymentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PaymentListView(generics.ListAPIView):
    """
    Эндпоинт для получения списка платежей с возможностью фильтрации и сортировки.
    """

    # Оптимизация: подгружаем связанные данные одним запросом
    queryset = Payments.objects.select_related(
        "user", "paid_course", "paid_lesson"
    ).all()

    # Сериализатор для преобразования объектов в JSON
    serializer_class = PaymentSerializer

    # Бэкенды для фильтрации и сортировки
    filter_backends = [
        DjangoFilterBackend,  # Позволяет фильтровать через ?поле=значение
        filters.OrderingFilter,
    ]  # Позволяет сортировать через ?ordering=поле
    filterset_fields = [
        "paid_course",  # ID курса
        "paid_lesson",  # ID курса
        "payment_method",  # Способ оплаты ('cash' или 'transfer')
    ]

    # Поля, по которым можно сортировать (По дате и по сумме)
    ordering_fields = ["payment_date", "payment_amount"]

    # Сортировка по умолчанию (новые платежи первыми)
    ordering = ["-payment_date"]

    def get_queryset(self):
        user = self.request.user

        queryset = Payments.objects.select_related("user", "paid_course", "paid_lesson")

        # Админ видит всё
        if user.is_superuser:
            return queryset

        # Обычный пользователь — только свои платежи
        return queryset.filter(user=user)


class SubscriptionAPIView(APIView):
    """
    Эндпоинт для управления подпиской
    GET: получить список подписок пользователя
    POST: подписаться/отписаться от курса
    """

    def get(self, request):
        """
        Обработка GET-запроса.
        """

        # Получаем пользователя
        user = request.user

        # 2) Получаем id курса из данных запроса
        subscriptions = Subscription.objects.filter(user=user).select_related("course")

        # Сериализируем и возвращаем
        serializer = SubscriptionSerializer(subscriptions, many=True)

        return Response(
            {
                "count": subscriptions.count(),
                "subscriptions": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request, *args, **kwargs):
        """
        Обработка POST-запроса.
        Подписаться или отписаться от курса
        """

        # 1) Получаем пользователя
        user = request.user

        # Получаем id курса из данных запроса
        course_id = request.data.get("course_id")

        # Проверяем, что ID передан
        if not course_id:
            return Response({"error": "Не указан ID курса"}, status=400)

        # Получаем объект курса из базы (или 404)
        course = get_object_or_404(Course, id=course_id)

        #  Получаем объекты подписок по текущему пользователю и курса
        subscription = Subscription.objects.filter(user=user, course=course)

        # Если подписка у пользователя на этот курс есть - удаляем ее
        if subscription.exists():
            subscription.delete()
            message = f"Ваша подписка на курс {course.title} удалена"
            is_subscribed = False

        # Если подписки у пользователя на этот курс нет - создаем ее
        else:
            Subscription.objects.create(user=user, course=course)
            message = f"Подписка на курс {course.title} успешно добавлена"
            is_subscribed = True

        return Response(
            {
                "message": message,
                "is_subscribed": is_subscribed,
                "course_id": course.id,
                "course_title": course.title,
            },
            status=status.HTTP_200_OK,
        )

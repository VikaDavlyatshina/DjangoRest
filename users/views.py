from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from rest_framework import filters, generics, permissions, status, serializers
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from config import settings
from lms.models import Course
from users.models import Payments, Subscription, User
from users.permissions import IsSelfOrReadOnly
from users.serializers import (PaymentCreateSerializer, PaymentSerializer,
                               SubscriptionSerializer, UserCreateSerializer,
                               UserSerializer)
from users.services import create_stripe_product, create_stripe_price, create_stripe_session



@extend_schema_view(
    post=extend_schema(
        summary="Регистрация пользователя. Доступна всем",
        description="Создаёт нового пользователя",
        request=UserCreateSerializer,
        responses={201: UserCreateSerializer, 400: None},
        tags=["users"],
    )
)
class UserCreateAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя (доступна всем)"""

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    # Разрешаем регистрацию всем
    permission_classes = [permissions.AllowAny]


@extend_schema_view(
    get=extend_schema(
        summary="Список пользователей",
        description="Возвращает список всех пользователей. Доступно только авторизованным",
        request=UserCreateSerializer,
        responses={200: UserSerializer(many=True)},
        tags=["users"],
    )
)
class UserListView(generics.ListAPIView):
    """Список всех пользователей (только чтение)"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


@extend_schema_view(
    get=extend_schema(
        summary="Профиль пользователя",
        description="Возвращает информацию о пользователе. Свой профиль — полная информация, чужой — ограниченная.",
        responses={200: UserSerializer},
        tags=['users'],
    ),
    put=extend_schema(
        summary="Полное обновление профиля",
        description="Обновляет профиль пользователя. Доступно только владельцу.",
        request=UserSerializer,
        responses={200: UserSerializer},
        tags=['users'],
    ),
    patch=extend_schema(
        summary="Частичное обновление профиля",
        description="Частично обновляет профиль пользователя. Доступно только владельцу.",
        request=UserSerializer,
        responses={200: UserSerializer},
        tags=['users'],
    ),
    delete=extend_schema(
        summary="Удаление профиля",
        description="Удаляет профиль пользователя. Доступно владельцу или администратору.",
        responses={204: None},
        tags=['users'],
    ),
)
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
    """Создание платежа с интеграцией Stripe."""

    serializer_class = PaymentCreateSerializer
    queryset = Payments.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Создание платежа",
        description="Создаёт платёж в Stripe и возвращает ссылку на оплату.",
        request=PaymentCreateSerializer,
        responses={201: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        payment = serializer.save(user=self.request.user)

        if not payment.paid_course:
            raise serializers.ValidationError("Можно оплатить только курс")

        if payment.paid_course.price <= 0:
            raise serializers.ValidationError("Цена курса должна быть больше нуля")

        try:
            product = create_stripe_product(payment.paid_course.title)
            price = create_stripe_price(product.id, payment.paid_course.price)
            session = create_stripe_session(
                price.id,
                f"{settings.STRIPE_SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}",
                settings.STRIPE_CANCEL_URL
            )

            payment.stripe_session_id = session.id
            payment.payment_url = session.url
            payment.save()

            self.payment_url = session.url

        except Exception as e:
            raise serializers.ValidationError(f"Ошибка Stripe: {str(e)}")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response({
            'payment_id': serializer.instance.id,
            'payment_url': self.payment_url,
            'message': 'Перейдите по ссылке для оплаты'
        }, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        summary="Список платежей",
        description="Возвращает список платежей пользователя. Администратор видит все платежи.",
        parameters=[
            OpenApiParameter(name='paid_course', description='ID курса', required=False, type=int),
            OpenApiParameter(name='paid_lesson', description='ID урока', required=False, type=int),
            OpenApiParameter(name='payment_method', description='Способ оплаты (cash/transfer/card)', required=False, type=str),
            OpenApiParameter(name='ordering', description='Сортировка (payment_date, -payment_date, payment_amount)', required=False, type=str),
        ],
        responses={200: PaymentSerializer(many=True)},
        tags=['payments'],
    )
)
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
    """ Эндпоинт для управления подписками """

    @extend_schema(
        summary="Список подписок",
        description="Возвращает список курсов, на которые подписан пользователь",
        responses={200: SubscriptionSerializer(many=True)},
    )
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

    @extend_schema(
        summary="Управление подпиской",
        description="Подписаться или отписаться от курса",
        request=OpenApiTypes.OBJECT,
        responses={200: OpenApiTypes.OBJECT},
    )
    def post(self, request):
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

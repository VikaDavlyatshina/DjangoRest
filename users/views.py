from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions

from users.models import Payments, User
from users.serializers import PaymentSerializer, UserSerializer, UserCreateSerializer


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


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля пользователя"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


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

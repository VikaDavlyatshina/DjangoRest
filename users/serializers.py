from django.db import models
from rest_framework import serializers

from lms.models import Course, Lesson
from users.models import Payments, User


class UserShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода частичной информации о пользователе.
    Используется как вложенный для платежей.
    """

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]


class CourseShortSerializer(serializers.ModelSerializer):
    """Краткая информация о курсе для платежей"""

    class Meta:
        model = Course
        fields = ["id", "title", "description"]


class LessonShortSerializer(serializers.ModelSerializer):
    """Краткая информация о курсе для платежей"""

    class Meta:
        model = Lesson
        fields = ["id", "title", "description"]


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для платежей.
    Использует краткие сериализаторы для связанных объектов.
    """

    # Вместо ID — краткая информация
    user = UserShortSerializer(read_only=True)
    paid_course = CourseShortSerializer(read_only=True)
    paid_lesson = LessonShortSerializer(read_only=True)

    # Вычисляемое поле для красивого отображения способа оплаты
    payment_method_display = serializers.CharField(
        source="get_payment_method_display", read_only=True
    )

    class Meta:
        model = Payments
        fields = [
            "id",
            "user",  # краткая информация о пользователе
            "payment_date",
            "paid_course",  # краткая информация о курсе
            "paid_lesson",  # краткая информация об уроке
            "payment_amount",
            "payment_method",
            "payment_method_display",
        ]


class UserPaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для платежей в профиле пользователя.
    Используется в UserSerializer для истории платежей.
    """

    paid_course = CourseShortSerializer(read_only=True)
    paid_lesson = LessonShortSerializer(read_only=True)

    payment_method_display = serializers.CharField(
        source="get_payment_method_display", read_only=True
    )

    class Meta:
        model = Payments
        fields = [
            "id",
            "payment_date",
            "paid_course",
            "paid_lesson",
            "payment_amount",
            "payment_method",
            "payment_method_display",
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания нового пользователя"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "phone", "city", "avatar", "password"]

        read_only_fields = ["id"]

    def validate_email(self, value):
        """Проверяем, что email не занят"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует"
            )
        return value

    def create(self, validated_data):
        """
        Создаёт пользователя с хэшированным паролем.
        """

        # Забираем пароль и email из словаря
        password = validated_data.pop("password")
        email = validated_data.pop("email")

        # Создаем пользователя
        user = User.objects.create_user(
            email=email,
            password=password,
            **validated_data,  # first_name, last_name, phone, city и т.д.
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода полной информации о пользователе.
    Включает историю платежей.
    """

    # История платежей
    payments = UserPaymentSerializer(many=True, read_only=True)
    # Общая сумма потраченных средств
    total_spent = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "city",
            "avatar",
            "first_name",
            "last_name",
            "payments",
            "total_spent",
        ]
        read_only_fields = ["id", "email"]  # email нельзя менять

    def get_total_spent(self, instance):
        """Вычисляет общую сумму всех платежей пользователя"""

        total = instance.payments.aggregate(total=models.Sum("payment_amount"))["total"]
        return total or 0

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")

        # Если это чужой профиль — скрываем историю платежей и total_spent
        if request and request.user != instance:
            data.pop("payments", None)
            data.pop("total_spent", None)
            data.pop("last_name", None)

        return data

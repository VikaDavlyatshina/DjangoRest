from django.db import models
from rest_framework import serializers

from lms.models import Course, Lesson
from users.models import User, Payments


class UserShortSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода частичной информации о пользователе.
    Используется как вложенный для платежей.
    """

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']

class CourseShortSerializer(serializers.ModelSerializer):
    """Краткая информация о курсе для платежей"""

    class Meta:
        model = Course
        fields = ['id', 'title', 'description']


class LessonShortSerializer(serializers.ModelSerializer):
    """Краткая информация о курсе для платежей"""

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description']

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
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Payments
        fields = [
            'id',
            'user',                     # краткая информация о пользователе
            'payment_date',
            'paid_course',              # краткая информация о курсе
            'paid_lesson',              # краткая информация об уроке
            'payment_amount',
            'payment_method',
            'payment_method_display'
        ]


class UserPaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для платежей в профиле пользователя.
    Используется в UserSerializer для истории платежей.
    """

    paid_course = CourseShortSerializer(read_only=True)
    paid_lesson = LessonShortSerializer(read_only=True)

    payment_method_display = serializers.CharField(
        source='get_payment_method_display',
        read_only=True
    )

    class Meta:
        model = Payments
        fields = [
            'id',
            'payment_date',
            'paid_course',
            'paid_lesson',
            'payment_amount',
            'payment_method',
            'payment_method_display'
        ]


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
        fields = ['id', 'email', 'phone', 'city', 'avatar', 'first_name', 'last_name', 'payments', 'total_spent']
        read_only_fields = ['id', 'email']  # email нельзя менять

    def get_total_spent(self, instance):
        """Вычисляет общую сумму всех платежей пользователя"""

        total = instance.payments.aggregate(total=models.Sum('payment_amount'))['total']
        return total or 0
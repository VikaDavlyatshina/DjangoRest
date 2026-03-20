from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.


class User(AbstractUser):
    user_name = None

    email = models.EmailField(
        unique=True, verbose_name='Email', help_text='Укажите email'
    )
    phone = PhoneNumberField(
        blank=True,
        null=True,
        verbose_name='Телефон',
        help_text='Введите номер телефона',
    )
    city = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Город',
        help_text='Введите город проживания',
    )
    avatar = models.ImageField(
        upload_to='users/avatars',
        blank=True,
        null=True,
        verbose_name='Фото профиля',
        help_text='Загрузите фото профиля',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Payments(models.Model):
    """
    Модель Платежи
    Поля:
    1. Пользователь
    2. Дата оплаты
    3. Оплаченный курс или урок (Два поля - одно для курса, другое для урока)
    4. Сумма оплаты
    5. Способ оплаты - наличие или перевод на счет
    """

    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='payments')
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата оплаты')
    paid_course= models.ForeignKey('lms.Course', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Оплаченный курс', related_name='payments')
    paid_lesson = models.ForeignKey('lms.Lesson', on_delete=models.SET_NULL, blank=True, null=True,
                                    verbose_name='Оплаченный урок', related_name='payments')
    payment_amount = models.PositiveIntegerField(verbose_name='Сумма оплаты', help_text='Сумма в рублях')
    payment_method =models.CharField(max_length=10, choices=PAYMENT_METHODS,default='cash', verbose_name='Способ оплаты')

    class Meta:
        verbose_name= 'Платёж'
        verbose_name_plural= 'Платежи'
        ordering = ('-payment_date',)

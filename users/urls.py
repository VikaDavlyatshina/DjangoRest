from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from users.apps import UsersConfig
from users.views import (PaymentCreateAPIView, PaymentListView,
                         UserCreateAPIView, UserListView, UserProfileView, SubscriptionAPIView)

app_name = UsersConfig.name

urlpatterns = [
    # Пользователи
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserProfileView.as_view(), name="user-profile"),
    path("register/", UserCreateAPIView.as_view(), name="register"),

    # Платежи
    path("payments/", PaymentListView.as_view(), name="payment-list"),
    path("payments/create/", PaymentCreateAPIView.as_view(), name="payment-create"),

    # Подписки (на курсы)
    path("courses/subscribe/", SubscriptionAPIView.as_view(), name="subscribe"),

    # Авторизация
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
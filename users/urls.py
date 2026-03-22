from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

from users.apps import UsersConfig
from users.views import PaymentListView, UserListView, UserProfileView, UserCreateAPIView

app_name = UsersConfig.name

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserProfileView.as_view(), name="user-profile"),
    path("payments/", PaymentListView.as_view(), name="payment-list"),

    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

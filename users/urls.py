from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

from users.views import PaymentListView, UserListView, UserProfileView

app_name = "users"

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserProfileView.as_view(), name="user-profile"),
    path("payments/", PaymentListView.as_view(), name="payment-list"),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

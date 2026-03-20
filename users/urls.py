from django.urls import path

from users.views import UserProfileView, PaymentListView, UserListView

app_name = "users"

urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("<int:pk>/", UserProfileView.as_view(), name="user-profile"),
    path("payments/", PaymentListView.as_view(), name="payment-list"),
]

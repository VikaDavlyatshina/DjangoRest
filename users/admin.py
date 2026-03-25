from django.contrib import admin

from .models import Payments, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "display_groups", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email",)

    def display_groups(self, obj):
        """Показывает группы пользователя"""
        return ", ".join([group.name for group in obj.groups.all()])

    display_groups.short_description = "Группы"


@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = ("user", "payment_date", "payment_amount", "payment_method")
    list_filter = ("payment_method",)
    search_fields = ("user__email",)

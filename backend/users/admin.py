from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscription

User = get_user_model()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    empty_value_display = settings.EMPTY_VALUE
    verbose_name = 'Подписка'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'email', 'username', 'first_name', 'last_name')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    empty_value_display = settings.EMPTY_VALUE
    verbose_name = 'Пользователь'

    fieldsets = (
        ('Персональная информация', {'fields': (
            'email', 'username', 'first_name', 'last_name', 'password'
        )}),
        ('Разрешения', {'fields': (
            'is_active', 'is_staff', 'is_superuser',
            'groups', 'user_permissions'
        )}),
        ('Важные даты/история', {'fields': ('last_login', 'date_joined')}),
    )

    ordering = ('-date_joined',)

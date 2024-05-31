from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from accounts.models import *


# class CustomUserAdmin(admin.ModelAdmin):

#     list_display = ('phone', 'username', )
#     search_fields = ('phone', 'username',)
#     ordering = ('phone',)

# admin.site.register(CustomUser, CustomUserAdmin)


# @admin.register(Profile)
# class ProfileAdmin(admin.ModelAdmin):
#     list_display = [field.name for field in Profile._meta.fields]
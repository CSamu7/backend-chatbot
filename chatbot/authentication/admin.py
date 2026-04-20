from django.contrib import admin
from rest_framework.authtoken.admin import TokenAdmin
from rest_framework.authtoken.models import Token
from .models import User

class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', 'username')

class CustomTokenAdmin(TokenAdmin):
    search_fields = ('user__username', 'key')
    autocomplete_fields = ['user']

admin.site.register(User, UserAdmin)

try:
    admin.site.unregister(Token)
except admin.sites.NotRegistered:
    pass
admin.site.register(Token, CustomTokenAdmin)
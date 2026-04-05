#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentication.models import User

# Crear usuario de prueba
user, created = User.objects.get_or_create(
    email='test@example.com',
    defaults={
        'username': 'testuser',
        'password': 'password123'
    }
)

if created:
    print(f"✅ Usuario creado: {user.email}")
else:
    print(f"ℹ️  Usuario ya existe: {user.email}")

# Mostrar todos los usuarios
print(f"\nTotal usuarios: {User.objects.count()}")
for u in User.objects.all():
    print(f"- {u.email} ({u.username})")

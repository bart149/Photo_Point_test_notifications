import os
import sys
import django

# Абсолютный путь до корня проекта (на уровень выше)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Добавляем в PYTHONPATH
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "notification_photo_point.settings")
django.setup()


from django.contrib.auth.models import User
from notifications.models import Notification

test_users = [
    {"username": "user1", "password": "123"},
    {"username": "user2", "password": "123"},
    {"username": "user3", "password": "123"},
]

for u in test_users:
    user, created = User.objects.get_or_create(username=u["username"])
    if created:
        user.set_password(u["password"])
        user.save()
        print(f"Создан пользователь: {user.username}")
    else:
        print(f"Пользователь уже существует: {user.username}")

notification = Notification.objects.create(message="Тестовое уведомление")
users = User.objects.filter(username__in=[u["username"] for u in test_users])
notification.users.set(users)
notification.save()

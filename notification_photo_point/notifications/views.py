from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Notification
from django.contrib.auth.models import User

# Страница с формой
def send_notification_page(request):
    users = User.objects.all()
    return render(request, 'notifications/send.html', {'users': users})

# Функции для отправки уведомлений
def send_email(user, message):
    print(f"Email отправлен пользователю {user.username}: {message}")
    return True

def send_sms(user, message):
    print(f"SMS сообщение отправлено пользователю {user.username}: {message}")
    return True

def send_telegram(user, message):
    print(f"Сообщение в Telegram отправлено пользователю {user.username}: {message}")
    return True

def send_with_fallback(user, message, chosen_channel):
    """
    Отправляет уведомление пользователю через выбранный способ отправки (канал).
    Если выбранный канал не срабатывает (возникает исключение или False),
    функция пробует остальные каналы в порядке ['main', 'alt1', 'alt2'].
    Возвращает канал, через который удалось отправить сообщение, или None, если все попытки неудачны.
    """
    channels = ['main', 'alt1', 'alt2']
    channel_funcs = {'main': send_email, 'alt1': send_sms, 'alt2': send_telegram}

    # Начинаем с выбранного канала
    try_order = [chosen_channel] + [c for c in channels if c != chosen_channel]

    for ch in try_order:
        try:
            if channel_funcs[ch](user, message): # Если вернулось True (успешная отправка)
                return ch
        except Exception:
            continue
    return None

@csrf_exempt
def send_notification_ajax(request):
    """
    AJAX-представление для отправки уведомлений выбранным способом.
    Проверяет данные запроса, создает уведомление в базе, 
    и отправляет сообщение выбранным каналом с возможностью 
    переключения на другие каналы, если основной способ не сработал.
    Возвращает JSON с результатом отправки.
    """
    # Проверяем, что метод запроса POST, иначе возвращаем ошибку
    if request.method != 'POST':
        return JsonResponse({'status': 'Метод не разрешен'}, status=405)

    # Загружаем данные из JSON тела запроса
    data = json.loads(request.body)
    user_ids = data.get('users', [])            # Список выбранных пользователей
    message = data.get('message', '').strip()   # Текст уведомления, без лишних пробелов
    chosen_channel = data.get('channel')        # Выбранный пользователем канал отправки

    # Валидация входных данных
    if not message:
        return JsonResponse({'status': 'Пожалуйста, введите текст уведомления!'}, status=400)
    if not user_ids:
        return JsonResponse({'status': 'Пожалуйста выберите пользователя!'}, status=400)
    if chosen_channel not in ['main', 'alt1', 'alt2']:
        return JsonResponse({'status': 'Пожалуйста выберите способ отправки!'}, status=400)

    # Создаём запись уведомления в базе данных
    notification = Notification.objects.create(message=message)
    users = User.objects.filter(id__in=user_ids)
    notification.users.set(users)
    notification.save()

    # Списки для хранения успешных и неудачных отправок
    success_users, failed_users = [], []

    # Отправляем уведомления каждому пользователю с возможностью изменения способа отправки
    for user in users:
        sent_channel = send_with_fallback(user, message, chosen_channel)  # функция пытается отправить через выбранный канал и альтернативные при ошибке
        if sent_channel:
            success_users.append(user.username)  # если успешно, добавляем в список успешных
        else:
            failed_users.append(user.username)   # если ни один канал не сработал, добавляем в список неудачных

    # Формируем текст статуса для ответа
    if failed_users:
        status_text = f"Отправлено: {', '.join(success_users)}. Не удалось: {', '.join(failed_users)}."
    else:
        status_text = f"Все уведомления успешно отправлены: {', '.join(success_users)}."

    # Возвращаем JSON с результатом
    return JsonResponse({'status': status_text})

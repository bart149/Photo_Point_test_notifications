from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('send/', views.send_notification_page, name='send_page'),  # для HTML
    path('send_ajax/', views.send_notification_ajax, name='send_ajax'),  # для AJAX
]
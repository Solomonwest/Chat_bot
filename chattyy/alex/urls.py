from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('send-message/', views.send_message, name='send_message'),
]
"""ai_assistant URL patterns."""
from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    path('', views.chat_home, name='chat'),
    path('ask/', views.ask_ai, name='ask_ai'),
    path('history/', views.conversation_history, name='history'),
]

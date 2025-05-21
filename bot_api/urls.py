from django.urls import path
from . import views

urlpatterns = [
    path('telegram/validate/', views.telegram_validate, name='telegram_validate'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('verify/email/<uidb64>/<token>/', views.email_verify_view, name='email_verify'),
    path('verify/email/sent/', views.verify_email_sent, name='verify_email_sent'),
]

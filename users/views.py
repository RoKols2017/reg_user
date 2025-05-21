# users/views.py
import os
from dotenv import load_dotenv
import qrcode
import io
import base64
import secrets

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import CustomUserRegistrationForm

load_dotenv()

def register_view(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # 🔐 Блокируем вход до подтверждения
            user.save()
            send_email_verification(user, request)
            return redirect('verify_email_sent')  # ⬅️ изменён редирект
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})


def send_email_verification(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    verify_url = request.build_absolute_uri(
        reverse('email_verify', kwargs={'uidb64': uid, 'token': token})
    )

    send_mail(
        subject="Подтверждение Email",
        message=f"Подтвердите почту: {verify_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )

def verify_email_sent(request):
    return render(request, 'users/verify_email_sent.html')

def email_verify_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        return HttpResponse("Ошибка UID")

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)  # Авторизация
        return redirect('profile')  # Или куда тебе удобно

    return HttpResponse("⛔ Неверный или просроченный токен")

@login_required
def telegram_verification_qr(request):
    user_profile = request.user.profile
    token = secrets.token_urlsafe(32)
    user_profile.telegram_verification_token = token
    user_profile.save()

    bot_username = os.getenv('BOT_USERNAME')
    deeplink = f"https://t.me/{bot_username}?start={token}"

    # Генерируем QR и преобразуем в base64 для встраивания в html
    img = qrcode.make(deeplink)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    qr_url = f"data:image/png;base64,{qr_base64}"

    return render(request, "users/telegram_qr.html", {
        "qr_url": qr_url,
        "deeplink": deeplink
    })

@login_required
def profile_view(request):
    return render(request, 'users/profile.html')
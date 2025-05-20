# users/views.py
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import CustomUserRegistrationForm

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
        return render(request, 'users/verify_email_success.html')

    return HttpResponse("⛔ Неверный или просроченный токен")

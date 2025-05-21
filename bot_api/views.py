from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from users.models import UserProfile
from django.utils import timezone

@csrf_exempt  # чтобы бот мог обращаться без CSRF-токена
def telegram_validate(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            token = data.get("token")
            telegram_id = data.get("telegram_id")
            telegram_username = data.get("telegram_username")
        except Exception:
            return HttpResponse("Invalid JSON", status=400)

        try:
            profile = UserProfile.objects.get(telegram_verification_token=token)
        except UserProfile.DoesNotExist:
            return HttpResponse("Invalid or expired token", status=400)

        # Валидация успешна
        profile.telegram_chat_id = telegram_id
        profile.telegram_username = telegram_username
        profile.is_telegram_verified = True
        profile.telegram_verified_at = timezone.now()
        profile.telegram_verification_token = None  # чтобы нельзя было повторно использовать
        profile.save()

        return HttpResponse("OK")
    return HttpResponse("Method not allowed", status=405)

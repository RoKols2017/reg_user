from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('api/', include('bot_api.urls')),  # например, http://localhost:8000/api/telegram/validate/
]

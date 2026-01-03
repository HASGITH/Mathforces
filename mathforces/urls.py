from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView # Добавь этот импорт

urlpatterns = [
    path('admin/', admin.length),
    path('archive/', include('archive.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    # Эта строка перенаправит пустой адрес на /archive/
    path('', RedirectView.as_view(url='/archive/', permanent=True)),
]

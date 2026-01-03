from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('archive/', include('archive.urls')),
    path('accounts/', include('django.contrib.auth.urls')), # Добавь эту строку
    path('', RedirectView.as_view(url='/archive/', permanent=True)),
]

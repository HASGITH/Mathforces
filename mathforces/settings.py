"""
Django settings for mathforces project.
"""

import os
from pathlib import Path

# Путь к папке проекта
BASE_DIR = Path(__file__).resolve().parent.parent


# --- НАСТРОЙКИ БЕЗОПАСНОСТИ ---

# SECURITY WARNING: keep the secret key used in production secret!
# Используем переменную окружения для сервера, или стандартный ключ для разработки
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-)vxi()jbduxmclto546*#!c62%pr0s8*(_l7po1pj9d1l7-8gd')

# SECURITY WARNING: don't run with debug turned on in production!
# Включаем DEBUG только если переменная окружения DJANGO_DEBUG=True (по умолчанию для разработки)
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'

# Список разрешенных хостов (адресов сайта)
ALLOWED_HOSTS = ['*'] # Для деплоя на PythonAnywhere или Render можно оставить так или вписать домен


# --- ОПРЕДЕЛЕНИЕ ПРИЛОЖЕНИЙ ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'archive', # Твое основное приложение
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mathforces.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # Можно добавить [BASE_DIR / 'templates'], если есть общие шаблоны
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mathforces.wsgi.application'


# --- БАЗА ДАННЫХ ---

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# --- ВАЛИДАЦИЯ ПАРОЛЕЙ ---

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- ЯЗЫК И ВРЕМЯ ---

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Baku'  # Твой часовой пояс
USE_I18N = True
USE_TZ = False # Упрощаем работу со временем для локальной разработки


# --- СТАТИЧЕСКИЕ ФАЙЛЫ (CSS, JavaScript, Images) ---

STATIC_URL = 'static/'

# Папка, куда Django соберет все статические файлы для сервера при команде collectstatic
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Дополнительные папки со статикой (если есть)
# STATICFILES_DIRS = [BASE_DIR / "static"]


# --- ПЕРЕНАПРАВЛЕНИЯ ПРИ ВХОДЕ/ВЫХОДЕ ---

LOGIN_REDIRECT_URL = '/archive/'
LOGOUT_REDIRECT_URL = '/archive/'

# По умолчанию использовать AutoField для ID моделей
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
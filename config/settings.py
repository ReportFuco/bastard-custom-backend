import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent


def load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_dotenv(BASE_DIR / ".env")


def get_env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)


def get_bool_env(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_list_env(name: str, default: list[str]) -> list[str]:
    value = os.environ.get(name)
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


DEBUG = get_bool_env("DJANGO_DEBUG", default=True)
SECRET_KEY = get_env("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-change-me"
    else:
        raise ImproperlyConfigured("DJANGO_SECRET_KEY is required when DJANGO_DEBUG is False")

ALLOWED_HOSTS = get_list_env(
    "DJANGO_ALLOWED_HOSTS",
    ["localhost", "127.0.0.1"],
)

CSRF_TRUSTED_ORIGINS = get_list_env(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    ["https://*.ngrok-free.app"],
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "users",
    "products",
    "cart",
    "orders",
    "inventory",
    "promotions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DB_ENGINE = get_env("DB_ENGINE", "sqlite").lower()

if DB_ENGINE == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": get_env("POSTGRES_DB", "tienda_online"),
            "USER": get_env("POSTGRES_USER", "tienda_online"),
            "PASSWORD": get_env("POSTGRES_PASSWORD", "tienda_online"),
            "HOST": get_env("POSTGRES_HOST", "db"),
            "PORT": get_env("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / get_env("SQLITE_NAME", "db.sqlite3"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = get_env("DJANGO_LANGUAGE_CODE", "es-cl")
TIME_ZONE = get_env("DJANGO_TIME_ZONE", "America/Santiago")
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

SECURE_SSL_REDIRECT = get_bool_env("DJANGO_SECURE_SSL_REDIRECT", default=not DEBUG)
SESSION_COOKIE_SECURE = get_bool_env("DJANGO_SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = get_bool_env("DJANGO_CSRF_COOKIE_SECURE", default=not DEBUG)
SECURE_HSTS_SECONDS = int(get_env("DJANGO_SECURE_HSTS_SECONDS", "0" if DEBUG else "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = get_bool_env("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=not DEBUG)
SECURE_HSTS_PRELOAD = get_bool_env("DJANGO_SECURE_HSTS_PRELOAD", default=not DEBUG)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": get_env("DRF_THROTTLE_ANON", "60/min"),
        "user": get_env("DRF_THROTTLE_USER", "200/min"),
    },
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

AUTH_USER_MODEL = "users.User"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

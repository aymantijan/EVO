import os
import dj_database_url
import math
from pathlib import Path
from datetime import timedelta
from decouple import config
import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

# Charge .env
load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, '.env'))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-your-secret-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'cloudinary_storage',
    'cloudinary',

    # Third-party apps
    'rest_framework',
    'corsheaders',
    'django_filters',
    'django_extensions',

    # Local apps
    'gamification.apps.GamificationConfig',
    'users.apps.UsersConfig',
    'actions.apps.ActionsConfig',
    'study_tracker.apps.StudyTrackerConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'gamification_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'gamification_config.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Casablanca'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# JWT configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JTI_CLAIM': 'jti',
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS configuration
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000',
    cast=lambda v: [s.strip() for s in v.split(',')]
)

CORS_ALLOW_CREDENTIALS = True

# CSRF Configuration
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://evpe.up.railway.app',
    'https://*.railway.app',
]
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_SECURITY_POLICY = {
        'default-src': ("'self'",),
        'script-src': ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"),
        'style-src': ("'self'", "'unsafe-inline'", "cdnjs.cloudflare.com"),
        'img-src': ("'self'", "data:", "https:"),
    }

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'gamification-cache',
    }
}

# Email configuration (for production)
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# ============================================================================
# ====== GAMIFICATION SYSTEM SETTINGS (1000 LEVELS / 10 GALAXIES) ======
# ============================================================================

# ====== GALAXIES (10 GALAXIES x 100 LEVELS) ======
GALAXIES = {
    1: {
        'name': '🌟 Étoile du Matin',
        'color': '#10b981',
        'min_level': 1,
        'max_level': 100,
        'description': 'Début du voyage cosmique'
    },
    2: {
        'name': '💫 Andromède',
        'color': '#06b6d4',
        'min_level': 101,
        'max_level': 200,
        'description': 'Première exploration galactique'
    },
    3: {
        'name': '⭐ Voie Lactée',
        'color': '#f59e0b',
        'min_level': 201,
        'max_level': 300,
        'description': 'Au cœur de la galaxie'
    },
    4: {
        'name': '🌌 Sombrero',
        'color': '#ec4899',
        'min_level': 301,
        'max_level': 400,
        'description': 'Galaxie mystérieuse'
    },
    5: {
        'name': '🪐 Spirale du Cygne',
        'color': '#8b5cf6',
        'min_level': 401,
        'max_level': 500,
        'description': 'Danse cosmique'
    },
    6: {
        'name': '🔴 Nébuleuse du Crabe',
        'color': '#ef4444',
        'min_level': 501,
        'max_level': 600,
        'description': 'Énergie stellaire'
    },
    7: {
        'name': '🔵 Galaxie d\'Orion',
        'color': '#3b82f6',
        'min_level': 601,
        'max_level': 700,
        'description': 'Territoire avancé'
    },
    8: {
        'name': '💎 Trésor Cosmique',
        'color': '#14b8a6',
        'min_level': 701,
        'max_level': 800,
        'description': 'Richesses précieuses'
    },
    9: {
        'name': '🌠 Paradis Stellaire',
        'color': '#f97316',
        'min_level': 801,
        'max_level': 900,
        'description': 'Proche de l\'apothéose'
    },
    10: {
        'name': '👑 Univers Suprême',
        'color': '#6366f1',
        'min_level': 901,
        'max_level': 1000,
        'description': 'Maître de l\'univers'
    },
}

# ====== GAMIFICATION SETTINGS ======
GAMIFICATION_SETTINGS = {
    'XP_PER_ACTION': 10,
    'XP_PER_LEVEL': 100,
    'HP_TYPES': ['General', 'Physical', 'Mental', 'Social', 'Spiritual'],
    'HP_MAX': 100,
    'HP_PER_ACTION': 5,
    'STREAK_BONUS_XP': 5,
    'ACHIEVEMENT_CATEGORIES': ['Combat', 'Exploration', 'Social', 'Learning', 'Challenge'],
    'MAX_LEVEL': 1000,
    'TOTAL_GALAXIES': 10,
    'LEVELS_PER_GALAXY': 100,
}

# ====== STUDY TRACKER SETTINGS ======
STUDY_TRACKER_SETTINGS = {
    'PROGRESS_PER_SECTION': 2,  # 2% per section (50 sections = 100%)
    'SECTIONS_PER_CHAPTER': 50,
    'STREAK_BONUS_XP': 10,
}

# ====== XP REWARDS (Same for all 1000 levels) ======
XP_REWARDS = {
    'study_session_15min': 10,
    'study_session_30min': 25,
    'study_session_60min': 50,
    'quiz_easy': 15,
    'quiz_medium': 30,
    'quiz_hard': 50,
    'challenge_easy': 50,
    'challenge_medium': 100,
    'challenge_hard': 200,
    'challenge_extreme': 500,
    'achievement_unlocked': 100,
    'first_challenge_completed': 250,
    'perfect_score': 150,
    'streak_7_days': 100,
    'streak_30_days': 500,
}

# ====== LEVEL THRESHOLDS (1000 LEVELS) ======
# Progression exponentielle: chaque niveau nécessite plus d'XP
# Formule: XP requis = 100 * ln(level + 1) * 10
LEVEL_THRESHOLDS = [
    int(100 * math.log(i + 1) * 10) if i > 0 else 0
    for i in range(1001)  # 0 to 1000 levels
]

# Alternative: Simple linear progression (100 XP per level)
# LEVEL_THRESHOLDS = [i * 100 for i in range(1001)]

# ====== HP SYSTEM (PERSONALITY TRAITS) ======
HP_SETTINGS = {
    'INITIAL_HP': 0,
    'MAX_HP': 100,
    'MIN_HP': 0,
    'HP_PER_TRAIT_LEVEL': 10,
    'HP_DECAY_PER_DAY': 1,  # 1 HP lost per day without activity
}

# ====== PERSONALITY TRAIT CATEGORIES ======
PERSONALITY_TRAIT_CATEGORIES = {
    'cognitive': {'name': 'Cognitif', 'color': '#3b82f6', 'icon': '🧠'},
    'emotional': {'name': 'Émotionnel', 'color': '#f59e0b', 'icon': '💖'},
    'behavioral': {'name': 'Comportemental', 'color': '#10b981', 'icon': '⚙️'},
    'social': {'name': 'Social', 'color': '#ec4899', 'icon': '👥'},
    'moral': {'name': 'Moral/Éthique', 'color': '#6366f1', 'icon': '⚖️'},
    'dark': {'name': 'Traits Sombres', 'color': '#6b7280', 'icon': '🌑'},
    'motivational': {'name': 'Motivationnel', 'color': '#06b6d4', 'icon': '🔥'},
    'existential': {'name': 'Existentiel', 'color': '#8b5cf6', 'icon': '🌌'},
    'leadership': {'name': 'Leadership', 'color': '#059669', 'icon': '👑'},
    'affective': {'name': 'Affectif', 'color': '#dc2626', 'icon': '❤️'},
}

# ====== RESOURCE TYPES & DOMAINS ======
RESOURCE_TYPES = {
    'Livre': {'icon': '📚', 'color': '#8b5cf6'},
    'Article': {'icon': '📰', 'color': '#3b82f6'},
    'FilmSérie': {'icon': '🎬', 'color': '#f59e0b'},
    'Mentor': {'icon': '👨‍🏫', 'color': '#ec4899'},
    'Podcast': {'icon': '🎙️', 'color': '#10b981'},
}

RESOURCE_DOMAINS = {
    'Finance': {'icon': '💰', 'color': '#059669'},
    'Business': {'icon': '💼', 'color': '#2563eb'},
    'Mindset': {'icon': '🧠', 'color': '#dc2626'},
    'Tech': {'icon': '💻', 'color': '#7c3aed'},
    'Entrepreneuriat': {'icon': '🚀', 'color': '#ea580c'},
    'Philosophie': {'icon': '🤔', 'color': '#6366f1'},
    'Physique': {'icon': '⚛️', 'color': '#3b82f6'},
    'Chimie': {'icon': '🧪', 'color': '#8b5cf6'},
    'Agriculture': {'icon': '🌾', 'color': '#10b981'},
    'Romans': {'icon': '📖', 'color': '#ec4899'},
    'Autre': {'icon': '📂', 'color': '#6b7280'},
}

# ====== ACHIEVEMENT SYSTEM ======
ACHIEVEMENT_CATEGORIES = {
    'combat': {'name': 'Combat', 'icon': '⚔️', 'color': '#ef4444'},
    'exploration': {'name': 'Exploration', 'icon': '🗺️', 'color': '#f59e0b'},
    'social': {'name': 'Social', 'icon': '👥', 'color': '#ec4899'},
    'learning': {'name': 'Learning', 'icon': '📚', 'color': '#3b82f6'},
    'challenge': {'name': 'Challenge', 'icon': '🏆', 'color': '#10b981'},
}

# ====== SKILL SYSTEM ======
SKILL_CATEGORIES = {
    'technical': {'name': 'Technique', 'icon': '💻', 'color': '#7c3aed'},
    'soft': {'name': 'Soft Skills', 'icon': '🤝', 'color': '#ec4899'},
    'academic': {'name': 'Académique', 'icon': '📚', 'color': '#3b82f6'},
    'business': {'name': 'Business', 'icon': '💼', 'color': '#2563eb'},
    'personal': {'name': 'Personnel', 'icon': '✨', 'color': '#f59e0b'},
}

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ====== AUTHENTICATION SETTINGS ======
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'gamification:leaderboard'
LOGOUT_REDIRECT_URL = 'login'

# ====== SESSION SETTINGS ======
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ====== PAGINATION ======
PAGINATION_SETTINGS = {
    'DEFAULT_PAGE_SIZE': 20,
    'MAX_PAGE_SIZE': 100,
}

# ====== API SETTINGS ======
API_SETTINGS = {
    'THROTTLE_ENABLED': True,
    'RATE_LIMIT': '1000/hour',
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME', 'default-cloud-name'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET', '')
}

# Configurer Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
    api_key=CLOUDINARY_STORAGE['API_KEY'],
    api_secret=CLOUDINARY_STORAGE['API_SECRET'],
    secure=True
)

# ✅ REMPLACER le stockage par défaut par Cloudinary
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

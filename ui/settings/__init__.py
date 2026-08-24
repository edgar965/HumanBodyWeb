# -*- coding: utf-8 -*-
"""Django-Grundeinstellung — der Rest liegt nach Themen daneben.

`ui/settings.py` hatte 475 Zeilen und vier Themen (Befund `dateigroesse`,
Kriterium 2). Aufgeteilt am 17.08.2026:

    wurzeln.py           Version und die fünf Verzeichnisse
    pfade.py             Interpreter, externe Programme, Datenordner
    protokoll.py         LOG_DIR, Rotationssicherung, LOGGING
    djangobase_conf.py   DJANGOBASE (Menü, Themen, Logs, Tests, Review)
    review/              die 59 Review-Bereiche, nach Themen

Hier steht nur, was Django selbst braucht — und die Reihenfolge, in der die
Teile geladen werden. `import *` ist in einer Settings-Datei der Django-Weg:
Django liest die Namen dieses Moduls, egal woher sie kommen. Alle Namen sind
GROSS geschrieben; ein `_`-Name wäre von `import *` ohnehin ausgeschlossen.
"""

from .wurzeln import *                                        # noqa: F401,F403
from .pfade import *                                          # noqa: F401,F403
from .protokoll import *                                      # noqa: F401,F403
from .wurzeln import BASE_DIR                                 # noqa: F401

SECRET_KEY = 'django-insecure-mocapnet-dev-key-change-in-production'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangobase',
    'core',
]

MIDDLEWARE = [
    'ui.no_cache.NoCacheStaticMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # Direkt hinter der CSRF-Prüfung: Sie greift bei den 35 `csrf_exempt`-
    # Endpunkten nicht, diese hier schon. Sie fragt nicht nach einem Token,
    # sondern ob die Anfrage von der eigenen Seite kommt (13.08.2026).
    'ui.same_origin.GleicherUrsprungMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ui.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ui.context_processors.version',
                'ui.context_processors.active_theme',
                'djangobase.context_processors.djangobase',
            ],
        },
    },
]

WSGI_APPLICATION = 'ui.wsgi.application'
ASGI_APPLICATION = 'ui.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#: Grenzen für den Video-Export: Der Browser schickt Hunderte PNG-Einzelbilder
#: in EINER Anfrage.
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024   # 500 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024   # 500 MB
DATA_UPLOAD_MAX_NUMBER_FILES = 10000              # bis zu 10.000 Bilder

#: Kanäle für die WebSocket-Verbindungen (im Speicher, Entwicklungsbetrieb).
CHANNEL_LAYERS = {
    'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'},
}

from .djangobase_conf import DJANGOBASE                       # noqa: E402,F401

# Örtliche Abweichungen (nicht im Repo — jeder Rechner hat seine eigene).
try:
    from ..local_settings import *                            # noqa: F401,F403
# stumm gewollt: Die Datei ist absichtlich nicht im Repo — jeder Rechner hat
# seine eigene, und die meisten haben gar keine. Ein Log hier stünde bei jedem
# Start da und würde nichts bedeuten.
except ImportError:
    pass

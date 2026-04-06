import os
import sys
from pathlib import Path

VERSION = '0.31'

BASE_DIR = Path(__file__).resolve().parent.parent
TOOLS_ROOT = BASE_DIR.parent              # A:\3DTools
VIDEOTOBVH_ROOT = TOOLS_ROOT / 'VideoToBVH'
MOCAPNET_ROOT = VIDEOTOBVH_ROOT / 'MocapNET'

# Add humanbody_core to Python path (lives inside HumanBody/)
HUMANBODY_ROOT = TOOLS_ROOT / 'HumanBody'
_core_parent = str(HUMANBODY_ROOT)
if _core_parent not in sys.path:
    sys.path.insert(0, _core_parent)

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
    'core',
]

MIDDLEWARE = [
    'ui.no_cache.NoCacheStaticMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
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

# Upload limits for video export (hundreds of PNG frames)
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024   # 500 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024   # 500 MB
DATA_UPLOAD_MAX_NUMBER_FILES = 10000               # up to 10k frames

# Pipeline Python (venv with CUDA PyTorch, ONNX Runtime GPU, etc.)
PIPELINE_PYTHON = str(TOOLS_ROOT / 'pythonENV' / 'Scripts' / 'python.exe')

# MocapNET paths
MOCAPNET_EXE = MOCAPNET_ROOT / 'MocapNET2CSV.exe'
MEDIAPIPE_SCRIPT = MOCAPNET_ROOT / 'src' / 'python' / 'mediapipe' / 'mediapipeHolistic2CSV.py'
BVH_OUTPUT_DIR = MOCAPNET_ROOT / 'output'
BLENDER_BVH_DIR = HUMANBODY_ROOT / 'data' / 'animations' / 'bvh' / 'MocapNET'

# OpenPose paths
OPENPOSE_ROOT = VIDEOTOBVH_ROOT / 'OpenPose'
OPENPOSE_EXE = OPENPOSE_ROOT / 'build' / 'bin' / 'OpenPoseDemo.exe'
OPENPOSE_MODEL_DIR = OPENPOSE_ROOT / 'models'
OPENPOSE_JSON2CSV_EXE = MOCAPNET_ROOT / 'convertOpenPoseJSONToCSV.exe'

# MocapNET v4 paths
MOCAPNET_V4_ROOT = VIDEOTOBVH_ROOT / 'MocapNET_v4'
MOCAPNET_V4_SCRIPT = MOCAPNET_V4_ROOT / 'run_v4_pipeline.py'

# New pipeline paths
GVHMR_ROOT = VIDEOTOBVH_ROOT / 'GVHMR'
WHAM_ROOT = VIDEOTOBVH_ROOT / 'WHAM'
PROMPTHMR_ROOT = VIDEOTOBVH_ROOT / 'PromptHMR'
WRAPPERS_DIR = VIDEOTOBVH_ROOT / 'wrappers'

# HumanBody paths (HUMANBODY_ROOT defined above with sys.path)
HUMANBODY_DATA_DIR = HUMANBODY_ROOT / 'data' / 'humanBody'
HUMANBODY_MODELS_DIR = HUMANBODY_ROOT / 'data' / 'models'
HUMANBODY_ASSETS_DIR = HUMANBODY_ROOT / 'data' / 'assets'
HUMANBODY_ASSETS_GLB_DIR = HUMANBODY_ROOT / 'data' / 'assets_glb'
HUMANBODY_ASSETS_INSTANCE_DIR = HUMANBODY_ROOT / 'data' / 'assetsInstance'
HUMANBODY_BVH_DIR = HUMANBODY_ROOT / 'data' / 'animations' / 'bvh' / 'MocapNET'
BVH_RESULTS_DIR = HUMANBODY_ROOT / 'data' / 'animations' / 'bvh' / 'Results'
HUMANBODY_GARMENT_LIBRARY_DIR = HUMANBODY_ROOT / 'data' / 'garment_library'
HUMANBODY_GARMENT_EXPORT_DIR = HUMANBODY_ROOT / 'data' / 'garment_exports'
HUMANBODY_SMPL_GARMENT_DIR = HUMANBODY_ROOT / 'data' / 'garment_pattern_gen'
SMPL_MODELS_DIR = VIDEOTOBVH_ROOT / 'models' / 'smpl'

# Add assetCreator to Python path for GarmentFitter
_asset_creator_parent = str(HUMANBODY_ROOT / 'assetCreator')
if _asset_creator_parent not in sys.path:
    sys.path.insert(0, _asset_creator_parent)

# Logging — rotating file + console
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'django.log'),
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 3,
            'formatter': 'verbose',
            'encoding': 'utf-8',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.channels.server': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'daphne': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'core': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'GarmentFitter': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Channel layers (in-memory for dev)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# Local overrides (not tracked in git — each team member has their own)
try:
    from .local_settings import *  # noqa: F401,F403
except ImportError:
    pass

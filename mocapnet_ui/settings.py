import os
import sys
from pathlib import Path

VERSION = '0.90'

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
    'mocapnet_ui.no_cache.NoCacheStaticMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mocapnet_ui.urls'

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
                'mocapnet_ui.context_processors.version',
            ],
        },
    },
]

WSGI_APPLICATION = 'mocapnet_ui.wsgi.application'
ASGI_APPLICATION = 'mocapnet_ui.asgi.application'

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

# Channel layers (in-memory for dev)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

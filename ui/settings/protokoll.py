# -*- coding: utf-8 -*-
"""Protokoll — Log-Verzeichnis, die Rotationssicherung und die LOGGING-Config.

Aus `ui/settings.py` herausgelöst (17.08.2026). Die 120 Zeilen `LOGGING` sind der
größte Einzelblock der alten Datei gewesen; dazu gehört der Eingriff in
`RotatingFileHandler` direkt darüber, der ohne den Zusammenhang unerklärlich ist.

FÜNF DATEIEN, WEIL FÜNF FRAGEN
==============================
`django.log` (Anfragen), `core.log` (Figur/API), `pipeline.log`
(Unterprozesse der Video-Kette), `client.log` (Meldungen aus dem Browser) und
`errors.log` (alles Rote, aggregiert). Wer eine Ursache sucht, sucht in genau
einer davon — deshalb nicht alles in eine.
"""

import logging.handlers as _lh

from .wurzeln import BASE_DIR

#: Hier liegen die Logdateien; djangoBase liest sie für Hilfe → Logs.
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)


# DIE ROTATION DES LOGS SELBST DARF NICHT WERFEN (Windows-Eigenheit): Hält ein
# zweiter Prozess (Daphne-Neustart, geöffneter Editor) `django.log` fest,
# scheitert das Umbenennen mit `PermissionError` — und zwar mitten in einem
# Logaufruf, also an einer Stelle, an der niemand mit einer Ausnahme rechnet.
# Der Eingriff steht hier statt in einem eigenen Modul, weil er zum Zeitpunkt
# von `dictConfig` schon gelaufen sein muss.
_orig_do_rollover = _lh.RotatingFileHandler.doRollover
_orig_rotate = _lh.RotatingFileHandler.rotate


def _safe_do_rollover(self):
    try:
        _orig_do_rollover(self)
    # stumm gewollt: Rotation des Logs selbst — ein Log darüber riefe sich im
    # Zweifel selbst auf. Die Rotation wird beim nächsten Mal nachgeholt.
    except (PermissionError, OSError):
        pass


def _safe_rotate(self, source, dest):
    try:
        _orig_rotate(self, source, dest)
    # stumm gewollt: siehe oben.
    except (PermissionError, OSError):
        pass


_lh.RotatingFileHandler.doRollover = _safe_do_rollover
_lh.RotatingFileHandler.rotate = _safe_rotate

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'job_ctx': {
            '()': 'core.logging_utils.JobContextFilter',
        },
    },
    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name} {job_str}{message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        # Aggregat: Django-Request-Pipeline + Errors
        'django_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'django.log'),
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose',
            'encoding': 'utf-8',
            'filters': ['job_ctx'],
        },
        # Character / HumanBody API: Mesh, Morphs, Rig, Wardrobe, Retarget
        'core_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'core.log'),
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose',
            'encoding': 'utf-8',
            'filters': ['job_ctx'],
        },
        # Video-to-BVH-Pipeline: MocapNET, GVHMR, OpenPose Subprocess-Output
        'pipeline_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'pipeline.log'),
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose',
            'encoding': 'utf-8',
            'filters': ['job_ctx'],
        },
        # Client-seitige JS-Logs (per /api/log/ gepostet)
        'client_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'client.log'),
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 3,
            'formatter': 'verbose',
            'encoding': 'utf-8',
            'filters': ['job_ctx'],
        },
        # Errors-Aggregat: alles WARNING+ landet zusaetzlich hier
        'error_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'errors.log'),
            'maxBytes': 5 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'verbose',
            'encoding': 'utf-8',
            'filters': ['job_ctx'],
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['job_ctx'],
        },
    },
    'root': {
        'handlers': ['django_file', 'error_file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['django_file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.channels.server': {
            'handlers': ['django_file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'daphne': {
            'handlers': ['django_file', 'error_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'core': {
            'handlers': ['core_file', 'error_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'core.pipeline': {
            'handlers': ['pipeline_file', 'error_file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'core.client': {
            'handlers': ['client_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'GarmentFitter': {
            'handlers': ['core_file', 'error_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


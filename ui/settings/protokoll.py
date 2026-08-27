# -*- coding: utf-8 -*-
"""Protokoll — Log-Verzeichnis und die LOGGING-Config aus djangoBase.

Aus `ui/settings.py` herausgelöst (17.08.2026).

UMBAU 28.08.2026 — KONFORM STATT EIGENGEBAUT
============================================
Hier standen 190 Zeilen: ein selbst geschriebenes `LOGGING`-Wörterbuch mit
fünf Rotationssicherungen und ein Eingriff in `RotatingFileHandler`. Vier
Konformitätsprüfungen von djangoBase schlugen darauf an, und jede benannte
einen echten Nachteil:

* **`errors.log` statt `error.log`** — Hilfe → Logs zeigt genau zwei Reiter,
  „Allgemein" (django.log) und „Exceptions" (error.log). Die Datei hieß
  anders, also war der Reiter „Exceptions" leer. Eine leere Fehlerseite liest
  sich wie „keine Fehler".
* **Kein Formatierer `voll`** — und das Format hatte keinen Doppelpunkt hinter
  dem Namen. `LogFenster.KOPF` konnte die Zeilen nicht zerlegen; die
  Testaufzeichnung sammelte still NULL Log-Zeilen.
* **`error_file` auf WARNING** — dann ist „Exceptions" eine Kopie von
  „Allgemein" und taugt nicht zum Nachsehen. Warnungen stehen weiterhin in
  `django.log`, es geht also nichts verloren.
* **Eigener `RotatingFileHandler`-Eingriff** — djangoBase nimmt
  `concurrent_log_handler` (portalocker), sobald er da ist. Der löst dasselbe
  Windows-Problem richtig, statt den `PermissionError` zu verschlucken.

FÜNF DATEIEN, WEIL FÜNF FRAGEN
==============================
`django.log` (Anfragen), `core.log` (Figur/API), `pipeline.log`
(Unterprozesse der Video-Kette), `client.log` (Meldungen aus dem Browser) und
`error.log` (alles Rote, aggregiert). Wer eine Ursache sucht, sucht in genau
einer davon — deshalb nicht alles in eine. Die ersten beiden liefert
djangoBase, die drei mittleren kommen als `extra_handlers` dazu.
"""

import djangobase.logging as dblog

from .wurzeln import BASE_DIR

#: Hier liegen die Logdateien; djangoBase liest sie für Hilfe → Logs.
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

#: Größe, ab der eine Logdatei rotiert wird (5 MB), und wie viele alte Stände
#: liegen bleiben. Gilt für alle fünf Dateien.
GROESSE = 5 * 1024 * 1024
SICHERUNGEN = 3

#: Die drei Dateien, die es nur in diesem Projekt gibt: Name -> Erklärung.
EIGENE = {
    'core_file': ('core.log',
                  'Character/HumanBody-API: Netz, Regler, Rig, Garderobe'),
    'pipeline_file': ('pipeline.log',
                      'Video-to-BVH-Kette: MocapNET, GVHMR, OpenPose'),
    'client_file': ('client.log',
                    'Meldungen aus dem Browser (über /api/log/)'),
}

#: Was in `django.log` und `error.log` MIT hineingehört.
GRUNDZIELE = ['console', 'django_file', 'error_file']


#: Die drei eigenen Dateien, fertig gebaut. Der Bausatz kommt aus djangoBase
#: (`dblog.datei_handler`, seit 28.08.2026 öffentlich): Nachgebaut sähe er
#: genauso aus — nur bliebe er beim nächsten Wechsel der Handler-Klasse oder
#: der Dateigröße stehen, während `django.log` und `error.log` mitzögen.
EIGENE_HANDLER = {
    name: dblog.datei_handler(LOG_DIR, datei, level='DEBUG',
                              max_bytes=GROESSE, backup_count=SICHERUNGEN,
                              filters=dblog.handler_filters_fuer(True))
    for name, (datei, _zweck) in EIGENE.items()
}

LOGGING = dblog.config(
    LOG_DIR,
    level='INFO',
    # Der `{job_str}`-Platz im Format und `djangobase.jobctx.JobContextFilter`
    # auf jedem Handler. Die Auftragskennung setzt
    # `core.logging_utils.Auftragskontext` — seit dem 28.08.2026 derselbe
    # ContextVar (vorher zwei, und der eine las nie, was der andere schrieb).
    job_context=True,
    extra_handlers=EIGENE_HANDLER,
    extra_loggers={
        'django.channels.server': {'handlers': GRUNDZIELE,
                                   'level': 'INFO', 'propagate': False},
        'daphne': {'handlers': ['django_file', 'error_file'],
                   'level': 'WARNING', 'propagate': False},
        'core': {'handlers': ['core_file', 'error_file', 'console'],
                 'level': 'DEBUG', 'propagate': False},
        'core.pipeline': {'handlers': ['pipeline_file', 'error_file',
                                       'console'],
                          'level': 'DEBUG', 'propagate': False},
        'core.client': {'handlers': ['client_file', 'error_file'],
                        'level': 'DEBUG', 'propagate': False},
        'GarmentFitter': {'handlers': ['core_file', 'error_file', 'console'],
                          'level': 'INFO', 'propagate': False},
    },
    file_max_bytes=GROESSE,
    file_backup_count=SICHERUNGEN,
)

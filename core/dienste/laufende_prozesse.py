# -*- coding: utf-8 -*-
"""LaufendeProzesse — welche Pipeline-Unterprozesse gerade laufen.

WARUM (Umbau 15.08.2026): In core/views.py standen `_active_procs = {}` und
`_active_procs_lock = threading.Lock()` als Modulvariablen, benutzt an neun
Stellen und von ZWEI Themen — den Auftrags-Endpunkten (anhalten) und den
Pipeline-Laeufen (eintragen). Beim Aufteilen der Datei waeren daraus zwei
getrennte Verzeichnisse geworden, und ein "Anhalten" haette einen Prozess
gesucht, den es in seiner Kopie nie gab.

Die Sperre gehoert zum Verzeichnis; deshalb liegen beide hier und werden nur
ueber diese Klasse angefasst.
"""
import logging
import threading

logger = logging.getLogger('core')


class LaufendeProzesse:
    """Verzeichnis der laufenden Pipeline-Prozesse, nach Auftrags-ID."""

    _prozesse = {}                 # job_id (str) -> subprocess.Popen
    _sperre = threading.Lock()

    @classmethod
    def eintragen(cls, job_id, prozess):
        with cls._sperre:
            cls._prozesse[str(job_id)] = prozess
        return prozess

    @classmethod
    def holen(cls, job_id):
        with cls._sperre:
            return cls._prozesse.get(str(job_id))

    @classmethod
    def entfernen(cls, job_id):
        with cls._sperre:
            return cls._prozesse.pop(str(job_id), None)

    @classmethod
    def anzahl(cls):
        with cls._sperre:
            return len(cls._prozesse)

    @classmethod
    def ids(cls):
        with cls._sperre:
            return list(cls._prozesse)

    @classmethod
    def beenden(cls, job_id, warten_s=5):
        """Prozess eines Auftrags beenden. True, wenn einer da war.

        Erst `terminate`, dann `kill`: Ein ML-Prozess mit CUDA-Kontext braucht
        einen Moment, um seine Puffer zu schliessen; ein sofortiges `kill`
        hinterlaesst belegten Grafikspeicher bis zum Prozessende."""
        prozess = cls.entfernen(job_id)
        if prozess is None:
            return False
        try:
            prozess.terminate()
            try:
                prozess.wait(timeout=warten_s)
            except Exception:                                     # noqa: BLE001
                prozess.kill()
        except Exception as e:                                    # noqa: BLE001
            logger.warning('Prozess von Auftrag %s liess sich nicht beenden: %s',
                           job_id, e)
            return False
        logger.info('Prozess von Auftrag %s beendet', job_id)
        return True

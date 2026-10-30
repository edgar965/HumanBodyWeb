# -*- coding: utf-8 -*-
"""Mesh3dairechenschlange — Warteschlange, Start und Anlage der Rechenläufe von Mesh3D-AI (23.10.2026, zu `Mesh3dairechenlauf`).

Ein Lauf zur Zeit: `3DObjects/mesh3dai/_rechnen/laeuft.json` (PID, Kennung) hält ihn, `schlange.json` die wartenden Kennungen. „Rechnen“ reiht ein und startet einen abgelösten Arbeitsprozess
(`manage.py mesh3dai_rechnen`), wenn keiner lebt; der arbeitet die Schlange ab. Ein Test aus einer hochgeladenen Datei bekommt `_test/<kennung>/eingang/<datei>` und `anlage.json`
({name, quelle, geschlecht}) — die Schrittskripte finden ihn darüber (`mesh3dai_test_rechnen.TESTS`, `Vorstufentest`).
"""
import json
import logging
import re
import subprocess
import sys
import time
from pathlib import Path

from django.conf import settings

from core.atomic_write import AtomarSchreiber

from .auftragsarbeiter import Auftragsarbeiter
from .mesh3dairechenlauf import Mesh3dairechenlauf
from .mesh3daitest import Mesh3daitest

logger = logging.getLogger('core')

__all__ = ['Mesh3dairechenschlange']


class Mesh3dairechenschlange:
    ENDUNGEN = ('.glb', '.obj', '.fbx', '.blend')

    @staticmethod
    def ordner():
        return Path(settings.OBJECTS_ROOT) / 'mesh3dai' / '_rechnen'

    @classmethod
    def _lesen(cls, name, vorgabe):
        try:
            return json.loads((cls.ordner() / name).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return vorgabe

    @staticmethod
    def _lebt(pid):
        try:
            import psutil
            return bool(pid) and psutil.pid_exists(int(pid))
        except (ImportError, ValueError):
            return False

    @classmethod
    def laeuft(cls):
        """{pid, kennung, seit} des lebenden Arbeitsprozesses oder None."""
        s = cls._lesen('laeuft.json', None)
        return s if s and cls._lebt(s.get('pid')) else None

    @classmethod
    def schlange(cls):
        return [k for k in cls._lesen('schlange.json', []) if isinstance(k, str)]

    @classmethod
    def starten(cls, kennung):
        """Einreihen und den Arbeitsprozess starten, falls keiner läuft. → Stand des Laufs."""
        stand = Mesh3dairechenlauf(kennung).vorbereiten('wartet')
        schlange = cls.schlange()
        if kennung not in schlange:
            schlange.append(kennung)
        AtomarSchreiber.json_schreiben(cls.ordner() / 'schlange.json', schlange)
        if cls.laeuft() is None:
            protokoll = open(cls.ordner() / 'arbeiter.log', 'a', encoding='utf-8')
            p = subprocess.Popen([sys.executable, str(Path(settings.BASE_DIR) / 'manage.py'), 'mesh3dai_rechnen'], cwd=str(settings.BASE_DIR), stdin=subprocess.DEVNULL,
                                 stdout=protokoll, stderr=subprocess.STDOUT, creationflags=Auftragsarbeiter.flags())
            logger.info('Mesh3D-AI Rechenlauf: Arbeitsprozess %d gestartet für %s', p.pid, kennung)
        return stand

    #: Sperrdatei des Arbeitsprozesses (30.10.2026): exklusiv angelegt (`os.O_EXCL`), Inhalt die PID; eine leere Datei ist höchstens so alt (s) noch „wird gerade geschrieben“
    SPERRE, SPERRE_LEER_S = 'arbeiter.sperre', 60.0

    @classmethod
    def _beanspruchen(cls):
        """Die Schlange exklusiv übernehmen → True, wenn dieser Prozess die Sperre hält. Bis 30.10.2026 prüfte `abarbeiten` `laeuft.json` und schrieb es erst danach — zwei kurz
        nacheinander gestartete Arbeiter kamen beide durch und rechneten ballerina_bunt doppelt (29.10.2026). Die Sperre eines toten Prozesses wird weggeräumt."""
        import os
        datei = cls.ordner() / cls.SPERRE
        for _ in range(3):
            try:
                fd = os.open(datei, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                try:
                    inhalt, alter = datei.read_text(encoding='utf-8').strip(), time.time() - datei.stat().st_mtime
                except OSError:
                    continue                                      # eben weggeräumt — noch einmal versuchen
                if (inhalt and cls._lebt(inhalt)) or (not inhalt and alter < cls.SPERRE_LEER_S):
                    return False
                datei.unlink(missing_ok=True)
                continue
            with os.fdopen(fd, 'w', encoding='utf-8') as aus:
                aus.write(str(os.getpid()))
            return True
        return False

    @classmethod
    def abarbeiten(cls):
        """Im Arbeitsprozess: die Schlange abarbeiten (ein Lauf zur Zeit). → Zahl der Läufe. Nach dem Freigeben noch einmal nachsehen: wer einreihte, während dieser Prozess schon
        aufhörte, sah ihn noch leben und startete keinen neuen Arbeiter."""
        import os
        cls.ordner().mkdir(parents=True, exist_ok=True)
        zahl = 0
        while cls._beanspruchen():
            AtomarSchreiber.json_schreiben(cls.ordner() / 'laeuft.json', {'pid': os.getpid(), 'kennung': None, 'seit': time.strftime('%Y-%m-%dT%H:%M:%S')})
            try:
                while True:
                    schlange = cls.schlange()
                    if not schlange:
                        break
                    kennung = schlange.pop(0)
                    AtomarSchreiber.json_schreiben(cls.ordner() / 'schlange.json', schlange)
                    AtomarSchreiber.json_schreiben(cls.ordner() / 'laeuft.json', {'pid': os.getpid(), 'kennung': kennung, 'seit': time.strftime('%Y-%m-%dT%H:%M:%S')})
                    try:
                        Mesh3dairechenlauf(kennung).ausfuehren()
                    except Exception:          # noqa: BLE001 — ein Lauf scheitert, die Schlange läuft weiter; der Fehler steht im Log
                        logger.exception('Mesh3D-AI Rechenlauf %s abgebrochen', kennung)
                    zahl += 1
            finally:
                (cls.ordner() / 'laeuft.json').unlink(missing_ok=True)
                (cls.ordner() / cls.SPERRE).unlink(missing_ok=True)
            if not cls.schlange():
                break
        return zahl

    @classmethod
    def anlegen(cls, name, datei, geschlecht):
        """Einen Test aus einer hochgeladenen Datei anlegen (Django `UploadedFile`). → Kennung."""
        name = str(name or '').strip() or Path(datei.name).stem
        endung = Path(datei.name).suffix.lower()
        if endung not in cls.ENDUNGEN:
            raise ValueError('Dateityp %s — erwartet %s' % (endung or '(keiner)', ', '.join(cls.ENDUNGEN)))
        if geschlecht not in ('weiblich', 'maennlich'):
            raise ValueError('Geschlecht weiblich oder maennlich')
        stamm = re.sub(r'[^a-z0-9]+', '_', name.lower().replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')).strip('_') or 'test'
        kennung, n = stamm, 2
        while (Mesh3daitest.ordner() / kennung).exists():
            kennung, n = '%s_%d' % (stamm, n), n + 1
        test = Mesh3daitest.ordner() / kennung
        ziel = test / 'eingang' / ('eingang%s' % endung)
        ziel.parent.mkdir(parents=True)
        with open(ziel, 'wb') as aus:
            for stueck in datei.chunks():
                aus.write(stueck)
        AtomarSchreiber.json_schreiben(test / 'anlage.json', {'name': name, 'quelle': str(ziel), 'geschlecht': geschlecht, 'datei': datei.name,
                                                             'angelegt': time.strftime('%Y-%m-%dT%H:%M:%S')})
        AtomarSchreiber.json_schreiben(test / 'einstellung.json', {'geschlecht': geschlecht})
        logger.info('Mesh3D-AI: Test %s aus %s angelegt (%s)', kennung, datei.name, ziel)
        return kennung

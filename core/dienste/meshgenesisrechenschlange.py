# -*- coding: utf-8 -*-
"""Meshgenesisrechenschlange — Warteschlange, Start und Anlage der Rechenläufe von Mesh-Genesis (23.10.2026, zu `Meshgenesisrechenlauf`).

Ein Lauf zur Zeit: `3DObjects/meshgenesis/_rechnen/laeuft.json` (PID, Kennung) hält ihn, `schlange.json` die wartenden Kennungen. „Rechnen“ reiht ein und startet einen abgelösten Arbeitsprozess
(`manage.py meshgenesis_rechnen`), wenn keiner lebt; der arbeitet die Schlange ab. Ein Test aus einer hochgeladenen Datei bekommt `_test/<kennung>/eingang/<datei>` und `anlage.json`
({name, quelle, geschlecht}) — die Schrittskripte finden ihn darüber (`meshgenesis_test_rechnen.TESTS`, `Vorstufentest`).
"""
import json
import logging
import subprocess
import sys
import time
from pathlib import Path

from django.conf import settings

from core.atomic_write import AtomarSchreiber

from .auftragsarbeiter import Auftragsarbeiter
from .kennungsstamm import Kennungsstamm
from .meshgenesisrechenlauf import Meshgenesisrechenlauf
from .meshgenesistest import Meshgenesistest

logger = logging.getLogger('core')

__all__ = ['Meshgenesisrechenschlange']


class Meshgenesisrechenschlange:
    ENDUNGEN = ('.glb', '.obj', '.fbx', '.blend')
    #: Eintrag für einen ganzen Job (`Fotogenesisjoblauf`: PSHuman, Foto-Kette, dann der Test); sonst steht in der Schlange die Kennung eines Tests
    JOB = 'job:'

    @staticmethod
    def ordner():
        return Path(settings.OBJECTS_ROOT) / 'meshgenesis' / '_rechnen'

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
    def starten(cls, kennung, ab=None):
        """Einreihen und den Arbeitsprozess starten, falls keiner läuft. `ab`: wie `Meshgenesisrechenlauf.vorbereiten`, dort auch der `ValueError`. → Stand des Laufs."""
        stand = Meshgenesisrechenlauf(kennung).vorbereiten('wartet', ab=ab)
        cls._einreihen(kennung)
        return stand

    @classmethod
    def job_starten(cls, job):
        """Einen ganzen Job einreihen (`Fotogenesisjoblauf`). → Stand. `ValueError`, wenn er schon rechnet oder etwas fehlt."""
        from .fotogenesisjoblauf import Fotogenesisjoblauf
        if cls.job_aktiv(job['id']):
            raise ValueError('Der Job rechnet schon')
        stand = Fotogenesisjoblauf(job).vorbereiten()
        cls._einreihen(cls.JOB + job['id'])
        return stand

    @classmethod
    def job_aktiv(cls, kennung):
        """Wartet der Job in der Schlange, oder rechnet ihn der Arbeitsprozess? Kennung None: Der Prozess nimmt gerade den nächsten Eintrag."""
        eintrag, lauf = cls.JOB + kennung, cls.laeuft()
        return eintrag in cls.schlange() or (lauf is not None and lauf.get('kennung') in (eintrag, None))

    @classmethod
    def _einreihen(cls, kennung):
        schlange = cls.schlange()
        if kennung not in schlange:
            schlange.append(kennung)
        AtomarSchreiber.json_schreiben(cls.ordner() / 'schlange.json', schlange)
        if cls.laeuft() is None:
            protokoll = open(cls.ordner() / 'arbeiter.log', 'a', encoding='utf-8')
            p = subprocess.Popen([sys.executable, str(Path(settings.BASE_DIR) / 'manage.py'), 'meshgenesis_rechnen'], cwd=str(settings.BASE_DIR), stdin=subprocess.DEVNULL,
                                 stdout=protokoll, stderr=subprocess.STDOUT, creationflags=Auftragsarbeiter.flags())
            logger.info('Mesh-Genesis Rechenlauf: Arbeitsprozess %d gestartet für %s', p.pid, kennung)

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
                # Seit 09.11.2026: Zwei Arbeiter sahen dieselbe tote Sperre; der erste räumte sie weg und legte seine an, der zweite löschte danach und bekam unter Windows
                # PermissionError (die neue Sperre war noch offen) — der Arbeiter stürzte ab. Gelöscht wird nur, was noch dieselbe tote Sperre ist; sonst noch einmal von vorn.
                try:
                    if datei.read_text(encoding='utf-8').strip() == inhalt:
                        datei.unlink()
                except OSError:
                    pass
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
                        cls._rechnen(kennung)
                    except Exception:          # noqa: BLE001 — ein Lauf scheitert, die Schlange läuft weiter; der Fehler steht im Log
                        logger.exception('Mesh-Genesis Rechenlauf %s abgebrochen', kennung)
                    zahl += 1
            finally:
                (cls.ordner() / 'laeuft.json').unlink(missing_ok=True)
                (cls.ordner() / cls.SPERRE).unlink(missing_ok=True)
            if not cls.schlange():
                break
        return zahl

    @classmethod
    def _rechnen(cls, eintrag):
        """Ein Eintrag der Schlange: ein Job oder die Kennung eines Tests."""
        if eintrag.startswith(cls.JOB):
            from .fotogenesisjoblauf import Fotogenesisjoblauf
            Fotogenesisjoblauf.aus_kennung(eintrag[len(cls.JOB):]).ausfuehren()
        else:
            Meshgenesisrechenlauf(eintrag).ausfuehren()

    @classmethod
    def anlegen(cls, name, datei, geschlecht, foto=None, maske=None):
        """Einen Test aus einer hochgeladenen Datei anlegen (Django `UploadedFile`). → Kennung. `foto` und `maske` (beide oder keins): das Foto, aus dem das Netz entstand, für den Schritt „foto“ (`Meshgenesisfotogelenke`)."""
        name = str(name or '').strip() or Path(datei.name).stem
        endung = Path(datei.name).suffix.lower()
        if endung not in cls.ENDUNGEN:
            raise ValueError('Dateityp %s — erwartet %s' % (endung or '(keiner)', ', '.join(cls.ENDUNGEN)))
        if geschlecht not in ('weiblich', 'maennlich'):
            raise ValueError('Geschlecht weiblich oder maennlich')
        stamm = Kennungsstamm.aus_name(name, Meshgenesistest.KENNUNG_MAX - 4) or 'test'        # - 4: Platz für `_NN`
        kennung, n = stamm, 2
        while (Meshgenesistest.ordner() / kennung).exists():
            kennung, n = '%s_%d' % (stamm, n), n + 1
        test = Meshgenesistest.ordner() / kennung
        ziel = test / 'eingang' / ('eingang%s' % endung)
        ziel.parent.mkdir(parents=True)
        with open(ziel, 'wb') as aus:
            for stueck in datei.chunks():
                aus.write(stueck)
        for stamm_foto, quelle in (('foto', foto), ('maske', maske)):
            if foto is not None and maske is not None:
                (test / 'foto').mkdir(exist_ok=True)
                with open(test / 'foto' / (stamm_foto + Path(quelle.name).suffix.lower()), 'wb') as aus:
                    for stueck in quelle.chunks():
                        aus.write(stueck)
        AtomarSchreiber.json_schreiben(test / 'anlage.json', {'name': name, 'quelle': str(ziel), 'geschlecht': geschlecht, 'datei': datei.name,
                                                             'angelegt': time.strftime('%Y-%m-%dT%H:%M:%S')})
        AtomarSchreiber.json_schreiben(test / 'einstellung.json', {'geschlecht': geschlecht})
        logger.info('Mesh-Genesis: Test %s aus %s angelegt (%s)', kennung, datei.name, ziel)
        return kennung

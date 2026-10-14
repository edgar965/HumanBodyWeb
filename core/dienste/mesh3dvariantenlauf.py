# -*- coding: utf-8 -*-
"""Mesh3dvariantenlauf — der abgelöste Prozess, der die Varianten eines Imports nacheinander rechnet (13.10.2026).

`manage.py mesh3d_varianten <kennung>` als eigener Prozess ohne Fenster (wie `Meshfigurarbeiter`/`Blendimportarbeiter`: ein Neustart des Servers reißt den Lauf nicht mit). PID und Log liegen im Ordner des Imports
(`varianten.pid`, `varianten.log`). Der Prozess rechnet jede wartende Variante (`Meshfigurauftrag.status == 'angelegt'`) mit `Blendimportfigur.rechnen` — dieselbe Rechnung wie der Schritt „figur“ des Imports,
mit demselben Körpernetz (`koerper.glb`), denselben Stimmen der Segmentierung und derselben Pose, nur mit dem anderen Wert; die Pose einer Variante `pose = aus` ist leer (MediaPipe).
Nacheinander, weil sich ein Lauf die GPU nicht teilt; ein gescheiterter hält die übrigen nicht auf.
"""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

from django.conf import settings

from ..daten.blendimportablage import Blendimportablage
from .auftragsarbeiter import Auftragsarbeiter

logger = logging.getLogger('core')

__all__ = ['Mesh3dvariantenlauf']


class Mesh3dvariantenlauf:
    BEFEHL = 'mesh3d_varianten'
    PID = 'varianten.pid'
    LOG = 'varianten.log'
    #: Wie bei den anderen Arbeitern: „haar“ und „kleidung“ rechnen in Fäden, mehrere OpenBLAS-Fäden hängen sich dabei auf.
    UMGEBUNG = {'OPENBLAS_NUM_THREADS': '1'}
    #: Sekunden zwischen zwei Blicken, ob ein anderer Import noch rechnet (nur mit `warten`).
    WARTEN_S = 20

    # ------------------------------------------------------------ Prozess

    @classmethod
    def starten(cls, kennung, warten=False):
        """`warten`: der Prozess rechnet erst, wenn kein ANDERER Import mehr rechnet (die automatische Variante startet am Ende ihres Imports, `Mesh3dvariantenauto`)."""
        ablage = Blendimportablage(kennung)
        befehl = [sys.executable, str(Path(settings.BASE_DIR) / 'manage.py'), cls.BEFEHL, kennung] + (['--warten'] if warten else [])
        with open(ablage.ordner() / cls.LOG, 'ab') as protokoll:
            prozess = Auftragsarbeiter._popen(befehl, protokoll, umgebung=cls.UMGEBUNG)
        (ablage.ordner() / cls.PID).write_text(str(prozess.pid))
        logger.info('Mesh-3D %s: Varianten-Prozess %s gestartet', kennung, prozess.pid)
        return prozess.pid

    @classmethod
    def pid(cls, kennung):
        try:
            return int((Blendimportablage(kennung).ordner() / cls.PID).read_text().strip())
        # stumm gewollt: keine PID-Datei heißt kein laufender Prozess
        except (OSError, ValueError):
            return None

    @classmethod
    def lebt(cls, kennung):
        from ..pipelines.prozesspruefung import Prozesspruefung

        pid = cls.pid(kennung)
        return bool(pid) and Prozesspruefung.lebt(pid)

    @classmethod
    def anhalten(cls, kennung):
        """Der Prozess samt Kindern (der Runner hält die GPU); was noch wartete oder rechnete, steht auf „angehalten“."""
        from ..models import Meshfigurauftrag
        from .mesh3dvarianten import Mesh3dvarianten

        pid = cls.pid(kennung)
        for eintrag in Mesh3dvarianten.lesen(kennung)['eintraege']:
            try:
                Meshfigurauftrag.objects.filter(pk=eintrag['id'], status__in=('angelegt', 'laeuft')).update(status='angehalten')
            except (ValueError, TypeError):
                logger.warning('Mesh-3D %s: Variante %s nicht angehalten', kennung, eintrag.get('id'))
        if not pid:
            return
        try:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], capture_output=True, check=False)
            else:
                os.kill(pid, 15)
        except OSError as fehler:
            logger.warning('Mesh-3D %s: Varianten-Prozess %s nicht beendet: %s', kennung, pid, fehler)
        try:
            (Blendimportablage(kennung).ordner() / cls.PID).unlink()
        except OSError:
            logger.debug('Mesh-3D %s: %s war nicht da', kennung, cls.PID)

    # ------------------------------------------------------------- Rechnen

    @classmethod
    def _abwarten(cls, kennung):
        """Rechnet ein ANDERER Import, gehören GPU und Kerne ihm (`Mesh3dvarianten._frei`): alle `WARTEN_S` nachsehen, bis er fertig ist."""
        from .blendimportarbeiter import Blendimportarbeiter

        gemeldet = False
        while True:
            andere = Blendimportarbeiter.laufender(ausser=kennung)
            if not andere:
                return
            if not gemeldet:
                logger.info('Mesh-3D %s: die Varianten warten auf den Import %s', kennung, andere)
                gemeldet = True
            time.sleep(cls.WARTEN_S)

    @classmethod
    def ausfuehren(cls, kennung, warten=False):
        """Im Arbeitsprozess: jede wartende Variante rechnen, bis keine mehr da ist (neu Angelegte werden mitgenommen, gelöschte übersprungen)."""
        from ..models import Meshfigurauftrag
        from .mesh3dvarianten import Mesh3dvarianten

        fertig = set()
        while True:
            eintrag = next((e for e in Mesh3dvarianten.lesen(kennung)['eintraege'] if e['id'] not in fertig), None)
            if eintrag is None:
                return
            fertig.add(eintrag['id'])
            if warten:
                cls._abwarten(kennung)
            job = Meshfigurauftrag.objects.filter(pk=eintrag['id']).first()
            if job is None or job.status != 'angelegt':
                continue
            try:
                cls._rechnen(kennung, job)
            except Exception as fehler:  # noqa: BLE001 — eine Variante scheitert für sich, die nächste läuft
                logger.exception('Mesh-3D %s: Variante %s gescheitert', kennung, eintrag.get('titel'))
                job = Meshfigurauftrag.objects.filter(pk=job.pk).first()
                if job is not None and job.status not in ('gescheitert', 'angehalten'):
                    job.status = 'gescheitert'
                    job.error_message = str(fehler)[:4000]
                    job.save(update_fields=['status', 'error_message', 'updated_at'])

    @staticmethod
    def _rechnen(kennung, job):
        from ..daten.meshfigurablage import Meshfigurablage
        from .blendimportfigur import Blendimportfigur
        from .blendimportkoerper import Blendimportkoerper
        from .blendimportpose import Blendimportpose
        from .blendimportsegmentierung import Blendimportsegmentierung
        from .mesh3dvarianten import Mesh3dvarianten

        ablage = Blendimportablage(kennung)
        stand = ablage.stand()
        eintrag = next(e for e in Mesh3dvarianten.lesen(kennung)['eintraege'] if e['id'] == str(job.id))
        glb = ablage.arbeit(Blendimportkoerper.DATEI)
        einstellungen = {**(stand.get('einstellungen') or {})}
        if eintrag['feld'] == 'pose':
            einstellungen['pose'] = eintrag['wert']
        zusatz = Blendimportpose.zusatz(ablage, {**stand, 'einstellungen': einstellungen}, glb)
        sapiens = Blendimportsegmentierung.fuer_figur(ablage, stand, Meshfigurablage(job.kennung), glb)
        Blendimportfigur.rechnen(job, zusatz, sapiens)

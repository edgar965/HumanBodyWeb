# -*- coding: utf-8 -*-
"""Blendermodelllauf — ein Auftrag „BlenderModel": Grundfigur → Kostüm-Kreislauf → Figur mit Rig → Blender.

DIES IST DIE PIPELINE DES BEREICHS — die Datei, in der gebaut wird (Edgar, 29.09.2026: „Darin möchte ich eine
neue Pipeline einbauen"). Alles, was um sie herum steht (Seite, Tabelle, Fotoauswahl, Neu berechnen,
Umbenennen, Duplizieren, Bühne, Export), fragt nur: Welche Schritte gibt es (`SCHRITTE`), in welchem Band des
Balkens läuft jeder (`BAENDER`), und was steht danach in `job.ergebnis`? Ein Schritt ist eine Zeile in
`schrittfolge()`.

FASSUNG VOM 29.09.2026 (abends): **ohne Netz aus den Fotos.** Die erste Fassung desselben Tages begann mit
„netz" (TRELLIS.2/Hunyuan3D über `_run_mesh.py`) und passte Genesis daran an (die Kette von „Mesh to 3D":
erkennung … frisur). Edgar: „trellis soll nicht laufen" — auf gemalten Vorlagen liefert es kein brauchbares
Netz, und ein Lauf mit der übrig gebliebenen Option `formmodell: trellis2` hat es trotzdem gestartet. Die
Fotos sind jetzt VORLAGE, gegen die der Kostüm-Kreislauf seine Renders benotet — kein Eingang eines Netzes.

    grundfigur   Genesis-9-Grundfigur (Option „Grundfigur") als GLB für Blender, Stellung für Bühne und Export
    kostuem      Kostüm-Kreislauf: Runden aus Optimierer + lokaler Prüf-KI gegen die Vorlagenbilder
    export       die Figur als GLB mit Rig (`Blendermodellexport`)
    blender      BVH retargeten und rendern (`Blendermodellblender`; ohne BVH übersprungen)
    speichern    Ablage in `output/Export/BlenderModel` (`Blendermodellspeichern`)

`ausfuehren(ab, bis)`: „Neu berechnen" beginnt beim gewählten Schritt; „Weiter iterieren" rechnet NUR
„kostuem" (`ab = bis = 'kostuem'`) — der Blender-Film dauert Minuten und zeigt das Kostüm noch nicht.
"""

import logging
import time

from django.utils import timezone

from ..daten.blendermodellablage import Blendermodellablage
from ..models import Blendermodellauftrag
from .blendermodelloptionen import Blendermodelloptionen

logger = logging.getLogger('core')

__all__ = ['Blendermodelllauf']


class Blendermodelllauf:
    SCHRITTE = ('grundfigur', 'kostuem', 'export', 'blender', 'speichern')
    #: Anteil am Balken 0…100 — der Kreislauf ist der lange Teil (je Runde ein Blender-Prozess).
    BAENDER = {
        'grundfigur': (0, 5),
        'kostuem': (5, 85),
        'export': (85, 88),
        'blender': (88, 98),
        'speichern': (98, 100),
    }

    class Angehalten(Exception):
        """Der Nutzer hat angehalten — kein Fehler, der Lauf endet still."""

    def __init__(self, job_id):
        self.job = Blendermodellauftrag.objects.get(pk=job_id)
        self.ablage = Blendermodellablage(self.job.kennung)
        #: Die Optionen der Figur (`basis`, `modell` — `Blendermodellspeichern` liest sie wie
        # `Meshfigurspeichern`).
        self.optionen = Blendermodelloptionen.figur(self.job.optionen)
        self._band = (0, 100)
        self._letzte_db = 0.0

    # --------------------------------------------------------------- Ablauf

    def schrittfolge(self):
        """Schritt → was er tut. Hier wird die Pipeline zusammengesteckt."""
        from .blendermodellblender import Blendermodellblender
        from .blendermodellexport import Blendermodellexport
        from .blendermodellgrundfigur import Blendermodellgrundfigur
        from .blendermodellspeichern import Blendermodellspeichern
        from .kostuemkreislauf import Kostuemkreislauf

        return {
            'grundfigur': lambda: Blendermodellgrundfigur(self).ausfuehren(),
            'kostuem': lambda: Kostuemkreislauf(self).ausfuehren(),
            'export': lambda: Blendermodellexport(self).ausfuehren(),
            'blender': lambda: Blendermodellblender(self).ausfuehren(),
            'speichern': lambda: Blendermodellspeichern(self).ausfuehren(),
        }

    def ausfuehren(self, ab=None, bis=None):
        job = self.job
        self.ablage.anlegen()
        job.ergebnis = dict(job.ergebnis or {})
        start = self.SCHRITTE.index(ab) if ab in self.SCHRITTE else 0
        ende = self.SCHRITTE.index(bis) + 1 if bis in self.SCHRITTE else len(self.SCHRITTE)
        if start > 0 and not self.ablage.arbeit('grundkoerper.glb').is_file():
            self._scheitern('Keine Grundfigur — erst den Schritt „Grundfigur" rechnen')
            return
        if start == 0:
            # Sonst stünden die Dauern früherer Schrittfolgen (die ausgebaute Netz-Kette) weiter im Ergebnis.
            job.ergebnis['dauer'] = {}
        schritte = self.schrittfolge()
        t0 = time.perf_counter()
        try:
            for name in self.SCHRITTE[start:ende]:
                self._schritt(name)
                t = time.perf_counter()
                schritte[name]()
                job.ergebnis.setdefault('dauer', {})[name] = round(time.perf_counter() - t, 1)
                self.sichern('ergebnis')
        except self.Angehalten:
            logger.info('BlenderModel %s: angehalten', job.kennung)
            return
        except Exception as fehler:  # noqa: BLE001 — jeder Fehler beendet den Lauf sichtbar
            logger.exception('BlenderModel %s: Schritt %s gescheitert', job.kennung, job.schritt)
            self._scheitern('%s: %s' % (job.schritt, fehler))
            return
        job.ergebnis['dauer_s'] = round(time.perf_counter() - t0, 1)
        job.status = 'fertig'
        job.progress = 100
        job.progress_detail = 'Fertig'
        job.finished_at = timezone.now()
        job.save(
            update_fields=['ergebnis', 'status', 'progress', 'progress_detail', 'finished_at', 'updated_at']
        )
        logger.info('BlenderModel %s: fertig in %.0f s', job.kennung, job.ergebnis['dauer_s'])

    def angehalten(self):
        return Blendermodellauftrag.objects.filter(pk=self.job.pk, status='angehalten').exists()

    def _schritt(self, name):
        if self.angehalten():
            raise self.Angehalten()
        self._band = self.BAENDER[name]
        self.job.schritt = name
        self.job.save(update_fields=['schritt', 'updated_at'])
        self.melden(0, name)

    def sichern(self, *felder):
        self.job.save(update_fields=list(felder) + ['updated_at'])

    def melden(self, anteil, text):
        """Fortschritt im Band des Schritts — höchstens zweimal je Sekunde in die Datenbank."""
        jetzt = time.monotonic()
        if jetzt - self._letzte_db < 0.5 and anteil < 1.0:
            return
        self._letzte_db = jetzt
        von, bis = self._band
        self.job.progress = max(self.job.progress or 0, int(von + (bis - von) * max(0.0, min(1.0, anteil))))
        self.job.progress_detail = str(text)[:200]
        self.sichern('progress', 'progress_detail')

    def _scheitern(self, text):
        job = self.job
        job.refresh_from_db()
        if job.status == 'angehalten':
            return
        job.status = 'gescheitert'
        job.error_message = text[:4000]
        job.finished_at = timezone.now()
        job.save(update_fields=['status', 'error_message', 'finished_at', 'updated_at'])

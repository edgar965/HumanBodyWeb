# -*- coding: utf-8 -*-
"""Haarenginelauf — ein Auftrag „Haar Engine": Grundfigur → Iterationen → Figur mit Rig → Film
(30.09.2026).

DIES IST DIE PIPELINE DES BEREICHS — die Datei, in der gebaut wird. Alles, was um sie herum steht (Seite,
Tabelle, Fotoauswahl, Neu berechnen, Umbenennen, Duplizieren, Bühne, Export), fragt nur: Welche Schritte
gibt es (`SCHRITTE`), in welchem Band des Balkens läuft jeder (`BAENDER`), und was steht danach in
`job.ergebnis`? Ein Schritt ist eine Zeile in `schrittfolge()`.

Kopie von `Blendermodelllauf`, mit der Genesis Haar Engine (`Genesishaarengine`) statt Blender:

    grundfigur   Genesis-9-Grundfigur (Option „Grundfigur") mit Rig, Stellung für Bühne und Export
    iterationen  die Iterationen: Runden aus Optimierer + lokaler Prüf-KI gegen die Vorlagenbilder (`Iterationskreislauf`)
    export       die Figur als GLB mit Rig (`Haarengineexport`)
    film         BVH retargeten, die Engine rendert den Film (`Haarenginefilm`; ohne BVH übersprungen)
    speichern    Ablage in `output/Export/HaarEngine` (`Haarenginespeichern`)

`ausfuehren(ab, bis)`: „Neu berechnen" beginnt beim gewählten Schritt; „Weiter iterieren" rechnet NUR
„iterationen" (`ab = bis = 'iterationen'`) — der Film dauert Minuten und zeigt das Haar erst nach den
Iterationen.

Solange die Engine nicht angebunden ist, endet der Lauf im Schritt „iterationen" mit ihrer Meldung
(`Genesishaarengine.NichtAngebunden`); die Grundfigur davor ist gerechnet und steht auf der Bühne.
"""

import logging
import time

from django.utils import timezone

from ..daten.haarengineablage import Haarengineablage
from ..models import Haarengineauftrag
from .haarengineoptionen import Haarengineoptionen

logger = logging.getLogger('core')

__all__ = ['Haarenginelauf']


class Haarenginelauf:
    SCHRITTE = ('netz', 'koerper', 'grundfigur', 'iterationen', 'export', 'film', 'speichern')
    #: Anteil am Balken 0…100 — Netz (TRELLIS) und Iterationen sind die langen Teile.
    BAENDER = {
        'netz': (0, 25),
        'koerper': (25, 40),
        'grundfigur': (40, 43),
        'iterationen': (43, 85),
        'export': (85, 88),
        'film': (88, 98),
        'speichern': (98, 100),
    }
    WARTET = 'wartet'

    class Angehalten(Exception):
        """Der Nutzer hat angehalten — kein Fehler, der Lauf endet still."""

    def __init__(self, job_id):
        self.job = Haarengineauftrag.objects.get(pk=job_id)
        self.ablage = Haarengineablage(self.job.kennung)
        #: Die Optionen der Figur (`basis`, `modell` — `Haarenginespeichern` liest sie wie `Meshfigurspeichern`).
        self.optionen = Haarengineoptionen.figur(self.job.optionen)
        self._band = (0, 100)
        self._letzte_db = 0.0

    # --------------------------------------------------------------- Ablauf

    def schrittfolge(self):
        """Schritt → was er tut. Hier wird die Pipeline zusammengesteckt."""
        from .haarengineexport import Haarengineexport
        from .haarenginefilm import Haarenginefilm
        from .haarenginegrundfigur import Haarenginegrundfigur
        from .haarenginekoerper import Haarenginekoerper
        from .haarenginenetz import Haarenginenetz
        from .haarenginespeichern import Haarenginespeichern
        from .iterationskreislauf import Iterationskreislauf

        return {
            'netz': lambda: Haarenginenetz(self).ausfuehren(),
            'koerper': lambda: Haarenginekoerper(self).ausfuehren(),
            'grundfigur': lambda: Haarenginegrundfigur(self).ausfuehren(),
            'iterationen': lambda: Iterationskreislauf(self).ausfuehren(),
            'export': lambda: Haarengineexport(self).ausfuehren(),
            'film': lambda: Haarenginefilm(self).ausfuehren(),
            'speichern': lambda: Haarenginespeichern(self).ausfuehren(),
        }

    def ausfuehren(self, ab=None, bis=None):
        job = self.job
        self.ablage.anlegen()
        job.ergebnis = dict(job.ergebnis or {})
        start = self.SCHRITTE.index(ab) if ab in self.SCHRITTE else 0
        ende = self.SCHRITTE.index(bis) + 1 if bis in self.SCHRITTE else len(self.SCHRITTE)
        if start > self.SCHRITTE.index('grundfigur') and not self.ablage.arbeit('grundkoerper.glb').is_file():
            self._scheitern('Keine Grundfigur — erst den Schritt „Grundfigur" rechnen')
            return
        if start == 0:
            # Sonst stünden die Dauern früherer Läufe weiter im Ergebnis.
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
            logger.info('Haar Engine %s: angehalten', job.kennung)
            return
        except Exception as fehler:  # noqa: BLE001 — jeder Fehler beendet den Lauf sichtbar
            logger.exception('Haar Engine %s: Schritt %s gescheitert', job.kennung, job.schritt)
            self._scheitern('%s: %s' % (job.schritt, fehler))
            return
        job.ergebnis['dauer_s'] = round(time.perf_counter() - t0, 1)
        # Begutachtung (Edgar, 30.09.2026): Endet der Lauf mit den Iterationen, wartet der Auftrag auf das nächste
        # Rezept — sichtbar als eigener Status, nicht als „fertig".
        wartet = (bis == 'iterationen' and (job.ergebnis.get('begutachtung') or {}).get('zustand') == self.WARTET)
        job.status = self.WARTET if wartet else 'fertig'
        job.progress = 100
        job.progress_detail = 'Wartet auf Begutachtung' if wartet else 'Fertig'
        job.finished_at = timezone.now()
        job.save(
            update_fields=['ergebnis', 'status', 'progress', 'progress_detail', 'finished_at', 'updated_at']
        )
        logger.info('2D3D Kleider %s: %s in %.0f s', job.kennung, job.status, job.ergebnis['dauer_s'])

    def angehalten(self):
        return Haarengineauftrag.objects.filter(pk=self.job.pk, status='angehalten').exists()

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

# -*- coding: utf-8 -*-
"""Engine2d3dKleiderlauf — ein Auftrag „2D3D Kleider": Grundfigur → Iterationen → Figur mit Rig → Film
(30.09.2026).

DIES IST DIE PIPELINE DES BEREICHS — die Datei, in der gebaut wird. Alles, was um sie herum steht (Seite,
Tabelle, Fotoauswahl, Neu berechnen, Umbenennen, Duplizieren, Bühne, Export), fragt nur: Welche Schritte
gibt es (`SCHRITTE`), in welchem Band des Balkens läuft jeder (`BAENDER`), und was steht danach in
`job.ergebnis`? Ein Schritt ist eine Zeile in `schrittfolge()`.

Kopie von `Blendermodelllauf`, mit der Genesis-Engine (`Genesisengine2d3dkleider`) statt Blender:

    vorbereitung die Fotos aufbereiten: Hintergrund entfernen, auf Wunsch den Körper senkrecht stellen, Zuschnitt, Licht
                 (`Engine2d3dKleidervorbereitung`, 03.10.2026; getrennt startbar, die Seite zeigt die Ergebnisse unter den Fotos)
    netz         Fotos → Netz (TRELLIS.2/Pixal3D), nimmt die vorbereiteten Fotos, wenn sie zu den Optionen passen
    kopf         OPTIONAL (Häkchen `kopf.rechnen`, Vorgabe an; ausdrücklich gestartet läuft er immer): der Kopf aus den drei vorbereiteten Fotos geschnitten und als eigenes Kopfnetz gerechnet
                 (Hunyuan3D, `Engine2d3dKleiderkopf`, 07.10.2026); der Schritt „koerper" setzt es für das Gesicht ein
    segmentierung OPTIONAL (Option `segmentierung.verwenden`, ausdrücklich gestartet läuft er immer): Sapiens zerlegt die vorbereiteten Fotos in Oberteil, Hose, Socken/Schuhe, Zubehör und
                 Haut und legt die Etiketten auf die Flächen des Netzes (`Engine2d3dKleidersegmentierung`, 04.10.2026); der Schritt „kleidung" der Körper-Kette nimmt sie für die Kleidungsmaske
    grundfigur   Genesis-9-Grundfigur (Option „Grundfigur") mit Rig, Stellung für Bühne und Export
    kleiderstuecke die Kleidung des Netzes als eigene Genesis-Stücke (Oberteil, Hose, Socken: `Fotostuecke`) VOR den Iterationen bauen und messen (`Kleiderstuecknote`), die Bühne trägt sie
                 schon vor Runde 1 (`Engine2d3dKleiderstuecke`, 04.10.2026)
    iterationen die Iterationen: Runden aus Optimierer + lokaler Prüf-KI gegen die Vorlagenbilder (`Iterationskreislauf`)
    export       die Figur als GLB mit Rig (`Engine2d3dKleiderexport`)
    film         BVH retargeten, die Engine rendert den Film (`Engine2d3dKleiderfilm`; ohne BVH übersprungen)
    speichern    Ablage in `output/Export/Engine2d3dKleider` (`Engine2d3dKleiderspeichern`)

`ausfuehren(ab, bis)`: „Neu berechnen" beginnt beim gewählten Schritt; „Weiter iterieren" rechnet NUR
„iterationen" (`ab = bis = 'iterationen'`) — der Film dauert Minuten und zeigt das Haar erst nach den
Iterationen.

Solange die Engine nicht angebunden ist, endet der Lauf im Schritt „iterationen" mit ihrer Meldung
(`Genesisengine2d3dkleider.NichtAngebunden`); die Grundfigur davor ist gerechnet und steht auf der Bühne.
"""

import logging
import time

from django.utils import timezone

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from ..models import Engine2d3dKleiderauftrag
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderlauf']


class Engine2d3dKleiderlauf:
    SCHRITTE = ('vorbereitung', 'netz', 'kopf', 'segmentierung', 'koerper', 'grundfigur', 'kleiderstuecke', 'iterationen', 'export', 'film', 'speichern')
    #: Anteil am Balken 0…100 — Netz (TRELLIS), Kopf (Hunyuan) und Iterationen sind die langen Teile.
    BAENDER = {
        'vorbereitung': (0, 3),
        'netz': (3, 17),
        'kopf': (17, 24),
        'segmentierung': (24, 27),
        'koerper': (27, 40),
        'grundfigur': (40, 43),
        'kleiderstuecke': (43, 47),
        'iterationen': (47, 85),
        'export': (85, 88),
        'film': (88, 98),
        'speichern': (98, 100),
    }
    WARTET = 'wartet'

    class Angehalten(Exception):
        """Der Nutzer hat angehalten — kein Fehler, der Lauf endet still."""

    def __init__(self, job_id):
        self.job = Engine2d3dKleiderauftrag.objects.get(pk=job_id)
        self.ablage = Engine2d3dKleiderablage(self.job.kennung)
        #: Die Optionen der Figur (`basis`, `modell` — `Engine2d3dKleiderspeichern` liest sie wie `Meshfigurspeichern`).
        self.optionen = Engine2d3dKleideroptionen.figur(self.job.optionen)
        self._band = (0, 100)
        self._letzte_db = 0.0
        #: Der Schritt, bei dem dieser Lauf einsetzt (`ausfuehren(ab=…)`) — ein OPTIONALER Schritt (`segmentierung`) läuft, wenn er so gewählt ist, auch bei Option „aus".
        self.ab = None

    # --------------------------------------------------------------- Ablauf

    def schrittfolge(self):
        """Schritt → was er tut. Hier wird die Pipeline zusammengesteckt."""
        from .engine2d3dkleiderexport import Engine2d3dKleiderexport
        from .engine2d3dkleiderfilm import Engine2d3dKleiderfilm
        from .engine2d3dkleidergrundfigur import Engine2d3dKleidergrundfigur
        from .engine2d3dkleiderkoerper import Engine2d3dKleiderkoerper
        from .engine2d3dkleiderkopf import Engine2d3dKleiderkopf
        from .engine2d3dkleidernetz import Engine2d3dKleidernetz
        from .engine2d3dkleiderstuecke import Engine2d3dKleiderstuecke
        from .engine2d3dkleidersegmentierung import Engine2d3dKleidersegmentierung
        from .engine2d3dkleiderspeichern import Engine2d3dKleiderspeichern
        from .engine2d3dkleidervorbereitung import Engine2d3dKleidervorbereitung
        from .iterationskreislauf import Iterationskreislauf

        return {
            'vorbereitung': lambda: Engine2d3dKleidervorbereitung(self).ausfuehren(),
            'netz': lambda: Engine2d3dKleidernetz(self).ausfuehren(),
            'kopf': lambda: Engine2d3dKleiderkopf(self).ausfuehren(),
            'segmentierung': lambda: Engine2d3dKleidersegmentierung(self).ausfuehren(),
            'koerper': lambda: Engine2d3dKleiderkoerper(self).ausfuehren(),
            'grundfigur': lambda: Engine2d3dKleidergrundfigur(self).ausfuehren(),
            'kleiderstuecke': lambda: Engine2d3dKleiderstuecke(self).ausfuehren(),
            'iterationen': lambda: Iterationskreislauf(self).ausfuehren(),
            'export': lambda: Engine2d3dKleiderexport(self).ausfuehren(),
            'film': lambda: Engine2d3dKleiderfilm(self).ausfuehren(),
            'speichern': lambda: Engine2d3dKleiderspeichern(self).ausfuehren(),
        }

    def ausfuehren(self, ab=None, bis=None):
        job = self.job
        self.ablage.anlegen()
        job.ergebnis = dict(job.ergebnis or {})
        self.ab = ab if ab in self.SCHRITTE else None
        start = self.SCHRITTE.index(ab) if ab in self.SCHRITTE else 0
        ende = self.SCHRITTE.index(bis) + 1 if bis in self.SCHRITTE else len(self.SCHRITTE)
        if start > self.SCHRITTE.index('grundfigur') and not self.ablage.arbeit('grundkoerper.glb').is_file():
            self._scheitern('Keine Grundfigur — erst den Schritt „Grundfigur" rechnen')
            return
        # Die Dauern der Schritte, die jetzt rechnen, stünden sonst von früheren Läufen weiter im Ergebnis; die der
        # anderen bleiben (02.10.2026: Einzelne Schritte laufen getrennt — „nur Mesh" darf die Schritte „Körper" bis
        # „Speichern" nicht auf „offen" zurücksetzen).
        dauer = dict(job.ergebnis.get('dauer') or {})
        for name in self.SCHRITTE[start:ende]:
            dauer.pop(name, None)
        job.ergebnis['dauer'] = dauer
        schritte = self.schrittfolge()
        t0 = time.perf_counter()
        try:
            for name in self.SCHRITTE[start:ende]:
                self._schritt(name)
                self._runden_beiseite(name)
                t = time.perf_counter()
                schritte[name]()
                job.ergebnis.setdefault('dauer', {})[name] = round(time.perf_counter() - t, 1)
                self.sichern('ergebnis')
        except self.Angehalten:
            logger.info('2D3D Kleider %s: angehalten', job.kennung)
            return
        except Exception as fehler:  # noqa: BLE001 — jeder Fehler beendet den Lauf sichtbar
            logger.exception('2D3D Kleider %s: Schritt %s gescheitert', job.kennung, job.schritt)
            self._scheitern('%s: %s' % (job.schritt, fehler))
            return
        self._standmodell(self.SCHRITTE[start:ende])
        job.ergebnis['dauer_s'] = round(time.perf_counter() - t0, 1)
        # Begutachtung (Edgar, 30.09.2026): Endet der Lauf mit den Iterationen, wartet der Auftrag auf das nächste
        # Rezept — sichtbar als eigener Status, nicht als „fertig".
        wartet = (bis == 'iterationen' and (job.ergebnis.get('begutachtung') or {}).get('zustand') == self.WARTET)
        job.status = self.WARTET if wartet else 'fertig'
        job.progress = 100
        kreis = job.ergebnis.get('kreislauf') or {}
        beste = ' · beste Runde %s, Note %.4f' % (kreis['runde_bester'], float((kreis.get('note') or {}).get(
            'gesamt') or 0)) if bis == 'iterationen' and kreis.get('runde_bester') else ''
        # Ein Lauf, der vor dem Ende aufhört (02.10.2026: Schritte einzeln starten), sagt es — „Fertig" allein täte so,
        # als wäre der Auftrag durch.
        teil = ' — nur bis „%s"' % bis if bis in self.SCHRITTE and ende < len(self.SCHRITTE) and bis != 'iterationen' \
            else ''
        job.progress_detail = 'Wartet auf Begutachtung' if wartet else 'Fertig' + beste + teil
        job.finished_at = timezone.now()
        job.save(
            update_fields=['ergebnis', 'status', 'progress', 'progress_detail', 'finished_at', 'updated_at']
        )
        logger.info('2D3D Kleider %s: %s in %.0f s', job.kennung, job.status, job.ergebnis['dauer_s'])

    def _runden_beiseite(self, name):
        """Rechnet ein Schritt Fotos, Netz oder Körper neu (`Iterationsarchiv.VERALTET`), gehen die Runden vorher ins Archiv (06.10.2026): ihre Noten gelten für ein anderes Netz, die neue Iteration 0 darf nicht gegen sie
        antreten. Beim zweiten solchen Schritt desselben Laufs gibt es nichts mehr wegzulegen."""
        from .iterationsarchiv import Iterationsarchiv
        if Iterationsarchiv.veraltet_durch(name) and Iterationsarchiv(self.job, self.ablage).beiseite('Schritt „%s“ neu gerechnet' % name):
            self.sichern('ergebnis')

    @staticmethod
    def _von_hand(job, gelaufen):
        """Gehören die Iterationen zu diesem Lauf, und werden sie von Hand gesteuert (Modus „Begutachtung": je Rezept ein Lauf mit einer oder n Runden, danach wartet der Auftrag)?"""
        if 'iterationen' not in gelaufen:
            return False
        from .iterationsoptionen import Iterationsoptionen
        o = Iterationsoptionen.pruefen((getattr(job, 'optionen', None) or {}).get('iterationen'))
        return o.get('modus') == Iterationsoptionen.BEGUTACHTUNG

    def _standmodell(self, gelaufen):
        """Das 3D-Modell des letzten Stands für die Bühne (`Engine2d3dKleiderstandmodell`, 01.10.2026) — nach jedem Lauf, der
        die Figur geändert hat, und nach dem Ende der letzten Runde, wenn die Iterationen von Hand gesteuert werden. Ein Fehler hält den Lauf nicht auf: die Bühne baut die Figur dann im Browser."""
        # Edgar 04.10.2026: „bau das Modell IMMER nach dem Beenden der letzten Iteration, wenn die Iterationen manuell gesteuert werden" — einmal am Ende des Laufs, nicht je Runde eines
        # Laufs mit n Runden. Der automatische Modus baut weiter nicht (20 s je Lauf, Edgar 02.10.2026 „eine Runde muss 2–3 s dauern"): die Bühne bestellt es beim Öffnen der Seite
        # (`Engine2d3dKleiderstandbestellung`).
        figur = {'koerper', 'grundfigur', 'kleiderstuecke'} & set(gelaufen)
        if not figur and not Engine2d3dKleiderlauf._von_hand(self.job, gelaufen):
            return
        from .engine2d3dkleiderstandmodell import Engine2d3dKleiderstandmodell
        from .standbewegung import Standbewegung
        # Die Bewegung der BVH auf der Figur (Play der Bühne) braucht den Film-Schritt nicht (`Standbewegung`, 04.10.2026) — ein Fehler hält den Lauf auch hier nicht auf. Sie hängt nur an der Stellung
        # des Auftrags und der BVH, nicht an den Runden: nach Runden gibt es nichts neu zu rechnen.
        try:
            if figur:
                self.melden(1.0, 'Bewegung auf der Figur')
                if Standbewegung(self.job, self.ablage).sichern():
                    self.sichern('ergebnis')
        except Exception:  # noqa: BLE001 — ohne Bewegung fehlt nur Play
            logger.exception('2D3D Kleider %s: Bewegung der Figur nicht gerechnet', self.job.kennung)
        stand = Engine2d3dKleiderstandmodell(self.job, self.ablage)
        try:
            self.melden(1.0, 'Modell des letzten Stands für die Bühne')
            stand.bauen()
        except Exception as fehler:  # noqa: BLE001 — siehe Docstring
            logger.exception('2D3D Kleider %s: Modell des Stands nicht gebaut', self.job.kennung)
            stand.scheitern(fehler)

    def angehalten(self):
        return Engine2d3dKleiderauftrag.objects.filter(pk=self.job.pk, status='angehalten').exists()

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

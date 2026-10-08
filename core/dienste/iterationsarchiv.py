# -*- coding: utf-8 -*-
"""Iterationsarchiv — die Runden eines Auftrags beiseitelegen, wenn ein Schritt vor den Iterationen NEU rechnet (06.10.2026).

Gemessen am Lauf `2026.10.06.14.10.22` (Kopie von „Edgar -best", voller Neulauf ab „Vorbereitung"): Das Netz, der Körper und die Kleiderstücke waren neu, aber `ergebnis.iterationen` und `ergebnis.kreislauf`
trugen noch Runde 0 und 1 der Quelle. Die neue Iteration 0 wurde Runde 2 (Gesamtnote 0,3975), die `Rundenauswahl` verglich sie mit der besten Runde der Quelle (Runde 1, 0,3516 — Note eines anderen Netzes) und verwarf
sie; jede weitere Runde ginge vom Modell der alten Runde 1 aus und müsste dieselbe Zahl unterbieten. Die Note eines anderen Netzes ist kein Maßstab (Gesicht, Haar und Umriss hängen am Netz).

Rechnet einer der Schritte in `VERALTET` (er erzeugt die Fotos, das Netz oder die Figur neu, gegen die die Runden gerechnet sind), legt `beiseite` die Runden weg, BEVOR er anfängt:
  * `ergebnis.iterationen`, `ergebnis.kreislauf` und `ergebnis.begutachtung` gehen als `iterationen/frueher/<Zeitstempel>/ergebnis.json` in eine Datei (die Zeile im Auftrag bleibt klein);
  * die Dateien der Runden (`iterationen/runde_*`: Tafeln, Kopfbilder, Renders, Formbezug) ziehen in denselben Ordner — Iteration 0 heißt immer Runde 0 und überschriebe sie sonst;
  * `ergebnis.fruehere_runden` führt eine Zeile je Archiv (Zeit, Grund, Zahl der Runden, beste Runde und Note, Ordner).
Nichts wird gelöscht. Der Lauf beginnt danach wie bei einem neuen Auftrag: erst Iteration 0 aus dem Startrezept (`Begutachtungsausgang`), dann die Runden.

Nicht in `VERALTET`: „Segmentierung" (ihre Etiketten wirken erst, wenn „Körper" neu rechnet), „Grundfigur" und „Kleiderstücke" (sie leiten sich aus Körper und Netz ab; ein einzelner Lauf zum Messen soll die Runden nicht wegräumen — Fassung
und Stücke bleiben, solange Netz, Maske und Figur gleich bleiben), „Iterationen" selbst (Edgars „weiter iterieren"), „Export", „Film", „Speichern". Ein Lauf, der nur „Grundfigur" oder „Kleiderstücke" neu rechnet, nachdem sich ihre Eingaben
geändert haben, wird davon nicht erfasst — das ist offen und nicht gemessen.
Nicht gebaut: eine Oberfläche, die die frühere Folge zeigt oder zurückholt (Zurückholen = Ordner und `ergebnis.json` lesen, Dateien zurückziehen).
"""

import logging
import shutil

from django.utils import timezone

from ..atomic_write import AtomarSchreiber

logger = logging.getLogger('core')

__all__ = ['Iterationsarchiv']


class Iterationsarchiv:
    #: Schritte, die Fotos, Netz oder Figur NEU erzeugen — nach ihnen gelten die Noten der alten Runden nicht mehr.
    VERALTET = ('vorbereitung', 'netz', 'koerper')
    #: Was in `job.ergebnis` zu den Runden gehört.
    SCHLUESSEL = ('iterationen', 'kreislauf', 'begutachtung')
    ORDNER = 'frueher'
    DATEI = 'ergebnis.json'
    #: Dateien der Runden im Ordner `iterationen/` (nicht die Unterordner wie `nachbesserung/`).
    MUSTER = 'runde_*'

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage

    @classmethod
    def veraltet_durch(cls, name):
        """True, wenn der Schritt `name` die Runden eines Auftrags überholt."""
        return name in cls.VERALTET

    def hat_runden(self):
        """Gibt es etwas wegzulegen — gerechnete Runden oder einen gemerkten Stand der Iterationen?"""
        ergebnis = self.job.ergebnis or {}
        return bool(ergebnis.get('iterationen') or (ergebnis.get('kreislauf') or {}).get('modell'))

    def _zusammenfassung(self, stempel, grund):
        ergebnis = self.job.ergebnis
        kreislauf = ergebnis.get('kreislauf') or {}
        return {
            'am': timezone.localtime().strftime('%Y-%m-%d %H:%M:%S'),
            'grund': grund,
            'runden': len(ergebnis.get('iterationen') or []),
            'beste': kreislauf.get('runde_bester'),
            'gesamt': (kreislauf.get('note') or {}).get('gesamt'),
            'ordner': '%s/%s' % (self.ORDNER, stempel),
        }

    def _dateien_ziehen(self, ziel):
        """Die `runde_*`-Dateien nach `ziel` — verschoben, nicht kopiert; eine gesperrte (wird gerade ausgeliefert) bleibt liegen und wird gemeldet."""
        ziel.mkdir(parents=True, exist_ok=True)
        gezogen = 0
        for datei in sorted(self.ablage.iterationen().glob(self.MUSTER)):
            if not datei.is_file():
                continue
            try:
                shutil.move(str(datei), str(ziel / datei.name))
                gezogen += 1
            except OSError as fehler:
                logger.warning('2D3D Kleider %s: %s nicht ins Archiv verschoben: %s', self.job.kennung, datei.name, fehler)
        return gezogen

    def beiseite(self, grund):
        """Die Runden ins Archiv legen und aus `job.ergebnis` nehmen (Speichern ist Sache des Aufrufers) → die Zeile in `ergebnis.fruehere_runden`, None ohne Runden."""
        if not self.hat_runden():
            return None
        ergebnis = self.job.ergebnis
        stempel = timezone.localtime().strftime('%Y%m%d_%H%M%S')
        ziel = self.ablage.iterationen(self.ORDNER) / stempel
        zeile = self._zusammenfassung(stempel, grund)
        # Erst die Datei mit dem Stand, dann erst aus dem Ergebnis nehmen: scheitert das Schreiben, bleibt alles, wie es war.
        ziel.mkdir(parents=True, exist_ok=True)
        AtomarSchreiber.json_schreiben(ziel / self.DATEI, {'zeile': zeile, **{k: ergebnis.get(k) for k in self.SCHLUESSEL}}, einzug=1)
        zeile['dateien'] = self._dateien_ziehen(ziel)
        for schluessel in self.SCHLUESSEL:
            ergebnis.pop(schluessel, None)
        ergebnis['fruehere_runden'] = list(ergebnis.get('fruehere_runden') or []) + [zeile]
        logger.info('2D3D Kleider %s: %d Runden beiseitegelegt (%s, beste Runde %s, Note %s) → %s', self.job.kennung, zeile['runden'], grund,
                    zeile['beste'], zeile['gesamt'], ziel)
        return zeile

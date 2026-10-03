# -*- coding: utf-8 -*-
"""Iterationsloeschung — Runden aus der Tabelle „Iterationen" löschen (einzeln oder viele auf einmal).

Gelöscht wird der Eintrag in `ergebnis['iterationen']` und alles, was zu ihm gehört: Vergleichstafel,
Renders je Blickwinkel, Modell-GLB (`dateien`, `je_ansicht[].render`). Die Kurve
(`ergebnis['kreislauf']['verlauf']`) und der beste Wertesatz bleiben — sie sind Geschichte bzw. Stand des
Kreislaufs, kein Anzeigestück.

Während eines Laufs schreibt NUR der Lauf in `ergebnis`: Er hält es minutenlang im Speicher und würde eine
Löschung der Seite bei der nächsten Runde wieder wegspeichern (dieselbe Falle wie
`Engine2d3dKleiderauftrag.bilder_sichern`). Die Seite legt deshalb eine Liste an (`arbeit/rundenloeschen.json`),
und der Lauf arbeitet sie zu Beginn jeder Runde ab (`Iterationskreislauf`). Ohne Lauf arbeitet der Endpunkt
sie selbst ab.
"""

import json
import logging
from pathlib import Path

from ..atomic_write import AtomarSchreiber
from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage

logger = logging.getLogger('core')

__all__ = ['Iterationsloeschung']


class Iterationsloeschung:
    LISTE = 'rundenloeschen.json'

    def __init__(self, job):
        self.job = job
        self.ablage = Engine2d3dKleiderablage(job.kennung)

    def _pfad(self):
        return self.ablage.arbeit(self.LISTE)

    def vorgemerkt(self):
        """Die Rundennummern, die auf das Löschen warten."""
        try:
            with open(self._pfad(), encoding='utf-8') as f:
                return sorted({int(n) for n in json.load(f)})
        except OSError, ValueError, TypeError:
            return []

    def vormerken(self, runden):
        """→ alle vorgemerkten Runden (die neuen zu den schon wartenden)."""
        alle = sorted(set(self.vorgemerkt()) | {int(n) for n in runden})
        self.ablage.arbeit().mkdir(parents=True, exist_ok=True)
        AtomarSchreiber.json_schreiben(self._pfad(), alle)
        return alle

    def abarbeiten(self):
        """Die vorgemerkten Runden löschen: Einträge aus `job.ergebnis` (im Speicher — Speichern ist Sache des
        Aufrufers) und ihre Dateien. → die gelöschten Rundennummern."""
        vorgemerkt = set(self.vorgemerkt())
        if not vorgemerkt:
            return []
        eintraege = (self.job.ergebnis or {}).get('iterationen') or []
        weg = [e for e in eintraege if e.get('runde') in vorgemerkt]
        for eintrag in weg:
            self._dateien_loeschen(eintrag)
        self.job.ergebnis['iterationen'] = [e for e in eintraege if e.get('runde') not in vorgemerkt]
        self._pfad().unlink(missing_ok=True)
        return sorted(e['runde'] for e in weg)

    def _dateien_loeschen(self, eintrag):
        namen = {str(v) for v in (eintrag.get('dateien') or {}).values()}
        for a in eintrag.get('je_ansicht') or []:
            if isinstance(a, dict):
                namen |= {str(a[k]) for k in ('render',) if a.get(k)}
        for name in namen:
            if Path(name).name != name:  # nie aus dem Ordner „iterationen" heraus
                logger.warning(
                    '2D3D Kleider %s: Dateiname %r der Runde %s übergangen',
                    self.job.kennung,
                    name,
                    eintrag.get('runde'),
                )
                continue
            try:
                self.ablage.iterationen(name).unlink(missing_ok=True)
            except OSError as fehler:  # gesperrt (wird gerade ausgeliefert): der Eintrag geht trotzdem
                logger.warning('2D3D Kleider %s: %s nicht gelöscht: %s', self.job.kennung, name, fehler)

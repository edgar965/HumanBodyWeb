# -*- coding: utf-8 -*-
"""Aufloesungsstufe — mit welcher Auflösung eine Runde von „2D3D Kleider" benotet wird (02.10.2026).

Edgar: „die Zwischenergebnisse sollen in höherer Auflösung gemacht werden. Vielleicht Auflösung inkrementell, am
Anfang der Iterationen kleinere Auflösung, und wenn nicht genügend Details vorhanden sind für Verbesserung, höhere
Auflösung … immer höher bis zur maximalen Auflösung, in der die Vorlagen vorhanden sind."

    Start         `iterationen.bildbreite` (Vorgabe 128 px Breite, Höhe × 1,5)
    höher         × 2, sobald `iterationen.stufe_stillstand` Runden der Stufe nacheinander nichts verbessert haben
                  ODER die Automatik aus der besten Runde keine Änderung mehr findet (bisher endete dort der Lauf)
    höchstens     die Auflösung, in der die Figur auf den Farbfotos vorliegt: Figurhöhe in Pixeln im freigestellten
                  Foto, umgerechnet auf die Fläche von `Iterationsbild` — darüber hinaus erfände das Hochrechnen der
                  Vorlage nur Unschärfe. Das kleinste der Farbfotos begrenzt.

Bei jedem Wechsel ist die nächste Runde eine MESSRUNDE: kein Rezept, die beste Runde wird in der neuen Stufe neu
benotet und ist die neue Bezugsnote (`Begutachtungsstand`) — eine Note auf 512 px ist mit einer auf 128 px nicht
vergleichbar. Die Farbnote wächst mit (`Iterationsnote.felder`: 8 × 12 Felder je 128 × 192), sonst sähe sie auch bei
hoher Auflösung nur Flächenmittel.

Zustand im Kreislauf: `aufloesung` (Breite der Stufe), `aufloesung_seit` (erste Runde der Stufe), `aufloesung_max`,
`aufloesung_verlauf` [[runde, breite, grund]].
"""

import logging

import numpy as np
from PIL import Image

from .iterationsbild import Iterationsbild
from .iterationsreferenz import Iterationsreferenz

logger = logging.getLogger('core')

__all__ = ['Aufloesungsstufe']


class Aufloesungsstufe:
    START = 128
    FAKTOR = 2
    STILLSTAND = 3

    def __init__(self, job, ablage, optionen):
        self.job, self.ablage = job, ablage
        self.start = int((optionen or {}).get('bildbreite') or self.START)
        self.stillstand_runden = int((optionen or {}).get('stufe_stillstand') or self.STILLSTAND)
        self._vorlagen = {}

    # ------------------------------------------------------------------ Stufe

    def breite(self, z):
        return int(z.get('aufloesung') or self.start)

    @staticmethod
    def groesse(breite):
        return int(breite), int(round(breite * 1.5))

    def hoechste(self, z, referenzen):
        """Die größte Breite, in der alle Farbfotos die Figur ohne Hochrechnen zeigen (gemerkt im Kreislauf)."""
        if z.get('aufloesung_max'):
            return int(z['aufloesung_max'])
        breiten = []
        for r in [r for r in referenzen if r.farbe] or list(referenzen):
            try:
                hoehe = self._figurhoehe(r.datei)
            except OSError as fehler:
                logger.warning('Auflösungsstufe: %s nicht lesbar (%s)', r.datei, fehler)
                continue
            if hoehe:
                breiten.append(int(hoehe / (1.0 - 2.0 * Iterationsbild.RAND) / 1.5))
        z['aufloesung_max'] = max(self.start, min(breiten)) if breiten else self.start
        return int(z['aufloesung_max'])

    def naechste(self, z, referenzen):
        """Die Breite der nächsten Stufe oder None (schon die höchste)."""
        jetzt, oben = self.breite(z), self.hoechste(z, referenzen)
        if jetzt >= oben:
            return None
        return min(jetzt * self.FAKTOR, oben)

    def stillstand(self, z):
        """Runden der laufenden Stufe in Folge ohne „besser" (die Messrunde zählt nicht)."""
        seit = int(z.get('aufloesung_seit') or 0)
        zaehler = 0
        for e in reversed(self.job.ergebnis.get('iterationen') or []):
            if int(e.get('runde') or 0) <= seit:
                break
            if (e.get('auswahl') or {}).get('aktion') == 'besser':
                break
            zaehler += 1
        return zaehler

    def faellig(self, z, referenzen):
        """Breite der nächsten Stufe, wenn die laufende stillsteht — sonst None."""
        if self.stillstand(z) < self.stillstand_runden:
            return None
        return self.naechste(z, referenzen)

    def steigen(self, z, neu, runde, grund):
        """Die Stufe wechseln; `runde` ist die Messrunde, die als erste in der neuen Stufe rechnet."""
        alt = self.breite(z)
        z.update(aufloesung=int(neu), aufloesung_seit=int(runde))
        z['aufloesung_verlauf'] = list(z.get('aufloesung_verlauf') or []) + [[int(runde), int(neu), grund]]
        logger.info('2D3D Kleider %s: Auflösung %d → %d px (%s)', self.job.kennung, alt, neu, grund)
        return '# Auflösung %d → %d px (%s): die beste Runde neu gemessen\n' % (alt, neu, grund)

    # --------------------------------------------------------------- Vorlagen

    def vorlage(self, referenz, breite):
        """Die Vorlage einer Referenz auf der Fläche der Stufe (je Lauf einmal gelesen)."""
        schluessel = (referenz.datei, int(breite))
        if schluessel not in self._vorlagen:
            if int(breite) == Iterationsbild.BREITE:
                self._vorlagen[schluessel] = referenz.bild
            else:
                self._vorlagen[schluessel] = Iterationsreferenz.bild(self.ablage, referenz.datei, self.groesse(breite))
        return self._vorlagen[schluessel]

    def _figurhoehe(self, datei):
        from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
        vorbereitet = self.ablage.unter(Engine2d3dKleiderablage.VORBEREITET) / (datei.rsplit('.', 1)[0] + '.png')
        if vorbereitet.is_file():
            with Image.open(vorbereitet) as bild:
                maske = np.asarray(bild.convert('RGBA'))[..., 3] > 127
        else:
            with Image.open(self.ablage.unter(Engine2d3dKleiderablage.EINGANG) / datei) as bild:
                rgb = np.asarray(bild.convert('RGB'), dtype=np.int32)
            maske = (765 - rgb.sum(axis=2)) > Iterationsbild.WEISS_SCHWELLE
        abbildung = Iterationsbild.abbildung(maske)
        return (abbildung[2] - abbildung[1]) if abbildung else 0

# -*- coding: utf-8 -*-
"""Iterationsreferenz — die Vorlagenbilder aus der Bildauswahl des Auftrags, je mit Blickwinkel und Gewicht.

Verwendet wird jedes Foto, dessen Rolle nicht „aus" ist und das ein Gewicht über 0 hat. Den Blickwinkel
(Grad ab vorn, positiv zur LINKEN Seite der Figur) nimmt es in dieser Reihenfolge:

    1. `winkel` am Foto — von Hand in den Eintrag der Bildauswahl gesetzt
    2. der Name der Schnittbilder eines Ansichtenbogens: `ansicht_<reihe>_<spalte>` (`BOGEN`, aus BlenderModel übernommen: Reihe 1
       vorn, rechte Seite, linke Seite, hinten; Reihe 2 vier Schrägen — gilt für einen Bogen dieser Art, NICHT für jeden; bei
       einem anderen Bogen die Tabelle prüfen)
    3. die Rolle: vorne 0, links 90, rechts −90, hinten 180

NICHT gemessen: Eine automatische Suche über die Umriss-Note schob in BlenderModel jede Seitenansicht an den
Rand ihres Suchfensters — die Note mag breitere Umrisse, sie findet den Blickwinkel nicht. Lieber ein
abgelesener Winkel als ein falsch gemessener. Ein Foto ohne Blickwinkel (Rolle „Automatisch", fremder Name)
wird ausgelassen und im Zustand genannt (`ergebnis['kreislauf']['ausgelassen']`). Ein ganzer Bogen gehört
NICHT dazu — er zeigt mehrere Figuren auf einmal; seine Rolle steht auf „aus".
"""

import re

from ..daten.haarengineablage import Haarengineablage
from .iterationsbild import Iterationsbild

__all__ = ['Iterationsreferenz']


class Iterationsreferenz:
    BOGEN = {'1_1': 0, '1_2': -90, '1_3': 90, '1_4': 180, '2_1': 35, '2_2': -45, '2_3': 135, '2_4': -135}
    ROLLEN = {'vorne': 0, 'links': 90, 'rechts': -90, 'hinten': 180}
    NAME = re.compile(r'ansicht_(\d_\d)', re.IGNORECASE)

    def __init__(self, datei, original, winkel, gewicht, bild):
        self.datei = datei
        self.original = original
        self.winkel = winkel
        self.gewicht = gewicht
        self.bild = bild

    @classmethod
    def winkel_von(cls, eintrag):
        """Grad oder None (siehe Kopf der Datei)."""
        if isinstance(eintrag.get('winkel'), (int, float)):
            return float(eintrag['winkel'])
        treffer = cls.NAME.search(str(eintrag.get('original') or eintrag.get('datei') or ''))
        if treffer and treffer.group(1) in cls.BOGEN:
            return float(cls.BOGEN[treffer.group(1)])
        if eintrag.get('rolle') in cls.ROLLEN:
            return float(cls.ROLLEN[eintrag['rolle']])
        return None

    @classmethod
    def laden(cls, job):
        """→ (referenzen, ausgelassen)."""
        ablage = Haarengineablage(job.kennung)
        aus, ausgelassen = [], []
        for eintrag in job.bilder or []:
            if eintrag.get('rolle') == 'aus' or float(eintrag.get('gewicht') or 0) <= 0:
                continue
            winkel = cls.winkel_von(eintrag)
            pfad = ablage.unter(Haarengineablage.EINGANG) / eintrag['datei']
            if winkel is None or not pfad.is_file():
                ausgelassen.append(eintrag.get('original') or eintrag['datei'])
                continue
            original = eintrag.get('original') or eintrag['datei']
            gewicht = float(eintrag.get('gewicht') or 100) / 100.0
            aus.append(cls(eintrag['datei'], original, winkel, gewicht, cls.bild(ablage, eintrag['datei'])))
        return aus, ausgelassen

    @staticmethod
    def bild(ablage, datei, groesse=None):
        """Das Vorlagenbild der Note: freigestellt aus dem Schritt „netz" (`vorbereitet/<name>.png`, Alpha = Figur),
        wenn es das gibt — ein Foto mit Zimmer dahinter ist sonst als Ganzes „Figur" (30.09.2026, Edgar - TEST: IoU
        0,32 gegen den Flur). Sonst das Foto selbst mit weißem Grund. `groesse` (Breite, Höhe): eine feinere Fläche
        als die der Note — die Fotoprojektion liest die Farbe mit 512 × 768."""
        vorbereitet = ablage.unter(Haarengineablage.VORBEREITET) / (datei.rsplit('.', 1)[0] + '.png')
        if vorbereitet.is_file():
            return Iterationsbild.aus_render(vorbereitet, groesse)
        return Iterationsbild.aus_vorlage(ablage.unter(Haarengineablage.EINGANG) / datei, groesse)

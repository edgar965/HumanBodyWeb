# -*- coding: utf-8 -*-
"""Kostuemreferenz — die Vorlagenbilder aus der Bildauswahl des Auftrags, je mit Blickwinkel und Gewicht.

Verwendet wird jedes Foto, dessen Rolle nicht „aus" ist und das ein Gewicht über 0 hat. Den Blickwinkel (Grad
ab vorn, positiv zur LINKEN Seite der Figur, wie `effekte/blender/kostuem/ansichten.py`) nimmt es in dieser
Reihenfolge:

    1. `winkel` am Foto — von Hand in den Eintrag der Bildauswahl gesetzt
    2. der Name der Schnittbilder des Ansichtenbogens (`vorlage_teilen.py`: `ansicht_<reihe>_<spalte>`),
       abgelesen am Bogen `Vorlage.jpeg` (29.09.2026): Reihe 1 vorn, rechte Seite, linke Seite, hinten;
       Reihe 2 die Schrägen vorn-links (35°), vorn-rechts (−45°), hinten-LINKS (135°), hinten-RECHTS (−135°)
       (Grade geschätzt). **Die beiden hinteren waren bis 30.09.2026 vertauscht** (`2_3` = −135, `2_4` = 135):
       Die IoU-Kurve des besten Modells über 24 Blickwinkel (`winkel_suche.py`) hat es gezeigt — `2_4` passt bei
       −135° mit 0,867 (zugewiesen: +135° mit 0,725), und der Stab steht in `2_3` links im Bild wie im Render bei
       +135°. Zwei von acht Ansichten arbeiteten gegeneinander, und die Fototextur klebte die Rückseiten auf die
       falsche Seite (verschmierte Farben).
    3. die Rolle: vorne 0, links 90, rechts −90, hinten 180

NICHT gemessen: Eine automatische Suche im ±40°-Fenster über die Umriss-Note hat am 29.09.2026 jede
Seitenansicht an den Fensterrand geschoben (−90° → −50°, 90° → 130°) — die Note mag breitere Umrisse, sie
findet den Blickwinkel nicht. Lieber ein abgelesener Winkel als ein falsch gemessener.

Ein Foto ohne Blickwinkel (Rolle „Automatisch", fremder Name) wird ausgelassen und im Zustand genannt
(`ergebnis['kostuem']['ausgelassen']`). Der ganze Bogen gehört NICHT dazu — er zeigt acht Figuren auf einmal;
seine Rolle steht auf „aus".
"""

import re

from ..daten.blendermodellablage import Blendermodellablage
from .kostuembild import Kostuembild

__all__ = ['Kostuemreferenz']


class Kostuemreferenz:
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
        ablage = Blendermodellablage(job.kennung)
        aus, ausgelassen = [], []
        for eintrag in job.bilder or []:
            if eintrag.get('rolle') == 'aus' or float(eintrag.get('gewicht') or 0) <= 0:
                continue
            winkel = cls.winkel_von(eintrag)
            pfad = ablage.unter(Blendermodellablage.EINGANG) / eintrag['datei']
            if winkel is None or not pfad.is_file():
                ausgelassen.append(eintrag.get('original') or eintrag['datei'])
                continue
            original = eintrag.get('original') or eintrag['datei']
            gewicht = float(eintrag.get('gewicht') or 100) / 100.0
            aus.append(cls(eintrag['datei'], original, winkel, gewicht, Kostuembild.aus_vorlage(pfad)))
        return aus, ausgelassen

# -*- coding: utf-8 -*-
"""Mesh3daitestexportquelle — die Exportleiste auf der Seite eines Tests von Mesh3D-AI (31.10.2026, `Exportleistequelle`).

Edgar: „mach mir die Buttons zum speichern des Modells in dem Bereich ‚Ganzer Körper‘, rechts unten … export als glb, obj, blend mit Checkbox mit oder ohne Animation“, „bitte auch pfad
für den Export vorbelegen“. Das Modell ist die Ausgabe der Seite als Genesis-Figur mit den Stücken der KI (`Mesh3daifigurbewegung`), gebaut im Browser.
Exportordner `output/Export/Mesh3DAI/<Name des Tests>` (wie MeshTo3D, BlenderModel, 2D3D Kleider — NICHT `3DObjects/modelsExport`: das ist die Jobliste von 2d-3d-AI);
Arbeitsordner `exportleiste/` im Ordner des Tests.
"""

import json
from pathlib import Path

from django.conf import settings

from .exportleistequelle import Exportleistequelle
from .mesh3dainame import Mesh3dainame
from .mesh3daitest import Mesh3daitest
from .modellexportziel import Modellexportziel

__all__ = ['Mesh3daitestexportquelle']


class Mesh3daitestexportquelle(Exportleistequelle):
    BEREICH = 'mesh3daitest'
    ORDNER = 'exportleiste'

    def __init__(self, kennung, ordner):
        super().__init__(kennung)
        self.ordner = Path(ordner)

    @classmethod
    def finden(cls, kennung):
        ordner = Mesh3daitest.pfad(kennung) or Mesh3daitest.angelegt(kennung)
        return cls(kennung, ordner) if ordner is not None else None

    def name(self):
        eigen = Mesh3dainame.lesen(self.ordner)
        if eigen:
            return eigen
        for datei in ('test.json', 'anlage.json'):
            try:
                return json.loads((self.ordner / datei).read_text(encoding='utf-8')).get('name') or self.kennung
            except (OSError, ValueError):
                continue
        return self.kennung

    def exportordner(self):
        return Path(settings.MESH3DAI_EXPORT_DIR) / Modellexportziel.name(self.name(), self.kennung)

    def arbeitsordner(self):
        return self.ordner / self.ORDNER

    def kollision(self):
        """Kapseln des Kostüm-Wegs (`Mesh3daitest.kapseln`, dieselben wie die Seite) und die Kinematik der Figur, in deren Ruhe sie stehen (`Mesh3daitest.form`) — oder None."""
        try:
            info = json.loads((self.ordner / 'test.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            info = {}
        g = Mesh3daitest.geschlecht(self.ordner, info)
        kapseln, form = Mesh3daitest.kapseln(self.ordner, g), Mesh3daitest.form(self.ordner, info, g)
        if not kapseln or not form:
            return None
        return kapseln, json.loads(form['kinematik'].read_text(encoding='utf-8'))['knochen']

    def kacheln(self):
        """Die Hautkacheln der KI dieses Tests (`haut_<g>/10xx.jpg`), wenn die Seite sie zeigt (`Mesh3daitesthaut.info`) — sonst bekam der Render die Daz-Haut der Grundfigur:
        Venus am 31.10.2026 mit fremdem Gesicht, einheitlichem Körperton und hellem Haaransatz (der Daz-Kopf hat unter dem Haar keine Haarfarbe; Edgar: „Haar hat Ansatz wie bei einer Perücke“)."""
        from .mesh3daitesthaut import Mesh3daitesthaut
        try:
            info = json.loads((self.ordner / 'test.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            info = {}
        g = Mesh3daitest.geschlecht(self.ordner, info)
        if Mesh3daitesthaut.info(self.kennung, g) is None:
            return {}
        return {int(d.stem): str(d) for d in sorted((self.ordner / ('haut_%s' % g)).glob('10??.jpg')) if Mesh3daitesthaut.KACHEL.match(d.name)}

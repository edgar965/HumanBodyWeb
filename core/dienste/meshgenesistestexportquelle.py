# -*- coding: utf-8 -*-
"""Meshgenesistestexportquelle — die Exportleiste auf der Seite eines Tests von Mesh-Genesis (31.10.2026, `Exportleistequelle`).

Edgar: „mach mir die Buttons zum speichern des Modells in dem Bereich ‚Ganzer Körper‘, rechts unten … export als glb, obj, blend mit Checkbox mit oder ohne Animation“, „bitte auch pfad
für den Export vorbelegen“. Das Modell ist die Ausgabe der Seite als Genesis-Figur mit den Stücken der KI (`Meshgenesisfigurbewegung`), gebaut im Browser.
Exportordner `output/Export/Mesh-Genesis/<Name des Tests>` (wie MeshTo3D, BlenderModel, 2D3D Kleider — NICHT `3DObjects/modelsExport`: das ist die Jobliste von Foto-Genesis);
Arbeitsordner `exportleiste/` im Ordner des Tests.
"""

import json
from pathlib import Path

from django.conf import settings

from .exportleistequelle import Exportleistequelle
from .meshgenesisname import Meshgenesisname
from .meshgenesistest import Meshgenesistest
from .modellexportziel import Modellexportziel

__all__ = ['Meshgenesistestexportquelle']


class Meshgenesistestexportquelle(Exportleistequelle):
    BEREICH = 'meshgenesistest'
    ORDNER = 'exportleiste'

    def __init__(self, kennung, ordner):
        super().__init__(kennung)
        self.ordner = Path(ordner)

    @classmethod
    def finden(cls, kennung):
        ordner = Meshgenesistest.pfad(kennung) or Meshgenesistest.angelegt(kennung)
        return cls(kennung, ordner) if ordner is not None else None

    def name(self):
        eigen = Meshgenesisname.lesen(self.ordner)
        if eigen:
            return eigen
        for datei in ('test.json', 'anlage.json'):
            try:
                return json.loads((self.ordner / datei).read_text(encoding='utf-8')).get('name') or self.kennung
            except (OSError, ValueError):
                continue
        return self.kennung

    def exportordner(self):
        return Path(settings.MESHGENESIS_EXPORT_DIR) / Modellexportziel.name(self.name(), self.kennung)

    def arbeitsordner(self):
        return self.ordner / self.ORDNER

    def kollision(self):
        """Kapseln des Kostüm-Wegs (`Meshgenesistest.kapseln`, dieselben wie die Seite) und die Kinematik der Figur, in deren Ruhe sie stehen (`Meshgenesistest.form`) — oder None."""
        try:
            info = json.loads((self.ordner / 'test.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            info = {}
        g = Meshgenesistest.geschlecht(self.ordner, info)
        kapseln, form = Meshgenesistest.kapseln(self.ordner, g), Meshgenesistest.form(self.ordner, info, g)
        if not kapseln or not form:
            return None
        return kapseln, json.loads(form['kinematik'].read_text(encoding='utf-8'))['knochen']

    def kacheln(self):
        """Die Hautkacheln der KI dieses Tests (`haut_<g>/10xx.jpg`), wenn die Seite sie zeigt (`Meshgenesistesthaut.info`) — sonst bekam der Render die Daz-Haut der Grundfigur:
        Venus am 31.10.2026 mit fremdem Gesicht, einheitlichem Körperton und hellem Haaransatz (der Daz-Kopf hat unter dem Haar keine Haarfarbe; Edgar: „Haar hat Ansatz wie bei einer Perücke“)."""
        from .meshgenesistesthaut import Meshgenesistesthaut
        try:
            info = json.loads((self.ordner / 'test.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            info = {}
        g = Meshgenesistest.geschlecht(self.ordner, info)
        if Meshgenesistesthaut.info(self.kennung, g) is None:
            return {}
        return {int(d.stem): str(d) for d in sorted((self.ordner / ('haut_%s' % g)).glob('10??.jpg')) if Meshgenesistesthaut.KACHEL.match(d.name)}

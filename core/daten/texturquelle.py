# -*- coding: utf-8 -*-
"""Texturquelle — aus der Adresse einer Auftragsdatei den Pfad auf der Platte.

Ein gespeichertes Genesis-Modell aus „Mesh to 3D" oder „Modell aus Bildern" trug bis 27.09.2026
seine Fotokacheln als Adresse IN DEN AUFTRAG (`/api/meshfigur/<id>/datei/ergebnis/<name>`) — war
der Auftrag gelöscht, war die Haut weg. `Modelltexturen.sichern` kopiert die Kacheln deshalb beim
Speichern neben das Modell und braucht dafür die Datei hinter der Adresse. Gelesen wird nur aus
`ergebnis/` eines Auftrags, den es gibt, über dieselbe Pfadprüfung wie die Ausliefer-Endpunkte;
alles andere ist None — dann bleibt die Adresse, wie sie war.
"""

import re
from urllib.parse import unquote

__all__ = ['Texturquelle']


class Texturquelle:
    #: Adresse → (Auftragsart). Die Endpunkte: `Meshfigurendpunkte.datei`, `Bildmodellendpunkte.datei`,
    #: `Blendermodellendpunkte.datei` (seit 29.09.2026), `Engine2d3dKleiderendpunkte.datei` (seit 30.09.2026).
    MUSTER = re.compile(
        r'^/api/(?P<art>meshfigur|bildmodell|blendermodell|engine2d3dkleider)/(?P<id>[0-9a-fA-F-]{36})/datei/ergebnis/'
        r'(?P<name>[^/?#]+)/?$'
    )

    #: Die Hautkachel der Figur eines 2d-3d-AI-Jobs (`Ai2d3dfigur._kacheln`, 31.10.2026 für `Ai2d3dmodell`) — nur Kacheln `10??.jpg`.
    FIGUR_2D3DAI = re.compile(r'^/api/2d3dai/(?P<job>[-a-zA-Z0-9_]+)/figur/(?P<g>maennlich|weiblich)/bild/(?P<name>10\d\d\.jpg)$')

    @classmethod
    def pfad(cls, adresse):
        """Die Datei hinter einer Auftragsadresse (`Path`) — oder None."""
        figur = cls.FIGUR_2D3DAI.match(str(adresse or '').split('?')[0])
        if figur:
            from ..dienste.ai2d3dfigur import Ai2d3dfigur
            return Ai2d3dfigur.figurbild(figur['job'], figur['g'], figur['name'])
        treffer = cls.MUSTER.match(str(adresse or '').split('?')[0])
        if not treffer:
            return None
        name = unquote(treffer['name'])
        try:
            if treffer['art'] == 'meshfigur':
                from ..daten.meshfigurablage import Meshfigurablage
                from ..models import Meshfigurauftrag

                job = Meshfigurauftrag.objects.filter(pk=treffer['id']).first()
                return Meshfigurablage(job.kennung).datei('ergebnis', name) if job else None
            if treffer['art'] == 'blendermodell':
                from ..daten.blendermodellablage import Blendermodellablage
                from ..models import Blendermodellauftrag

                job = Blendermodellauftrag.objects.filter(pk=treffer['id']).first()
                return Blendermodellablage(job.kennung).datei('ergebnis', name) if job else None
            if treffer['art'] == 'engine2d3dkleider':
                from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
                from ..models import Engine2d3dKleiderauftrag

                job = Engine2d3dKleiderauftrag.objects.filter(pk=treffer['id']).first()
                return Engine2d3dKleiderablage(job.kennung).datei('ergebnis', name) if job else None
            from ..daten.bildmodellablage import Bildmodellablage
            from ..models import Bildmodellauftrag

            job = Bildmodellauftrag.objects.filter(pk=treffer['id']).first()
            return Bildmodellablage(job.kennung).datei('ergebnis', name) if job else None
        except ValueError:
            return None

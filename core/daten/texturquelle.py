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
    #: Adresse → (Auftragsart). Die Endpunkte: `Meshfigurendpunkte.datei`, `Bildmodellendpunkte.datei`.
    MUSTER = re.compile(
        r'^/api/(?P<art>meshfigur|bildmodell)/(?P<id>[0-9a-fA-F-]{36})/datei/ergebnis/(?P<name>[^/?#]+)/?$'
    )

    @classmethod
    def pfad(cls, adresse):
        """Die Datei hinter einer Auftragsadresse (`Path`) — oder None."""
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
            from ..daten.bildmodellablage import Bildmodellablage
            from ..models import Bildmodellauftrag

            job = Bildmodellauftrag.objects.filter(pk=treffer['id']).first()
            return Bildmodellablage(job.kennung).datei('ergebnis', name) if job else None
        except ValueError:
            return None

# -*- coding: utf-8 -*-
"""Studioexportquelle — die Exportleiste im BVH Studio (20.11.2026, Edgar: „http://127.0.0.1:8081/studio/ … da drin möchte ich den Renderer usw. haben“; `Exportleistequelle`).

Die Figur ist die Genesis-9-Figur der gewählten Bewegungsspur des Studios (`Spurfigurarten.BAUER['genesis9']`: `Genesis9Modell` mit `figur` = Name in der Bibliothek oder eines
gespeicherten Modells), gebaut im Browser; die Kennung ist dieser Name. Ein Arbeitsordner je Modell (Render-Läufe, Regler) unter dem Exportordner, NIE unter `HumanBody/data/models`
(dort liegt das gespeicherte Modell selbst). Hautkacheln: die Fotokacheln des gespeicherten Modells (`fototextur`, `Modelltexturen`) — ohne sie die Daz-Haut der Grundfigur.

    quelle = Exportleistebereiche.quelle('studio', 'Asian Female')
"""

from pathlib import Path

from django.conf import settings

from .exportleistequelle import Exportleistequelle
from .modellexportziel import Modellexportziel

__all__ = ['Studioexportquelle']


class Studioexportquelle(Exportleistequelle):
    BEREICH = 'studio'
    ORDNER = 'exportleiste'

    def __init__(self, kennung, eintrag):
        super().__init__(kennung)
        self.eintrag = eintrag

    @classmethod
    def finden(cls, kennung):
        """Nur Genesis-9-Figuren (Bibliothek oder gespeichert, `G9figur._eintrag`) — der Render kann nur Genesis 9."""
        from ..api.g9figur import G9figur
        eintrag = G9figur._eintrag(str(kennung or ''))
        return cls(kennung, eintrag) if eintrag is not None else None

    def name(self):
        return self.kennung

    def exportordner(self):
        return Path(settings.STUDIO_EXPORT_DIR) / Modellexportziel.name(self.name(), 'studio')

    def arbeitsordner(self):
        return self.exportordner() / self.ORDNER

    def kacheln(self):
        """Die Fotokacheln des gespeicherten Modells (`fototextur`: {'1001': Adresse, '1001:normalen': …}) als `{1001: Pfad}` — nur die Farbkacheln, die es als Datei gibt."""
        from .modelltexturen import Modelltexturen
        aus = {}
        for kachel, adresse in (self.eintrag.get('fototextur') or {}).items():
            if not str(kachel).isdigit():
                continue
            pfad = Modelltexturen._quelle(str(adresse or ''))
            if pfad is not None and Path(pfad).is_file():
                aus[int(kachel)] = str(pfad)
        return aus

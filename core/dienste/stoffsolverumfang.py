# -*- coding: utf-8 -*-
"""Stoffsolverumfang — was der Stoffsolver von Blenders Cloth, Haar und UV schon kann und was nicht (02.10.2026).

Edgar: „was fehlt am Solver?", dann „implementiere alles, was fehlt", dann „starte blender nach belieben! Teste alle Funktionen gegen Blender" und „mach alle". Die Tabelle auf der Seite
Hilfe → Architektur → 2D3D (Reiter „Workflow") stellt je Blender-Funktion die Klasse im Solver und den STAND dar. Der Stand ist ehrlich in fünf Stufen:

    blender  gegen einen echten Blender-Lauf gemessen (Blender 5.2.2, Hintergrundmodus; Rauschgrenze, Wirkung und Gegenprobe wie in `Stoffsolver/README.md`, Abschnitt „Messungen")
    quelle   nach Blenders Quelltext gebaut und gegen Handrechnung getestet — KEIN Blender-Lauf (Blender kann es im Hintergrundmodus nicht)
    eigen    Eigenbau, den es in Blender so nicht gibt (UV-Prüfung, Henkelschnitt, Fotoprojektion, Mipmaps)
    teil     teilweise gebaut, die Anmerkung nennt was
    nein     nicht gebaut

Die Zeilen stehen nach Bereich getrennt in `Stoffsolverumfangkleid`, `Stoffsolverumfanghaar` und `Stoffsolverumfanguv`. Die Klassen werden beim Aufruf im Code gesucht
(`Architektur2d3dklassen.zeile`): Fehlt eine, steht „fehlt" in der Zeile, statt dass die Behauptung stehen bleibt.
"""

from .architektur2d3dklassen import Architektur2d3dklassen
from .stoffsolverumfangkleid import Stoffsolverumfangkleid
from .stoffsolverumfanghaar import Stoffsolverumfanghaar
from .stoffsolverumfanguv import Stoffsolverumfanguv

__all__ = ['Stoffsolverumfang']


class Stoffsolverumfang:
    STAENDE = {
        'blender': 'gegen Blender gemessen',
        'quelle': 'nach Quelltext gebaut und getestet, kein Blender-Lauf',
        'eigen': 'Eigenbau, nicht aus Blender',
        'teil': 'teilweise',
        'nein': 'nicht gebaut',
    }
    QUELLE = ('Stoffsolver/README.md (Messungen, Bausteine) und Stoffsolver/LUECKEN.md; Läufe in Blender 5.2.2 am 02.10.2026. Maße: Punktabstand Solver ↔ Blender im letzten Bild in mm; '
              'die Rauschgrenze ist Blender gegen Blender bei 1e-7 bis 1 µm Störung der Ausgangslage, bei UV die Form in Inseldiagonalen')
    #: (Bereich, Blender-Funktion, [(Datei, Klasse)], Stand, Anmerkung)
    ZEILEN = Stoffsolverumfangkleid.ZEILEN + Stoffsolverumfanghaar.ZEILEN + Stoffsolverumfanguv.ZEILEN

    @classmethod
    def zeilen(cls):
        """Die Tabelle: je Zeile Bereich, Blender-Funktion, `klassen` ({klasse, anker, fehlt}), Stand-Kennung und -Text, Anmerkung."""
        aus = []
        for bereich, blender, klassen, stand, hinweis in cls.ZEILEN:
            gefunden = []
            for modul, klasse in klassen:
                z = Architektur2d3dklassen.zeile(modul, klasse)
                gefunden.append({'klasse': klasse, 'anker': 'k-' + klasse, 'fehlt': z['fehlt']})
            aus.append({'bereich': bereich, 'blender': blender, 'klassen': gefunden, 'stand': stand,
                        'stand_text': cls.STAENDE[stand], 'hinweis': hinweis})
        return aus

    @classmethod
    def zaehlung(cls):
        """[{stand, text, anzahl}] in der Reihenfolge der Stufen — gezählt aus den Zeilen, nicht geschrieben."""
        return [{'stand': s, 'text': t, 'anzahl': sum(1 for z in cls.ZEILEN if z[3] == s)} for s, t in cls.STAENDE.items()]

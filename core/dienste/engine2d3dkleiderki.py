# -*- coding: utf-8 -*-
"""Engine2d3dKleiderki — welche KI den Schritt „Netz" rechnet, für die Liste und die Überschriften von „2D3D Kleider" (03.10.2026).

Edgar: „warum sehe ich bei den Jobs keine Auswahl der KI (also trellis v.2 oder Pixar usw)?" — die Wahl stand nur als Feld „Modell" der Karte „Mesh"
unter den Bildern der Auftragsseite (`Engine2d3dKleidermeshoptionen`, Gruppe `mesh`), die Liste zeigte sie nicht, und die Überschrift der Karte, die Laufleiste und die
Schrittauswahl hießen fest „TRELLIS". Jetzt zeigt die Liste eine Spalte „KI" als Auswahlfeld (schreibt dieselbe Option `mesh.modell`), und die Auftragsseite benennt
Karte und Schritt nach dem gewählten Modell (`engine2d3dkleidermeshkarte.js`).

    trellis2     TRELLIS.2 (Microsoft) — ein Foto
    pixal3d      Pixal3D (Tencent ARC) — ein Foto
    pixal3d_mv   Pixal3D Mehrbild — vorne/hinten/links/rechts mit Kameras

`aktuell` liest die gespeicherte Option direkt und prüft sie nur gegen die Wertliste: `Engine2d3dKleideroptionen.pruefen` fragt Kataloge, die die Daz-Bibliothek und Ollama
anfassen — für eine Zeile der Liste (19 und mehr) viel zu teuer.
"""

from .engine2d3dkleidermeshoptionen import Engine2d3dKleidermeshoptionen

__all__ = ['Engine2d3dKleiderki']


class Engine2d3dKleiderki:
    @classmethod
    def werte(cls):
        """`[(wert, kurzer Name, langer Text)]` aus dem Katalog der Gruppe `mesh` — der Kurzname ist der Teil vor dem Gedankenstrich."""
        eintrag = next(e for e in Engine2d3dKleidermeshoptionen.KATALOG if e['schluessel'] == 'modell')
        return [(w, t.split(' — ')[0], t) for w, t in eintrag['werte']]

    @classmethod
    def aktuell(cls, optionen):
        """Das gewählte Modell eines Auftrags (`optionen['mesh']['modell']`, sonst oder bei einem unbekannten Wert die Vorgabe `trellis2`)."""
        wert = ((optionen or {}).get('mesh') or {}).get('modell')
        return wert if wert in [w for w, _k, _t in cls.werte()] else Engine2d3dKleidermeshoptionen.vorgaben()['modell']

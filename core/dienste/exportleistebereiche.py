# -*- coding: utf-8 -*-
"""Exportleistebereiche — welche Bereiche die Exportleiste tragen (31.10.2026): Kennung des Bereichs → `Exportleistequelle`.

Eine Seite bekommt die Leiste mit drei Schritten: eine Quelle (erbt von `Exportleistequelle`) hier eintragen, `{% include "_exportleiste.html" with bereich=… kennung=… %}` in die
Vorlage, und `new Exportleiste(wurzel, quelle)` mit der Figur der Seite (`static/viewer/exportleiste/exportleiste.js`).
"""

__all__ = ['Exportleistebereiche']


class Exportleistebereiche:
    @staticmethod
    def klassen():
        from .ai2d3dexportquelle import Ai2d3dexportquelle
        from .engine2d3dkleiderexportquelle import Engine2d3dKleiderexportquelle
        from .mesh3daitestexportquelle import Mesh3daitestexportquelle
        return {k.BEREICH: k for k in (Mesh3daitestexportquelle, Ai2d3dexportquelle, Engine2d3dKleiderexportquelle)}

    @classmethod
    def quelle(cls, bereich, kennung):
        """Die Quelle — oder None (unbekannter Bereich oder unbekannte Kennung)."""
        klasse = cls.klassen().get(str(bereich))
        return klasse.finden(kennung) if klasse else None

# -*- coding: utf-8 -*-
"""Exportleistebereiche — welche Bereiche die Exportleiste tragen (31.10.2026): Kennung des Bereichs → `Exportleistequelle`.

Eine Seite bekommt die Leiste mit drei Schritten: eine Quelle (erbt von `Exportleistequelle`) hier eintragen, `{% include "_exportleiste.html" with bereich=… kennung=… %}` in die
Vorlage, und `new Exportleiste(wurzel, quelle)` mit der Figur der Seite (`static/viewer/exportleiste/exportleiste.js`).
"""

__all__ = ['Exportleistebereiche']


class Exportleistebereiche:
    @staticmethod
    def klassen():
        from .fotogenesisexportquelle import Fotogenesisexportquelle
        from .engine2d3dkleiderexportquelle import Engine2d3dKleiderexportquelle
        from .meshgenesisanpassungexportquelle import Meshgenesisanpassungexportquelle
        from .meshgenesistestexportquelle import Meshgenesistestexportquelle
        klassen = (Meshgenesistestexportquelle, Meshgenesisanpassungexportquelle, Fotogenesisexportquelle,
                   Engine2d3dKleiderexportquelle)
        return {k.BEREICH: k for k in klassen}

    @classmethod
    def quelle(cls, bereich, kennung):
        """Die Quelle — oder None (unbekannter Bereich oder unbekannte Kennung)."""
        klasse = cls.klassen().get(str(bereich))
        return klasse.finden(kennung) if klasse else None

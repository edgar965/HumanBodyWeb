# -*- coding: utf-8 -*-
"""G9retargetziel — das Genesis-9-Skelett als Ziel des Retargets.

Herausgeloest aus `Retargetdaten` (17.09.2026), damit die Datei unter 300
Zeilen bleibt: hier steht, WOHER das Zielskelett kommt — aus derselben
Kette, aus der auch der Browser seine Knochen baut
(`G9formung.skelett().kette()`, mit Morphversatz und Bodenversatz). Waere
es eine zweite Rechnung, rechnete der Motor gegen eine Ruhelage, die die
Figur nicht hat (Befund SMPL, 07.09.2026).
"""

__all__ = ["G9retargetziel"]


class G9retargetziel:
    """Geometrie und Zuordnung fuer `Retargetdaten._auf_kette`."""

    FEHLT = "Daz-Bibliothek mit Genesis 9 fehlt — siehe Genesis9/HERKUNFT.md"

    @classmethod
    def geometrie(cls, formung):
        """`SkeletonGeometry` der Reglerstellung; `formung` darf None sein."""
        from Genesis9.formung import G9formung
        from Genesis9.pfade import G9pfade

        if not G9pfade.vorhanden():
            raise ValueError(cls.FEHLT)
        if not isinstance(formung, G9formung):
            formung = G9formung({})
        return formung.skelett().kette().geometrie()

    @staticmethod
    def zuordnung():
        from humanbody_core.skeleton.formats.g9_zuordnung import G9zuordnung

        return G9zuordnung

# -*- coding: utf-8 -*-
"""Garmentbauart — wie der GarmentCode-Reiter drapiert: wie SMPL oder mit Nacharbeit.

Edgar (25.09.2026): „mach darin die Einstellungen für den Garment Code build.
Default: «Drapierung wie bei SMPL» - Alternativ - «Mit Nacharbeit». Checkbox in
Toolbar kann dann weg". Die Wahl liegt in `AppSettings.ui_prefs` unter
`SCHLUESSEL` (Seite Einstellungen → Kleider, `seite_kleider_einstellungen.py`),
gelesen vom Server bei jedem Bau — nicht vom Browser mitgeschickt, damit der
Einzel- und der gemeinsame Bau dieselbe Antwort bekommen.

`wie_smpl` heißt: GarmentCodes Kollisionsabstand (0,25 cm) und keine
Nacharbeit (Herausschieben, Anlegen, Hochziehen) — Begründung in
`Assets/GarmentCode/baufeineinstellung.py`, Abschnitt „WIE SMPL".

NICHT FUER HOSE UND SHORTS (26.09.2026): Sie brauchen das Hochziehen (Schritt an den
Schritt) unabhaengig von der Einstellung — ohne es kam die Hose als Pluderhose heraus.
Anzug und Schuh folgen der Einstellung (Edgar: „anzug soll ja auch drapiert werden,
Schuh auch").
"""

__all__ = ['Garmentbauart']


class Garmentbauart:
    """Die gewählte Bauart des GarmentCode-Reiters."""

    SCHLUESSEL = 'garmentcode_drapierung'
    SMPL = 'smpl'
    NACHARBEIT = 'nacharbeit'
    VORGABE = SMPL
    #: Wert → Anzeigetext, in der Reihenfolge der Auswahl.
    WAHLEN = {
        SMPL: 'Drapierung wie bei SMPL',
        NACHARBEIT: 'Mit Nacharbeit',
    }

    #: Katalogstuecke, die das Hochziehen IMMER brauchen — unabhaengig von
    #: der Einstellung (Katalognamen aus `Assets/GarmentCode/katalog.py`).
    IMMER_NACHARBEIT = ('hose', 'shorts')

    @classmethod
    def aus(cls, prefs):
        """Die Wahl aus einem `ui_prefs`-Dict; Unbekanntes heißt Vorgabe."""
        wert = str((prefs or {}).get(cls.SCHLUESSEL) or cls.VORGABE)
        return wert if wert in cls.WAHLEN else cls.VORGABE

    @classmethod
    def gewaehlt(cls):
        from ..models import AppSettings
        return cls.aus(AppSettings.load().ui_prefs)

    @classmethod
    def wie_smpl(cls, vorlage=None, anliegen_mm=None):
        """Ohne Nacharbeit bauen? Nie fuer `IMMER_NACHARBEIT`, und nie, wenn das
        Anlegen an die Haut verlangt ist (Leggings: `bau.anliegen_mm`) — das
        Anlegen IST Nacharbeit, „wie SMPL" haette es stumm gestrichen."""
        if vorlage in cls.IMMER_NACHARBEIT or anliegen_mm:
            return False
        return cls.gewaehlt() == cls.SMPL

    @staticmethod
    def vorlage_aus(spezifikation):
        """Die Vorlage aus dem Ordner des Schnitts (`hose_female/…`,
        `hose_smplx_f_…/…`, `GarmentcodeDienst.erzeugen`) — fuer Anfragen
        eines Browsers, der sie noch nicht mitschickt. Unbekannt: None."""
        import os
        from GarmentCode.katalog import Katalog
        ordner = os.path.basename(os.path.dirname(str(spezifikation or '')))
        kopf = ordner.split('_', 1)[0]
        return kopf if kopf in Katalog.STUECKE else None

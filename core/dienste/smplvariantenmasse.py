"""Smplvariantenmasse — die Maße einer geformten SMPL-X-Variante, gemessen ohne Ablage (25.11.2026 aus `Smplvarianten._erzeugen` herausgelöst).

Anlass (Edgar, 25.11.2026: „Maße bei SMPL-X: werden erst gemessen, wenn der Bereich offen ist; das dauert 5–8 s“ → „fixe“): Seit die Hüllen der Körpermessung in einem Kern rechnen
(`Kartenhuelle2`), kostet eine Messung 0,25 statt 8 s. Die Anzeige misst darum nach jedem Zug — aber nur im Speicher: OBJ und YAML (700 kB je Stellung) schreibt weiter erst, wer sie
braucht (`Smplvarianten.sicherstellen`, Drapieren). Den Durchschnittskörper, gegen den gemessen wird, misst `vorwaermen` beim ersten Zug im Hintergrund.

    masse, herkunft = Smplvariantenmasse.von(geschlecht, betas, punkte)      # wie bisher, ohne Dateien
    masse = Smplvariantenmasse.gemessen(name)                                # aus den abgelegten Betas, je Name einmal
"""
import json
import logging
import os
import threading
from collections import OrderedDict

logger = logging.getLogger('core')

__all__ = ['Smplvariantenmasse']


class Smplvariantenmasse:
    #: so viele gemessene Varianten bleiben im Speicher
    HOECHSTENS = 64
    _roh_durchschnitt = {}
    _gemessen = OrderedDict()
    _schloss = threading.RLock()
    _gewaermt = set()

    @classmethod
    def von(cls, geschlecht, betas, punkte):
        """`(masse, herkunft)` einer Form gegen den Durchschnitt ihres Geschlechts."""
        from SMPL.masse import Smplmasse

        from .smplfigur import Smplfiguren
        from .smplvarianten import Smplvarianten
        modell = Smplvarianten.modell(geschlecht)
        # Die Armlaenge kommt aus den Gelenken, nicht aus der YAML: dort stehen 80 cm bei 165 cm Koerpergroesse (siehe Smplkoerper.armlaenge).
        return Smplmasse(Smplvarianten.segmentierung()).relativ(punkte, None, Smplfiguren.masse(Smplvarianten.VORLAGE[geschlecht]),
                                                               zusatz={'arm_length': modell.armlaenge(betas)}, roh_durchschnitt=cls._durchschnitt(geschlecht))

    @classmethod
    def _durchschnitt(cls, geschlecht):
        """Die rohen Maße des Durchschnittskörpers — einmal je Geschlecht und Prozess."""
        from SMPL.masse import Smplmasse

        from .smplfigur import Smplfiguren
        from .smplvarianten import Smplvarianten
        with cls._schloss:
            if geschlecht not in cls._roh_durchschnitt:
                messung = Smplmasse(Smplvarianten.segmentierung())
                cls._roh_durchschnitt[geschlecht] = messung.roh(Smplvarianten.modell(geschlecht).a40(None), Smplfiguren.masse(Smplvarianten.VORLAGE[geschlecht]))
            return cls._roh_durchschnitt[geschlecht]

    @classmethod
    def gemessen(cls, name):
        """Die Maße der Variante `name` aus ihren abgelegten Betas — None, wenn keine Betas liegen."""
        from .smplvarianten import Smplvarianten
        with cls._schloss:
            if name in cls._gemessen:
                cls._gemessen.move_to_end(name)
                return cls._gemessen[name]
            pfad = os.path.join(Smplvarianten.ordner(), str(name) + Smplvarianten.BETAS)
            if not Smplvarianten.ist_variante(name) or not os.path.isfile(pfad):
                return None
            with open(pfad, encoding='utf-8') as quelle:
                betas = json.load(quelle)
            geschlecht = Smplvarianten.geschlecht(name)
            masse, _herkunft = cls.von(geschlecht, betas, Smplvarianten.modell(geschlecht).a40(betas))
            cls._gemessen[name] = masse
            while len(cls._gemessen) > cls.HOECHSTENS:
                cls._gemessen.popitem(last=False)
            return masse

    @classmethod
    def vorwaermen(cls, geschlecht):
        """Den Durchschnittskörper einmal im Hintergrund messen (erster Zug), damit die erste Messung nicht doppelt kostet."""
        if geschlecht in cls._gewaermt:
            return
        cls._gewaermt.add(geschlecht)
        threading.Thread(target=cls._waermen, args=(geschlecht,), name='smpl-masse', daemon=True).start()

    @classmethod
    def _waermen(cls, geschlecht):
        try:
            cls._durchschnitt(geschlecht)
        except Exception:  # noqa: BLE001 — nur Vorarbeit: die erste Messung rechnet ihn sonst selbst
            logger.exception('SMPL-X: Durchschnitt (%s) nicht vorgemessen', geschlecht)

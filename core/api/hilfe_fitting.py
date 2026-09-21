# -*- coding: utf-8 -*-
"""Hilfe -> Kleidung -> Fitting: warum Haut durch Kleidung kam und was dagegen gilt.

Edgar (21.09.2026): „schreibe die Erkenntnis in die Seite Hilfe - Kleidung -
Fitting". Die Daten kommen aus `kleidung.fitting.Kleidungsfitting`, nicht aus
der Vorlage — dieselbe Regel wie bei `KleidungPhysik`.
"""

from kleidung.fitting import Kleidungsfitting

from .hilfeseite import Hilfeseite


class KleidungFitting(Hilfeseite):
    """Vorfaelle, Ursachen, wie andere es machen, die vier Schichten, Stand."""

    template_name = 'hilfe/kleidung_fitting.html'
    AKTIV = 'hilfe_kleidung_fitting'

    def kontext(self):
        return {
            'vorfaelle': Kleidungsfitting.vorfaelle(),
            'ursachen': Kleidungsfitting.ursachen(),
            'andere': Kleidungsfitting.andere(),
            'schichten': Kleidungsfitting.schichten(),
            'abnahme': Kleidungsfitting.abnahme(),
            'stand': Kleidungsfitting.stand(),
            'nicht': Kleidungsfitting.nicht(),
            'quellen': Kleidungsfitting.quellen(),
            'kollision_mm': Kleidungsfitting.KOLLISION_MM,
            'stand_prozent': Kleidungsfitting.STAND_PROZENT,
            'sitzen_prozent': Kleidungsfitting.SITZEN_PROZENT,
        }

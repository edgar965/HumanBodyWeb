# -*- coding: utf-8 -*-
u"""Effektvorgaben — was die Effekte-Seite beim Laden vorwählt.

Quelle sind die Felder aus `EffektEinstellungen` (Seite Einstellungen →
Effekte, Edgar 12.09.2026: „das Standard Modell … mit dem die Seite geladen
wird, standard: Female2"). Die Klasse übersetzt sie in das, was die Vorlage
braucht: die Startstellung der Regler (`karte()` beider Pipelines mit
ersetzter `vorgabe`) und drei `data-vorgabe-*`-Attribute am Formular, die
`effektseite.js` beim Aufbau anwendet.

Ein Modell, das es nicht (mehr) gibt, wird NICHT vorgewählt — die Seite
zeigt „keins gewählt" statt eines Namens, den der Start dann abweist.
"""

from ..dienste.modellvorlagen import Modellvorlagen
from ..models import Effektauftrag

__all__ = ['Effektvorgaben']


class Effektvorgaben:

    #: Einstellungsfeld -> Name des Reglers auf der Seite.
    REGLER = (('effekte_video_fps', 'fps'), ('effekte_video_width', 'breite'),
              ('effekte_video_height', 'hoehe'), ('effekte_wind', 'wind'))

    def __init__(self, einstellungen):
        self.s = einstellungen

    def pipeline(self):
        wert = self.s.effekte_default_pipeline
        return wert if wert in dict(Effektauftrag.PIPELINE_CHOICES) else 'figur_def'

    def modell(self):
        name = self.s.effekte_default_model or ''
        return name if Modellvorlagen.pfad(name) else ''

    def animation(self):
        return (self.s.effekte_default_animation or '').strip()

    def windrichtung(self):
        return self.s.effekte_windrichtung or 'seite'

    def karte(self, karte):
        u"""`Parametersatz.karte()` mit den Startwerten aus den Einstellungen —
        im Rahmen der Feldgrenzen."""
        werte = {regler: getattr(self.s, feld) for feld, regler in self.REGLER}
        aus = []
        for f in karte:
            f = dict(f)
            if f['name'] in werte and f['typ'] != 'bool':
                wert = min(max(werte[f['name']], f['min']), f['max'])
                f['vorgabe'] = int(wert) if f['typ'] == 'int' else wert
            aus.append(f)
        return aus

    def kontext(self):
        u"""Die drei Startwahlen fuer `data-vorgabe-*` am Formular."""
        return {'vorgabe_pipeline': self.pipeline(), 'vorgabe_modell': self.modell(),
                'vorgabe_animation': self.animation(),
                'vorgabe_windrichtung': self.windrichtung()}

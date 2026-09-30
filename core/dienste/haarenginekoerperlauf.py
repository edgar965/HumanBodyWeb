# -*- coding: utf-8 -*-
"""Haarenginekoerperlauf — die Schrittklassen von „Mesh to 3D" auf einem Auftrag „2D3D Kleider" (30.09.2026).

`Meshfigurkette`, `Meshfigurende`, `Meshfigurhaar`, `Meshfigurkleidung`, `Meshfigurvorschau` sprechen nur mit
`lauf.job`, `lauf.ablage`, `lauf.optionen`, `lauf.melden`, `lauf.runner`, `lauf.zusatz`, `lauf.vorlage` —
dieselbe Beobachtung wie bei BlenderModel (`blendermodell.md`). Diese Klasse ERBT von `Meshfigurlauf`
(`auftrag()`, `runner()`, `umgebung()`, `_erkennung`, `_kalibrierung`, `vorlage()` bleiben) und ersetzt nur
den Aufbau: der Auftrag und die Ablage sind die von „2D3D Kleider", der Fortschritt geht in das Band des
Schritts „koerper" des äußeren Laufs.

Nicht ersetzt: `runner()` prüft „angehalten" gegen die Tabelle von „Mesh to 3D" (findet dort nichts) — der
äußere Lauf prüft zwischen den Schritten, und „Anhalten" beendet den Arbeitsprozess samt Runner ohnehin
(`Haarenginearbeiter.anhalten`, `taskkill /T`).

NICHT GELAUFEN (Stand 30.09.2026): Der erste Auftrag übernahm den Körper (`koerper.quelle = uebernehmen`); dieser
Weg ist geschrieben, aber ohne Lauf — rund 15 Minuten Grafikkarte.
"""

from .meshfigurlauf import Meshfigurlauf
from .meshfiguroptionen import Meshfiguroptionen

__all__ = ['Haarenginekoerperlauf']


class Haarenginekoerperlauf(Meshfigurlauf):
    def __init__(self, aussen, koerperoptionen):        # noqa: D107 — kein `super().__init__`: der lädt Meshfigurauftrag
        self.aussen = aussen
        self.job = aussen.job
        self.ablage = aussen.ablage
        figur = dict(koerperoptionen or {})
        figur['basis'] = (aussen.optionen or {}).get('basis') or figur.get('basis') or 'masculine'
        figur['modell'] = 'aus'
        self.optionen = Meshfiguroptionen.pruefen(figur)
        self.zusatz = {}
        self._von, self._bis = 0.0, 1.0
        self._letzte_db = 0.0
        self.Angehalten = aussen.Angehalten

    def schrittfolge(self):
        from .meshfigurende import Meshfigurende
        from .meshfigurhaar import Meshfigurhaar
        from .meshfigurkette import Meshfigurkette
        from .meshfigurkleidung import Meshfigurkleidung
        from .meshfigurvorschau import Meshfigurvorschau

        return {
            'erkennung': self._erkennung,
            'haar': lambda: Meshfigurhaar(self).ausfuehren(),
            'kleidung': lambda: Meshfigurkleidung(self).ausfuehren(),
            'kalibrierung': self._kalibrierung,
            'koerper': lambda: Meshfigurkette(self).koerper(),
            'gesicht': lambda: Meshfigurkette(self).gesicht(),
            'rest': lambda: Meshfigurende(self).rest(),
            'textur': lambda: Meshfigurende(self).textur(),
            'vorschau': lambda: Meshfigurvorschau(self).ausfuehren(),
        }

    def band(self, von, bis, name):
        """Der Anteil des Bands „koerper", in dem dieser Teilschritt läuft."""
        self._von, self._bis = von, bis
        self.aussen.melden(von, 'Körper: %s' % name)

    def melden(self, anteil, text):
        self.aussen.melden(self._von + (self._bis - self._von) * max(0.0, min(1.0, anteil)), 'Körper: %s' % text)

    def sichern(self, *felder):
        self.aussen.sichern(*felder)

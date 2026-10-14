# -*- coding: utf-8 -*-
"""Meshfigurabnahme — der Befund jedes Laufs „Mesh to 3D", ohne Schalter (13.10.2026, Konzept „Mesh-3D ohne Nacharbeit").

Edgar: „mach das alles" — Empfehlungen und Vergleiche brauchen Zahlen, die bei JEDEM Lauf da sind, nicht nur dort, wo ich sie von Hand gerechnet habe. Der Befund steht in `ergebnis.abnahme`:

* `objekte` — Flächen je Objekt, Doppelte, Waisen, Hut (`Meshfigurabnahmeobjekte`)
* `abstand_je_teil_mm`, `stoff_im_koerper`, `masse_cm` (`Meshfigurabnahmekoerper`)
* `hoehe_cm`, `figur_netz` — aus der Vorschau desselben Laufs

Jeder Teil fängt seinen Fehler selbst (`{'fehler': …}` statt des Teils); ein Fehler der Abnahme bricht den Lauf nie ab (`sicher`). Läuft am Ende des Schritts „vorschau", wenn alle Objekte stehen.
"""

import logging
import time

logger = logging.getLogger('core')

__all__ = ['Meshfigurabnahme']


class Meshfigurabnahme:
    #: Hochzählen, wenn sich eine Messung ändert — der Vergleich mit einem älteren Lauf warnt dann.
    FASSUNG = 1

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job

    @classmethod
    def sicher(cls, lauf):
        """Der Befund — oder `{'fehler': …}`; wirft nie."""
        try:
            return cls(lauf).rechnen()
        except Exception as fehler:  # noqa: BLE001 — ein Zusatz: sichtbar im Ergebnis und im Log, der Lauf geht weiter
            logger.exception('Mesh to 3D %s: Abnahme gescheitert', lauf.job.kennung)
            return {'fassung': cls.FASSUNG, 'fehler': str(fehler)[:300]}

    def rechnen(self):
        from .meshfigurabnahmekoerper import Meshfigurabnahmekoerper
        from .meshfigurabnahmeobjekte import Meshfigurabnahmeobjekte
        from .meshfigurkleidung import Meshfigurkleidung

        t0 = time.perf_counter()
        scan, _ = Meshfigurkleidung(self.lauf).koerpernetz()
        koerper = Meshfigurabnahmekoerper(self.lauf, scan)
        vorschau = self.job.ergebnis.get('vorschau') or {}
        abstand = vorschau.get('abstand') or {}
        aus = {
            'fassung': self.FASSUNG,
            'objekte': self._teil(lambda: Meshfigurabnahmeobjekte(self.lauf).messen(scan)),
            'abstand_je_teil_mm': self._teil(koerper.abstand_je_teil),
            'stoff_im_koerper': self._teil(koerper.stoff_im_koerper),
            'masse_cm': self._teil(koerper.masse),
            'hoehe_cm': vorschau.get('hoehe_cm'),
            'figur_netz': {k: abstand.get(k) for k in ('figur_netz_rms_mm', 'netz_figur_rms_mm')},
        }
        aus['sekunden'] = round(time.perf_counter() - t0, 1)
        logger.info('Mesh to 3D %s: Abnahme %.1f s — %s', self.job.kennung, aus['sekunden'], (aus['objekte'] or {}).get('urteil') or 'ohne Objekte')
        return aus

    def _teil(self, rechnung):
        try:
            return rechnung()
        except Exception as fehler:  # noqa: BLE001 — ein Teil der Abnahme fehlt, die anderen stehen
            logger.exception('Mesh to 3D %s: Teil der Abnahme gescheitert', self.job.kennung)
            return {'fehler': str(fehler)[:300]}

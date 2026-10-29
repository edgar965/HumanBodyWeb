# -*- coding: utf-8 -*-
"""Ai2d3dformki — welche KI die Form aus den Fotos rechnet (28.10.2026 abends, Edgar: „die alte KopfKI war doch schon sehr gut, hole die wieder heraus“ — „Du kannst es ja optional
machen, in den Einstellungen - 2d-3d-ai einstellbar, KopfKI oder iterative MeshKi, mache einen zweiten Job mit der iterativen MeshKI zum Vergleich“).

`kopfki`: die Kopf-KI (`KopfKI/kopfnetz.py`, Netz A, Stand kopfki8 vom 27.10.2026, über alle Trainingsjobs gelernt) — Fotos → Kopfregler und Kopflage, der Körper aus der
Fotoeinpassung. `iterativ`: die iterative Mesh-KI (`KoerperKI_Fotos/meshschritt*.py`) — ein Netz, das den Korrekturschritt der geometrischen Figur gegen die Fotos lernt (Eingang je Punkt:
Gradient des Fotoverlusts, bisherige Verschiebung, Normale), einige Runden lang; aus dem Ergebnis macht `Genesis9.meshgenesis` die Genesis-Figur. Gespeichert in
`AppSettings.ui_prefs` wie `Ai2d3dmeshwahl`.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Ai2d3dformki']


class Ai2d3dformki:
    SCHLUESSEL = 'ai2d3d_form_ki'
    VORGABE = 'kopfki'
    WERTE = (('kopfki', 'Kopf-KI — Fotos → Kopfregler (Netz A, kopfki8)'), ('iterativ', 'Iterative Mesh-KI — gelernter Schritt der geometrischen Figur, dann Genesis'))
    BESCHREIBUNG = {
        'kopfki': 'Ein Netz, über alle Trainingsjobs gelernt, liest die Fotos und gibt die Kopfregler und die Kopflage je Foto aus; der Körper kommt aus der Einpassung an die Fotos. '
                  'Stand: Netz A vom 27.10.2026 (kopfki8), an EdgarTrip Kopfmaß 6,90 → 1,16 mm, Abnahme 45/55 grün.',
        'iterativ': 'Ein Netz, über alle Trainingsjobs gelernt, korrigiert die geometrische Figur Runde für Runde: es bekommt je Punkt, wohin der Fotoverlust (Umriss, Ohren, Gesicht, '
                    'ViTPose) die Figur ziehen will, und gibt die Verschiebung aus — statt hunderter Rechenschritte je Job wenige gelernte. Aus der Figur macht die Mesh-Einpassung '
                    'die Genesis-Figur. Im Vergleich gegen die Kopf-KI.',
    }

    @classmethod
    def aus(cls, prefs):
        w = str((prefs or {}).get(cls.SCHLUESSEL, cls.VORGABE)).strip()
        return w if w in dict(cls.WERTE) else cls.VORGABE

    @classmethod
    def gewaehlt(cls):
        """Die gespeicherte KI — ohne lesbare Einstellungen die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — Rechenläufe sollen auch ohne Datenbank laufen, mit der Vorgabe
            logger.warning('Ai2d3dformki: Einstellung nicht lesbar (%s) — Vorgabe %s', fehler, cls.VORGABE)
            return cls.VORGABE

    @classmethod
    def text(cls, wert):
        return dict(cls.WERTE).get(wert, str(wert))

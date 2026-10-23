# -*- coding: utf-8 -*-
"""Mesh3daikostuemstufe — wie weit der Kostüm-Weg A (Kostüm aus dem Eingang ausschneiden) gehen soll: Stufe 1 Stand, 2 Bewegung, 3 Stoff (23.10.2026).

Edgar zur Strategie für eigene Kostüme: „Was heißt fertig? … zu Punkt 3: Das bitte einstellbar. Für die Strategie, und erste Berechnung: Stufe 1“. Konzept
`Docu/konzepte/2026-10-23_mesh3dai-eigene-kostueme-strategie-konzept.md`.
Die Stufe entscheidet im Rechenlauf (`ProjektTemp/_wegwerf/mesh3dai_kostuem_lauf.py`), wie die Stücke auf die Figur kommen (1: Rückhäutung, im Stand exakt wie im Eingang; 2/3: Bindung nach Kategorie,
`Kleideruebertrag`) und welche Prüfungen zur Abnahme gehören (ab 2 die Bewegung, ab 3 der Stoff — beide noch nicht gebaut und darum FEHLER). Gespeichert in `AppSettings.ui_prefs` wie
`Mesh3daiabnahmewahl`; sie ändert keinen Lauf, der schon gerechnet ist.
"""

import logging

logger = logging.getLogger('core')

__all__ = ['Mesh3daikostuemstufe']


class Mesh3daikostuemstufe:
    SCHLUESSEL = 'mesh3dai_kostuem_stufe'
    VORGABE = 1
    WERTE = ((1, 'Stufe 1 — Stand: sieht aus wie der Eingang'), (2, 'Stufe 2 — Bewegung: Teile folgen dem Körper'), (3, 'Stufe 3 — Stoff schwingt'))
    BESCHREIBUNG = {
        1: 'Jedes Stück wird so auf die Figur der KI gelegt, dass es in ihrer Haltung genau dort liegt, wo es im Eingang liegt (Rückhäutung). Geprüft: Löcher, Ränder, Umriss, Haut statt '
           'Kostüm, Lage, Durchstich, Farbe. Gebaut.',
        2: 'Die Stücke hängen nach ihrer Kategorie an der Figur: genähte Kleidung folgt der Haut, feste Formen und Requisiten starr an einem Knochen. Übertragung vorhanden, die Prüfung '
           'der Bewegung ist NICHT gebaut (zählt als Fehler).',
        3: 'Wie Stufe 2, dazu schwingt Stoff in der Bewegung. NICHT gebaut (zählt als Fehler).',
    }

    @classmethod
    def aus(cls, prefs):
        try:
            w = int(str((prefs or {}).get(cls.SCHLUESSEL, cls.VORGABE)).strip())
        except ValueError:
            return cls.VORGABE
        return w if w in dict(cls.WERTE) else cls.VORGABE

    @classmethod
    def gewaehlt(cls):
        """Die gespeicherte Stufe — ohne lesbare Einstellungen die Vorgabe, mit Warnung."""
        try:
            from ..models import AppSettings
            return cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — Rechenläufe sollen auch ohne Datenbank laufen, mit der Vorgabe
            logger.warning('Mesh3daikostuemstufe: Einstellung nicht lesbar (%s) — Vorgabe %d', fehler, cls.VORGABE)
            return cls.VORGABE

    @classmethod
    def text(cls, wert):
        return dict(cls.WERTE).get(wert, str(wert))

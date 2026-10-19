# -*- coding: utf-8 -*-
"""Netzvorratwahl — bis zu welcher Stufe die Anzeigen der Genesis-Figuren dauerhaft abgelegt werden (19.10.2026).

Edgar, 19.10.2026: „bei jedem Modell, das gespeichert ist, direkt alles speichern für alle Anzeigen … sodass sie beim Laden schnell angezeigt werden" und
„mach die Speicherung einstellbar, bei Einstellungen - Charakter. Default: alles bis ultrafein". Die Wahl liegt in `AppSettings.ui_prefs` unter `SCHLUESSEL`
(Seite Einstellungen → Charakter, `core/api/einstellungen/szenenseite.py`); der Server liest sie je Netzanfrage (`G9antworten.liefern`, `G9modellvorrat`), der
Browser beim Laden (`static/viewer/charakter/starteinstellungen.js` → `Genesis9vorrat.einstellen`: was er nach dem Laden vorab füllt).

    aus        nichts dauerhaft — wie vor dem 19.10.2026 (der Antwortvorrat je Code-Fassung bleibt)
    grob       nur der Käfig (`?stufen=0`)
    fein       grob und die Ansichtsstufe
    ultrafein  alle drei (Vorgabe)

Die Stufe einer Anfrage ist die WIRKSAME Genesis-Stufe (`G9netzstufe.browser()`: 0 Käfig, 1 Ansicht, 2 Renderstufe), nicht die Angabe in der Adresse.
"""
import logging
import time

__all__ = ['Netzvorratwahl']

logger = logging.getLogger('core')


class Netzvorratwahl:
    SCHLUESSEL = 'netzvorrat'
    AUS = 'aus'
    VORGABE = 'ultrafein'
    #: Wert → Anzeigetext, in der Reihenfolge der Auswahl.
    WAHLEN = {
        'ultrafein': 'Alles bis ultrafein (Vorgabe)',
        'fein': 'Bis fein (grob und fein)',
        'grob': 'Nur grob',
        AUS: 'Aus — nichts dauerhaft ablegen',
    }
    #: Die Stufen in Reihenfolge; ihr Platz ist die Genesis-Stufe (0, 1, 2).
    STUFEN = ('grob', 'fein', 'ultrafein')
    #: So lange gilt eine gelesene Wahl (eine Datenbankfrage je Netzanfrage wäre zu viel; nach dem Speichern der Seite wirkt sie spätestens dann).
    FRIST_S = 5.0

    _gelesen = (0.0, None)

    @classmethod
    def aus(cls, prefs):
        """Die Wahl aus einem `ui_prefs`-Dict; Unbekanntes heißt Vorgabe."""
        wert = str((prefs or {}).get(cls.SCHLUESSEL) or cls.VORGABE)
        return wert if wert in cls.WAHLEN else cls.VORGABE

    @classmethod
    def gewaehlt(cls):
        """Die gespeicherte Wahl (höchstens `FRIST_S` alt) — ohne lesbare Einstellungen die Vorgabe."""
        zeit, wert = cls._gelesen
        if wert is not None and time.monotonic() - zeit < cls.FRIST_S:
            return wert
        try:
            from ..models import AppSettings
            wert = cls.aus(AppSettings.load().ui_prefs)
        except Exception as fehler:  # noqa: BLE001 — ohne Datenbank (Skript, Test) gilt die Vorgabe
            logger.debug('Netzvorratwahl: Einstellung nicht lesbar (%s) — %s', fehler, cls.VORGABE)
            wert = cls.VORGABE
        cls._gelesen = (time.monotonic(), wert)
        return wert

    @classmethod
    def behalten(cls, stufe, wahl=None):
        """Wird eine Antwort der Genesis-Stufe `stufe` (0, 1, 2) dauerhaft abgelegt?"""
        wahl = wahl or cls.gewaehlt()
        if wahl == cls.AUS or wahl not in cls.STUFEN:
            return False
        try:
            return 0 <= int(stufe) <= cls.STUFEN.index(wahl)
        except (TypeError, ValueError):
            return False

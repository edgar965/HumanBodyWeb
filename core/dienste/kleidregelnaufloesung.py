# -*- coding: utf-8 -*-
"""Kleidregelnaufloesung — die Wahl der Kleidungsregeln beim Start einer Rechnung in den Test schreiben (21.11.2026, Edgar: „mach weiter mit dem Plan“; Konzept
`Docu/konzepte/2026-11-21_bibliothek-anpassen-konzept.md`, Abschnitt 10, Punkt 4: „Beim Start einer Rechnung wird die geltende Wahl einmal aufgelöst und in die `einstellung.json` des Tests
geschrieben; die Kette liest nur dort“).

Die Kette läuft im Skriptdienst ohne Django und liest die Wahl in `meshgenesis/meshgenesis_kleidregeln.py` (`Kleidregeln.lesen`): zuletzt gesetzt gewinnt — Lauf (`einstellung.json` →
`kleider_regeln`), darüber der Job (`job.json` → `pshuman.kleider_regeln`, gesetzt auf der Foto-Genesis-Seite). Hier kommt die unterste Ebene dazu: die Einstellung der App
(`AppSettings.ui_prefs`, `kleider_regel_<Kennung>` = '1' / '0', Seite `/settings/kleider/`); ohne Eintrag gilt die Voreinstellung `wie_bisher`. Jeder Start schreibt sie neu — wer die
Wahl für einen einzelnen Job festhalten will, stellt sie am Job ein.

    Kleidregelnaufloesung.wahl()                  # {Kennung: bool} aus den Einstellungen der App
    Kleidregelnaufloesung.schreiben(kennung)      # in `einstellung.json` des Tests → die geschriebene Wahl
"""
import json
import logging

from core.atomic_write import AtomarSchreiber

from .kleidregelnkatalog import Kleidregelnkatalog
from .meshgenesistest import Meshgenesistest

logger = logging.getLogger('core')

__all__ = ['Kleidregelnaufloesung']


class Kleidregelnaufloesung:
    #: Feld in `einstellung.json`, wie `Kleidregeln.FELD` der Kette
    FELD = 'kleider_regeln'

    @classmethod
    def wahl(cls, prefs=None):
        """{Kennung: bool} der App-Einstellung (`prefs` = `ui_prefs`, sonst aus der Datenbank)."""
        if prefs is None:
            from ..models import AppSettings
            prefs = dict(AppSettings.load().ui_prefs or {})
        return {r['kennung']: r['an'] for g in Kleidregelnkatalog.regeln(prefs) for r in g['regeln']}

    @classmethod
    def schreiben(cls, kennung, prefs=None):
        """Die Wahl der App in `einstellung.json` des Tests `kennung`; fehlt der Test oder die Datei, geschieht nichts → die Wahl oder None."""
        datei = Meshgenesistest.ordner() / kennung / 'einstellung.json'
        try:
            alt = json.loads(datei.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            logger.warning('Kleidregelnaufloesung: %s hat keine lesbare einstellung.json — Wahl nicht geschrieben', kennung)
            return None
        wahl = cls.wahl(prefs)
        AtomarSchreiber.json_schreiben(datei, dict(alt, **{cls.FELD: wahl}))
        return wahl

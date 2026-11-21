# -*- coding: utf-8 -*-
"""Fotogenesiskleiderregeln — die Kleidungsregeln eines Foto-Genesis-Jobs (21.11.2026, Edgar: „mach weiter mit dem Plan“; Konzept `Docu/konzepte/2026-11-21_bibliothek-anpassen-konzept.md`,
Abschnitt 10, Stufe 4: „der Block am Job“).

Am Job steht `pshuman.kleider_regeln` = {Kennung: true | false} in der `job.json`; eine Kennung, die dort fehlt, folgt den Einstellungen der App (`/settings/kleider/`,
`Kleidregelnaufloesung`). Der Job geht vor: die Kette liest ihn in `Kleidregeln.lesen` (`Hautohneki.jobs`) nach der Wahl aus `einstellung.json`. Die Foto-Genesis-Seite zeigt je Regel
eine Auswahl „wie Einstellungen“ / „an“ / „aus“ und schickt {kleider_regeln: {Kennung: true | false | null}} an `POST /api/fotogenesis/<job>/pshuman/`; `null` nimmt die eigene Wahl zurück.

    Fotogenesiskleiderregeln.zeilen(job)                  # Zeilen für die Seite: {kennung, name, text, app_an, wahl: 'einstellung' | 'an' | 'aus'}
    Fotogenesiskleiderregeln.mischen(alt, rumpf)          # neue Wahl des Jobs aus der alten und der Anfrage; ValueError bei Unbekanntem
"""
import json

from .kleidregelnaufloesung import Kleidregelnaufloesung
from .kleidregelnkatalog import Kleidregelnkatalog

__all__ = ['Fotogenesiskleiderregeln']


class Fotogenesiskleiderregeln:
    FELD = 'kleider_regeln'

    @classmethod
    def lesen(cls, info):
        """{Kennung: bool} der Wahl am Job (`job.json`-Inhalt); Unbekanntes und Nicht-Wahrheitswerte zählen nicht."""
        roh = (info.get('pshuman') or {}).get(cls.FELD)
        if not isinstance(roh, dict):
            return {}
        bekannt = {r['kennung'] for g in Kleidregelnkatalog.regeln({}) for r in g['regeln']}
        return {k: v for k, v in roh.items() if k in bekannt and isinstance(v, bool)}

    @classmethod
    def mischen(cls, alt, rumpf):
        """Die neue Wahl: `alt` ({Kennung: bool}) mit `rumpf` ({Kennung: true | false | null}) überschrieben, `null` löscht. `ValueError` bei unbekannter Kennung oder anderem Wert."""
        if not isinstance(rumpf, dict):
            raise ValueError('kleider_regeln: erwartet {Kennung: true | false | null}')
        bekannt = {r['kennung'] for g in Kleidregelnkatalog.regeln({}) for r in g['regeln']}
        fremd = sorted(set(rumpf) - bekannt)
        if fremd:
            raise ValueError('kleider_regeln: unbekannte Regeln %s' % (fremd,))
        neu = dict(alt)
        for kennung, wert in rumpf.items():
            if wert is None:
                neu.pop(kennung, None)
            elif isinstance(wert, bool):
                neu[kennung] = wert
            else:
                raise ValueError('kleider_regeln.%s %r: erlaubt true, false oder null' % (kennung, wert))
        return neu

    @classmethod
    def zeilen(cls, job, prefs=None):
        """Zeilen für den Block der Seite, nach den Gruppen des Katalogs; `wahl` 'einstellung' (folgt der App), 'an' oder 'aus' (eigene Wahl des Jobs)."""
        try:
            info = json.loads((job['ordner'] / 'job.json').read_text(encoding='utf-8'))
        except (KeyError, OSError, ValueError):
            return []
        eigen = cls.lesen(info)
        if prefs is None:
            from ..models import AppSettings
            prefs = dict(AppSettings.load().ui_prefs or {})
        app = Kleidregelnaufloesung.wahl(prefs)
        return [{'kennung': r['kennung'], 'name': r['name'], 'text': r['text'], 'gruppe': g['name'], 'app_an': app[r['kennung']],
                 'wahl': 'einstellung' if r['kennung'] not in eigen else ('an' if eigen[r['kennung']] else 'aus')}
                for g in Kleidregelnkatalog.regeln(prefs) for r in g['regeln']]

# -*- coding: utf-8 -*-
u"""Hbkleidprobe — jedes Genesis-Kleidungsstück auf den HumanBody-Grundfiguren.

Edgar (25.09.2026): „was muss ich nun tun, um dies auch für HumanBody verwendbar
machen, alle Genesis Kleider?" — nichts, der Weg „Daz auf HumanBody" nimmt jedes
Stück der Garderobe; offen war, wie gut sie SITZEN. Dann: „mach den Probelauf".

Je Stück und Geschlecht `Eigenstueckprobe.humanbody` (derselbe Endpunkt wie der
Browser, `G9kleidhumanbody.antwort`, vier Ansichten pyrender, Hautpixel vor dem Stoff
binnen 2 cm). Ergebnis je Zeile in `ergebnis.json` im Zielordner, nach jedem Stück
atomar geschrieben — ein abgebrochener Lauf setzt fort (`neu=False`).
"""
import logging
import time
from pathlib import Path

from core.atomic_write import AtomarSchreiber

logger = logging.getLogger('core')

__all__ = ['Hbkleidprobe']


class Hbkleidprobe:
    u"""`laufen(melden)` → Zeilen `{id, name, kategorie, geschlecht, pixel, teile, sekunden, fehler}`."""

    GESCHLECHTER = ('female', 'male')
    DATEI = 'ergebnis.json'

    def __init__(self, ziel, nur=None, geschlechter=None, neu=False):
        self.ziel = Path(ziel)
        self.nur = nur
        self.geschlechter = tuple(geschlechter or self.GESCHLECHTER)
        self.neu = neu

    def stuecke(self):
        from Genesis9.garderobe import G9garderobe
        aus = [e for e in G9garderobe.liste() if e.get('art') == 'kleidung' and e.get('zeigbar')]
        if self.nur:
            aus = [e for e in aus if self.nur.lower() in (e['id'] + ' ' + e.get('name', '')).lower()]
        return aus

    def _alt(self):
        import json
        try:
            zeilen = json.loads((self.ziel / self.DATEI).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {}
        return {(z['id'], z['geschlecht']): z for z in zeilen}

    def laufen(self, melden=None):
        from core.dienste.eigenstueckprobe import Eigenstueckprobe
        probe = Eigenstueckprobe()
        stuecke = self.stuecke()
        fertig = {} if self.neu else self._alt()
        gesamt = len(stuecke) * len(self.geschlechter)
        nummer = 0
        for eintrag in stuecke:
            for geschlecht in self.geschlechter:
                nummer += 1
                schluessel = (eintrag['id'], geschlecht)
                if schluessel in fertig and not fertig[schluessel].get('fehler'):
                    continue
                zeile = self._probe(probe, eintrag, geschlecht)
                fertig[schluessel] = zeile
                AtomarSchreiber.json_schreiben(self.ziel / self.DATEI, list(fertig.values()))
                if melden:
                    melden('[%d/%d] %s %s: %s (%.0f s)' % (
                        nummer, gesamt, geschlecht, eintrag['id'],
                        ('FEHLER ' + zeile['fehler']) if zeile['fehler'] else '%d Pixel' % zeile['pixel'],
                        zeile['sekunden']))
        return list(fertig.values())

    def _probe(self, probe, eintrag, geschlecht):
        from Genesis9.garderobekategorien import G9garderobekategorien
        start = time.time()
        zeile = {'id': eintrag['id'], 'name': eintrag.get('name', ''),
                 'kategorie': G9garderobekategorien.vorgabe(eintrag), 'geschlecht': geschlecht,
                 'pixel': None, 'teile': 0, 'fehler': ''}
        try:
            ergebnis = probe.humanbody(eintrag['id'], self.ziel / geschlecht / eintrag['id'], geschlecht)
            zeile.update(pixel=ergebnis['pixel'], teile=ergebnis['teile'])
        except Exception as fehler:                      # noqa: BLE001 — ein Stück hält den Lauf nicht auf
            logger.exception('HB-Probe %s (%s) gescheitert', eintrag['id'], geschlecht)
            zeile['fehler'] = ('%s: %s' % (type(fehler).__name__, fehler))[:300]
        zeile['sekunden'] = round(time.time() - start, 1)
        return zeile

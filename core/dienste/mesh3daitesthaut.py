# -*- coding: utf-8 -*-
"""Mesh3daitesthaut — die Haut der KI auf der Figur einer Testseite (23.10.2026 nachts, Edgar: „Haut: Die Haut-KI ist nicht angebunden, die Figur trägt die Grundhaut“ → „mach alles“).

Die Figur eines Tests trägt je Material ein Bild der Grundhaut (`form_<g>/anzeige/bilder/m<i>.jpg`). Hat die Stufe 2 der KI die Haut dieses Tests gerechnet (`haut_<g>/1001…1005.jpg`,
`Stufe2hauteinsatz`), steht in `haut_<g>/anzeige.json`, welche Kachel auf welchem Bild liegt (`ProjektTemp/_wegwerf/mesh3dai_testhautbilder.py`: Überdeckung im UV-Raum — die Materialnamen
taugen dafür nicht). Diese Klasse liefert dann die Kachel statt der Grundhaut; dieselbe Zuordnung liest die Kostüm-Prüfung (`Kostuemszene._figurfarben`), damit sie misst, was die Seite zeigt.

    Mesh3daitesthaut.bild(kennung, geschlecht, name) -> Path | None     # None: Grundhaut (kein Lauf, keine Zuordnung)
    Mesh3daitesthaut.info(kennung, geschlecht)       -> {'lauf', 'gerechnet', 'bilder'} | None
"""
import json
import re

from .mesh3daitest import Mesh3daitest

__all__ = ['Mesh3daitesthaut']


class Mesh3daitesthaut:
    NAME = re.compile(r'^m\d{1,4}\.jpg$')
    KACHEL = re.compile(r'^10\d\d\.jpg$')

    @classmethod
    def info(cls, kennung, geschlecht):
        p = Mesh3daitest.pfad(kennung)
        if p is None or geschlecht not in Mesh3daitest.GESCHLECHTER:
            return None
        try:
            d = json.loads((p / ('haut_%s' % geschlecht) / 'anzeige.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        return d if isinstance(d.get('bilder'), dict) else None

    @classmethod
    def kacheln(cls, kennung, geschlecht):
        """`{'1001': Adresse, …}` der Kacheln, wenn die Seite sie zeigt (`info`) — als `fototextur` der Genesis-Figur (Bewegung und Exportleiste, `Genesis9fototextur`; 31.10.2026, Venus:
        die bewegte Figur trug bis dahin die Katalog-Haut G9 Feminine 01, Export und Render sahen anders aus als die Seite). Der Zeitstempel hält den Browser-Speicher frisch."""
        if cls.info(kennung, geschlecht) is None:
            return {}
        haut = Mesh3daitest.pfad(kennung) / ('haut_%s' % geschlecht)
        return {d.stem: '/api/mesh3dai/test/%s/figur/%s/bild/%s?t=%d' % (kennung, geschlecht, d.name, int(d.stat().st_mtime))
                for d in sorted(haut.glob('10??.jpg')) if cls.KACHEL.match(d.name)}

    @classmethod
    def bild(cls, kennung, geschlecht, name):
        if cls.KACHEL.match(str(name)) and cls.info(kennung, geschlecht) is not None:            # die Kachel selbst (`kacheln`)
            pfad = Mesh3daitest.pfad(kennung) / ('haut_%s' % geschlecht) / str(name)
            return pfad if pfad.is_file() else None
        if not cls.NAME.match(str(name)):
            return None
        d = cls.info(kennung, geschlecht)
        ziel = (d or {}).get('bilder', {}).get(str(name))
        if not ziel or not cls.KACHEL.match(str(ziel)):
            return None
        pfad = Mesh3daitest.pfad(kennung) / ('haut_%s' % geschlecht) / ziel
        return pfad if pfad.is_file() else None

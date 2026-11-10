# -*- coding: utf-8 -*-
"""Fotogenesisweitverdeckung — „Haut unter weiten Stücken“ auf der Jobseite von Foto-Genesis, unter dem Feld Genesis-Ergebnis (08.11.2026, Edgar: „diese extra regel möchte ich per UI auf der Jobseite
laufen lassen können? Unter dem Genesis View?“).

Ein Schritt nach der Kette wie „Haut angleichen“ (`Fotogenesishautangleich`): Er blendet am fertigen Test die Haut unter Robe, weiten Ärmeln und langen Röcken aus, wo sie in der Animation der Testseite
nie frei wird (`meshgenesis/meshgenesis_kostuem_weitverdeckung.py`, Regel und Messungen dort). Gerechnet wird im eigenen Prozess unter der GPU-Sperre (`meshgenesis/meshgenesis_kostuem_weitschritt.py`, die Ablage
`kleider_<g>/weitverdeckung/` ist dort beschrieben); diese Klasse startet ihn und liest den Stand. Rechnet die Kette das Kostüm neu, gilt das Ergebnis nicht mehr (Stempel der `eintrag.json`), die
Seite zeigt den Knopf wieder.

Läuft der Rechenlauf von Mesh-Genesis gerade an diesem Test, startet nichts: Beide schreiben dieselben Masken.
"""

import json
import logging
import os
import subprocess
import sys

import psutil
from django.conf import settings

from .auftragsarbeiter import Auftragsarbeiter
from .meshgenesisrechenschlange import Meshgenesisrechenschlange
from .meshgenesistest import Meshgenesistest

logger = logging.getLogger('core')

__all__ = ['Fotogenesisweitverdeckung']


class Fotogenesisweitverdeckung:
    ORDNER = 'weitverdeckung'
    SKRIPT = 'meshgenesis_kostuem_weitschritt.py'
    ANZEIGE = 'ANZEIGE '            # Zeilen des Laufs, die die Seite zeigt (`Kostuemweitschritt.ANZEIGE`)
    CUDA_CACHE = '4294967296'

    def __init__(self, kennung, geschlecht):
        self.kennung, self.g = kennung, geschlecht
        self.kleider = Meshgenesistest.pfad(kennung) / ('kleider_%s' % geschlecht)
        self.k = self.kleider / 'k'
        self.ablage = self.kleider / self.ORDNER

    @classmethod
    def fuer(cls, job):
        """Der Schritt zum Test des Jobs `job` — None ohne Test oder ohne Kostüm (`kleider_<g>/k/*/eintrag.json`)."""
        kennung = (job or {}).get('test')
        pfad = Meshgenesistest.pfad(kennung) if kennung else None
        if pfad is None:
            return None
        s = cls(kennung, Meshgenesistest.geschlecht(pfad, {}))
        return s if s.stempel() else None

    def stempel(self):
        """{Stück-ID: [Größe, Zeit]} aller `eintrag.json` des Kostüm-Wegs — die Rechnung der Kette (`Kostuemweitschritt.stempel_von`)."""
        from .meshgenesisrechenlauf import Meshgenesisrechenlauf
        return Meshgenesisrechenlauf.modul('meshgenesis_kostuem_weitschritt').Kostuemweitschritt.stempel_von(self.k)

    def _lesen(self, name):
        try:
            return json.loads((self.ablage / name).read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None

    def laeuft(self):
        try:
            pid = int((self.ablage / 'lauf.pid').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return False
        try:
            return psutil.Process(pid).is_running() and any(self.SKRIPT in teil for teil in psutil.Process(pid).cmdline())
        except (psutil.Error, OSError):
            return False

    def _zeile(self):
        """Letzte Zeile des laufenden Laufs für die Seite (nur Zeilen mit `ANZEIGE`)."""
        try:
            zeilen = (self.ablage / 'lauf.log').read_text(encoding='utf-8', errors='replace').splitlines()
        except OSError:
            return ''
        return next((z[len(self.ANZEIGE):] for z in reversed(zeilen) if z.startswith(self.ANZEIGE)), '')

    def _im_rechenlauf(self):
        lauf = Meshgenesisrechenschlange.laeuft()
        return bool(lauf and lauf.get('kennung') == self.kennung)

    def stand(self):
        laeuft = self.laeuft()
        erg = self._lesen('ergebnis.json')
        angewandt = bool(erg) and erg.get('stempel') == self.stempel()
        return {'ok': True, 'laeuft': laeuft, 'zeile': self._zeile() if laeuft else '', 'angewandt': angewandt,
                'befund': (erg or {}).get('befund') if angewandt else None, 'sekunden': (erg or {}).get('sekunden') if angewandt else None,
                'veraltet': bool(erg) and not angewandt, 'zustand': None if laeuft else self._lesen('zustand.json'), 'rechenlauf': self._im_rechenlauf()}

    def starten(self, zuruecksetzen=False):
        """Den Lauf im eigenen Prozess starten (`zuruecksetzen`: die Masken des Kostümlaufs zurück, ohne Karte). `ValueError`, wenn der Rechenlauf von Mesh-Genesis an diesem Test rechnet."""
        if self.laeuft():
            return
        if self._im_rechenlauf():
            raise ValueError('Der Test wird gerade von Mesh-Genesis gerechnet — danach noch einmal')
        self.ablage.mkdir(exist_ok=True)
        (self.ablage / 'zustand.json').unlink(missing_ok=True)
        meshgenesis = settings.TOOLS_ROOT / 'meshgenesis'
        befehl = [sys.executable, '-u', str(meshgenesis / self.SKRIPT), self.kennung, self.g] + (['--zuruecksetzen'] if zuruecksetzen else [])
        env = dict(os.environ, PYTHONIOENCODING='utf-8', CUDA_CACHE_MAXSIZE=self.CUDA_CACHE)
        with open(self.ablage / 'lauf.log', 'w', encoding='utf-8') as protokoll:
            p = subprocess.Popen(befehl, cwd=str(meshgenesis), env=env, stdin=subprocess.DEVNULL, stdout=protokoll, stderr=subprocess.STDOUT,
                                 creationflags=Auftragsarbeiter.flags() | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        (self.ablage / 'lauf.pid').write_text(str(p.pid), encoding='utf-8')
        logger.info('Haut unter weiten Stücken: %s für %s/%s gestartet (Prozess %d)', 'Zurücksetzen' if zuruecksetzen else 'Rechnen', self.kennung, self.g, p.pid)

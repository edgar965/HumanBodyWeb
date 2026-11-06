# -*- coding: utf-8 -*-
"""Ai2d3dhautangleich — Ablage und Lauf von „Haut angleichen“ eines Tests (05.11.2026, Edgar: „Vielleicht ein Schritt unabhängig von der Joberzeugung, danach? Ein paar slider wo man die Haut anpasst“).

Der Schritt gehört zum Job, nicht zur Kette: Er liest die fertigen Kacheln `haut_<g>/10xx.jpg` des Mesh3D-AI-Tests des Jobs, die Regler rechnen im Browser (`Ai2d3dhautangleich` in `viewer/ai2d3d/`),
Speichern schreibt die Kacheln zurück. `angleich/original/` hält die Kacheln, von denen die Regler ausgehen; die Tonfelder rechnet `KoerperKI_Fotos.Hautangleich` einmal je Haut.

Rechnet die Kette die Haut neu, sind die Kacheln weder das Original noch das zuletzt Gespeicherte: `_basis_gilt` wird falsch, der Stand zeigt wieder „vorbereiten“, und `vorbereiten` nimmt die neuen
Kacheln als Original. Ein gespeicherter Angleich geht dabei verloren (so auch roomguest-0c, 05.11.2026: `Hautohneki`- und Kostüm-Läufe schreiben `haut_<g>/` neu).
"""

import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from io import BytesIO

import psutil
from django.conf import settings
from PIL import Image

from core.atomic_write import AtomarSchreiber

from .auftragsarbeiter import Auftragsarbeiter
from .mesh3daitest import Mesh3daitest
from .mesh3daitesthaut import Mesh3daitesthaut

logger = logging.getLogger('core')

__all__ = ['Ai2d3dhautangleich']


class Ai2d3dhautangleich:
    ORDNER = 'angleich'
    FASSUNG = 3
    KACHEL = re.compile(r'^10\d\d$')
    REGLER = {'dunkel': (0, 1), 'hell': (0, 1), 'unsichtbar': (0, 1), 'zeichnung': (0, 1), 'bezug': (-1, 1), 'reichweite': (0, 1)}
    DATEN = {'felder': 'felder.bin', 'netz': 'netz.bin'}

    def __init__(self, kennung, geschlecht, winkel=(0,)):
        self.kennung, self.g, self.winkel = kennung, geschlecht, winkel
        self.test = Mesh3daitest.pfad(kennung)
        self.haut = self.test / ('haut_%s' % geschlecht)
        self.ablage = self.haut / self.ORDNER
        self.original = self.ablage / 'original'

    @classmethod
    def fuer(cls, job):
        """Der Angleich des Tests zu `job` — None ohne Test oder ohne fertige Haut."""
        kennung = (job or {}).get('test')
        pfad = Mesh3daitest.pfad(kennung) if kennung else None
        if pfad is None:
            return None
        g = Mesh3daitest.geschlecht(pfad, {})
        winkel = sorted({f['winkel'] for f in job.get('fotos') or [] if f.get('winkel') is not None}) or [0]          # Was die Fotos sehen konnten, trägt den Bezugston (`Hautvertrauen`)
        return cls(kennung, g, winkel) if Mesh3daitesthaut.info(kennung, g) is not None else None

    def kacheln(self):
        return sorted(d for d in self.haut.glob('10??.jpg') if self.KACHEL.match(d.stem))

    @staticmethod
    def _stempel(datei):
        s = datei.stat()
        return [s.st_size, s.st_mtime_ns]

    def _gespeichert(self):
        try:
            return json.loads((self.ablage / 'stand.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return {}

    def _basis_gilt(self):
        """Liegen die Kacheln so, wie der Angleich sie kennt: als Original oder als zuletzt gespeichert?"""
        stempel = self._gespeichert().get('stempel', {})
        for d in self.kacheln():
            orig = self.original / d.name
            if not orig.is_file():
                return False
            jetzt = self._stempel(d)
            if jetzt != self._stempel(orig) and jetzt != stempel.get(d.stem):
                return False
        return bool(self.kacheln())

    def _kopf(self):
        try:
            kopf = json.loads((self.ablage / 'felder.json').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        return kopf if kopf.get('fassung') == self.FASSUNG else None

    def laeuft(self):
        try:
            pid = int((self.ablage / 'lauf.pid').read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return False
        return psutil.pid_exists(pid)

    def stand(self, job_id):
        adresse = '/api/2d3dai/%s/hautangleich/' % job_id
        kopf = self._kopf() if self._basis_gilt() else None
        marke = int((self.ablage / 'felder.json').stat().st_mtime) if kopf else 0
        gespeichert = self._gespeichert() if kopf else {}
        return {'ok': True, 'bereit': kopf is not None, 'laeuft': self.laeuft(), 'kopf': kopf, 'bilder': (Mesh3daitesthaut.info(self.kennung, self.g) or {}).get('bilder', {}),
                'regler': gespeichert.get('regler'), 'felder': '%sdaten/felder/?t=%d' % (adresse, marke), 'netz': '%sdaten/netz/?t=%d' % (adresse, marke),
                'original': {d.stem: '%soriginal/%s/?t=%d' % (adresse, d.stem, self._stempel(self.original / d.name)[1] // 10 ** 9) for d in self.kacheln() if (self.original / d.name).is_file()},
                'zeichnung': {d.stem: '%szeichnung/%s/?t=%d' % (adresse, d.stem, marke) for d in self.kacheln() if self.zeichnungsbild(d.stem)},
                'fehler': self._fehler()}

    def _fehler(self):
        """Letzte Zeilen des Protokolls, wenn der letzte Lauf ohne Ergebnis endete."""
        protokoll = self.ablage / 'lauf.log'
        if self.laeuft() or (self.ablage / 'felder.json').is_file() or not protokoll.is_file():          # ein Kopf alter Fassung ist kein Fehlschlag: `vorbereiten` räumt ihn vor dem Lauf weg
            return ''
        return ' '.join(protokoll.read_text(encoding='utf-8', errors='replace').splitlines()[-2:])[-300:]

    def vorbereiten(self):
        """Original sichern, wenn nötig, und die Tonfelder im eigenen Prozess rechnen lassen. Rechnet nichts, wenn sie gelten oder schon gerechnet werden."""
        if self.laeuft():
            return
        if not self._basis_gilt():
            self.ablage.mkdir(exist_ok=True)
            self.original.mkdir(exist_ok=True)
            for d in self.kacheln():
                shutil.copy2(d, self.original / d.name)
            for name in ('felder.json', 'stand.json'):
                (self.ablage / name).unlink(missing_ok=True)
        if self._kopf() is not None:
            return
        (self.ablage / 'felder.json').unlink(missing_ok=True)
        wurzel = settings.TOOLS_ROOT
        env = dict(os.environ, PYTHONPATH=os.pathsep.join(str(p) for p in (wurzel, wurzel / 'mesh3dai', wurzel / 'HumanBody')))
        with open(self.ablage / 'lauf.log', 'w', encoding='utf-8') as protokoll:
            p = subprocess.Popen([sys.executable, '-m', 'KoerperKI_Fotos.hautangleich', str(self.test), self.g, ','.join(str(w) for w in self.winkel)], cwd=str(wurzel), env=env,
                                 stdin=subprocess.DEVNULL, stdout=protokoll, stderr=subprocess.STDOUT, creationflags=Auftragsarbeiter.flags() | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        (self.ablage / 'lauf.pid').write_text(str(p.pid), encoding='utf-8')
        logger.info('Haut angleichen: Tonfelder für %s/%s gestartet (Prozess %d)', self.kennung, self.g, p.pid)

    def speichern(self, dateien, regler):
        """`dateien` {'1001': Bytes der JPEG-Kachel}, `regler` {Name: Wert in `REGLER`}. Schreibt die Kacheln und merkt sich ihre Stempel. `ValueError`, wenn etwas nicht passt, dann bleibt alles, wie es war."""
        if not self._basis_gilt() or self._kopf() is None:
            raise ValueError('Die Haut ist nicht vorbereitet')
        namen = {d.stem: d for d in self.kacheln()}
        if set(dateien) != set(namen):
            raise ValueError('Erwartet die Kacheln %s' % ', '.join(sorted(namen)))
        seite = self._kopf()['seite']
        for name, bytes_ in dateien.items():
            with Image.open(BytesIO(bytes_)) as bild:
                if bild.format != 'JPEG' or bild.size != (seite, seite):
                    raise ValueError('Kachel %s: %s %s, erwartet JPEG %d²' % (name, bild.format, bild.size, seite))
        werte = {k: float(regler[k]) for k in self.REGLER}
        if any(not self.REGLER[k][0] <= v <= self.REGLER[k][1] for k, v in werte.items()):
            raise ValueError('Regler außerhalb des Bereichs')
        for name, bytes_ in dateien.items():
            AtomarSchreiber.bytes_schreiben(namen[name], bytes_)
        AtomarSchreiber.json_schreiben(self.ablage / 'stand.json', {'regler': werte, 'stempel': {n: self._stempel(d) for n, d in namen.items()}, 'gespeichert': time.strftime('%Y-%m-%dT%H:%M:%S')})
        logger.info('Haut angleichen: %s/%s gespeichert, Regler %s', self.kennung, self.g, werte)

    def zuruecksetzen(self):
        """Die Kacheln wieder auf das Original. `ValueError`, wenn die Haut inzwischen neu gerechnet wurde (dann gibt es nichts zurückzusetzen)."""
        if not self._basis_gilt():
            raise ValueError('Die Haut wurde neu gerechnet, das Original gilt nicht mehr')
        for d in self.kacheln():
            shutil.copy2(self.original / d.name, d)
        (self.ablage / 'stand.json').unlink(missing_ok=True)

    def datei(self, name):
        pfad = self.ablage / self.DATEN[name] if name in self.DATEN else None
        return pfad if pfad is not None and pfad.is_file() else None

    def originalbild(self, kachel):
        pfad = self.original / ('%s.jpg' % kachel)
        return pfad if self.KACHEL.match(str(kachel)) and pfad.is_file() else None

    def zeichnungsbild(self, kachel):
        pfad = self.ablage / 'zeichnung' / ('%s.jpg' % kachel)
        return pfad if self.KACHEL.match(str(kachel)) and pfad.is_file() else None

# -*- coding: utf-8 -*-
u"""Figurfilm — der Unterprozess der Pipeline „HumanBody-Figur (DEF-Skelett)".

    python figurfilm.py --modell <name>.json --bvh <datei> --ausgabe <mp4> [Felder]

Derselbe Weg wie „Video erzeugen" im Animations-Reiter der Szene
(`TheatreJS/ModelPhysik/filmlauf.py`), nur ohne Browser: Die Figur kommt
aus der gespeicherten Modelldatei (`Modellfigur`), die Bewegung aus einer
BVH-Datei, und statt einer Fortschrittsdatei allein schreibt der Prozess
`Effekte: …`-Zeilen ins Protokoll, die der `Effektbeobachter` liest.

Was anders ist als in `Filmlauf`:
- Bildgroesse aus den Parametern (dort fest 720 x 900).
- H.264 ueber ffmpeg (`Videokodierer`) statt `mp4v` aus OpenCV — Chrome
  spielt MPEG-4 Teil 2 nicht ab, und der Ausgabeschirm der Seite ist ein
  `<video>`.
- Die Bilder gehen als PNG in einen Ordner NEBEN der Ausgabe (Projekt, nie
  System-Temp) und werden nach dem Kodieren geloescht.
- Bericht `<ausgabe>.json` im Aufbau der Blender-Pipeline (`parameter`,
  `sekunden`, `figur`, `bilder`, `bildrate`, `video`) plus die Bilanz des
  Films (Ruheprobe, Sitz, Gleichlauf je Teil).
"""
import json
import os
import sys
import time

WURZEL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELPHYSIK = os.path.join(WURZEL, 'TheatreJS', 'ModelPhysik')
for pfad in (WURZEL, MODELPHYSIK):
    if pfad not in sys.path:
        sys.path.insert(0, pfad)

from effekte.figurparameter import Figurparameter          # noqa: E402
from effekte.figur.modellfigur import Modellfigur          # noqa: E402
from effekte.figur.effektfilmlauf import Effektfilmlauf    # noqa: E402


class Figurfilm:

    PRAEFIX = 'Effekte: '

    def __init__(self, parameter):
        self.p = parameter
        self.ausgabe = os.path.abspath(parameter.ausgabe)
        self.stamm = os.path.splitext(self.ausgabe)[0]
        self.ablage = self.stamm + '_lauf'
        self.zeiten = {}
        self.begonnen = time.time()
        self.stuecke = []
        self.stoffbericht = None

    # ------------------------------------------------------------- Meldung

    def melden(self, phase, anteil):
        u"""Bruchform `n / 100` — `Logbeobachter.BRUCH` liest sie."""
        print(u'%s%s — %d / 100' % (self.PRAEFIX, phase, int(round(anteil * 100))),
              flush=True)

    # -------------------------------------------------------------- Ablauf

    def laufen(self):
        from bvh_nach_anim import Animschreiber
        Animschreiber._django()
        os.makedirs(os.path.dirname(self.ausgabe) or '.', exist_ok=True)
        os.makedirs(self.ablage, exist_ok=True)
        modell = Modellfigur(self.p.modell)
        self.melden(u'Modell %s' % modell.name, 0.0)
        self.stuecke = modell.stuecke(self.ablage)
        auftrag = self._auftrag(modell)
        auftrag_pfad = os.path.join(self.ablage, 'auftrag.json')
        with open(auftrag_pfad, 'w', encoding='utf-8') as datei:
            json.dump(auftrag, datei, indent=1, ensure_ascii=False)
        lauf = Effektfilmlauf(auftrag_pfad, self)
        code = lauf.laufen()
        if code != 0 or not os.path.isfile(self.ausgabe):
            stand = lauf.stand()
            raise SystemExit(u'Film abgebrochen: %s' % (stand.get('fehler') or stand))
        self._bericht(modell, lauf)
        self.melden(u'Fertig', 1.0)
        return 0

    def _auftrag(self, modell):
        u"""Der Auftrag im Aufbau von `filmlauf.py`, aus Modell und Parametern."""
        return {
            'body_type': modell.koerpertyp(),
            'morphs': modell.morphs(),
            'stuecke': self.stuecke,
            'bvh': os.path.abspath(self.p.bvh),
            'ab_sekunden': float(self.p.ab),
            'sekunden': float(self.p.bilder) / float(self.p.fps),
            'fps': float(self.p.fps),
            'physik_mm': float(self.p.physik),
            'breite': int(self.p.breite), 'hoehe': int(self.p.hoehe),
            'ziel': self.ausgabe,
            'fortschritt': os.path.join(self.ablage, 'fortschritt.json'),
        }

    # ------------------------------------------------------------- Bericht

    def _bericht(self, modell, lauf):
        bilanz = {}
        pfad = self.ausgabe + '.json'
        if os.path.isfile(pfad):
            with open(pfad, encoding='utf-8') as datei:
                bilanz = json.load(datei)
            os.remove(pfad)
        self.zeiten['gesamt'] = round(time.time() - self.begonnen, 1)
        bericht = {
            'pipeline': 'figur_def',
            'parameter': {n: getattr(self.p, n) for n in self.p.namen()},
            'modell': self.p.modell, 'bvh': self.p.bvh,
            'sekunden': self.zeiten,
            'figur': modell.beschreibung(),
            'bilder': bilanz.get('bilder', 0),
            'bildrate': self.p.fps,
            'bildrate_bvh': bilanz.get('quell_fps'),
            'schritt': bilanz.get('schritt'),
            'wurzelweg_m': bilanz.get('wurzelweg_m'),
            'teile': bilanz.get('teile', []),
            'stoff': self.stoffbericht,
            'video': self.ausgabe,
        }
        with open(self.stamm + '.json', 'w', encoding='utf-8') as datei:
            json.dump(bericht, datei, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    # Das Protokoll liest der Server als UTF-8; umgeleitet schriebe Python
    # unter Windows cp1252, und aus dem Gedankenstrich der Meldung wuerde
    # auf der Seite ein Ersatzzeichen (gemessen 12.09.2026).
    for strom in (sys.stdout, sys.stderr):
        if hasattr(strom, 'reconfigure'):
            strom.reconfigure(encoding='utf-8', errors='replace')
    sys.exit(Figurfilm(Figurparameter.aus_argv(sys.argv[1:])).laufen())

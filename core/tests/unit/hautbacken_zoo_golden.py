# -*- coding: utf-8 -*-
"""Hautbackenzoo, Golden-Daten — Blenders Ergebnisse des Zoos (`hautbacken_zoo.py`) in einer Form, die ins Repository passt und ohne Blender läuft.

    Hautbackenzoogolden.packen(zoo, ziel)           # aus dem Arbeitsordner des Zoos (Blender-CPU-Läufe, `ergebnis_cpu/`) — nur zum Erzeugen
    zoo = Hautbackenzoogolden(ziel)                 # die Tests: dieselbe Schnittstelle wie `Hautbackenzoo` (`lokal`, `golden`, `vergleichen`)

Ordner `ziel` (zusammen ~4 MB): `netz.npz` (die Netzdaten des Körpers, für alle Sätze gleich, dazu die Ruhelage `lage`), `graphen.json` (der Knotengraph je Material, wie ihn
`blendexport.py` schreibt), `saetze.json` (Namen je Satz), `material.npz` (das Material je Dreieck und Satz), `golden_<kanal>.png` (Blenders Bilder, alle Sätze untereinander) und
`bilder/*.png` (die Eingangsbilder der Materialien). Blender-Stand: 5.2.2, Cycles auf der CPU (ohne die Rundung der GPU-Texturhardware), 256 px, eine Probe je Texel.
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image

from core.tests.unit.hautbacken_zoo import Hautbackenzoo

__all__ = ['Hautbackenzoogolden']


class Hautbackenzoogolden(Hautbackenzoo):
    def __init__(self, ordner, px=256, je_satz=8):
        super().__init__(ordner, px, je_satz, 'CPU')
        self._graphen = json.loads((self.ordner / 'graphen.json').read_text(encoding='utf-8'))
        self._saetze = json.loads((self.ordner / 'saetze.json').read_text(encoding='utf-8'))
        self._netz = {k: v for k, v in np.load(self.ordner / 'netz.npz').items()}
        self._material = np.load(self.ordner / 'material.npz')
        self._bilder = {}

    def saetze(self):
        return len(self._saetze['namen'])

    # ------------------------------------------------------------------ Quelle des Satzes (statt der Dateien des Arbeitsordners)

    def lage(self):
        return self._netz['lage']

    def satz_daten(self, satz):
        """`(netz-Eintrag, npz, Namen, spec_lesen(material))` — die Materialien eines Satzes aus den gepackten Daten."""
        namen = self._saetze['namen'][satz]
        npz = {k: v for k, v in self._netz.items() if k != 'lage'}
        npz['material'] = self._material['satz_%02d' % satz]
        netz = dict(self._saetze['netz'], materialien=[{'name': n, 'graph': n} for n in namen])
        return netz, npz, namen, self.spec

    def spec(self, material):
        spec = json.loads(json.dumps(self._graphen[material['graph']]))
        for bild in spec['bilder'].values():
            bild['datei'] = str(self.ordner / 'bilder' / Path(bild['datei']).name)
        return spec

    def golden(self, satz):
        h = self.px
        aus = {}
        for kanal in self.KANAELE:
            if kanal not in self._bilder:
                self._bilder[kanal] = np.asarray(Image.open(self.ordner / ('golden_%s.png' % kanal)).convert('RGB'))
            aus[kanal] = self._bilder[kanal][satz * h:(satz + 1) * h]
        return aus

    # ------------------------------------------------------------------ Erzeugen

    @staticmethod
    def packen(zoo, ziel):
        """Packt den Arbeitsordner `zoo` (`Hautbackenzoo`, mit Blender-CPU-Läufen aller Sätze) nach `ziel`."""
        ziel = Path(ziel)
        (ziel / 'bilder').mkdir(parents=True, exist_ok=True)
        # Der Export schreibt Farbattribute nur, wenn ein Graph sie liest: die Netzdaten stammen aus dem Satz mit den meisten Arrays (er hat sie alle).
        def arrays(satz):
            e = zoo.ordner / ('satz_%02d' % satz) / 'export'
            return e, json.loads((e / 'inventar.json').read_text(encoding='utf-8'))['netze'][0]

        basis = max(range(zoo.saetze()), key=lambda s: len(np.load(arrays(s)[0] / arrays(s)[1]['datei']).files))
        z0, inventar = arrays(basis)
        netz = {k: v for k, v in np.load(z0 / inventar['datei']).items() if k != 'material'}
        netz['lage'] = np.load(zoo.ordner / 'lage.npy').astype(np.float32)
        np.savez_compressed(ziel / 'netz.npz', **netz)
        graphen, namen, material = {}, [], {}
        for satz in range(zoo.saetze()):
            s = zoo.ordner / ('satz_%02d' % satz)
            n = json.loads((s / 'namen.json').read_text(encoding='utf-8'))
            e = json.loads((s / 'export' / 'inventar.json').read_text(encoding='utf-8'))['netze'][0]
            for name, m in zip(n, e['materialien']):
                graphen[name] = json.loads((s / 'export' / m['graph']).read_text(encoding='utf-8'))
            namen.append(n)
            material['satz_%02d' % satz] = np.load(s / 'export' / e['datei'])['material'].astype(np.uint8)
        np.savez_compressed(ziel / 'material.npz', **material)
        (ziel / 'graphen.json').write_text(json.dumps(graphen, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        (ziel / 'saetze.json').write_text(json.dumps({'namen': namen, 'netz': {k: v for k, v in inventar.items() if k != 'materialien'}}, ensure_ascii=False), encoding='utf-8')
        for kanal in zoo.KANAELE:
            stapel = np.concatenate([np.asarray(Image.open(zoo.ordner / ('satz_%02d' % s) / 'ergebnis_cpu' / ('haut_1001_%s.png' % kanal)).convert('RGB'))
                                     for s in range(zoo.saetze())], axis=0)
            Image.fromarray(stapel).save(ziel / ('golden_%s.png' % kanal), optimize=True)
        for name, feld in Hautbackenzoo.bilder().items():
            Hautbackenzoo.bild_schreiben(ziel / 'bilder' / (name + '.png'), feld)
        return ziel

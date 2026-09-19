# -*- coding: utf-8 -*-
u"""G9frisur — eine HumanBody-Frisur (GLB aus `hairstyles/`) auf dem Kopf einer
Genesis-9-Figur.

WARUM (Edgar, 19.09.2026: „bei Genesis sehe ich nicht alle Assets die ich bei
HumanBody sehe, z.B. Haar. mach das, teste auch ob das Haar von HumanBody /
MakeHuman auf Genesis fittet"): Die drei GLB-Frisuren sind fuer den
HumanBody-Kopf modelliert (`_loadHairForCharacter` haengt sie starr an den
Kopfknochen). Der Genesis-Kopf ist anders geformt — gemessen an Ursula1
gegen die HumanBody-Frau (`_wegwerf/mess_haar_genesis.py`, Kopfpunkte ueber
die Hautgewichte `DEF-spine.006` bzw. `head`):

    HumanBody   17,4 cm hoch, 14,5 breit, 18,8 tief
    Genesis 9   18,4 cm hoch, 16,4 breit, 20,9 tief

Nur verschoben (Scheitel auf Scheitel) stecken 25 % der Haarpunkte im
Schaedel (bis 18 mm), gleichmaessig um 1,057 skaliert noch 21 %. ACHSWEISE
skaliert (Breite 1,136, Hoehe 1,057, Tiefe 1,108, um Scheitel und
Kastenmitte) sind es 1,4 % (bis 16 mm — Nacken und Ohren), und
`G9kollision.hinaus` hebt den Rest auf `ABSTAND` aus der Haut: 0 im Schaedel,
Hub hoechstens 18 mm (Dutt 54 mm — er sass im tieferen Genesis-Hinterkopf).
Das Haar liegt danach median 9–11 mm ueber der Kopfhaut, wie auf HumanBody
(dort 12,7 mm).

WAS AUF HUMANBODY IN DER HAUT STECKT, DARF ES AUCH HIER (Edgar, 19.09.2026
spaet: „Ballerina Dutt funktioniert nicht auf Genesis Modell"): Der Dutt
(`ballerina_dutt.glb`, 219 Punkte) ist eine Kugel von 9 cm, die auf
HumanBody zur Haelfte im Hinterkopf steckt — 75 Punkte bis 47 mm tief,
gewollt, man sieht nur die aeussere Haelfte. Punktweise auf `ABSTAND`
gehoben wurde die Kugel platt (10 x 7 x 10 cm -> 12 x 8 x 6,5 cm, Hub bis
54 mm; `_wegwerf/mess_dutt_genesis.py`). Deshalb bekommt jeder Punkt als
Ziel seine Tiefe auf HumanBody, wenn er dort in der Haut lag, sonst
`ABSTAND` (`zieltiefe`).

Gebunden wird alles an `head` (Gewicht 1): Die Frisur folgt dem Kopf, wie
auf HumanBody. Kein UV, keine Bilder — die Farbe setzt der Browser wie bei
HumanBody (`hairColorData`).
"""
import logging
import os

import numpy as np
from django.conf import settings

from Genesis9.kollision import G9kollision
from Genesis9.koerpernetz import G9koerpernetz

from .g9garmentfigur import G9garmentfigur
from .hbtraeger import Hbtraeger

logger = logging.getLogger('core')

__all__ = ['G9frisur']


class G9frisur:
    u"""HumanBody-Frisur (GLB) -> Netz auf dem Genesis-9-Kopf."""

    #: Kopfknochen beider Figuren.
    HB_KOPF = 'DEF-spine.006'
    G9_KOPF = 'head'
    #: Ab diesem Gewicht gehoert ein Punkt zum Kopf.
    KOPFGEWICHT = 0.5
    #: Mindestabstand des Haars zur Kopfhaut (Meter).
    ABSTAND = 0.002
    DURCHGAENGE = 3
    #: Kopfkasten der HumanBody-Grundfigur je Geschlecht — einmal gerechnet.
    _hb_kopf = {}

    def __init__(self, regler, geschlecht='female'):
        self.figur = G9garmentfigur(regler)
        self.geschlecht = 'male' if geschlecht == 'male' else 'female'

    # ------------------------------------------------------------ Frisur

    @classmethod
    def ordner(cls):
        return os.path.join(str(settings.HUMANBODY_DATA_DIR), 'hairstyles')

    @classmethod
    def pfad(cls, name):
        u"""Die GLB zu einem Frisurnamen — nur ein Dateiname, kein Weg."""
        name = os.path.basename(str(name or ''))
        if not name or name.startswith('.'):
            raise ValueError('Keine Frisur angegeben')
        pfad = os.path.join(cls.ordner(), name + '.glb')
        if not os.path.isfile(pfad):
            raise FileNotFoundError('Frisur %s nicht gefunden' % name)
        return pfad

    @classmethod
    def laden(cls, pfad):
        u"""(Punkte (N, 3), Dreiecke (M, 3)) der GLB in Weltlage (alle Knoten)."""
        import trimesh
        szene = trimesh.load(pfad, force='scene')
        punkte, dreiecke, versatz = [], [], 0
        for knoten in szene.graph.nodes_geometry:
            matrix, name = szene.graph.get(knoten)
            geo = szene.geometry[name]
            m = np.asarray(matrix, dtype=np.float64)
            p = np.asarray(geo.vertices, dtype=np.float64) @ m[:3, :3].T + m[:3, 3]
            punkte.append(p)
            dreiecke.append(np.asarray(geo.faces, dtype=np.int64) + versatz)
            versatz += len(p)
        if not punkte:
            raise ValueError('GLB ohne Flaechen: %s' % os.path.basename(pfad))
        return np.concatenate(punkte), np.concatenate(dreiecke)

    # -------------------------------------------------------------- Kopf

    @classmethod
    def kopf_hb(cls, geschlecht):
        u"""`{min, max, scheitel}` des HumanBody-Kopfs (Kaefig, Y oben)."""
        if geschlecht not in cls._hb_kopf:
            hb = Hbtraeger.laden(geschlecht, None, {}, {})
            kopf = list(hb['knochen']).index(cls.HB_KOPF)
            p = np.asarray(hb['punkte'])
            # Die Gewichte (Stufe 1) beginnen mit den Kaefigpunkten.
            maske = np.array([any(int(k) == kopf and w > cls.KOPFGEWICHT for k, w in hb['gewichte'][i])
                              for i in range(len(p))])
            cls._hb_kopf[geschlecht] = cls._kasten(p[maske])
        return cls._hb_kopf[geschlecht]

    def kopf_g9(self):
        haut = self.figur.haut()
        kopf = list(haut['knochen']).index(self.G9_KOPF)
        maske = ((np.asarray(haut['index']) == kopf)
                 & (np.asarray(haut['gewicht']) > self.KOPFGEWICHT)).any(axis=1)
        return self._kasten(self.figur.punkte()[maske])

    def zieltiefe(self, punkte):
        u"""Je Haarpunkt der Abstand zur Genesis-Haut, den er mindestens haben
        soll: `ABSTAND` — oder seine Tiefe auf HumanBody, wenn er dort in der
        Haut steckt (Modulkopf, der Dutt)."""
        hb = Hbtraeger.laden(self.geschlecht, None, {}, {})
        fein = np.asarray(hb['fein'], dtype=np.float64)
        tiefe = G9kollision.tiefe(punkte, fein, np.asarray(hb['fein_normalen'], dtype=np.float64),
                                  G9kollision.baum(fein))
        return np.minimum(tiefe, self.ABSTAND)

    @staticmethod
    def _kasten(p):
        if not len(p):
            raise ValueError('Kein Kopfpunkt gefunden')
        return {'min': p.min(axis=0), 'max': p.max(axis=0), 'scheitel': p[p[:, 1].argmax()]}

    # ------------------------------------------------------------- bauen

    def bauen(self, name, stufen=1):
        u"""Das Netz der Frisur auf dieser Figur: `{punkte, dreiecke, normalen,
        uv, gruppen, haut, name, hub_mm}` — Punkte in Browserlage (Y oben,
        Fuesse auf dem Boden), wie die Daz-Stuecke."""
        punkte, dreiecke = self.laden(self.pfad(name))
        ziel = self.zieltiefe(punkte)
        hb, g9 = self.kopf_hb(self.geschlecht), self.kopf_g9()
        skala = (g9['max'] - g9['min']) / np.maximum(hb['max'] - hb['min'], 1e-6)
        mitte_hb = self._bezug(hb)
        mitte_g9 = self._bezug(g9)
        gelegt = (punkte - mitte_hb) * skala + mitte_g9
        fein, normalen, baum = G9koerpernetz(self.figur.formung, stufen=stufen).koerperflaeche()
        frei = G9kollision.hinaus(gelegt, fein, normalen, abstand=ziel, baum=baum,
                                  durchgaenge=self.DURCHGAENGE)
        hub = float(np.linalg.norm(frei - gelegt, axis=1).max()) * 1e3
        logger.info('Genesis 9: Frisur %s — %d Punkte, Skala %.3f/%.3f/%.3f, Hub max %.1f mm',
                    name, len(frei), *skala, hub)
        n = len(frei)
        return {
            'punkte': frei, 'dreiecke': dreiecke,
            'normalen': Hbtraeger.nach_aussen(frei, Hbtraeger.normalen(frei, dreiecke)),
            'uv': None, 'gruppen': [], 'name': name, 'hub_mm': round(hub, 1),
            'haut': {'knochen': [self.G9_KOPF],
                     'index': np.zeros((n, 4), dtype=np.int64),
                     'gewicht': np.tile([1.0, 0.0, 0.0, 0.0], (n, 1))},
        }

    @staticmethod
    def _bezug(kasten):
        u"""Kastenmitte in Breite und Tiefe, Scheitel in der Hoehe."""
        lo, hi = kasten['min'], kasten['max']
        return np.array([(lo[0] + hi[0]) / 2, kasten['scheitel'][1], (lo[2] + hi[2]) / 2])

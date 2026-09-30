# -*- coding: utf-8 -*-
"""Haarengineblender — der EINE Blender-Arbeiter von „2D3D Kleider" (30.09.2026, nachts; Edgar: „blender aufrufe sind
möglich"). Alles, was Blender für eine Runde rechnet, geht durch diese Klasse — `BlenderNurUeberEinenArbeiterTest` hält
die übrigen Dienste des Bereichs Blender-frei.

Zwei Befehle: `drapieren(kennung, bilder, druck)` — ein Stück der Garderobe durch Blenders Cloth-Simulation gegen die
Grundfigur (`effekte/blender/haarengine/drapieren.py`), Ergebnis als eigener Morph `<kennung>.eigen.drapiert`
(`G9kleidmorphe.ablegen`), also linear stellbar wie jeder Regler; und `haar(sorte, name, knoten, ort, **parameter)` —
eine von Blenders Hair-Node-Gruppen auf das Stranghaar einer Frisur (`haarknoten.py`, Ortsgewicht als `Mask`), Ergebnis
`<sorte>.eigen.<name>`. Ein Aufruf je Befehl (Blender 5.2.2: Start 4–9 s, die Rechnung Sekunden) — kein dauerhafter
Arbeiter, weil beides selten in einer Runde läuft.

Die Rechnung liegt unter `<ablage>/arbeit/blender/`; Käfig und Körper gehen als `.npz` hin (Reihenfolge der Punkte
bleibt, kein Importer), die Punkte danach kommen als `.npz` zurück.
"""

import json
import logging
import time
from pathlib import Path

import numpy as np
from django.conf import settings

from ..atomic_write import AtomarSchreiber
from ..pipeline_process import PipelineProzess

logger = logging.getLogger('core')

__all__ = ['Haarengineblender']


class Haarengineblender:
    SKRIPT = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'haarengine' / 'drapieren.py'
    NAME = 'drapiert'
    ZEIT_S = 900

    def __init__(self, ordner):
        """`ordner`: der Arbeitsordner der Rechnung (z. B. `ablage.arbeit('blender')`)."""
        self.ordner = Path(ordner)

    def drapieren(self, kennung, bilder=24, druck=0.0, steifigkeit=15.0, name=NAME):
        """→ Steckbrief des Morphs `<kennung>.eigen.<name>` (RuntimeError, wenn Blender scheitert)."""
        from Genesis9.kleidmorphe import G9kleidmorphe
        teile, kaefige, _y0, _y1, _mitte, _e = G9kleidmorphe.kaefige(kennung)
        k_punkte, k_dreiecke, _n, _b, _boden = G9kleidmorphe.koerper()
        self.ordner.mkdir(parents=True, exist_ok=True)
        deltas, berichte = [], []
        for nummer, ((folger, _lage), punkte) in enumerate(zip(teile, kaefige, strict=True)):
            dreiecke = self._dreiecke(folger)
            if dreiecke is None or not len(dreiecke):
                deltas.append(np.zeros_like(punkte))
                continue
            stamm = self.ordner / ('%s_%d' % (kennung, nummer))
            np.savez_compressed(str(stamm) + '_koerper.npz', punkte=k_punkte.astype(np.float32),
                                dreiecke=np.asarray(k_dreiecke, dtype=np.int32))
            np.savez_compressed(str(stamm) + '_stueck.npz', punkte=np.asarray(punkte, dtype=np.float32),
                                dreiecke=np.asarray(dreiecke, dtype=np.int32))
            auftrag = {'koerper': str(stamm) + '_koerper.npz', 'stueck': str(stamm) + '_stueck.npz',
                       'aus': str(stamm) + '_nachher.npz', 'bericht': str(stamm) + '_bericht.json',
                       'bilder': int(bilder), 'druck': float(druck), 'steifigkeit': float(steifigkeit)}
            AtomarSchreiber.json_schreiben(Path(str(stamm) + '_auftrag.json'), auftrag)
            bericht = self._laufen(Path(str(stamm) + '_auftrag.json'), Path(auftrag['bericht']))
            with np.load(auftrag['aus']) as d:
                nachher = np.asarray(d['punkte'], dtype=np.float64)
            deltas.append(nachher - np.asarray(punkte, dtype=np.float64))
            berichte.append(bericht)
        brief = {'art': 'drapiert', 'bilder': int(bilder), 'druck': float(druck), 'steifigkeit': float(steifigkeit),
                 'blender': berichte}
        return G9kleidmorphe.ablegen(kennung, name, [f.kennung for f, _lage in teile], deltas, brief)

    # ------------------------------------------------------------ Haar-Knoten

    HAARSKRIPT = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'haarengine' / 'haarknoten.py'
    KNOTEN = ('trim', 'clump', 'curl', 'frizz', 'noise', 'straighten', 'roll', 'smooth', 'braid', 'displace', 'rotate')

    @staticmethod
    def _straehnen(segmente, anzahl):
        """`[Index-Feld je Strähne]` aus den Segmenten (S, 2) eines `G9strang` — jede Kette von Anfang bis Ende."""
        segmente = np.asarray(segmente, dtype=np.int64)
        naechster = np.full(anzahl, -1, dtype=np.int64)
        naechster[segmente[:, 0]] = segmente[:, 1]
        hat_vorgaenger = np.zeros(anzahl, dtype=bool)
        hat_vorgaenger[segmente[:, 1]] = True
        aus = []
        for start in np.flatnonzero((naechster >= 0) & ~hat_vorgaenger):
            kette, p = [int(start)], int(start)
            while naechster[p] >= 0 and len(kette) < anzahl:
                p = int(naechster[p])
                kette.append(p)
            aus.append(np.asarray(kette, dtype=np.int64))
        return aus

    @staticmethod
    def _eingang(name):
        """`length_factor` → „Length Factor" (die Sockets der Hair-Gruppen heißen so)."""
        return ' '.join(w.capitalize() for w in str(name).replace('-', '_').split('_'))

    def haar(self, sorte, name, knoten, ort=None, **parameter):
        """Eine Hair-Node-Gruppe auf das STRANGHAAR der Sorte → Steckbrief des Morphs `<sorte>.eigen.<name>`.
        `parameter`: Eingänge der Gruppe (`length_factor=0.5` → „Length Factor"); `ort` als Mask je Punkt."""
        from Genesis9.kleidmorphe import G9kleidmorphe
        from Genesis9.ortsmorph import G9ortsmorph
        if str(knoten) not in self.KNOTEN:
            raise ValueError('knoten: %s' % '|'.join(self.KNOTEN))
        teile, kaefige, y0, y1, mitte, eintrag = G9kleidmorphe.kaefige(sorte)
        if eintrag.get('art') != 'haar':
            raise ValueError(u'%s ist keine Frisur' % sorte)
        werte = {self._eingang(k): v for k, v in parameter.items()}
        self.ordner.mkdir(parents=True, exist_ok=True)
        deltas, berichte, straenge = [], [], 0
        for nummer, ((folger, _lage), punkte) in enumerate(zip(teile, kaefige, strict=True)):
            punkte = np.asarray(punkte, dtype=np.float64)
            if getattr(folger, 'ART', None) != 'strang':
                deltas.append(np.zeros_like(punkte))
                continue
            ketten = self._straehnen(folger.segmente, len(punkte))
            reihe = np.concatenate(ketten) if ketten else np.zeros(0, dtype=np.int64)
            if not len(reihe):
                deltas.append(np.zeros_like(punkte))
                continue
            maske = (G9ortsmorph.gewicht({'ort': dict(ort)}, punkte, y0, y1, mitte) if ort
                     else np.ones(len(punkte)))
            stamm = self.ordner / ('%s_%d_%s' % (sorte, nummer, knoten))
            np.savez_compressed(str(stamm) + '_straehnen.npz', punkte=punkte[reihe].astype(np.float32),
                                laengen=np.asarray([len(k) for k in ketten], dtype=np.int32),
                                maske=maske[reihe].astype(np.float32))
            auftrag = {'straehnen': str(stamm) + '_straehnen.npz', 'aus': str(stamm) + '_nachher.npz',
                       'bericht': str(stamm) + '_bericht.json', 'knoten': str(knoten), 'werte': werte}
            AtomarSchreiber.json_schreiben(Path(str(stamm) + '_auftrag.json'), auftrag)
            bericht = self._laufen(Path(str(stamm) + '_auftrag.json'), Path(auftrag['bericht']), self.HAARSKRIPT)
            with np.load(auftrag['aus']) as d:
                nachher = np.asarray(d['punkte'], dtype=np.float64)
            delta = np.zeros_like(punkte)
            delta[reihe] = nachher - punkte[reihe]
            deltas.append(delta)
            berichte.append(bericht)
            straenge += len(ketten)
        if not straenge:
            raise ValueError(u'%s hat kein Stranghaar — Kartenhaar nimmt haar_trim/clump/noise/… (G9haarops)' % sorte)
        brief = {'art': 'haarknoten', 'knoten': str(knoten), 'werte': werte, 'ort': ort, 'straehnen': straenge,
                 'blender': berichte}
        return G9kleidmorphe.ablegen(sorte, name, [f.kennung for f, _lage in teile], deltas, brief)

    @staticmethod
    def _dreiecke(folger):
        """Die Dreiecke des Käfigs eines Teils auf den DAZ-Punkten (die `punkte_zu` liefert): `folger.dreiecke` zeigt auf
        die an den UV-Nähten geteilten Browserpunkte (`G9netzteilung`), `folger.ursprung` führt sie auf den Daz-Punkt
        zurück. (T, 4) mit −1 (Vierecke) wird zu Dreiecken."""
        roh = getattr(folger, 'dreiecke', None)
        if roh is None:
            return None
        roh = np.asarray(roh)
        if roh.ndim == 2 and roh.shape[1] == 4:
            vier = roh[:, 3] >= 0
            aus = [roh[:, :3]]
            if vier.any():
                aus.append(roh[vier][:, [0, 2, 3]])
            roh = np.vstack(aus)
        roh = roh.reshape(-1, 3)
        ursprung = getattr(folger, 'ursprung', None)
        if ursprung is not None:
            roh = np.asarray(ursprung, dtype=np.int64)[roh]
        return roh

    def _laufen(self, auftrag, bericht, skript=None):
        t0 = time.perf_counter()
        skript = skript or self.SKRIPT
        pp = PipelineProzess.starten(
            [str(settings.BLENDER_EXE), '-b', '--factory-startup', '--python', str(skript), '--',
             '--auftrag', str(auftrag)],
            cwd=str(skript.parent),
            env_extra={'TMP': str(self.ordner), 'TEMP': str(self.ordner), 'PYTHONIOENCODING': 'utf-8'},
            stdout_lesen=False)
        try:
            pp.proc.wait(timeout=self.ZEIT_S)
        except Exception as fehler:  # noqa: BLE001 — Zeitgrenze: Prozessbaum beenden, dann melden
            pp.beenden()
            raise RuntimeError('Blender-Drapierung: Zeitgrenze %d s (%s)' % (self.ZEIT_S, fehler)) from None
        if not bericht.is_file():
            raise RuntimeError('Blender-Drapierung ohne Bericht: %s' % pp.fehlertext(1500))
        with open(bericht, encoding='utf-8') as fh:
            daten = json.load(fh)
        if daten.get('fehler'):
            raise RuntimeError('Blender-Drapierung: %s' % daten['fehler'])
        daten['sekunden'] = round(time.perf_counter() - t0, 1)
        logger.info('Blender-Drapierung %s: %s', auftrag.name, daten)
        return daten

# -*- coding: utf-8 -*-
"""Engine2d3dKleiderblender — der EINE Blender-Arbeiter von „2D3D Kleider" (30.09.2026, nachts; Edgar: „blender aufrufe sind
möglich"). Alles, was Blender für eine Runde rechnet, geht durch diese Klasse — `BlenderNurUeberEinenArbeiterTest` hält
die übrigen Dienste des Bereichs Blender-frei.

Zwei Befehle: `drapieren(kennung, bilder, druck)` — ein Stück der Garderobe durch Blenders Cloth-Simulation gegen die
Grundfigur (`effekte/blender/engine2d3dkleider/drapieren.py`), Ergebnis als eigener Morph `<kennung>.eigen.drapiert`
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

__all__ = ['Engine2d3dKleiderblender']


class Engine2d3dKleiderblender:
    SKRIPT = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'engine2d3dkleider' / 'drapieren.py'
    NAME = 'drapiert'
    ZEIT_S = 900
    #: Anteil der Höhe des Stücks, der beim Drapieren festbleibt (Bund, Schultern) — derselbe Wert wie bei `Kleiddrapierung`.
    FEST_OBEN = 0.08

    def __init__(self, ordner):
        """`ordner`: der Arbeitsordner der Rechnung (z. B. `ablage.arbeit('blender')`)."""
        self.ordner = Path(ordner)

    def drapieren(self, kennung, bilder=24, druck=0.0, steifigkeit=15.0, name=NAME, fest_oben=FEST_OBEN):
        """→ Steckbrief des Morphs `<kennung>.eigen.<name>` (RuntimeError, wenn Blender scheitert).

        `fest_oben`: das obere Band des Stücks (Anteil der Höhe, wie bei `Kleiddrapierung`) bleibt stehen — Bund, Schultern;
        sonst rutscht das Stück an der Figur hinunter. Die Schwerkraft fällt entlang −Y (Bühne), nicht mehr entlang −Z
        (Blenders Vorgabe, 02.10.2026 gemessen)."""
        from Genesis9.kleidmorphe import G9kleidmorphe
        teile, kaefige, y0, y1, _mitte, _e = G9kleidmorphe.kaefige(kennung)
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
            fest = np.asarray(punkte, dtype=np.float64)[:, 1] >= y1 - float(fest_oben) * (y1 - y0)
            auftrag = {'koerper': str(stamm) + '_koerper.npz', 'stueck': str(stamm) + '_stueck.npz',
                       'aus': str(stamm) + '_nachher.npz', 'bericht': str(stamm) + '_bericht.json',
                       'bilder': int(bilder), 'druck': float(druck), 'steifigkeit': float(steifigkeit),
                       'schwerkraft': [0.0, -9.81, 0.0], 'anheften': np.flatnonzero(fest).tolist()}
            AtomarSchreiber.json_schreiben(Path(str(stamm) + '_auftrag.json'), auftrag)
            bericht = self._laufen(Path(str(stamm) + '_auftrag.json'), Path(auftrag['bericht']))
            with np.load(auftrag['aus']) as d:
                nachher = np.asarray(d['punkte'], dtype=np.float64)
            delta = nachher - np.asarray(punkte, dtype=np.float64)
            delta[fest] = 0.0
            deltas.append(delta)
            bericht['fest'] = int(fest.sum())
            berichte.append(bericht)
        brief = {'art': 'drapiert', 'motor': 'blender', 'bilder': int(bilder), 'druck': float(druck),
                 'steifigkeit': float(steifigkeit), 'fest_oben': float(fest_oben), 'schwerkraft': 'Y unten',
                 'blender': berichte}
        return G9kleidmorphe.ablegen(kennung, name, [f.kennung for f, _lage in teile], deltas, brief)

    # ------------------------------------------------------------ Haar-Knoten

    HAARSKRIPT = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'engine2d3dkleider' / 'haarknoten.py'
    #: Verformende Knoten (Delta je Punkt → eigener Morph) — seit 01.10.2026 auch Shrinkwrap (Zielobjekt: die
    #: Grundfigur) und Attach — und erzeugende (Duplicate; Interpolate/Generate → Zusatzsträhnen `str.<name>`).
    #: Attach, Interpolate und Generate brauchen die Kopfhaut mit EINDEUTIGER UV (`G9kopfhaut`: Daz-Kappe oder Kopf der
    #: Grundfigur mit Genesis-UV): Die erste Fassung gab der Figur eine Draufsicht als UV, in der Kopf und Füße dieselben
    #: Werte haben — Attach versetzte alle 236.136 Pixie-Punkte 1,66 m, Interpolate lieferte 14 Einzelpunkte. Die
    #: Rückführung weist so ein Ergebnis weiter ab.
    KNOTEN = ('trim', 'clump', 'curl', 'frizz', 'noise', 'straighten', 'roll', 'smooth', 'braid', 'displace', 'rotate',
              'shrinkwrap', 'attach', 'duplicate', 'interpolate', 'generate')

    @staticmethod
    def _straehnen(segmente, anzahl):
        """`[Index-Feld je Strähne]` aus den Segmenten (S, 2) eines `G9strang` (`G9haarzusatz.ketten`)."""
        from Genesis9.haarzusatz import G9haarzusatz
        return G9haarzusatz.ketten(segmente, anzahl)

    @staticmethod
    def _eingang(name):
        """`length_factor` → „Length Factor" (die Sockets der Hair-Gruppen heißen so)."""
        return ' '.join(w.capitalize() for w in str(name).replace('-', '_').split('_'))

    def haar(self, sorte, name, knoten, ort=None, **parameter):
        """Eine Hair-Node-Gruppe auf das STRANGHAAR der Sorte → Steckbrief des Morphs `<sorte>.eigen.<name>` (oder des
        Zusatzes `<sorte>.str.<name>` bei duplicate/interpolate/generate; `brief['art']` sagt, was es ist).
        `parameter`: Eingänge der Gruppe (`length_factor=0.5` → „Length Factor"); `ort` als Mask je Punkt."""
        from Genesis9.haarzusatz import G9haarzusatz
        from Genesis9.kleidmorphe import G9kleidmorphe
        from Genesis9.ortsmorph import G9ortsmorph

        from .haarknotenauftrag import Haarknotenauftrag
        if str(knoten) not in self.KNOTEN:
            raise ValueError('knoten: %s' % '|'.join(self.KNOTEN))
        teile, kaefige, y0, y1, mitte, eintrag = G9kleidmorphe.kaefige(sorte)
        if eintrag.get('art') != 'haar':
            raise ValueError(u'%s ist keine Frisur' % sorte)
        werte = {self._eingang(k): v for k, v in parameter.items()}
        # Trim: „Replace Length" steht in Blender auf An und setzt jede Strähne auf `Length` (1 m) — gemessen 01.10.2026
        # am Pixie: 500 mm Weg statt der halben Länge. Wer einen Faktor meint, meint Skalieren.
        if knoten == 'trim' and 'Length' not in werte and 'Replace Length' not in werte:
            werte['Replace Length'] = False
            werte.setdefault('Length Factor', 0.5)
        # Duplicate: Blenders Vorgabe „Amount" 10 machte aus dem Pixie 2,6 Mio. Punkte (gemessen 01.10.2026) — zwei
        # Kopien je Strähne sind die Vorgabe, wer mehr will, sagt `amount=`.
        if knoten == 'duplicate':
            werte.setdefault('Amount', 2)
        self.ordner.mkdir(parents=True, exist_ok=True)
        hin = Haarknotenauftrag(self.ordner, sorte, knoten, werte, teile=teile, kaefige=kaefige, y0=y0)
        zusatz = str(knoten) in Haarknotenauftrag.ZUSATZ
        deltas, je_teil, berichte, straenge = [], [], [], 0
        for nummer, ((folger, _lage), punkte) in enumerate(zip(teile, kaefige, strict=True)):
            punkte = np.asarray(punkte, dtype=np.float64)
            deltas.append(np.zeros_like(punkte))
            je_teil.append(None)
            if getattr(folger, 'ART', None) != 'strang':
                continue
            ketten = self._straehnen(folger.segmente, len(punkte))
            if not ketten:
                continue
            maske = (G9ortsmorph.gewicht({'ort': dict(ort)}, punkte, y0, y1, mitte) if ort
                     else np.ones(len(punkte)))
            pfad, auftrag = hin.schreiben(nummer, punkte, ketten, maske)
            bericht = self._laufen(pfad, Path(auftrag['bericht']), self.HAARSKRIPT)
            if zusatz:
                je_teil[-1] = Haarknotenauftrag.zusatz(auftrag, folger, punkte)
                f = je_teil[-1]
                if f is None or len(f['l']) < 0.01 * len(ketten) or float(np.mean(f['l'])) < 2.0:
                    raise ValueError(u'%s: Blender erzeugte aus %d Strähnen nichts Brauchbares (%s Strähnen, %s Punkte je '
                                     u'Strähne) — Dichte/Kopfhaut prüfen (Bericht); haar_duplizieren/'
                                     u'haar_interpolieren (Python) gehen immer'
                                     % (knoten, len(ketten), 0 if f is None else len(f['l']),
                                        0 if f is None else round(float(np.mean(f['l'])), 1)))
            else:
                deltas[-1] = Haarknotenauftrag.delta(auftrag, punkte, np.concatenate(ketten), maske)
            berichte.append(bericht)
            straenge += len(ketten)
        if not straenge:
            raise ValueError(u'%s hat kein Stranghaar — Kartenhaar nimmt haar_trim/clump/noise/… (G9haarops)' % sorte)
        namen = [f.kennung for f, _lage in teile]
        if zusatz:
            return G9haarzusatz.ablegen(sorte, name, namen, je_teil,
                                        {'art': 'haarzusatz', 'knoten': str(knoten), 'werte': werte, 'blender': berichte,
                                         'kopfhaut': hin.kopfhaut})
        brief = {'art': 'haarknoten', 'knoten': str(knoten), 'werte': werte, 'ort': ort, 'straehnen': straenge,
                 'blender': berichte, 'kopfhaut': hin.kopfhaut}
        return G9kleidmorphe.ablegen(sorte, name, namen, deltas, brief)

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

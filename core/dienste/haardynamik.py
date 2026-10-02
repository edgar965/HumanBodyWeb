# -*- coding: utf-8 -*-
"""Haardynamik — `haar_dynamik` mit dem Stoffsolver (`Stoffsolver/`, 02.10.2026): Blenders Haar-Dynamik (`do_hair_dynamics`,
Cloth-Solver auf Strängen) als Warp-Löser auf der GPU, auf das STRANGHAAR einer Frisur der Garderobe.

Ein Morph wie die anderen Haar-Operationen: die Strähnen der Frisur (Käfig auf der Bühne, Y oben, m) fallen ein paar Bilder
lang unter der Schwerkraft gegen die Grundfigur, die Wurzeln bleiben an der Kopfhaut; das Ergebnis ist ein Delta je Käfigpunkt,
abgelegt als `<sorte>.eigen.<name>` (`G9kleidmorphe.ablegen`) — Netz, UV und Textur bleiben, der Regler stellt 0…1. NICHT Teil
der Automatik: nur per Rezeptzeile `m.haar_dynamik(sorte, bilder=24)` (`ModellHaarMixin.haar_dynamik`).

Der Solver läuft als Prozess in `python14` (`werkzeug/haar_lauf.py`, die Schlüssel von `Haarauftrag`), nicht im Server: Warp
und CUDA gehören nicht in den Django-Prozess. Er braucht eine CUDA-GPU (die Haarkollision gibt es nur dort) und lehnt sonst ab
(`RuntimeError` mit dem Grund aus `Haarsimulation`), statt das Haar still durch den Kopf laufen zu lassen. Kartenhaar (kein
Strang) rechnet er nicht (ValueError mit dem Hinweis auf `haar_trim` u. a.).

Kollisionskörper ist die ganze Grundfigur (`G9kleidmorphe.koerper`), nicht nur der Kopf: langes Haar fällt auf Schultern und
Rücken. **Mindestabstand 2 mm statt Blenders 31 mm:** Blenders Vorgaben (`distance_min` 0,015 m, `thickness_outer` 0,02 m)
ergeben `(0,015 + 0,02) · 8/9` = 31 mm; gemessen an der Ruhelage (Stichprobe 30.000 freie Punkte, Abstand zu den
Körperdreiecken, 02.10.2026) liegen bei Pixie 97,9 % und bei Hime Cut 93,3 % der freien Haarpunkte näher als 31 mm an der
Körperfläche, das Haar liegt auf dem Kopf. Gemessen am Ergebnis nach 24 Bildern (Probe `haardynamik_probe.py`, dieselben
30.000 Punkte, „neu eingedrungen“ = vorher außen, nachher mehr als 0,5 mm innerhalb der Körperfläche): Pixie 0 bei 1, 2 und
3 mm; Hime Cut 43 bei 1 mm (bis 53 mm tief), 0 bei 1,5, 2 und 3 mm. Deshalb 2 mm. Ab einer Reichweite `abstand + dicke` von
3,4 mm stürzt der Gerätelauf an Hime Cut ab (CUDA-Fehler 700, „illegal memory access“, auch mit Blenders 31 mm; 3,375 mm läuft)
— nicht in dieser Klasse, beim Stoffsolver gemeldet. Einstellbar: `mindestabstand_mm`.
"""

import json
import logging
import subprocess
import time
from pathlib import Path

import numpy as np
from django.conf import settings

from ..atomic_write import AtomarSchreiber

logger = logging.getLogger('core')

__all__ = ['Haardynamik']


class Haardynamik:
    NAME = 'dynamik'
    ZEIT_S = 900
    SCHWERKRAFT = [0.0, -9.81, 0.0]                       # Bühne: Y oben
    #: Mindestabstand Haar–Körper in mm; der Solver rechnet `(abstand + dicke) · 8/9` (`WarpHaarAblauf.mindest`). Grund: Moduldoc.
    MINDESTABSTAND_MM = 2.0

    def __init__(self, ordner):
        """`ordner`: Arbeitsordner der Rechnung (z. B. `ablage.arbeit('haardynamik')`)."""
        self.ordner = Path(ordner)

    def simulieren(self, sorte, name=NAME, bilder=24, material='vorgabe', material_felder=None,
                   mindestabstand_mm=MINDESTABSTAND_MM, **haarargumente):
        """→ Steckbrief des Morphs `<sorte>.eigen.<name>` (ValueError bei Kartenhaar, RuntimeError, wenn der Solver scheitert).

        `haarargumente` gehen unverändert an `Haarsimulation` (`kontinuum`, `biegung_zufall`, `zufall_seed`, `abstand` …); ein
        eigener `abstand` ersetzt den aus `mindestabstand_mm`."""
        from Genesis9.haarzusatz import G9haarzusatz
        from Genesis9.kleidmorphe import G9kleidmorphe
        from Genesis9.kopfhaut import G9kopfhaut

        from .haarstraehnen import Haarstraehnen
        teile, kaefige, y0, _y1, _mitte, eintrag = G9kleidmorphe.kaefige(sorte)
        if eintrag.get('art') != 'haar':
            raise ValueError(u'%s ist keine Frisur' % sorte)
        self.ordner.mkdir(parents=True, exist_ok=True)
        k_punkte, k_dreiecke, _n, _b, _boden = G9kleidmorphe.koerper()
        haut = G9kopfhaut.aus_teilen(teile, kaefige, y0)
        argumente = dict(haarargumente)
        argumente.setdefault('abstand', self._abstand_m(mindestabstand_mm))
        deltas, berichte, straenge, umgedreht, fern = [], [], 0, 0, 0
        for nummer, ((folger, _lage), punkte) in enumerate(zip(teile, kaefige, strict=True)):
            punkte = np.asarray(punkte, dtype=np.float64)
            deltas.append(np.zeros_like(punkte))
            if getattr(folger, 'ART', None) != 'strang':
                continue
            ketten = G9haarzusatz.ketten(folger.segmente, len(punkte))
            if not ketten:
                continue
            fasern = Haarstraehnen(punkte, ketten, haut)
            stamm = self.ordner / ('%s_%d' % (sorte, nummer))
            auftrag = self._schreiben(stamm, fasern, k_punkte, k_dreiecke, bilder, material, material_felder, argumente)
            bericht = self._laufen(Path(str(stamm) + '_auftrag.json'), Path(auftrag['bericht']))
            with np.load(auftrag['aus']) as d:
                deltas[-1] = fasern.delta(d['punkte'])
            bericht['wurzel_abstand_max_mm'] = fasern.wurzel_abstand_max_mm
            berichte.append(bericht)
            straenge += fasern.anzahl
            umgedreht += fasern.umgedreht
            fern += fasern.wurzel_fern
        if not straenge:
            raise ValueError(u'%s hat kein Stranghaar — die Haar-Dynamik rechnet Strähnen (Kartenhaar nimmt '
                             u'haar_trim/clump/noise/… aus G9haarops)' % sorte)
        brief = {'art': 'haardynamik', 'motor': 'stoffsolver', 'bilder': int(bilder), 'material': material,
                 'material_felder': material_felder, 'mindestabstand_mm': float(mindestabstand_mm),
                 'schwerkraft': 'Y unten', 'haarargumente': argumente, 'straehnen': straenge, 'umgedreht': umgedreht,
                 'wurzel_fern': fern,
                 'kopfhaut': {'quelle': haut['quelle'], 'flaeche_m2': round(float(haut['flaeche_m2']), 5)},
                 'stoffsolver': berichte}
        return G9kleidmorphe.ablegen(sorte, name, [f.kennung for f, _lage in teile], deltas, brief)

    @staticmethod
    def _abstand_m(mindestabstand_mm):
        """`distance_min` der Haarsimulation so, dass `(abstand + dicke) · 8/9` der Mindestabstand ist (Körperdicke 0)."""
        return float(mindestabstand_mm) * 1e-3 * 9.0 / 8.0

    def _schreiben(self, stamm, fasern, k_punkte, k_dreiecke, bilder, material, material_felder, argumente):
        """Strähnen und Körper als `.npz` (Reihenfolge der Punkte bleibt) und der Auftrag — die Schlüssel von `Haarauftrag`."""
        np.savez_compressed(str(stamm) + '_straehnen.npz', punkte=fasern.punkte.astype(np.float32), laengen=fasern.laengen,
                            normalen=fasern.normalen.astype(np.float32))
        np.savez_compressed(str(stamm) + '_koerper.npz', punkte=np.asarray(k_punkte, dtype=np.float32),
                            dreiecke=np.asarray(k_dreiecke, dtype=np.int32))
        auftrag = {'straehnen': str(stamm) + '_straehnen.npz', 'koerper': str(stamm) + '_koerper.npz',
                   'aus': str(stamm) + '_nachher.npz', 'bericht': str(stamm) + '_bericht.json', 'bilder': int(bilder),
                   'schwerkraft': self.SCHWERKRAFT, 'material': str(material), 'dicke': 0.0, 'rechner': 'warp',
                   'haarargumente': argumente}
        if material_felder:
            auftrag['material_felder'] = dict(material_felder)
        AtomarSchreiber.json_schreiben(Path(str(stamm) + '_auftrag.json'), auftrag)
        return auftrag

    def _laufen(self, auftrag, bericht):
        skript = Path(settings.STOFFSOLVER_HAARSKRIPT)
        if not skript.is_file():
            raise RuntimeError('Stoffsolver fehlt: %s' % skript)
        t0 = time.perf_counter()
        bericht.unlink(missing_ok=True)
        prozess = subprocess.Popen([str(settings.PYTHON14), str(skript), '--auftrag', str(auftrag)], stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, cwd=str(skript.parent))
        try:
            aus, _ = prozess.communicate(timeout=self.ZEIT_S)
        except subprocess.TimeoutExpired:
            prozess.kill()
            raise RuntimeError('Haar-Dynamik: Zeitgrenze %d s' % self.ZEIT_S) from None
        if not bericht.is_file():
            letzte = '\n'.join((aus or b'').decode('utf-8', errors='replace').splitlines()[-15:])
            raise RuntimeError('Haar-Dynamik ohne Bericht (Code %s):\n%s' % (prozess.returncode, letzte))
        daten = json.loads(bericht.read_text(encoding='utf-8'))
        if daten.get('fehler'):
            raise RuntimeError('Haar-Dynamik: %s' % daten['fehler'])
        daten['sim_s'] = daten.get('sekunden')         # nur die Zeitschritte (`Haarsimulation.dauer`); `sekunden`: ganzer Prozess
        daten['sekunden'] = round(time.perf_counter() - t0, 1)
        logger.info('Haar-Dynamik %s: %s', auftrag.name, daten)
        return daten

# -*- coding: utf-8 -*-
"""Exportleistehautmaske — die Haut unter den Stücken fällt aus dem Körper, im Render und im Export (31.10.2026, `Exportleisterendermodell`, `Exportleiste.exportieren`).

Der Browser zeichnet die Haut unter dem Stoff nicht (`Hautverdeckung`, Rechnung `gemeinsam/hautmaske.js`); der Körper, den der Server für den Render baut, trug sie: Im Render
vom 31.10.2026 (Test edgar, DanceKurz, 10 Bilder) stach die Haut des Gesäßes durch die Hose der KI, der Fleck wuchs von Bild zu Bild. Die Browser-GLB bringt die Maske nicht
mit (Körper mit vollem Index, 0 von 104.480 Punkten ohne Dreieck, `ProjektTemp/_wegwerf/exportleiste/koerperindex_probe.py`). Darum hier dieselbe Maske in der Fassung des
Server-Videowegs (`TheatreJS/ModelPhysik/hautmaske.py`, Regel für Regel wie im Browser, `test_hautmaske_python`): in Ruhelage, der Körper gegen alle deckenden Stücke; ein
Dreieck fällt weg, wenn alle drei Ecken verdeckt sind (`Hautmaske.index_ohne`). Die Randdreiecke bleiben wie im Browser; dort zieht der Shader ihre verdeckten Ecken unter
die Kante (`Hauteinzug`), hier nicht.

Seit dem Abend des 31.10.2026 wird der Körper vor der Maske an gleichen Lagen verschweißt und die Inseln schließt die Regel des Browsers (`Exportleisteinseln`): Vorher fielen
im Render alle Nägel weg (Messung dort).

Welche Stücke decken, sagt die Seite (`stellung.haut_deckt`, die Knotennamen der Stücke, unter denen die Szene die Haut ausblendet — kein Haar ohne Kostüm); ohne Angabe decken
alle Stücke mit deckendem Material (durchsichtige `MASK`/`BLEND` nie). Wie tief: mit der Tiefe der Kostümstücke von Mesh3D-AI (`TIEFE_M` = `Mesh3daikikleiderfeld.STOFF_TIEFE_M`:
der Körper ragt dort Zentimeter durch das Stück) und an den UV-Nähten verschweißt wie `Meshfighautstueck.verschweissen` (sonst ist jede Naht ein lockerer Rand mit freiem
Streifen). Die Szene rechnet Stücke ohne Kostüm mit 5 mm und unverschweißt: an Test edgar 3.517 verdeckte Punkte, alle im Saumband, kein Dreieck weg (Chrome, 31.10.2026,
`Hautverdeckung.anwendenAsync`); mit dieser Regel waren Render (10 Bilder, 16:43, deckend Hose und Uhr) und .blend sauber (Workbench, Hüfte in Bild 1, 250, 500, 750, 1000 von drei Seiten,
`ProjektTemp/_wegwerf/exportleiste/blend_huefte_bilder.py`).
"""

import importlib
import re
import sys

import numpy as np
from django.conf import settings

__all__ = ['Exportleistehautmaske']


class Exportleistehautmaske:
    #: So tief (m) darf der Stoff hinter der Haut liegen und deckt sie trotzdem.
    TIEFE_M = 0.040
    #: Punkte näher als das (m) sind beim Verschweißen einer.
    NAHT_M = 1e-6
    #: Der Körper in der GLB des Browsers (`Modellexport`: Netz `genesis9_koerper_<Figur>`).
    KOERPER = re.compile(r'^genesis9_koerper_')

    @classmethod
    def maske(cls, punkte, dreiecke, stuecke):
        """Bool je Körperpunkt: verdeckt von einem der Stücke `[(punkte, dreiecke)]` (Ruhelage). Der Körper wird dafür an gleichen Lagen verschweißt (UV-Nähte, Materialzonen),
        und die Inseln schließt die Regel des Browsers (`Exportleisteinseln`) statt der älteren der Python-Fassung."""
        from .exportleisteinseln import Exportleisteinseln
        P = np.asarray(punkte, dtype=np.float64).reshape(-1, 3)
        T = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        _, erster, lage = np.unique(np.round(P / cls.NAHT_M).astype(np.int64), axis=0, return_index=True, return_inverse=True)
        lage = lage.reshape(-1)
        tw = lage[T]
        tw = tw[(tw[:, 0] != tw[:, 1]) & (tw[:, 1] != tw[:, 2]) & (tw[:, 0] != tw[:, 2])]
        stoffe = [cls.verschweissen(p, d) for p, d in stuecke]
        maske = cls._modul().Hautmaske.verdeckt(P[erster], tw, stoffe, tiefe=cls.TIEFE_M, inseln=0)
        Exportleisteinseln.schliessen(maske, P[erster], tw)
        return maske[lage]

    @classmethod
    def koerper(cls, netz, stuecke):
        """`netz` (`G9koerpernetz`) ohne die verdeckten Dreiecke, Gruppen nachgezogen → (Netz, Bericht). `stuecke`: `[(punkte, dreiecke)]` in Ruhelage."""
        dreiecke = np.asarray(netz['dreiecke'], dtype=np.int64).reshape(-1, 3)
        if not stuecke:
            return netz, {'stuecke': 0, 'punkte_verdeckt': 0, 'dreiecke_weg': 0, 'dreiecke': len(dreiecke)}
        maske = cls.maske(netz['punkte'], dreiecke, stuecke)
        weg = maske[dreiecke].all(axis=1)
        vorher = np.concatenate([[0], np.cumsum(~weg)])                   # bleibende Dreiecke vor jedem Dreieck: die neuen Grenzen der Gruppen
        gruppen = []
        for g in netz['gruppen']:
            von = int(g['index_ab']) // 3
            bis = von + int(g['index_anzahl']) // 3
            gruppen.append(dict(g, index_ab=int(vorher[von]) * 3, index_anzahl=int(vorher[bis] - vorher[von]) * 3))
        bleibt = dreiecke[~weg]
        neu = dict(netz, dreiecke=bleibt.reshape(-1) if np.ndim(netz['dreiecke']) == 1 else bleibt, gruppen=gruppen)
        return neu, {'stuecke': len(stuecke), 'punkte_verdeckt': int(maske.sum()), 'dreiecke_weg': int(weg.sum()), 'dreiecke': len(dreiecke)}

    @classmethod
    def glb(cls, modell, stuecke):
        """Die GLB des Browsers (`G9glbanimation`, an Ort und Stelle): aus dem Körper fallen die verdeckten Dreiecke, je Materialgruppe (Primitive) → Bericht.
        `stuecke`: `[(punkte, dreiecke)]` in der Bindlage der GLB."""
        from .exportleisterendermodell import Exportleisterendermodell
        bericht = {'stuecke': len(stuecke), 'punkte_verdeckt': 0, 'dreiecke_weg': 0, 'dreiecke': 0}
        for knoten in modell.j.get('nodes', []):
            if knoten.get('mesh') is None or not cls.KOERPER.match(knoten.get('name') or ''):
                continue
            netz = modell.j['meshes'][knoten['mesh']]
            prims = [p for p in netz['primitives'] if p.get('mode', 4) == 4 and 'indices' in p]
            for lage in sorted({p['attributes']['POSITION'] for p in prims}):
                eigene = [p for p in prims if p['attributes']['POSITION'] == lage]
                teile = [Exportleisterendermodell._feld(modell, p['indices']).reshape(-1, 3).astype(np.int64) for p in eigene]
                bericht['dreiecke'] += sum(len(t) for t in teile)
                if not stuecke:
                    continue
                maske = cls.maske(Exportleisterendermodell._feld(modell, lage), np.concatenate(teile), stuecke)
                bericht['punkte_verdeckt'] += int(maske.sum())
                for p, t in zip(eigene, teile, strict=True):
                    weg = maske[t].all(axis=1)
                    bericht['dreiecke_weg'] += int(weg.sum())
                    if weg.all():
                        netz['primitives'].remove(p)                     # glTF: kein Index ohne Eintrag
                    elif weg.any():
                        cls._index_kuerzen(modell, p, t[~weg])
        return bericht

    @staticmethod
    def _index_kuerzen(modell, primitiv, dreiecke):
        """Die bleibenden Dreiecke an den Anfang des Indexpuffers der Primitive (sie werden nur weniger), `count` nachgezogen."""
        from .exportleisterendermodell import Exportleisterendermodell
        a = modell.j['accessors'][primitiv['indices']]
        werte = np.ascontiguousarray(dreiecke.reshape(-1), dtype=Exportleisterendermodell.TYPEN[a['componentType']])
        ab = modell.j['bufferViews'][a['bufferView']].get('byteOffset', 0) + a.get('byteOffset', 0)
        modell.bin[ab:ab + werte.nbytes] = werte.tobytes()
        a['count'] = int(werte.size)
        a.pop('min', None)
        a.pop('max', None)

    @classmethod
    def verschweissen(cls, punkte, dreiecke):
        """Gleiche Lagen (UV-Nähte) zu einem Punkt → (Punkte, Dreiecke ohne entartete)."""
        p = np.asarray(punkte, dtype=np.float64).reshape(-1, 3)
        _, erster, neu = np.unique(np.round(p / cls.NAHT_M).astype(np.int64), axis=0, return_index=True, return_inverse=True)
        t = neu.reshape(-1)[np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)]
        return p[erster], t[(t[:, 0] != t[:, 1]) & (t[:, 1] != t[:, 2]) & (t[:, 0] != t[:, 2])]

    @staticmethod
    def _modul():
        """`ModelPhysik/hautmaske.py`. Die Module dort importieren einander flach; ihr Ordner kommt ans ENDE des Suchpfads, damit er kein gleichnamiges Modul des Servers verdeckt."""
        ordner = str(settings.BASE_DIR / 'TheatreJS' / 'ModelPhysik')
        if ordner not in sys.path:
            sys.path.append(ordner)
        return importlib.import_module('hautmaske')

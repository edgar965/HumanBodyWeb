# -*- coding: utf-8 -*-
"""Blendimportnetz — Schritt „koerper“ des Wegs „netz“: das verschmolzene Netz als Körpernetz für „Mesh to 3D“ bereitstellen (11.10.2026).

Beim Weg „teile“ baut `Blendimportkoerper` aus dem nackten Körper und den Augen eine GLB; beim Weg „netz“ IST das Netz die Eingabe (`Blendimportweg`). Dieser Schritt macht daraus `arbeit/koerper.glb` — dieselbe
Datei, die `pose` rendert und `figur` an „Mesh to 3D“ gibt — und bringt es auf Menschenhöhe, wenn es keine hat:

    Ein Bild-zu-3D-Netz kommt ohne Maßstab (Tripo: der Zauberer ist 0,979 m hoch samt Hut und Stab). „Mesh to 3D“ liest 0,98 als Meter und müsste eine Figur von 98 cm anpassen; die Genesis-Regler
    erreichen das nicht. Liegt die Höhe außerhalb von `MENSCH_M`, wird das Netz auf `SOLL_M` gestreckt — als Skalierung des Wurzelknotens im JSON-Block der GLB, die Punkte und Bilder bleiben, wie sie sind
    (die Datei wird nicht über trimesh neu geschrieben). `SOLL_M` ist die Höhe des GANZEN Netzes samt Hut, Stab und Haar: eine Setzung, kein Messwert — wer die Person kennt, stellt sie hier ein.
"""

import filecmp
import json
import logging
import os
import shutil
import struct
import time
from pathlib import Path

import numpy as np

from .blendimportweg import Blendimportweg

logger = logging.getLogger('core')

__all__ = ['Blendimportnetz']


class Blendimportnetz:
    DATEI = 'koerper.glb'
    #: Höhen (m), die für einen stehenden Menschen samt Hut und Stab gelten; außerhalb wird skaliert.
    MENSCH_M = (1.4, 2.3)
    #: Höhe (m) des ganzen Netzes nach dem Skalieren (Setzung: ein Zauberer mit Hut von 0,98 m wird 2,00 m, der Kopf sitzt bei etwa 1,7 m).
    SOLL_M = 2.0

    def __init__(self, ablage, melden):
        self.ablage = ablage
        self.melden = melden

    # ------------------------------------------------------------------ Ablauf

    def schreiben(self, quelle):
        """Bericht des Schritts (für `stand.ergebnis.koerper`): Größe, Höhe vorher und nachher, Faktor, Bilder der Datei."""
        t0 = time.perf_counter()
        self.melden(0.0, 'Netz lesen')
        daten = Blendimportweg.glb_json(quelle)
        flaechen = self._zaehlen(daten)
        hoehe = self._hoehe(daten)
        faktor = 1.0 if self.MENSCH_M[0] <= hoehe <= self.MENSCH_M[1] else self.SOLL_M / hoehe
        ziel = self.ablage.arbeit(self.DATEI)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        self.melden(0.4, 'Netz auf Menschenhöhe' if faktor != 1.0 else 'Netz kopieren')
        geschrieben = self._kopieren(quelle, ziel) if faktor == 1.0 else self._skaliert_schreiben(quelle, ziel, daten, faktor)
        self.melden(1.0, 'Netz bereit')
        bericht = {'weg': Blendimportweg.NETZ, 'datei': self.DATEI, 'punkte': flaechen['punkte'], 'dreiecke': flaechen['dreiecke'], 'augen': 0,
                   'hoehe_m_original': round(hoehe, 4), 'faktor': round(faktor, 4), 'hoehe_m': round(hoehe * faktor, 4), 'soll_m': self.SOLL_M,
                   'material': len(daten.get('materials') or []), 'bilder': [b.get('name') or b.get('mimeType') for b in daten.get('images') or []],
                   'unveraendert': not geschrieben, 'groesse_mb': round(ziel.stat().st_size / 1e6, 1), 'dauer_s': round(time.perf_counter() - t0, 1)}
        logger.info('Mesh-3D %s: Netz %d Punkte, %d Dreiecke, %.3f m → %.3f m (Faktor %.4f)', self.ablage.kennung, bericht['punkte'], bericht['dreiecke'], hoehe, bericht['hoehe_m'], faktor)
        # Die leichte Kopie für die 3D-Ansicht baut ab jetzt, neben Segmentierung, Pose und Figur — nicht erst beim Öffnen der Jobseite (125 s Wartezeit am Auftrag „Edgar“).
        from .mesh3dnetzansicht import Mesh3dnetzansicht

        Mesh3dnetzansicht.vorab(self.ablage.kennung)
        return bericht

    # ------------------------------------------------------------------ Lesen

    @staticmethod
    def _zaehlen(daten):
        konten = daten.get('accessors') or []
        punkte = dreiecke = 0
        for netz in daten.get('meshes') or []:
            for p in netz.get('primitives') or []:
                punkte += konten[p['attributes']['POSITION']]['count']
                if 'indices' in p and p.get('mode', 4) == 4:
                    dreiecke += konten[p['indices']]['count'] // 3
        return {'punkte': int(punkte), 'dreiecke': int(dreiecke)}

    @classmethod
    def _hoehe(cls, daten):
        """Höhe (Y, glTF) des Netzes in der Welt: die Eckpunkte des Kastens aus `min`/`max` der POSITION-Zugriffe, mit der Matrix des Netzknotens (ohne Eltern — der Weg „netz“ hat einen Knoten)."""
        konten = daten.get('accessors') or []
        unten, oben = np.full(3, np.inf), np.full(3, -np.inf)
        for netz in daten.get('meshes') or []:
            for p in netz.get('primitives') or []:
                a = konten[p['attributes']['POSITION']]
                if 'min' not in a or 'max' not in a:
                    raise ValueError('Der POSITION-Zugriff der GLB trägt kein min/max — Höhe nicht lesbar')
                unten, oben = np.minimum(unten, a['min']), np.maximum(oben, a['max'])
        knoten = next((n for n in daten.get('nodes') or [] if 'mesh' in n), {})
        ecken = np.array([[x, y, z, 1.0] for x in (unten[0], oben[0]) for y in (unten[1], oben[1]) for z in (unten[2], oben[2])])
        welt = ecken @ cls._matrix(knoten).T
        return float(welt[:, 1].max() - welt[:, 1].min())

    @staticmethod
    def _matrix(knoten):
        """4×4 des Knotens (glTF: `matrix` spaltenweise, sonst Verschiebung · Drehung (Quaternion x y z w) · Skalierung)."""
        if 'matrix' in knoten:
            return np.array(knoten['matrix'], dtype=np.float64).reshape(4, 4, order='F')
        x, y, z, w = knoten.get('rotation') or [0.0, 0.0, 0.0, 1.0]
        d = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                      [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                      [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
        m = np.eye(4)
        m[:3, :3] = d @ np.diag(knoten.get('scale') or [1.0, 1.0, 1.0])
        m[:3, 3] = knoten.get('translation') or [0.0, 0.0, 0.0]
        return m

    # ------------------------------------------------------------------ Schreiben

    @staticmethod
    def _kopieren(quelle, ziel):
        """`quelle` nach `ziel` — nur wenn `ziel` nicht schon genau diesen Inhalt hat; `True`, wenn geschrieben wurde. Grund: Alles, was am Körpernetz hängt (Abstimm-Netz der Segmentierung, `.scan.npz`
        neben der Datei, die Kopie im Eingang von „Mesh to 3D"), trägt die Änderungszeit der Datei im Stempel. Jeder Start schrieb sie neu, auch bei gleichem Inhalt — gemessen 12.10.2026 am Zauberer:
        das Abstimm-Netz (pymeshlab, ein Kern) wurde in jedem Lauf neu gebaut, ~79 s."""
        if os.path.isfile(ziel) and filecmp.cmp(str(quelle), str(ziel), shallow=False):
            return False
        shutil.copyfile(str(quelle), str(ziel))
        return True

    @staticmethod
    def _ablegen(ziel, inhalt):
        """`inhalt` (bytes) als `ziel` — nur wenn es nicht schon genau so dort liegt (Grund: `_kopieren`); erst in eine Nebendatei, dann ersetzen. `True`, wenn geschrieben wurde."""
        try:
            if os.path.getsize(ziel) == len(inhalt) and Path(ziel).read_bytes() == inhalt:
                return False
        except OSError:
            pass
        nebendatei = '%s.%d.teil' % (ziel, os.getpid())
        with open(nebendatei, 'wb') as f:
            f.write(inhalt)
        os.replace(nebendatei, str(ziel))
        return True

    @classmethod
    def _skaliert_schreiben(cls, quelle, ziel, daten, faktor):
        """GLB mit neuem JSON-Block: jeder Wurzelknoten der Szene um `faktor` gestreckt (um den Ursprung); der Rest der Datei (Puffer, Bilder) wird unverändert übernommen. `True`, wenn die Datei geschrieben wurde
        (gleicher Inhalt wie schon dort: unangetastet, `_kopieren`)."""
        szene = (daten.get('scenes') or [{}])[daten.get('scene', 0)]
        for index in szene.get('nodes') or []:
            knoten = daten['nodes'][index]
            if 'matrix' in knoten:
                m = np.array(knoten['matrix'], dtype=np.float64).reshape(4, 4, order='F')
                m[:3, :] *= faktor
                knoten['matrix'] = [float(v) for v in m.reshape(-1, order='F')]
            else:
                knoten['scale'] = [float(s) * faktor for s in knoten.get('scale') or [1.0, 1.0, 1.0]]
                knoten['translation'] = [float(t) * faktor for t in knoten.get('translation') or [0.0, 0.0, 0.0]]
        neu = json.dumps(daten, separators=(',', ':')).encode('utf-8')
        neu += b' ' * (-len(neu) % 4)
        with open(str(quelle), 'rb') as f:
            roh = f.read()
        alt = struct.unpack('<I', roh[12:16])[0]
        rest = roh[20 + alt:]
        kopf = b'glTF' + struct.pack('<II', 2, 12 + 8 + len(neu) + len(rest)) + struct.pack('<I', len(neu)) + b'JSON'
        return cls._ablegen(ziel, kopf + neu + rest)

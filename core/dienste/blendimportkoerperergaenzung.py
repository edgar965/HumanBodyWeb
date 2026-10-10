# -*- coding: utf-8 -*-
"""Blendimportkoerperergaenzung — die Beine unter einer Strumpfhose für „Mesh to 3D" (10.10.2026).

Rosemary Winters: der Körper endet in der Oberschenkelmitte, die Beine gibt es nur als Strumpf-Netz (Rolle Kleid). Die Figur
soll aber an eine vollständige Form passen. Hier wird das Körper-Netz NUR für die GLB von „Mesh to 3D" ergänzt — die Haut
(`Blendimporthaut`, `koerper_ruhe`) bleibt beim Original, damit nie eine Strumpffarbe in die Haut gelangt.

Geometrie: die Dreiecke des Kleidungsnetzes, die unter der Körperkante liegen, 3 mm nach innen (zur Mitte ihres Umfangs).
Farbe: ein Ausschnitt der Genesis-9-Standardhaut (`Blendimportkoerper.HAUT_*`), zylindrisch auf den Umfang gelegt — die
Winkel und Höhen liefert dieses Modul, die Abbildung auf den Atlas macht `Blendimportkoerper`.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Blendimportkoerperergaenzung']


class Blendimportkoerperergaenzung:
    #: Dreiecke, deren größte Höhe unter der Körperkante + RAND_M liegt, zählen zum Stück unter dem Körper.
    RAND_M = 0.03
    #: Abstand der neuen Punkte nach innen (Stoffdicke plus Luft zur Haut).
    DICKE_M = 0.003
    #: Radius, in dem die Nachbarn eines Punkts seine Mitte bestimmen.
    RADIUS_M = 0.08
    #: Vertikale Schicht, in der Nachbarn zur Mitte zählen.
    SCHICHT_M = 0.02
    #: Körperecken, die als „Kante" gelten — Abstand zur tiefsten Körperhöhe.
    KANTE_M = 0.02
    #: Der Ring über der Unterkante (Meter), an dem die Breite des Körpers gemessen wird.
    RING_M = 0.05
    #: Ein Kleidungsnetz, dessen Teil unter der Körperkante mehr als dieses Vielfache der Körperbreite an der Kante misst, ist kein Bein:
    #: seoris Mantel (1,41 und 3,2 fach) hätte als Bein gegolten, die Beine selbst (`head.002`, Hose, Strumpf) liegen bei 0,99–1,06. Gemessen
    #: an allen gespeicherten Läufen (`ProjektTemp/_wegwerf/blendimport_massstab/ergaenzung_alle.py`): was bisher ergänzt wurde (Strumpf,
    #: Stiefel, Hose, Schuhe), liegt bei 0,32–1,15 — die Schwelle 1,25 verändert keinen davon. Die Tiefe taugt dafür nicht (1,2- bis 6,9fach).
    MAX_BREITE = 1.25

    def __init__(self, ablage, inventar, rollen):
        self.ablage = ablage
        self.inventar = {n['name']: n for n in inventar['netze']}
        self.rollen = rollen

    def _laden(self, name):
        netz = self.inventar[name]
        with np.load(self.ablage.export(netz['datei'])) as d:
            return {k: d[k] for k in d.files}

    def ergaenzen(self, koerper):
        """`koerper` ist das Körper-Netz `{punkte, dreiecke, uv_ecken, material}` (Blender-Achsen). → `{punkte, dreiecke, winkel,
        hoehe, kleider}` für die Stücke unter dem Körper (`winkel` in Radiant um die Stückmitte, `hoehe` in m), oder None,
        wenn kein Kleidungsnetz unter den Körper reicht."""
        from scipy.spatial import cKDTree

        kante = float(koerper['punkte'][:, 2].min())
        ring = koerper['punkte'][koerper['punkte'][:, 2] < kante + self.RING_M]
        ring_breite = float(np.ptp(ring[:, 0])) if len(ring) else 0.0
        punkte, winkel, hoehen, dreiecke, kleider = [], [], [], [], []
        for name in [r['name'] for r in self.rollen if r['rolle'] == 'kleid' and r['name'] in self.inventar]:
            k = self._laden(name)
            kp = np.asarray(k['punkte'], dtype=np.float64)
            kd = np.asarray(k['dreiecke'], dtype=np.int64)
            unter = kd[kp[kd][..., 2].max(axis=1) < kante + self.RAND_M]
            if not len(unter) or kp[:, 2].min() > kante - 0.01:
                continue
            verts = np.unique(unter)
            breite = float(np.ptp(kp[verts][:, 0]))
            if ring_breite > 0 and breite > self.MAX_BREITE * ring_breite:
                logger.info('Körperergänzung: %s übersprungen — unter der Körperkante %.2f m breit, der Körper dort %.2f m (kein Bein)',
                            name, breite, ring_breite)
                continue
            baum = cKDTree(kp)
            nah = baum.query_ball_point(kp[verts], r=self.RADIUS_M)
            neu = kp[verts].copy()
            wink = np.zeros(len(verts))
            for i, v in enumerate(verts):
                nb = kp[nah[i]]
                nb = nb[np.abs(nb[:, 2] - kp[v, 2]) < self.SCHICHT_M]
                if not len(nb):
                    continue
                mitte = nb[:, :2].mean(axis=0)
                richtung = mitte - kp[v, :2]
                laenge = float(np.linalg.norm(richtung))
                if laenge > 1e-9:
                    neu[i, :2] += richtung / laenge * self.DICKE_M
                wink[i] = np.arctan2(kp[v, 1] - mitte[1], kp[v, 0] - mitte[0])
            punkte.append(neu)
            winkel.append(wink)
            hoehen.append(neu[:, 2])
            zuordnung = {int(v): j for j, v in enumerate(verts)}
            dreiecke.append(np.array([[zuordnung[int(a)], zuordnung[int(b)], zuordnung[int(c)]] for a, b, c in unter], dtype=np.int64))
            kleider.append(name)
        if not punkte:
            return None
        versatz = np.cumsum([0] + [len(p) for p in punkte[:-1]])
        dreiecke = np.vstack([d + int(v) for d, v in zip(dreiecke, versatz, strict=True)])
        logger.info('Körperergänzung: %d Punkte, %d Dreiecke unter der Körperkante von %s', sum(len(p) for p in punkte), len(dreiecke),
                    ', '.join(kleider))
        return {'punkte': np.vstack(punkte), 'dreiecke': dreiecke, 'winkel': np.concatenate(winkel),
                'hoehe': np.concatenate(hoehen), 'kleider': kleider}

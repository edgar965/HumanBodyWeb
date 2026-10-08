# -*- coding: utf-8 -*-
"""Blendimportlage — Punkte aus der .blend in die Ruhelage der Genesis-Figur, und die Figur selbst als Netz.

Drei Abbildungen, alle aus dem fertigen Auftrag „Mesh to 3D" (`Blendimportfigur`):

    ins_netz   Blender-Achsen → glTF-Achsen (`Blendimportkoerper.gltf`) → Lage der Erkennung (`arbeit/scan_lage.npz`,
               dieselbe Matrix, mit der „Mesh to 3D" das Körpernetz gedreht, gestellt und skaliert hat)
    ruhelage   von dort in die Ruhelage der Figur — `Kleidungsentposen` mit dem Käfig in Ruhe (`genesis_ende.npz`) und in
               der Haltung des Netzes (`posiert.npy`), wie `Meshfigurkleidung.objekt` und `Fotostuecke`
    kopf_starr wie `ruhelage`, aber EINE Starrkörperbewegung (Kabsch) aus den Kopfpunkten des Käfigs — für das Haar, das
               nur am Kopfknochen hängt (alle Punkte, Gewicht 0,77–0,85, gemessen 08.10.2026): die Nachbarschaft von `Kleidungsentposen` zöge lange Strähnen an Schultern
               und Rücken mit (`haar.md`: Haar folgt dem Kopf)

Dazu `genesis`: die fertige Figur (Regler samt Eigenmorph, `G9formung`) auf Stufe 1 — Punkte in Ruhe (Meter, Y oben,
Füße 0), Dreiecke, UV mit der UDIM-Kachel der Gruppe im ganzzahligen Teil (Genesis führt UV je Gruppe in 0..1 und die
Kachel an der Gruppe: Head/Mouth Cavity 1001, Body 1002, Legs 1003, Arms 1004, Nägel 1005 — gelesen 08.10.2026).
"""

import logging

import numpy as np

from .blendimportkoerper import Blendimportkoerper

logger = logging.getLogger('core')

__all__ = ['Blendimportlage']


class Blendimportlage:
    STUFE = 1
    #: Kacheln, die NICHT gebacken werden: 1005 (Finger- und Zehennägel). Gemessen am ersten Import (2026.10.08.11.28.06):
    #: nur 30,4 % der Kachel getroffen bei 52,4 % Inselfläche, die Normalen im Median 32° gekippt — die Nägel des Originals
    #: liegen nicht auf denen der Figur. Ohne Fototextur für 1005 gelten die Genesis-Nägel und der Nagellack-Preset färbt sie
    #: (Edgar, 08.10.2026: „Nägel färben sich nicht, wenn ich die über Genesis setze").
    NICHT_GEBACKEN = (1005,)

    def __init__(self, job, zusatz=None):
        from ..daten.meshfigurablage import Meshfigurablage

        self.job = job
        #: Weitere Regler der Stellung (die Nachformung der Scham, `Blendimportnachformung.zusatzregler`) — `{eigen:…: 1.0}`.
        self.zusatz = dict(zusatz or {})
        self.ablage = Meshfigurablage(job.kennung)
        with np.load(self.ablage.arbeit('scan_lage.npz')) as d:
            self.matrix = np.asarray(d['matrix'], dtype=np.float64)
        with np.load(self.ablage.arbeit('genesis_ende.npz')) as d:
            self.kaefig_ruhe = np.asarray(d['punkte'], dtype=np.float64)
            self.teil = np.asarray(d['teil'])
        self.kaefig_posiert = np.load(self.ablage.arbeit('posiert.npy')).astype(np.float64)
        self._entposen = None

    def stellung(self):
        """Die Regler der Figur: die der Anpassung samt Eigenmorph plus die Zusatzregler der Nachformung."""
        return {**(self.job.stellung() or {}), **self.zusatz}

    def ins_netz(self, punkte_blender):
        p = Blendimportkoerper.gltf(punkte_blender)
        return p @ self.matrix[:3, :3].T + self.matrix[:3, 3]

    def entposen(self):
        from Kleidung.kleidungsentposen import Kleidungsentposen

        if self._entposen is None:
            self._entposen = Kleidungsentposen(self.kaefig_ruhe, self.kaefig_posiert)
        return self._entposen

    def ruhelage(self, punkte_blender):
        return self.entposen().ruhelage(self.ins_netz(punkte_blender))

    def kopf_starr(self, punkte_blender):
        """Haar: Kabsch (ohne Maßstab) über die Kopfpunkte des Käfigs, Haltung → Ruhe."""
        from Genesis9.koerperteile import G9koerperteile

        kopf = self.teil == G9koerperteile.NUMMER['kopf']
        a, b = self.kaefig_posiert[kopf], self.kaefig_ruhe[kopf]
        ma, mb = a.mean(axis=0), b.mean(axis=0)
        u, _, vt = np.linalg.svd((a - ma).T @ (b - mb))
        d = np.sign(np.linalg.det(vt.T @ u.T)) or 1.0
        r = vt.T @ np.diag([1.0, 1.0, d]) @ u.T
        rest = np.linalg.norm((a - ma) @ r.T + mb - b, axis=1) * 1000.0
        self.kopf_befund = {'punkte': int(kopf.sum()), 'rest_rms_mm': round(float(np.sqrt((rest ** 2).mean())), 2)}
        return (self.ins_netz(punkte_blender) - ma) @ r.T + mb

    # ----------------------------------------------------------------- Figur

    def genesis(self):
        """`{punkte, dreiecke, uv, kachel_je_dreieck}` — die fertige Figur auf Stufe 1 in Ruhe."""
        from Genesis9.basisnetz import G9basisnetz
        from Genesis9.formung import G9formung
        from Genesis9.reglerableitung import G9reglerableitung

        kaefig, _, _ = G9reglerableitung.lage(G9formung(self.stellung()))
        stufe = G9basisnetz.holen().netzstufe(self.STUFE)
        punkte = np.asarray(stufe.punkte(np.asarray(kaefig, dtype=np.float64)), dtype=np.float64)
        dreiecke = np.asarray(stufe.dreiecke, dtype=np.int64).reshape(-1, 3)
        kachel = np.zeros(len(dreiecke), dtype=np.int64)
        for g in stufe.gruppen:
            ab = int(g['index_ab']) // 3
            kachel[ab:ab + int(g['dreiecke'])] = int(g['kachel'])
        uv = np.asarray(stufe.uv, dtype=np.float64)
        return {'punkte': punkte, 'dreiecke': dreiecke, 'uv': uv, 'kachel': kachel,
                'gruppen': [(g['name'], int(g['kachel'])) for g in stufe.gruppen]}

    def genesis_objs(self, ordner):
        """Je Kachel ein OBJ der Figur (`genesis_<kachel>.obj`) in BLENDER-Achsen (Z oben), UV wie Genesis (0..1) —
        `blendbacken.py` backt jede Kachel in ein eigenes Bild (außer `NICHT_GEBACKEN`). Gibt `{kachel: Datei}`."""
        g = self.genesis()
        blender = self.blender(g['punkte'])
        aus = {}
        for kachel in sorted({int(k) for k in g['kachel']} - set(self.NICHT_GEBACKEN)):
            dreiecke = g['dreiecke'][g['kachel'] == kachel]
            genutzt, neu = np.unique(dreiecke.reshape(-1), return_inverse=True)
            uv = g['uv'][dreiecke.reshape(-1)]
            zeilen = ['o Genesis_%d' % kachel] + ['v %.6f %.6f %.6f' % tuple(v) for v in blender[genutzt]]
            zeilen += ['vt %.6f %.6f' % tuple(t) for t in uv]
            zeilen += ['f %d/%d %d/%d %d/%d' % (a + 1, 3 * i + 1, b + 1, 3 * i + 2, c + 1, 3 * i + 3)
                       for i, (a, b, c) in enumerate(neu.reshape(-1, 3))]
            pfad = ordner / ('genesis_%d.obj' % kachel)
            pfad.write_text('\n'.join(zeilen) + '\n', encoding='utf-8')
            aus[kachel] = str(pfad)
        return aus

    @staticmethod
    def blender(punkte_ruhe):
        """Ruhelage (Y oben) → Blender-Achsen (Z oben): die Umkehr von `Blendimportkoerper.gltf`."""
        p = np.asarray(punkte_ruhe, dtype=np.float64)
        return np.column_stack([p[:, 0], -p[:, 2], p[:, 1]])

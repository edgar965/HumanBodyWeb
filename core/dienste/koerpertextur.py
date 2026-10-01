# -*- coding: utf-8 -*-
"""Koerpertextur — der Körper der Runden MIT der gebackenen Haut (UDIM-Kacheln aus dem Netz/Foto), nicht einfarbig.

Befund (01.10.2026, Testauftrag 2026.10.01.12.38.09): `Kleidermodellbau.koerper` gab dem Körper die feste Farbe `HAUT`
(0,82 / 0,68 / 0,60) ohne UV und ohne Textur. Gerendert, benotet und vermessen wurde also eine blasse Einheitshaut —
Befund Körper: Foto (0,44 / 0,32 / 0,27), Render (0,77 / 0,63 / 0,56) —, egal wie gut die gebackene Haut war. Die Bühne
(`Standmodellglb.koerper`) zeigte sie, die Runde nie.

Die Netzstufe 0 trägt UV (je Browserpunkt, Kachel-lokal 0…1) und Materialgruppen mit `kachel`, `index_ab`,
`index_anzahl` — dieselbe Zerlegung wie `Standmodellglb.koerper`. Je Gruppe ein Eintrag im Format von
`Kleidermodellbau._textur` (`ab`/`anzahl` in Dreiecken, `albedo` = Pfad der Kachel, `faktor` 1). Ohne Kachel für eine
Gruppe bleibt sie bei `HAUT` (Faktor = Hautfarbe, kein Bild).
"""

import numpy as np

__all__ = ['Koerpertextur']


class Koerpertextur:
    @staticmethod
    def kacheln(job, ablage):
        """`{kachel: Pfad}` der gebackenen Hautkacheln des Auftrags (`ergebnis.fototextur.kacheln`), nur vorhandene."""
        aus = {}
        for k, name in (((job.ergebnis or {}).get('fototextur') or {}).get('kacheln') or {}).items():
            if str(k).isdigit() and ablage.ergebnis(name).is_file():
                aus[int(k)] = str(ablage.ergebnis(name))
        return aus

    @staticmethod
    def teil(punkte, stufe, haut, hautfarbe, kacheln=None):
        """Das Körperteil im Format von `Kleidermodellbau.teile` — mit UV und Textur, wenn es Kacheln gibt."""
        teil = {'punkte': punkte, 'dreiecke': np.asarray(stufe.dreiecke, dtype=np.int64),
                'farbe': np.asarray(hautfarbe), 'haut': haut, 'art': 'koerper', 'sorte': 'koerper', 'uv': None,
                'normalen': None, 'gruppen': [], 'textur': []}
        if not kacheln:
            return teil
        textur = []
        for g in stufe.gruppen or []:
            pfad = kacheln.get(int(g.get('kachel') or 1001))
            textur.append({'ab': int(g['index_ab']) // 3, 'anzahl': int(g['index_anzahl']) // 3, 'albedo': pfad,
                           'normalen': None, 'normalenachse': 1,
                           'faktor': np.ones(3) if pfad else np.asarray(hautfarbe, dtype=np.float64)})
        if not any(t['albedo'] for t in textur):
            return teil
        uv = np.asarray(stufe.uv, dtype=np.float64).reshape(-1, 2).copy()
        uv[:, 0] = np.clip(uv[:, 0], 0.0, 1.0)
        teil.update(uv=uv, textur=textur)
        return teil

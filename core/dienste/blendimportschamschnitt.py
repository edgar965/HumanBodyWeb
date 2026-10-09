# -*- coding: utf-8 -*-
"""Blendimportschamschnitt — ein Dreiecksnetz exakt an einer glatten Kontur abschneiden (09.10.2026).

BEFUND (Edgar: „Scham-Stück: keine helle, gesägte Zipfel an den Rändern!!", Chrome, „cute girl", Stück allein und mit Haut gesehen):
`Blendimportscham.auswahl` nahm GANZE Dreiecke, deren drei Ecken in der Hülle der Saat lagen — der Rand des Stücks folgte den
Dreiecken des Originals (4–8 mm), lief in Spitzen aus und stand als helle Zähne in den Leisten; dazu reichte die Hülle der Saat bis
±80 mm seitlich, so dass lange Flügel an den Oberschenkeln entlangliefen (die weiche Deckkraft am Rand, `stueckrand.js`, kann Zacken
dieser Größe nicht verstecken, sie folgt dem Netzrand).

HIER: Jeder Punkt bekommt einen Schnittwert `w` (negativ = innen, 0 = Kontur). Ein Dreieck mit gemischten Vorzeichen wird an der
Nullstelle geteilt (linear entlang der Kanten, Lage und UV je Ecke), der Teil außen fällt weg. Der Rand ist dann die Kontur selbst —
bei einer Hülle ein glatter Linienzug —, nicht mehr die Kante eines Dreiecks. Zwei Dreiecke an derselben Kante bekommen denselben
neuen Punkt (Schlüssel = Eckpunkte der Kante), das Netz bleibt dicht. Ohne Django, ohne Genesis, ohne trimesh (nur numpy).
"""

import numpy as np

__all__ = ['Blendimportschamschnitt']


class Blendimportschamschnitt:
    @staticmethod
    def schneiden(punkte, dreiecke, uv_ecken, werte):
        """`(punkte, dreiecke, uv_ecken)` des Teils mit `werte < 0`.

        `punkte` (n, 3), `dreiecke` (m, 3), `uv_ecken` (m, 3, 2) — UV je Ecke je Dreieck —, `werte` (n,). Die neuen Punkte stehen hinter
        den alten (die alten bleiben, auch unbenutzte); die Drehrichtung der Dreiecke bleibt erhalten."""
        punkte = np.asarray(punkte, dtype=np.float64)
        dreiecke = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        uv_ecken = np.asarray(uv_ecken, dtype=np.float64).reshape(-1, 3, 2)
        werte = np.asarray(werte, dtype=np.float64)
        neue, lage = [], {}                                       # neue Punkte; Kante (innen, außen) → Nummer

        def schnittpunkt(a, b):
            """Nummer des Punkts auf der Kante `a` (innen) – `b` (außen) bei `werte = 0`."""
            schluessel = (int(a), int(b))
            if schluessel not in lage:
                t = werte[a] / (werte[a] - werte[b])
                lage[schluessel] = len(punkte) + len(neue)
                neue.append(punkte[a] + t * (punkte[b] - punkte[a]))
            return lage[schluessel]

        def uv_punkt(uv, i, j, wi, wj):
            t = wi / (wi - wj)
            return uv[i] + t * (uv[j] - uv[i])

        aus_d, aus_uv = [], []
        innen = werte[dreiecke] < 0.0
        for tri, drin, uv in zip(dreiecke, innen, uv_ecken, strict=True):
            zahl = int(drin.sum())
            if zahl == 3:
                aus_d.append(tri)
                aus_uv.append(uv)
            elif zahl == 1:
                e = int(np.argmax(drin))                         # die eine Ecke innen; zyklisch geordnet bleibt die Drehrichtung
                a, b, c = tri[e], tri[(e + 1) % 3], tri[(e + 2) % 3]
                ab, ac = schnittpunkt(a, b), schnittpunkt(a, c)
                aus_d.append(np.array([a, ab, ac]))
                aus_uv.append(np.array([uv[e], uv_punkt(uv, e, (e + 1) % 3, werte[a], werte[b]),
                                        uv_punkt(uv, e, (e + 2) % 3, werte[a], werte[c])]))
            elif zahl == 2:
                e = int(np.argmin(drin))                         # die eine Ecke außen
                c, a, b = tri[e], tri[(e + 1) % 3], tri[(e + 2) % 3]      # a, b innen (in Drehrichtung nach c)
                ua, ub = uv[(e + 1) % 3], uv[(e + 2) % 3]
                ca, cb = schnittpunkt(a, c), schnittpunkt(b, c)           # Kanten a–c und b–c (innen, außen)
                uca = uv_punkt(uv, (e + 1) % 3, e, werte[a], werte[c])
                ucb = uv_punkt(uv, (e + 2) % 3, e, werte[b], werte[c])
                aus_d += [np.array([a, b, cb]), np.array([a, cb, ca])]
                aus_uv += [np.array([ua, ub, ucb]), np.array([ua, ucb, uca])]
        if neue:
            punkte = np.vstack([punkte, np.asarray(neue)])
        dreiecke_neu = np.asarray(aus_d, dtype=np.int64).reshape(-1, 3)
        uv_neu = np.asarray(aus_uv, dtype=np.float64).reshape(-1, 3, 2)
        return punkte, dreiecke_neu, uv_neu

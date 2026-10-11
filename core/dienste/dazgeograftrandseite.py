# -*- coding: utf-8 -*-
"""Dazgeograftrandseite — Punkte des Stücks, die hinter dem Ring auf der Hautseite liegen, ins Loch zurückschieben (11.10.2026).

BEFUND (Chrome und Python, „cute girl Daz Scham", Edgar: „löse das mit der Naht"): An den Ringkanten 16/17 und 58/59 lagen Haut- und Stückdreieck mit 147–160° aufeinander
zurückgeklappt (`Schammessungknick`). Ursache: die erste Punktreihe des Geografts hinter dem Ring stand 0,3–1,8 mm JENSEITS der Ringkante, auf der Seite des Hautdreiecks (Schnitt senkrecht
zur Kante: das Stück läuft vom Ring erst ein Stück zurück in die Haut, bevor es nach unten abknickt); das Viereck am Ring ist dort nicht-konvex, sein Dreieckspaar klappt um. An den Ringecken
11–19 und 57–65, wo die Haut selbst an der Leiste schmale Nadeldreiecke trägt (Seitenverhältnis bis 15).

HIER: Jeder Stückpunkt (außer den Randpunkten) bis `UMKREIS_M` von einer Ringkante liegt mindestens `ABSTAND_M` auf der Lochseite dieser Kante — gemessen in der Ebene des anliegenden
Hautdreiecks, senkrecht zur Kante, von der Spitze des Dreiecks weg. Wer weiter innen liegt, bleibt unberührt. Gemessen an der fertigen Stückdatei (Haut mit der Verschiebung der Glättung,
wie der Browser sie zeigt): Knick über die Naht größter Wert 147° → 55°, Kanten über 60°: 8 → 0; 57 Punkte bewegt, größte Verschiebung 2,1 mm.
"""
import numpy as np

__all__ = ['Dazgeograftrandseite']


class Dazgeograftrandseite:
    #: So weit (m) liegt ein Punkt hinter der Ringkante mindestens auf der Lochseite.
    ABSTAND_M = 0.001
    #: Punkte bis zu so weit (m) von einer Ringkante werden geprüft.
    UMKREIS_M = 0.003
    #: Ein Punkt nahe einer Ringecke kann gegen zwei Kanten verstoßen: nach dem Schieben an der nächsten wird neu gesucht (höchstens so oft).
    DURCHGAENGE = 3

    @classmethod
    def schieben(cls, punkte, figur, loch):
        """`(neue Punkte, bericht)`; `bericht`: `{bewegt, max_mm, kanten}`. `figur`: `{punkte, dreiecke}` (Stufe 1); `loch`: `{dreiecke, ring, ring_punkte, verschiebung}` des Baus."""
        from scipy.spatial import cKDTree

        from .schammessungknick import Schammessungknick

        p = np.array(punkte, dtype=np.float64)
        ring = np.asarray(loch['ring'], dtype=np.float64)
        ring_punkte = np.asarray(loch['ring_punkte'], dtype=np.int64)
        fp = Schammessungknick.haut_lage(figur, loch)
        kanten = cls._kanten(ring, ring_punkte, fp, Schammessungknick.ringkanten(fp, Schammessungknick.sichtbare(figur, loch), ring_punkte))
        if not kanten:
            return p, {'bewegt': 0, 'max_mm': 0.0, 'kanten': 0}
        anfang, richtung, laenge, ins = (np.array([k[i] for k in kanten]) for i in range(4))
        baum = cKDTree(anfang + 0.5 * laenge[:, None] * richtung)
        reichweite = cls.UMKREIS_M + 0.5 * float(laenge.max())
        auf_ring = set(int(i) for liste in cKDTree(p).query_ball_point(ring, 1e-7) for i in liste)
        vorher = p.copy()
        for _durchgang in range(cls.DURCHGAENGE):
            geschoben = 0
            for i, kandidaten in enumerate(baum.query_ball_point(p, reichweite)):
                if kandidaten and i not in auf_ring:
                    geschoben += cls._punkt_schieben(p, i, kandidaten, anfang, richtung, laenge, ins)
            if not geschoben:
                break
        weg = np.linalg.norm(p - vorher, axis=1)
        return p, {'bewegt': int((weg > 0).sum()), 'max_mm': round(float(weg.max()) * 1000.0, 2), 'kanten': int(len(kanten))}

    @classmethod
    def _punkt_schieben(cls, p, i, kandidaten, anfang, richtung, laenge, ins):
        """Punkt `i` an der nächsten der `kandidaten`-Ringkanten prüfen; liegt er näher als `UMKREIS_M` und weniger als `ABSTAND_M` auf der Lochseite, in `p` verschieben → 1, sonst 0."""
        bestes = None
        for j in kandidaten:
            t = np.clip((p[i] - anfang[j]) @ richtung[j], 0.0, laenge[j])
            vom_fuss = p[i] - (anfang[j] + richtung[j] * t)
            abstand = float(np.linalg.norm(vom_fuss))
            if bestes is None or abstand < bestes[0]:
                bestes = (abstand, j, float(vom_fuss @ ins[j]))
        if bestes[0] < cls.UMKREIS_M and bestes[2] < cls.ABSTAND_M - 1e-9:
            p[i] += ins[bestes[1]] * (cls.ABSTAND_M - bestes[2])
            return 1
        return 0

    @staticmethod
    def _kanten(ring, ring_punkte, fp, ringkanten):
        """`[(Anfang, Richtung, Länge, Lochrichtung)]` je Ringkante: die Lochrichtung liegt in der Ebene des Hautdreiecks, senkrecht zur Kante, von dessen Spitze weg."""
        k = len(ring)
        aus = []
        for j, t in ringkanten:
            a, b = j, (j + 1) % k
            r = ring[b] - ring[a]
            laenge = float(np.linalg.norm(r))
            spitze = [int(x) for x in t if int(x) not in (int(ring_punkte[a]), int(ring_punkte[b]))]
            if laenge < 1e-9 or not spitze:
                continue
            r = r / laenge
            h = fp[spitze[0]] - ring[a]
            h = h - r * (h @ r)
            ln = float(np.linalg.norm(h))
            if ln < 1e-12:
                continue
            aus.append((ring[a], r, laenge, -h / ln))
        return aus

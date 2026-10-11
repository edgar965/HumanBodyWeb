# -*- coding: utf-8 -*-
"""Schamnahtrandseite — Punkte eines Scham-Stücks, die hinter dem Ring auf der Hautseite liegen, ins Loch zurückschieben (11.10.2026; vorher `Dazgeograftrandseite`).

BEFUND (Chrome und Python, „cute girl Daz Scham", Edgar: „löse das mit der Naht"): An den Ringkanten 16/17 und 58/59 lagen Haut- und Stückdreieck mit 147–160° aufeinander
zurückgeklappt (`Schammessungknick`). Ursache: die erste Punktreihe des Geografts hinter dem Ring stand 0,3–1,8 mm JENSEITS der Ringkante, auf der Seite des Hautdreiecks (Schnitt senkrecht
zur Kante: das Stück läuft vom Ring erst ein Stück zurück in die Haut, bevor es nach unten abknickt); das Viereck am Ring ist dort nicht-konvex, sein Dreieckspaar klappt um. An den Ringecken
11–19 und 57–65, wo die Haut selbst an der Leiste schmale Nadeldreiecke trägt (Seitenverhältnis bis 15).

HIER: Jeder Stückpunkt (außer den Randpunkten) bis `UMKREIS_M` von einer Ringkante liegt mindestens `ABSTAND_M` auf der Lochseite dieser Kante — gemessen in der Ebene des anliegenden
Hautdreiecks, senkrecht zur Kante, von der Spitze des Dreiecks weg. Wer weiter innen liegt, bleibt unberührt. Gemessen an der fertigen Stückdatei (Haut mit der Verschiebung der Glättung,
wie der Browser sie zeigt): Knick über die Naht größter Wert 147° → 55°, Kanten über 60°: 8 → 0; 57 Punkte bewegt, größte Verschiebung 2,1 mm.

GENERISCH (11.10.2026, zweiter Durchgang): die Klasse gehört keinem Verfahren — sie läuft für das Daz-Geograft (`Dazgeograft.randseite`, auch die Basis-Stücke Frau und Mann; vorher: Frau 17 Ringkanten
über 60° mit größtem Knick 122°, Mann 23 mit 122°, danach 0 mit 55,7° / 50,9°) und für das Blender-Scham-Stück (`Blendimportschamgeograft.verschweissen`). Mehrere Durchgänge (`DURCHGAENGE`): ein Punkt
nahe einer Ringecke kann gegen zwei Kanten verstoßen (an der Kunsthaut mit rechtwinkligen Ecken blieb nach EINEM Durchgang eine Falte; am echten Ring, dessen Ecken flach sind, ändert es nichts —
gemessen: 65 / 2,51 mm und 83 / 3,01 mm vorher wie nachher).

SPITZEN (nur mit `dreiecke`): am Blender-Stück von „cute girl" (Import 08:45) blieben Ringkante 14 und 66 bei 178° und 168°, obwohl der Umkreis-Durchgang 130 Punkte schob: das Stückdreieck (2 mm²) hat zwei Ringecken
und eine DRITTE Ecke, die 5,5–6,6 mm von der Ringkante entfernt (am Ende der Kante, außerhalb von `UMKREIS_M`) und 1,3–1,5 mm hinter der KANTENLINIE liegt; die Entfernung zum Kantenstück hält den Punkt aus dem Umkreis,
das Dreieck klappt trotzdem um. Darum wird zusätzlich die Spitze jedes Stückdreiecks, das eine Ringkante trägt, gegen die Kantenlinie geprüft (ohne Umkreis).
"""
import numpy as np

__all__ = ['Schamnahtrandseite']


class Schamnahtrandseite:
    #: So weit (m) liegt ein Punkt hinter der Ringkante mindestens auf der Lochseite.
    ABSTAND_M = 0.001
    #: Punkte bis zu so weit (m) von einer Ringkante werden geprüft.
    UMKREIS_M = 0.003
    #: Ein Punkt nahe einer Ringecke kann gegen zwei Kanten verstoßen: nach dem Schieben an der nächsten wird neu gesucht (höchstens so oft).
    DURCHGAENGE = 3

    @classmethod
    def schieben(cls, punkte, figur, loch, dreiecke=None):
        """`(neue Punkte, bericht)`; `bericht`: `{bewegt, max_mm, kanten}`. `figur`: `{punkte, dreiecke}` (Stufe 1); `loch`: `{dreiecke, ring, ring_punkte, verschiebung}` des Baus;
        `dreiecke`: die des Stücks — mit ihnen wird auch die Spitze jedes Stückdreiecks an einer Ringkante geprüft (`SPITZEN` oben)."""
        from scipy.spatial import cKDTree

        from .schammessungknick import Schammessungknick

        p = np.array(punkte, dtype=np.float64)
        ring = np.asarray(loch['ring'], dtype=np.float64)
        ring_punkte = np.asarray(loch['ring_punkte'], dtype=np.int64)
        fp = Schammessungknick.haut_lage(figur, loch)
        kanten = cls._kanten(ring, ring_punkte, fp, Schammessungknick.ringkanten(fp, Schammessungknick.sichtbare(figur, loch), ring_punkte))
        if not kanten:
            return p, {'bewegt': 0, 'max_mm': 0.0, 'kanten': 0}
        anfang, richtung, laenge, ins = (np.array([k[i] for k in kanten]) for i in range(1, 5))
        baum = cKDTree(anfang + 0.5 * laenge[:, None] * richtung)
        reichweite = cls.UMKREIS_M + 0.5 * float(laenge.max())
        auf_ring_listen = cKDTree(p).query_ball_point(ring, 1e-7)
        auf_ring = set(int(i) for liste in auf_ring_listen for i in liste)
        spitzen = cls._spitzen(dreiecke, kanten, auf_ring_listen, auf_ring) if dreiecke is not None else []
        vorher = p.copy()
        for _durchgang in range(cls.DURCHGAENGE):
            geschoben = 0
            for i, kandidaten in enumerate(baum.query_ball_point(p, reichweite)):
                if kandidaten and i not in auf_ring:
                    geschoben += cls._punkt_schieben(p, i, kandidaten, anfang, richtung, laenge, ins)
            for i, k in spitzen:
                geschoben += cls._spitze_schieben(p, i, anfang[k], richtung[k], ins[k])
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

    @classmethod
    def _spitze_schieben(cls, p, i, anfang, richtung, ins):
        """Die Spitze `i` eines Stückdreiecks an der Ringkante (`anfang`, `richtung`): liegt sie gegen die Kantenlinie (nicht das Kantenstück) weniger als `ABSTAND_M` auf der Lochseite, in `p` verschieben → 1, sonst 0."""
        vom = p[i] - anfang
        seite = float((vom - richtung * (vom @ richtung)) @ ins)
        if seite < cls.ABSTAND_M - 1e-9:
            p[i] += ins * (cls.ABSTAND_M - seite)
            return 1
        return 0

    @staticmethod
    def _spitzen(dreiecke, kanten, auf_ring_listen, auf_ring):
        """`[(Punkt, Index in kanten)]`: die dritte Ecke jedes Stückdreiecks, das zwei benachbarte Ringecken trägt; Ecken, die selbst auf dem Ring liegen, zählen nicht."""
        d = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        k_ring = len(auf_ring_listen)
        aus = []
        for k, kante in enumerate(kanten):
            a, b = auf_ring_listen[kante[0]], auf_ring_listen[(kante[0] + 1) % k_ring]
            if not len(a) or not len(b):
                continue
            for t in d[np.isin(d, a).any(axis=1) & np.isin(d, b).any(axis=1)]:
                aus += [(int(x), k) for x in t if int(x) not in auf_ring]
        return aus

    @staticmethod
    def _kanten(ring, ring_punkte, fp, ringkanten):
        """`[(Ringecke j, Anfang, Richtung, Länge, Lochrichtung)]` je Ringkante: die Lochrichtung liegt in der Ebene des Hautdreiecks, senkrecht zur Kante, von dessen Spitze weg."""
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
            aus.append((j, ring[a], r, laenge, -h / ln))
        return aus

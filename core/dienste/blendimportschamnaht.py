# -*- coding: utf-8 -*-
"""Blendimportschamnaht — den Rand des Scham-Stücks genau auf den Kantenring des Hautlochs legen (09.10.2026).

Das Gegenstück zu `Blendimportschamloch`: Daz verschweißt das Geograft „Anatomical Elements" Punkt für Punkt mit einem Loch im Körper —
die Randpunkte des Stücks SIND Punkte der Haut. Das Stück kommt aus dem Original geschnitten (`Blendimportschamschnitt`), sein Rand ist
eine glatte Kontur, die ein paar Millimeter neben dem Ring liegt, den die Kanten der Haut bilden. Hier wird das Stück an diesen Ring
gelegt:

    einrasten    jeder Randpunkt rückt auf den nächsten Punkt des Rings; die Reihenfolge bleibt (kein Rand läuft rückwärts)
    ausklingen   die Verschiebung läuft über `BAND_MM` (Weg entlang der Kanten, Hermite) ins Stück aus — keine Stufe
    einfügen     jede Ecke des Rings, die kein Randpunkt ist, wird Randpunkt (die Kante des Stücks wird dort geteilt): der Rand
                 des Stücks läuft dann auf den Kanten der Haut und nicht an ihnen vorbei, und es bleibt kein Spalt
    zu den Ecken jeder Randpunkt, der KEINE Ecke ist, rückt in die nächste Ecke (Kantenkollaps am Rand): nach diesem Schritt hat der
                 Rand genau die Punkte des Rings — ein Punkt mitten auf einer Kante läge in Haltung neben ihr (Linear-Blend-Skinning
                 ist in den Gewichten nicht linear), eine Ecke teilt Lage und Gewichte mit dem Hautpunkt

Danach sind die Kanten des Rands genau die Kanten des Rings, jede einmal. Ohne Django. Der Ablauf im Ganzen: `Blendimportschamgeograft`.
"""

import numpy as np
from scipy import sparse
from scipy.sparse import csgraph

__all__ = ['Blendimportschamnaht']


class Blendimportschamnaht:
    #: Weg (mm) entlang der Kanten, über den die Verschiebung des Rands ins Stück ausläuft.
    BAND_MM = 10.0
    #: Ein Randpunkt, der so nah (mm) an einer Ecke des Rings landet, rastet in der Ecke ein.
    EINRASTEN_MM = 1.2
    #: Lose Stücke mit weniger Dreiecken fallen weg (Inseln, die der Schnitt übrig lässt).
    MINDEST_DREIECKE = 12

    def __init__(self, ring):
        """`ring` (k, 3): die Ecken des Kantenrings, geschlossen ohne Wiederholung der ersten Ecke (m, Ruhelage)."""
        self.ring = np.asarray(ring, dtype=np.float64)
        k = len(self.ring)
        self.ziel = np.roll(self.ring, -1, axis=0)
        self.seg = self.ziel - self.ring
        self.laenge = np.linalg.norm(self.seg, axis=1)
        #: Bogenlänge an der Ecke j; `gesamt` ist der Umfang.
        self.bogen = np.concatenate([[0.0], np.cumsum(self.laenge)[:-1]])
        self.gesamt = float(self.laenge.sum())
        if k < 3 or self.gesamt <= 0.0:
            raise ValueError('Kantenring zu klein')

    # ----------------------------------------------------------------- Rand

    @staticmethod
    def _insel_ab(punkte, dreiecke, uv_ecken, mindest):
        """Nur das größte zusammenhängende Stück (über gemeinsame Punkte), Punkte neu nummeriert."""
        n = len(punkte)
        a = np.concatenate([dreiecke[:, 0], dreiecke[:, 1]])
        b = np.concatenate([dreiecke[:, 1], dreiecke[:, 2]])
        _, lab = csgraph.connected_components(sparse.coo_matrix((np.ones(len(a)), (a, b)), shape=(n, n)), directed=False)
        je_dreieck = lab[dreiecke[:, 0]]
        gross = int(np.bincount(je_dreieck).argmax())
        behalten = je_dreieck == gross
        if int(behalten.sum()) < mindest:
            raise ValueError('Stück: nur %d zusammenhängende Dreiecke' % int(behalten.sum()))
        benutzt, neu = np.unique(dreiecke[behalten], return_inverse=True)
        return punkte[benutzt], neu.reshape(-1, 3), uv_ecken[behalten], int((~behalten).sum())

    @staticmethod
    def _randfolge(dreiecke):
        """Der längste Randring des Stücks als Folge von Punktnummern (sonst ValueError), dazu die Zahl der übrigen Ringe."""
        kanten = np.sort(np.concatenate([dreiecke[:, [0, 1]], dreiecke[:, [1, 2]], dreiecke[:, [2, 0]]]), axis=1)
        roh, zaehl = np.unique(kanten, axis=0, return_counts=True)
        rand = roh[zaehl == 1]
        nachbarn = {}
        for a, b in rand.tolist():
            nachbarn.setdefault(a, []).append(b)
            nachbarn.setdefault(b, []).append(a)
        if any(len(v) != 2 for v in nachbarn.values()):
            raise ValueError('Stück: der Rand ist kein einfacher Ring (Punkt mit mehr als zwei Randkanten)')
        gesehen, ringe = set(), []
        for start in nachbarn:
            if start in gesehen:
                continue
            folge, vor, cur = [start], -1, start
            gesehen.add(start)
            while True:
                a, b = nachbarn[cur]
                nxt = b if a == vor else a
                if nxt == start:
                    break
                folge.append(nxt)
                gesehen.add(nxt)
                vor, cur = cur, nxt
            ringe.append(folge)
        ringe.sort(key=len, reverse=True)
        return np.asarray(ringe[0], dtype=np.int64), len(ringe) - 1

    # --------------------------------------------------------------- Einrasten

    def _auf_ring(self, p):
        """Je Punkt `(Bogenlänge, Abstand)` des nächsten Punkts auf dem Ring."""
        v = p[:, None, :] - self.ring[None, :, :]
        t = np.clip((v * self.seg[None]).sum(-1) / np.maximum((self.seg ** 2).sum(-1), 1e-18)[None], 0.0, 1.0)
        nah = self.ring[None] + t[..., None] * self.seg[None]
        abstand = np.linalg.norm(p[:, None, :] - nah, axis=-1)
        j = abstand.argmin(axis=1)
        zeile = np.arange(len(p))
        return self.bogen[j] + t[zeile, j] * self.laenge[j], abstand[zeile, j]

    def _punkt_bei(self, s):
        """Punkte auf dem Ring bei den Bogenlängen `s`."""
        s = np.mod(s, self.gesamt)
        j = np.clip(np.searchsorted(self.bogen, s, side='right') - 1, 0, len(self.ring) - 1)
        t = (s - self.bogen[j]) / np.maximum(self.laenge[j], 1e-18)
        return self.ring[j] + t[:, None] * self.seg[j]

    def _gleichlaeufig(self, s):
        """Bogenlängen entlang der Randfolge `s`, aufgerollt und nicht rückläufig; `(u, richtung)`.
        Der Rand kehrt nie um — ein Rand, der rückwärts läuft, würde ein Dreieck umklappen."""
        ds = np.diff(np.append(s, s[0]))
        ds = np.mod(ds + self.gesamt / 2.0, self.gesamt) - self.gesamt / 2.0
        richtung = 1.0 if ds.sum() >= 0.0 else -1.0
        u = s[0] + np.concatenate([[0.0], np.cumsum(ds)[:-1]])
        u = richtung * u
        u = np.maximum.accumulate(u)
        u = np.minimum(u, u[0] + self.gesamt)
        return richtung * u, richtung

    def _einrasten(self, punkte, folge):
        """`(neue Lagen der Randpunkte, Bogenlängen u, Richtung)`."""
        s, _ = self._auf_ring(punkte[folge])
        u, richtung = self._gleichlaeufig(s)
        ecken = np.mod(self.bogen, self.gesamt)
        for i in range(len(u)):                       # in Ecken einrasten
            d = np.abs(np.mod(u[i] - ecken + self.gesamt / 2.0, self.gesamt) - self.gesamt / 2.0)
            j = int(d.argmin())
            if d[j] * 1000.0 < self.EINRASTEN_MM:
                u[i] += np.mod(ecken[j] - u[i] + self.gesamt / 2.0, self.gesamt) - self.gesamt / 2.0
        return self._punkt_bei(u), u, richtung

    def _ausklingen(self, punkte, dreiecke, folge, verschiebung):
        """Die Verschiebung der Randpunkte läuft über `BAND_MM` (Weg entlang der Kanten) ins Stück aus."""
        n = len(punkte)
        a = np.concatenate([dreiecke[:, 0], dreiecke[:, 1], dreiecke[:, 2]])
        b = np.concatenate([dreiecke[:, 1], dreiecke[:, 2], dreiecke[:, 0]])
        graph = sparse.csr_matrix((np.linalg.norm(punkte[a] - punkte[b], axis=1) * 1000.0 + 1e-9, (a, b)), shape=(n, n))
        weg, _, quelle = csgraph.dijkstra(graph, directed=False, indices=folge, min_only=True, return_predecessors=True)
        wert = np.zeros((n, 3))
        wo = np.flatnonzero(weg < self.BAND_MM)
        t = np.clip(weg[wo] / self.BAND_MM, 0.0, 1.0)
        halb = 1.0 - (3.0 * t ** 2 - 2.0 * t ** 3)
        platz = {int(v): i for i, v in enumerate(folge)}
        zeile = np.array([platz[int(quelle[v])] for v in wo])
        wert[wo] = halb[:, None] * verschiebung[zeile]
        return wert

    # --------------------------------------------------------------- Zusammenlegen

    @staticmethod
    def _zusammenlegen(punkte, dreiecke, uv_ecken, folge, u):
        """Aufeinanderfolgende Randpunkte, die auf demselben Punkt des Rings gelandet sind, werden einer (die Kante dazwischen hat Länge 0;
        ihr Dreieck entfällt). `(dreiecke, uv_ecken, folge, u, zusammengelegt)`."""
        n = len(folge)
        ersatz = np.arange(len(punkte))
        behalten = np.ones(n, dtype=bool)
        letzter = 0
        for j in range(1, n):
            if np.linalg.norm(punkte[folge[j]] - punkte[folge[letzter]]) < 1e-9:
                ersatz[folge[j]] = folge[letzter]
                behalten[j] = False
            else:
                letzter = j
        while n > 2 and letzter > 0 and np.linalg.norm(punkte[folge[letzter]] - punkte[folge[0]]) < 1e-9:    # der Schluss trifft den Anfang
            ersatz[folge[letzter]] = folge[0]
            behalten[letzter] = False
            letzter = int(np.flatnonzero(behalten[:letzter])[-1])
        if behalten.all():
            return dreiecke, uv_ecken, folge, u, 0
        dreiecke = ersatz[dreiecke]
        ganz = (dreiecke[:, 0] != dreiecke[:, 1]) & (dreiecke[:, 1] != dreiecke[:, 2]) & (dreiecke[:, 2] != dreiecke[:, 0])
        return dreiecke[ganz], uv_ecken[ganz], folge[behalten], u[behalten], int((~behalten).sum())

    # ----------------------------------------------------------------- Einfügen

    def _einfuegen(self, punkte, dreiecke, uv_ecken, folge, u, richtung):
        """Jede Ecke des Rings, die zwischen zwei Randpunkten liegt, wird Randpunkt. `(punkte, dreiecke, uv_ecken, anzahl)`."""
        punkte = [p for p in punkte]
        dreiecke = [d for d in dreiecke]
        uv_ecken = [x for x in uv_ecken]
        eingefuegt = 0
        n = len(folge)
        ecken = np.mod(self.bogen, self.gesamt)
        for i in range(n):
            a, b = int(folge[i]), int(folge[(i + 1) % n])
            u0 = u[i]
            u1 = u[(i + 1) % n] if i + 1 < n else u[0] + richtung * self.gesamt
            lo, hi = (u0, u1) if richtung > 0 else (u1, u0)
            kandidaten = []
            for umlauf in (-1, 0, 1, 2):
                s = ecken + (np.floor(lo / self.gesamt) + umlauf) * self.gesamt
                kandidaten += [(float(x), j) for j, x in enumerate(s) if lo + 1e-9 < x < hi - 1e-9]
            if not kandidaten:
                continue
            kandidaten.sort(key=lambda c: c[0], reverse=(richtung < 0))
            neu = []
            for _bogen, j in kandidaten:
                punkte.append(self.ring[j].copy())
                neu.append(len(punkte) - 1)
            gefunden = None
            for t, tri in enumerate(dreiecke):
                for e in range(3):
                    if (int(tri[e]), int(tri[(e + 1) % 3])) in ((a, b), (b, a)):
                        gefunden = (t, e)
                        break
                if gefunden:
                    break
            if gefunden is None:
                raise ValueError('Stück: Randkante %d–%d nicht gefunden' % (a, b))
            t, e = gefunden
            tri, uv = dreiecke[t], uv_ecken[t]
            p, q, c = int(tri[e]), int(tri[(e + 1) % 3]), int(tri[(e + 2) % 3])
            up, uq, uc = uv[e], uv[(e + 1) % 3], uv[(e + 2) % 3]
            kette = [p] + (neu if p == a else neu[::-1]) + [q]
            gesamt_len = max(float(np.linalg.norm(punkte[q] - punkte[p])), 1e-18)
            uvs = [up] + [up + (uq - up) * float(np.linalg.norm(punkte[v] - punkte[p])) / gesamt_len for v in kette[1:-1]] + [uq]
            fans = [np.array([kette[k], kette[k + 1], c]) for k in range(len(kette) - 1)]
            fan_uv = [np.array([uvs[k], uvs[k + 1], uc]) for k in range(len(kette) - 1)]
            dreiecke[t:t + 1] = fans
            uv_ecken[t:t + 1] = fan_uv
            eingefuegt += len(neu)
        return np.asarray(punkte), np.asarray(dreiecke, dtype=np.int64), np.asarray(uv_ecken, dtype=np.float64), eingefuegt

    # -------------------------------------------------------------- Zu den Ecken

    def _zu_ecken(self, punkte, dreiecke):
        """Jeder Randpunkt, der keine Ecke des Rings ist, rückt in die nächste Ecke (Kantenkollaps entlang des Rands): der Rand des
        Stücks hat dann genau die Punkte des Rings, und seine Kanten sind die Kanten der Haut.

        WARUM (Chrome, „cute girl", Oberschenkel um 25° gespreizt, `__spreizen`): Ein Randpunkt MITTEN auf einer Kante der Haut trägt
        die gemischten Gewichte ihrer beiden Enden, und Linear-Blend-Skinning ist in den Gewichten nicht linear — in Haltung liegt der
        Punkt neben der Kante (Rand-Spalt bis 1–2 mm, dunkle Haarlinie rund ums Stück). Eine Ecke teilt Lage UND Gewichte mit dem
        Hautpunkt, dort gibt es keinen Spalt, in keiner Haltung. `(dreiecke, behalten, zahl)`: `behalten` je Dreieck (die Kollabierten
        fallen weg), `zahl` der gewanderten Randpunkte; die UV bleiben je Ecke, wie sie waren (die Textur wird dort um höchstens eine
        halbe Kante gestreckt)."""
        folge, _ = self._randfolge(dreiecke)
        n = len(folge)
        ecke = np.zeros(n, dtype=bool)
        for i, p in enumerate(punkte[folge]):
            ecke[i] = float(np.min(np.linalg.norm(self.ring - p, axis=1))) < 1e-9
        if not ecke.any():
            raise ValueError('Stück: kein Randpunkt liegt auf einer Ecke des Rings')
        ersatz = np.arange(len(punkte))
        ids = np.flatnonzero(ecke)
        for i in range(n):
            if ecke[i]:
                continue
            # nächste Ecken davor und dahinter, gezählt entlang des Rands (in Randpunkten) — zur näheren hin
            davor = int(ids[(np.searchsorted(ids, i) - 1) % len(ids)])
            dahinter = int(ids[np.searchsorted(ids, i) % len(ids)])
            wege = [(np.linalg.norm(punkte[folge[i]] - punkte[folge[ziel]]), ziel) for ziel in (davor, dahinter)]
            ersatz[folge[i]] = folge[min(wege)[1]]
        neu = ersatz[dreiecke]
        ganz = (neu[:, 0] != neu[:, 1]) & (neu[:, 1] != neu[:, 2]) & (neu[:, 2] != neu[:, 0])
        return neu[ganz], ganz, int((~ecke).sum())

    # ------------------------------------------------------------------- Lauf

    @staticmethod
    def flaechennormalen(punkte, dreiecke):
        """Nicht normierte Flächennormale je Dreieck."""
        return np.cross(punkte[dreiecke[:, 1]] - punkte[dreiecke[:, 0]], punkte[dreiecke[:, 2]] - punkte[dreiecke[:, 0]])

    @classmethod
    def _umgeklappt(cls, vorher, nachher, dreiecke):
        """Zahl der Dreiecke, deren Normale sich um mehr als 90° gedreht hat."""
        return int(((cls.flaechennormalen(vorher, dreiecke) * cls.flaechennormalen(nachher, dreiecke)).sum(axis=1) < 0.0).sum())

    def anlegen(self, punkte, dreiecke, uv_ecken):
        """`(punkte, dreiecke, uv_ecken, bericht)`: das Stück mit dem Rand auf dem Ring. `uv_ecken` (m, 3, 2) je Ecke je Dreieck."""
        punkte = np.asarray(punkte, dtype=np.float64)
        dreiecke = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        uv_ecken = np.asarray(uv_ecken, dtype=np.float64).reshape(-1, 3, 2)
        punkte, dreiecke, uv_ecken, inseln = self._insel_ab(punkte, dreiecke, uv_ecken, self.MINDEST_DREIECKE)
        folge, ringe_mehr = self._randfolge(dreiecke)
        neu_rand, u, richtung = self._einrasten(punkte, folge)
        weg = np.linalg.norm(neu_rand - punkte[folge], axis=1) * 1000.0
        verschiebung = neu_rand - punkte[folge]
        neu = punkte + self._ausklingen(punkte, dreiecke, folge, verschiebung)
        neu[folge] = neu_rand
        umgeklappt = self._umgeklappt(punkte, neu, dreiecke)
        dreiecke, uv_ecken, folge, u, zusammen = self._zusammenlegen(neu, dreiecke, uv_ecken, folge, u)
        aus_p, aus_d, aus_uv, eingefuegt = self._einfuegen(neu, dreiecke, uv_ecken, folge, u, richtung)
        vor_ecken = aus_d
        aus_d, ganz, gewandert = self._zu_ecken(aus_p, aus_d)
        aus_uv = aus_uv[ganz]
        bericht = {'rand_punkte': int(len(folge)), 'rand_weg_median_mm': round(float(np.median(weg)), 2),
                   'rand_weg_p90_mm': round(float(np.percentile(weg, 90)), 2), 'rand_weg_max_mm': round(float(weg.max()), 2),
                   'ecken_eingefuegt': eingefuegt, 'ring_ecken': int(len(self.ring)), 'inseln_weg': inseln,
                   'weitere_ringe': ringe_mehr, 'umgeklappt': umgeklappt, 'zusammengelegt': zusammen,
                   'zu_ecken': gewandert, 'dreiecke_weg': int((~ganz).sum()),
                   'umgeklappt_nach_ecken': int(((self.flaechennormalen(aus_p, vor_ecken[ganz]) * self.flaechennormalen(aus_p, aus_d)).sum(axis=1) < 0.0).sum())}
        return aus_p, aus_d, aus_uv, bericht

# -*- coding: utf-8 -*-
"""Blendimportschamloch — das Loch in der Haut unter dem Scham-Stück als Kantenring der Figur (09.10.2026).

WARUM (Edgar, 09.10.2026, mit Bild: „bei der Scham gibt es immer noch die Probleme an den Rändern. Schau nach, wie Genesis das mit der
Nase und dem Mund macht, und mach es genau so"): Bei Genesis ist ein Rand nie eine Überlappung, sondern eine Kante: Lippen und Mundhöhle
sind EIN Netz, die Randpunkte gehören beiden Flächen (Material `Mouth Cavity` in derselben Kachel wie der Kopf, `G9basisnetz`), und Daz'
Geograft „Anatomical Elements" verschweißt seine Randpunkte mit den Punkten eines Lochs im Körper. Bis heute entschied dagegen der
Browser zur Laufzeit, welche Haut weg muss (Strahlen entlang der Normalen, Splitter, Lücken, `hautverdeckung.js`) — das Loch war der
Rest einer Rechnung und sein Rand ein Stern aus ganzen Dreiecken, das Stück endete irgendwo daneben (gesehen im Chrome: dunkle Keile
bis zum Hintergrund, helle Zipfel).

HIER: das Loch wird beim Bau festgelegt, als Menge ganzer Dreiecke der Figur (Stufe 1 — dieselbe Dreiecksfolge wie im Browser, gemessen
09.10.2026: 201.248 Dreiecke, gleiche Prüfsumme), mit EINEM geschlossenen Rand aus Kanten der Figur. `Blendimportschamnaht` legt den Rand
des Stücks genau auf diesen Ring. Ohne Django, ohne Genesis (nur numpy/scipy).

Der Ablauf: Dreiecke, deren Mitte im Schnittbereich liegt (`werte` < 0, die Hülle der Saat von `Blendimportscham.schnittwerte`) →
Mittel über die Nachbardreiecke (die Kontur verliert Zacken und Kerben) → größtes zusammenhängendes Stück → eingeschlossene Löcher füllen
→ Engstellen im Rand schließen. Nachbarschaft zählt nach Lage verschweißt: die Figur ist an UV-Nähten geteilt (7.700 offene Kanten
ungeschweißt, 104 verschweißt).
"""

import numpy as np
from scipy import sparse
from scipy.sparse import csgraph

__all__ = ['Blendimportschamloch']


class Blendimportschamloch:
    #: Punkte mit gleicher Lage (auf diese Größe in m gerundet) sind derselbe Punkt der Figur.
    LAGE_M = 1e-6
    #: Durchgänge, in denen jedes Dreieck ins Mittel seiner Nachbarn rückt (Kerben und Zacken der Kontur verschwinden), und das Eigengewicht.
    GLAETTEN = 8
    EIGEN = 0.2
    #: Öffnen und Schließen (m, Weg über die Dreiecksmitten): Streifen und Kerben unter zwei Radien Breite verschwinden.
    RADIUS_M = 0.004
    #: Weniger Dreiecke ist kein Loch.
    MINDEST = 20
    #: Höchstens so viele Runden, um Engstellen im Rand zu schließen.
    ENGSTELLEN_MAX = 12

    def __init__(self, punkte, dreiecke):
        """`punkte` (n, 3) und `dreiecke` (m, 3): die Haut der Figur in Ruhelage (Stufe 1 — die Dreiecke des Browsers)."""
        self.punkte = np.asarray(punkte, dtype=np.float64)
        self.dreiecke = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        schluessel = np.round(self.punkte / self.LAGE_M).astype(np.int64)
        _, erste, self.rep = np.unique(schluessel, axis=0, return_index=True, return_inverse=True)
        self.rep = self.rep.ravel()
        #: Je verschweißtem Punkt der erste Punkt der Figur (für Gewichte und Lage).
        self.figurpunkt = erste
        self.verschweisst = self.rep[self.dreiecke]
        self._graph = None
        self._kanten()

    # ------------------------------------------------------------- Nachbarschaft

    def _kanten(self):
        """Kanten (verschweißt) und je Kante die beiden Dreiecke; `nachbar` ist die Dreiecks-Nachbarschaft als Matrix."""
        m = len(self.verschweisst)
        a = self.verschweisst[:, [0, 1, 2]].ravel()
        b = self.verschweisst[:, [1, 2, 0]].ravel()
        n = int(self.rep.max()) + 1
        lo, hi = np.minimum(a, b), np.maximum(a, b)
        schluessel = lo * n + hi
        dreieck = np.repeat(np.arange(m), 3)
        ordnung = np.argsort(schluessel, kind='stable')
        s, t = schluessel[ordnung], dreieck[ordnung]
        gleich = s[1:] == s[:-1]
        if np.any(s[2:] == s[:-2]):
            raise ValueError('Haut hat eine Kante mit mehr als zwei Dreiecken')
        paar_a, paar_b = t[:-1][gleich], t[1:][gleich]
        self.n_punkte = n
        self._schluessel, self._dreieck = s, t
        self.nachbar = sparse.coo_matrix((np.ones(len(paar_a) * 2), (np.r_[paar_a, paar_b], np.r_[paar_b, paar_a])), shape=(m, m)).tocsr()
        self.grad = np.asarray(self.nachbar.sum(axis=1)).ravel()

    def _abstand_zu(self, maske):
        """Weg (m) über die Dreiecksmitten zum nächsten Dreieck in `maske` (Infinity, wo keines erreichbar ist)."""
        quellen = np.flatnonzero(maske)
        if not len(quellen):
            return np.full(len(maske), np.inf)
        graph = self._weglaenge()
        return csgraph.dijkstra(graph, directed=False, indices=quellen, min_only=True)

    def _weglaenge(self):
        """Die Nachbarschaftsmatrix, gewichtet mit dem Abstand der Dreiecksmitten (m); einmal gebaut."""
        if self._graph is None:
            mitte = self.punkte[self.dreiecke].mean(axis=1)
            a, b = self.nachbar.nonzero()
            gewicht = np.linalg.norm(mitte[a] - mitte[b], axis=1) + 1e-12
            self._graph = sparse.csr_matrix((gewicht, (a, b)), shape=self.nachbar.shape)
        return self._graph

    def _oeffnen(self, h, radius):
        """Erst `radius` abtragen, dann `radius` wieder zugeben (nur innerhalb des alten Lochs): Streifen und Zacken, die schmaler
        als zwei Radien sind, verschwinden — die Teile der Dichte eines Dreiecks (2–3 mm breit) an den steilen Wänden des Damms."""
        kern = self._abstand_zu(~h) > radius
        if not kern.any():
            return h
        return h & (self._abstand_zu(kern) <= radius)

    def _schliessen(self, h, radius):
        """Das Gegenstück: Kerben, die schmaler als zwei Radien sind, füllen sich."""
        voll = self._abstand_zu(h) <= radius
        return (self._abstand_zu(~voll) > radius) | h

    def komponenten(self, maske):
        """Nummer der zusammenhängenden Gruppe je Dreieck in `maske` (−1 außerhalb) und die Anzahl der Gruppen."""
        idx = np.flatnonzero(maske)
        marke = -np.ones(len(maske), dtype=np.int64)
        if not len(idx):
            return marke, 0
        n, lab = csgraph.connected_components(self.nachbar[idx][:, idx], directed=False)
        marke[idx] = lab
        return marke, int(n)

    def groesste(self, maske):
        marke, n = self.komponenten(maske)
        if n == 0:
            return maske
        return marke == int(np.bincount(marke[marke >= 0]).argmax())

    # --------------------------------------------------------------------- Loch

    def loch(self, werte):
        """Bool je Dreieck: im Loch. `werte` je Punkt der Figur, negativ = im Schnittbereich (Mitte des Dreiecks zählt)."""
        werte = np.asarray(werte, dtype=np.float64)
        h = self.groesste(werte[self.dreiecke].mean(axis=1) < 0.0)
        h = self.groesste(self._oeffnen(h, self.RADIUS_M))
        h = self._schliessen(h, self.RADIUS_M)
        f = h.astype(np.float64)
        teiler = np.maximum(self.grad, 1.0)
        for _ in range(self.GLAETTEN):
            # Mehrheit der Nachbarn mit wenig Eigengewicht: ein Dreieck, das nur an einer Kante im Loch hängt (Ohr), fällt weg, eine
            # Kerbe (zwei von drei Nachbarn im Loch) füllt sich. Mit halbem Eigengewicht blieben Ohren stehen (0,5 + 0,5/3 > 0,5).
            f = self.EIGEN * f + (1.0 - self.EIGEN) * (self.nachbar @ f) / teiler
        h = self.groesste(f > 0.5)
        h = self._eingeschlossene_fuellen(h)
        h = self._engstellen_schliessen(h)
        if int(h.sum()) < self.MINDEST:
            raise ValueError('Hautloch: nur %d Dreiecke' % int(h.sum()))
        return h

    def _eingeschlossene_fuellen(self, h):
        marke, n = self.komponenten(~h)
        if n <= 1:
            return h
        zahl = np.bincount(marke[marke >= 0], minlength=n)
        aussen = int(zahl.argmax())
        for k in range(n):
            if k != aussen:
                h = h | (marke == k)
        return h

    def randkanten(self, h):
        """Kanten (verschweißte Punktnummern, je `(klein, groß)`), die genau ein Dreieck des Lochs berühren."""
        s, t = self._schluessel, self._dreieck
        gleich = np.r_[s[1:] == s[:-1], False]          # Kante `i` hat ein Paar mit `i + 1`
        paar = np.flatnonzero(gleich)
        einzel = np.ones(len(s), dtype=bool)
        einzel[paar] = False
        einzel[paar + 1] = False
        rand = np.r_[paar[h[t[paar]] != h[t[paar + 1]]], np.flatnonzero(einzel & h[t])]
        schluessel = s[rand]
        return np.stack([schluessel // self.n_punkte, schluessel % self.n_punkte], axis=1)

    def _engstellen_schliessen(self, h):
        """Ein Punkt mit mehr als zwei Randkanten ist eine Engstelle (der Rand berührt sich selbst): die Dreiecke um ihn, die nicht im
        Loch liegen, kommen dazu, bis der Rand einfach ist."""
        for _ in range(self.ENGSTELLEN_MAX):
            kanten = self.randkanten(h)
            zahl = np.bincount(kanten.ravel(), minlength=self.n_punkte)
            eng = np.flatnonzero(zahl > 2)
            if not len(eng):
                return h
            enger = np.zeros(self.n_punkte, dtype=bool)
            enger[eng] = True
            h = h | enger[self.verschweisst].any(axis=1)
            h = self._eingeschlossene_fuellen(self.groesste(h))
        raise ValueError('Hautloch: der Rand bleibt nicht einfach')

    # --------------------------------------------------------------------- Ring

    def ring(self, h):
        """Der Rand des Lochs als geordnete Folge verschweißter Punktnummern (geschlossen, ohne Wiederholung des ersten)."""
        kanten = self.randkanten(h)
        nachbarn = {}
        for a, b in kanten.tolist():
            nachbarn.setdefault(a, []).append(b)
            nachbarn.setdefault(b, []).append(a)
        if any(len(v) != 2 for v in nachbarn.values()):
            raise ValueError('Hautloch: der Rand ist kein einfacher Ring')
        start = int(kanten[0][0])
        folge, vor, cur = [start], -1, start
        while True:
            a, b = nachbarn[cur]
            nxt = b if a == vor else a
            if nxt == start:
                break
            folge.append(nxt)
            vor, cur = cur, nxt
        if len(folge) != len(nachbarn):
            raise ValueError('Hautloch: der Rand hat mehrere Ringe (%d von %d Punkten im ersten)' % (len(folge), len(nachbarn)))
        return np.asarray(folge, dtype=np.int64)

    def lage(self, ring):
        """Die Punkte des Rings (m): Lage des ersten Punkts der Figur je verschweißtem Punkt."""
        return self.punkte[self.figurpunkt[np.asarray(ring)]]

    def ringpunkte(self, ring):
        """Die Nummern der Figurpunkte zum Ring (der erste Punkt jeder Lage — Gewichte sind je Lage gleich)."""
        return self.figurpunkt[np.asarray(ring)]

    def bericht(self, h, ring):
        lage = self.lage(ring)
        seg = np.linalg.norm(np.diff(np.vstack([lage, lage[:1]]), axis=0), axis=1)
        return {'dreiecke': int(h.sum()), 'ring_punkte': int(len(ring)), 'ring_mm': round(float(seg.sum()) * 1000.0, 1),
                'segment_max_mm': round(float(seg.max()) * 1000.0, 1)}

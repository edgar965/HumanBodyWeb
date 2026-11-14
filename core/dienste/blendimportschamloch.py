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

import math
import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.kartenduenn import Kartenduenn as sparse
from KoerperKI_alle.kartengraph import Kartengraph as csgraph

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
        self.punkte = Torchfeld.feld(punkte, dtype=torch.float64)
        self.dreiecke = Torchfeld.feld(dreiecke, dtype=torch.int64).reshape(-1, 3)
        schluessel = Torchfeld.astype(Torchfeld.round(self.punkte / self.LAGE_M), torch.int64)
        _, erste, self.rep = Torchfeld.unique(schluessel, axis=0, return_index=True, return_inverse=True)
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
        lo, hi = Torchfeld.minimum(a, b), Torchfeld.maximum(a, b)
        schluessel = lo * n + hi
        dreieck = Torchfeld.repeat_interleave(Torchfeld.arange(m), 3)
        ordnung = torch.argsort(schluessel, stable=True)
        s, t = schluessel[ordnung], dreieck[ordnung]
        gleich = s[1:] == s[:-1]
        if Torchfeld.any(s[2:] == s[:-2]):
            raise ValueError('Haut hat eine Kante mit mehr als zwei Dreiecken')
        paar_a, paar_b = t[:-1][gleich], t[1:][gleich]
        self.n_punkte = n
        self._schluessel, self._dreieck = s, t
        self.nachbar = sparse.coo_matrix((torch.ones(len(paar_a) * 2, dtype=torch.float64, device='cuda'), (Torchfeld.r_[paar_a, paar_b], Torchfeld.r_[paar_b, paar_a])), shape=(m, m)).tocsr()
        self.grad = Torchfeld.feld(self.nachbar.sum(axis=1)).ravel()

    def _abstand_zu(self, maske):
        """Weg (m) über die Dreiecksmitten zum nächsten Dreieck in `maske` (Infinity, wo keines erreichbar ist)."""
        quellen = torch.flatten(maske).nonzero()[:, 0]
        if not len(quellen):
            return Torchfeld.full(len(maske), math.inf)
        graph = self._weglaenge()
        return csgraph.dijkstra(graph, directed=False, indices=quellen, min_only=True)

    def _weglaenge(self):
        """Die Nachbarschaftsmatrix, gewichtet mit dem Abstand der Dreiecksmitten (m); einmal gebaut."""
        if self._graph is None:
            mitte = self.punkte[self.dreiecke].mean(axis=1)
            a, b = torch.nonzero(Torchfeld.feld(self.nachbar), as_tuple=True)
            gewicht = Torchfeld.linalg_norm(mitte[a] - mitte[b], dim=1) + 1e-12
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
        idx = torch.flatten(maske).nonzero()[:, 0]
        marke = -torch.ones(len(maske), dtype=torch.int64, device='cuda')
        if not len(idx):
            return marke, 0
        n, lab = csgraph.connected_components(self.nachbar[idx][:, idx], directed=False)
        marke[idx] = lab
        return marke, int(n)

    def groesste(self, maske):
        marke, n = self.komponenten(maske)
        if n == 0:
            return maske
        return marke == int(Torchfeld.bincount(marke[marke >= 0]).argmax())

    # --------------------------------------------------------------------- Loch

    def loch(self, werte):
        """Bool je Dreieck: im Loch. `werte` je Punkt der Figur, negativ = im Schnittbereich (Mitte des Dreiecks zählt)."""
        werte = Torchfeld.feld(werte, dtype=torch.float64)
        h = self.groesste(werte[self.dreiecke].mean(axis=1) < 0.0)
        h = self.groesste(self._oeffnen(h, self.RADIUS_M))
        h = self._schliessen(h, self.RADIUS_M)
        f = Torchfeld.astype(h, torch.float64)
        teiler = Torchfeld.maximum(self.grad, 1.0)
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
        zahl = Torchfeld.bincount(marke[marke >= 0], minlength=n)
        aussen = int(zahl.argmax())
        for k in range(n):
            if k != aussen:
                h = h | (marke == k)
        return h

    def randkanten(self, h):
        """Kanten (verschweißte Punktnummern, je `(klein, groß)`), die genau ein Dreieck des Lochs berühren."""
        s, t = self._schluessel, self._dreieck
        gleich = Torchfeld.r_[s[1:] == s[:-1], False]          # Kante `i` hat ein Paar mit `i + 1`
        paar = torch.flatten(gleich).nonzero()[:, 0]
        einzel = torch.ones(len(s), dtype=torch.bool, device='cuda')
        einzel[paar] = False
        einzel[paar + 1] = False
        rand = Torchfeld.r_[paar[h[t[paar]] != h[t[paar + 1]]], torch.flatten(einzel & h[t]).nonzero()[:, 0]]
        schluessel = s[rand]
        return Torchfeld.stack([schluessel // self.n_punkte, schluessel % self.n_punkte], axis=1)

    def _engstellen_schliessen(self, h):
        """Ein Punkt mit mehr als zwei Randkanten ist eine Engstelle (der Rand berührt sich selbst): die Dreiecke um ihn, die nicht im
        Loch liegen, kommen dazu, bis der Rand einfach ist."""
        for _ in range(self.ENGSTELLEN_MAX):
            kanten = self.randkanten(h)
            zahl = Torchfeld.bincount(kanten.ravel(), minlength=self.n_punkte)
            eng = torch.flatten(zahl > 2).nonzero()[:, 0]
            if not len(eng):
                return h
            enger = torch.zeros(self.n_punkte, dtype=torch.bool, device='cuda')
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
        return Torchfeld.feld(folge, dtype=torch.int64)

    def lage(self, ring):
        """Die Punkte des Rings (m): Lage des ersten Punkts der Figur je verschweißtem Punkt."""
        return self.punkte[self.figurpunkt[Torchfeld.feld(ring)]]

    def ringpunkte(self, ring):
        """Die Nummern der Figurpunkte zum Ring (der erste Punkt jeder Lage — Gewichte sind je Lage gleich)."""
        return self.figurpunkt[Torchfeld.feld(ring)]

    def bericht(self, h, ring):
        lage = self.lage(ring)
        seg = Torchfeld.linalg_norm(Torchfeld.diff(Torchfeld.vstack([lage, lage[:1]]), dim=0), dim=1)
        return {'dreiecke': int(h.sum()), 'ring_punkte': int(len(ring)), 'ring_mm': round(float(seg.sum()) * 1000.0, 1),
                'segment_max_mm': round(float(seg.max()) * 1000.0, 1)}

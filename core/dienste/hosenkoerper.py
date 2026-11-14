# -*- coding: utf-8 -*-
"""Hosenkoerper — die Hose des Stand-Modells aus dem Körpernetz statt aus den Schnittbahnen (04.10.2026).

Anlass (Edgar, 04.10.2026): „Hose zwischen den Beinen kaputt, Hose viel zu eng anliegend, die Drapierungen fehlen", und „beim Play im 3D-View kommt die Haut durch die Hose".
Gemessen am Stand von Runde 59 (`ProjektTemp/_wegwerf/randy/hose/hose_abstand.py`): Die Hose aus den GarmentCode-Bahnen liegt im Median 7,6 mm auf der Haut (p10 4,6 mm, p90 11,1 mm) —
wie ein Strumpf mit den Muskeln darunter, trotz `bau.anliegen_mm` 30 und Stoffsolver-Drapierung. Im Schritt klafft die Naht zwischen Vorder- und Rückenbahn als Sägezahn
(Bühne, `zeigen/r59_schritt_vorn.png`): Die Bahnen sind nicht verschweißt, ihre Punktreihen passen nicht aufeinander (72 % der Randpunkte haben einen Gegenpunkt unter 2 mm, 22 % liegen 4–10 mm
daneben; `hose/hose_naehte.py`).

Hier entsteht die Hose aus dem Körpernetz (Hüfte bis Knöchel): die Dreiecke des Körpers im Höhenband der GC-Hose, zusammenhängend und ohne Nähte; Verformung in drei Schritten:
1. Glätten (Taubin, ohne Schrumpfen) — der Stoff überbrückt die Muskeln, statt sie nachzuzeichnen; der vordere Schrittbereich wird stärker geglättet (kein Körperrelief im Stoff).
2. Abstand zur Haut nach Höhe (`ABSTAND`: Saum 20, Wade 16, Knie 14, Oberschenkel 22, Hüfte 22 → 20, Bund 12 mm; Augenmaß gegen die Vorlage, nicht gemessen) entlang der Normalen, danach mindestens `MINDEST` zum nächsten Körperpunkt.
3. Drapierung (`Hosenfalten.anwenden`: Fächer vom Schritt, Knie, Saum).
Die Hautgewichte (Knochen und Gewichte) stammen vom nächsten Körperpunkt — im Play folgt der Stoff der Haut, der Abstand bleibt.

UV: zylindrisch um jedes Bein (U = Winkel um den Ring der Höhe, 0,5 an der Außennaht, V = Höhe); das Bild ist weiß mit dem Seitenstreifen der Vorlage (`Hosenstreifen.muster`: rot, schwarze Linie,
zweireihiges Karo), Breiten nach Augenmaß aus `vergleich/hose_streifen.png`. Dreiecke, die über die Rückseite des Rings (U 0/1) laufen, bekommen eigene Eckpunkte mit U + 1 (Wiederholung).

    gebaut = Hosenkoerper(koerper_punkte, koerper_dreiecke).bauen(ymin, ymax)       # {punkte, dreiecke, uv, quelle}; uv v nach oben (Daz), `Standmodellglb._uv` dreht
    bild = Hosenkoerper.textur(gebaut)                                              # PIL-Bild RGB"""

import math
import torch
from KoerperKI_alle.torchfeld import Torchfeld

__all__ = ['Hosenkoerper']


class Hosenkoerper:
    BREITE_X = 0.27           # nur Körperdreiecke innerhalb |x| (m): Beine und Hüfte, keine Arme und Hände
    BAND = 0.01               # Höhe der Zeilen der Radiustabelle für das Bild (m)
    FENSTER = 0.04            # halbe Höhe des Fensters, über das Mitte und Radius des Beinrings gemittelt werden (m)
    RAND = 0.015              # Dreiecke bis so weit außerhalb des Höhenbands bleiben; ihre Punkte werden danach auf den Rand gelegt (gerader Saum und Bund)
    #: (Höhe als Anteil der Beinlänge Schritt → Saum bis 1,0; darüber m über dem Schritt) → Abstand zur Haut (m)
    #: Saum 20 mm: der Stiefelschaft (Radius > Hose bei 6 mm) stand sonst goldfarben durch den Saum.
    #: 04.10.2026 (Edgar: „Beine viel zu dick"): Wade 16 → 10, Knie 14 → 8, Oberschenkel 22 → 12 mm. Gemessen am Stand von Runde 60 (`hose/beine_vergleich.py`) lag die Hose
    #: 34–42 mm breiter als der Körper (Oberschenkel 20,6 gegen 16,4 cm), und in den Vergleichsbildern war der Render im Mittel 1,24–1,64-mal so breit wie die Vorlage
    #: (`hose/ansicht_breiten.py`); der Körperregler `MassThighs −0,8` brachte davon nur 4 %.
    ABSTAND = ((0.0, 0.020), (0.30, 0.010), (0.55, 0.008), (0.85, 0.012), (1.0, 0.012))
    ABSTAND_HUEFTE = ((0.0, 0.012), (0.15, 0.012), (1.0, 0.010))          # über dem Schritt: (m über Schritt bis Bund als Anteil, Abstand)
    #: Enge Hose (Unterhose, Radlerhose; 05.10.2026, Edgar: „Unterhose ist viel zu weit, in der Vorlage ist sie eng anliegend", danach „total aufgebläht, sie muss am Körper liegen"): ohne Falten, kaum geglättet
    #: (`GLAETTEN_ENG`: nur das Rauschen des Netzes, nicht die Rundung des Gesäßes und den Schritt), `ABSTAND_ENG` über der Haut, nie unter `MINDEST_ENG`. Mit 8 mm und 60/900 Glättungsschritten war die Hose am Stand von
    #: `stand_e9105675fcae.glb` (gemessen 05.10.2026, `ProjektTemp/_wegwerf/sapiens/hose_anliegen.py`) je Seite 9,5–11,1 mm breiter und am Gesäß 9–14 mm tiefer als der Körper, im Schritt bis 39 mm abgehoben.
    #: Die Werte 4 mm / 3 mm sind Augenmaß (nicht gegen die Vorlage gemessen); ob die Haut bei 3 mm durchscheint, zeigt erst die Bühne.
    ABSTAND_ENG, MINDEST_ENG = 0.004, 0.003
    GLAETTEN_ENG, GLAETTEN_SCHRITT_ENG = 6, 200
    MINDEST = 0.007           # nie näher am Körper (m)
    GLAETTEN, GLAETTEN_SCHRITT = 60, 900     # Schritte Taubin überall / im vorderen Schrittbereich (22/90 ließen die Muskeln und die Wölbung vorn stehen, 60/260 die Wölbung noch sichtbar)
    SCHRITT_BREITE = 0.14                    # halbe Breite des Bereichs vorn im Schritt (m), in dem stark geglättet wird
    WEISS = (240.0, 236.0, 228.0)
    BUND_UNTER_HOSE = 0.035   # der Bund liegt so weit unter dem oberen Rand der GC-Hose (die ragte als Beutel über den Gürtel)

    def __init__(self, punkte, dreiecke):
        self.p = Torchfeld.feld(punkte, dtype=torch.float64)
        d = Torchfeld.feld(dreiecke, dtype=torch.int64).reshape(-1, 3)
        # UV-Nähte verdoppeln die Punkte: ohne Verschweißen nach Lage zerfällt der Körper in Inseln (Beine, Rumpf), und Glätten und Zusammenhang arbeiten an jeder Naht gegeneinander
        _schluessel, erste, inv = Torchfeld.unique(Torchfeld.astype(Torchfeld.round(self.p * 1e5), torch.int64), axis=0, return_index=True, return_inverse=True)
        d = inv.reshape(-1)[d]
        self.d = d[(d[:, 0] != d[:, 1]) & (d[:, 1] != d[:, 2]) & (d[:, 0] != d[:, 2])]
        self.pw = self.p[erste]                      # verschweißte Punkte; `erste[i]`: ein Originalpunkt dazu (Haut und UV sind an beiden Seiten einer Naht gleich)
        self.erste = erste

    # ------------------------------------------------------------ Netz

    def _auswahl(self, ymin, ymax):
        """(Punkte, Dreiecke, quelle) — Körperdreiecke im Höhenband, größte zusammenhängende Fläche."""
        from KoerperKI_alle.kartenduenn import Kartenduenn as sparse
        from KoerperKI_alle.kartengraph import connected_components
        mitte = self.pw[self.d].mean(axis=1)
        wahl = (mitte[:, 1] >= ymin - self.RAND) & (mitte[:, 1] <= ymax + self.RAND) & (Torchfeld.abs(mitte[:, 0]) <= self.BREITE_X)
        d = self.d[wahl]
        nummern, neu = Torchfeld.unique(d.ravel(), return_inverse=True)
        d = neu.reshape(-1, 3)
        n = len(nummern)
        kanten = Torchfeld.vstack([d[:, [0, 1]], d[:, [1, 2]]])
        _zahl, teil = connected_components(sparse.coo_matrix((torch.ones(len(kanten), dtype=torch.float64, device='cuda'), (kanten[:, 0], kanten[:, 1])), shape=(n, n)), directed=False)
        groesster = Torchfeld.argmax(Torchfeld.bincount(teil[d[:, 0]]))
        d = d[teil[d[:, 0]] == groesster]
        nummern2, neu2 = Torchfeld.unique(d.ravel(), return_inverse=True)
        gewaehlt = nummern[nummern2]
        return Torchfeld.kopie(self.pw[gewaehlt]), neu2.reshape(-1, 3), self.erste[gewaehlt]

    @staticmethod
    def _nachbarn(d, n):
        from KoerperKI_alle.kartenduenn import Kartenduenn as sparse
        kanten = Torchfeld.vstack([d[:, [0, 1]], d[:, [1, 2]], d[:, [2, 0]]])
        kanten = Torchfeld.vstack([kanten, Torchfeld.umgekehrt(kanten, 1)])
        a = sparse.coo_matrix((torch.ones(len(kanten), dtype=torch.float64, device='cuda'), (kanten[:, 0], kanten[:, 1])), shape=(n, n)).tocsr()
        a.data[:] = 1.0
        grad = Torchfeld.feld(a.sum(axis=1)).ravel()
        return sparse.diags(1.0 / Torchfeld.maximum(grad, 1.0)) @ a

    @staticmethod
    def _rand(d, n):
        """Boolesche Reihe: Punkt auf einer Randkante (Bund, Saum)."""
        k = torch.sort(Torchfeld.vstack([d[:, [0, 1]], d[:, [1, 2]], d[:, [2, 0]]]), dim=1, stable=True).values
        eindeutig, zahl = Torchfeld.unique(k, axis=0, return_counts=True)
        r = torch.zeros(n, dtype=torch.bool, device='cuda')
        r[eindeutig[zahl == 1].ravel()] = True
        return r

    @staticmethod
    def _normalen(p, d):
        f = Torchfeld.cross(p[d[:, 1]] - p[d[:, 0]], p[d[:, 2]] - p[d[:, 0]])
        n = torch.zeros_like(p)
        for k in range(3):
            Torchfeld.add_at(n, d[:, k], f)
        return n / Torchfeld.maximum(Torchfeld.linalg_norm(n, dim=1, keepdim=True), 1e-12)

    @classmethod
    def _glaetten(cls, p, matrix, gewicht, schritte, lam=0.5, mu=-0.53):
        for _ in range(schritte):
            p = p + lam * gewicht[:, None] * (matrix @ p - p)
            p = p + mu * gewicht[:, None] * (matrix @ p - p)
        return p

    @staticmethod
    def _weich(x):
        x = Torchfeld.clip(x, 0.0, 1.0)
        return x * x * (3.0 - 2.0 * x)

    def _ausserhalb(self, p, matrix, glatt=8, runden=4, mindest=None):
        """Jeden Hosenpunkt mindestens `MINDEST` AUSSERHALB der Körperfläche halten (04.10.2026, Edgar: „riesen Geschlechtsteil", graue Flecken auf der Hose).

        Gemessen (`hose/durchstoss.py`, Stand Runde 60 und 62): 8,2 % der Körperpunkte im Beinband lagen außerhalb der Hose, bis 43 mm weit, fast alle im Schritt und
        Unterbauch — die Hose wird dort stark geglättet und blieb unter der Körperform stehen; der Körper mit seiner aus den Fotos projizierten Haut (darauf die weißen
        Hosen der Vorlagen, grau mit Falten) drückte durch. Die frühere Prüfung (Abstand zum nächsten Körperpunkt ≥ `MINDEST`) bemerkt das nicht: Ein Punkt tief IM Körper
        hat zu jedem Körperpunkt Abstand. Hier zählt die Lage zur Fläche: Ist `(p − nächster Körperpunkt) · Körpernormale` kleiner als `MINDEST`, wird der Punkt entlang der
        Normale herausgeschoben. Das Schiebemaß wird zuerst über die Hose geglättet (`glatt` Schritte), damit keine Zacken entstehen; in der letzten Runde hart, damit es hält.
        """
        from KoerperKI_alle.kartenbaum import Kartenbaum as cKDTree
        mindest = self.MINDEST if mindest is None else mindest
        if getattr(self, '_kn', None) is None:
            kn = self._normalen(self.pw, self.d)
            mitte = self.pw.mean(axis=0)
            if ((self.pw - mitte) * kn).sum() < 0.0:          # Windung der Körperdreiecke: Normalen müssen nach außen zeigen
                kn = -kn
            self._kn, self._baum = kn, cKDTree(self.pw)
        for runde in range(runden):
            _dist, j = self._baum.query(p)
            t = ((p - self.pw[j]) * self._kn[j]).sum(axis=1)
            fehl = Torchfeld.maximum(mindest - t, 0.0)
            if not (fehl > 1e-5).any():
                break
            schub = self._kn[j] * fehl[:, None]
            if glatt and runde < runden - 1:
                schub = self._glaetten(schub, matrix, torch.ones(len(p), dtype=torch.float64, device='cuda'), glatt)
            p = p + schub
        return p

    # ------------------------------------------------------------ Hose

    def bauen(self, ymin, ymax, eng=False):
        """`eng`: eine eng anliegende Hose (`ABSTAND_ENG`, keine Falten) statt der lockeren mit Saum und Drapierung."""
        from .hosenfalten import Hosenfalten
        p0, d, quelle = self._auswahl(ymin, ymax)
        n = len(p0)
        p0[:, 1] = Torchfeld.clip(p0[:, 1], ymin, ymax)
        rand = self._rand(d, n)
        matrix = self._nachbarn(d, n)
        mitte = p0[Torchfeld.abs(p0[:, 0]) < 0.015]
        yc = float(mitte[:, 1].min()) if len(mitte) else ymin + 0.78 * (ymax - ymin)       # Schritt: tiefster Punkt der Mittelebene
        beine = max(yc - ymin, 0.3)
        # 1. Glätten: überall leicht, vorn im Schritt stark (Körperrelief soll nicht im Stoff stehen)
        glatt, glatt_schritt = (self.GLAETTEN_ENG, self.GLAETTEN_SCHRITT_ENG) if eng else (self.GLAETTEN, self.GLAETTEN_SCHRITT)
        mindest = self.MINDEST_ENG if eng else self.MINDEST
        gewicht = torch.where(rand, 0.0, 1.0)
        p = self._glaetten(p0, matrix, gewicht, glatt)
        vorn = (Torchfeld.abs(p0[:, 0]) < self.SCHRITT_BREITE) & (p0[:, 1] > yc - 0.06) & (p0[:, 1] < yc + 0.18) & (p0[:, 2] > p0[:, 2].mean())
        stark = torch.where(rand, 0.0, 1.0) * self._weich(2.0 * (1.0 - Torchfeld.abs(p0[:, 0]) / self.SCHRITT_BREITE)) * vorn
        p = self._glaetten(p, matrix, stark, glatt_schritt)
        # 2. Abstand zur Haut nach Höhe, entlang der Normalen der geglätteten Fläche
        s = (p[:, 1] - ymin) / beine
        unten = Torchfeld.interp(s, [a for a, _ in self.ABSTAND], [c for _, c in self.ABSTAND])
        ueber = Torchfeld.interp((p[:, 1] - yc) / max(ymax - yc, 0.05), [a for a, _ in self.ABSTAND_HUEFTE], [c for _, c in self.ABSTAND_HUEFTE])
        abstand = torch.where(p[:, 1] < yc, unten, ueber)
        if eng:
            abstand = Torchfeld.full(len(p), self.ABSTAND_ENG)
        nach = self._normalen(p, d)
        aus = torch.zeros_like(p)                                    # von der Beinachse (Mitte je Seite) weg
        for seite in (p[:, 0] >= 0.0, p[:, 0] < 0.0):
            aus[seite, 0] = p[seite, 0] - p[seite, 0].mean()
            aus[seite, 2] = p[seite, 2] - p[seite, 2].mean()
        drehen = (nach * aus).sum() < 0.0                         # Die Windung der Dreiecke legt fest, wohin die Normalen zeigen: dann alle umdrehen
        if drehen:
            nach = -nach
        p = p + nach * abstand[:, None]
        p = self._ausserhalb(p, matrix, mindest=mindest)
        # 3. Drapierung
        if not eng:
            p = Hosenfalten.anwenden(p, d)
        p[:, 1] = Torchfeld.clip(p[:, 1], ymin, ymax)
        p = self._ausserhalb(p, matrix, glatt=0, mindest=mindest)          # die Falten dürfen nicht wieder in den Körper schneiden
        normalen = self._normalen(p, d) * (-1.0 if drehen else 1.0)      # vor dem Verdoppeln der Eckpunkte: an der Rückseite des Rings keine Schattennaht
        uv, d, herkunft = self._uv(p, d, ymin, ymax)
        return {'punkte': p[herkunft], 'dreiecke': d, 'uv': uv, 'quelle': quelle[herkunft], 'normalen': normalen[herkunft], 'ymin': ymin, 'ymax': ymax,
                'ring_y': self.ring_y, 'ring_r': self.ring_r}

    # ------------------------------------------------------------ UV

    def _ringmitte(self, p):
        """(seite, cx, cz, r) je Punkt: Mitte und Radius des Beinrings als Mittel über ein Höhenfenster (`FENSTER`) derselben Seite — glatt über die Höhe (ein Band je Zentimeter
        erwischte je nach Netzreihe nur einen Teil des Rings: die Mitte sprang um Zentimeter, die Streifenlinie lief im Zickzack)."""
        seite = torch.where(p[:, 0] >= 0.0, 1.0, -1.0)
        cx, cz, r = torch.zeros(len(p), dtype=torch.float64, device='cuda'), torch.zeros(len(p), dtype=torch.float64, device='cuda'), torch.zeros(len(p), dtype=torch.float64, device='cuda')
        for sg in (1.0, -1.0):
            idx = torch.flatten(seite == sg).nonzero()[:, 0]
            if len(idx) < 10:
                continue
            o = idx[torch.argsort(p[idx, 1], stable=True)]
            y = p[o, 1]
            lo, hi = Torchfeld.searchsorted(y, y - self.FENSTER), Torchfeld.searchsorted(y, y + self.FENSTER, side='right')

            def mittel(werte):
                c = Torchfeld.cat([[0.0], Torchfeld.cumsum(werte)])
                return (c[hi] - c[lo]) / (hi - lo)

            mx, mz = mittel(p[o, 0]), mittel(p[o, 2])
            cx[o], cz[o], r[o] = mx, mz, mittel(Torchfeld.hypot(p[o, 0] - mx, p[o, 2] - mz))
        return seite, cx, cz, r

    def _uv(self, p, d, ymin, ymax):
        """(uv, dreiecke, herkunft) — zylindrische UV je Bein; Dreiecke über die Rückseite des Rings (U 0/1) bekommen eigene Eckpunkte mit U + 1.
        `herkunft[i]` ist der Punkt, von dem Eckpunkt i abstammt (für Lage, Normale, Haut)."""
        seite, cx, cz, r = self._ringmitte(p)
        winkel = torch.where(r > 0.0, Torchfeld.arctan2(p[:, 2] - cz, seite * (p[:, 0] - cx)), math.pi)
        band = Torchfeld.astype(Torchfeld.floor((p[:, 1] - ymin) / self.BAND), torch.int64)
        ys = Torchfeld.arange(band.max() + 1) * self.BAND + ymin + 0.5 * self.BAND
        radius = Torchfeld.feld([r[(band == b) & (r > 0.0)].mean() if ((band == b) & (r > 0.0)).any() else math.nan for b in range(band.max() + 1)], copy=True)
        gut = ~Torchfeld.isnan(radius)
        self.ring_y, self.ring_r = ys[gut], radius[gut]
        u = winkel / (2.0 * math.pi) + 0.5
        v = (p[:, 1] - ymin) / max(ymax - ymin, 1e-6)
        ecken_u = u[d]
        ueber = (Torchfeld.amax(ecken_u, dim=1) - Torchfeld.amin(ecken_u, dim=1)) > 0.5
        herkunft, neu_u, neu_v = [Torchfeld.arange(len(p))], [u], [v]
        d = Torchfeld.kopie(d)
        n = len(p)
        for k in range(3):
            zeile = torch.flatten(ueber & (ecken_u[:, k] < 0.5)).nonzero()[:, 0]
            eindeutig, rueck = Torchfeld.unique(d[zeile, k], return_inverse=True)
            d[zeile, k] = n + rueck
            herkunft.append(eindeutig)
            neu_u.append(u[eindeutig] + 1.0)
            neu_v.append(v[eindeutig])
            n += len(eindeutig)
        return Torchfeld.column_stack([Torchfeld.cat(neu_u), Torchfeld.cat(neu_v)]), d, Torchfeld.cat(herkunft)

    @classmethod
    def textur(cls, gebaut, breite=512, hoehe=1024, farbe=None):
        """Das Bild der Hose: weißer Stoff mit dem Seitenstreifen an der Außennaht (U = 0,5) — mit `farbe` (RGB 0–255) ein einfarbiger Stoff ohne Streifen."""
        from PIL import Image
        if farbe is not None:
            return Image.new('RGB', (16, 16), tuple(int(c) for c in farbe[:3]))

        from .hosenstreifen import Hosenstreifen
        ymin, ymax = gebaut['ymin'], gebaut['ymax']
        y = ymin + (1.0 - (Torchfeld.arange(hoehe) + 0.5) / hoehe) * (ymax - ymin)             # Zeile 0 = oben
        r = Torchfeld.interp(y, gebaut['ring_y'], gebaut['ring_r'])
        u = ((Torchfeld.arange(breite) + 0.5) / breite - 0.5)[None, :] * 2.0 * math.pi * r[:, None]
        farbe, deckung = Hosenstreifen.muster(u, Torchfeld.broadcast_to(y[:, None], u.shape), ymax, ymin)
        grund = Torchfeld.feld(cls.WEISS)[None, None, :] * 0.98
        aus = grund * (1.0 - deckung[..., None]) + farbe * deckung[..., None]
        return Image.fromarray(Torchfeld.roh(Torchfeld.astype(Torchfeld.clip(Torchfeld.round(aus), 0, 255), torch.uint8)), 'RGB')

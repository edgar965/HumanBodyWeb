# -*- coding: utf-8 -*-
"""Dazgeograftanpassung — das Daz-Geograft auf die vorgegebene Scham eines Blender-Imports anpassen (10.10.2026).

Edgar: „im Blender-File war die Scham ja vorgegeben, die sollst du mit Hilfe der Scham aus Genesis nachbauen". Gemessen am cute girl: die Figur des Imports liegt
in einem anderen Raum als die Grundfigur (1,749 gegen 1,701 m, Scham 0,853–0,929 gegen 0,800–0,875 m), das Original steht bis 28 mm vor ihrer Haut (`Dazgeograftziel`).
Vier Schritte, jeder mit Zahlen im Bericht:

    verlegen      die Punkte des Geografts folgen der Verschiebung der Haut von der Grundfigur zur Figur des Imports (die 6 nächsten Hautpunkte, Gewicht 1/d²)
    ausrichten    die Erhebungen (mehr als `ANBAU_M` über der Haut) beider Formen werden in der Ebene der Haut aufeinandergelegt: Verschiebung und Maßstab je Achse (ICP,
                  nach der Höhe gewichtet), zum Ring des Lochs hin ausgeblendet — die Scham des Originals sitzt nicht an der Stelle von Dazs
    anpassen      jeder Punkt geht entlang der Hautnormalen auf die nächste Fläche des Originals (höchstens `SUCHE_M` weit), sonst auf die Haut der Figur
    glätten       die Verschiebungen werden über die Nachbarn gemittelt (Rauschen der Strahlen), der Rand bleibt
Die Topologie bleibt die des Geografts (Dreiecke, UV), nur die Lage ändert sich — Regler, Loch und Naht laufen danach wie beim unveränderten Stück.
"""
import numpy as np

__all__ = ['Dazgeograftanpassung']


class Dazgeograftanpassung:
    #: Höhe über der Haut (m), ab der ein Punkt zur Erhebung (Hügel, Lippen) gehört.
    ANBAU_M = 0.004
    #: Strahl: ein Treffer gilt höchstens so weit (m) vor oder hinter dem Punkt.
    SUCHE_M = 0.03
    #: Abstand vom Ring (m), ab dem die Ausrichtung voll wirkt, und ab dem die Anpassung voll wirkt.
    RING_AUS_M, RING_AN_M = 0.02, 0.004
    #: Grenzen des Maßstabs der Ausrichtung je Achse.
    MASSSTAB = (0.6, 1.5)
    #: Steifigkeit `a` der Anpassung (Gewicht des Laplace gegen die Treffer; Punktabstand des Geografts ≈ 4 mm), Gewicht der Randpunkte und Zahl der Durchgänge.
    STEIFIGKEIT, RAND_GEWICHT, DURCHGAENGE = 3.0, 100.0, 3
    #: Gewicht `μ` der Glättung der Verlege-Verschiebung: gelöst wird `(I + μ·L) D = D_roh` (gemessen, siehe `verlegen`: 5 → 2,8 % knickende Kanten, 200 → 2,2 %, 1000 → 2,4 %).
    GLAETTUNG = 200.0
    #: Randband: Punkte, die höchstens so weit (m) vom Ring liegen, bleiben mit diesem Gewicht nahe ihrer verlegten (geglätteten) Lage. 0 = aus.
    #: Anlass (gemessen 10.10.2026, `Schammessung`): 9 von 100 Randpunkten hatten Normalen gegen die der Haut (bis 140°), dazu 4 am Seitenrand um 50° gekippt — der Rand knickte weg.
    BAND_M, BAND_GEWICHT = 0.006, 3.0
    #: Gemessen und verworfen (10.10.2026, `Schammessung`, Knicke im Band 12 mm am Rand: über 60° 2,3 %, über 90° 1,9 %): Laplace-Glättung der Punkte nahe am Ring nach der Anpassung
    #: (8–20 mm × 10–60 Schritte: Knicke 1,5–3,9 % über 90°, Randnormalen p90 28 → 42–57°) und stärkeres Glätten der Ringlinie (`Blendimportschamring.MAX_MM` 8–16 mm: Knicke über 90° 3,5–3,7 %).
    #: Feineres Netz (`stufe` 2: Punktabstand ≈ 2 mm, Frau 16.780 statt 4.280 Punkte, Dreiecke ×4): Steifigkeit und Glättung ×0,5 je Stufe, Umklapp-Toleranz ×4 (die Zahl der Dreiecke, die schon
    #: vor dem Anpassen umgeklappt sind, wächst mit ihr: 840 gegen 5.000). Gemessen 11.10.2026 mit `Schammessung` an „cute girl" (Probebau ohne Schreiben, `ProjektTemp/_wegwerf/stufe_reihe.sh`),
    #: Form Original → Modell Median / p90 | Lippen seitlich Median | Knick über die Naht größter / Kanten über 60°:
    #:   Stufe 1, Vorgaben            0,63 / 2,19 mm | 1,67 mm | 56,6° / 0
    #:   Stufe 2, Vorgaben            0,49 / 2,13    | 1,57    | 52,0° / 0     die Durchgänge liefen nur mit Schritt 0,5 und 0,25 (Toleranz 100 zu klein)
    #:   Stufe 2, Toleranz 400        0,41 / 1,83    | 1,00    | 53,4° / 0
    #:   Stufe 2, Steifigkeit ×4 / ×2 0,67 / 2,46 und 0,53 / 2,02 — zu steif, schlechter als Toleranz allein
    #:   Stufe 2, ×0,5 (gewählt)      0,32 / 1,73    | 0,83    | 49,2° / 0     ×0,25: 0,27 / 1,86, aber Fläche über 90° 1,4 % (Original 1,1 %) — knittert
    #: Die Regler am Basis-Stück (Stufe 1) kommen auch von einem Stück auf Stufe 2: `Dazgeograftmorphbasis` ordnet über die Rohnummern der Unterteilung zu (`Dazgeograftstufenzuordnung`).
    STUFE_STEIF, STUFE_TOLERANZ = 0.5, 4.0
    #: Breite der festgehaltenen Ringreihen: `RING_AN_M` und `BAND_M` sind in Metern gesetzt, bei Stufe 1 (4 mm Punktabstand) halten sie die Ringreihe und eine weitere, bei Stufe 2 (2 mm) zwei bis drei Reihen.
    #: Gemessen 11.10.2026 (`ProjektTemp/_wegwerf/stufe2_ring.py`, Probebau ohne Schreiben, Höhe des Stücks über der Hautebene an den 10 Ringpunkten mit tiefer Wand im Original, bei 1/2/3/5/8 mm nach innen):
    #:   Stufe 1                     -0,1 / -11,7 / -12,4 / -13,1 / -13,6 mm   (die Wand beginnt bei 1–2 mm)
    #:   Stufe 2, 4 / 6 mm (alt)      0,1 /   0,8 /   1,2 / -13,3 / -13,7       ein Absatz von 3–5 mm auf Hautniveau, dann die Wand; Kanten im Band 12 mm über 60° 8,7 %, über 90° 5,0 % (Stufe 1: 3,7 / 1,3 %)
    #:   Stufe 2, 2 / 3 mm           -0,1 / -13,1 / -13,5 / -13,7 / -14,0       Wand wie bei Stufe 1; Band über 60° 4,1 %, über 90° 2,3 %; Form 0,31 / 1,85 mm (alt 0,32 / 1,73); Knick über die Naht größter 65,3° (alt 49,2°)
    #: ABER (`Schammessungansichten`, 11.10.2026, `ProjektTemp/_wegwerf/ansichten_probe.py`): der Absatz 2 mm hinter dem Ring (Höhe über der Hautebene) ist mit 2 / 3 mm HÖHER, nicht niedriger — p90 5,8 / größter 14,5 mm,
    #: 14 Ringpunkte über 3 mm und 5 über 10 mm (4 / 6 mm: 2,7 / 10,1 mm, 8 und 2; Stufe 1: 5,2 / 13,5 mm, 13 und 4) —, und das Stück trägt seitlich nur 49 % der Erhebung des Originals (4 / 6 mm: 57 %). Die Wand
    #: von 10–15 mm liegt im Original selbst (seitlich am Ring steht die Haut 10–15 mm über ihm); der Faktor schiebt sie nur an den Ring. Verworfen: `STUFE_RING` = 1 (keine Skalierung); der Mechanismus bleibt für Proben.
    STUFE_RING = 1.0

    def __init__(self, figur0, figur, ring_punkte, ziel, stufe=1):
        """`figur0`, `figur`: `{punkte, dreiecke}` der Grundfigur und der Figur des Imports (Stufe 1, gleiche Topologie); `ring_punkte`: Nummern der Hautpunkte auf dem Ring des
        Lochs (in beiden Figuren dieselben); `ziel`: `Dazgeograftziel`; `stufe`: Unterteilungsstufe des Geografts, das angepasst wird (1 = Punktabstand ≈ 4 mm, 2 = ≈ 2 mm)."""
        import trimesh
        from scipy.spatial import cKDTree

        self.stufe = int(stufe)
        #: Faktor auf Steifigkeit und Glättung und auf die Umklapp-Toleranz (1 bei Stufe 1).
        self.steif_faktor, self.toleranz_faktor = self.STUFE_STEIF ** (self.stufe - 1), self.STUFE_TOLERANZ ** (self.stufe - 1)
        #: Faktor auf `RING_AN_M` und `BAND_M` (1 bei Stufe 1).
        self.ring_faktor = self.STUFE_RING ** (self.stufe - 1)
        self.p0 = np.asarray(figur0['punkte'], dtype=np.float64)
        self.p1 = np.asarray(figur['punkte'], dtype=np.float64)
        self.haut = trimesh.Trimesh(self.p1, np.asarray(figur['dreiecke'], dtype=np.int64), process=False)
        self.normalen = np.asarray(self.haut.vertex_normals, dtype=np.float64)
        self.baum0, self.baum1 = cKDTree(self.p0), cKDTree(self.p1)
        self.ring = self.p1[np.asarray(ring_punkte, dtype=np.int64)]
        self.ring_baum = cKDTree(self.ring)
        self.ziel = ziel
        self.ziel_netz = trimesh.Trimesh(ziel.punkte, ziel.dreiecke, process=False)
        f = self.normalen[np.asarray(ring_punkte, dtype=np.int64)].mean(axis=0)
        self.vorne = f / np.linalg.norm(f)
        e1 = np.cross([0.0, 1.0, 0.0], self.vorne)
        self.e1 = e1 / np.linalg.norm(e1)
        self.e2 = np.cross(self.vorne, self.e1)
        self.bericht = {}

    # ------------------------------------------------------------ Hilfen

    @staticmethod
    def _hermite(t):
        t = np.clip(t, 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)

    def hoehe(self, punkte):
        """Höhe über der Haut der Figur (m, plus = außen): Abstand zum nächsten Hautpunkt längs dessen Normale."""
        _d, i = self.baum1.query(punkte)
        return np.einsum('ij,ij->i', punkte - self.p1[i], self.normalen[i])

    def ringabstand(self, punkte):
        return self.ring_baum.query(punkte)[0]

    # ------------------------------------------------------------ Schritte

    def verlegen(self, punkte, dreiecke=None):
        """Die Punkte (Raum der Grundfigur) in den Raum der Figur des Imports. Mit `dreiecke` wird die Verschiebung über das Netz geglättet (`GLÄTTUNG`): die rohe Verschiebung (6 nächste
        Hautpunkte) ist so rau wie die Nachformung der Haut, und das knickte die Fläche — gemessen 10.10.2026 mit `Schammessung` an „cute girl" (Nachformung 1): Kanten über 90° beim
        rohen Geograft 1,7 %, nach rohem Verlegen 7,2 %, nach der Anpassung 10,3 % (Original 0,8 %); mit Glättung 200 nach der Anpassung 2,2 % und die Form besser (Original → Modell
        Median 0,95 → 0,68 mm, p90 4,98 → 2,70 mm). Glättung 1000 / 5000: Form 0,81 / 0,80 mm, also schlechter."""
        d, i = self.baum0.query(punkte, k=6)
        w = 1.0 / (d * d + 1e-8)
        w /= w.sum(axis=1, keepdims=True)
        verschiebung = np.einsum('nk,nkj->nj', w, (self.p1 - self.p0)[i])
        glaettung = self.GLAETTUNG * self.steif_faktor
        if dreiecke is not None and glaettung > 0:
            import scipy.sparse as sp
            import scipy.sparse.linalg as spl

            lhs = (sp.identity(len(punkte)) + glaettung * self._laplace(dreiecke, len(punkte))).tocsc()
            verschiebung = spl.splu(lhs).solve(verschiebung)
        self.bericht['verlegt_mm'] = {'median': round(float(np.median(np.linalg.norm(verschiebung, axis=1)) * 1000), 1),
                                      'max': round(float(np.linalg.norm(verschiebung, axis=1).max() * 1000), 1), 'glaettung': glaettung if dreiecke is not None else 0.0}
        return punkte + verschiebung

    def ausrichten(self, punkte):
        """Die Erhebungen aufeinanderlegen (Verschiebung und Maßstab je Achse der Hautebene) → neue Punkte. Ohne genug Erhebung bleibt alles stehen."""
        from scipy.spatial import cKDTree

        hg = self.hoehe(punkte)
        ht = self.hoehe(self.ziel.punkte)
        g, t = np.flatnonzero(hg > self.ANBAU_M), np.flatnonzero(ht > self.ANBAU_M)
        if len(g) < 30 or len(t) < 30:
            self.bericht['ausrichten'] = {'uebersprungen': 'zu wenig Erhebung (%d / %d Punkte)' % (len(g), len(t))}
            return punkte
        uv = np.column_stack([punkte @ self.e1, punkte @ self.e2])
        ziel_uv = np.column_stack([self.ziel.punkte[t] @ self.e1, self.ziel.punkte[t] @ self.e2])
        baum = cKDTree(ziel_uv)
        gew = hg[g]
        s, v = np.ones(2), np.zeros(2)
        for _ in range(40):
            bild = uv[g] * s + v
            _d, nach = baum.query(bild)
            for a in range(2):
                A = np.column_stack([uv[g, a], np.ones(len(g))]) * np.sqrt(gew)[:, None]
                loesung = np.linalg.lstsq(A, ziel_uv[nach, a] * np.sqrt(gew), rcond=None)[0]
                s[a], v[a] = np.clip(loesung[0], *self.MASSSTAB), loesung[1]
        abgebildet = uv * s + v
        w = self._hermite(self.ringabstand(punkte) / self.RING_AUS_M)
        d_uv = (abgebildet - uv) * w[:, None]
        self.bericht['ausrichten'] = {'massstab': [round(float(x), 3) for x in s], 'verschiebung_mm': [round(float(x) * 1000, 1) for x in v],
                                      'erhebung_punkte': [int(len(g)), int(len(t))],
                                      'rest_mm': round(float(np.median(baum.query(abgebildet[g])[0]) * 1000), 1)}
        return punkte + np.outer(d_uv[:, 0], self.e1) + np.outer(d_uv[:, 1], self.e2)

    def anpassen(self, punkte, dreiecke, steifigkeit=None, verfeinern=True, fest=True):
        """Das Netz auf das Original ziehen, ohne es zu zerknittern → neue Punkte. `fest`: die Ringreihen (und das Randband) bleiben bei ihrer verlegten Lage — richtig, wenn der Rand des Netzes auf
        dem Ring der Haut liegt (das Geograft mit seinem eigenen Loch). Ist das Netz am Umriss des Blender-Stücks zugeschnitten (`Dazgeograftumriss`), liegt sein Rand IM Geograft und nicht auf der Haut:
        `fest=False` lässt ihn dem Original folgen, die Haut holt `Blendimportscham.angleichen` danach heran.

        Je Punkt gibt es einen Treffer des Strahls längs der Hautnormalen auf dem Original (`_treffer`, höchstens `SUCHE_M` weit) — oder keinen. Gelöst wird die Verschiebung `D` des
        ganzen Netzes aus `(W + a·L) D = W (Treffer − Punkt)`: `W` = 1 an Punkten mit Treffer, `RAND_GEWICHT` auf dem Ring (dort bleibt die Haut), sonst 0; `L` der Graph-Laplace des
        Netzes. Ohne Treffer füllen die Nachbarn die Verschiebung weich auf; je größer `a` (Steifigkeit), desto mehr bleibt das Netz glatt. Die Treffer werden von der neuen Lage
        aus noch `DURCHGAENGE`-mal gesucht."""
        import scipy.sparse as sp
        import scipy.sparse.linalg as spl

        a = self.STEIFIGKEIT * self.steif_faktor if steifigkeit is None else float(steifigkeit)
        _d, i = self.baum1.query(punkte)
        n = self.normalen[i]
        keine = np.zeros(len(punkte), dtype=bool)
        rand = self.ringabstand(punkte) < self.RING_AN_M * self.ring_faktor if fest else keine
        band = (self.ringabstand(punkte) < self.BAND_M * self.ring_faktor) & ~rand if fest and self.BAND_GEWICHT > 0 else keine.copy()
        laplace = self._laplace(dreiecke, len(punkte))
        q, treffer_zahl = punkte, 0
        for _ in range(self.DURCHGAENGE):
            ziel = self._treffer(q, n)
            hat = ~np.isnan(ziel[:, 0])
            w = hat.astype(np.float64)
            ziel[~hat] = punkte[~hat]
            w[rand], ziel[rand] = self.RAND_GEWICHT, punkte[rand]
            if band.any():
                alt = w[band].copy()
                w[band] = alt + self.BAND_GEWICHT
                ziel[band] = (alt[:, None] * ziel[band] + self.BAND_GEWICHT * punkte[band]) / w[band][:, None]
            lhs = (sp.diags(w) + a * laplace + 1e-9 * sp.identity(len(punkte))).tocsc()
            loesung = spl.splu(lhs).solve(w[:, None] * (ziel - punkte))
            q, treffer_zahl = punkte + loesung, int((hat & ~rand).sum())
        if verfeinern:
            from .dazgeograftverfeinerung import Dazgeograftverfeinerung

            plan = tuple((s * self.steif_faktor, r) for s, r in Dazgeograftverfeinerung.PLAN)
            toleranz = int(round(Dazgeograftverfeinerung.UMKLAPP_TOLERANZ * self.toleranz_faktor))
            q, self.bericht['verfeinern'] = Dazgeograftverfeinerung.verfeinern(punkte, q, dreiecke, rand, laplace, self.ziel_netz, n, plan=plan, band=band, band_gewicht=self.BAND_GEWICHT,
                                                                               toleranz=toleranz)
        betrag = np.linalg.norm(q - punkte, axis=1)
        self.bericht['anpassen'] = {'steifigkeit': a, 'treffer_original': treffer_zahl, 'ohne_treffer': int(len(punkte) - treffer_zahl),
                                    'verschiebung_mm': {'median': round(float(np.median(betrag) * 1000), 1), 'max': round(float(betrag.max() * 1000), 1)}}
        return q

    def _treffer(self, punkte, n):
        """`(P, 3)`: der Treffer des Strahls durch jeden Punkt längs `n` auf dem Original, der dem Punkt am nächsten liegt — NaN ohne Treffer in `SUCHE_M`."""
        aus = np.full(punkte.shape, np.nan)
        orte, strahl, _tri = self.ziel_netz.ray.intersects_location(punkte - self.SUCHE_M * n, n, multiple_hits=True)
        if not len(orte):
            return aus
        abstand = np.linalg.norm(orte - punkte[strahl], axis=1)
        for r in np.unique(strahl):
            alle = np.flatnonzero(strahl == r)
            beste = alle[np.argmin(abstand[alle])]
            if abstand[beste] <= self.SUCHE_M:
                aus[r] = orte[beste]
        return aus

    @staticmethod
    def _laplace(dreiecke, n):
        """Der Graph-Laplace `L = Grad − Nachbarschaft` des Netzes (dünn besetzt, jede Kante einmal)."""
        import scipy.sparse as sp

        kanten = np.concatenate([dreiecke[:, [0, 1]], dreiecke[:, [1, 2]], dreiecke[:, [2, 0]]])
        nachbar = sp.coo_matrix((np.ones(len(kanten)), (kanten[:, 0], kanten[:, 1])), shape=(n, n)).tocsr()
        nachbar = ((nachbar + nachbar.T) > 0).astype(np.float64)
        return sp.diags(np.asarray(nachbar.sum(axis=1)).ravel()) - nachbar

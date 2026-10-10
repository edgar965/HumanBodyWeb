# -*- coding: utf-8 -*-
"""Schammessunggeometrie — die Form des Scham-Stücks gegen die Vorgabe, an festen Stellen gemessen (10.10.2026).

Edgar: „wir haben ja die Geometrie an verschiedenen Punkten gemessen … mach das auch bei dem Importprozess". Vier Maße, alle in mm:

    original_zu_modell   jeder Punkt der Vorgabe (Original-Scham) → nächster Punkt des MODELLS (sichtbare Haut der Figur + Stück), je Zone: so weit müsste die Fläche des Modells
                         verschoben werden (Maß von `scham_vergleich.py`, 09.10.2026). Sieht auch das Innere (Spalt, innere Lippen)
    stueck_zu_original   jeder Punkt des Stücks → nächster Punkt des Originals (bei einer Teil-Vorgabe samt Haut der Figur): wo steht das Stück dort, wo das Original nichts hat?
    tiefenkarte          Strahlen von vorn (`-vorne`) im Raster `RASTER_M` auf Original und Modell: Tiefe der ersten Fläche; Unterschied je Zone (Mitte/seitlich, Drittel), dazu der
                         Mittelschnitt (`profil_mitte`) und drei Querprofile (`profil_quer`). Sieht nur die Außenfläche — dort, wo das Auge hinsieht
    symmetrie            Punkte des Stücks an der Mittelebene gespiegelt → Abstand zur Fläche des Stücks (Kern `KERN_M`, ohne `RAND_ABSTAND_M` am Rand), daneben dasselbe für das Original
                         (`symmetrie.py`, 09.10.2026: das Original ist symmetrisch, Median 0,34 mm)
"""
import numpy as np

__all__ = ['Schammessunggeometrie']


class Schammessunggeometrie:
    #: Abstand der Strahlen der Tiefenkarte (m).
    RASTER_M = 0.004
    #: Mehr Vorgabepunkte als das werden gleichmäßig zufällig (fester Samen) auf so viele ausgedünnt.
    PROBEN = 20000
    #: Kern der Symmetrie (|quer|, m) und Mindestabstand zum Rand (m).
    KERN_M, RAND_ABSTAND_M = 0.022, 0.006
    #: Die Vorgabe zählt bis so weit (m) über die Ausdehnung des Stücks hinaus (quer, längs) und so tief (m) vor und hinter ihm.
    UEBERSTAND_M, TIEFE_M = 0.003, 0.015
    #: Querprofile: Orte quer (m) in den Mitten der drei Drittel.
    PROFIL_QUER_M = (-0.024, -0.016, -0.008, 0.0, 0.008, 0.016, 0.024)

    def __init__(self, rahmen, stueck, modell, vorgabe, original, rand):
        """`stueck`, `modell`, `vorgabe`, `original`: `trimesh.Trimesh` (Modell = sichtbare Haut + Stück; `original` = Vorgabe, bei einer Teil-Vorgabe samt Haut der Figur); `rand`: `(R, 3)`
        Randpunkte des Stücks."""
        self.rahmen, self.stueck, self.modell, self.vorgabe, self.original = rahmen, stueck, modell, vorgabe, original
        self.rand = np.asarray(rand, dtype=np.float64).reshape(-1, 3)
        #: `(V,)` Abstand (mm) jedes Stückpunkts zum Original — für die Textur-Messung (nah am Original oder nicht).
        self.abstand_stueck = None

    def messen(self):
        aus = {}
        if self.vorgabe is not None and len(self.vorgabe.vertices):
            region = self._region()
            if len(region):
                aus['original_zu_modell'] = self._original_zu_modell(region)
                aus['stueck_zu_original'] = self._stueck_zu_original()
                aus['tiefenkarte'] = self._tiefenkarte()
            else:
                aus['hinweis'] = 'die Vorgabe liegt nicht im Bereich des Stücks'
        aus['symmetrie'] = self._symmetrie()
        return aus

    # ------------------------------------------------------------ Hilfen

    def _region(self):
        """Nummern der Vorgabepunkte im Kasten um das Stück (quer, längs, vorne)."""
        k = self.rahmen.koordinaten(self.vorgabe.vertices)
        g = self.rahmen.grenzen
        zu = (self.UEBERSTAND_M, self.UEBERSTAND_M, self.TIEFE_M)
        innen = np.ones(len(k), dtype=bool)
        for a in range(3):
            innen &= (k[:, a] >= g[a][0] - zu[a]) & (k[:, a] <= g[a][1] + zu[a])
        nummern = np.flatnonzero(innen)
        if len(nummern) > self.PROBEN:
            nummern = np.sort(np.random.default_rng(7).choice(nummern, self.PROBEN, replace=False))
        return nummern

    @staticmethod
    def _abstand_mm(netz, punkte):
        import trimesh

        return trimesh.proximity.closest_point(netz, punkte)[1] * 1000.0

    # ------------------------------------------------------------ Maße

    def _original_zu_modell(self, region):
        punkte = np.asarray(self.vorgabe.vertices)[region]
        d = self._abstand_mm(self.modell, punkte)
        return {'gesamt': self.rahmen.statistik(d), 'innerhalb_1mm': round(float((d < 1.0).mean()), 3), 'innerhalb_2mm': round(float((d < 2.0).mean()), 3),
                'zonen': self.rahmen.tabelle(d, punkte)}

    def _stueck_zu_original(self):
        punkte = np.asarray(self.stueck.vertices)
        self.abstand_stueck = self._abstand_mm(self.original, punkte)
        return {'gesamt': self.rahmen.statistik(self.abstand_stueck), 'zonen': self.rahmen.tabelle(self.abstand_stueck, punkte)}

    def _tiefen(self, netz, ursprung):
        """Tiefe (m, relativ zur Mitte, längs `vorne`) der ersten Fläche je Strahl — NaN ohne Treffer."""
        r = self.rahmen
        tiefe = np.full(len(ursprung), -np.inf)
        orte, strahl, _ = netz.ray.intersects_location(ursprung, np.tile(-r.vorne, (len(ursprung), 1)), multiple_hits=False)
        if len(orte):
            np.maximum.at(tiefe, strahl, (orte - r.mitte) @ r.vorne)
        tiefe[np.isinf(tiefe)] = np.nan
        return tiefe

    def _tiefenkarte(self):
        r, g = self.rahmen, self.rahmen.grenzen
        us = np.arange(g[0][0], g[0][1] + 1e-9, self.RASTER_M)
        ws = np.arange(g[1][0], g[1][1] + 1e-9, self.RASTER_M)
        uu, ww = np.meshgrid(us, ws)
        ursprung = r.mitte + uu.ravel()[:, None] * r.quer + ww.ravel()[:, None] * r.laengs + (g[2][1] + 0.05) * r.vorne
        t_orig, t_mod = self._tiefen(self.original, ursprung), self._tiefen(self.modell, ursprung)
        d = (t_mod - t_orig) * 1000.0
        ok = np.isfinite(d)
        if not ok.any():
            return {'hinweis': 'kein Strahl traf Original und Modell zugleich'}
        orte = r.mitte + uu.ravel()[ok][:, None] * r.quer + ww.ravel()[ok][:, None] * r.laengs
        d_ok = d[ok]
        return {'strahlen': int(len(d)), 'beide_getroffen': int(ok.sum()), 'bias_mm': round(float(d_ok.mean()), 2),
                'betrag': self.rahmen.statistik(np.abs(d_ok)), 'zonen': self.rahmen.tabelle(np.abs(d_ok), orte),
                'profil_mitte': self._zeilen(us, ws, t_orig, t_mod, d, [(0.0, w) for w in ws[::2]]),
                'profil_quer': self._zeilen(us, ws, t_orig, t_mod, d, [(u, g[1][1] - (k + 0.5) / 3.0 * (g[1][1] - g[1][0])) for k in range(3) for u in self.PROFIL_QUER_M])}

    def _zeilen(self, us, ws, t_orig, t_mod, d, orte):
        """Messpunkte `[{quer_mm, laengs_mm, original_mm, modell_mm, d_mm}]` an den Rasterzellen, die den Orten `(quer, längs)` am nächsten liegen; Zellen ohne Treffer entfallen."""
        zeilen = []
        for u, w in orte:
            i, j = int(np.argmin(np.abs(ws - w))), int(np.argmin(np.abs(us - u)))
            n = i * len(us) + j
            if np.isfinite(d[n]):
                zeilen.append({'quer_mm': round(float(us[j]) * 1000, 1), 'laengs_mm': round(float(ws[i]) * 1000, 1), 'original_mm': round(float(t_orig[n]) * 1000, 2),
                               'modell_mm': round(float(t_mod[n]) * 1000, 2), 'd_mm': round(float(d[n]), 2)})
        return zeilen

    def _symmetrie(self):
        from scipy.spatial import cKDTree

        r = self.rahmen
        p = np.asarray(self.stueck.vertices)
        kern = np.abs(r.koordinaten(p)[:, 0]) < self.KERN_M
        if len(self.rand):
            kern &= cKDTree(self.rand).query(p)[0] > self.RAND_ABSTAND_M
        aus = {'stueck': r.statistik(self._abstand_mm(self.stueck, r.spiegeln(p[kern]))) if kern.any() else None}
        if self.vorgabe is not None and len(self.vorgabe.vertices):
            v = np.asarray(self.vorgabe.vertices)[self._region()]
            v = v[np.abs(r.koordinaten(v)[:, 0]) < self.KERN_M]
            aus['original'] = r.statistik(self._abstand_mm(self.vorgabe, r.spiegeln(v))) if len(v) else None
        return aus

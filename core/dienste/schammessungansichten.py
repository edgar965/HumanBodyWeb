# -*- coding: utf-8 -*-
"""Schammessungansichten — Erhebungen und Absätze des Scham-Stücks aus mehreren Blickrichtungen (11.10.2026).

Edgar: „das ist eine Sprungschanze … seitlich gibt es cm hohe Absätze", „cute girl Daz2 ist ja komplett ohne Geometrie", „Messungen aller Geometrien, aller Erhebungen aus mindestens vier Winkeln".
Die übrigen Maße (`Schammessunggeometrie`) maßen Form und Tiefe nur von vorn und gegen die Haut, die das Original selbst trägt — ein Absatz zwischen Haut und Original, den das Stück
getreu mitmacht, fiel nicht auf (Form Original → Modell Median 0,32 mm, während das Stück seitlich 14 mm unter der Haut begann).

    ansichten   je Blickrichtung (vorn, unten 45°, links 45°, rechts 45°): Strahlen im Raster `RASTER_M` auf die ganze Haut (ohne Loch), das Original und das Modell;
                Erhebung = Abstand der ersten Fläche vor der Haut (mm, + = davor, − = darunter). Je Richtung:
                  volumen_*_mm3    Summe der Erhebungen (Original / Modell) mal Zellenfläche; `senke_*_mm3` dasselbe für die Vertiefungen
                  treue            Volumen Modell / Volumen Original (1 = gleich viel Erhebung; 0 = flach)
                  hoehe_*_mm       p95 und größte Erhebung (Original / Modell) auf den Zellen, auf denen das Original über `ERHEBT_MM` steht
                  abweichung       Betrag Erhebung Modell − Erhebung Original (n, Median, p90, max), dazu je Zone
    absatz      je Ringpunkt: Höhe der Fläche `ABSATZ_NACH_INNEN_M` hinter dem Ring über der Tangentialebene der Haut am Ring, entlang der Hautnormale — für das Original und das Stück.
                Am Ring SOLL sie null sein (die Haut geht ohne Stufe ins Stück über); jede Zahl darüber ist eine Stufe im Bild (Edgar: „cm hohe Absätze").
"""
import numpy as np

__all__ = ['Schammessungansichten']


class Schammessungansichten:
    #: Blickrichtungen `(Name, Höhenwinkel, Seitenwinkel)` in Grad im Rahmen der Messung (Höhe + = von oben, Seite + = von rechts, 0/0 = von vorn).
    RICHTUNGEN = (('vorn', 0.0, 0.0), ('unten 45°', -45.0, 0.0), ('links 45°', 0.0, -45.0), ('rechts 45°', 0.0, 45.0))
    #: Abstand der Strahlen (m). Gemessen 11.10.2026 (trimesh ohne Embree): sechs Richtungen (dazu „oben 45°", fast leer, und „unten 60°", wie „unten 45°") bei 1,5 mm brauchten am Stück auf Stufe 1 237 s,
    #: bei 2,5 mm 79 s (Stufe 2: 154–212 s) — für eine Messung bei jedem Bau zu lang.
    RASTER_M = 0.004
    #: Zellen zählen nur, wenn ihre Haut höchstens so weit (m) neben dem Stück (quer, längs) und so weit vor/hinter ihm (vorne) liegt.
    KASTEN_SEITE_M, KASTEN_TIEFE_M = 0.006, 0.020
    #: Eine Richtung wird nur beurteilt (`treue`), wenn das Original dort mindestens so viel Erhebung (mm³) hat — von oben verdeckt der Hügel fast alles.
    MIN_VOLUMEN_MM3 = 300
    #: Das Original zählt als erhaben, wenn es mehr als so viel (mm) vor der Haut steht.
    ERHEBT_MM = 1.0
    #: Absatz: so weit (m) hinter dem Ring wird die Höhe gemessen.
    ABSATZ_NACH_INNEN_M = 0.002

    def __init__(self, rahmen, haut, original, modell, stueck, vorgabe, ring, ring_normalen):
        """`haut`, `original`, `modell`, `stueck`, `vorgabe`: `trimesh.Trimesh` (`haut` = die ganze Haut im Kasten OHNE Loch; `original` = Vorgabe samt sichtbarer Haut; `modell` = sichtbare Haut + Stück; `vorgabe` = nur das Original);
        `ring`: `(R, 3)` Ringecken; `ring_normalen`: `(R, 3)` Hautnormalen dort."""
        self.rahmen, self.haut, self.original, self.modell, self.stueck, self.vorgabe = rahmen, haut, original, modell, stueck, vorgabe
        self.ring, self.ring_normalen = np.asarray(ring, dtype=np.float64), np.asarray(ring_normalen, dtype=np.float64)

    def messen(self):
        aus = {'ansichten': [self._ansicht(*r) for r in self.RICHTUNGEN]}
        if len(self.ring):
            aus['absatz'] = self._absatz()
        return aus

    # ------------------------------------------------------------ Ansichten

    def _blick(self, hoehe, seite):
        """Einheitsvektor von der Mitte zur Kamera."""
        r = self.rahmen
        h, s = np.radians(hoehe), np.radians(seite)
        return np.cos(h) * np.cos(s) * r.vorne + np.sin(h) * r.laengs + np.cos(h) * np.sin(s) * r.quer

    def _erste(self, netz, wurzeln, richtung):
        """Weg (m) bis zur ersten Fläche je Strahl, NaN ohne Treffer."""
        t = np.full(len(wurzeln), np.nan)
        orte, strahl, _ = netz.ray.intersects_location(wurzeln, np.tile(richtung, (len(wurzeln), 1)), multiple_hits=False)
        if len(orte):
            t[strahl] = np.linalg.norm(orte - wurzeln[strahl], axis=1)
        return t

    def _ansicht(self, name, hoehe, seite):
        r = self.rahmen
        blick = self._blick(hoehe, seite)
        u = r.quer - (r.quer @ blick) * blick
        u /= np.linalg.norm(u)
        v = np.cross(blick, u)
        k = np.asarray(self.stueck.vertices) - r.mitte
        a, b = (k @ u).min(), (k @ u).max()
        c, d = (k @ v).min(), (k @ v).max()
        uu, vv = np.meshgrid(np.arange(a, b, self.RASTER_M), np.arange(c, d, self.RASTER_M))
        flaeche = self.RASTER_M * self.RASTER_M * 1e6                                            # mm² je Zelle, senkrecht zum Strahl
        wurzel = r.mitte + 0.12 * blick + uu.ravel()[:, None] * u + vv.ravel()[:, None] * v
        t_haut = self._erste(self.haut, wurzel, -blick)
        # nur Zellen, deren Haut im Kasten ums Stück liegt — von unten und von der Seite stünden sonst Schenkel und Bauch im Bild (gemessen 11.10.2026: „unten 70°" meldete 10.045 mm³, Höhe 107 mm)
        k = r.koordinaten(wurzel - np.nan_to_num(t_haut)[:, None] * blick)
        g = r.grenzen
        im_kasten = np.isfinite(t_haut)
        for a, rand in ((0, self.KASTEN_SEITE_M), (1, self.KASTEN_SEITE_M), (2, self.KASTEN_TIEFE_M)):
            im_kasten &= (k[:, a] >= g[a][0] - rand) & (k[:, a] <= g[a][1] + rand)
        nummern = np.flatnonzero(im_kasten)
        t_orig, t_mod = np.full(len(wurzel), np.nan), np.full(len(wurzel), np.nan)
        if len(nummern):
            t_orig[nummern] = self._erste(self.original, wurzel[nummern], -blick)
            t_mod[nummern] = self._erste(self.modell, wurzel[nummern], -blick)
        e_orig, e_mod = (t_haut - t_orig) * 1000.0, (t_haut - t_mod) * 1000.0
        ok = np.isfinite(e_orig) & np.isfinite(e_mod)
        aus = {'name': name, 'strahlen': int(len(wurzel)), 'im_kasten': int(len(nummern)), 'zellen': int(ok.sum())}
        if not ok.any():
            return dict(aus, hinweis='kein Strahl traf Haut, Original und Modell zugleich')
        eo, em = e_orig[ok], e_mod[ok]
        vo, vm = float(np.clip(eo, 0, None).sum() * flaeche), float(np.clip(em, 0, None).sum() * flaeche)
        erhaben = eo > self.ERHEBT_MM
        aus.update(volumen_original_mm3=round(vo), volumen_modell_mm3=round(vm), treue=round(vm / vo, 2) if vo >= self.MIN_VOLUMEN_MM3 else None,
                   senke_original_mm3=round(float(np.clip(-eo, 0, None).sum() * flaeche)), senke_modell_mm3=round(float(np.clip(-em, 0, None).sum() * flaeche)))
        if erhaben.any():
            aus['hoehe_original_mm'] = [round(float(np.percentile(eo[erhaben], 95)), 1), round(float(eo[erhaben].max()), 1)]
            aus['hoehe_modell_mm'] = [round(float(np.percentile(em[erhaben], 95)), 1), round(float(em[erhaben].max()), 1)]
        orte = (wurzel - np.nan_to_num(t_haut)[:, None] * blick)[ok]
        betrag = np.abs(em - eo)
        aus['abweichung'] = r.statistik(betrag)
        aus['zonen'] = r.tabelle(betrag, orte)
        return aus

    # ------------------------------------------------------------ Absatz am Ring

    def _hoehe_entlang(self, netz, ring_punkt, normale, nach_innen):
        """Höhe (mm) der ersten Fläche über der Tangentialebene am Ringpunkt, `ABSATZ_NACH_INNEN_M` hinter dem Ring — NaN ohne Treffer."""
        q = ring_punkt + nach_innen * self.ABSATZ_NACH_INNEN_M
        orte, _i, _t = netz.ray.intersects_location((q + normale * 0.03)[None], (-normale)[None], multiple_hits=True)
        if not len(orte):
            return np.nan
        return float((orte[int(np.argmin(np.linalg.norm(orte - (q + normale * 0.03), axis=1)))] - ring_punkt) @ normale * 1000.0)

    def _absatz(self):
        mitte = self.ring.mean(axis=0)
        orig, stueck = [], []
        # das Original ohne die Haut: sonst träfe der Strahl die Haut, die über dem Original steht
        original_pur = self.vorgabe
        for p, n in zip(self.ring, self.ring_normalen, strict=True):
            n = n / max(np.linalg.norm(n), 1e-12)
            innen = mitte - p
            innen = innen - (innen @ n) * n
            innen /= max(np.linalg.norm(innen), 1e-12)
            orig.append(self._hoehe_entlang(original_pur, p, n, innen))
            stueck.append(self._hoehe_entlang(self.stueck, p, n, innen))
        o, s = np.abs(np.asarray(orig)), np.abs(np.asarray(stueck))
        stat = self.rahmen.statistik
        return {'nach_innen_mm': self.ABSATZ_NACH_INNEN_M * 1000.0, 'stueck_mm': stat(s), 'original_mm': stat(o),
                'stueck_ueber_3mm': int(np.nansum(s > 3.0)), 'stueck_ueber_10mm': int(np.nansum(s > 10.0)),
                'original_ueber_3mm': int(np.nansum(o > 3.0)), 'original_ueber_10mm': int(np.nansum(o > 10.0)), 'ringpunkte': int(len(self.ring))}

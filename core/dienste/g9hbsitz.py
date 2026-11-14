# -*- coding: utf-8 -*-
u"""G9hbsitz — der Sitz eines Daz-Stuecks auf HumanBody: Rumpfhoehen nach
Landmarken und ein oertlicher Massstab je Koerperpunkt.

WARUM (19.09.2026, Edgar mit drei Bildern: „die Hose … etwas zu tief
angepasst", „das Oberteil zu weit"): Die Paarung der Grundkoerper
(`G9aufhumanbody`) schaetzt den Rumpf ueber EINE Aehnlichkeitsabbildung der
Gelenke — Wirbel, Hals, Schultern, Hueftgelenke. Wo Bund und Saum sitzen,
entscheidet aber die Oberflaeche: Genesis 9 hat die Hueftweite 10 cm ueber
dem Schritt, HumanBody 15 cm; die Taille 28 gegen 29 cm. Gemessen an den
Grundfiguren (`_wegwerf/mess_dazsitz_hb.py`): der Bund der Angie Jeans lag
auf Genesis 10,1 cm ueber der Hueftweite, auf HumanBody 3,6 cm — ein
tiefer Bund, den niemand gezeichnet hat. Und HumanBodys Taille ist 13 cm
schmaler (Umfang 0,607 gegen 0,736 m), das Stueck behielt aber seinen
Abstand zur Haut in Metern: das Top stand 1,74-fach um den Rumpf statt
1,55-fach wie auf Genesis.

RUMPFHOEHEN: Drei Landmarken je Grundfigur am Rumpfsegment — Schritt
(tiefster Rumpfpunkt nahe der Mitte), Hueftweite (groesster Umfang bis 25 cm
darueber), Taille (kleinster Umfang bis 30 cm ueber der Huefte). Die
Schaetzung der Rumpfpunkte wird in der Hoehe stueckweise linear so verbogen,
dass Genesis' Landmarken auf HumanBodys fallen; 15 cm ueber der Taille und
5 cm unter dem Schritt gilt wieder die Schaetzung selbst (stetig, monoton).
Alles andere (Arme, Beine, Kopf) bleibt.

OERTLICHER MASSSTAB: Der Versatz eines Stoffpunkts zum Koerper wird mit dem
Verhaeltnis der RUMPFUMFAENGE skaliert — Umfang der Figur (mit Morphs) in
der Hoehe des gepaarten Punkts durch den Umfang von Genesis in der Hoehe
des Genesis-Punkts, je 1-cm-Band am Rumpfsegment bis 20 cm ueber der
Taille (Achseln); darueber, an Armen, Beinen und Gesicht bleibt der
Hoehenmassstab — ueber den Achseln zaehlt ein Band die Schultern mal mit, mal
nicht (Segmentgrenzen), und ein Kragen 15 cm ueber der Halswurzel rutschte
um 8 cm. Ein schmalerer Rumpf bekommt ein engeres
Top, eine groessere Brust mehr Raum davor. Ein Massstab aus den
Nachbarabstaenden der gepaarten Punkte war ungeeignet (gemessen: Median
1,12 bei einem 13 cm schmaleren Rumpf, im Kopf bis 2,0) — die Streuung der
Paarung blaeht jede Nachbarschaft auf.
"""
import torch
from KoerperKI_alle.torchfeld import Torchfeld

__all__ = ['G9hbsitz']


class G9hbsitz:
    u"""Landmarken, Hoehenkorrektur des Rumpfs, oertlicher Massstab."""

    BAND = 0.01          # Hoehenband der Umfangsmessung (m)
    MITTE = 0.05         # |x| fuer den Schrittpunkt (m)
    HUEFTE_BIS = 0.25    # Hueftweite: bis so weit ueber dem Schritt
    TAILLE_BIS = 0.30    # Taille: bis so weit ueber der Huefte
    BRUST_UEBER = 0.15   # ab so weit ueber der Taille gilt die Schaetzung wieder
    UNTER_SCHRITT = 0.05
    MASSSTAB_MIN, MASSSTAB_MAX = 0.5, 2.0
    ACHSEL_UEBER = 0.20  # Umfangsmassstab bis so weit ueber der Taille (Genesis)
    UEBERGANG = 0.10     # darueber ueber diese Hoehe auf den Hoehenmassstab

    # ---------------------------------------------------------- Landmarken

    @classmethod
    def umfang(cls, punkte, y):
        u"""Umfang der konvexen Huelle (xz) im Hoehenband um y — NaN ohne Punkte."""
        from KoerperKI_alle.kartenhuelle import ConvexHull
        m = Torchfeld.abs(punkte[:, 1] - y) < cls.BAND
        if m.sum() < 8:
            return float('nan')
        return float(ConvexHull(punkte[m][:, [0, 2]]).area)

    @classmethod
    def landmarken(cls, punkte, rumpf):
        u"""`{schritt, huefte, taille}` (Hoehen, m) am Rumpfsegment `rumpf` (Nummern)."""
        r = Torchfeld.feld(punkte, dtype=torch.float64)[Torchfeld.feld(rumpf, dtype=torch.int64)]
        mitte = r[Torchfeld.abs(r[:, 0]) < cls.MITTE]
        schritt = float(mitte[:, 1].min()) if len(mitte) else float(r[:, 1].min())
        huefte = cls._extrem(r, schritt, schritt + cls.HUEFTE_BIS, Torchfeld.nanargmax)
        taille = cls._extrem(r, huefte, huefte + cls.TAILLE_BIS, Torchfeld.nanargmin)
        return {'schritt': schritt, 'huefte': huefte, 'taille': taille}

    @classmethod
    def _extrem(cls, r, von, bis, wahl):
        ys = Torchfeld.arange(von, bis, cls.BAND)
        us = Torchfeld.feld([cls.umfang(r, y) for y in Torchfeld.liste(ys)], copy=True)
        if not Torchfeld.isfinite(us).any():
            return float(von)
        return float(ys[int(wahl(us))])

    # ---------------------------------------------------------- Rumpfhoehen

    @classmethod
    def rumpfhoehen(cls, geschaetzt, g9_punkte, g9_rumpf, hb_punkte, hb_rumpf):
        u"""Kopie von `geschaetzt` (N, 3), die Hoehe der Rumpfpunkte so verbogen,
        dass Genesis' Landmarken auf HumanBodys liegen. Liefert (Punkte, Knoten)."""
        aus = Torchfeld.feld(geschaetzt, dtype=torch.float64, copy=True)
        g9 = Torchfeld.feld(g9_punkte, dtype=torch.float64)
        idx = Torchfeld.feld(g9_rumpf, dtype=torch.int64)
        if not len(idx):
            return aus, None
        lg = cls.landmarken(g9, idx)
        lh = cls.landmarken(hb_punkte, hb_rumpf)
        # Knoten im Raum der Schaetzung: je Landmarke die geschaetzte Hoehe der
        # Genesis-Rumpfpunkte in ihrem Band; Ziel die HumanBody-Hoehe.
        est_y = aus[idx, 1]
        g9_y = g9[idx, 1]

        def geschaetzte_hoehe(y):
            m = Torchfeld.abs(g9_y - y) < cls.BAND
            return float(est_y[m].mean()) if m.any() else float('nan')

        namen = ('schritt', 'huefte', 'taille')
        von = [geschaetzte_hoehe(lg[n]) for n in namen]
        nach = [lh[n] for n in namen]
        oben = geschaetzte_hoehe(lg['taille'] + cls.BRUST_UEBER)
        unten = geschaetzte_hoehe(lg['schritt'] - cls.UNTER_SCHRITT)
        if not Torchfeld.isfinite(oben):
            oben = von[-1] + cls.BRUST_UEBER
        if not Torchfeld.isfinite(unten):
            unten = von[0] - cls.UNTER_SCHRITT
        x = Torchfeld.feld([unten] + von + [oben], copy=True)
        y = Torchfeld.feld([unten] + nach + [oben], copy=True)
        if not (Torchfeld.isfinite(x).all() and Torchfeld.all(Torchfeld.diff(x) > 0) and Torchfeld.all(Torchfeld.diff(y) > 0)):
            return aus, None                       # nicht monoton: lieber nichts verbiegen
        # Nur zwischen den Knoten verbiegen — `np.interp` haelt ausserhalb den
        # Randwert fest, und der Kopf laege dann auf Brusthoehe.
        drin = (est_y >= x[0]) & (est_y <= x[-1])
        aus[idx[drin], 1] = Torchfeld.interp(est_y[drin], x, y)
        return aus, {'von': x.round(decimals=4).tolist(), 'nach': y.round(decimals=4).tolist(),
                     'genesis': lg, 'humanbody': lh}

    # ------------------------------------------------------ Oertlicher Massstab

    @classmethod
    def umfangstabelle(cls, punkte, rumpf):
        u"""(Hoehen, Umfaenge) des Rumpfsegments je Band — nur Baender mit Wert."""
        r = Torchfeld.feld(punkte, dtype=torch.float64)[Torchfeld.feld(rumpf, dtype=torch.int64)]
        ys = Torchfeld.arange(r[:, 1].min(), r[:, 1].max(), cls.BAND)
        us = Torchfeld.feld([cls.umfang(r, y) for y in Torchfeld.liste(ys)], copy=True)
        ok = Torchfeld.isfinite(us)
        return ys[ok], us[ok]

    @classmethod
    def massstab(cls, g9_punkte, g9_rumpf, zu, figur_punkte, hb_rumpf, sonst=1.0, bis=None):
        u"""(N,) Massstab je Genesis-Koerperpunkt: am Rumpf das Umfangsverhaeltnis
        Figur/Genesis in der jeweiligen Hoehe, sonst `sonst` (Hoehenmassstab).
        `bis` (Genesis-Hoehe, m): bis hierher gilt der Umfang, darueber blendet
        er ueber UEBERGANG auf `sonst` — ueber den Achseln zaehlen die Baender
        die Schultern nur auf einer Seite mit."""
        g9 = Torchfeld.feld(g9_punkte, dtype=torch.float64)
        aus = Torchfeld.full(len(g9), float(sonst))
        idx = Torchfeld.feld(g9_rumpf, dtype=torch.int64)
        if not len(idx) or not len(hb_rumpf) or bis is None:
            return aus
        yg, ug = cls.umfangstabelle(g9, g9_rumpf)
        yh, uh = cls.umfangstabelle(figur_punkte, hb_rumpf)
        if len(yg) < 2 or len(yh) < 2:
            return aus
        fig = Torchfeld.feld(figur_punkte, dtype=torch.float64)
        u_g9 = Torchfeld.interp(g9[idx, 1], yg, ug)
        u_hb = Torchfeld.interp(fig[Torchfeld.feld(zu, dtype=torch.int64)[idx], 1], yh, uh)
        umfang = Torchfeld.clip(u_hb / Torchfeld.maximum(u_g9, 1e-6), cls.MASSSTAB_MIN, cls.MASSSTAB_MAX)
        anteil = Torchfeld.clip((g9[idx, 1] - bis) / cls.UEBERGANG, 0.0, 1.0)      # 0 Rumpf, 1 darueber
        aus[idx] = (1.0 - anteil) * umfang + anteil * float(sonst)
        return aus

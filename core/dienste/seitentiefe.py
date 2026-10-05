# -*- coding: utf-8 -*-
"""Seitentiefe — wie tief (vorn–hinten) ist der Rumpf je Höhe: im Seitenfoto, im Netz, am Körper, am Hemd (05.10.2026).

Edgar (05.10.2026, Seitenansicht): „bauch ist viel zu dick beim Modell im vergleich zur vorlage". Die Messgröße der Kleiderstücke (`Kleiderstuecknote`) vergleicht die Stücke mit dem NETZ und konnte den Fehler nicht
sehen, denn das Netz selbst war zu tief: Am Testauftrag 2026.10.04.11.11.44 war es bei 0,50–0,55 der Körpergröße 33 und 29 mm tiefer als die Silhouette im Seitenfoto, das Hemd-Stück bis 42 mm.

Die Silhouette eines Seitenfotos legt die Tiefe fest, unabhängig davon, was ein Netz erfindet: Breite der Maske in der Zeile = Tiefe des Körpers samt Stoff (und hängendem Arm, der innerhalb liegt — das Foto kann nur
zu tief erscheinen, nie zu flach). Alles wird als ANTEIL DER KÖRPERGRÖSSE gerechnet (Tiefe ÷ Höhe von der Sohle bis zum Scheitel), nicht in Millimetern: dann gilt dieselbe Rechnung für das Roh-Netz (beliebige Einheit)
und für Stücke in Metern; die Millimeter folgen aus der Körpergröße.

    foto_profil(alpha)                          Tiefe je Höhenanteil aus der Maske des Seitenfotos
    modell_profil(punkte, y0, y1)               Tiefe, Rückseite und Vorderseite je Höhenanteil: Schnitt ± `SCHICHT`, nur Punkte im Mittelstreifen (`STREIFEN` der Größe um die Mitte — ohne hängende Arme),
                                                Perzentil 1 … 99 entlang der Tiefenachse
    abweichung(modell, foto)                    Modell − Foto je Höhenanteil im Band, + = Modell tiefer; mit `hoehe_m` in Millimetern

Achsen wie die Fotoprojektion (`ACHSEN`): hoch = y, breit = x, tief = z, vorn = +z.
"""

import numpy as np

__all__ = ['Seitentiefe']


class Seitentiefe:
    #: Höhenanteile, an denen gemessen wird: 0,40 bis 0,85 der Körpergröße von der Sohle (Hüfte bis Schulter).
    HOEHEN = tuple(round(0.40 + 0.01 * i, 2) for i in range(46))
    #: Halbe Dicke des Schnitts, als Anteil der Körpergröße (6 mm bei 1,69 m).
    SCHICHT = 0.0035
    #: Halbe Breite des Mittelstreifens, als Anteil der Körpergröße (0,17 m bei 1,69 m) — die Arme hängen weiter außen.
    STREIFEN = 0.10
    #: Das Band, in dem Foto und Modell verglichen werden.
    BAND = (0.50, 0.80)
    MIN_PUNKTE = 8

    @classmethod
    def foto_profil(cls, alpha, hoehen=None):
        """`{höhenanteil: Tiefe als Anteil der Körpergröße}` aus der Maske (H, W) bool eines Seitenfotos — die Höhe der Maske ist die Körpergröße (Scheitel bis Sohle)."""
        alpha = np.asarray(alpha, dtype=bool)
        zeilen = np.flatnonzero(alpha.any(axis=1))
        if not len(zeilen):
            return {}
        oben, unten = int(zeilen.min()), int(zeilen.max())
        hoehe = max(1, unten - oben)
        aus = {}
        for h in hoehen or cls.HOEHEN:
            spalten = np.flatnonzero(alpha[int(round(unten - h * hoehe))])
            if len(spalten):
                aus[h] = float(spalten.max() - spalten.min()) / hoehe
        return aus

    @classmethod
    def modell_profil(cls, punkte, y0=None, y1=None, hoehen=None, mitte_x=None):
        """`{höhenanteil: {'tiefe': Anteil der Größe, 'hinten': z, 'vorne': z}}` — `y0`/`y1`: Sohle und Scheitel (Vorgabe: Spanne der Punkte), `mitte_x`: Mitte des Rumpfs (Vorgabe: Median)."""
        p = np.asarray(punkte, dtype=np.float64)
        y0 = float(p[:, 1].min()) if y0 is None else float(y0)
        y1 = float(p[:, 1].max()) if y1 is None else float(y1)
        hoehe = max(y1 - y0, 1e-9)
        aus = {}
        for h in hoehen or cls.HOEHEN:
            schicht = p[np.abs(p[:, 1] - (y0 + h * hoehe)) < cls.SCHICHT * hoehe]
            if len(schicht) < cls.MIN_PUNKTE:
                continue
            mitte = float(np.median(schicht[:, 0])) if mitte_x is None else float(mitte_x)
            streifen = schicht[np.abs(schicht[:, 0] - mitte) < cls.STREIFEN * hoehe]
            if len(streifen) < cls.MIN_PUNKTE:
                continue
            hinten, vorne = (float(x) for x in np.percentile(streifen[:, 2], (1, 99)))
            aus[h] = {'tiefe': (vorne - hinten) / hoehe, 'hinten': hinten, 'vorne': vorne}
        return aus

    @classmethod
    def mittel(cls, profile):
        """Mittel mehrerer Foto-Profile (z. B. links und rechts) je Höhenanteil, nur wo alle einen Wert haben."""
        if not profile:
            return {}
        gemeinsam = set.intersection(*(set(p) for p in profile))
        return {h: float(np.mean([p[h] for p in profile])) for h in sorted(gemeinsam)}

    @classmethod
    def abweichung(cls, modell, foto, hoehe_m=None):
        """`{'je_hoehe': {h: Modell − Foto}, 'mittel', 'max', 'tiefer_als_foto'}` im Band `BAND` — als Anteil der Größe, mit `hoehe_m` zusätzlich in Millimetern (`*_mm`)."""
        je = {h: (m['tiefe'] if isinstance(m, dict) else m) - foto[h] for h, m in modell.items() if h in foto and cls.BAND[0] <= h <= cls.BAND[1]}
        if not je:
            return {}
        werte = np.array(list(je.values()))
        aus = {'je_hoehe': {h: round(v, 5) for h, v in je.items()}, 'mittel': round(float(werte.mean()), 5), 'max': round(float(werte.max()), 5),
               'tiefer_als_foto': round(float((werte > 0).mean()), 3)}
        if hoehe_m:
            aus.update(mittel_mm=round(aus['mittel'] * hoehe_m * 1000, 1), max_mm=round(aus['max'] * hoehe_m * 1000, 1),
                       je_hoehe_mm={h: round(v * hoehe_m * 1000, 1) for h, v in je.items()})
        return aus

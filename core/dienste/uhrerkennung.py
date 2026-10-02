# -*- coding: utf-8 -*-
"""Uhrerkennung — trägt die Person auf den Fotos eine Armbanduhr, und an welchem Arm? (01.10.2026)

Edgar (01.10.2026): „Erzeuge für alle Objekte aus den Bildern eigene Assets wie Haare, Kleider, Uhr usw." — die Uhr
baut `G9uhrstueck`; hier die Frage, ob sie auf den Fotos ist. Nur Fotos, die für die Farbe zählen (`Iterationsreferenz.
farbe`), mit Posenlandmarken (`Fotolandmarken`, MediaPipe: 15/16 Handgelenk, 13/14 Ellbogen — „links" ist der linke Arm
der PERSON).

MESSUNG je Arm und Foto: Querstreifen über den Unterarm, vom Handgelenk (`VON`) Richtung Ellbogen (`BIS`, Anteil der
Unterarmlänge), je `BREITE` der Unterarmlänge breit. Die Haut kommt aus dem Unterarm weiter oben (`HAUT`); ein Pixel ist
„Uhr", wenn es deutlich dunkler ist als diese Haut (`DUNKEL` · Helligkeit) und kaum bunt (`BUNT`). Ein Streifen mit mehr
als `ANTEIL` solcher Pixel ist ein Uhrband — gefunden, wenn mindestens `STREIFEN_MIN` aufeinanderfolgende es sind.
Testauftrag 2026.10.01.12.38.09: schwarze Uhr links, rechts nichts.
"""

import numpy as np

__all__ = ['Uhrerkennung']


class Uhrerkennung:
    GELENKE = {'l': (15, 13), 'r': (16, 14)}
    VON, BIS, SCHRITTE = 0.02, 0.35, 24
    BREITE = 0.10
    HAUT = (0.45, 0.75)
    DUNKEL = 0.55
    BUNT = 0.12
    ANTEIL = 0.45
    STREIFEN_MIN = 2
    SICHTBAR = 0.5

    def __init__(self, ablage):
        self.ablage = ablage

    @staticmethod
    def _hell(rgb):
        return rgb @ np.array([0.299, 0.587, 0.114])

    def _streifen(self, bild, hand, ellbogen, t):
        """Pixel (K, 3) 0…1 eines Querstreifens bei `t` (Anteil Handgelenk → Ellbogen)."""
        achse = ellbogen - hand
        laenge = float(np.linalg.norm(achse))
        quer = np.array([-achse[1], achse[0]]) / max(laenge, 1e-9)
        mitte = hand + achse * t
        s = np.linspace(-self.BREITE, self.BREITE, 21) * laenge
        dt = np.linspace(-0.5, 0.5, 3) * laenge * (self.BIS - self.VON) / self.SCHRITTE
        orte = mitte[None, None, :] + s[None, :, None] * quer + dt[:, None, None] * (achse / max(laenge, 1e-9))
        x = np.clip(np.round(orte[..., 0]).astype(int), 0, bild.shape[1] - 1)
        y = np.clip(np.round(orte[..., 1]).astype(int), 0, bild.shape[0] - 1)
        return bild[y, x].reshape(-1, 3)

    def arm(self, bild, pose, seite):
        """→ (Anteil dunkler Pixel je Streifen, gefunden) für einen Arm; None, wenn der Arm nicht sicher sichtbar ist."""
        i_hand, i_ell = self.GELENKE[seite]
        h, b = bild.shape[:2]
        p_hand, p_ell = pose[i_hand], pose[i_ell]
        if len(p_hand) > 2 and min(float(p_hand[-1]), float(p_ell[-1])) < self.SICHTBAR:
            return None
        hand = np.array([float(p_hand[0]) * b, float(p_hand[1]) * h])
        ell = np.array([float(p_ell[0]) * b, float(p_ell[1]) * h])
        haut = np.concatenate([self._streifen(bild, hand, ell, t) for t in np.linspace(*self.HAUT, 6)])
        haut_hell = float(np.median(self._hell(haut)))
        anteile = []
        for t in np.linspace(self.VON, self.BIS, self.SCHRITTE):
            px = self._streifen(bild, hand, ell, t)
            dunkel = (self._hell(px) < self.DUNKEL * haut_hell) & ((px.max(axis=1) - px.min(axis=1)) < self.BUNT)
            anteile.append(round(float(dunkel.mean()), 3))
        lauf, best = 0, 0
        for a in anteile:
            lauf = lauf + 1 if a > self.ANTEIL else 0
            best = max(best, lauf)
        return anteile, best >= self.STREIFEN_MIN

    def erkennen(self, referenzen):
        """`{l|r: {'gefunden': bool, 'fotos': {datei: bool}}}` über die Farbfotos — gefunden, wenn ein Foto sie
        zeigt."""
        from PIL import Image

        from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
        from .fotolandmarken import Fotolandmarken
        eingang = self.ablage.unter(Engine2d3dKleiderablage.EINGANG)
        farbig = [r for r in referenzen if getattr(r, 'farbe', True)]
        marken = Fotolandmarken(self.ablage).holen([eingang / r.datei for r in farbig])
        aus = {s: {'gefunden': False, 'fotos': {}} for s in self.GELENKE}
        for r in farbig:
            befund = marken.get(r.datei) or {}
            if not befund.get('pose'):
                continue
            bild = np.asarray(Image.open(eingang / r.datei).convert('RGB'), dtype=np.float64) / 255.0
            for seite in self.GELENKE:
                ergebnis = self.arm(bild, befund['pose'], seite)
                if ergebnis is None:
                    continue
                aus[seite]['fotos'][r.datei] = ergebnis[1]
                aus[seite]['gefunden'] |= ergebnis[1]
        return aus

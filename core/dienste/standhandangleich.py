# -*- coding: utf-8 -*-
"""Standhandangleich — die Haut der Hand und des Handgelenks im Ton des Unterarms (04.10.2026, Edgar: „hände sind wie angenäht").

Die Armkachel (1004) der Figur hat zwei Quellen: Der Unterarm trägt die Farbe der Fotos (HD-Schicht des Schritts „Körper", `Meshfigurtextur`), die Hand nicht — „Finger, Hände (die Faust des
Netzes ist nicht die offene Hand der Figur) und Innenräume bekommen keine Netzfarbe; dort bleibt die auf den Hautton getönte Daz-Haut" (`G9texturbacken`: Tonangleich nur im Umkreis von 48 Texeln
um HD-Texel). Am Handgelenk stoßen deshalb zwei Töne und zwei Schärfen aneinander: im Bühnenbild eine helle, rosige Hand an einem dunkleren Arm, dazwischen ein Ring aus Daz-Haut mit hartem Rand.

Hier wird der Ton aller Texel OHNE Netzfarbe (Hand, Handgelenk, Lücken im Unterarm) an den der Texel MIT Netzfarbe angeglichen — nur der Ton, die Zeichnung der Daz-Haut bleibt:

1. Daz-Haut = belegte Texel ohne HD-Farbe (`hd`, die Herkunftskarte der Kachel `meshfigur_herkunft_<k>.png`); ohne Herkunftskarte: die Texel mit Handgewicht > 0,5 (`Handhaut.masken`).
   Bezug = belegte Texel mit HD-Farbe am Unterarm (Handgewicht < 0,05, Unterarmgewicht > 0,5).
2. Je Kanal, linear: die Tiefpassfarbe (Gauß `SIGMA_PX`, nur über die jeweiligen Texel gemittelt) des Bezugs durch die der Daz-Haut — das Verhältnis gilt dort, wo beide nahe sind (am Handgelenk), und fällt
   in der Tiefe der Hand auf das Verhältnis der Mittelwerte beider Flächen zurück.
3. Nur die Daz-Haut wird mit diesem Verhältnis multipliziert (Rand der Maske 3 px weich). Die Texel mit Netzfarbe bleiben — die Farbe am Handgelenk trifft so von beiden Seiten denselben Ton.

Kein Ton ohne Bezug: fehlt die Hand oder der Unterarm (Aufträge ohne Arme), bleibt das Bild, wie es ist.
"""

import numpy as np

__all__ = ['Standhandangleich']


class Standhandangleich:
    #: Tiefpass der Töne in Texeln der Kachel (2048²) — groß genug, dass die Zeichnung (Adern, Haare, Falten) nicht mitgerechnet wird, klein genug für den Verlauf am Handgelenk.
    SIGMA_PX = 40.0
    #: Mindestzahl Texel je Fläche, ab der ein Verhältnis gilt.
    MINDEST = 400
    #: Das Verhältnis wird auf diese Grenzen gekappt (ein Ton um mehr als 40 % daneben ist ein Fehler der Maske, nicht der Haut).
    GRENZEN = (0.6, 1.6)
    #: Ab diesem Gewicht des Bezugs-Tiefpasses gilt das örtliche Verhältnis ganz; darunter mischt das Verhältnis der Mittelwerte dazu.
    ORT_AB = 0.05

    @staticmethod
    def _linear(c):
        return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

    @staticmethod
    def _srgb(c):
        c = np.clip(c, 0.0, 1.0)
        return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)

    @classmethod
    def flaechen(cls, masken, hd=None):
        """`(daz, bezug)` — Boolesche Felder: die Texel, deren Ton angeglichen wird, und die, nach denen er sich richtet."""
        hand_w, unter_w, belegt = masken[..., 0], masken[..., 1], masken[..., 2] > 0.5
        arm = belegt & (hand_w < 0.05) & (unter_w > 0.5)
        if hd is not None and hd.shape == belegt.shape:
            return belegt & ~hd, arm & hd
        return belegt & (hand_w > 0.5), arm

    @classmethod
    def faktor(cls, lin, masken, hd=None):
        """`(H, W, 3)` Faktor (linear) für die Daz-Haut, 1 sonst — oder None, wenn eine der beiden Flächen fehlt. `lin`: die Kachel linear (H, W, 3); `masken`: (H, W, 3) Hand-, Unterarmgewicht, belegt."""
        from scipy import ndimage

        daz, bezug = cls.flaechen(masken, hd)
        if int(daz.sum()) < cls.MINDEST or int(bezug.sum()) < cls.MINDEST:
            return None
        gross = np.clip(lin[bezug].mean(axis=0) / np.maximum(lin[daz].mean(axis=0), 1e-6), *cls.GRENZEN)
        # Tiefpass je Fläche, nur über ihre Texel (normierte Faltung) — auf einem Viertel der Kante gerechnet (Zehntelsekunden statt Sekunden).
        schritt = 4
        sigma = cls.SIGMA_PX / schritt

        def tief(m):
            w = m[::schritt, ::schritt].astype(np.float64)
            nenner = ndimage.gaussian_filter(w, sigma)
            kanaele = [ndimage.gaussian_filter(lin[::schritt, ::schritt, c] * w, sigma) for c in range(3)]
            return np.stack(kanaele, axis=-1) / np.maximum(nenner, 1e-9)[..., None], nenner

        farbe_b, gewicht_b = tief(bezug)
        farbe_d, gewicht_d = tief(daz)
        ort = np.clip(farbe_b / np.maximum(farbe_d, 1e-6), *cls.GRENZEN)
        trauen = np.clip(np.minimum(gewicht_b, gewicht_d) / cls.ORT_AB, 0.0, 1.0)[..., None]
        klein = trauen * ort + (1.0 - trauen) * gross
        f = np.stack([ndimage.zoom(klein[..., c], schritt, order=1)[:lin.shape[0], :lin.shape[1]] for c in range(3)], axis=-1)
        weich = ndimage.gaussian_filter(daz.astype(np.float64), 3.0)[..., None]
        return 1.0 + (f - 1.0) * weich

    #: Breite des Streifens (Texel) beiderseits der Grenze zwischen Netzfarbe und Daz-Haut, der neu eingemalt wird, und der Abstand zum Inselrand, den er hält.
    NAHT_PX = 7
    INSELRAND_PX = 10

    @classmethod
    def naht(cls, srgb8, belegt, hd):
        """Die Grenze zwischen Netzfarbe und Daz-Haut ohne ihre dunkle Kontur: der Streifen `NAHT_PX` beiderseits der Grenze (innerhalb der Inseln, `INSELRAND_PX` vom Rand weg) wird aus der Umgebung
        eingemalt (Telea, wie `G9texturbacken.luecken_malen`). Am Handgelenk lief dort ein dunkler Ring um die Hand — die Kontur der HD-Schicht, die als Naht an der Hand stand. `srgb8`: (H, W, 3) uint8."""
        import cv2
        from scipy import ndimage

        grenze = ndimage.binary_dilation(hd, iterations=cls.NAHT_PX) & ndimage.binary_dilation(~hd, iterations=cls.NAHT_PX)
        innen = ndimage.binary_erosion(belegt, iterations=cls.INSELRAND_PX)
        maske = (grenze & innen).astype(np.uint8)
        if int(maske.sum()) < 50:
            return srgb8
        # Das Weiß außerhalb der Inseln darf nicht in die Naht ziehen: dort steht für die Rechnung die nächste Farbe der Insel.
        _abstand, (iy, ix) = ndimage.distance_transform_edt(~belegt, return_indices=True)
        grund = np.where(belegt[..., None], srgb8, srgb8[iy, ix])
        neu = cv2.inpaint(np.ascontiguousarray(grund), maske, 4, cv2.INPAINT_TELEA)
        return np.where(maske[..., None] > 0, neu, srgb8)

    @classmethod
    def anwenden(cls, bild, masken, hd=None):
        """PIL-Bild der Armkachel (sRGB) → PIL-Bild mit der Daz-Haut im Ton der Netzfarbe und ohne dunkle Naht an der Grenze; das Bild selbst, wenn es nichts anzugleichen gibt. `masken` (und `hd`, Bool) haben die Größe des Bilds (sonst wird nichts getan)."""
        from PIL import Image

        arr = np.asarray(bild.convert('RGB'), dtype=np.float64) / 255.0
        if masken is None or masken.shape[:2] != arr.shape[:2]:
            return bild
        lin = cls._linear(arr)
        f = cls.faktor(lin, masken, hd)
        if f is None:
            return bild
        aus = np.rint(cls._srgb(lin * f) * 255.0).astype(np.uint8)
        if hd is not None and hd.shape == arr.shape[:2]:
            aus = cls.naht(aus, masken[..., 2] > 0.5, hd)
        return Image.fromarray(aus, 'RGB')

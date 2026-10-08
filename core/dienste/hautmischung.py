# -*- coding: utf-8 -*-
"""Hautmischung — die Fotohaut nahtlos in die gebackene Kachel des Netzes einarbeiten (05.10.2026).

Edgar (Auftrag 2026.10.04.21.41.43, Iteration 1): „Die Beine und Arme haben ‚Nähte' zwischen einzelnen Teilen", „Texturprobleme auch bei der Hand". Die Kachel der Fotohaut war bis dahin die gebackene Kachel des Netzes
(TRELLIS-Malerei) mit der Projektion der Fotos darüber, gewichtet mit der Deckung — gesehen an `hautfoto_1003.jpg` / `_1004.jpg` (Iteration 1): Flecken aus Foto-Haut mit hartem Rand auf einer anderen Grundfarbe
(Tonsprung am Rand, am Arm ein Rechteck mit dunkler Kante), senkrechte Bänder zwischen den Ansichten an den Beinen, eine helle Rosahaut an den Händen (dort liegen Hand und Finger der Figur nicht auf denen des Fotos), und die
dünne dunkle Linie unterm Saum der Hose, die schon in der gebackenen Kachel stand. Drei Dinge, drei Mittel:

1. **Ton angleichen statt überblenden:** Die Tiefpassfarbe (Gauß `TIEF_PX`) der Fotohaut geteilt durch die der gebackenen Kachel unter denselben Texeln ist der Ton-Faktor dort, wo das Foto sitzt; er wird per normierter
   Faltung (Gauß `AUSBREITUNG_PX`) in die ganze Kachel getragen und multipliziert die gebackene Haut — am Rand der Fotoflecken haben beide denselben Ton, und die gebackene Haut ist überall im Ton der Fotos (Hand
   und Lücken auch). Außerhalb der Reichweite gilt der Mittelwert aller Faktoren.
2. **Zwei Bänder:** Der Ton (tiefe Frequenzen) geht von der Fotohaut zur angeglichenen gebackenen Haut über, die Zeichnung (hohe Frequenzen: Haare, Poren, Adern) kommt von der Fotohaut, wo sie sitzt, und zu `ZEICHNUNG_GRUND`
   von der gebackenen sonst; der Übergang ist weich (Gauß `UEBERGANG_PX`), also ohne Kante.
3. **Fremde Pixel raus:** Die gebackene Kachel verliert dünne dunkle und helle Linien (Schwarz-/Weiß-Hut-Filter `LINIE_PX`, mit Telea eingemalt) — die Linie unterm Hosensaum ist eine solche. Nur dort, wo das Foto nicht sitzt:
   eine Linie im Foto ist ein Haar.

Hände (und Füße, Gesicht — alles, was `ohne_foto` meldet) bekommen nie Fotofarbe: Die Pose des Fotos liegt auf der Hand der Figur nie genau, die Farbe käme verschmiert; sie tragen die gebackene Haut im Ton der Fotohaut des
Unterarms (Punkt 1).

Gerechnet wird linear, auf der Rasterkante der Fotohaut (`Koerperfotoprojektion.RASTER`); die Differenz (neu − gebacken) wird auf die Kachelgröße gebracht und zur gebackenen Kachel addiert — deren feine Zeichnung bleibt.
"""

import numpy as np

__all__ = ['Hautmischung']


class Hautmischung:
    #: Tiefpass für den Ton, Ausbreitung des Ton-Faktors und Breite des Übergangs, in Texeln des Rasters (1 Texel ≈ 1,1 mm).
    TIEF_PX = 10.0
    AUSBREITUNG_PX = 50.0
    UEBERGANG_PX = 7.0
    #: Der Ton-Faktor wird auf diese Grenzen gekappt (mehr wäre ein Fehler der Zuordnung, nicht des Tons).
    GRENZEN = (0.55, 1.8)
    #: Ab diesem Gewicht der Ausbreitung (Anteil Texel mit Foto im Umkreis) gilt der örtliche Ton-Faktor ganz; darunter mischt der Mittelwert dazu.
    ORT_AB = 0.08
    #: Wie viel der Zeichnung der gebackenen Haut bleibt, wo das Foto nicht sitzt (die Flecken der Netzmalerei wirken als Zeichnung, sind keine).
    ZEICHNUNG_GRUND = 0.6
    #: Linien dünner als `LINIE_PX` Texel (Hut-Filter) und kontrastreicher als `LINIE_KONTRAST` (linear) verschwinden aus der gebackenen Kachel.
    LINIE_PX = 9
    LINIE_KONTRAST = 0.06

    @staticmethod
    def _linear(c):
        return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

    @staticmethod
    def _srgb(c):
        c = np.clip(c, 0.0, 1.0)
        return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)

    @staticmethod
    def tief(wert, gewicht, sigma):
        """Tiefpass (Gauß `sigma` Texel) über die Texel mit `gewicht`, normiert → `(wert (H, W, 3), anteil (H, W))`; auf einem verkleinerten Bild gerechnet."""
        import cv2

        hoehe, breite = gewicht.shape
        schritt = max(1, int(sigma // 5))
        klein = (max(1, breite // schritt), max(1, hoehe // schritt))
        zaehler = cv2.resize((wert * gewicht[..., None]).astype(np.float32), klein, interpolation=cv2.INTER_AREA)
        nenner = cv2.resize(gewicht.astype(np.float32), klein, interpolation=cv2.INTER_AREA)
        s = max(sigma / schritt, 0.5)
        zaehler = cv2.GaussianBlur(zaehler, (0, 0), s)
        nenner = cv2.GaussianBlur(nenner, (0, 0), s)
        aus = cv2.resize(zaehler / np.maximum(nenner, 1e-6)[..., None], (breite, hoehe), interpolation=cv2.INTER_LINEAR)
        return aus.astype(np.float64), cv2.resize(nenner, (breite, hoehe), interpolation=cv2.INTER_LINEAR).astype(np.float64)

    @classmethod
    def ohne_linien(cls, grund, insel, foto):
        """Die gebackene Kachel (linear, (H, W, 3)) ohne dünne dunkle/helle Linien dort, wo das Foto nicht sitzt (`foto` Bool): Hut-Filter auf der Helligkeit, Telea auf den Pixeln darunter."""
        import cv2

        y = (grund @ np.array([0.2126, 0.7152, 0.0722])).astype(np.float32)
        kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (cls.LINIE_PX, cls.LINIE_PX))
        auffaellig = (cv2.morphologyEx(y, cv2.MORPH_BLACKHAT, kern) > cls.LINIE_KONTRAST) | (cv2.morphologyEx(y, cv2.MORPH_TOPHAT, kern) > cls.LINIE_KONTRAST)
        innen = cv2.erode(insel.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        maske = (auffaellig & innen & ~foto).astype(np.uint8)
        if int(maske.sum()) < 20:
            return grund, 0
        maske = cv2.dilate(maske, np.ones((3, 3), np.uint8))
        bild = np.rint(cls._srgb(grund) * 255.0).astype(np.uint8)
        neu = cv2.inpaint(np.ascontiguousarray(bild), maske, 3, cv2.INPAINT_TELEA)
        return np.where(maske[..., None] > 0, cls._linear(neu / 255.0), grund), int(maske.sum())

    @classmethod
    def mischen(cls, grund, insel, foto, deckung, massstab=1.0):
        """`grund` (H, W, 3) sRGB 0…1 — die gebackene Kachel auf Rasterkante; `insel` (H, W) Bool — Texel der Kachel, die zum Körper gehören; `foto` (H, W, 3) sRGB — Fotofarbe (gefüllt, überall definiert);
        `deckung` (H, W) 0…1 — wie sehr das Foto zählt (0 auch für Hände) → `(neu (H, W, 3) sRGB, Bericht)`; ohne Fotodeckung bleibt der Grund (nur ohne Linien).
        `massstab`: so viel kleiner ist ein Texel dieser Kachel als die Körperkacheln (Kopf: ~3,5) — Tiefpass, Ausbreitung und Übergang wachsen in Texeln mit (die Längen sind in Millimetern gemeint)."""
        from scipy import ndimage

        tief_px, ausbreitung_px, uebergang_px = cls.TIEF_PX * massstab, cls.AUSBREITUNG_PX * massstab, cls.UEBERGANG_PX * massstab

        g, f = cls._linear(np.asarray(grund, dtype=np.float64)), cls._linear(np.asarray(foto, dtype=np.float64))
        sitzt = deckung > 0.3
        g, entfernt = cls.ohne_linien(g, insel, sitzt)
        bericht = {'linien_texel': entfernt, 'foto_anteil': round(float(sitzt[insel].mean()) if insel.any() else 0.0, 3)}
        if int(sitzt.sum()) < 400:
            return cls._srgb(g), bericht
        # 1. Ton: Fotohaut / gebackene Haut unter denselben Texeln, in die ganze Kachel getragen
        gew = (deckung * sitzt).astype(np.float64)
        foto_tief, _anteil = cls.tief(f, gew, tief_px)
        grund_tief, _a2 = cls.tief(g, gew, tief_px)
        verhaeltnis = np.clip(foto_tief / np.maximum(grund_tief, 1e-4), *cls.GRENZEN)
        mittel = np.clip(np.median(verhaeltnis[sitzt], axis=0), *cls.GRENZEN)
        ort, anteil = cls.tief(verhaeltnis, sitzt.astype(np.float64), ausbreitung_px)
        trauen = np.clip(anteil / cls.ORT_AB, 0.0, 1.0)[..., None]
        faktor = np.clip(trauen * ort + (1.0 - trauen) * mittel, *cls.GRENZEN)
        angeglichen = g * faktor
        # 2. Zwei Bänder
        alle = insel.astype(np.float64)
        a, _n = cls.tief(angeglichen, alle, tief_px)
        foto_zeichnung = np.where(sitzt[..., None], f - foto_tief, 0.0)
        grund_zeichnung = angeglichen - a
        weich = np.clip(ndimage.gaussian_filter(deckung * sitzt, uebergang_px), 0.0, 1.0)[..., None]
        ton = weich * foto_tief + (1.0 - weich) * a
        zeichnung = weich * foto_zeichnung + (1.0 - weich) * cls.ZEICHNUNG_GRUND * grund_zeichnung
        neu = np.clip(ton + zeichnung, 0.0, 1.0)
        bericht.update(faktor_mittel=[round(float(c), 3) for c in mittel], faktor_klein=round(float(faktor[insel].min()), 3), faktor_gross=round(float(faktor[insel].max()), 3))
        return cls._srgb(np.where(insel[..., None], neu, g)), bericht

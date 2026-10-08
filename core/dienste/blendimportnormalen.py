# -*- coding: utf-8 -*-
"""Blendimportnormalen — falsch getroffene Stellen der gebackenen Normalenkarte flachlegen (08.10.2026).

Das Backen („Selected to Active", `blendbacken.py`) wirft je Texel der Genesis-Figur einen Strahl auf das Original. Wo beide
Flächen nicht übereinanderliegen und die Stelle konkav ist — das Dekolleté, wo sich die Brüste berühren, der Schritt, die
Fingerzwischenräume — trifft er manchmal das falsche Stück (die andere Brust, die Nachbarfläche, eine Rückseite). Die
Tangentenraum-Normale dieses Treffers steht dann weit schief zur Figur.

Gemessen am ersten Import (2026.10.08.11.28.06, `normalen_kippung.py`, Kachel 1002, Mitte des Rumpfs): Brusthöhe 1,00–1,25 m
Kippung im Mittel 6–7° (höchstens 34°), dagegen 1,30–1,40 m (Dekolleté) 26° bzw. 38° im Mittel, bis 168°, 976 Punkte über 45°.
Das beleuchtete sich als weißer „Pflaster"-Fleck (Edgar: „was ist das Pflaster zwischen den Brüsten von cute girl?"). Nägel
(Kachel 1005): Median 32°, Kopf (1001) 3,8 %, Hände (1004) 3,2 % der Texel über 30°.

Der Median der belegten Texel liegt bei 5–7° (gemessen, alle Hautkacheln). Die Grenze von 50° ist eine Setzung, kein Messwert:
Was darüber liegt, gilt als falscher Treffer, das Texel und sein Rand (`RAND_PX`) werden flach (die Normale der Figur selbst
gilt dann). Je Kachel steht der Anteil der geänderten Texel im Bericht (`normalen_flach`).

Gemessen im zweiten Import (2026.10.08.19.31.50, 50°, derselbe Körper mit Fingersegmenten): 1001 2,8 %, 1002 1,2 %, 1003 0,8 %,
1004 2,7 % der Texel geändert. Bei einem ANDEREN Modell ist die Grenze nicht gemessen — deshalb wählbar (Dialog „Normalen säubern
ab", `Blendimporteinstellungen`) und `WARN_PROZENT` meldet eine Kachel, in der mehr als das Dreifache des gemessenen Höchstwerts
fällt (Setzung): dort stimmt die Grenze oder das Backen nicht.
"""

import math

import numpy as np

__all__ = ['Blendimportnormalen']


class Blendimportnormalen:
    FLACH = (128, 128, 255)
    #: Grad zur flachen Normale (0, 0, 1), ab denen ein Texel als falscher Treffer gilt.
    GRENZE_GRAD = 50.0
    #: So viele Pixel um einen falschen Treffer werden mit flachgelegt (Übergang).
    RAND_PX = 3
    BAND = 512
    #: Ab diesem Anteil geänderter Texel einer Kachel (in %) meldet der Import eine Warnung.
    WARN_PROZENT = 8.0

    @classmethod
    def falsche(cls, normal, leer=None, grad=None):
        """Maske (H, W) der Texel mit Kippung über `grad` (Vorgabe `GRENZE_GRAD`), ohne `leer` — bandweise (8192² in
        float32 wäre ein Gigabyte)."""
        grenze = math.cos(math.radians(cls.GRENZE_GRAD if grad is None else grad))
        maske = np.zeros(normal.shape[:2], dtype=bool)
        for oben in range(0, normal.shape[0], cls.BAND):
            band = normal[oben:oben + cls.BAND].astype(np.float32) / 127.5 - 1.0
            laenge = np.linalg.norm(band, axis=2)
            maske[oben:oben + cls.BAND] = band[..., 2] < grenze * np.maximum(laenge, 1e-6)
        if leer is not None:
            maske &= ~leer
        return maske

    #: Gröber als so viele Pixel (bei 8192 px je Kachel) ist FORM, nicht Feindetail — Poren und Haut sind Pixel breit, die
    #: Formdifferenz zwischen Figur und Original (Brust, Scham, Lippen) reicht über Hunderte.
    FORM_PX = 24.0

    @classmethod
    def feindetail(cls, normal, leer=None, sigma_px=None, teiler=4):
        """Die Karte nur mit ihrem Feindetail (`FORM_PX`): das großflächige Neigungsfeld fällt weg. Die gebackene Karte trägt
        auch den Unterschied der FORM — wo die Figur vom Original abweicht (gemessen 08.10.2026: Scham, bis 22 mm), kippt sie
        die Normalen großflächig, und im Licht steht eine Form, die die Fläche nicht hat. `leer` (Fehlstellen) zählt nicht in
        die Mittelung und bleibt flach; die Eingabe bleibt unverändert."""
        from scipy import ndimage

        hoehe, breite = normal.shape[:2]
        if hoehe % teiler or breite % teiler:
            teiler = 1
        sigma = (cls.FORM_PX if sigma_px is None else float(sigma_px)) / teiler
        gueltig = np.ones((hoehe, breite), dtype=np.float32) if leer is None else (~leer).astype(np.float32)
        x = normal[..., 0].astype(np.float32) / 127.5 - 1.0
        y = normal[..., 1].astype(np.float32) / 127.5 - 1.0
        z = np.maximum(normal[..., 2].astype(np.float32) / 127.5 - 1.0, 0.05)
        tx, ty = x / z, y / z

        def tief(feld):
            """Gewichtetes Mittel der gültigen Neigung, auf `teiler` verkleinert, geglättet und wieder in voller Größe."""
            klein = (feld * gueltig).reshape(hoehe // teiler, teiler, breite // teiler, teiler).mean(axis=(1, 3))
            gewicht = gueltig.reshape(hoehe // teiler, teiler, breite // teiler, teiler).mean(axis=(1, 3))
            mittel = ndimage.gaussian_filter(klein, sigma) / np.maximum(ndimage.gaussian_filter(gewicht, sigma), 1e-3)
            return ndimage.zoom(mittel, teiler, order=1) if teiler > 1 else mittel

        hx = (tx - tief(tx)) * gueltig
        hy = (ty - tief(ty)) * gueltig
        laenge = np.sqrt(hx * hx + hy * hy + 1.0)
        neu = normal.copy()
        for kanal, wert in enumerate((hx / laenge, hy / laenge, 1.0 / laenge)):
            kodiert = np.clip(np.rint((wert + 1.0) * 127.5), 0, 255).astype(normal.dtype)
            if leer is not None:
                kodiert[leer] = cls.FLACH[kanal]
            neu[..., kanal] = kodiert
        return neu

    @classmethod
    def saeubern(cls, normal, leer=None, grad=None):
        """`(neue Karte, Anteil der geänderten Texel in %)` — `normal` (H, W, 3) uint8; ändert die Eingabe nicht."""
        from scipy import ndimage

        schlecht = cls.falsche(normal, leer, grad)
        if schlecht.any() and cls.RAND_PX:
            schlecht = ndimage.binary_dilation(schlecht, iterations=cls.RAND_PX)
        if leer is not None:
            schlecht &= ~leer
        neu = normal.copy()
        neu[schlecht] = cls.FLACH
        return neu, round(100.0 * float(schlecht.mean()), 3)

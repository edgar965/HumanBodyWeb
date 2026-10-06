# -*- coding: utf-8 -*-
"""Haarkappenbild — feines Strähnenrauschen um die Haarfarbe als Bild der Haarkappe (aus `Haarkappe.bild` herausgelöst, 05.10.2026: `haarkappe.py` wuchs über 300 Zeilen)."""

import numpy as np

__all__ = ['Haarkappenbild']


class Haarkappenbild:
    @staticmethod
    def schreiben(rgb, pfad, groesse, kontrast, straehne, samen):
        """Rauschen um die Haarfarbe (`rgb` 0–1, `groesse` Texel je Kante) als PNG nach `pfad` — in beiden Richtungen nahtlos (die UV wiederholt sich nicht, aber die Würfelabbildung kennt keine Naht)."""
        from PIL import Image
        from scipy import ndimage

        zufall = np.random.default_rng(samen)

        def rauschen(sigma_u, sigma_v):
            z = ndimage.gaussian_filter(zufall.standard_normal((groesse, groesse)), (sigma_v, sigma_u), mode='wrap')      # Zeilen = v
            return z / z.std()

        # Strähnen: schmal in u, lang in v (`straehne`) — die Würfelabbildung legt v an Hinterkopf, Seiten und Scheitel in die Wuchsrichtung (senkrecht bzw. vor–zurück). Nur feines Rauschen, gröbere Flecken
        # ließen die Dreiecke der Würfelabbildung als Facetten erkennen.
        feld = 0.8 * rauschen(0.7, straehne) + 0.2 * rauschen(2.0, 2.0)
        licht = 1.0 + kontrast * feld / feld.std()
        farbe = np.clip(np.asarray(rgb[:3], dtype=np.float64)[None, None, :] * licht[..., None], 0.0, 1.0)
        pfad.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(np.rint(farbe * 255.0).astype(np.uint8), 'RGB').save(pfad)
        return pfad

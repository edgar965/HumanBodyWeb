# -*- coding: utf-8 -*-
"""Haarfarbmessung — wie hell das Haar im Render gegen die Fotos erscheint (05.10.2026).

Edgar: „Das Haar in der Vorlage soll perfekt auf ein Haar aus Genesis umgebaut werden, inkl. Textur, Form, Farbe." Die Karten der Frisur rendern dunkler als ihre Tönung (Eigenschatten); `Haarumbau.KARTEN_HELL`
gleicht das aus, gemessen aber nur an Mavick Hair Style. Statt einer Wegwerf-Messung je Frisur misst jede Begutachtungsrunde das selbst: `Haarabgleich` rendert den Kopf je Ansicht auch in Farbe und legt hier die mittlere
Farbe des Haars im Foto neben die im Render — über die Pixel, in denen BEIDE Haar zeigen (Brauen, Hemd und Haut des Fotos zählen nicht mit), Rand abgezogen.
`befund['haarabgleich']['farbe']`: `{foto, render, verhaeltnis, pixel}` — `verhaeltnis` = Mittelwert Render ÷ Mittelwert Foto (1,0 = gleich hell; unter 1 = der Render ist zu dunkel).
"""

import numpy as np

__all__ = ['Haarfarbmessung']


class Haarfarbmessung:
    RAND = 3                       # Pixel, die vom Rand der gemeinsamen Haarfläche abgezogen werden (Übergang zu Haut und Hintergrund)
    MINDESTENS = 50                # weniger gemeinsame Haarpixel in einer Ansicht: keine Aussage

    @classmethod
    def ansicht(cls, render_rgb, foto_rgb, foto_haar, render_haar):
        """`(Pixel, Mittel Foto, Mittel Render)` (Farben 0…1) einer Ansicht — None bei zu wenigen gemeinsamen Haarpixeln. Alle Felder haben dieselbe Form (Pixel des Kopfausschnitts)."""
        from scipy.ndimage import binary_erosion
        beide = binary_erosion(np.asarray(foto_haar, dtype=bool) & np.asarray(render_haar, dtype=bool), iterations=cls.RAND)
        n = int(beide.sum())
        if n < cls.MINDESTENS:
            return None
        foto = np.asarray(foto_rgb, dtype=np.float64)[..., :3][beide].mean(axis=0) / 255.0
        render = np.asarray(render_rgb, dtype=np.float64)[..., :3][beide].mean(axis=0) / 255.0
        return n, foto, render

    @classmethod
    def auswerten(cls, ansichten):
        """Die Ansichten zusammen, nach Pixeln gewichtet → `{foto, render, verhaeltnis, pixel}` — None ohne messbare Ansicht."""
        liste = [a for a in ansichten if a]
        pixel = sum(n for n, _f, _r in liste)
        if not pixel:
            return None
        foto = sum(n * f for n, f, _r in liste) / pixel
        render = sum(n * r for n, _f, r in liste) / pixel
        return {'foto': [round(float(c), 3) for c in foto], 'render': [round(float(c), 3) for c in render],
                'verhaeltnis': round(float(render.mean() / max(float(foto.mean()), 1e-6)), 2), 'pixel': pixel}

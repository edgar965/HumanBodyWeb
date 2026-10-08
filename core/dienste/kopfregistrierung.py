# -*- coding: utf-8 -*-
"""Kopfregistrierung — das Gesicht des Vorderfotos auf das Modell ausrichten: Landmarken, Warp, Hautmaske (06.10.2026).

Ablauf (nur mit einem Vorderfoto, |Winkel| ≤ `VORN_BIS`, und erkanntem Gesicht auf Foto UND Render):

1. Kopf-Render des Modells in Flachfarben (Geometrie, keine gebackene Malerei — das Foto soll auf die Geometrie passen, nicht auf TRELLIS' Gesicht), `SAATEN` Mal, Landmarken je Render, gemittelt (Detektorrauschen, `Gesichtsmasse`).
2. Ausschnitt des vorbereiteten Fotos um den Kopf in voller Auflösung (die normierte Fläche der Note hat nur ein Drittel davon), auf Weiß gelegt; Landmarken des Ausschnitts.
3. `Kopfwarp` (Render → Foto) mit Glättung aus der Kreuzprüfung. Ist der Fehler an ungesehenen Landmarken größer als `FEHLER_MAX_MM`, gibt es KEINE Kopfprojektion: die gebackene Haut bleibt (lieber Malerei als ein verschobenes Gesicht).
4. `Kopfmarken.haut`: wo im Foto Gesichtshaut zählt (ohne Haar, Augen, Mundöffnung).

→ `(Kopfprojektion, bericht)` oder `(None, Grund)`; ein Fehler hält den Körper-Schritt nie auf.
"""

import logging

import numpy as np
from PIL import Image

from .kopfmarken import Kopfmarken
from .kopfprojektion import Kopfprojektion
from .kopfwarp import Kopfwarp

logger = logging.getLogger('core')

__all__ = ['Kopfregistrierung']


class Kopfregistrierung:
    VORN_BIS = 30.0
    SAATEN = (0, 1, 2, 3)
    GROESSE = (1024, 1024)
    RENDER = 'kopf_reg_render_s%d.png'
    FOTO = 'kopf_reg_foto.png'
    #: Ausschnitt des Fotos, als Anteil der Figurhöhe: links und rechts von der Rumpfmitte, über dem Scheitel, unter dem Scheitel.
    AUSSCHNITT = (0.17, 0.02, 0.25)
    #: Vorhersagefehler der Kreuzprüfung (Millimeter am Modell), ab dem kein Warp gilt.
    FEHLER_MAX_MM = 3.0
    #: Wie weit die Landmarken der Saaten streuen dürfen (Pixel des Renders), sonst ist der Detektor am Render unsicher.
    STREUUNG_MAX_PX = 6.0

    def __init__(self, ablage, render):
        self.ablage = ablage
        self.render = render

    def _foto(self, r, ziel):
        """Ausschnitt des Vorderfotos (`vorbereitet/<name>.png` mit Alpha, sonst das Original auf Weiß) → `(pfad, farbe (H, B, 3) 0…1, figur (H, B) Bool)` oder None — die Landmarken werden auf dem Ausschnitt selbst erkannt, der Warp zielt also schon auf seine Pixel."""
        from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
        from .iterationsbild import Iterationsbild
        stamm = r.datei.rsplit('.', 1)[0]
        vorbereitet = self.ablage.unter(Engine2d3dKleiderablage.VORBEREITET) / (stamm + '.png')
        if vorbereitet.is_file():
            with Image.open(vorbereitet) as bild:
                rgba = np.asarray(bild.convert('RGBA'))
            figur, rgb = rgba[..., 3] > 127, rgba[..., :3].astype(np.float32)
            alpha = rgba[..., 3:4].astype(np.float32) / 255.0
            rgb = rgb * alpha + 255.0 * (1.0 - alpha)
        else:
            with Image.open(self.ablage.unter(Engine2d3dKleiderablage.EINGANG) / r.datei) as bild:
                rgb = np.asarray(bild.convert('RGB'), dtype=np.float32)
            figur = (765.0 - rgb.sum(axis=2)) > Iterationsbild.WEISS_SCHWELLE
        abbildung = Iterationsbild.abbildung(figur)
        if abbildung is None:
            return None
        cx, y0, y1 = abbildung
        h = float(y1 - y0)
        links, oben, unten = self.AUSSCHNITT
        x_a, x_b = int(max(cx - links * h, 0)), int(min(cx + links * h, rgb.shape[1]))
        y_a, y_b = int(max(y0 - oben * h, 0)), int(min(y0 + unten * h, rgb.shape[0]))
        farbe = rgb[y_a:y_b, x_a:x_b]
        ziel.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(np.rint(farbe).astype(np.uint8)).save(ziel, compress_level=1)
        return ziel, farbe / 255.0, figur[y_a:y_b, x_a:x_b]

    def _render_marken(self, teile, winkel, aus):
        """Landmarken des Kopf-Renders (Pixel), über die Saaten gemittelt → `(marken (478, 2), streuung_px)` oder None."""
        from .fotolandmarken import Fotolandmarken
        pfade = [aus / (self.RENDER % s) for s in self.SAATEN]
        flach = [(t['punkte'], t['dreiecke'], t['farbe']) for t in teile]
        for saat, pfad in zip(self.SAATEN, pfade, strict=True):
            self.render.bild_kopf(flach, winkel, pfad, groesse=self.GROESSE, saat=saat)
        befunde = Fotolandmarken(self.ablage).holen(pfade)
        arten = [Kopfmarken.punkte(b['gesicht'], b['breite'], b['hoehe']) for b in (befunde.get(p.name) or {} for p in pfade) if b.get('gesicht')]
        if len(arten) < 2:
            return None
        arten = np.asarray(arten)
        mittel = arten.mean(axis=0)
        return mittel, float(np.sqrt(((arten - mittel) ** 2).sum(axis=2).mean()))

    def projektion(self, teile, referenzen, aus):
        """→ `(Kopfprojektion, bericht)` oder `(None, Grund)`; `teile` die gebauten Teile (alle, mit Haar — die Kamera hängt am höchsten Punkt, wie bei `Gesichtsmasse`)."""
        from .fotolandmarken import Fotolandmarken
        vorn = [r for r in referenzen if abs(float(r.winkel)) <= self.VORN_BIS]
        if not vorn:
            return None, 'kein Vorderfoto'
        r = min(vorn, key=lambda x: abs(float(x.winkel)))
        foto = self._foto(r, aus / self.FOTO)
        if foto is None:
            return None, 'keine Figur im Vorderfoto'
        pfad, farbe, figur = foto
        render = self._render_marken(teile, r.winkel, aus)
        bf = (Fotolandmarken(self.ablage).holen([pfad]).get(pfad.name) or {})
        if render is None or not bf.get('gesicht'):
            return None, 'kein Gesicht auf %s' % ('dem Render' if render is None else 'dem Foto')
        marken_render, streuung = render
        if streuung > self.STREUUNG_MAX_PX:
            return None, 'Landmarken des Renders streuen um %.1f px' % streuung
        marken_foto = Kopfmarken.punkte(bf['gesicht'], bf['breite'], bf['hoehe'])
        halb = 0.5 * self.render.KOPF_HOEHE
        mm_je_px = 1000.0 * 2.0 * halb / self.GROESSE[1]
        warp = Kopfwarp.passen(marken_render, marken_foto, mm_je_px=mm_je_px)
        if warp.fehler_mm is None or warp.fehler_mm > self.FEHLER_MAX_MM:
            return None, 'Warp zu ungenau (%s mm an ungesehenen Landmarken, Grenze %.1f)' % (
                None if warp.fehler_mm is None else round(warp.fehler_mm, 2), self.FEHLER_MAX_MM)
        scheitel = max(float(np.asarray(t['punkte'])[:, 1].max()) for t in teile)
        mitte = np.array([0.0, scheitel - self.render.KOPF_UNTER_SCHEITEL, 0.0])
        haut = Kopfmarken.haut(marken_foto, (farbe.shape[1], farbe.shape[0])) & figur
        projektion = Kopfprojektion(mitte, halb, self.GROESSE, warp)
        projektion.ansicht(r.winkel, (0.0, 0.0, 1.0), farbe, haut, np.ones(haut.shape, dtype=bool))
        bericht = {'foto': r.datei, 'winkel': float(r.winkel), 'fehler_mm': round(warp.fehler_mm, 2), 'fehler_px': round(warp.fehler_px, 2),
                   'glaettung': warp.glaettung, 'massstab': round(warp.massstab, 3), 'streuung_px': round(streuung, 2),
                   'haut_anteil': round(float(haut.mean()), 3)}
        logger.info('2D3D Kleider %s: Kopfregistrierung %s', getattr(self.ablage, 'kennung', ''), bericht)
        return projektion, bericht

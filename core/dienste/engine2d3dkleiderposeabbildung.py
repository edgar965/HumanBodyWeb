# -*- coding: utf-8 -*-
"""Engine2d3dKleiderposeabbildung — Gelenke am vorbereiteten Foto → Landmarken im Netz, dazu der Maßstab (11.10.2026, Schritt „pose").

Das Netz entsteht aus dem vorbereiteten Foto (Hunyuan3D/TRELLIS/Pixal3D: die Fotoseite nach +Z, Bild rechts = +X, Y oben — `mesh_fototextur.ACHSEN`). Seine Silhouette von vorn (x, −y) liegt deshalb auf der
Person des Fotos; die beiden Rahmen sind nur um Verschiebung und Streckung verschieden: die Kasten (Netzumriss ↔ Alphakasten der Person) werden aufeinander gelegt, `sx`/`sy` Pixel je Netzeinheit.
So wird aus jedem Gelenk-Pixel `(x, y)` im Netz; die Tiefe `z` ist die MITTE der Netzpunkte im Strahl (vorderste und hinterste Fläche gemeinsam, also im Körper). Ein Gelenk, dessen Strahl das Netz
verfehlt (Fuß am Bildrand, vom Gemälde abgeschnitten), wird auf die nächsten 400 Netzpunkte gezogen (`treffer` 4 statt 9). Gemessen an „Modigliani" (Probe E8): Silhouetten-IoU 0,72, 21 Landmarken, das Skelett
liegt in vier Ansichten im Körper; das Gegenstück zu den acht Orientierungen der Probe (`(x,-y)` siegte mit 0,72 gegen höchstens 0,44) bleibt als Prüfung: nur die vier Vorzeichenwahlen, und eine andere als
`(x,-y)` nur, wenn sie die IoU um `BESSER_UM` übertrifft (Spiegelung allein ist an einem symmetrischen Körper kein sicheres Maß).

Maßstab: SAM 3D Body schätzt den Abstand der Person zur Kamera (`Z = k3.z + cam_t.z`) bei Brennweite `f` (Pixel): Meter je Pixel = `Z / f` (nachgerechnet an der Probe: `u = f·X/Z + b/2` mit 0,0 px Abweichung).
Pixel je Netzeinheit sind `sqrt(sx · sy)`. Meter je Netzeinheit = Meter je Pixel × Pixel je Netzeinheit. Das ist SAMs Vorstellung von der Größe der Person (ein Formmodell für Erwachsene), keine Messung am Gemälde.
"""

import numpy as np
from PIL import Image, ImageDraw

__all__ = ['Engine2d3dKleiderposeabbildung']


class Engine2d3dKleiderposeabbildung:
    #: Raster (Pixel der längeren Seite) für den Silhouettenvergleich.
    RASTER = 320
    #: Vorzeichen der beiden Netzachsen (Bild rechts, Bild unten) — `(x,-y)` ist die Lage eines Netzes aus einem Foto.
    VARIANTEN = {'(x,-y)': (1.0, -1.0), '(-x,-y)': (-1.0, -1.0), '(x,y)': (1.0, 1.0), '(-x,y)': (-1.0, 1.0)}
    VORGABE = '(x,-y)'
    #: Eine andere Vorzeichenwahl gilt nur, wenn sie die Silhouetten-IoU um so viel übertrifft.
    BESSER_UM = 0.10
    #: Erst darunter werden die anderen Vorzeichenwahlen überhaupt gerechnet.
    GUT_GENUG = 0.60
    #: Netzpunkte im Strahl: Radius als Anteil der längeren Ausdehnung des Netzes in der Bildebene; weniger als `MIN_PUNKTE` heißt „außerhalb".
    RADIUS = 0.02
    MIN_PUNKTE = 5
    ZIEHEN_AUF = 400
    #: Tiefe eines Gelenks aus den Netzpunkten im Strahl: `mitte` = Mitte der Dicke (2.–98. Perzentil, im Körper — wie der Kopf der Datei es sagt), `median` = die ältere Wahl. Der Median liegt bei zwei
    #: Schichten (Vorder- und Rückseite des Rumpfs, fast gleich viele Punkte) in der dichteren: gemessen am Auftrag „Edgar" (12.10.2026) saßen die Hüften auf der Vorderseite (z +0,11 m, Gelenk der Figur ±0,00),
    #: die Schultern auf der Rückseite (−0,13 m, Gelenk −0,05) — 8–12 cm Tiefenfehler, die der Körper-Kette als Gelenkrest von 5–12 cm erschienen.
    TIEFE = 'mitte'

    def __init__(self, scan, alpha):
        """`scan`: `Meshfigurscan.laden(netz)` (Koordinaten wie die Körper-Kette sie lädt); `alpha`: Alphakanal des vorbereiteten Fotos (H × W)."""
        self.scan = scan
        self.person = np.asarray(alpha) > 127
        ys, xs = np.nonzero(self.person)
        if not len(xs):
            raise ValueError('Die Person im vorbereiteten Foto ist leer (Alpha)')
        self.kasten = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
        self.variante, self.iou, self.alle_iou = self.VORGABE, None, {}
        self.sx = self.sy = self.u0 = self.v0 = None
        self._punkte = self._baum = None
        self.ausrichten()

    # ------------------------------------------------------------ Ausrichtung

    def _uv(self, punkte, variante):
        vx, vy = self.VARIANTEN[variante]
        return vx * punkte[:, 0], vy * punkte[:, 1]

    def _strecken(self, variante):
        """`(u0, v0, sx, sy)`: Netzumriss auf den Alphakasten der Person gestreckt."""
        u, v = self._uv(self.scan.punkte, variante)
        x0, y0, x1, y1 = self.kasten
        return float(u.min()), float(v.min()), (x1 - x0) / float(np.ptp(u)), (y1 - y0) / float(np.ptp(v))

    def _iou(self, variante):
        h, b = self.person.shape
        k = self.RASTER / float(max(h, b))
        u0, v0, sx, sy = self._strecken(variante)
        u, v = self._uv(self.scan.punkte, variante)
        px, py = ((u - u0) * sx + self.kasten[0]) * k, ((v - v0) * sy + self.kasten[1]) * k
        bild = Image.new('L', (max(1, int(b * k)), max(1, int(h * k))), 0)
        zeichner = ImageDraw.Draw(bild)
        for f in self.scan.flaechen[::3]:
            zeichner.polygon([(px[f[0]], py[f[0]]), (px[f[1]], py[f[1]]), (px[f[2]], py[f[2]])], fill=255)
        netz = np.asarray(bild) > 0
        person = np.asarray(Image.fromarray(self.person.astype(np.uint8) * 255).resize(bild.size, Image.NEAREST)) > 0
        return float((netz & person).sum() / max(1, (netz | person).sum()))

    def ausrichten(self):
        """Wählt die Vorzeichenwahl (Vorgabe `(x,-y)`) und legt Streckung und Verschiebung fest."""
        self.alle_iou = {self.VORGABE: self._iou(self.VORGABE)}
        if self.alle_iou[self.VORGABE] < self.GUT_GENUG:
            for name in self.VARIANTEN:
                if name not in self.alle_iou:
                    self.alle_iou[name] = self._iou(name)
        beste = max(self.alle_iou, key=self.alle_iou.get)
        self.variante = beste if self.alle_iou[beste] >= self.alle_iou[self.VORGABE] + self.BESSER_UM else self.VORGABE
        self.iou = self.alle_iou[self.variante]
        self.u0, self.v0, self.sx, self.sy = self._strecken(self.variante)

    def auf_foto(self, punkte):
        """Netzpunkte (N, 3) → Pixel des vorbereiteten Fotos (N, 2) — Gegenstück zu `landmarken` (für die Kontrollbilder)."""
        u, v = self._uv(np.asarray(punkte, dtype=np.float64), self.variante)
        return np.stack([(u - self.u0) * self.sx + self.kasten[0], (v - self.v0) * self.sy + self.kasten[1]], axis=1)

    # ------------------------------------------------------------- Landmarken

    def _baum_und_punkte(self):
        if self._baum is None:
            from scipy.spatial import cKDTree
            self._punkte = self.scan.abtasten(300000)[0]
            self._baum = cKDTree(self._punkte[:, :2])
        return self._baum, self._punkte

    def landmarken(self, k2, namen, zuordnung, weglassen=()):
        """`(roh (33, 3), treffer (33,), liste)` — `k2` (70, 2) in Pixeln des vorbereiteten Fotos, `namen` die MHR-Namen, `zuordnung` {MediaPipe-Nummer: MHR-Name}.

        `roh` in den Koordinaten des GELADENEN Netzes (vor Einheit und Ausrichtung, NaN = kein Punkt) — so liest es `Meshfigurerkennungsschritt._von_hand`. `liste`: je Gelenk Pixel, Netzpunkt und Stand
        (`innen`, `ausserhalb` = auf die nächsten Netzpunkte gezogen, `weggelassen`)."""
        baum, punkte = self._baum_und_punkte()
        index = {n: i for i, n in enumerate(namen)}
        vx, vy = self.VARIANTEN[self.variante]
        ausdehnung = max(float(np.ptp(self.scan.punkte[:, 0])), float(np.ptp(self.scan.punkte[:, 1])))
        radius = self.RADIUS * ausdehnung
        roh, treffer, liste = np.full((33, 3), np.nan), np.zeros(33), []
        for mp, name in sorted(zuordnung.items()):
            px, py = (float(w) for w in k2[index[name]])
            eintrag = {'mp': mp, 'name': name, 'foto': [round(px, 1), round(py, 1)]}
            if name in weglassen:
                liste.append(dict(eintrag, stand='weggelassen'))
                continue
            u = (px - self.kasten[0]) / self.sx + self.u0
            v = (py - self.kasten[1]) / self.sy + self.v0
            xy = [u / vx, v / vy]
            nah = baum.query_ball_point(xy, radius)
            if len(nah) < self.MIN_PUNKTE:
                _, nn = baum.query(xy, k=self.ZIEHEN_AUF)
                ziel = punkte[nn].mean(0)
                roh[mp], treffer[mp], stand = ziel, 4.0, 'ausserhalb'
            else:
                z = punkte[nah, 2]
                roh[mp] = [xy[0], xy[1], float(np.median(z)) if self.TIEFE == 'median' else float((np.percentile(z, 2) + np.percentile(z, 98)) / 2.0)]
                treffer[mp], stand = 9.0, 'innen'
            liste.append(dict(eintrag, stand=stand, netz=[round(float(w), 4) for w in roh[mp]]))
        return roh, treffer, liste

    # ---------------------------------------------------------------- Maßstab

    def masstab(self, k3, cam_t, brennweite, namen, verwendet):
        """Meter je Netzeinheit aus SAMs Abstand zur Kamera (siehe Kopf der Datei) — über die Gelenke `verwendet` (MHR-Namen). `{faktor, meter_je_pixel, pixel_je_einheit, abstand_m, laengste_achse_m}`."""
        index = {n: i for i, n in enumerate(namen)}
        abstand = np.array([float(k3[index[n]][2]) + float(cam_t[2]) for n in verwendet], dtype=np.float64)
        abstand = abstand[abstand > 0.05]
        if not len(abstand) or not brennweite:
            raise ValueError('Kein Abstand aus SAM 3D Body — Maßstab nicht bestimmbar')
        meter_je_pixel = float(np.median(abstand)) / float(brennweite)
        pixel_je_einheit = float(np.sqrt(self.sx * self.sy))
        faktor = meter_je_pixel * pixel_je_einheit
        laengste = float(np.ptp(self.scan.punkte, axis=0).max())
        return {'faktor': faktor, 'meter_je_pixel': meter_je_pixel, 'pixel_je_einheit': pixel_je_einheit, 'abstand_m': float(np.median(abstand)),
                'laengste_achse_m': laengste * faktor}

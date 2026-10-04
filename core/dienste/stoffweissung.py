# -*- coding: utf-8 -*-
"""Stoffweissung — weißen Stoff aus der Fotoprojektion von den Flecken der anderen Ansichten befreien (04.10.2026).

Anlass (Edgar, 04.10.2026): „Hose um den Penis herum völlig falsch" — im Schritt und an den Oberschenkeln standen graue und hautfarbene Flecken auf der weißen Hose, am Innenschenkel
rote Schmierstreifen. Sie stammen aus der Fotoprojektion (`Engine2d3dKleiderfototextur`): Wo keine Ansicht den Stoff sauber sah, füllt der Mittelwert der Nachbarn mit Hautton und Schatten
(gemessen 04.10.2026 am Stand von Runde 54: Füllfarbe RGB(208,193,188), `ProjektTemp/_wegwerf/randy/hose/hose_mittel_vs_median.py`), und der rote Seitenstreifen der Außenseite wird
auf die Innenseite des Beins geschmiert (Bühne, Runde 55). Die Vorlage zeigt eine WEISSE Hose, den Streifen (rot, schwarz-weißes Karo) nur außen.

Regel 1: Ein Pixel, das FARBLOS (kleine Buntheit = Maximum − Minimum der Kanäle) und HELL ist, wird auf Weiß gezogen; Farbe (roter Streifen) und Dunkles (schwarze Karos) bleiben. Etwas
Helligkeitsstruktur des Fotos bleibt erhalten (`STRUKTUR`), damit der Stoff nicht wie Papier aussieht; die Falten kommen aus der Geometrie (`Hosenfalten`), nicht aus dem Bild.
Regel 2: Dreiecke, die nach INNEN zeigen (`innen`: Liste von UV-Dreiecken, siehe `Hosenfalten.innen`), werden im Bild ganz weiß — dort gehört nie ein Streifen hin.
Die Schwellen sind Augenmaß, am Randy-Stand nicht nachgemessen außer der Füllfarbe oben.

    weissen = Stoffweissung(uv_dreiecke)        # uv_dreiecke: (n, 3, 2) in glTF-UV (v von oben) oder None
    bild = weissen(bild)                        # PIL-Bild RGB → PIL-Bild RGB; `weissen.schluessel` für den Bildspeicher der GLB"""

import hashlib

import numpy as np

__all__ = ['Stoffweissung']


class Stoffweissung:
    WEISS = (240.0, 236.0, 228.0)       # warmes Weiß (die Vorlage hat Elfenbein, kein Blauweiß)
    BUNT_VON, BUNT_BIS = 45.0, 85.0     # unter BUNT_VON voll weißen, über BUNT_BIS gar nicht (roter Streifen, Hautton in der Fotofarbe)
    HELL_VON, HELL_BIS = 110.0, 170.0   # dunkler als HELL_VON bleibt (schwarze Karos), ab HELL_BIS voll
    STRUKTUR = 0.05                     # (0,12 am 04.10.2026 -> 0,05: das Fotorauschen blieb als Wollmuster auf den Waden) Anteil der Foto-Helligkeit, der als Stoffstruktur bleibt
    UNSCHAERFE = 2.0                    # Weichzeichnung (Pixel) der Innenmaske

    def __init__(self, innen_uv=None):
        self.innen_uv = None if innen_uv is None or not len(innen_uv) else np.asarray(innen_uv, dtype=np.float64)
        text = b'' if self.innen_uv is None else np.round(self.innen_uv, 4).tobytes()
        self.schluessel = hashlib.sha1(text).hexdigest()[:12] if text else 'ohne'

    @staticmethod
    def _weich(x):
        x = np.clip(x, 0.0, 1.0)
        return x * x * (3.0 - 2.0 * x)

    def _maske(self, groesse):
        """Innenmaske (H, B) 0…1: die UV-Dreiecke der Innenflächen, leicht weichgezeichnet."""
        from PIL import Image, ImageDraw, ImageFilter
        breite, hoehe = groesse
        maske = Image.new('L', groesse, 0)
        zeichner = ImageDraw.Draw(maske)
        for dreieck in self.innen_uv:
            zeichner.polygon([(float(u) * breite, float(v) * hoehe) for u, v in dreieck], fill=255)
        return np.asarray(maske.filter(ImageFilter.GaussianBlur(self.UNSCHAERFE)), dtype=np.float64) / 255.0

    def __call__(self, bild):
        from PIL import Image
        a = np.asarray(bild.convert('RGB'), dtype=np.float64)
        bunt = a.max(axis=2) - a.min(axis=2)
        hell = a @ np.array([0.299, 0.587, 0.114])
        w = (1.0 - self._weich((bunt - self.BUNT_VON) / (self.BUNT_BIS - self.BUNT_VON))) * self._weich((hell - self.HELL_VON) / (self.HELL_BIS - self.HELL_VON))
        struktur = (1.0 - self.STRUKTUR) + self.STRUKTUR * np.clip((hell - 150.0) / 90.0, 0.0, 1.0)
        if self.innen_uv is not None:
            m = self._maske(bild.size)
            w = np.maximum(w, m)
            struktur = struktur * (1.0 - m) + 0.96 * m          # die Innenseite ohne Fleckenrest: gleichmäßig helles Weiß
        ziel = np.asarray(self.WEISS)[None, None, :] * struktur[..., None]
        aus = a * (1.0 - w[..., None]) + ziel * w[..., None]
        return Image.fromarray(np.clip(np.rint(aus), 0, 255).astype(np.uint8), 'RGB')

# -*- coding: utf-8 -*-
"""Blendimportfarbangleich — die Ersatzfüllung einer Haut-Kachel im Ton der gebackenen Nachbarschaft (10.10.2026).

Wo kein Strahl das Original trifft, gilt die Kachel von „Mesh to 3D" (`Blendimporthaut._farbe_fuellen`): die Daz-Haut, auf EINEN
Hautton getönt. Neben den gebackenen Texeln steht sie in einem anderen Ton — Edgar (10.10.2026, „texturfehler bei der Hand bei
Modell asian"): an der Daumenwurzel der Kachel 1004 (Asian) lagen grünlich-beige Flecken der Ersatzkachel zwischen rosa Streifen des
Originals, dazu ein weißes Loch im Daumen. Gemessen an dieser Kachel: Die Ersatzkachel hat nur 2048² (die Kachel 8192²), ihr
weißer Hintergrund ist EIN Gebiet von 2,09 Mio. Pixeln, dazu 278 Gebiete unter 200 Pixeln — das sind Löcher in ihren Inseln.

1. `stopfen`: Löcher der Ersatzkachel (weiße Gebiete unter `TASCHE_MAX` Pixeln, samt ihrem hellen Hof) nehmen die Farbe des nächsten
   Pixels, das weder weiß noch hell ist. Der Hof ist das JPEG-Echo um das Weiß: ein Loch von 4 Pixeln hatte 237–250 in einem 6×6-Fleck
   um sich, in Haut von 115–135 — mit einem festen Radius von 4 blieben die Ränder stehen und die Füllung nahm ihre Farbe von ihnen.
2. `hinten`: Je Fehlstelle gilt die Ersatzfarbe PLUS ein Versatz, der sich aus dem Unterschied Gebackenes − Ersatz in der Nähe
   ergibt (gaußgewichtet, drei Maßstäbe von fein nach grob; wo ringsum nichts Gebackenes liegt, bleibt es bei der Ersatzfarbe). Das
   Feindetail der Ersatzkachel bleibt, nur ihr Ton wandert. Gerechnet wird auf dem Raster der Ersatzkachel.

Gemessen (Asian, Kachel 1004, `ProjektTemp/_wegwerf/import_serie/asian_angleich.py`, `asian_zeit.py`): der beige Keil und der gelbliche Fleck an der
Daumenwurzel sind im Ton der Umgebung, das weiße Loch im Daumen ist zu; 1,5 s Stopfen, 8,3 s Blöcke, 27,8 s Versatz, 16,3 s Anwenden je Kachel
(nebenher rechnete ein Import). Nicht angeglichen wird, was GEBACKEN ist: die rosa Streifen und der kleine rote Punkt in der Daumenwurzel sind
Treffer des Strahls auf dem Original — ob es falsche Treffer sind (Abstand der Figur zum Original dort), ist nicht geprüft.
"""

import numpy as np

__all__ = ['Blendimportfarbangleich']


class Blendimportfarbangleich:
    #: Ab dieser Helligkeit in allen Kanälen gilt ein Pixel der Ersatzkachel als weiß (außerhalb der Inseln).
    WEISS = 250
    #: Weiße Gebiete bis zu so vielen Pixeln (auf dem Raster der Ersatzkachel) sind Löcher in einer Insel, größere der Hintergrund.
    TASCHE_MAX = 200
    #: Der Hof eines Lochs: bis zu so viele Pixel (Ersatzraster) um das Weiß, soweit sie heller sind als `HELL` (kein Hautton der Ersatzkachel).
    HOF_PX = 6
    HELL = 215
    #: Gaußbreiten in Pixeln des Ersatzrasters (bei 2048² zu 8192² also das Vierfache in Kachelpixeln), fein zuerst.
    SIGMA = (3.0, 12.0, 48.0)
    #: Ab diesem Anteil gültiger Fläche im Gaußkern gilt der Versatz dieses Maßstabs (darunter fällt er ins gröbere).
    MIN_GEWICHT = 0.05
    #: Das Raster, auf dem der Versatz gerechnet wird (die Ersatzkachel von „Mesh to 3D" hat es selbst); kleinere Kacheln rechnen auf ihrem.
    GROB_PX = 2048
    #: Zeilen je Streifen beim Anwenden (hält den Speicher klein: 8192² × 3 als Gleitkomma wären 800 MB).
    STREIFEN = 512

    @classmethod
    def stopfen(cls, ersatz):
        """Die Ersatzkachel (H, W, 3) uint8 mit gestopften Löchern (nächster nicht weißer Pixel); die Eingabe bleibt, wie sie ist."""
        from scipy import ndimage

        helligkeit = ersatz.min(axis=2)
        weiss = helligkeit >= cls.WEISS
        # Achter-Nachbarschaft: eine Kerbe, die nur diagonal am Hintergrund hängt, ist kein Loch (mit Vierer-Nachbarschaft fraß die Füllung
        # Zacken in den Inselrand, gesehen an Asian 1004).
        marke, anzahl = ndimage.label(weiss, structure=np.ones((3, 3)))
        if anzahl == 0:
            return ersatz
        klein = np.flatnonzero(np.bincount(marke.ravel())[1:] <= cls.TASCHE_MAX) + 1
        tasche = np.isin(marke, klein)
        if not tasche.any():
            return ersatz
        # Um ein Loch liegt ein heller Hof (JPEG der Ersatzkachel: 237–250 in Haut von 115–135, bis 6 Pixel vom Weiß, gemessen an Asian
        # 1004, Daumen): er gehört mit zum Loch, sonst nähme die Füllung ihre Farbe von ihm. Der große weiße Hintergrund bleibt, wie er ist.
        hell = helligkeit >= cls.HELL
        loch = (tasche | (ndimage.binary_dilation(tasche, iterations=cls.HOF_PX) & hell)) & ~(weiss & ~tasche)
        zeile, spalte = ndimage.distance_transform_edt(hell | loch, return_distances=False, return_indices=True)
        neu = ersatz.copy()
        neu[loch] = ersatz[zeile[loch], spalte[loch]]
        return neu

    @staticmethod
    def _bloecke(farbe, gueltig, faktor):
        """`(Anteil gültig, Mittel der gültigen)` je `faktor × faktor`-Block: `(h, w)` und `(h, w, 3)` Gleitkomma."""
        hoehe, breite = gueltig.shape
        h, w = hoehe // faktor, breite // faktor
        anteil = np.zeros((h, w), dtype=np.float32)
        summe = np.zeros((h, w, 3), dtype=np.float32)
        schritt = faktor * max(1, 256 // faktor)
        for a in range(0, hoehe, schritt):
            b = min(a + schritt, hoehe)
            m = gueltig[a:b].astype(np.float32)
            zeilen = slice(a // faktor, b // faktor)
            anteil[zeilen] = m.reshape(-1, faktor, w, faktor).mean(axis=(1, 3))
            gewichtet = farbe[a:b].astype(np.float32) * m[..., None]
            summe[zeilen] = gewichtet.reshape(-1, faktor, w, faktor, 3).mean(axis=(1, 3))
        mittel = np.where(anteil[..., None] > 0, summe / np.maximum(anteil[..., None], 1e-6), 0.0)
        return anteil, mittel

    @classmethod
    def versatz(cls, ersatz, farbe, gueltig):
        """Der Versatz Gebackenes − Ersatz auf dem Raster der Ersatzkachel: `(h, w, 3)` Gleitkomma.

        `ersatz` (h, w, 3) uint8 auf dem groben Raster, `farbe` (H, W, 3) und `gueltig` (H, W) auf dem der Kachel (H = Vielfaches von h)."""
        from scipy import ndimage

        h, w = ersatz.shape[:2]
        faktor = farbe.shape[0] // h
        anteil, gebacken = cls._bloecke(farbe, gueltig, faktor)
        ok = (ersatz.min(axis=2) < cls.WEISS) & (anteil > 0)
        gewicht = np.where(ok, anteil, 0.0).astype(np.float32)
        unterschied = np.where(ok[..., None], gebacken - ersatz.astype(np.float32), 0.0)
        ergebnis = np.zeros((h, w, 3), dtype=np.float32)
        # Von grob nach fein überblenden: wo der feine Maßstab genug Fläche sieht, gilt er, sonst der gröbere.
        for sigma in sorted(cls.SIGMA, reverse=True):
            g = ndimage.gaussian_filter(gewicht, sigma)
            anteil_ok = np.clip(g / cls.MIN_GEWICHT, 0.0, 1.0)
            d = np.stack([ndimage.gaussian_filter(unterschied[..., k] * gewicht, sigma) for k in range(3)], axis=-1)
            d = d / np.maximum(g[..., None], 1e-6)
            ergebnis = ergebnis * (1.0 - anteil_ok[..., None]) + d * anteil_ok[..., None]
        return ergebnis

    @staticmethod
    def _hoch(versatz, zeilen, breite, faktor):
        """Der grobe Versatz für die Bildzeilen `zeilen` (slice) auf dem feinen Raster, bilinear."""
        h, w = versatz.shape[:2]
        y = np.arange(zeilen.start, zeilen.stop)
        fy = np.clip((y + 0.5) / faktor - 0.5, 0, h - 1)
        y0 = np.floor(fy).astype(int)
        y1 = np.minimum(y0 + 1, h - 1)
        wy = (fy - y0).astype(np.float32)[:, None, None]
        quer = versatz[y0] * (1 - wy) + versatz[y1] * wy                       # (Zeilen, w, 3)
        fx = np.clip((np.arange(breite) + 0.5) / faktor - 0.5, 0, w - 1)
        x0 = np.floor(fx).astype(int)
        x1 = np.minimum(x0 + 1, w - 1)
        wx = (fx - x0).astype(np.float32)[None, :, None]
        return quer[:, x0] * (1 - wx) + quer[:, x1] * wx

    @classmethod
    def hinten(cls, ersatz, farbe, ungueltig):
        """Die Ersatzfarbe für jede Fehlstelle im Ton der Nachbarschaft: `(H, W, 3)` uint8 auf dem Raster von `farbe`.

        `ersatz` ist die Ersatzkachel als Bild (PIL, RGB) beliebiger Größe, `farbe` die gebackene Kachel (H, W, 3) uint8, `ungueltig`
        (H, W) die Fehlstellen und ihr Saum. Nur die Fehlstellen werden verändert; weißer Hintergrund bleibt weiß."""
        from PIL import Image

        hoehe, breite = farbe.shape[:2]
        grob = cls.stopfen(np.asarray(ersatz.convert('RGB')))
        faktor = max(1, hoehe // cls.GROB_PX)
        while hoehe % faktor or breite % faktor:
            faktor -= 1
        if grob.shape[:2] != (hoehe // faktor, breite // faktor):
            grob = np.asarray(Image.fromarray(grob).resize((breite // faktor, hoehe // faktor), Image.LANCZOS))
        versatz = cls.versatz(grob, farbe, ~ungueltig)
        voll = np.asarray(Image.fromarray(grob).resize((breite, hoehe), Image.LANCZOS)).copy()
        for a in range(0, hoehe, cls.STREIFEN):
            zeilen = slice(a, min(a + cls.STREIFEN, hoehe))
            stueck = voll[zeilen]
            stelle = ungueltig[zeilen] & (stueck.min(axis=2) < cls.WEISS)
            if not stelle.any():
                continue
            d = cls._hoch(versatz, zeilen, breite, faktor)
            stueck[stelle] = np.clip(stueck[stelle].astype(np.float32) + d[stelle], 0, 255).astype(np.uint8)
        return voll

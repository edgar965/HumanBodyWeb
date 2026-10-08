# -*- coding: utf-8 -*-
"""Kopfmarken — die Gruppen der 478 FaceLandmarker-Punkte (MediaPipe) und die Masken, die daraus im FOTO entstehen (06.10.2026).

Edgar zur Kopfkachel (1001) von „Edgar - 7": Die gebackene Haut des Kopfes ist TRELLIS' Malerei — braun, mit dem Mund eines anderen Gesichts, orangen Punkten in den Nasenlöchern. Die Fotos als Quelle gab es für den Kopf nie
(`Koerperfotoprojektion.AUSGENOMMEN`): Fassung 1 verschob Augen, Brauen und Mund um Millimeter. Die Gesichter von Foto und Modell sind verschieden gebaut (Augenhöhe, Nase: bis 14 mm Unterschied gemessen an der Kopftafel) —
darum richtet `Kopfwarp` das FOTO nach den Landmarken auf das Modell aus, und diese Klasse sagt, wo im Foto Haut zählt:

* `haut`: Gesichtsoval (Landmarken-Umriss), nach innen verkleinert, die Stirn unter der Haargrenze abgeschnitten — Haar im Foto ist keine Haut;
* ohne die Augenöffnungen (das Modell hat eigene Augäpfel dahinter) und ohne die Mundöffnung (Zähne, Zunge sind eigene Teile).

Die Nummern sind die Umrissketten von MediaPipe (`face_mesh_connections`); an Foto und Render gezeichnet geprüft (`ProjektTemp/_wegwerf/edgar/kopf_reg_probe.py`).
"""

import numpy as np
from PIL import Image, ImageDraw

__all__ = ['Kopfmarken']


class Kopfmarken:
    OVAL = (10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
            172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109)
    AUGE_LINKS = (263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466)
    AUGE_RECHTS = (33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246)
    MUND_INNEN = (78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95)
    BRAUE_LINKS = (276, 283, 282, 295, 285, 300, 293, 334, 296, 336)
    BRAUE_RECHTS = (46, 53, 52, 65, 55, 70, 63, 105, 66, 107)
    #: Stirn 10, Kinn 152 — die Gesichtshöhe, an der alle Abstände hängen.
    STIRN, KINN = 10, 152
    #: Das Oval schrumpft um diesen Anteil der Gesichtshöhe (Rand: Haarsaum, Schatten am Ohr, Bartkante).
    OVAL_RAND = 0.035
    #: Die Stirn zählt erst ab diesem Anteil des Weges von der oberen Brauenkante zum Stirnpunkt (10): darüber liegt oft Haar.
    STIRN_BIS = 0.45
    #: Augen und Mundöffnung wachsen um diesen Anteil der Gesichtshöhe (Lider, Wimpern, Lippenrand).
    AUGEN_RAND = 0.02
    MUND_RAND = 0.012

    @staticmethod
    def punkte(gesicht, breite, hoehe, ursprung=(0.0, 0.0)):
        """`gesicht`: 478 × (x, y) in Bildanteilen eines Bildes `breite` × `hoehe` px → (478, 2) in Pixeln, um `ursprung` verschoben (Ausschnitt im größeren Bild)."""
        p = np.asarray([[float(q[0]), float(q[1])] for q in gesicht], dtype=np.float64)
        return p * np.array([float(breite), float(hoehe)]) - np.asarray(ursprung, dtype=np.float64)

    @classmethod
    def hoehe(cls, p):
        """Gesichtshöhe Stirn – Kinn in Pixeln."""
        return float(np.hypot(*(p[cls.STIRN] - p[cls.KINN])))

    @staticmethod
    def _flaeche(punkte, groesse):
        """Bool-Maske `(hoehe, breite)` des Vielecks `punkte` (N, 2)."""
        bild = Image.new('L', (int(groesse[0]), int(groesse[1])), 0)
        ImageDraw.Draw(bild).polygon([(float(x), float(y)) for x, y in punkte], fill=255)
        return np.asarray(bild) > 0

    @staticmethod
    def _wachsen(maske, radius):
        from scipy import ndimage
        return ndimage.distance_transform_edt(~maske) <= max(float(radius), 1.0)

    @staticmethod
    def _schrumpfen(maske, radius):
        from scipy import ndimage
        return ndimage.distance_transform_edt(maske) > max(float(radius), 1.0)

    @classmethod
    def haut(cls, p, groesse):
        """Pixel des Fotos, in denen Gesichtshaut zählt: `(hoehe, breite)` Bool für `p` (478, 2) in Pixeln eines Ausschnitts `groesse` (Breite, Höhe)."""
        h = cls.hoehe(p)
        maske = cls._schrumpfen(cls._flaeche(p[list(cls.OVAL)], groesse), cls.OVAL_RAND * h)
        brauen = np.vstack([p[list(cls.BRAUE_LINKS)], p[list(cls.BRAUE_RECHTS)]])
        oben = float(brauen[:, 1].min())
        grenze = oben - cls.STIRN_BIS * (oben - float(p[cls.STIRN][1]))
        maske[: max(int(grenze), 0)] = False
        for kette, rand in ((cls.AUGE_LINKS, cls.AUGEN_RAND), (cls.AUGE_RECHTS, cls.AUGEN_RAND), (cls.MUND_INNEN, cls.MUND_RAND)):
            maske &= ~cls._wachsen(cls._flaeche(p[list(kette)], groesse), rand * h)
        return maske

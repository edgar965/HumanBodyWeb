# -*- coding: utf-8 -*-
"""BVH-Bewegung in 2D-Bildpunkte projizieren.

Aus core/dienste/keypoints.py herausgeloest (Umbau 16.08.2026): 180 Zeilen
Vorwaertskinematik und orthographische Projektion — eine Rechnung, kein Dienst.

Am 17.08.2026 in drei Klassen zerlegt (Befund `dateigroesse`, Kriterium 2 und 10):

    bvhbaum.py               Hierarchie und Bewegungsdaten lesen
    vorwaertskinematik.py    Kanalwerte -> Weltpositionen je Bild
    ueberlagerungskamera.py  Weltpositionen -> Videopixel wie im Browser

Diese Datei ist nur noch die Kette darüber. Die Zahlen sind durch
`core/tests/unit/test_bvh_projektion.py` festgenagelt — von Hand nachgerechnet,
nicht aus dem Lauf übernommen.

UMBAU 27.08.2026 (Befund `freie-funktionen`): Die Kette stand als freie
Funktion `_parse_bvh_to_2d` da. Sie ist die einzige oeffentliche Methode von
`Bvhprojektion` geworden — die drei Schritte darunter tragen jetzt Namen, statt
in einem Rumpf zu stehen.
"""

from .bvhbaum import Bvhbaum
from .ueberlagerungskamera import Ueberlagerungskamera
from .vorwaertskinematik import Vorwaertskinematik


class Bvhprojektion:
    """BVH lesen, Vorwaertskinematik rechnen, auf Videopixel projizieren."""

    @classmethod
    def punkte(cls, bvh_pfad, video_breite, video_hoehe):
        """`(bildpunkte, verbindungen)` fuer die Videoueberlagerung.

          * `bildpunkte`: [{Gelenkname: (x_px, y_px, 1.0)}, …] je Bild
          * `verbindungen`: [(Eltern, Kind), …] aus der BVH-Hierarchie

        Eine Datei ohne Bewegungsdaten oder ohne Gelenke ergibt `([], [])` —
        der Aufrufer zeichnet dann kein Rig, statt abzubrechen.
        """
        baum = Bvhbaum(bvh_pfad)
        if baum.leer:
            return [], []
        positionen = Vorwaertskinematik(baum).positionen()
        kamera = Ueberlagerungskamera(positionen, video_breite, video_hoehe)
        return kamera.bilder(positionen), baum.verbindungen()

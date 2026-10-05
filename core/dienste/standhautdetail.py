# -*- coding: utf-8 -*-
"""Standhautdetail — ruhigere Haut mit feiner Zeichnung für Beine und Arme vor den Iterationen (04.10.2026, Edgar: „die textur bei den beinen und armen ist sehr verwaschen").

Die Hautkacheln des Schritts „Körper" kommen aus der Farbe des Netzes (TRELLIS.2, `Meshfigurtextur`): Ein Netz mit 100.000 Flächen trägt kein Haar und keine Poren, die gebackene Kachel zeigt die Malerei
des Netzes — weiche Flecken von einigen Zentimetern, dazwischen Plateaus dort, wo die Daz-Haut die Lücken füllt. Im Bühnenbild liest sich das als „verwaschen und fleckig". Die Fotos selbst lösen die Haut
auf (die Haut aus den Fotos, `Koerperfotoprojektion`, rechnet erst in den Iterationen); bis dahin zeichnet diese Klasse die Kachel ruhiger:

1. Die Flecken (Schwankungen zwischen `FLECK_PX` und `GRUND_PX` Texeln, rund 7–60 mm) werden um `DAEMPFUNG` gedämpft — linear gerechnet über die Tiefpässe der Kachel (nur über ihre Inseln gemittelt).
   Die große Schattierung (Muskeln, Licht) und die Zeichnung unter 7 mm bleiben.
2. Dazu eine feine Zeichnung: kurze dunkle Punkte (Haare) und leichte Fleckung (Poren).

Ein Versuch mit Nachschärfen (Unsharp-Maske) machte die Flecken zu Krusten — sichtbar im Bühnenbild —, deshalb gedämpft statt geschärft. Das ist erfundene Feinzeichnung, keine gemessene: Der Ton der Kachel
(Mittel und große Schattierung) bleibt, die Verteilung der Haare folgt nicht dem Foto. Sobald die Iterationen die Haut aus den Fotos gebaut haben (`hautfoto_<k>.jpg`), bleibt die Kachel, wie sie ist.
"""

import numpy as np

__all__ = ['Standhautdetail']


class Standhautdetail:
    #: Die gebackenen Netzkacheln mit Beinen (1003) und Armen (1004); Rumpf (1002) trägt Hemd, Kopf (1001) hat ein echtes Gesicht.
    KACHELN = (1003, 1004)
    #: Tiefpass der großen Schattierung und der Flecken, in Texeln der Kachel (2048², rund 0,5 mm je Texel an Beinen und Armen).
    GRUND_PX = 120.0
    FLECK_PX = 14.0
    #: Wie viel von den Flecken weggenommen wird (0 = nichts, 1 = alle).
    DAEMPFUNG = 0.6
    #: Haarpunkte: Schwelle im geglätteten Rauschen (in Standardabweichungen) und größte Abdunklung eines Punkts.
    PUNKT_AB = 1.5
    PUNKT_DUNKEL = 0.45
    #: Feinfleckung (Poren): Stärke der Helligkeitsschwankung.
    POREN = 0.03
    SAMEN = 11
    JPEG_GUETE = 90

    @staticmethod
    def _linear(c):
        return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

    @staticmethod
    def _srgb(c):
        c = np.clip(c, 0.0, 1.0)
        return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)

    @classmethod
    def gilt(cls, kachel, pfad):
        """Nur für die gebackene Netzkachel (`meshfigur_<k>.jpg`) — eine Haut aus den Fotos (`hautfoto_<k>.jpg`) bleibt."""
        from pathlib import Path
        return int(kachel) in cls.KACHELN and Path(str(pfad)).name.startswith('meshfigur_')

    @staticmethod
    def _tief(lin, w, sigma):
        """Tiefpass (Gauß `sigma` Texel) über die Texel mit Gewicht `w`, normiert — auf verkleinertem Bild gerechnet (ein Sechstel von `sigma` je Schritt), dann auf die Größe von `lin` gebracht."""
        import cv2

        hoehe, breite = w.shape
        schritt = max(1, int(sigma // 6))
        klein = (max(1, breite // schritt), max(1, hoehe // schritt))
        zaehler = cv2.resize((lin * w[..., None]).astype(np.float32), klein, interpolation=cv2.INTER_AREA)
        nenner = cv2.resize(w.astype(np.float32), klein, interpolation=cv2.INTER_AREA)
        s = sigma / schritt
        zaehler = cv2.GaussianBlur(zaehler, (0, 0), s)
        nenner = cv2.GaussianBlur(nenner, (0, 0), s)
        aus = zaehler / np.maximum(nenner, 1e-6)[..., None]
        return cv2.resize(aus, (breite, hoehe), interpolation=cv2.INTER_LINEAR).astype(np.float64)

    @classmethod
    def anwenden(cls, bild):
        """PIL-Bild (sRGB) → PIL-Bild mit gedämpften Flecken und feiner Zeichnung; außerhalb der Inseln (Weiß) bleibt es, wie es ist."""
        from PIL import Image
        from scipy import ndimage

        arr = np.asarray(bild.convert('RGB'), dtype=np.float64) / 255.0
        insel = ~np.all(arr > 0.985, axis=2)
        belegt = ndimage.binary_erosion(insel, iterations=6)
        lin = cls._linear(arr)
        w = insel.astype(np.float64)
        grund = cls._tief(lin, w, cls.GRUND_PX)
        mittel = cls._tief(lin, w, cls.FLECK_PX)
        gedaempft = grund + (1.0 - cls.DAEMPFUNG) * (mittel - grund) + (lin - mittel)
        zufall = np.random.default_rng(cls.SAMEN)
        rauschen = ndimage.gaussian_filter(zufall.random(w.shape), 0.8)
        rauschen = (rauschen - rauschen.mean()) / max(float(rauschen.std()), 1e-9)
        haar = 1.0 - cls.PUNKT_DUNKEL * np.clip(rauschen - cls.PUNKT_AB, 0.0, 1.0)
        poren = 1.0 + cls.POREN * 3.0 * ndimage.gaussian_filter(zufall.standard_normal(w.shape), 1.2)
        neu = cls._srgb(np.clip(gedaempft, 0.0, None) * (haar * poren)[..., None])
        return Image.fromarray(np.rint(np.where(belegt[..., None], neu, arr) * 255.0).astype(np.uint8), 'RGB')

    @classmethod
    def karte(cls, glb, albedo):
        """glTF-Texturnummer der Kachel `albedo` (Pfad) mit Feinzeichnung, als JPEG in die Datei gelegt (`Standmodellglb`); bei einem Fehler None — der Aufrufer nimmt die Kachel, wie sie war."""
        import io
        import logging

        from PIL import Image
        try:
            with Image.open(albedo) as roh:
                bild = cls.anwenden(roh)
            speicher = io.BytesIO()
            bild.save(speicher, format='JPEG', quality=cls.JPEG_GUETE)
            glb.gltf.setdefault('images', []).append({'bufferView': glb._ablegen(speicher.getvalue()), 'mimeType': 'image/jpeg'})        # noqa: SLF001
            glb.gltf.setdefault('textures', []).append({'source': len(glb.gltf['images']) - 1, 'sampler': 0})
            glb.zahl['bilder'] += 1
            return len(glb.gltf['textures']) - 1
        except Exception:  # noqa: BLE001 — die Feinzeichnung ist eine Zugabe: der Stand muss in jedem Fall entstehen
            logging.getLogger('core').exception('Hautdetail: Kachel %s nicht gezeichnet — bleibt wie sie war', albedo)
            return None

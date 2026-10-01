# -*- coding: utf-8 -*-
"""Mitsubamaterial — Farben, Bilder und Materialien für `Mitsubaszene` (01.10.2026).

Mitsuba rechnet LINEAR; alles, was hier hereinkommt, ist sRGB (die flachen Farben der Teile, die Daz-Bilder, die
komponierten Schichten). Deshalb: Farbe und Albedo nach linear, das Bild am Ende zurück nach sRGB
(`Mitsubaszene.rendern`). Eine Fläche mit Albedo c, die nur der gleichmäßige Himmel (Strahldichte 1) beleuchtet, zeigt
dann genau c — die Tönung im Rezept bleibt eine Farbe, kein Belichtungswert.

- **Bilder** werden verkleinert (`kante`) und als Feld übergeben (`bitmap` mit `data`), nicht als Datei — eine 4K-Karte
  lädt Mitsuba sonst als Gleitkomma (200 MB je Bild auf der Grafikkarte). Ein kleiner Vorrat je Prozess (Pfad, Stand,
  Kante) spart das Dekodieren über die Ansichten und Runden.
- **Normalkarten** (Daz, gebackene Falten): roh, Tangentenraum; DirectX-Karten (`normalenachse` −1,
  `G9browserbilder`) bekommen den grünen Kanal gespiegelt. Mitsubas `normalmap` baut den Rahmen aus dp/du und der
  Normale (t = n × s) — unabhängig davon, wie herum v läuft.
- **Haar** (Kurven): NICHT Mitsubas `hair` (Chiang 2016), sondern dasselbe matte Material wie die Stoffe — gemessen
  01.10.2026 an den Pixie-Strähnen (256², vorn + hinten, 64 Abtastungen): mit `hair` und der Absorption nach Chiang
  Gl. 9 staucht der farblose Glanz die Farben, Soll 0,10 → 0,23, 0,30 → 0,40, 0,85 → 0,60 (schwarzes Haar aus einem
  Foto wäre unerreichbar, die Tönung liefe an den Anschlag); matt bleibt das Verhältnis über den ganzen Bereich bei
  0,68–0,93 (Eigenschatten der Strähnen) — ein fester Faktor, den der Farbangleich der Iterationen herausrechnet.
  `haar_sigma` bleibt für einen späteren Glanzlauf.
- **Normalen** je Punkt über verschweißte Lagen: Die Netze sind an den UV-Nähten geteilt (`G9netzteilung`); geteilte
  Punkte bekämen sonst je Seite eine eigene Normale, und jede Naht stünde als Kante im Bild.
"""

import logging
from collections import OrderedDict

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Mitsubamaterial']


class Mitsubamaterial:
    #: Rauheit/Glanz der Stoffe und der Haut (Disney „principled") — matt, ein Hauch Glanz.
    RAUHEIT = 0.8
    GLANZ = 0.25
    #: Chiangs azimutale Rauheit β_n der Strähnen (Mitsuba-Vorgabe 0,3).
    HAAR_BETA = 0.3
    VORRAT = 24
    _vorrat = OrderedDict()

    # ------------------------------------------------------------- Farben

    @staticmethod
    def linear(srgb):
        c = np.clip(np.asarray(srgb, dtype=np.float64), 0.0, 1.0)
        return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

    @staticmethod
    def srgb(linear):
        c = np.clip(np.asarray(linear, dtype=np.float64), 0.0, 1.0)
        return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.power(c, 1.0 / 2.4) - 0.055)

    @classmethod
    def haar_sigma(cls, farbe_srgb):
        """Absorption σ_a je Kanal aus der Strähnenfarbe (Chiang et al. 2016, Gl. 9)."""
        b = cls.HAAR_BETA
        nenner = 5.969 - 0.215 * b + 2.532 * b ** 2 - 10.73 * b ** 3 + 5.574 * b ** 4 + 0.245 * b ** 5
        c = np.clip(cls.linear(farbe_srgb), 1e-3, 0.999)
        return (np.log(c) / nenner) ** 2

    # -------------------------------------------------------------- Bilder

    @classmethod
    def bild(cls, pfad, kante, art='albedo', achse=1):
        """(H, B, 3) float32 — `albedo` linear, `normalen` roh (0…1, Grün gespiegelt bei `achse` −1)."""
        from pathlib import Path

        from PIL import Image
        pfad = Path(pfad)
        schluessel = (str(pfad), pfad.stat().st_mtime_ns, int(kante), art, int(achse))
        feld = cls._vorrat.get(schluessel)
        if feld is not None:
            cls._vorrat.move_to_end(schluessel)
            return feld
        with Image.open(pfad) as roh:
            bild = roh.convert('RGB')
            if max(bild.size) > kante:
                bild.thumbnail((int(kante), int(kante)), Image.Resampling.LANCZOS)
            feld = np.asarray(bild, dtype=np.float32) / 255.0
        if art == 'albedo':
            feld = cls.linear(feld).astype(np.float32)
        elif int(achse) < 0:
            feld = feld.copy()
            feld[..., 1] = 1.0 - feld[..., 1]
        cls._vorrat[schluessel] = np.ascontiguousarray(feld)
        while len(cls._vorrat) > cls.VORRAT:
            cls._vorrat.popitem(last=False)
        return cls._vorrat[schluessel]

    # ---------------------------------------------------------- Materialien

    @staticmethod
    def _beidseitig(innen):
        return {'type': 'twosided', 'bsdf': innen}

    @classmethod
    def flach(cls, farbe_srgb):
        farbe = {'type': 'rgb', 'value': cls.linear(farbe_srgb)[:3].tolist()}
        return cls._beidseitig({'type': 'principled', 'base_color': farbe, 'roughness': cls.RAUHEIT,
                                'specular': cls.GLANZ})

    @staticmethod
    def kennung(farbe):
        """Kennfarbe (Teilmasken): diffus, damit die Albedo-Ausgabe genau die Farbe trägt."""
        return {'type': 'twosided', 'bsdf': {'type': 'diffuse',
                                             'reflectance': {'type': 'rgb', 'value': [float(c) for c in farbe[:3]]}}}

    @classmethod
    def textur(cls, albedo, faktor, normalen=None, kante=1024, achse=1):
        """Albedo-Bild × Faktor (linear, wie glTFs baseColorFactor), wahlweise mit Normalkarte."""
        feld = cls.bild(albedo, kante, 'albedo') * np.asarray(faktor, dtype=np.float32)[:3]
        innen = {'type': 'principled',
                 'base_color': {'type': 'bitmap', 'data': np.ascontiguousarray(feld, dtype=np.float32), 'raw': True,
                                'filter_type': 'bilinear'},
                 'roughness': cls.RAUHEIT, 'specular': cls.GLANZ}
        if normalen is not None:
            innen = {'type': 'normalmap', 'bsdf': innen,
                     'normalmap': {'type': 'bitmap', 'data': cls.bild(normalen, kante, 'normalen', achse), 'raw': True,
                                   'filter_type': 'bilinear'}}
        return cls._beidseitig(innen)

    @classmethod
    def haar(cls, farbe_srgb):
        """Material der Strähnen (Kurven) — matt wie die Stoffe, siehe Kopf der Datei."""
        return cls.flach(farbe_srgb)

    @classmethod
    def haar_glanz(cls, farbe_srgb):
        """Mitsubas Haarmaterial (Chiang 2016) — schöner, aber farblich gestaucht (Kopf der Datei)."""
        return {'type': 'hair', 'sigma_a': {'type': 'rgb', 'value': cls.haar_sigma(farbe_srgb)[:3].tolist()},
                'azimuthal_roughness': cls.HAAR_BETA}

    # ------------------------------------------------------------- Normalen

    @staticmethod
    def gruppen(punkte):
        """Je Punkt die Nummer seiner Lage — Nahtkopien teilen sie. Im Film einmal aus der Ruhelage (`Mitsubaszene`):
        Nahtkopien tragen dieselbe Haut und bleiben beisammen, und die Suche kostete je Bild und Netz 0,19 s
        (01.10.2026)."""
        p = np.asarray(punkte, dtype=np.float64)
        return np.unique(np.round(p / 1e-6).astype(np.int64), axis=0, return_inverse=True)[1].ravel()

    @classmethod
    def normalen(cls, punkte, dreiecke, gruppe=None):
        """Glatte Normalen je Punkt, flächengewichtet, über Punkte gleicher Lage gemittelt (Nahtkopien; `gruppe` aus
        `gruppen`, sonst hier gesucht)."""
        p = np.asarray(punkte, dtype=np.float64)
        d = np.asarray(dreiecke, dtype=np.int64).reshape(-1, 3)
        flaeche = np.cross(p[d[:, 1]] - p[d[:, 0]], p[d[:, 2]] - p[d[:, 0]])
        gruppe = cls.gruppen(p) if gruppe is None else np.asarray(gruppe, dtype=np.int64)
        anzahl = int(gruppe.max()) + 1 if len(gruppe) else 0
        ecken = gruppe[d.T.ravel()]                   # alle Ecke-0-, dann Ecke-1-, dann Ecke-2-Einträge
        summe = np.stack([np.bincount(ecken, weights=np.tile(flaeche[:, k], 3), minlength=anzahl) for k in range(3)],
                         axis=1)
        n = summe[gruppe]
        laenge = np.linalg.norm(n, axis=1, keepdims=True)
        leer = laenge[:, 0] < 1e-20
        n = n / np.maximum(laenge, 1e-20)
        n[leer] = (0.0, 0.0, 1.0)
        return n.astype(np.float32)

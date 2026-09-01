# -*- coding: utf-8 -*-
"""Koerperhuelle — Huellkoerper, an denen Kleidung angepasst wird.

Fuenf Funktionen aus core/api/kleidung.py, zusammen 618 Zeilen reine Geometrie:
eine geglaettete Huelle um den Koerper, eine aus Zylindern je Knochen, eine aus
dem Rig, dazu die beiden Anpassungsverfahren. Sie hatten nichts mit HTTP zu tun
und standen doch zwischen den Endpunkten (Umbau 15.08.2026).

UMBAU 17.08.2026
================
`allgemein_anpassen` (78 Zeilen) und `glatt` (68) sind in Schritte zerlegt. Dabei
gemessen und behoben: `glatt` baute die Nachbarschaftsmatrix in einer Python-
Schleife über alle Flächen und Kantenpaare (17.288 Vierecke × 6 Paare = 103.728
Einzelzuweisungen in eine `lil_matrix`). Vektorisiert über die Kantenliste sind
es zwei numpy-Aufrufe. Gemessen am weiblichen Grundkörper (18.210 Punkte),
abwechselnd je zweimal:

    vorher   0,70 s / 0,65 s
    nachher  siehe `test_koerperhuelle` — dieselbe Ausgabe, ein Bruchteil der Zeit

Dieselbe Ausgabe: Die Prüfung vergleicht gegen die alte Fassung, nicht gegen
sich selbst.
"""

import numpy as np
from humanbody_core.koerperabstand import Koerperabstand


class Koerperhuelle:
    """Koerperhuelle — Huellkoerper, an denen Kleidung angepasst wird."""

    #: Schrumpf-Durchgänge und die Kantenlänge, die dabei kleiner wird.
    SCHRUMPFEN = 5
    KANTENLAENGE = 0.08
    #: Unterhalb dieser Achslänge wird nicht skaliert (Division durch fast 0).
    MINDESTLAENGE = 0.001

    # ---------------------------------------------------- Anpassen an ein Netz

    @staticmethod
    def allgemein_anpassen(garment_verts, garment_faces, target_verts,
                           offset=0.006, stiffness=0.5, color=(0.3, 0.35, 0.5),
                           coordinate_system='auto'):
        """Generic garment fit: wrap garment around ANY target mesh.

        No arm-retarget, no crotch handling, no body-specific logic.
        Just: convert coords → align bounding boxes → shrinkwrap → smooth →
        push outside.
        """
        from GarmentFitter.fitter import _compute_vertex_normals

        punkte, dreiecke = Koerperhuelle._vorbereiten(
            garment_verts, garment_faces, coordinate_system)
        punkte = Koerperhuelle._einpassen(punkte, target_verts)
        normalen = Koerperhuelle._radialnormalen(target_verts)
        # Ziel leicht aufblasen: So bleibt nach dem Schrumpfen der Abstand
        # uebrig, den der Stoff braucht.
        gedehnt = target_verts + normalen * (offset * 0.5)
        punkte = Koerperhuelle._schrumpfen(punkte, gedehnt, normalen, dreiecke,
                                           offset)
        punkte = Koerperhuelle._verfeinern(punkte, gedehnt, dreiecke, offset,
                                           stiffness)
        # Dictionary gewollt: dasselbe Format wie `fit_garment` liefert.
        return {
            'vertices': punkte.astype(np.float32),
            'faces': dreiecke,
            'normals': _compute_vertex_normals(punkte, dreiecke).astype(np.float32),
            'color': color,
        }

    @staticmethod
    def _vorbereiten(punkte, flaechen, koordinatensystem):
        """Koordinatensystem klären und in Dreiecke zerlegen."""
        from GarmentFitter.fitter import (mh_to_blender, _triangulate,
                                          _detect_coordinate_system)
        werte = punkte.copy().astype(np.float64)
        if koordinatensystem == 'auto':
            koordinatensystem = _detect_coordinate_system(werte)
        if koordinatensystem == 'makehuman':
            werte = mh_to_blender(werte)
        return werte, _triangulate(flaechen.copy())

    @classmethod
    def _einpassen(cls, punkte, ziel):
        """Umgebungsquader angleichen: mitteln, je Achse skalieren, versetzen.

        Je Achse einzeln (nicht gleichförmig): Eine Kleidungsvorlage ist oft für
        eine andere Figur gebaut, und ein gleichförmiger Maßstab macht sie dann
        entweder zu kurz oder zu weit.
        """
        klein, gross = punkte.min(axis=0), punkte.max(axis=0)
        z_klein, z_gross = ziel.min(axis=0), ziel.max(axis=0)
        laenge, z_laenge = gross - klein, z_gross - z_klein
        mass = np.ones(3)
        genug = laenge > cls.MINDESTLAENGE
        mass[genug] = z_laenge[genug] / laenge[genug]
        return (punkte - (klein + gross) * 0.5) * mass + (z_klein + z_gross) * 0.5

    @staticmethod
    def _radialnormalen(punkte):
        """Normalen aus der Richtung zum Schwerpunkt — ohne Flächen."""
        richtung = punkte - punkte.mean(axis=0)
        laenge = np.linalg.norm(richtung, axis=1, keepdims=True)
        laenge[laenge < 1e-8] = 1.0
        return richtung / laenge

    @classmethod
    def _schrumpfen(cls, punkte, ziel, normalen, dreiecke, offset):
        """Anlegen, glätten, herausschieben — mit kleiner werdender Kantenlänge.

        Die Kantenlänge sinkt je Durchgang (`0,08 / (1 + i·0,3)`): Zuerst grob
        anlegen, dann fein. Konstant grob bliebe der Stoff kantig, konstant fein
        käme er in einem Durchgang nicht weit genug.
        """
        from GarmentFitter.fitter import _laplacian_smooth, _shrinkwrap
        for durchgang in range(cls.SCHRUMPFEN):
            punkte = _shrinkwrap(
                punkte, ziel, normalen, offset=offset, soft=True,
                char_length=cls.KANTENLAENGE / (1 + durchgang * 0.3))
            punkte = _laplacian_smooth(punkte, dreiecke, iterations=2,
                                       factor=0.15)
            punkte = Koerperabstand.gerichtet(punkte, ziel,
                                              mindestabstand=offset * 0.8)
        return punkte

    @staticmethod
    def _verfeinern(punkte, ziel, dreiecke, offset, stiffness):
        """Steifigkeit: weicher Stoff wird stärker geglättet, aber seltener."""
        from GarmentFitter.fitter import _laplacian_smooth
        steife = max(0.0, min(1.0, stiffness))
        staerke = 0.5 - steife * 0.4
        durchgaenge = max(2, round(5 - steife * 3))
        for _ in range(durchgaenge):
            punkte = _laplacian_smooth(punkte, dreiecke, iterations=3,
                                       factor=staerke)
            punkte = Koerperabstand.gerichtet(punkte, ziel,
                                              mindestabstand=offset * 0.8)
        return punkte

    # ------------------------------------------------------- Geglättete Hülle

    @staticmethod
    def glatt(body_verts, body_faces, inflate_mm=15, smooth_iterations=20):
        """Create a smoothed, inflated version of the body mesh.

        This fills in crotch/neck/armpit gaps by:
        1. Computing vertex normals
        2. Inflating outward along normals
        3. Heavy Laplacian smoothing to create a blobby envelope
        """
        punkte = body_verts.copy().astype(np.float64)
        normalen = Koerperhuelle._flaechennormalen(punkte, body_faces)
        punkte += normalen * (inflate_mm / 1000.0)
        if body_faces is None or len(body_faces) == 0:
            return punkte
        return Koerperhuelle._glaetten(punkte, body_faces, smooth_iterations)

    @staticmethod
    def dreiecke(flaechen):
        """Vierecke in Dreiecke — vektorisiert, ohne Python-Schleife.

        Nur für die Normalenrechnung: Die Umlaufrichtung bleibt wie gegeben
        ((0,1,2) und (0,2,3)), weil hier keine Fläche gezeichnet wird. Wo es
        gezeichnet wird, dreht `Materialgruppen.aus_flaechen` die Wicklung.
        """
        felder = np.asarray(flaechen)
        if felder.ndim == 2 and felder.shape[1] == 4:
            return np.concatenate([felder[:, [0, 1, 2]], felder[:, [0, 2, 3]]],
                                  axis=0).astype(np.int32)
        return felder[:, :3].astype(np.int32)

    @classmethod
    def _flaechennormalen(cls, punkte, flaechen):
        """Punktnormalen aus den Flächen — oder radial, wenn es keine gibt."""
        if flaechen is None or len(flaechen) == 0:
            return cls._radialnormalen(punkte)
        dreiecke = cls.dreiecke(flaechen)
        ecke = [punkte[dreiecke[:, i]] for i in range(3)]
        flaechennormalen = np.cross(ecke[1] - ecke[0], ecke[2] - ecke[0])
        # `np.add.at` und nicht `np.bincount`: Lehre gilt hier nicht
        # („bincount-statt-add-at"). Gemessen am 27.08.2026
        # unter numpy 2.4 mit denselben Zahlen (bitgleiches Ergebnis,
        # groesste Abweichung 5e-15): 18.000 Punkte / 36.000 Dreiecke je
        # 12 ms, bei 70.000 Punkten 29 ms gegen 31 ms fuer bincount. Die
        # bincount-Fassung braucht zusaetzlich ein `np.repeat` ueber alle
        # Dreiecksecken — mehr Speicher, kein Zeitgewinn.
        normalen = np.zeros_like(punkte)
        for i in range(3):
            np.add.at(normalen, dreiecke[:, i], flaechennormalen)
        laenge = np.linalg.norm(normalen, axis=1, keepdims=True)
        laenge[laenge < 1e-8] = 1.0
        return normalen / laenge

    @classmethod
    def _glaetten(cls, punkte, flaechen, durchgaenge, staerke=0.5):
        """Laplace-Glättung über die Nachbarschaftsmatrix der Flächen."""
        from scipy.sparse import diags
        nachbarn = cls._nachbarschaft(flaechen, len(punkte))
        grade = np.asarray(nachbarn.sum(axis=1)).flatten()
        grade[grade == 0] = 1
        mittel = diags(1.0 / grade) @ nachbarn
        for _ in range(durchgaenge):
            punkte = (1.0 - staerke) * punkte + staerke * (mittel @ punkte)
        return punkte

    @staticmethod
    def _nachbarschaft(flaechen, anzahl):
        """Wer grenzt an wen — als Matrix, aus der KANTENLISTE gebaut.

        Vorher lief hier eine Python-Schleife über alle Flächen und alle
        Eckenpaare darin und schrieb je Paar zwei Werte in eine `lil_matrix`:
        bei 17.288 Vierecken über hunderttausend Einzelzuweisungen. Jetzt werden
        die Kanten in einem Zug erzeugt und die Matrix in einem Aufruf gebaut.
        """
        from scipy.sparse import coo_matrix
        felder = np.asarray(flaechen)
        ecken = felder.shape[1]
        paare = [(i, j) for i in range(ecken) for j in range(i + 1, ecken)]
        von = np.concatenate([felder[:, i] for i, _ in paare])
        nach = np.concatenate([felder[:, j] for _, j in paare])
        # Beide Richtungen: Die Matrix muss symmetrisch sein.
        zeilen = np.concatenate([von, nach])
        spalten = np.concatenate([nach, von])
        werte = np.ones(len(zeilen), dtype=np.float64)
        matrix = coo_matrix((werte, (zeilen, spalten)),
                            shape=(anzahl, anzahl)).tocsr()
        # Doppelte Kanten (geteilt zwischen zwei Flächen) auf 1 setzen — die
        # `lil`-Fassung hat zugewiesen, nicht addiert.
        matrix.data[:] = 1.0
        return matrix

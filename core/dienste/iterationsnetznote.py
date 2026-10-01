# -*- coding: utf-8 -*-
"""Iterationsnetznote — wie weit ein Modell (Körper, Kleider, Haar) vom Netz aus den Fotos abweicht, in 3D.

Ergänzt `Iterationsnote` (Fotos: Umriss und Farbe je Blickwinkel) um das Maß, das nur „2D3D Kleider" hat: das
Netz aus TRELLIS/Hunyuan (`Haarengineablage.bezugsnetz`, in der Lage der Erkennung — dieselbe wie die Figur).
Zwei Zahlen, beide in Metern gemessen:

    modell_mm   mittlerer Abstand der Kleider- und Haarpunkte zur Netzoberfläche (Stoff, der zu weit vom Foto absteht)
    deckung     Anteil der Netzproben, die näher als NAH_M an einem Punkt des Modells liegen (was das Foto zeigt,
                ist auch da)

`abweichung = modell_mm / MASS_MM + (1 − deckung)` — kleiner ist besser, wie bei der Fotonote. Gemessen wird gegen
`PROBEN` Oberflächenproben des Netzes (fest gesät, damit zwei Runden vergleichbar sind).
"""

import numpy as np

__all__ = ['Iterationsnetznote']


class Iterationsnetznote:
    PROBEN = 60000
    NAH_M = 0.015
    #: So viele Millimeter mittlerer Abstand zählen wie eine ganz fehlende Deckung.
    MASS_MM = 50.0
    SAAT = 20260930

    def __init__(self, netz_pfad, lage=None):
        import trimesh
        from scipy.spatial import cKDTree
        netz = trimesh.load(str(netz_pfad), force='mesh', process=False)
        if lage is not None:
            netz.apply_transform(np.asarray(lage, dtype=np.float64))
        proben, flaechen = trimesh.sample.sample_surface(netz, self.PROBEN, seed=self.SAAT)
        self.proben = np.asarray(proben, dtype=np.float64)
        #: Fläche je Probe und Flächenzahl des Netzes — damit die Flächenlabels des Körperschritts
        #: (`arbeit/kleidung_maske.npz`: haut/kleidung je Fläche) auf die Proben kommen (`labels`, 01.10.2026).
        self.flaechen = np.asarray(flaechen, dtype=np.int64)
        self.flaechen_anzahl = int(len(netz.faces))
        self.labels = None
        #: Normale der Fläche je Probe, nach AUSSEN — für den Abstand mit Vorzeichen (`Befundmessung`, Ordner
        #: `2d3DIterationen`). Ob die Wicklung nach außen zeigt, sagt das Vorzeichen des Volumens (Divergenzsatz
        #: über die Flächen); eine Eichung am Schwerpunkt ging schief — er liegt bei einer Figur in der Lücke
        #: zwischen den Beinen.
        normalen = np.asarray(netz.face_normals, dtype=np.float64)[np.asarray(flaechen)]
        self.normalen = -normalen if float(netz.volume) < 0 else normalen
        self._baum = cKDTree(self.proben)
        self.hoehe = float(netz.bounds[1][1] - netz.bounds[0][1])

    @classmethod
    def laden(cls, ablage):
        """Aus der Ablage eines Auftrags — None ohne Bezugsnetz."""
        pfad = ablage.bezugsnetz()
        if pfad is None:
            return None
        lage_pfad = ablage.arbeit(ablage.BEZUGSLAGE)
        lage = None
        if lage_pfad.is_file():
            with np.load(lage_pfad) as d:
                lage = d['matrix'] if 'matrix' in d.files else None
        note = cls(pfad, lage)
        note.labels = note._labels(ablage.arbeit('kleidung_maske.npz'))
        return note

    def _labels(self, pfad):
        """`{'haut': (P,) bool, 'kleidung': (P,) bool}` je Probe aus den Flächenlabels des Körperschritts
        (`Meshfigurkleidung`) — None ohne Datei oder wenn sie nicht zu diesem Netz passt. Damit misst `Befundmessung`
        ein Kleid nur gegen die Stofffläche des Netzes und den Körper nur gegen seine Haut: Die Fotos zeigen hängende
        Arme, das Modell steht in A-Pose — ohne Labels liefen die Zellenmorphe des Shirts den Armen des Netzes
        hinterher (±4 cm, 01.10.2026, `.51` Runden 7–22)."""
        if not pfad.is_file():
            return None
        try:
            with np.load(pfad) as d:
                if 'haut' not in d.files or 'kleidung' not in d.files or len(d['haut']) != self.flaechen_anzahl:
                    return None
                return {'haut': np.asarray(d['haut'], bool)[self.flaechen],
                        'kleidung': np.asarray(d['kleidung'], bool)[self.flaechen]}
        except (OSError, ValueError, KeyError):
            return None

    def vergleichen(self, teile):
        """`teile` wie `Kleidermodellbau.teile` → {modell_mm, deckung, abweichung, koerper_mm}."""
        from scipy.spatial import cKDTree
        stoff = [t['punkte'] for t in teile if t.get('art') != 'koerper']
        koerper = [t['punkte'] for t in teile if t.get('art') == 'koerper']
        alle = np.vstack([np.asarray(p, dtype=np.float64) for p in stoff + koerper]) if (stoff or koerper) else None
        aus = {'modell_mm': None, 'koerper_mm': None, 'deckung': 0.0}
        if stoff:
            abstand, _ = self._baum.query(np.vstack(stoff))
            aus['modell_mm'] = round(float(np.mean(abstand)) * 1000.0, 2)
        if koerper:
            abstand, _ = self._baum.query(np.vstack(koerper))
            aus['koerper_mm'] = round(float(np.mean(abstand)) * 1000.0, 2)
        if alle is not None and len(alle):
            abstand, _ = cKDTree(alle).query(self.proben)
            aus['deckung'] = round(float(np.mean(abstand < self.NAH_M)), 4)
        mm = aus['modell_mm'] if aus['modell_mm'] is not None else (aus['koerper_mm'] or 0.0)
        aus['abweichung'] = round(mm / self.MASS_MM + (1.0 - aus['deckung']), 4)
        return aus

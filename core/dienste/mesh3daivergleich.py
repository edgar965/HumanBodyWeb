# -*- coding: utf-8 -*-
"""Mesh3daivergleich — zwei Maßstäbe für den Fehler des Netzes, je Probe und Zeile der Jobseite von Mesh3D-AI (16.10.2026).

Edgar: „mach beim Ergebnis in jeder Zeile eine genaue Ausgabe in mindestens 10 Zahlen, wie gut das Ergebnis ist“. Die Tabelle unter dem Ergebnis (`Mesh3daiguete`, Seite) rechnet die meisten Zahlen selbst aus den
Rig-Punkten; diese zwei braucht sie vom Server, weil sie den ganzen Trainingssatz kennen:
- **mittlere Trainingspose:** der Fehler, wenn man immer die mittlere Soll-Pose des Trainings vorhersagt — dieselbe Basislinie wie `mittlere_pose_mm` in `lauf_ergebnis.json`.
- **nächste Trainingspose:** der Fehler der ähnlichsten Trainingspose (für diese Zeile gesucht, Mittel über ihre Rig-Punkte; bei einer Trainingsprobe die nächste ANDERE). Gemessen 15.10.2026
  (`ProjektTemp/_wegwerf/mesh3dai_naechste_trainingspose.py`, Lauf `2026.10.15.11.59_dgcnn`): auf den nie trainierten Posen folgt der Fehler des Netzes diesem Abstand mit der Korrelation 0,99 —
  er zeigt, wie weit eine Pose vom Gelernten weg ist.
Alle Abstände in mm, Mittel über die Rig-Punkte der Zeile, im ausgerichteten Rahmen des Datensatzes (wie der Fehler des Netzes).
"""

import numpy as np

__all__ = ['Mesh3daivergleich']


class Mesh3daivergleich:
    def __init__(self, training):
        """`training`: `{nr: Soll-Rig (138, 3) in m}` der Proben der Gruppe „training“."""
        self.nummern = list(training)
        self.rig = np.stack([training[n] for n in self.nummern]) if training else np.zeros((0, 0, 3))
        self.mittel = self.rig.mean(axis=0) if training else None

    def werte(self, nr, soll, indizes):
        """`{mittlere_pose_mm, naechste_pose_mm, naechste_pose_nr}` für die Rig-Punkte `indizes`; leer ohne Trainingsproben."""
        if self.mittel is None:
            return {}
        abstand = 1000.0 * np.linalg.norm(self.rig[:, indizes] - soll[None, indizes], axis=-1).mean(axis=1)
        if nr in self.nummern:
            abstand[self.nummern.index(nr)] = np.inf
        if not np.isfinite(abstand).any():
            return {}
        i = int(np.argmin(abstand))
        basis = 1000.0 * np.linalg.norm(self.mittel[indizes] - soll[indizes], axis=-1).mean()
        return {'mittlere_pose_mm': round(float(basis), 1), 'naechste_pose_mm': round(float(abstand[i]), 1), 'naechste_pose_nr': int(self.nummern[i])}

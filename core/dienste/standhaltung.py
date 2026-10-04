# -*- coding: utf-8 -*-
"""Standhaltung — die Haltung der Iterationen als Ruhedrehung der Gelenkknoten des Stand-Modells (03.10.2026).

Edgar: „warum sehe ich als Modell was anderes als in den Iterationen???" Jede Runde rendert Körper, Kleider, Haar und Zubehör in der
Haltung (`ModellMitKleidern.drehung`: Arme gesenkt, Unterarme, Oberschenkel, Finger — `G9haltungshaut` häutet jedes Teil mit seiner Haut
von der A-Pose in die Haltung), das Stand-Modell der Bühne stand dagegen in der A-Pose. Ein Versuch, die Haltung in den Bau des Körpers zu
geben, ließ Hemd, Hose und Zubehör in der A-Pose stehen. Hier bleibt das Netz in der A-Pose (die Bindematrizen auch), und die Haltung kommt
als Drehung auf die Gelenkknoten: three.js häutet dann ALLE Teile gemeinsam mit denselben Gewichten wie `G9haltungshaut`.

    Weltlage in der Haltung  W'_b = D'_b · W_b      D'_b = T(−boden) · D_b · T(+boden)   (D_b: `G9haltungshaut.verformungen`, Meter)
    Lokale Drehung           R_b  = Drehanteil von  W'_eltern⁻¹ · W'_b

Nur die Drehung der Knoten wird gesetzt, ihre Verschiebung bleibt (eine reine Gelenkdrehung verschiebt ein Kind im Eltern-Raum nicht). Die
Bewegung (BVH) schreibt absolute Drehungen auf dieselben Knoten und überstimmt die Haltung — die Haltung gilt, solange nichts spielt.
"""

import numpy as np

__all__ = ['Standhaltung']


class Standhaltung:
    @staticmethod
    def anwenden(glb, haltung, boden):
        """Setzt die Drehung der Gelenkknoten von `glb` (`Standmodellglb`) → Zahl der gedrehten Knoten. `haltung`: `G9haltungshaut`."""
        from scipy.spatial.transform import Rotation

        verformung = haltung.verformungen()
        if not verformung:
            return 0
        hin, zurueck = np.eye(4), np.eye(4)
        hin[1, 3], zurueck[1, 3] = float(boden), -float(boden)
        knoten = glb.gltf['nodes']
        ruhe = glb.welt(glb.gelenke)
        eltern = {kind: i for i, k in enumerate(knoten) for kind in k.get('children', [])}
        namen = {glb.gelenke[i]: k['name'] for i, k in enumerate(glb.knochen)}
        pose = {i: (zurueck @ verformung[namen[i]] @ hin @ ruhe[i]) if namen[i] in verformung else ruhe[i] for i in glb.gelenke}
        gesetzt = 0
        for i in glb.gelenke:
            if namen[i] not in verformung:
                continue
            lokal = np.linalg.inv(pose[eltern[i]]) @ pose[i] if eltern.get(i) in pose else pose[i]
            drehung = lokal[:3, :3]
            laenge = np.linalg.norm(drehung, axis=0)
            quaternion = Rotation.from_matrix(drehung / np.where(laenge > 0, laenge, 1.0)).as_quat()   # x, y, z, w wie glTF
            knoten[i]['rotation'] = [float(x) for x in quaternion]
            gesetzt += 1
        return gesetzt

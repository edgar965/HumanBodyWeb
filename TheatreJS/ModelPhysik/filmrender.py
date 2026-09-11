# -*- coding: utf-8 -*-
u"""Kamera und Bilder eines Films — aus `hbfilm.py` abgeteilt (11.09.2026).

Die Kamera laeuft mit und schaut der Figur ins Gesicht. Beides ist
gemessen, nicht angenommen: Ein fester Versatz stand bei `136_12` hinter
der Figur, und die LAUFRICHTUNG taugt nicht als Blickrichtung, weil die
Person dort rueckwaerts geht (Zehen 170 Grad gegen die Bewegung).
"""
import os

import numpy as np


class Filmrender:
    u"""Rendert die Teile eines `Hbfilm` Bild fuer Bild."""

    HINTERGRUND = (0.93, 0.94, 0.96)
    ABSTAND = 2.2

    #: Blender-Lage (z oben) -> Renderlage (y oben). Die KAMERA braucht
    #: sie genauso wie die Netze: Wer die Kameramitte in
    #: Blender-Koordinaten rechnet und in Renderkoordinaten einsetzt,
    #: verwechselt Tiefe mit Hoehe — die Figur laeuft dann nach 36
    #: Bildern aus dem Bild, obwohl die Kamera „mitlaeuft".
    DREHUNG = np.array([[1.0, 0.0, 0.0],
                        [0.0, 0.0, 1.0],
                        [0.0, -1.0, 0.0]])

    def __init__(self, teile, bahn, melder=None):
        self.teile = teile
        self.bahn = bahn
        self.melder = melder or (lambda phase, anteil: None)

    def _kamera(self, nummer):
        u"""Die Kamera laeuft mit — IN RENDERKOORDINATEN.

        Ohne das Mitlaufen verlaesst die Figur nach 2,8 m das Bild, und ein
        Video, auf dem am Ende nur Hintergrund steht, ist kein Beleg. Die
        Mitte wird durch DIESELBE Drehung geschickt wie die Netze; wer sie
        in Blender-Koordinaten laesst, setzt die Tiefe als Hoehe ein und
        die Kamera laeuft in die falsche Richtung davon.
        """
        koerper = self.teile[0]['haut'].folge[nummer]
        mitte = self.DREHUNG @ koerper.mean(axis=0)
        hoehe = float(self.teile[0]['haut'].folge[0][:, 2].max())
        blick = np.array([mitte[0], 0.52 * hoehe, mitte[2]])
        lage = np.eye(4)
        # SCHRAEG VON VORN, an der LAUFRICHTUNG ausgerichtet. Ein fester
        # Versatz steht je nach Bewegung mal vor, mal hinter der Figur —
        # bei `136_12` genau dahinter, und dann sieht man vom T-Shirt den
        # Ruecken statt die Vorderseite.
        vorn, seite = self._richtung(), np.array([0.0, 1.0, 0.0])
        quer = np.cross(seite, vorn)
        lage[:3, 3] = blick + self.ABSTAND * hoehe * (
            0.82 * vorn + 0.52 * quer + 0.18 * seite)
        return lage, hoehe, blick

    def _richtung(self):
        u"""BLICKRICHTUNG der Figur in Renderkoordinaten, waagrecht.

        NICHT die Laufrichtung. Gemessen in der BVH-Quelle stehen bei
        `136_12` die Zehen 170 Grad gegen die Bewegung — die Person geht
        rueckwaerts, und eine Kamera in Laufrichtung filmt dann den
        Ruecken. Die Blickrichtung kommt aus den Zehen UNSERES Rigs
        (`DEF-toe.L` gegen `DEF-foot.L`), das in Ruhe unstrittig frontal
        steht, und wird ueber die Beckendrehung je Bild mitgefuehrt.
        """
        if getattr(self, '_blick', None) is not None:
            return self._blick
        ruhe = self.bahn.ruhe
        if 'DEF-toe.L' in ruhe and 'DEF-foot.L' in ruhe:
            vor = self._waagrecht(np.asarray(ruhe['DEF-toe.L'][0])
                                  - np.asarray(ruhe['DEF-foot.L'][0]))
            lokal = self.bahn.dreh(ruhe['DEF-spine'][1]).T @ vor
            mittel = np.mean([self._waagrecht(
                self.bahn.dreh(lage['DEF-spine'][1]) @ lokal)
                for lage in self.bahn.lagen], axis=0)
            self._blick = self.DREHUNG @ self._waagrecht(mittel)
        else:
            self._blick = np.array([0.0, 0.0, 1.0])
        self._blick[1] = 0.0
        self._blick /= max(np.linalg.norm(self._blick), 1e-9)
        return self._blick

    @staticmethod
    def _waagrecht(v):
        u"""Auf die Bodenebene des RIGS (z oben) projiziert und normiert."""
        v = np.array(v, dtype=np.float64)
        v[2] = 0.0
        return v / max(np.linalg.norm(v), 1e-9)

    @staticmethod
    def _blicken(lage, ziel):
        u"""Kameramatrix, die von `lage` auf `ziel` schaut (Y oben)."""
        auge = lage[:3, 3]
        vor = auge - ziel
        vor /= max(np.linalg.norm(vor), 1e-9)
        rechts = np.cross(np.array([0.0, 1.0, 0.0]), vor)
        rechts /= max(np.linalg.norm(rechts), 1e-9)
        oben = np.cross(vor, rechts)
        aus = np.eye(4)
        aus[:3, 0], aus[:3, 1], aus[:3, 2] = rechts, oben, vor
        aus[:3, 3] = auge
        return aus

    def bilder_rendern(self, breite=720, hoehe=900):
        import trimesh
        import pyrender
        drehung = self.DREHUNG
        kamera = pyrender.PerspectiveCamera(yfov=np.deg2rad(36.0))
        licht = pyrender.DirectionalLight(color=np.ones(3), intensity=3.6)
        werk = pyrender.OffscreenRenderer(breite, hoehe)
        # ZWEISEITIG wie in der Szene (`side: THREE.DoubleSide`): Die
        # Vorlagen-Hose ist zu 76 % nach INNEN gewickelt (gemessen
        # 11.09.2026); einseitig gerendert blieben von ihr nur Fetzen an
        # den Beinen, die von innen zu sehen sind.
        stoffe = [pyrender.MetallicRoughnessMaterial(
            baseColorFactor=list(t['farbe']) + [1.0], metallicFactor=0.0,
            roughnessFactor=0.62, doubleSided=True) for t in self.teile]
        try:
            zahl = len(self.teile[0]['haut'].folge)
            for nummer in range(zahl):
                self.melder(u'Bild %d von %d' % (nummer + 1, zahl),
                            0.45 + 0.55 * nummer / max(zahl, 1))
                lage, figurhoehe, blick = self._kamera(nummer)
                szene = pyrender.Scene(
                    bg_color=list(self.HINTERGRUND) + [1.0],
                    ambient_light=[0.40, 0.40, 0.42])
                for teil, werkstoff in zip(self.teile, stoffe):
                    netz = trimesh.Trimesh(
                        vertices=teil['haut'].folge[nummer] @ drehung.T,
                        faces=teil['dreiecke'], process=False)
                    szene.add(pyrender.Mesh.from_trimesh(
                        netz, smooth=True, material=werkstoff))
                szene.add(kamera, pose=self._blicken(lage, blick))
                lichtlage = np.array(lage)
                lichtlage[:3, 3] = lage[:3, 3] + np.array(
                    [0.0, 1.4 * figurhoehe, 0.0])
                szene.add(licht, pose=self._blicken(lichtlage, blick))
                farbe, _t = werk.render(szene)
                yield np.asarray(farbe[:, :, :3], dtype=np.uint8)
        finally:
            werk.delete()

    def schreiben(self, ziel, fps=24, schleifen=2):
        import cv2
        os.makedirs(os.path.dirname(ziel) or '.', exist_ok=True)
        gesammelt = list(self.bilder_rendern())
        h, b = gesammelt[0].shape[:2]
        schreiber = cv2.VideoWriter(ziel, cv2.VideoWriter_fourcc(*'mp4v'),
                                    float(fps), (b, h))
        if not schreiber.isOpened():
            raise SystemExit(u'VideoWriter liess sich nicht oeffnen.')
        try:
            for _ in range(max(1, int(schleifen))):
                for bild in gesammelt:
                    schreiber.write(cv2.cvtColor(bild, cv2.COLOR_RGB2BGR))
        finally:
            schreiber.release()
        return ziel, len(gesammelt) * max(1, int(schleifen))


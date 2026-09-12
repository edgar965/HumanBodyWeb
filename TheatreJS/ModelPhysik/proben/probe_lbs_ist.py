# -*- coding: utf-8 -*-
u"""Was macht das reine Linear Blend Skinning mit unserem Netz?

WARUM: Der Browser haeutet mit `THREE.SkinnedMesh` — das ist LBS, ohne jede
posenabhaengige Korrektur. Gemessen werden die beiden klassischen Artefakte:

  Beugen    -> die Beuge faellt ein, der Querschnitt kollabiert
  Verdrehen -> "Candy Wrapper": der Querschnitt schnuert sich ein

Gemessen wird der Querschnittsumfang (konvexe Huelle der Punkte in einer
Scheibe senkrecht zur Knochenachse). Er braucht kein geschlossenes Netz und
ist deshalb belastbar, anders als ein Volumen ueber offene Raender.

DER ERSTE MESSVERSUCH WAR FALSCH und ist die Warnung wert: Ohne Beschraenkung
auf die Armpunkte schneidet die Ebene senkrecht zur Oberarmachse den ganzen
RUMPF mit — Ergebnis 207 cm "Oberarmumfang". Die Auswahl laeuft deshalb ueber
die Hautgewichte (ein Punkt gehoert zum Arm, wenn sein Gewicht dort
ueberwiegt), und die Ruhewerte sind die Gegenprobe: ein Oberarm hat rund
30 cm Umfang, nicht 200.

NUR LESEND auf `HumanBody/data`.
"""
import json
import sys

import numpy as np

WURZEL = r'A:\3DTools\HumanBody\data\humanBody'

#: Was noch als "Arm" gilt. Ohne die Hand — sie dreht mit und verfaelscht
#: die Scheiben am Handgelenk.
ARM_L = ('DEF-upper_arm.L', 'DEF-upper_arm.L.001',
         'DEF-forearm.L', 'DEF-forearm.L.001')


class Armmass:
    u"""Die Rechenbausteine der Probe: Drehungen, LBS, Scheibe, Umfang."""

    @staticmethod
    def quat_matrix(q):
        u"""[w, x, y, z] wie in `def_skeleton.json` -> 3x3."""
        w, x, y, z = q
        return np.array([
            [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
            [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
            [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
        ])

    @staticmethod
    def achsdrehung(achse, winkel):
        a = np.asarray(achse, dtype=np.float64)
        a = a / np.linalg.norm(a)
        k = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
        return np.eye(3) + np.sin(winkel) * k + (1 - np.cos(winkel)) * (k @ k)

    @staticmethod
    def haeuten(punkte, gewichte, ruhe, pose):
        u"""LBS wie Three.js: v' = sum_i w_i * (P_i * R_i^-1) * v."""
        delta = pose @ np.linalg.inv(ruhe)
        aus = np.zeros_like(punkte)
        for v, eintraege in enumerate(gewichte):
            p = np.append(punkte[v], 1.0)
            neu = np.zeros(4)
            for knochen, w in eintraege:
                neu += w * (delta[knochen] @ p)
            aus[v] = neu[:3]
        return aus

    @staticmethod
    def scheibe(punkte, auswahl, ursprung, achse, hoehe, dicke=0.010):
        u"""Punktnummern in einer Scheibe senkrecht zur Achse (Ruhelage)."""
        achse = achse / np.linalg.norm(achse)
        t = (punkte[auswahl] - ursprung) @ achse
        return auswahl[np.abs(t - hoehe) < dicke]

    @staticmethod
    def umfang(punkte, nummern, achse):
        u"""Umfang der konvexen Huelle DIESER Punkte, projiziert auf die Ebene
        senkrecht zur Achse.

        Gemessen wird immer dieselbe PUNKTMENGE, nicht dieselbe Raumstelle:
        Eine ortsfeste Scheibe laeuft leer, sobald das Glied wegdreht — der
        erste Versuch lieferte bei 90 Grad Beugung `None`.
        """
        from scipy.spatial import ConvexHull
        if len(nummern) < 8:
            return None
        achse = achse / np.linalg.norm(achse)
        hilf = np.array([1.0, 0.0, 0.0])
        if abs(achse @ hilf) > 0.9:
            hilf = np.array([0.0, 0.0, 1.0])
        u = np.cross(achse, hilf)
        u /= np.linalg.norm(u)
        w = np.cross(achse, u)
        rel = punkte[nummern]
        flach = np.stack([rel @ u, rel @ w], axis=1)
        rand = flach[ConvexHull(flach).vertices]
        strecken = np.linalg.norm(np.diff(np.vstack([rand, rand[:1]]), axis=0), axis=1)
        return float(strecken.sum() * 100.0)                      # cm

    @staticmethod
    def winkel_zwischen(a, b):
        return float(np.degrees(np.arccos(np.clip(
            a @ b / (np.linalg.norm(a) * np.linalg.norm(b)), -1, 1))))


class Skelett:

    def __init__(self, pfad):
        knochen = json.load(open(pfad))['bones']
        self.namen = [b['name'] for b in knochen]
        self.nummer = {n: i for i, n in enumerate(self.namen)}
        self.eltern = [self.nummer.get(b['parent'], -1) for b in knochen]
        self.lokal = []
        for b in knochen:
            m = np.eye(4)
            m[:3, :3] = Armmass.quat_matrix(b['local_quaternion'])
            m[:3, 3] = b['local_position']
            self.lokal.append(m)

    def welt(self, zusatz=None):
        u"""Weltmatrizen; `zusatz` = {knochenname: lokale 3x3-Drehung}.

        Rekursiv aufgeloest: Die Liste in `def_skeleton.json` ist NICHT
        topologisch sortiert — ein Kind kann vor seinem Elternteil stehen.
        """
        zusatz = zusatz or {}
        aus = [None] * len(self.lokal)

        def loesen(i):
            if aus[i] is not None:
                return aus[i]
            m = self.lokal[i].copy()
            dreh = zusatz.get(self.namen[i])
            if dreh is not None:
                r = np.eye(4)
                r[:3, :3] = dreh
                m = m @ r
            e = self.eltern[i]
            aus[i] = m if e < 0 else loesen(e) @ m
            return aus[i]

        for i in range(len(self.lokal)):
            loesen(i)
        return np.array(aus)


class LbsProbe:
    u"""Beugen und Verdrehen des linken Unterarms, Umfang je Messscheibe."""

    #: Messscheiben: Abstand vom Ellbogen entlang der Knochenachse (m).
    SCHEIBEN = ((-0.03, 'Oberarm  3 cm ueber'), (-0.06, 'Oberarm  6 cm ueber'),
                (0.03, 'Unterarm 3 cm unter'), (0.06, 'Unterarm 6 cm unter'))

    def __init__(self):
        self.punkte = np.load(WURZEL + r'\vertices_tpose.npy').astype(np.float64)
        roh = json.load(open(WURZEL + r'\skin_weights_base.json'))
        self.skelett = Skelett(WURZEL + r'\def_skeleton.json')
        umnummerieren = [self.skelett.nummer[n] for n in roh['bone_names']]
        self.gewichte = [[(umnummerieren[b], w) for b, w in e] for e in roh['weights']]
        arm = {self.skelett.nummer[n] for n in ARM_L}
        anteil = np.array([sum(w for b, w in e if b in arm) for e in self.gewichte])
        self.auswahl = np.where(anteil > 0.5)[0]
        self.ruhe = self.skelett.welt()
        self.i_ell = self.skelett.nummer['DEF-forearm.L']
        self.i_ober = self.skelett.nummer['DEF-upper_arm.L']
        self.ursprung = self.ruhe[self.i_ell][:3, 3]
        self.achse_ober = self.ruhe[self.i_ober][:3, 1]
        self.achse_unter = self.ruhe[self.i_ell][:3, 1]
        self.ruhewinkel = Armmass.winkel_zwischen(self.achse_ober, self.achse_unter)
        self.scheiben = {}

    def _ruheachse(self, hoehe):
        return self.achse_ober if hoehe < 0 else self.achse_unter

    def scheiben_bestimmen(self):
        u"""Die Messscheiben werden EINMAL in der Ruhelage bestimmt."""
        print('Netz %d Punkte, davon Arm links %d'
              % (len(self.punkte), len(self.auswahl)))
        print('Ellbogen bei %s, Ruhewinkel Ober-/Unterarm %.1f Grad'
              % (np.round(self.ursprung, 3), self.ruhewinkel))
        for hoehe, wo in self.SCHEIBEN:
            achse = self._ruheachse(hoehe)
            nummern = Armmass.scheibe(self.punkte, self.auswahl, self.ursprung,
                                      achse, hoehe)
            self.scheiben[wo] = (nummern, hoehe)
            print('  Ruhe %-20s dem Ellbogen: %5.2f cm (%d Punkte)'
                  % (wo, Armmass.umfang(self.punkte, nummern, achse), len(nummern)))

    def bericht(self, pose, neu):
        aus = []
        for wo, (nummern, hoehe) in self.scheiben.items():
            # Nach der Pose zeigt die Knochenachse woanders hin.
            pose_achse = (pose[self.i_ober] if hoehe < 0 else pose[self.i_ell])[:3, 1]
            u0 = Armmass.umfang(self.punkte, nummern, self._ruheachse(hoehe))
            u1 = Armmass.umfang(neu, nummern, pose_achse)
            if u0 is None or u1 is None:
                continue                      # Scheibe zu duenn besetzt
            aus.append((wo, u0, u1, 100.0 * (u1 - u0) / u0))
        return aus

    def _posieren(self, achse, grad):
        drehung = Armmass.achsdrehung(achse, np.radians(grad))
        pose = self.skelett.welt({'DEF-forearm.L': drehung})
        return pose, Armmass.haeuten(self.punkte, self.gewichte, self.ruhe, pose)

    def beugen(self):
        print('')
        print('--- Beugen (lokale X-Achse des Unterarms) ---')
        for grad in (30, 60, 90, 120):
            pose, neu = self._posieren([1, 0, 0], grad)
            echt = Armmass.winkel_zwischen(pose[self.i_ober][:3, 1],
                                           pose[self.i_ell][:3, 1]) - self.ruhewinkel
            teile = ['%s %5.2f -> %5.2f (%+6.1f %%)' % (wo.split()[0][:8], u0, u1, d)
                     for wo, u0, u1, d in self.bericht(pose, neu)
                     if '3 cm' in wo]
            print('  %3d Grad (echt %+5.1f):  %s   %s'
                  % (grad, echt, teile[0], teile[1]))

    def verdrehen(self):
        print('')
        print('--- Verdrehen um die Laengsachse (Candy-Wrapper) ---')
        for grad in (45, 90, 135, 180):
            pose, neu = self._posieren([0, 1, 0], grad)
            teile = ['%s %5.2f -> %5.2f (%+6.1f %%)'
                     % (wo.split()[2] + ' cm', u0, u1, d)
                     for wo, u0, u1, d in self.bericht(pose, neu)
                     if wo.startswith('Unterarm')]
            print('  %3d Grad:  Unterarm %s   %s' % (grad, teile[0], teile[1]))

    def laufen(self):
        self.scheiben_bestimmen()
        self.beugen()
        self.verdrehen()


def main():
    LbsProbe().laufen()


if __name__ == '__main__':
    sys.exit(main())

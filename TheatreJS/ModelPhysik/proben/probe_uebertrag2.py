# -*- coding: utf-8 -*-
u"""Machbarkeit, zweiter Anlauf: erst die Skelette zur Deckung bringen.

DER ERSTE ANLAUF (`probe_uebertrag_posedirs.py`) IST GESCHEITERT, und die
Zahl sagt auch warum: Die Punktzuordnung lag im Median 43,8 mm und im p90
263,5 mm daneben — auf einem Koerper, der 1,70 m gross ist. Eine Korrektur,
die am falschen Punkt abgeholt wird, wirkt nicht; gemessen kam sie mit
-18,2 statt -17,7 % sogar auf der falschen Seite heraus.

Zwei Ursachen, beide in `SMPL/uebertrag.py` (07.09.2026) schon benannt:

1. **Die Haltung war verschieden.** SMPLs Ruhelage haelt die Arme leicht
   abgesenkt, unsere T-Pose waagrecht. Am Oberarm liegen die Punkte damit
   zentimeterweit auseinander.
2. **Ausrichtung ueber den Schwerpunkt ist untauglich.** Unser Netz fuehrt
   6.213 Punkte in Zaehnen, Zunge und Augen; die ziehen den Mittelwert in
   den Kopf.

Hier wird stattdessen ueber die GELENKE ausgerichtet (Procrustes mit
Massstab) und die SMPL-Haltung an unsere angeglichen — dieselbe Reihenfolge
wie im vorhandenen Uebertrag.

NUR LESEND.
"""
import json
import sys

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, r'A:\3DTools')
sys.path.insert(0, r'A:\3DTools\HumanBodyWeb\TheatreJS\ModelPhysik\proben')

from SMPL.koerper import Smplkoerper                        # noqa: E402
from probe_lbs_ist import Skelett, Armmass, ARM_L, WURZEL   # noqa: E402

MODELLE = r'A:\3DTools\VideoToBVH\models\smpl'

#: SMPL-Gelenknummer -> unser DEF-Knochen (Kopf des Knochens).
#: Nur Gelenke, die in beiden Rigs dasselbe MEINEN.
PAARE = {
    0: 'DEF-spine', 1: 'DEF-thigh.L', 2: 'DEF-thigh.R',
    4: 'DEF-shin.L', 5: 'DEF-shin.R', 7: 'DEF-foot.L', 8: 'DEF-foot.R',
    12: 'DEF-spine.004', 15: 'DEF-spine.006',
    16: 'DEF-upper_arm.L', 17: 'DEF-upper_arm.R',
    18: 'DEF-forearm.L', 19: 'DEF-forearm.R',
    20: 'DEF-hand.L', 21: 'DEF-hand.R',
}
ELLBOGEN_SMPL, SCHULTER_L, SCHULTER_R = 18, 16, 17


class Smplraum:
    u"""Achsen, Ausrichtung und Armrichtung — die Rechenbausteine."""

    @staticmethod
    def hin(punkte):
        u"""Blender (Z oben) -> SMPL (Y oben)."""
        return np.stack([punkte[:, 0], punkte[:, 2], -punkte[:, 1]], axis=1)

    @staticmethod
    def zurueck(vektoren):
        return np.stack([vektoren[:, 0], -vektoren[:, 2], vektoren[:, 1]], axis=1)

    @staticmethod
    def procrustes(quelle, ziel):
        u"""Aehnlichkeitstransformation quelle -> ziel (Drehung, Massstab, Versatz)."""
        qm, zm = quelle.mean(axis=0), ziel.mean(axis=0)
        q, z = quelle - qm, ziel - zm
        u, s, vt = np.linalg.svd(q.T @ z)
        d = np.sign(np.linalg.det(vt.T @ u.T))
        r = vt.T @ np.diag([1, 1, d]) @ u.T
        massstab = s[:2].sum() + d * s[2]
        massstab /= (q ** 2).sum()
        return r, massstab, zm - massstab * (r @ qm)

    @staticmethod
    def armwinkel(gelenke, schulter, ellbogen):
        richtung = gelenke[ellbogen] - gelenke[schulter]
        return richtung / np.linalg.norm(richtung)


class Uebertragprobe:
    u"""Vier Schritte: Haltung angleichen, ausrichten, zuordnen, Wirkung messen."""

    def __init__(self):
        self.punkte = np.load(WURZEL + r'\vertices_tpose.npy').astype(np.float64)
        roh = json.load(open(WURZEL + r'\skin_weights_base.json'))
        self.skelett = Skelett(WURZEL + r'\def_skeleton.json')
        umnummerieren = [self.skelett.nummer[n] for n in roh['bone_names']]
        self.gewichte = [[(umnummerieren[b], w) for b, w in e] for e in roh['weights']]
        self.ruhe = self.skelett.welt()
        self.k = Smplkoerper.laden('FEMALE', MODELLE)
        self.smpl_rest = self.k.formen(None)
        self.nummern = sorted(PAARE)
        unsere_gelenke_roh = {n: self.ruhe[self.skelett.nummer[n]][:3, 3]
                              for n in PAARE.values()}
        self.unsere = Smplraum.hin(np.array([unsere_gelenke_roh[PAARE[i]]
                                             for i in self.nummern]))

    def haltung_angleichen(self):
        u"""1. SMPL-Arme in unsere T-Pose drehen."""
        smpl_gelenke = self.k.J_regressor @ self.smpl_rest
        unser_arm = Smplraum.armwinkel(
            {0: self.unsere[self.nummern.index(16)],
             1: self.unsere[self.nummern.index(18)]}, 0, 1)
        smpl_arm = Smplraum.armwinkel(smpl_gelenke, SCHULTER_L, ELLBOGEN_SMPL)
        # Winkel in der Frontalebene (x nach links, y nach oben)
        diff = (np.degrees(np.arctan2(unser_arm[1], unser_arm[0]))
                - np.degrees(np.arctan2(smpl_arm[1], smpl_arm[0])))
        print('Armrichtung: unsere %s, SMPL %s -> %.1f Grad angleichen'
              % (np.round(unser_arm, 3), np.round(smpl_arm, 3), diff))
        w = np.radians(diff)
        self.smpl_rest_t = self.k.posieren(self.smpl_rest, {
            SCHULTER_L: np.array([0.0, 0.0, w]),
            SCHULTER_R: np.array([0.0, 0.0, -w]),
        })

    def ausrichten(self):
        u"""2. Ueber die Gelenke ausrichten."""
        smpl_gelenke_t = self.k.J_regressor @ self.smpl_rest_t
        ziel = np.array([smpl_gelenke_t[i] for i in self.nummern])
        self.r, self.massstab, self.versatz = Smplraum.procrustes(self.unsere, ziel)
        rest = np.linalg.norm((self.massstab * (self.r @ self.unsere.T).T + self.versatz)
                              - ziel, axis=1)
        print('Gelenkpassung: %d Paare, Median %.1f mm, max %.1f mm, Massstab %.4f'
              % (len(ziel), np.median(rest) * 1000, rest.max() * 1000, self.massstab))

    def zuordnen(self):
        u"""3. Jeden unserer Punkte an den naechsten SMPL-Punkt."""
        unser_im_smpl = (self.massstab * (self.r @ Smplraum.hin(self.punkte).T).T
                         + self.versatz)
        abstand, self.zuordnung = cKDTree(self.smpl_rest_t).query(unser_im_smpl, workers=-1)
        print('Zuordnung: Median %.1f mm, p90 %.1f mm, max %.1f mm'
              % (np.median(abstand) * 1000, np.percentile(abstand, 90) * 1000,
                 abstand.max() * 1000))

    def _korrektur(self, wk):
        u"""SMPLs posedirs-Korrektur fuer die Ellbogenbeugung, in unseren Raum."""
        rot = np.tile(np.eye(3), (self.k.J_regressor.shape[0], 1, 1))
        rot[ELLBOGEN_SMPL] = self.k._rodrigues(np.array([0.0, 0.0, -wk]))
        merkmal = (rot[1:] - np.eye(3)).reshape(-1)
        korrektur_smpl = (self.k.posedirs @ merkmal)[self.zuordnung]
        rueck = np.linalg.inv(self.r) / self.massstab
        return Smplraum.zurueck((rueck @ korrektur_smpl.T).T)

    def wirkung(self):
        u"""4. Armumfang 3 cm ueber dem Ellbogen: LBS gegen LBS + Korrektur."""
        i_ell = self.skelett.nummer['DEF-forearm.L']
        i_ober = self.skelett.nummer['DEF-upper_arm.L']
        ursprung = self.ruhe[i_ell][:3, 3]
        achse_ober = self.ruhe[i_ober][:3, 1]
        arm = {self.skelett.nummer[n] for n in ARM_L}
        anteil = np.array([sum(wg for b, wg in e if b in arm) for e in self.gewichte])
        auswahl = np.where(anteil > 0.5)[0]
        messpunkte = Armmass.scheibe(self.punkte, auswahl, ursprung, achse_ober, -0.03)
        print('')
        print('Armumfang 3 cm ueber dem Ellbogen, %d Punkte' % len(messpunkte))
        print('%-10s %9s %24s %26s'
              % ('Beugung', 'Ruhe', 'nur LBS (heute)', 'LBS + SMPL-Korrektur'))
        u0 = Armmass.umfang(self.punkte, messpunkte, achse_ober)
        for grad in (30, 60, 90, 120):
            wk = np.radians(grad)
            pose = self.skelett.welt({'DEF-forearm.L': Armmass.achsdrehung([1, 0, 0], wk)})
            lbs = Armmass.haeuten(self.punkte, self.gewichte, self.ruhe, pose)
            mit = Armmass.haeuten(self.punkte + self._korrektur(wk), self.gewichte,
                                  self.ruhe, pose)
            pose_achse = pose[i_ober][:3, 1]
            u_lbs = Armmass.umfang(lbs, messpunkte, pose_achse)
            u_mit = Armmass.umfang(mit, messpunkte, pose_achse)
            print('%-10s %6.2f cm   %7.2f cm (%+6.1f %%)   %8.2f cm (%+6.1f %%)'
                  % ('%d Grad' % grad, u0, u_lbs, 100 * (u_lbs - u0) / u0,
                     u_mit, 100 * (u_mit - u0) / u0))

    def laufen(self):
        self.haltung_angleichen()
        self.ausrichten()
        self.zuordnen()
        self.wirkung()


def main():
    Uebertragprobe().laufen()


if __name__ == '__main__':
    sys.exit(main())

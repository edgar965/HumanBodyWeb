# -*- coding: utf-8 -*-
u"""Machbarkeit: SMPLs Pose-Korrektur auf UNSEREM Netz.

WARUM: `probe_lbs_ist.py` misst am HumanBody-Netz -17,7 % Armumfang bei
90 Grad Beugung. `probe_vergleich_beuge.py` zeigt, dass SMPLs Pose-Korrektur
zwei Drittel davon zurueckholt. Offen ist die Frage dazwischen: Laesst sich
diese Korrektur auf ein Netz FREMDER TOPOLOGIE uebertragen — 18.210 Punkte
gegen 6.890, andere Nummerierung, andere Proportionen?

Der Weg ist derselbe wie in `SMPL/uebertrag.py` (07.09.2026), nur in der
anderen Richtung: dort SMPL-Punkt -> fremder Punkt (fuer den Regressor),
hier fremder Punkt -> SMPL-Punkt (fuer die Korrektur).

WAS DIESE PROBE NICHT IST: kein Einbau. Die Zuordnung ist der naechste
Punkt (nicht baryzentrisch), und die Beugung wird an beiden Modellen
getrennt gesetzt statt ueber eine Retarget-Tabelle. Beides waere im
Einbau besser. Die Probe beantwortet nur: kommt die Korrektur ueberhaupt
an der richtigen Stelle heraus?

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
ELLBOGEN_SMPL = 18


class Posedirsuebertrag:
    u"""SMPLs `posedirs` ueber den naechsten Punkt auf das HumanBody-Netz."""

    GRADE = (30, 60, 90, 120)

    @staticmethod
    def nach_smpl_raum(punkte):
        u"""Blender (Z oben) -> SMPL (Y oben): (x, y, z) -> (x, z, -y)."""
        return np.stack([punkte[:, 0], punkte[:, 2], -punkte[:, 1]], axis=1)

    @staticmethod
    def zurueck(vektoren):
        u"""Die Gegenrichtung, fuer Verschiebungen."""
        return np.stack([vektoren[:, 0], -vektoren[:, 2], vektoren[:, 1]], axis=1)

    def __init__(self):
        # ---------------------------------------------------------- unser Netz
        self.punkte = np.load(WURZEL + r'\vertices_tpose.npy').astype(np.float64)
        roh = json.load(open(WURZEL + r'\skin_weights_base.json'))
        self.skelett = Skelett(WURZEL + r'\def_skeleton.json')
        umnummerieren = [self.skelett.nummer[n] for n in roh['bone_names']]
        self.gewichte = [[(umnummerieren[b], w) for b, w in e] for e in roh['weights']]
        # ------------------------------------------------------------ SMPL
        self.k = Smplkoerper.laden('FEMALE', MODELLE)
        self.smpl_rest = self.k.formen(None)
        self.massstab, self.zuordnung = self.zuordnen()
        self.ruhe = self.skelett.welt()
        self.i_ober = self.skelett.nummer['DEF-upper_arm.L']
        self.achse_ober = self.ruhe[self.i_ober][:3, 1]
        self.messpunkte = self._messpunkte()

    def zuordnen(self):
        u"""Beide in denselben Raum und auf dieselbe Hoehe; je Punkt der
        naechste SMPL-Punkt."""
        unser = self.nach_smpl_raum(self.punkte)
        unser_hoehe = unser[:, 1].max() - unser[:, 1].min()
        smpl_hoehe = self.smpl_rest[:, 1].max() - self.smpl_rest[:, 1].min()
        massstab = smpl_hoehe / unser_hoehe
        unser_gleich = ((unser - unser.mean(axis=0)) * massstab
                        + self.smpl_rest.mean(axis=0))
        print('Unser Netz %.3f m hoch, SMPL %.3f m — Massstab %.4f'
              % (unser_hoehe, smpl_hoehe, massstab))
        abstand, zuordnung = cKDTree(self.smpl_rest).query(unser_gleich, workers=-1)
        print('Zuordnung: Median %.1f mm, p90 %.1f mm, max %.1f mm'
              % (np.median(abstand) * 1000, np.percentile(abstand, 90) * 1000,
                 abstand.max() * 1000))
        return massstab, zuordnung

    def _messpunkte(self):
        u"""Die Scheibe 3 cm ueber dem Ellbogen, nur Armpunkte."""
        ursprung = self.ruhe[self.skelett.nummer['DEF-forearm.L']][:3, 3]
        arm = {self.skelett.nummer[n] for n in ARM_L}
        anteil = np.array([sum(w for b, w in e if b in arm) for e in self.gewichte])
        auswahl = np.where(anteil > 0.5)[0]
        return Armmass.scheibe(self.punkte, auswahl, ursprung, self.achse_ober, -0.03)

    def korrektur(self, w):
        u"""SMPLs Korrektur fuer diesen Ellbogenwinkel, auf unser Netz gebracht:
        Punkt fuer Punkt, Massstab und Achsen zurueck."""
        drehungen = {ELLBOGEN_SMPL: np.array([0.0, 0.0, -w])}
        rot = np.tile(np.eye(3), (self.k.J_regressor.shape[0], 1, 1))
        for i, vektor in drehungen.items():
            rot[i] = self.k._rodrigues(np.asarray(vektor, dtype=np.float64))
        merkmal = (rot[1:] - np.eye(3)).reshape(-1)
        korrektur_smpl = self.k.posedirs @ merkmal            # (6890, 3)
        return self.zurueck(korrektur_smpl[self.zuordnung]) / self.massstab

    def zeile(self, grad):
        w = np.radians(grad)
        pose = self.skelett.welt({'DEF-forearm.L': Armmass.achsdrehung([1, 0, 0], w)})
        lbs = Armmass.haeuten(self.punkte, self.gewichte, self.ruhe, pose)
        # Die Korrektur gilt in der RUHELAGE und wird mitgehaeutet — genau
        # wie bei SMPL, wo sie vor dem Skinning addiert wird.
        mit = Armmass.haeuten(self.punkte + self.korrektur(w), self.gewichte,
                              self.ruhe, pose)
        pose_achse = pose[self.i_ober][:3, 1]
        u0 = Armmass.umfang(self.punkte, self.messpunkte, self.achse_ober)
        u_lbs = Armmass.umfang(lbs, self.messpunkte, pose_achse)
        u_mit = Armmass.umfang(mit, self.messpunkte, pose_achse)
        return ('%-12s %8.2f cm   %8.2f cm (%+6.1f %%)   %8.2f cm (%+6.1f %%)'
                % ('%d Grad' % grad, u0,
                   u_lbs, 100 * (u_lbs - u0) / u0,
                   u_mit, 100 * (u_mit - u0) / u0))

    def gegenprobe(self):
        u"""In der RUHELAGE (keine Beugung) darf die Korrektur nichts tun."""
        null = np.abs(self.korrektur(0.0)).max()
        print('')
        print('Gegenprobe ohne Beugung: groesste Korrektur %.6f mm (muss 0 sein)'
              % (null * 1000))

    def laufen(self):
        print('')
        print('Armumfang 3 cm ueber dem Ellbogen, %d Punkte' % len(self.messpunkte))
        print('%-12s %10s %26s %26s'
              % ('Beugung', 'Ruhe', 'nur LBS (heute)', 'LBS + SMPL-Korrektur'))
        for grad in self.GRADE:
            print(self.zeile(grad))
        self.gegenprobe()


def main():
    Posedirsuebertrag().laufen()


if __name__ == '__main__':
    sys.exit(main())

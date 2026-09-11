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
from scipy.spatial import cKDTree, ConvexHull

sys.path.insert(0, r'A:\3DTools')
sys.path.insert(0, r'A:\3DTools\HumanBodyWeb\TheatreJS\ModelPhysik\proben')

from SMPL.koerper import Smplkoerper                        # noqa: E402
from probe_lbs_ist import (Skelett, achsdrehung, haeuten,    # noqa: E402
                           scheibe, umfang, ARM_L, WURZEL)

MODELLE = r'A:\3DTools\VideoToBVH\models\smpl'
ELLBOGEN_SMPL = 18


def nach_smpl_raum(punkte):
    u"""Blender (Z oben) -> SMPL (Y oben): (x, y, z) -> (x, z, -y)."""
    return np.stack([punkte[:, 0], punkte[:, 2], -punkte[:, 1]], axis=1)


def zurueck(vektoren):
    u"""Die Gegenrichtung, fuer Verschiebungen."""
    return np.stack([vektoren[:, 0], -vektoren[:, 2], vektoren[:, 1]], axis=1)


def main():
    # ---------------------------------------------------------- unser Netz
    punkte = np.load(WURZEL + r'\vertices_tpose.npy').astype(np.float64)
    roh = json.load(open(WURZEL + r'\skin_weights_base.json'))
    skelett = Skelett(WURZEL + r'\def_skeleton.json')
    umnummerieren = [skelett.nummer[n] for n in roh['bone_names']]
    gewichte = [[(umnummerieren[b], w) for b, w in e] for e in roh['weights']]

    # ------------------------------------------------------------ SMPL
    k = Smplkoerper.laden('FEMALE', MODELLE)
    smpl_rest = k.formen(None)

    # Beide in denselben Raum und auf dieselbe Hoehe.
    unser = nach_smpl_raum(punkte)
    unser_hoehe = unser[:, 1].max() - unser[:, 1].min()
    smpl_hoehe = smpl_rest[:, 1].max() - smpl_rest[:, 1].min()
    massstab = smpl_hoehe / unser_hoehe
    unser_gleich = (unser - unser.mean(axis=0)) * massstab + smpl_rest.mean(axis=0)
    print('Unser Netz %.3f m hoch, SMPL %.3f m — Massstab %.4f'
          % (unser_hoehe, smpl_hoehe, massstab))

    baum = cKDTree(smpl_rest)
    abstand, zuordnung = baum.query(unser_gleich)
    print('Zuordnung: Median %.1f mm, p90 %.1f mm, max %.1f mm'
          % (np.median(abstand) * 1000, np.percentile(abstand, 90) * 1000,
             abstand.max() * 1000))

    # ------------------------------------------------- Korrektur uebertragen
    ruhe = skelett.welt()
    i_ell = skelett.nummer['DEF-forearm.L']
    i_ober = skelett.nummer['DEF-upper_arm.L']
    ursprung = ruhe[i_ell][:3, 3]
    achse_ober = ruhe[i_ober][:3, 1]
    arm = {skelett.nummer[n] for n in ARM_L}
    anteil = np.array([sum(w for b, w in e if b in arm) for e in gewichte])
    auswahl = np.where(anteil > 0.5)[0]
    messpunkte = scheibe(punkte, auswahl, ursprung, achse_ober, -0.03)

    print('')
    print('Armumfang 3 cm ueber dem Ellbogen, %d Punkte' % len(messpunkte))
    print('%-12s %10s %26s %26s'
          % ('Beugung', 'Ruhe', 'nur LBS (heute)', 'LBS + SMPL-Korrektur'))
    for grad in (30, 60, 90, 120):
        w = np.radians(grad)
        # unser Netz beugen
        pose = skelett.welt({'DEF-forearm.L': achsdrehung([1, 0, 0], w)})
        lbs = haeuten(punkte, gewichte, ruhe, pose)

        # SMPLs Korrektur fuer denselben Winkel
        drehungen = {ELLBOGEN_SMPL: np.array([0.0, 0.0, -w])}
        rot = np.tile(np.eye(3), (k.J_regressor.shape[0], 1, 1))
        for i, vektor in drehungen.items():
            rot[i] = k._rodrigues(np.asarray(vektor, dtype=np.float64))
        merkmal = (rot[1:] - np.eye(3)).reshape(-1)
        korrektur_smpl = k.posedirs @ merkmal                # (6890, 3)

        # auf unser Netz: Punkt fuer Punkt, Massstab und Achsen zurueck
        korrektur = zurueck(korrektur_smpl[zuordnung]) / massstab
        # Die Korrektur gilt in der RUHELAGE und wird mitgehaeutet — genau
        # wie bei SMPL, wo sie vor dem Skinning addiert wird.
        mit = haeuten(punkte + korrektur, gewichte, ruhe, pose)

        pose_achse = pose[i_ober][:3, 1]
        u0 = umfang(punkte, messpunkte, achse_ober)
        u_lbs = umfang(lbs, messpunkte, pose_achse)
        u_mit = umfang(mit, messpunkte, pose_achse)
        print('%-12s %8.2f cm   %8.2f cm (%+6.1f %%)   %8.2f cm (%+6.1f %%)'
              % ('%d Grad' % grad, u0,
                 u_lbs, 100 * (u_lbs - u0) / u0,
                 u_mit, 100 * (u_mit - u0) / u0))

    # Gegenprobe: In der RUHELAGE (keine Beugung) darf die Korrektur nichts tun.
    rot = np.tile(np.eye(3), (k.J_regressor.shape[0], 1, 1))
    merkmal = (rot[1:] - np.eye(3)).reshape(-1)
    null = np.abs(zurueck(k.posedirs @ merkmal)[zuordnung]).max()
    print('')
    print('Gegenprobe ohne Beugung: groesste Korrektur %.6f mm (muss 0 sein)'
          % (null * 1000))


if __name__ == '__main__':
    sys.exit(main())

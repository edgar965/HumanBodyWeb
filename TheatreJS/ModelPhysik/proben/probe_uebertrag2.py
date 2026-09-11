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
from probe_lbs_ist import (Skelett, achsdrehung, haeuten,    # noqa: E402
                           scheibe, umfang, ARM_L, WURZEL)

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


def nach_smpl_raum(punkte):
    u"""Blender (Z oben) -> SMPL (Y oben)."""
    return np.stack([punkte[:, 0], punkte[:, 2], -punkte[:, 1]], axis=1)


def zurueck(vektoren):
    return np.stack([vektoren[:, 0], -vektoren[:, 2], vektoren[:, 1]], axis=1)


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


def armwinkel(gelenke, schulter, ellbogen):
    richtung = gelenke[ellbogen] - gelenke[schulter]
    return richtung / np.linalg.norm(richtung)


def main():
    punkte = np.load(WURZEL + r'\vertices_tpose.npy').astype(np.float64)
    roh = json.load(open(WURZEL + r'\skin_weights_base.json'))
    skelett = Skelett(WURZEL + r'\def_skeleton.json')
    umnummerieren = [skelett.nummer[n] for n in roh['bone_names']]
    gewichte = [[(umnummerieren[b], w) for b, w in e] for e in roh['weights']]
    ruhe = skelett.welt()

    k = Smplkoerper.laden('FEMALE', MODELLE)
    smpl_rest = k.formen(None)
    smpl_gelenke = k.J_regressor @ smpl_rest

    # --- 1. Haltung angleichen: SMPL-Arme in unsere T-Pose drehen ---------
    unsere_gelenke_roh = {n: ruhe[skelett.nummer[n]][:3, 3] for n in PAARE.values()}
    unsere = nach_smpl_raum(np.array([unsere_gelenke_roh[PAARE[i]]
                                      for i in sorted(PAARE)]))
    unser_arm = armwinkel(
        {0: unsere[list(sorted(PAARE)).index(16)],
         1: unsere[list(sorted(PAARE)).index(18)]}, 0, 1)
    smpl_arm = armwinkel(smpl_gelenke, SCHULTER_L, ELLBOGEN_SMPL)
    # Winkel in der Frontalebene (x nach links, y nach oben)
    diff = (np.degrees(np.arctan2(unser_arm[1], unser_arm[0]))
            - np.degrees(np.arctan2(smpl_arm[1], smpl_arm[0])))
    print('Armrichtung: unsere %s, SMPL %s -> %.1f Grad angleichen'
          % (np.round(unser_arm, 3), np.round(smpl_arm, 3), diff))

    w = np.radians(diff)
    smpl_rest_t = k.posieren(smpl_rest, {
        SCHULTER_L: np.array([0.0, 0.0, w]),
        SCHULTER_R: np.array([0.0, 0.0, -w]),
    })
    smpl_gelenke_t = k.J_regressor @ smpl_rest_t

    # --- 2. Ueber die Gelenke ausrichten ----------------------------------
    ziel = np.array([smpl_gelenke_t[i] for i in sorted(PAARE)])
    r, massstab, versatz = procrustes(unsere, ziel)
    rest = np.linalg.norm((massstab * (r @ unsere.T).T + versatz) - ziel, axis=1)
    print('Gelenkpassung: %d Paare, Median %.1f mm, max %.1f mm, Massstab %.4f'
          % (len(ziel), np.median(rest) * 1000, rest.max() * 1000, massstab))

    unser_im_smpl = massstab * (r @ nach_smpl_raum(punkte).T).T + versatz

    # --- 3. Zuordnung ------------------------------------------------------
    abstand, zuordnung = cKDTree(smpl_rest_t).query(unser_im_smpl)
    print('Zuordnung: Median %.1f mm, p90 %.1f mm, max %.1f mm'
          % (np.median(abstand) * 1000, np.percentile(abstand, 90) * 1000,
             abstand.max() * 1000))

    # --- 4. Wirkung messen -------------------------------------------------
    i_ell = skelett.nummer['DEF-forearm.L']
    i_ober = skelett.nummer['DEF-upper_arm.L']
    ursprung = ruhe[i_ell][:3, 3]
    achse_ober = ruhe[i_ober][:3, 1]
    arm = {skelett.nummer[n] for n in ARM_L}
    anteil = np.array([sum(wg for b, wg in e if b in arm) for e in gewichte])
    auswahl = np.where(anteil > 0.5)[0]
    messpunkte = scheibe(punkte, auswahl, ursprung, achse_ober, -0.03)
    print('')
    print('Armumfang 3 cm ueber dem Ellbogen, %d Punkte' % len(messpunkte))
    print('%-10s %9s %24s %26s'
          % ('Beugung', 'Ruhe', 'nur LBS (heute)', 'LBS + SMPL-Korrektur'))

    rueck = np.linalg.inv(r) / massstab
    for grad in (30, 60, 90, 120):
        wk = np.radians(grad)
        pose = skelett.welt({'DEF-forearm.L': achsdrehung([1, 0, 0], wk)})
        lbs = haeuten(punkte, gewichte, ruhe, pose)

        rot = np.tile(np.eye(3), (k.J_regressor.shape[0], 1, 1))
        rot[ELLBOGEN_SMPL] = k._rodrigues(np.array([0.0, 0.0, -wk]))
        merkmal = (rot[1:] - np.eye(3)).reshape(-1)
        korrektur_smpl = (k.posedirs @ merkmal)[zuordnung]
        korrektur = zurueck((rueck @ korrektur_smpl.T).T)

        mit = haeuten(punkte + korrektur, gewichte, ruhe, pose)
        pose_achse = pose[i_ober][:3, 1]
        u0 = umfang(punkte, messpunkte, achse_ober)
        u_lbs = umfang(lbs, messpunkte, pose_achse)
        u_mit = umfang(mit, messpunkte, pose_achse)
        print('%-10s %6.2f cm   %7.2f cm (%+6.1f %%)   %8.2f cm (%+6.1f %%)'
              % ('%d Grad' % grad, u0, u_lbs, 100 * (u_lbs - u0) / u0,
                 u_mit, 100 * (u_mit - u0) / u0))


if __name__ == '__main__':
    sys.exit(main())

# -*- coding: utf-8 -*-
u"""Derselbe Messwert an beiden Modellen: was eine Pose-Korrektur bringt.

WARUM: `probe_lbs_ist.py` zeigt, dass unser Netz beim Beugen Querschnitt
verliert (LBS ohne Korrektur). `probe_smpl_posedirs.py` zeigt, wie gross die
Korrektur bei SMPL ausfaellt. Diese Probe legt BEIDE auf dasselbe Mass:
Umfang einer festen Punktmenge am Oberarm, kurz oberhalb des Ellbogens.

Damit ist die Aussage "eine Pose-Korrektur haelt den Arm rund" belegt und
nicht behauptet — und zwar an SMPL, wo beide Varianten derselben Rechnung
verfuegbar sind.

Zusaetzlich: Woelbt sich der Bizeps? Gemessen als Umfangsaenderung in der
Mitte des Oberarms. Bei reinem LBS ist sie null (der Oberarm dreht gar
nicht mit), bei SMPL nicht.

NUR LESEND.
"""
import sys

import numpy as np
from scipy.spatial import ConvexHull

sys.path.insert(0, r'A:\3DTools')
from SMPL.koerper import Smplkoerper                        # noqa: E402

MODELLE = r'A:\3DTools\VideoToBVH\models\smpl'
ELLBOGEN_L, SCHULTER_L, HANDGELENK_L = 18, 16, 20


def ohne_posedirs(k, v_rest, drehungen):
    sicherung = k.posedirs
    k.posedirs = np.zeros_like(sicherung)
    try:
        return k.posieren(v_rest, drehungen)
    finally:
        k.posedirs = sicherung


def umfang(punkte, nummern, achse):
    u"""Umfang der konvexen Huelle dieser Punkte, senkrecht zur Achse (cm)."""
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
    return float(strecken.sum() * 100.0)


def main():
    for geschlecht in ('FEMALE', 'MALE'):
        k = Smplkoerper.laden(geschlecht, MODELLE)
        v_rest = k.formen(None)
        gelenke = k.J_regressor @ v_rest
        schulter, ellbogen = gelenke[SCHULTER_L], gelenke[ELLBOGEN_L]
        achse = ellbogen - schulter
        laenge = np.linalg.norm(achse)
        achse = achse / laenge

        # Punkte des linken Oberarms: Gewicht ueberwiegend an Schulter/Oberarm
        arm = k.weights[:, SCHULTER_L] > 0.5
        t = (v_rest - schulter) @ achse

        scheiben = {}
        for anteil, wo in ((0.85, 'kurz ueber dem Ellbogen'),
                           (0.50, 'Mitte des Oberarms')):
            nah = arm & (np.abs(t - anteil * laenge) < 0.010)
            scheiben[wo] = np.where(nah)[0]

        print('')
        print('=== SMPL %s: Oberarm links, %s ==='
              % (geschlecht, ', '.join('%s %d Punkte' % (w, len(n))
                                       for w, n in scheiben.items())))
        for grad in (30, 60, 90, 120):
            drehungen = {ELLBOGEN_L: np.array([0.0, 0.0, -np.radians(grad)])}
            mit = k.posieren(v_rest, drehungen)
            ohne = ohne_posedirs(k, v_rest, drehungen)
            teile = []
            for wo, nummern in scheiben.items():
                if len(nummern) < 8:
                    continue
                u0 = umfang(v_rest, nummern, achse)
                u_ohne = umfang(ohne, nummern, achse)
                u_mit = umfang(mit, nummern, achse)
                teile.append('%-24s Ruhe %5.2f | LBS %5.2f (%+5.1f %%) | '
                             'mit Korrektur %5.2f (%+5.1f %%)'
                             % (wo, u0, u_ohne, 100 * (u_ohne - u0) / u0,
                                u_mit, 100 * (u_mit - u0) / u0))
            print('  Ellbogen %3d Grad' % grad)
            for zeile in teile:
                print('      %s' % zeile)


if __name__ == '__main__':
    sys.exit(main())

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

Der Umfang kommt aus `Armmass` (probe_lbs_ist), das Abschalten der
Korrektur aus `Posedirsprobe` (probe_smpl_posedirs) — dieselbe Rechnung
stand hier vorher ein zweites Mal (Befund `freie-funktionen`, 12.09.2026).

NUR LESEND.
"""
import sys

import numpy as np

sys.path.insert(0, r'A:\3DTools')
sys.path.insert(0, r'A:\3DTools\HumanBodyWeb\TheatreJS\ModelPhysik\proben')

from SMPL.koerper import Smplkoerper                        # noqa: E402
from probe_lbs_ist import Armmass                           # noqa: E402
from probe_smpl_posedirs import Posedirsprobe               # noqa: E402

MODELLE = r'A:\3DTools\VideoToBVH\models\smpl'
ELLBOGEN_L, SCHULTER_L, HANDGELENK_L = 18, 16, 20


class Beugevergleich:
    u"""Oberarmumfang an SMPL: Ruhe, reines LBS, LBS mit Pose-Korrektur."""

    GRADE = (30, 60, 90, 120)
    SCHEIBEN = ((0.85, 'kurz ueber dem Ellbogen'), (0.50, 'Mitte des Oberarms'))

    def __init__(self, geschlecht):
        self.geschlecht = geschlecht
        self.k = Smplkoerper.laden(geschlecht, MODELLE)
        self.v_rest = self.k.formen(None)
        gelenke = self.k.J_regressor @ self.v_rest
        schulter, ellbogen = gelenke[SCHULTER_L], gelenke[ELLBOGEN_L]
        achse = ellbogen - schulter
        self.laenge = float(np.linalg.norm(achse))
        self.achse = achse / self.laenge
        self.scheiben = self._scheiben(schulter)

    def _scheiben(self, schulter):
        u"""Punkte des linken Oberarms in zwei Scheiben laengs der Achse."""
        arm = self.k.weights[:, SCHULTER_L] > 0.5
        t = (self.v_rest - schulter) @ self.achse
        scheiben = {}
        for anteil, wo in self.SCHEIBEN:
            nah = arm & (np.abs(t - anteil * self.laenge) < 0.010)
            scheiben[wo] = np.where(nah)[0]
        return scheiben

    def zeilen(self, grad):
        u"""Je Scheibe eine Zeile: Ruhe, LBS und mit Korrektur."""
        drehungen = {ELLBOGEN_L: np.array([0.0, 0.0, -np.radians(grad)])}
        mit = self.k.posieren(self.v_rest, drehungen)
        ohne = Posedirsprobe.ohne_posedirs(self.k, self.v_rest, drehungen)
        teile = []
        for wo, nummern in self.scheiben.items():
            u0 = Armmass.umfang(self.v_rest, nummern, self.achse)
            if u0 is None:
                continue
            u_ohne = Armmass.umfang(ohne, nummern, self.achse)
            u_mit = Armmass.umfang(mit, nummern, self.achse)
            teile.append('%-24s Ruhe %5.2f | LBS %5.2f (%+5.1f %%) | '
                         'mit Korrektur %5.2f (%+5.1f %%)'
                         % (wo, u0, u_ohne, 100 * (u_ohne - u0) / u0,
                            u_mit, 100 * (u_mit - u0) / u0))
        return teile

    def laufen(self):
        print('')
        print('=== SMPL %s: Oberarm links, %s ==='
              % (self.geschlecht,
                 ', '.join('%s %d Punkte' % (w, len(n))
                           for w, n in self.scheiben.items())))
        for grad in self.GRADE:
            print('  Ellbogen %3d Grad' % grad)
            for zeile in self.zeilen(grad):
                print('      %s' % zeile)


def main():
    for geschlecht in ('FEMALE', 'MALE'):
        Beugevergleich(geschlecht).laufen()


if __name__ == '__main__':
    sys.exit(main())

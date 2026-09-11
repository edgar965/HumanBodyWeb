# -*- coding: utf-8 -*-
u"""Wie gross ist die posenabhaengige Korrektur, die SMPL selbst mitbringt?

WARUM: Bevor irgendetwas gebaut wird, muss die Groessenordnung feststehen.
SMPL fuehrt `posedirs` (207 x 6890 x 3) — eine gelernte Korrektur der Haut je
Gelenkstellung. Sie ist im Projekt vorhanden (VideoToBVH/models/smpl) und wird
von `Smplkoerper.posieren` bereits angewandt. Gemessen wird der Unterschied
zwischen "mit" und "ohne" bei echten Beugewinkeln.

Kein Schreiben ausserhalb dieses Ordners, keine Produktivdaten angefasst.
"""
import sys
import numpy as np

sys.path.insert(0, r'A:\3DTools')
from SMPL.koerper import Smplkoerper                        # noqa: E402

MODELLE = r'A:\3DTools\VideoToBVH\models\smpl'

# SMPL-Kinematik: 0 Becken, 4/5 Knie, 18/19 Ellbogen, 16/17 Schulter
ELLBOGEN_L, KNIE_L, SCHULTER_L = 18, 4, 16


def ohne_posedirs(k, v_rest, drehungen):
    u"""Dieselbe Rechnung, nur ohne die Pose-Blendshapes."""
    sicherung = k.posedirs
    k.posedirs = np.zeros_like(sicherung)
    try:
        return k.posieren(v_rest, drehungen)
    finally:
        k.posedirs = sicherung


def volumen(punkte, flaechen):
    u"""Netzvolumen ueber das Divergenztheorem (Liter)."""
    a = punkte[flaechen[:, 0]]
    b = punkte[flaechen[:, 1]]
    c = punkte[flaechen[:, 2]]
    return abs(np.einsum('ij,ij->i', a, np.cross(b, c)).sum() / 6.0) * 1000.0


def messen(name, k, drehungen):
    v_rest = k.formen(None)
    mit = k.posieren(v_rest, drehungen)
    ohne = ohne_posedirs(k, v_rest, drehungen)
    weg = np.linalg.norm(mit - ohne, axis=1) * 1000.0        # mm
    betroffen = weg > 1.0
    print('%-22s  Punkte ueber 1 mm: %5d von %d (%.1f %%)'
          % (name, betroffen.sum(), len(weg), 100.0 * betroffen.mean()))
    print('%-22s  Median %5.2f mm   p99 %6.2f mm   max %6.2f mm'
          % ('', np.median(weg[betroffen]) if betroffen.any() else 0.0,
             np.percentile(weg, 99), weg.max()))
    print('%-22s  Volumen mit %7.3f l   ohne %7.3f l   Rest %7.3f l'
          % ('', volumen(mit, k.faces), volumen(ohne, k.faces),
             volumen(v_rest, k.faces)))
    return weg


def main():
    for geschlecht in ('FEMALE', 'MALE'):
        k = Smplkoerper.laden(geschlecht, MODELLE)
        print('\n=== SMPL %s: %d Punkte, posedirs %s ==='
              % (geschlecht, len(k.v_template), k.posedirs.shape))
        for grad in (30, 60, 90, 120):
            w = np.radians(grad)
            messen('Ellbogen %d Grad' % grad, k,
                   {ELLBOGEN_L: np.array([0.0, 0.0, -w])})
        for grad in (45, 90):
            w = np.radians(grad)
            messen('Knie %d Grad' % grad, k,
                   {KNIE_L: np.array([-w, 0.0, 0.0])})
            messen('Schulter %d Grad' % grad, k,
                   {SCHULTER_L: np.array([0.0, 0.0, -w])})


if __name__ == '__main__':
    main()

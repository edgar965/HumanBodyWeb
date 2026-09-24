# -*- coding: utf-8 -*-
"""Abstandswahrung: Der Arm kommt auf dem Ziel nicht naeher ans Bein als in der Quelle.

Befund Edgar (24.09.2026, Dance1 Bild 49): „der Arm kommt viel zu nahe zum
Bein" — mit gleichen Richtungen legte der kuerzere Rumpf des DEF-Rigs den
Ellbogen auf 0,31 statt 0,46 Oberschenkellaengen an den Oberschenkel.

EICHFALL MIT BEKANNTER WAHRHEIT: Kunstskelette mit Einheitsdrehungen, der
Gelenkort ist die Summe der Versaetze. Ziel: Ellbogen und Handgelenk 5 cm
neben der rechten Oberschenkelachse (0,125 Laengen). Quelle: derselbe Arm
30 cm daneben (0,75 Laengen, ueber dem Deckel `NAHBEREICH` 0,6).

1. Danach liegen Ellbogen und Handgelenk mindestens 0,9 x 0,6 Laengen weg,
   der naechste von beiden hoechstens 1,1 x 0,6 (nicht weiter als noetig).
2. Liegt die Quelle genauso nah, bleibt alles, wie es war.
3. Fehlt ein Knochen (kein `DEF-foot.L`), ist die Stufe aus.

Sabotage-Gegenproben (gelaufen 24.09.2026, `ProjektTemp/armbein/sabotage.py`):
`NAHBEREICH` auf 0 -> Fall 1 rot; in `_groesster_fehlbetrag` `soll - ist`
durch `ist - soll` -> Fall 2 rot, Fall 1 erst mit der Obergrenze (davor
gruen: das falsche Vorzeichen stoesst Punkte ab, die schon weit weg sind,
und schwenkte den Arm zufaellig ebenfalls hinaus).
"""

import unittest
from types import SimpleNamespace

import numpy as np

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.quaternion import Quat  # noqa: E402
from humanbody_core.skeleton.retarget.abstandswahrung import Abstandswahrung  # noqa: E402

#: Ort (m) je Gelenk des Ziels; Eltern.
ORTE = {
    'DEF-spine': ((0.0, 0.0, 0.0), None),
    'DEF-thigh.R': ((-0.1, 0.0, 0.0), 'DEF-spine'),
    'DEF-shin.R': ((-0.1, -0.4, 0.0), 'DEF-thigh.R'),
    'DEF-foot.R': ((-0.1, -0.8, 0.0), 'DEF-shin.R'),
    'DEF-thigh.L': ((0.1, 0.0, 0.0), 'DEF-spine'),
    'DEF-shin.L': ((0.1, -0.4, 0.0), 'DEF-thigh.L'),
    'DEF-foot.L': ((0.1, -0.8, 0.0), 'DEF-shin.L'),
    'DEF-upper_arm.R': ((-0.15, 0.4, 0.0), 'DEF-spine'),
    'DEF-forearm.R': ((-0.15, -0.1, 0.0), 'DEF-upper_arm.R'),
    'DEF-hand.R': ((-0.15, -0.3, 0.0), 'DEF-forearm.R'),
    'DEF-upper_arm.L': ((0.6, 0.4, 0.0), 'DEF-spine'),
    'DEF-forearm.L': ((0.9, 0.4, 0.0), 'DEF-upper_arm.L'),
    'DEF-hand.L': ((1.2, 0.4, 0.0), 'DEF-forearm.L'),
}
ARM_R = ('DEF-upper_arm.R', 'DEF-forearm.R', 'DEF-hand.R')


class Aufbau:
    """Kunstskelette und Lauf fuer ein Bild."""

    @staticmethod
    def skelett(orte):
        knochen = {}
        for name, (ort, elter) in orte.items():
            versatz = np.array(ort) - (np.array(orte[elter][0]) if elter else 0.0)
            knochen[name] = SimpleNamespace(name=name, parent_name=elter, local_pos=versatz)
        return SimpleNamespace(bones=knochen, bone_order=list(orte))

    @staticmethod
    def quelle(verschiebung_x):
        """BVH-Seite in cm: dieselben Orte, der rechte Arm um `verschiebung_x` m versetzt."""
        orte = {('b' + n): ((np.array(o) + ([verschiebung_x, 0, 0] if n in ARM_R else 0.0)) * 100,
                            'b' + e if e else None) for n, (o, e) in ORTE.items()}
        namen = list(orte)
        offsets = [np.array(o) - (np.array(orte[e][0]) if e else 0.0) for o, e in orte.values()]
        bvh = SimpleNamespace(offsets=np.array(offsets))
        idx = {n: i for i, n in enumerate(namen)}
        eltern = {n: e for n, (_, e) in orte.items() if e}
        return bvh, idx, eltern

    @classmethod
    def lauf(cls, verschiebung_x, orte=ORTE):
        skel = cls.skelett(orte)
        bvh, idx, eltern = cls.quelle(verschiebung_x)
        zuordnung = {n: 'b' + n for n in orte}
        stufe = Abstandswahrung(skel, bvh, zuordnung, idx, eltern)
        rig_welt = {n: Quat.ID.copy() for n in orte}
        welt_jetzt = {n: Quat.ID.copy() for n in idx}
        spuren = {n: np.tile(Quat.ID, 1) for n in orte}
        stufe.korrigieren(0, welt_jetzt, rig_welt, spuren)
        return stufe, rig_welt, spuren


class TestAbstandswahrung(unittest.TestCase):
    """Eichfall: Arm am Oberschenkel auf dem Ziel, weit weg in der Quelle."""

    def test_arm_rueckt_auf_den_quellabstand(self):
        stufe, rig_welt, _ = Aufbau.lauf(-0.25)
        orte = stufe.rig_orte(rig_welt)
        soll = Abstandswahrung.NAHBEREICH * 0.4
        abstaende = [stufe.abstand(orte[punkt], orte['DEF-thigh.R'], orte['DEF-shin.R'])[0]
                     for punkt in ('DEF-forearm.R', 'DEF-hand.R')]
        for abstand in abstaende:
            self.assertGreater(abstand, 0.9 * soll)
        # Nicht weiter als noetig: der naechste Punkt liegt AM Soll (gemessen
        # 0,238 bei 0,24; mit vertauschtem Vorzeichen schwenkte der Arm auf 0,586).
        self.assertLess(min(abstaende), 1.1 * soll)
        self.assertEqual(stufe.bilder, 1)

    def test_gleich_nahe_quelle_bleibt(self):
        stufe, rig_welt, spuren = Aufbau.lauf(0.0)
        self.assertEqual(stufe.bilder, 0)
        np.testing.assert_array_equal(spuren['DEF-upper_arm.R'], Quat.ID)

    def test_ohne_fuss_aus(self):
        orte = {n: w for n, w in ORTE.items() if n != 'DEF-foot.L'}
        stufe, _, _ = Aufbau.lauf(-0.25, orte)
        self.assertFalse(stufe.aktiv)

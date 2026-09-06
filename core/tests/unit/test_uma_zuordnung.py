# -*- coding: utf-8 -*-
u"""DEF -> UMA: die eine Tabelle, aus der alle BVH-Formate ihr UMA-Ziel bekommen.

WARUM (05.09.2026): Ein falscher Eintrag hier verdreht auf UMA jede
Animation aller Formate zugleich — die Tabelle ist der Engpass. Geprueft
wird mechanisch, was mechanisch pruefbar ist: dass jeder DEF-Name existiert,
dass kein UMA-Name doppelt vergeben ist, dass links links bleibt — und an
der echten GLB, dass jeder UMA-Name darin vorkommt und die Finger so liegen,
wie der Kopf von `uma_knochen.py` es behauptet.

DIE ECHTE GLB IST PFLICHT, kein Grund zum Ueberspringen (Befund
`uebersprungen`, 30.08.2026): Fehlt sie, ist das rot mit dem Pfad — sonst
meldete ein Rechner ohne Figurkatalog gruen, ohne die Tabelle je gegen die
Datei gehalten zu haben.

Aufruf:  python manage.py test core.tests.unit.test_uma_zuordnung
"""
import os

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.skeleton import (  # noqa: E402
    DEF_ZU_UMA, Gltfskelett, SkeletonGeometry, Umazuordnung)
from humanbody_core.skeleton.formats import (  # noqa: E402
    SkeletonCMU, SkeletonMixamo, SkeletonMocapNet)
from humanbody_core.skeleton.zuordnungspruefung import (  # noqa: E402
    Zuordnungspruefung)

#: Die GLB, die Unity exportiert hat — nur lesend.
UMA_GLB = os.path.join(str(settings.FIGUREN_KATALOG), 'uma', 'UmaKleidung.glb')


class TabelleTest(SimpleTestCase):

    databases = []

    def test_jeder_def_name_existiert(self):
        knochen = Zuordnungspruefung().knochen
        fehlend = [n for n in DEF_ZU_UMA if n not in knochen]
        self.assertEqual(fehlend, [])

    def test_kein_uma_name_doppelt(self):
        ziele = list(DEF_ZU_UMA.values())
        self.assertEqual(len(ziele), len(set(ziele)))

    def test_links_bleibt_links(self):
        for defname, uma in DEF_ZU_UMA.items():
            if defname.endswith('.L'):
                self.assertTrue(uma.startswith('Left'), (defname, uma))
            if defname.endswith('.R'):
                self.assertTrue(uma.startswith('Right'), (defname, uma))

    def test_die_wirbelsaeule_ist_lueckenlos_bis_auf_005(self):
        self.assertNotIn('DEF-spine.005', DEF_ZU_UMA)
        for n in ('DEF-spine', 'DEF-spine.001', 'DEF-spine.002',
                  'DEF-spine.003', 'DEF-spine.004', 'DEF-spine.006'):
            self.assertIn(n, DEF_ZU_UMA)


class AbleitungTest(SimpleTestCase):

    databases = []

    def test_mixamo_landet_auf_denselben_namen(self):
        zuordnung = Umazuordnung.fuer(SkeletonMixamo)
        self.assertEqual(zuordnung['LeftForeArm'], 'LeftForeArm')
        self.assertEqual(zuordnung['Hips'], 'Hips')
        self.assertEqual(zuordnung['Spine2'], 'Spine1')   # Mixamo hat einen mehr
        self.assertEqual(zuordnung['LeftHandThumb1'], 'LeftHandFinger05_01')

    def test_cmu_spine1_ist_umas_spine1(self):
        u"""CMU kennt kein Spine2; sein Spine1 traegt DEF-spine.003 = Spine1."""
        self.assertEqual(Umazuordnung.fuer(SkeletonCMU)['Spine1'], 'Spine1')

    def test_ohne_ziel_bleibt_ohne_ziel(self):
        u"""`Neck` zeigt bei den Biped-Formaten auf None — auch bei UMA."""
        self.assertIsNone(Umazuordnung.fuer(SkeletonMixamo)['Neck'])

    def test_die_reihenfolge_des_formats_bleibt(self):
        u"""Der erste Eintrag ist die Wurzel (`_wurzelknochen`)."""
        self.assertEqual(next(iter(Umazuordnung.fuer(SkeletonMixamo))), 'Hips')

    def test_ausnahmen_werden_uebersetzt(self):
        ausnahmen = Umazuordnung.ausnahmen(SkeletonMocapNet)
        for name in ausnahmen:
            self.assertIn(name, DEF_ZU_UMA.values())
        erwartet = [n for n in SkeletonMocapNet.SKIP_DIR_CORRECTION
                    if n in DEF_ZU_UMA]
        self.assertEqual(len(ausnahmen), len(erwartet))


class EchteGlbTest(SimpleTestCase):
    u"""Gegen die Datei, die Unity exportiert hat — nur lesend."""

    databases = []

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        assert os.path.isfile(UMA_GLB), (
            'UMA-GLB fehlt: %s — die Tabelle DEF_ZU_UMA kann nicht gegen '
            'die Datei gehalten werden' % UMA_GLB)
        cls.skelett = Gltfskelett(UMA_GLB)
        cls.welt = SkeletonGeometry.from_three(cls.skelett.knochen()) \
            .compute_world_transforms()

    def _ort(self, name):
        return self.welt[name]['world_pos']

    def _spitze(self, name):
        u"""Das Ende einer Knochenkette — mit oder ohne `_end`-Blatt.

        Manche Exportlaeufe schreiben zu jedem Blattknochen einen synthetischen
        Endpunkt `<name>_end` (232 Knoten), andere nicht (159). Beides ist
        gueltig; der Retarget liest die Endpunkte nicht. Der Test darf davon
        nicht abhaengen (06.09.2026: `UmaKleidung.glb` kam ohne sie zurueck).
        """
        return self._ort('%s_end' % name if '%s_end' % name in self.welt else name)

    def test_jeder_uma_name_kommt_in_der_glb_vor(self):
        namen = set(self.skelett.namen())
        fehlend = [n for n in DEF_ZU_UMA.values() if n not in namen]
        self.assertEqual(fehlend, [])

    def test_finger05_ist_der_daumen(self):
        u"""Der Daumen wurzelt am naechsten an der Handwurzel."""
        hand = self._ort('LeftHand')
        abstand = {n: np.linalg.norm(self._ort('LeftHandFinger0%s_01' % n) - hand)
                   for n in '12345'}
        self.assertEqual(min(abstand, key=abstand.get), '5', abstand)

    def test_finger01_ist_der_kleine_finger(self):
        u"""Der kleine Finger: kuerzeste Kette der vier Langfinger und am
        weitesten vom Daumen entfernt."""
        def laenge(n):
            return np.linalg.norm(self._spitze('LeftHandFinger0%s_03' % n)
                                  - self._ort('LeftHandFinger0%s_01' % n))
        self.assertEqual(min('1234', key=laenge), '1')
        daumen = self._ort('LeftHandFinger05_01')
        abstand = {n: np.linalg.norm(self._ort('LeftHandFinger0%s_01' % n) - daumen)
                   for n in '1234'}
        self.assertEqual(max(abstand, key=abstand.get), '1', abstand)

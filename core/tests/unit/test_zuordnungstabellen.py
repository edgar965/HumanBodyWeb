# -*- coding: utf-8 -*-
u"""Die BVH-nach-DEF-Zuordnungen — laufen jetzt bei jedem Testlauf mit.

WARUM DIESER TEST EXISTIERT (01.09.2026)
----------------------------------------
Die Pruefung gab es seit dem 13.08.2026, als Skript unter
``Docu/pruefe_zuordnungstabellen.py``. Sie las eine ZWEITE, von Hand
gefuehrte Fassung der Tabellen (``retarget_mappings.BVH_TO_RIGIFY``) —
nicht die, aus der der Retarget wirklich liest. Die Abschrift war
unvollstaendig: **SMPL (25 Eintraege) und MEDIAPIPE fehlten darin.**
Beide Formate wurden nie geprueft, und die Ausgabe sagte trotzdem
„Summe der Beanstandungen: 0".

Seither leitet ``retarget_mappings`` aus den Formatklassen ab, und die
Pruefung steht als ``Zuordnungspruefung`` im Kern. Dieser Test ruft
dieselbe Klasse auf — damit ein neues Format nicht wieder jahrelang
ungeprueft mitlaufen kann.

Aufruf:  python manage.py test core.tests.unit.test_zuordnungstabellen
"""
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.skeleton import Skeleton                      # noqa: E402
from humanbody_core.skeleton.zuordnungspruefung import (          # noqa: E402
    Zuordnungspruefung)


class ZuordnungstabellenTest(SimpleTestCase):
    u"""Tippfehler, doppelte Ziele und vertauschte Seiten."""

    databases = []

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pruefung = Zuordnungspruefung()

    def test_skelett_wird_erkannt(self):
        u"""Die Produktionsdatei liefert Knochen in beiden Schreibweisen."""
        knochen = self.pruefung.knochen
        self.assertIn('DEF-spine.006', knochen)
        self.assertIn('DEF-spine_006', knochen)

    def test_alle_formate_dabei(self):
        u"""Kein Format faellt aus der Pruefung — auch SMPL und MEDIAPIPE."""
        formate = set(self.pruefung.formate)
        for name in ('CMU', 'MIXAMO', 'MOCAPNET', 'OPENPOSE', 'AIST',
                     'BANDAI', 'SMPL', 'MEDIAPIPE'):
            self.assertIn(name, formate)

    def test_keine_beanstandungen(self):
        u"""Der ganze Bericht muss sauber sein."""
        zeilen, summe = self.pruefung.bericht()
        self.assertEqual(summe, 0, '\n'.join(zeilen))

    def test_unbekanntes_ziel_faellt_auf(self):
        u"""Gegenprobe: ein Tippfehler im Ziel muss rot werden."""
        class Kaputt(Skeleton):
            FORMAT = None
            BONE_MAP_TO_RIGIFY = {'Hips': 'DEF-spine.OO6'}
        _, funde = self.pruefung.format_pruefen(Kaputt)
        self.assertEqual(funde['unbekannt'], [('Hips', 'DEF-spine.OO6')])

    def test_doppeltes_ziel_faellt_auf(self):
        u"""Gegenprobe: zwei Namen auf denselben Knochen — der erste faellt weg."""
        class Doppelt(Skeleton):
            FORMAT = None
            BONE_MAP_TO_RIGIFY = {'Hips': 'DEF-spine', 'Root': 'DEF-spine'}
        _, funde = self.pruefung.format_pruefen(Doppelt)
        self.assertEqual(funde['doppelt'], [('Hips', 'Root', 'DEF-spine')])

    def test_mehrere_schreibweisen_bleiben_still(self):
        u"""Dasselbe Format mit `MEHRERE_SCHREIBWEISEN` meldet nichts."""
        class Zweisprachig(Skeleton):
            FORMAT = None
            MEHRERE_SCHREIBWEISEN = True
            BONE_MAP_TO_RIGIFY = {'lhand': 'DEF-hand.L', 'lHand': 'DEF-hand.L'}
        _, funde = self.pruefung.format_pruefen(Zweisprachig)
        self.assertEqual(funde['doppelt'], [])

    def test_vertauschte_seite_faellt_auf(self):
        u"""Gegenprobe: links auf rechts."""
        class Verdreht(Skeleton):
            FORMAT = None
            BONE_MAP_TO_RIGIFY = {'LeftHand': 'DEF-hand.R'}
        _, funde = self.pruefung.format_pruefen(Verdreht)
        self.assertEqual(funde['seite'], [('LeftHand', 'DEF-hand.R')])

    def test_face_hand_bones_zeigen_ins_skelett(self):
        u"""Die abgeleitete Gesichts-/Handliste trifft echte Knochen."""
        self.assertEqual(self.pruefung.listen_pruefen(), {})

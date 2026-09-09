# -*- coding: utf-8 -*-
u"""Die Ablage des Retargets traegt die Fassung der Regeln.

BEFUND (09.09.2026): `Retargetdaten.ablage` baute ihren Namen aus
Koerpergroesse, Format, Fusskorrektur und Delta-Weg — aus dem, was der
AUFRUFER mitgibt. Die Regeln selbst (Zuordnungstabellen,
`SKIP_DIR_CORRECTION`, der Motor) standen nicht darin.

Als an diesem Tag die Ausnahmelisten von CMU, Mixamo und Bandai
umgestellt wurden, lagen 132 solcher Ablagen neben den BVH-Dateien.
Alle waeren weiter gelesen worden: kein Fehler, keine Meldung, und die
Aenderung waere nirgends angekommen. Dieselbe Fehlerklasse wie in
`~/.claude/rules/artefakte-benennen.md`.

Die Faelle hier pruefen die EIGENSCHAFT, nicht die Zahl: Zwei
verschiedene Fassungen muessen verschiedene Dateien nennen, dieselbe
dieselbe. Die Gegenprobe unten faellt, wenn die Fassung aus dem Namen
verschwindet.
"""
from unittest import mock

from django.test import SimpleTestCase

from core.dienste.retargetdaten import Retargetdaten
from humanbody_core.skeleton.retarget import fassung
from humanbody_core.skeleton.formats import richtungsausnahmen
from humanbody_core.skeleton.formats.cmu import SkeletonCMU
from humanbody_core.skeleton.formats.mixamo import SkeletonMixamo
from humanbody_core.skeleton.formats.bandai import SkeletonBandai
from humanbody_core.skeleton.formats.aist_smpl import SkeletonAIST_SMPL

BVH = r'A:/3DTools/3DObjects/animations/bvh/Walk/01_01.bvh'


class RetargetfassungTest(SimpleTestCase):

    databases = []

    def _ablage(self, fassungsnummer):
        with mock.patch.object(fassung, 'REGELFASSUNG', fassungsnummer):
            # `ablage` liest die Konstante ueber den Modulnamen im
            # Dienst — deshalb dort ebenfalls setzen.
            import core.dienste.retargetdaten as dienst
            with mock.patch.object(dienst, 'REGELFASSUNG', fassungsnummer):
                return Retargetdaten(BVH).ablage

    def test_verschiedene_fassungen_verschiedene_dateien(self):
        u"""Sonst liest eine neue Regel das Ergebnis der alten."""
        self.assertNotEqual(self._ablage(1), self._ablage(2))

    def test_gleiche_fassung_gleiche_datei(self):
        u"""Ein Zwischenspeicher, der nie trifft, ist keiner."""
        self.assertEqual(self._ablage(7), self._ablage(7))

    def test_die_fassung_steht_im_namen(self):
        u"""Gegenprobe: verschwindet sie, faellt dieser Fall."""
        self.assertIn('_retarget_', self._ablage(3))
        # Der Name ist ein Hash — geprueft wird, dass die Fassung
        # eingeht, nicht wie sie geschrieben steht.
        self.assertNotEqual(self._ablage(3), self._ablage(4))

    def test_ausnahmelisten_stehen_wie_gemessen(self):
        u"""Die Entscheidung vom 09.09.2026, festgehalten.

        Nicht der Schoenheit halber: Wer eine Liste aendert, aendert das
        Ergebnis JEDER Bewegung dieses Formats. Faellt dieser Fall, ist
        das ein Anlass nachzumessen (`ProjektTemp/halshaltung.py`) — und
        `REGELFASSUNG` zu erhoehen.
        """
        hals = richtungsausnahmen.HALS_UND_KOPF
        fuesse = richtungsausnahmen.FUESSE_UND_KOPF
        # AIST nimmt Fuesse und Kopf aus.
        self.assertEqual(list(SkeletonAIST_SMPL.SKIP_DIR_CORRECTION),
                         list(fuesse))
        # Mixamo: nur Hals und Kopf. Der Hals steht damit bei 31,1 Grad
        # gegen die Brustachse (Ruhelage 31,3), ohne die Liste bei 14,7
        # — der Schwanenhals. Die Fuesse wuerden mit Korrektur
        # schlechter (`DEF-foot.R` 20,92 -> 32,95 Grad).
        self.assertEqual(list(SkeletonMixamo.SKIP_DIR_CORRECTION),
                         list(hals))
        # CMU UND BANDAI BLEIBEN LEER, und das ist gemessen: Bei CMU
        # ueberschiesst die Grundhaltung mit Liste (59,0 statt 18,1
        # Grad bei 31,3 Ruhelage), bei Bandai verschlechtert sie die
        # Beugung von 0,1 auf 8,9 Grad. Begruendung in
        # `richtungsausnahmen`, Eichfall in `test_halstreue`.
        for klasse in (SkeletonCMU, SkeletonBandai):
            self.assertEqual(list(klasse.SKIP_DIR_CORRECTION), [],
                             klasse.FORMAT)

    def test_die_ausnahmeliste_fuehrt_hals_und_kopf(self):
        u"""Was drinsteht, ist der Grund, warum AIST unauffaellig ist."""
        for name in ('DEF-spine.004', 'DEF-spine.006',
                     'DEF-foot.L', 'DEF-foot.R'):
            self.assertIn(name, richtungsausnahmen.FUESSE_UND_KOPF)
        self.assertEqual(len(richtungsausnahmen.FUESSE_UND_KOPF), 6)

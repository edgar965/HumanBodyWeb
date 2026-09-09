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
        fuesse = richtungsausnahmen.FUESSE_UND_KOPF
        # AIST nimmt Fuesse und Kopf aus - und ist das einzige Format,
        # bei dem der Hals unauffaellig ist.
        self.assertEqual(list(SkeletonAIST_SMPL.SKIP_DIR_CORRECTION),
                         list(fuesse))
        # CMU, MIXAMO und BANDAI korrigieren ueberall. Das ist am
        # 09.09.2026 nachgemessen und ABSICHTLICH so geblieben: Fuenf
        # Fassungen des Masses gaben fuenf verschiedene Antworten, und
        # die einzige unabhaengig bestaetigte sagt, dass CMUs
        # A_Pose-Dateien mit Ausnahmeliste schlechter werden
        # (11,0 -> 25,3 Grad). Begruendung in `richtungsausnahmen`.
        for klasse in (SkeletonCMU, SkeletonMixamo, SkeletonBandai):
            self.assertEqual(list(klasse.SKIP_DIR_CORRECTION), [],
                             klasse.FORMAT)

    def test_die_ausnahmeliste_fuehrt_hals_und_kopf(self):
        u"""Was drinsteht, ist der Grund, warum AIST unauffaellig ist."""
        for name in ('DEF-spine.004', 'DEF-spine.006',
                     'DEF-foot.L', 'DEF-foot.R'):
            self.assertIn(name, richtungsausnahmen.FUESSE_UND_KOPF)
        self.assertEqual(len(richtungsausnahmen.FUESSE_UND_KOPF), 6)

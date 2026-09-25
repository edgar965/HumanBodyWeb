# -*- coding: utf-8 -*-
u"""UMA_Python.Ausblendung — Verdraengen, Hides, HideTags, MeshHide (25.09.2026).

Kunstrezepte und Kunstslots, kein UMA-Projekt:

1. Ein Rezept, das `BottomUnderlayer` verdraengt, nimmt die Unterhose aus dem Bau.
2. `Hides` nimmt einen Slot aus den Wuenschen, auch einen des Basisrezepts.
3. `HideTags` nimmt Slots mit passendem Tag heraus.
4. MeshHide: `int[]` als Hex (Little Endian), Bit i = Dreieck i, vom niedrigsten
   Bit an (C# `BitArray(int[])`) — Dreiecke 0 und 2 von 4 fallen weg.
5. Ein MeshHide, dessen Ziel nicht im Bau ist, laesst alles stehen (wie Unity).

Sabotage: `bitorder='big'` in `bits` → Fall 4 rot (am echten Katalog gemessen:
die sichtbaren Beindreiecke lagen dann bis zum Knie statt nur am Knoechel).
"""
from types import SimpleNamespace

import numpy as np
from django.test import SimpleTestCase
from UMA_Python.ausblendung import Ausblendung


def _rezept(name, platz='', verdraengt=(), hides=(), felder=None):
    return SimpleNamespace(name=name, kleidungsplatz=platz, verdraengt=list(verdraengt),
                           blendet_aus=list(hides), felder=felder or {})


def _slot(name, dreiecke=4, tags=()):
    return SimpleNamespace(name=name, slotname=name, felder={'tags': list(tags)},
                           dreiecke=np.arange(dreiecke * 3).reshape(-1, 3))


class Ausblendungsfaelle(SimpleTestCase):

    def test_1_verdraengen(self):
        hose = _rezept('Hose', 'Legs', verdraengt=['BottomUnderlayer'])
        unterhose = _rezept('Unterhose', 'BottomUnderlayer')
        self.assertEqual([r.name for r in Ausblendung.rezepte([hose, unterhose])], ['Hose'])

    def test_2_hides(self):
        wuensche = [SimpleNamespace(name='FemaleLegs'), SimpleNamespace(name='Torso')]
        aus = Ausblendung.wuensche(wuensche, [_rezept('Hose', hides=['FemaleLegs'])])
        self.assertEqual([w.name for w in aus], ['Torso'])

    def test_3_hidetags(self):
        slots = [_slot('Haar', tags=['hiddenshorthair']), _slot('Kopf')]
        hut = _rezept('Hut', felder={'HideTags': ['hiddenshorthair']})
        self.assertEqual([s.name for s in Ausblendung.slots(slots, [hut], None)], ['Kopf'])

    def test_4_meshhide_bits(self):
        # Bits 0 und 2 gesetzt -> 0b0101 = 5 als int32 Little Endian: '05000000'
        self.assertEqual(list(Ausblendung.bits({'flags': '05000000', 'Count': 4})),
                         [True, False, True, False])
        bein = _slot('Bein')
        felder = {'m_Name': 'Probe', '_assetSlotName': 'Bein',
                  '_serializedFlags': [{'flags': '05000000', 'Count': 4}]}
        Ausblendung._verdecken([bein], felder)
        np.testing.assert_array_equal(bein.dreiecke, [[3, 4, 5], [9, 10, 11]])

    def test_5_ziel_fehlt(self):
        bein = _slot('Bein')
        felder = {'m_Name': 'Probe', '_assetSlotName': 'Bein_slot_baked_X',
                  '_serializedFlags': [{'flags': '0f000000', 'Count': 4}]}
        with self.assertLogs('core', level='WARNING'):
            Ausblendung._verdecken([bein], felder)
        self.assertEqual(len(bein.dreiecke), 4)

# -*- coding: utf-8 -*-
u"""Die Spuren eines Retargets kommen immer in derselben Reihenfolge.

WARUM DIESER TEST EXISTIERT (31.08.2026)
----------------------------------------
`Retargetlauf` führte die zugeordneten Knochen als **`set`**:

    self.mapped_rig_names = set(self.rig_to_bvh)

Die Iterationsreihenfolge eines Sets von Zeichenketten hängt an deren
Hashes, und die wählt Python **je Prozess zufällig**. Dieselbe
BVH-Datei, dreimal in getrennten Prozessen gerechnet:

    ['DEF-shin.L',     'DEF-toe.L',      'DEF-forearm.L']
    ['DEF-thigh.L',    'DEF-spine.006',  'DEF-upper_arm.L']
    ['DEF-shoulder.L', 'DEF-upper_arm.R','DEF-thigh.L']

Die Zahlen waren jedes Mal dieselben — die Ausgabe trotzdem nie zweimal
gleich. Das ist keine Kosmetik: Ein Ergebnis, das sich bei gleicher
Eingabe unterscheidet, lässt sich nicht zwischenspeichern, nicht
vergleichen und nicht gegenprüfen. Genau daran wäre die Gegenprobe zum
Umbau dieses Tages fast gescheitert.

Ein `dict` hält die Einfügereihenfolge, und `in` ist darauf genauso
schnell.

Der Test läuft ohne BVH-Datei: Er prüft die Datenstruktur, denn genau
sie ist die Zusicherung.

Aufruf:  python manage.py test core.tests.unit.test_retarget_reihenfolge
"""
import inspect

from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.skeleton.retarget.motor import Retargetlauf  # noqa: E402


class ReihenfolgeTest(SimpleTestCase):
    u"""Die zugeordneten Knochen liegen geordnet, nicht in einem Set."""

    def test_kein_set_im_quelltext(self):
        quelle = inspect.getsource(Retargetlauf._zuordnung_bauen)
        self.assertNotIn('set(self.rig_to_bvh)', quelle,
                         'mapped_rig_names darf kein `set` sein — die '
                         'Reihenfolge wäre je Prozess zufällig')
        self.assertIn('dict.fromkeys(self.rig_to_bvh)', quelle)

    def test_die_zuordnung_bleibt_in_ihrer_reihenfolge(self):
        u"""Was zuerst zugeordnet wird, steht zuerst in den Spuren."""
        lauf = Retargetlauf.__new__(Retargetlauf)
        lauf.rig_to_bvh = {}
        lauf.mapping = {}
        lauf.skel = _Skelett(['A', 'B', 'C', 'D'])
        lauf.mapping = {'bA': 'A', 'bB': 'B', 'bC': 'C', 'bD': 'D'}
        lauf.bvh_idx = {'bA': 0, 'bB': 1, 'bC': 2, 'bD': 3}
        lauf._zuordnung_bauen()
        self.assertEqual(list(lauf.mapped_rig_names), ['A', 'B', 'C', 'D'])

    def test_enthaeltpruefung_geht_weiter(self):
        u"""`in` muss auf der neuen Struktur genauso funktionieren."""
        lauf = Retargetlauf.__new__(Retargetlauf)
        lauf.rig_to_bvh = {}
        lauf.skel = _Skelett(['A', 'B'])
        lauf.mapping = {'bA': 'A', 'bB': 'B'}
        lauf.bvh_idx = {'bA': 0, 'bB': 1}
        lauf._zuordnung_bauen()
        self.assertIn('A', lauf.mapped_rig_names)
        self.assertNotIn('Z', lauf.mapped_rig_names)


class _Skelett:
    u"""Gerade so viel Skelett, wie `_zuordnung_bauen` anfasst."""

    def __init__(self, namen):
        self.bones = {n: object() for n in namen}

# -*- coding: utf-8 -*-
u"""G9passformvorgabe — `leggings` und `fallout_ranger_hose_body001` sitzen von sich aus länger (19.10.2026).

Edgar: „leggings und fallout_ranger_hose_body001 sollen bis zum Boden reichen". Kunstdaten, ohne Daz-Bibliothek.

1. Ein Stück mit Vorgabe bekommt die Länge, solange der Rumpf keine nennt — auch ohne Rumpf.
2. Nennt der Rumpf die Länge, auch als 0 (der Browser schickt nur Abweichungen von der Vorgabe), gilt die Vorgabe nicht.
3. Ein Stück ohne Vorgabe bekommt nichts.
4. `erweitern` setzt die Vorgabe nur am Längenregler, gibt eine Kopie zurück und lässt die Liste ohne Vorgabe, wie sie ist.

Sabotage (gedacht): in `werte` die Prüfung `G9passform.LAENGE in roh` weglassen → Fall 2 rot.
"""
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.passform import G9passform  # noqa: E402
from Genesis9.passformvorgabe import G9passformvorgabe  # noqa: E402


class Passformvorgabe(SimpleTestCase):
    databases = set()

    def test_1_bis_3_werte(self):
        laenge = G9passformvorgabe.LAENGE_CM['leggings']
        self.assertEqual(G9passformvorgabe.werte('leggings', None), {G9passform.LAENGE: laenge})
        self.assertEqual(G9passformvorgabe.werte('leggings', {'drapierung:abstand': 4.0}), {G9passform.LAENGE: laenge})
        self.assertEqual(G9passformvorgabe.werte('leggings', {G9passform.LAENGE: 0}), {})
        self.assertEqual(G9passformvorgabe.werte('leggings', {G9passform.LAENGE: 3.5}), {})
        self.assertEqual(G9passformvorgabe.werte('g9_base_shorts', None), {})

    def test_4_erweitern(self):
        regler = [{'name': G9passform.LAENGE, 'vorgabe': 0.0}, {'name': G9passform.WEITE, 'vorgabe': 0.0}]
        neu = G9passformvorgabe.erweitern('fallout_ranger_hose_body001', regler)
        self.assertEqual([r['vorgabe'] for r in neu], [G9passformvorgabe.LAENGE_CM['fallout_ranger_hose_body001'], 0.0])
        self.assertEqual(regler[0]['vorgabe'], 0.0, 'die abgelegte Liste bleibt unberührt')
        self.assertIs(G9passformvorgabe.erweitern('g9_base_shorts', regler), regler)

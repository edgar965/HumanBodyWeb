# -*- coding: utf-8 -*-
u"""`Morphgruppen`: die Morph-Kategorien in Gesicht, Körper und Fantasie.

WARUM (Edgar, 12.09.2026: „Die Morphs mach auch auf- zuklappbar, auch
Gesicht, Körper"): Die Zuordnung ist eine Tabelle; geprüft wird, dass sie
die 29 Kategorien von `/api/character/morphs/` VOLLSTÄNDIG verteilt (keine
landet unter „Weitere"), dass Unbekanntes trotzdem sichtbar bleibt, und
dass leere Bereiche wegfallen.

Sabotage-Gegenprobe: `'Neck'` aus der Körper-Liste → Fall 1 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'morphgruppen.js')

KATEGORIEN = ['Abdomen', 'Armpit', 'Arms', 'Body', 'Cheeks', 'Chest', 'Chin', 'Ears',
              'Elbows', 'Eyebrows', 'Eyelids', 'Eyes', 'Face', 'Fantasy', 'Feet',
              'Forehead', 'Hands', 'Head', 'Jaw', 'Legs', 'Mouth', 'Neck', 'Nose',
              'Pelvis', 'Shoulders', 'Stomach', 'Torso', 'Waist', 'Wrists']

SKRIPT = """
const { Morphgruppen: M } = await import(MODUL);
const alle = %s;
const aus = M.aufteilen(alle);
const namen = aus.map(([n]) => n);
const verteilt = aus.flatMap(([, k]) => k);
if (namen.includes(M.WEITERE)) {
    throw new Error('unter Weitere: ' + JSON.stringify(aus.at(-1)));
}
if (verteilt.length !== alle.length) {
    throw new Error('verteilt ' + verteilt.length + ' von ' + alle.length);
}
const fremd = M.aufteilen(['Nose', 'Quatsch']);
const soll = [['Gesicht', ['Nose']], ['Weitere', ['Quatsch']]];
if (JSON.stringify(fremd) !== JSON.stringify(soll)) {
    throw new Error('fremd: ' + JSON.stringify(fremd));
}
console.log(JSON.stringify({ ok: true, bereiche: namen,
                             groessen: aus.map(([, k]) => k.length) }));
""" % KATEGORIEN


class MorphgruppenTest(SimpleTestCase):

    def test_alle_kategorien_verteilt(self):
        aus = MODUL.laufen(SKRIPT)
        self.assertTrue(aus.get('ok'), aus)
        self.assertEqual(aus['bereiche'], ['Gesicht', 'Körper', 'Fantasie'])
        self.assertEqual(aus['groessen'], [12, 16, 1])

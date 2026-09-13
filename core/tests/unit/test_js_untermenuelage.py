# -*- coding: utf-8 -*-
u"""`Untermenuelage`: ein Untermenü liegt immer ganz im Fenster.

Edgar (13.09.2026, BVH Studio): „kann nun das Kontextmenü nicht mehr bedienen -
beim Hinzufügen einer Animation klappt es zu". Gemessen bei 1548 × 804: Das
Spurmenü stand am unteren Rand (top 632), die Ordnerliste reichte bis 1031,
die Animationsliste zu „Dance" von 780 bis 1180 — außerhalb des Fensters.

1. Platz genug: rechts neben dem Eintrag, fünf Pixel höher.
2. Unten zu wenig: hochgeschoben, Unterkante zehn Pixel über dem Rand.
3. Rechts zu wenig: links neben den Eintrag.
4. Höher als das Fenster: gedeckelt auf Fensterhöhe minus zwei Ränder,
   oben am Rand; nie über 400.

Sabotage-Gegenprobe: `fensterHoehe - rand - hoch` → `fensterHoehe - hoch`
in `rechnen` → Fall 2 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('bvh_studio', 'untermenuelage.js')

SKRIPT = """
const { Untermenuelage } = await import(MODUL);
const fehler = [];
const fehl = (t) => fehler.push(t);
const gleich = (a, b, t) => { if (JSON.stringify(a) !== JSON.stringify(b)) fehl(t + ': ' + JSON.stringify(a) + ' statt ' + JSON.stringify(b)); };
const eintrag = (top) => ({ left: 829, right: 1008, top, bottom: top + 34 });

// --- 1. Platz genug ------------------------------------------------------------
gleich(Untermenuelage.rechnen(eintrag(300), 218, 400, 1548, 804), { left: 1008, top: 295 }, 'Platz genug');

// --- 2. unten zu wenig: hoch ------------------------------------------------------
gleich(Untermenuelage.rechnen(eintrag(637), 218, 400, 1548, 804), { left: 1008, top: 394 }, 'unten zu wenig');
gleich(Untermenuelage.rechnen(eintrag(785), 296, 400, 1548, 804), { left: 1008, top: 394 }, 'Dance-Liste');

// --- 3. rechts zu wenig: links daneben -------------------------------------------
gleich(Untermenuelage.rechnen({ left: 1300, right: 1480, top: 300 }, 296, 200, 1548, 804),
       { left: 1004, top: 295 }, 'rechts zu wenig');
gleich(Untermenuelage.rechnen({ left: 100, right: 280, top: 300 }, 400, 200, 500, 804),
       { left: 10, top: 295 }, 'nirgends Platz: am linken Rand');

// --- 4. höher als das Fenster ------------------------------------------------------
if (Untermenuelage.hoechstens(804) !== 400) fehl('hoechstens(804): ' + Untermenuelage.hoechstens(804));
if (Untermenuelage.hoechstens(300) !== 280) fehl('hoechstens(300): ' + Untermenuelage.hoechstens(300));
gleich(Untermenuelage.rechnen(eintrag(200), 218, 400, 1548, 300), { left: 1008, top: 10 }, 'kleines Fenster');

console.log(JSON.stringify({ ok: fehler.length === 0, fehler }));
"""


class UntermenuelageTest(SimpleTestCase):

    databases = set()

    def test_ein_untermenue_bleibt_im_fenster(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

# -*- coding: utf-8 -*-
u"""BVH Studio: Abspielleiste bei den Animationen, „Endlos" am Ende der
letzten Animation.

WARUM (Edgar, 11.09.2026): „verschiebe die Play Leiste nach links in den Tab
mit den Animationen. Mach einen Button «Endlos» mit dem das Video von vorne
abgespielt wird wenn die letzte Animation zu ende ist."

Bis dahin sprang der Abspielkopf immer am Ende der PROJEKTDAUER auf 0 — die
ist das Ende des längsten Clips über ALLE Spuren (Modellclips mindestens 300
Bilder, Tonspuren minutenlang), die Figur stand also still, bis der Ton aus
war. Geprüft in Node, ohne DOM:

1. Das Ende ist der späteste Clip einer BEWEGUNGSspur; Ton-, Modell- und
   Lichtclips zählen nicht. Ohne Bewegungsclips gilt die Projektdauer.
2. Vor dem Ende läuft es weiter; am Ende ohne Endlos: anhalten am Ende;
   mit Endlos: auf 0. Leeres Projekt: bleibt bei 0.
3. Start hinter dem Ende beginnt von vorn.

Dazu die Verdrahtung: Leiste in der Seitenleiste (nicht mehr unter der
Zeitleiste), Knopf `pb-loop`, Schleife fragt `Abspielende`.

Sabotage-Gegenprobe: `type !== 'bvh'` entfernt → Fall 1 rot.
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

WURZEL = Path(settings.BASE_DIR)
STUDIO = Jsmodul.VIEWER / 'bvh_studio'

MODUL = Jsmodul('bvh_studio', 'abspielende.js')

SKRIPT = """
const { Abspielende } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
const spur = (type, ...enden) => ({ type, clips: enden.map(e => ({ endFrame: e })) });
// 1. Ende = letzte Animation, nicht der längste Clip
const spuren = [spur('bvh', 300, 1004), spur('audio', 5520), spur('model', 4530), spur('light', 200)];
pruefe('letzte Animation', Abspielende.bild(spuren, 30, 184), 1004);
pruefe('zwei Bewegungsspuren', Abspielende.bild([spur('bvh', 100), spur('bvh', 250)], 30, 9), 250);
pruefe('ohne Bewegung: Projektdauer', Abspielende.bild([spur('audio', 5520)], 30, 184), 5520);
pruefe('leer', Abspielende.bild([], 30, 0), 0);
// 2. Weiter, anhalten, von vorn
pruefe('davor', Abspielende.naechstes(500, 1004, false), { bild: 500, anhalten: false });
pruefe('am Ende ohne Endlos', Abspielende.naechstes(1004, 1004, false), { bild: 1004, anhalten: true });
pruefe('hinter dem Ende ohne Endlos', Abspielende.naechstes(1010, 1004, false), { bild: 1004, anhalten: true });
pruefe('am Ende mit Endlos', Abspielende.naechstes(1004, 1004, true), { bild: 0, anhalten: false });
pruefe('leeres Projekt', Abspielende.naechstes(7, 0, true), { bild: 0, anhalten: false });
// 3. Start hinter dem Ende
pruefe('Start am Ende', Abspielende.startbild(1004, 1004), 0);
pruefe('Start mittendrin', Abspielende.startbild(40, 1004), 40);
pruefe('Start leer', Abspielende.startbild(40, 0), 40);
console.log(JSON.stringify({ok: true}));
"""


class AbspielendeTest(SimpleTestCase):

    databases = set()

    def test_ende_und_endlos(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class AbspielendeVerdrahtungTest(SimpleTestCase):

    databases = set()

    def test_die_leiste_steht_in_der_seitenleiste(self):
        html = (WURZEL / 'templates' / 'bvh_studio.html').read_text(encoding='utf-8')
        seitenleiste = html[html.index('id="studio-sidebar"'):html.index('<!-- Library context menus -->')]
        self.assertIn('id="studio-playback"', seitenleiste)
        self.assertIn('id="pb-loop"', seitenleiste)
        self.assertIn('id="pb-speed"', seitenleiste)
        self.assertEqual(html.count('class="studio-playback"'), 1, 'die Leiste darf nur einmal stehen')

    def test_die_schleife_fragt_abspielende(self):
        schleife = (STUDIO / 'studioschleife.js').read_text(encoding='utf-8')
        self.assertIn('Abspielende.naechstes(state.playheadFrame, abspielende(), state.endlos)', schleife)
        self.assertIn('if (naechstes.anhalten) pausePlayback()', schleife)
        self.assertNotIn('state.playheadFrame = 0;   // von vorn', schleife)
        abspiel = (STUDIO / 'playback.js').read_text(encoding='utf-8')
        self.assertIn('Endlosschalter.binden()', abspiel)
        self.assertIn('Abspielende.startbild(state.playheadFrame, abspielende())', abspiel)
        schalter = (STUDIO / 'endlosschalter.js').read_text(encoding='utf-8')
        self.assertIn("getElementById('pb-loop')", schalter)
        self.assertIn('state.endlos = !state.endlos', schalter)

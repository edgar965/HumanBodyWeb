# -*- coding: utf-8 -*-
"""`Schluesselpaar` — die Keyframe-Suche gegen die alte, doppelte Schleife.

WARUM DIESER TEST (17.08.2026)
=============================
Die Suche „welche zwei Keyframes umgeben dieses Bild" stand in `spur_anwenden.js`
ZWEIMAL buchstabengleich (Kamera und Licht) und ist jetzt eine Klasse. Ein Fehler
darin fällt beim Ansehen NICHT auf: Die Wiedergabe läuft weiter, die Werte sind
nur die falschen — eine Kamera, die den ersten Keyframe hält, sieht aus wie eine
Kamera, die noch nicht losgeflogen ist.

Deshalb steht die alte Fassung hier im Skript nochmal und wird gegen die neue
Klasse gerechnet, auf den Fällen, die weh tun:

    Bild 0    vor dem ersten Keyframe  -> beide = erster  (Rückfall)
    Bild 50   zwischen zwei            -> Anteil 0,5
    Bild 100  genau auf dem zweiten    -> beide = zweiter
    Bild 200  hinter dem letzten       -> beide = letzter (Rückfall)
    zwei Keyframes auf DEMSELBEN Bild  -> Sprung, kein Mischen (Division durch 0)

Dazu die Gewichtung: `smooth` ist `3t²−2t³` (bei 0,5 genau 0,5, bei 0,25 aber
0,156), `step` bleibt auf 0.

Ohne `node` im Pfad wird der Test übersprungen, nicht rot.
"""
import shutil
import unittest
from pathlib import Path

from djangobase.testhelfer import Webmodul

WURZEL = Path(__file__).resolve().parents[3]
MODUL = WURZEL / 'static' / 'viewer' / 'bvh_studio' / 'schluesselpaar.js'
STATIC_WURZELN = {
    '/static/djangobase/': Path(__import__('djangobase').__file__).parent
                           / 'static' / 'djangobase',
    '/static/': WURZEL / 'static',
}

SKRIPT = """
const { Schluesselpaar } = await import(MODUL);

const clips = [
    { startFrame: 0,   data: { fade: true, intensity: 0,  interpolation: 'linear' } },
    { startFrame: 100, data: { fade: true, intensity: 10, interpolation: 'linear' } },
];

// --- die ALTE, doppelte Schleife, unveraendert aus spur_anwenden.js ---
function alt(kfs, frame) {
    let prev = null, next = null;
    for (let i = 0; i < kfs.length; i++) {
        if (kfs[i].startFrame <= frame) prev = kfs[i];
        if (kfs[i].startFrame >= frame && !next) next = kfs[i];
    }
    if (!prev && !next) return null;
    if (!prev) prev = next;
    if (!next) next = prev;
    return { prev, next };
}

const ergebnis = { paare: [], anteile: [], glatt: [], stufe: [], sonderfaelle: {} };
for (const frame of [-10, 0, 25, 50, 100, 200]) {
    const a = alt(clips, frame);
    const neu = Schluesselpaar.finden(clips, frame);
    ergebnis.paare.push([
        a.prev.startFrame === neu.vorher.startFrame,
        a.next.startFrame === neu.nachher.startFrame,
    ]);
    ergebnis.anteile.push(Number(neu.anteil.toFixed(4)));
}

// Gewichtung je Interpolationsart
for (const [art, ziel] of [['smooth', 'glatt'], ['step', 'stufe']]) {
    const eigene = [
        { startFrame: 0,   data: { fade: true, interpolation: art } },
        { startFrame: 100, data: { fade: true, interpolation: art } },
    ];
    for (const frame of [25, 50, 75]) {
        ergebnis[ziel].push(Number(
            Schluesselpaar.finden(eigene, frame).gewichtung.toFixed(4)));
    }
}

// Sonderfaelle
ergebnis.sonderfaelle.ohneClips = Schluesselpaar.finden([], 10);
ergebnis.sonderfaelle.einer = Schluesselpaar.finden([clips[0]], 50).sprung;
const gleich = [
    { startFrame: 60, data: { fade: true, trackPosition: 'upper' } },
    { startFrame: 60, data: { fade: true, trackPosition: 'lower' } },
];
ergebnis.sonderfaelle.gleichesBild = Schluesselpaar.finden(gleich, 60).sprung;
ergebnis.sonderfaelle.anteilGleichesBild =
    Schluesselpaar.finden(gleich, 60).anteil;
const ohneFade = [
    { startFrame: 0,   data: { fade: false } },
    { startFrame: 100, data: { fade: true } },
];
ergebnis.sonderfaelle.fadeAus = Schluesselpaar.finden(ohneFade, 50).sprung;
ergebnis.sonderfaelle.mischen =
    Schluesselpaar.finden(clips, 50).mischen('intensity');
ergebnis.sonderfaelle.mischenFehlend =
    Schluesselpaar.finden(clips, 50).mischen('gibtsnicht');
console.log(JSON.stringify(ergebnis));
"""


@unittest.skipUnless(shutil.which('node'), 'node fehlt')
class SchluesselpaarTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ergebnis = Webmodul(MODUL, STATIC_WURZELN).laufen(SKRIPT)

    def test_paare_wie_die_alte_schleife(self):
        """Für jedes geprüfte Bild dasselbe Paar wie vorher."""
        for vorher, nachher in self.ergebnis['paare']:
            self.assertTrue(vorher, 'vorheriger Keyframe weicht ab')
            self.assertTrue(nachher, 'nächster Keyframe weicht ab')

    def test_anteile_nachgerechnet(self):
        """Bilder -10, 0, 25, 50, 100, 200 bei Keyframes 0 und 100."""
        self.assertEqual(self.ergebnis['anteile'],
                         [0.0, 0.0, 0.25, 0.5, 0.0, 0.0])

    def test_glatte_gewichtung(self):
        """`smooth` = 3t²−2t³: bei 0,25 -> 0,1563, bei 0,5 -> 0,5."""
        self.assertEqual(self.ergebnis['glatt'], [0.1563, 0.5, 0.8438])

    def test_stufe_bleibt_auf_null(self):
        self.assertEqual(self.ergebnis['stufe'], [0.0, 0.0, 0.0])

    def test_sonderfaelle(self):
        sonder = self.ergebnis['sonderfaelle']
        self.assertIsNone(sonder['ohneClips'], 'ohne Keyframes kein Paar')
        self.assertTrue(sonder['einer'], 'ein Keyframe = Sprung')
        self.assertTrue(sonder['gleichesBild'],
                        'zwei Keyframes am gleichen Bild = Sprung')
        self.assertEqual(sonder['anteilGleichesBild'], 0,
                         'kein Teilen durch 0')
        self.assertTrue(sonder['fadeAus'], 'fade=false = harter Wechsel')

    def test_mischen(self):
        sonder = self.ergebnis['sonderfaelle']
        self.assertEqual(sonder['mischen'], 5, '0 und 10 in der Mitte')
        self.assertIsNone(sonder['mischenFehlend'],
                          'ein Feld, das es nicht gibt, ergibt nichts')

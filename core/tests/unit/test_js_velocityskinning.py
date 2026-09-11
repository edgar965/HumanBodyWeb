# -*- coding: utf-8 -*-
u"""Die JavaScript-Fassung von Velocity Skinning gegen die Python-Fassung.

ZWEI FASSUNGEN DERSELBEN RECHNUNG laufen irgendwann auseinander — die eine
wird korrigiert, die andere nicht, und im Browser sieht die Figur anders
aus als im Server-Video. Dieser Test haelt beide an DIESELBEN Zahlen:
`VelocitySkinning_Python/fixture.py` rechnet mit der Python-Fassung und
legt Eingabe und Ergebnis ab (`fixture.json`); hier rechnet Node dieselben
Eingaben mit `gemeinsam/velocityskinning.js` nach.

Gleichheit auf 1e-9 — beide rechnen in double, es gibt keinen Grund fuer
mehr Spiel. Und ein Fall MUSS dabei den Deckel treffen (grosser Winkel),
sonst prueft der Test nur die einfache Haelfte der Formel.

Fehlt die Fixture, wird sie NICHT still uebersprungen: Der Test sagt, wie
sie entsteht. Ein gruener Test ohne Fixture waere ein Test ohne Inhalt.
"""
import json
import os

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'velocityskinning.js')
FIXTURE = os.path.join(str(settings.TOOLS_ROOT), 'VelocitySkinning_Python',
                       'fixture.json')

SKRIPT = """
const { Velocityskinning: V } = await import(MODUL);
const F = FIXTURE;
const TOLERANZ = 1e-9;
let geprueft = 0, deckel = 0;
const flach = (liste) => Float64Array.from(liste.flat());
const vergleichen = (was, ist, soll) => {
    const s = soll.flat();
    for (let i = 0; i < s.length; i++) {
        if (Math.abs(ist[i] - s[i]) > TOLERANZ) {
            throw new Error(`${was}: Index ${i} ist ${ist[i]} statt ${s[i]}`);
        }
    }
    geprueft += s.length;
};

for (const fall of F.faelle.flappy_linear) {
    const aus = new Float64Array(fall.w.length * 3);
    fall.w.forEach((w, i) => V.flappyLinear(w, fall.tempo, aus, i));
    vergleichen('flappyLinear', aus, fall.ergebnis);
}
for (const fall of F.faelle.squashy_linear) {
    const p = flach(fall.punkte);
    const aus = new Float64Array(p.length);
    for (let i = 0; i < fall.punkte.length; i++) {
        V.squashyLinear(fall.w_squashy, fall.tempo, p, fall.mitte, aus, i);
    }
    vergleichen('squashyLinear', aus, fall.ergebnis);
}
for (const fall of F.faelle.flappy_rotation) {
    const p = flach(fall.punkte);
    const aus = new Float64Array(p.length);
    for (let i = 0; i < fall.punkte.length; i++) {
        if (fall.punkttempo[i] * fall.w[i] > F.hoechstwinkel) deckel += 1;
        V.flappyRotation(fall.w[i], p, fall.gelenk, fall.achse,
                         fall.punkttempo[i], aus, i);
    }
    vergleichen('flappyRotation', aus, fall.ergebnis);
}
for (const fall of F.faelle.squashy_rotation) {
    const p = flach(fall.punkte);
    const aus = new Float64Array(p.length);
    for (let i = 0; i < fall.punkte.length; i++) {
        V.squashyRotation(fall.w_squashy, p, fall.gelenk, fall.medial,
                          fall.achse, fall.punkttempo[i], aus, i);
    }
    vergleichen('squashyRotation', aus, fall.ergebnis);
}
for (const fall of F.faelle.drehung) {
    vergleichen('drehung', V.drehung(fall.achse, fall.winkel), fall.ergebnis);
}
if (deckel === 0) throw new Error('Kein Fall traf den Hoechstwinkel');
console.log(JSON.stringify({ ok: true, geprueft, deckel }));
"""


class VelocityskinningJsTest(SimpleTestCase):

    databases = []

    def test_fixture_liegt_vor(self):
        self.assertTrue(
            os.path.isfile(FIXTURE),
            u'Fixture fehlt: %s — erzeugen mit '
            u'`python14 VelocitySkinning_Python/fixture.py`' % FIXTURE)

    def test_js_rechnet_wie_python(self):
        with open(FIXTURE, encoding='utf-8') as datei:
            fixture = json.load(datei)
        skript = SKRIPT.replace('FIXTURE;', json.dumps(fixture) + ';', 1)
        ausgabe = MODUL.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        # Mindestens die Zufallsfaelle: 6 je Formel mit 2 bis 5 Punkten.
        self.assertGreater(ausgabe['geprueft'], 200, ausgabe)
        self.assertGreater(ausgabe['deckel'], 0, ausgabe)

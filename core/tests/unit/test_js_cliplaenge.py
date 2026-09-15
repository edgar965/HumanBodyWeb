# -*- coding: utf-8 -*-
u"""`Cliplaenge`: die Länge eines Clips in Sekunden oder Prozent setzen.

Edgar (13.09.2026, BVH Studio): „keine Längenvorgaben! mach kontextmenüs wo
man die Länge der Clips setzen kann (in s oder in %)". Und am selben Tag:
„Länge einstellen soll auch beim Modell-Eintrag als Kontextmenü kommen" —
ein Modellclip hat keine Quelle, Sekunden setzen `totalFrames` (auch länger
als vorher), Prozent beziehen sich auf die Projektdauer (`bezug`).

1. Bewegungsclip 1004 Bilder bei 60 fps: 5 s → 300 Bilder (trimOut 704);
   50 % → 502; 100 % → trimOut 0. Der Anfang (`trimIn`) bleibt: mit
   trimIn 100 sind 100 % = 904 Bilder.
2. Grenzen: mehr als die Quelle → alles; weniger als ein Bild → ein Bild.
3. `speed` 2: fünf Sekunden Zeitleiste sind 600 Quellbilder.
4. Tonclip (30 s ganz): 12 s → 12; 50 % → 15; 99 s → 30 (gedeckelt);
   `stand` kennt Sekunden und Prozent.
5. `zahl`: „12,5 s" → 12,5; leer, Text, negativ, null → null.

Sabotage-Gegenprobe: `hoechstens - gesetzt` → `gesetzt` in `bilder` → Fall 1 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('bvh_studio', 'cliplaenge.js')

SKRIPT = """
const { Cliplaenge } = await import(MODUL);
const fehler = [];
const fehl = (t) => fehler.push(t);
const nah = (a, b, t) => { if (Math.abs(a - b) > 0.01) fehl(t + ': ' + a + ' statt ' + b); };
const bvh = () => ({ type: 'bvh', name: 'tanz', totalFrames: 1004, fps: 60, speed: 1, trimIn: 0, trimOut: 0 });

// --- 1. Sekunden und Prozent am Bewegungsclip -------------------------------
let c = bvh();
let s = Cliplaenge.sekunden(c, 5);
if (c.trimOut !== 704 || s.bilder !== 300) fehl('5 s: trimOut ' + c.trimOut + ', bilder ' + s.bilder);
nah(s.sekunden, 5, '5 s Stand'); nah(s.prozent, 100 * 300 / 1004, '5 s Prozent');
s = Cliplaenge.prozent(c, 50);
if (c.trimOut !== 502 || s.bilder !== 502) fehl('50 %: trimOut ' + c.trimOut);
s = Cliplaenge.prozent(c, 100);
if (c.trimOut !== 0) fehl('100 %: trimOut ' + c.trimOut);
nah(s.ganz, 1004 / 60, 'ganz');
c = bvh(); c.trimIn = 100;
s = Cliplaenge.prozent(c, 100);
if (c.trimOut !== 0 || s.bilder !== 904 || c.trimIn !== 100) fehl('trimIn bleibt: ' + JSON.stringify(c));
Cliplaenge.sekunden(c, 1);
if (c.trimOut !== 844 || c.trimIn !== 100) fehl('1 s mit trimIn: ' + JSON.stringify(c));

// --- 2. Grenzen ------------------------------------------------------------
c = bvh();
Cliplaenge.sekunden(c, 999);
if (c.trimOut !== 0) fehl('mehr als die Quelle: trimOut ' + c.trimOut);
s = Cliplaenge.sekunden(c, 0.001);
if (s.bilder !== 1 || c.trimOut !== 1003) fehl('unter einem Bild: ' + s.bilder);

// --- 3. speed -------------------------------------------------------------
c = bvh(); c.speed = 2;
s = Cliplaenge.sekunden(c, 5);
if (s.bilder !== 600) fehl('speed 2: ' + s.bilder + ' Bilder');
nah(s.sekunden, 5, 'speed 2 Sekunden');

// --- 4. Ton ----------------------------------------------------------------
const ton = { type: 'audio', name: 'lied', speed: 1, data: { audioDuration: 30, audioVoll: 30 } };
s = Cliplaenge.sekunden(ton, 12);
nah(ton.data.audioDuration, 12, 'Ton 12 s'); nah(s.prozent, 40, 'Ton 12 s Prozent');
s = Cliplaenge.prozent(ton, 50);
nah(ton.data.audioDuration, 15, 'Ton 50 %'); nah(s.sekunden, 15, 'Ton Stand');
Cliplaenge.sekunden(ton, 99);
nah(ton.data.audioDuration, 30, 'Ton gedeckelt');
const tonPuffer = { type: 'audio', speed: 1, data: { audioDuration: 20, audioBuffer: { duration: 40 } } };
Cliplaenge.prozent(tonPuffer, 100);
nah(tonPuffer.data.audioDuration, 40, 'Ton ganz aus dem Puffer');

// --- 5. Modellclip: keine Quelle, Sekunden auch laenger, Prozent auf die Projektdauer
const modell = () => ({ type: 'model', name: 'Female1', totalFrames: 300, fps: 30, speed: 1, trimIn: 0, trimOut: 0 });
let m = modell();
s = Cliplaenge.sekunden(m, 20, 900);          // Projekt 30 s = 900 Bilder
if (m.totalFrames !== 600 || m.trimOut !== 0) fehl('Modell 20 s: ' + JSON.stringify(m));
nah(s.sekunden, 20, 'Modell 20 s Stand'); nah(s.prozent, 100 * 600 / 900, 'Modell Prozent der Projektdauer');
nah(s.ganz, 30, 'Modell ganz = Projektdauer');
s = Cliplaenge.prozent(m, 50, 900);
if (m.totalFrames !== 450) fehl('Modell 50 %: ' + m.totalFrames);
s = Cliplaenge.prozent(m, 100, 900);
if (m.totalFrames !== 900) fehl('Modell 100 %: ' + m.totalFrames);
s = Cliplaenge.sekunden(m, 0.001, 900);
if (m.totalFrames !== 1 || s.bilder !== 1) fehl('Modell unter einem Bild: ' + m.totalFrames);
m = modell(); m.trimIn = 10;
Cliplaenge.sekunden(m, 5, 900);
if (m.totalFrames !== 160 || m.trimIn !== 10) fehl('Modell mit trimIn: ' + JSON.stringify(m));
s = Cliplaenge.stand(modell());
nah(s.prozent, 100, 'Modell ohne Bezug: 100 %');

// --- 6. zahl ---------------------------------------------------------------
if (Cliplaenge.zahl('12,5 s') !== 12.5) fehl('zahl 12,5 s: ' + Cliplaenge.zahl('12,5 s'));
if (Cliplaenge.zahl('75 %') !== 75) fehl('zahl 75 %');
for (const e of ['', 'abc', '-3', null, undefined, '0']) if (Cliplaenge.zahl(e) !== null) fehl('zahl(' + e + ') nicht null');

console.log(JSON.stringify({ ok: fehler.length === 0, fehler }));
"""


class CliplaengeTest(SimpleTestCase):

    databases = set()

    def test_laenge_in_sekunden_und_prozent(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

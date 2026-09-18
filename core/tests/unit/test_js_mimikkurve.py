# -*- coding: utf-8 -*-
"""`Mimikkurve`: Gewichte zwischen den Schlüsselbildern der Mimikspur.

WARUM (Edgar, 13.09.2026: „setze ich eine Pose zu einem Zeitpunkt, eine
andere für einen anderen, und die interpolierst zwischen den 2 Posen? … die
letzte Mimik bleibt am Modell"):

1. Vor dem ersten Schlüsselbild neutral, nach dem letzten bleibt die letzte
   Pose (mit ihrer Stärke).
2. Zwischen zweien: Haltezeit hält die erste, dann Übergang — weich
   (Smoothstep: Mitte 0,5, Viertel 0,156) oder linear (Viertel 0,25); die
   Art steht am Ziel.
3. Mischen über alle Einheiten: Einheiten, die nur eine Pose hat, laufen
   von/nach 0; die Reihenfolge der Schlüsselbilder ist egal.

Sabotage-Gegenprobe: in `gewichte` `if (i + 1 >= reihe.length) return a;`
→ `return {}` → Fall 1 rot („die letzte bleibt").
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul("bvh_studio", "mimikkurve.js")

SKRIPT = """
const { Mimikkurve: K } = await import(MODUL);
const nah = (was, a, b) => { if (Math.abs(a - b) > 1e-6) throw new Error(was + ': ' + a + ' statt ' + b);
};
const A = { frame: 30, gewichte: { mouthSmile: 1, eyeSquintL: 0.4 }, staerke: 0.5 };
const B = { frame: 90, gewichte: { browsMidVert: 0.8 }, uebergang: 'weich' };
const fps = 30;
// 1. davor neutral, danach die letzte
if (Object.keys(K.gewichte([B, A], 10, fps)).length) throw new Error('vor dem ersten nicht neutral');
nah('am ersten', K.gewichte([B, A], 30, fps).mouthSmile, 0.5);
nah('nach dem letzten bleibt', K.gewichte([B, A], 500, fps).browsMidVert, 0.8);
if ('mouthSmile' in K.gewichte([B, A], 500, fps)) throw new Error('erste Pose nach dem Ende noch da');
// 2. Uebergang weich / linear / halten
const mitte = K.gewichte([A, B], 60, fps);
nah('weich Mitte smile', mitte.mouthSmile, 0.25);
nah('weich Mitte brauen', mitte.browsMidVert, 0.4);
nah('weich Viertel', K.gewichte([A, B], 45, fps).browsMidVert, 0.8 * 0.15625);
const Bl = { ...B, uebergang: 'linear' };
nah('linear Viertel', K.gewichte([A, Bl], 45, fps).browsMidVert, 0.2);
const Ah = { ...A, halten: 1 };
nah('haelt 1 s', K.gewichte([Ah, B], 55, fps).mouthSmile, 0.5);
if ('browsMidVert' in K.gewichte([Ah, B], 55, fps)) throw new Error('waehrend des Haltens schon Ziel');
nah('nach dem Halten Mitte', K.gewichte([Ah, B], 75, fps).mouthSmile, 0.25);
// 3. Einheiten nur einer Seite
const nurA = K.gewichte([A, B], 45, fps);
nah('eyeSquintL laeuft gegen 0', nurA.eyeSquintL, 0.2 * (1 - 0.15625));
console.log(JSON.stringify({ ok: true }));
"""


class MimikkurveTest(SimpleTestCase):
    def test_interpolation_und_die_letzte_bleibt(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get("ok"))

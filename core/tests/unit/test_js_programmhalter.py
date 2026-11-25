# -*- coding: utf-8 -*-
u"""`Programmhalter` — ein nicht fertiges Shader-Programm lässt das alte weiterzeichnen (25.11.2026, Edgar: „stand die Seite … 6,4 und 5,1 s“), geprüft in Node.

1. `zurueckhalten`: nur, wenn es ein altes Programm gibt, das neue ein anderes und noch nicht fertig ist — dann zeichnet das alte, die Fassung gilt als gesehen, die Uniforms bleiben die neuen.
2. `einsetzen`: erst das fertige Programm kommt zurück (und wird gemeldet); ein inzwischen wieder geändertes Material fällt heraus.
3. `behalten`: jedes Programm zählt einmal mehr; über `HOECHSTENS` gehen die unbenutzten zuerst, benutzte nie.

Sabotage-Gegenprobe (nicht gefahren): in `zurueckhalten` `e.uniforms` mit zurücksetzen → Fall 1 rot (so stand die Haut nach zwei Änderungen ohne ihre neuen Werte); in `einsetzen` `isReady`
nicht fragen → Fall 2 rot; in `behalten` `usedTimes === 1` streichen → Fall 3 rot. Geschrieben, nicht gelaufen (nur auf Ansage).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'programmhalter.js')

SKRIPT = """
const { Programmhalter: P } = await import(MODUL);
const programm = (fertig) => ({ fertig, program: {}, usedTimes: 1, weg: false, isReady() { return this.fertig; }, destroy() { this.weg = true; this.program = undefined; } });
const eigenschaften = new Map();
const renderer = { properties: { get: m => eigenschaften.get(m) }, info: { programs: [] } };
const alt = programm(true), neu = programm(false), haut = { version: 4 };
eigenschaften.set(haut, { currentProgram: alt, __version: 3, uniforms: 'alt' });

// 1. zurückhalten
const stand = P.stand(renderer, haut);
pruefe('Stand', stand === alt, true);
Object.assign(eigenschaften.get(haut), { currentProgram: neu, uniforms: 'neu', uniformsList: 'alt' });      // das tat `renderer.compile`
pruefe('zurückgehalten', P.zurueckhalten(renderer, haut, stand), true);
const e = eigenschaften.get(haut);
pruefe('das alte zeichnet, mit den neuen Uniforms', [e.currentProgram === alt, e.uniforms, e.uniformsList, e.__version, P.wartend()], [true, 'neu', null, 4, 1]);
const fertig = { version: 1 };
eigenschaften.set(fertig, { currentProgram: programm(true), __version: 0 });
pruefe('ein fertiges wird nicht zurückgehalten', P.zurueckhalten(renderer, fertig, alt), false);
eigenschaften.set('nie', { });
pruefe('nie gezeichnet: kein Stand', P.stand(renderer, 'nie'), null);

// 2. einsetzen
const gemeldet = [];
P.einsetzen(p => gemeldet.push(p));
pruefe('noch nicht fertig', [e.currentProgram === alt, gemeldet.length], [true, 0]);
neu.fertig = true;
P.einsetzen(p => gemeldet.push(p));
pruefe('eingesetzt', [e.currentProgram === neu, gemeldet[0] === neu, P.wartend()], [true, true, 0]);
const neu2 = programm(false);
Object.assign(e, { currentProgram: neu2 });
P.zurueckhalten(renderer, haut, neu);
haut.version += 1;
neu2.fertig = true;
P.einsetzen(() => gemeldet.push('falsch'));
pruefe('inzwischen geändert: fällt heraus', [P.wartend(), gemeldet.length], [0, 1]);

// 3. behalten
P.HOECHSTENS = 2;
const a = programm(true), b = programm(true), c = programm(true);
renderer.info.programs.push(a, b, c);
P.behalten(renderer);
pruefe('zählt einmal mehr', [a.usedTimes, b.usedTimes, c.usedTimes], [2, 2, 2]);
P.behalten(renderer);
pruefe('nur einmal, und benutzte bleiben', [a.usedTimes, renderer.info.programs.length], [2, 3]);
a.usedTimes = 1;                                   // three hat seine Verweise abgegeben
P.behalten(renderer);
pruefe('das unbenutzte geht', [a.weg, b.weg, renderer.info.programs.includes(a), renderer.info.programs.length], [true, false, false, 2]);
console.log(JSON.stringify({ ok: true }));
"""


class ProgrammhalterTest(SimpleTestCase):
    databases = set()

    def test_programmhalter(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

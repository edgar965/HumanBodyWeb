# -*- coding: utf-8 -*-
"""`Genesis9hautebenenwerte`, zweite Reglerwelle (18.10.2026): Farbton … Aknenarben, geprüft in Node. Geschrieben, nicht gelaufen.

Edgar, 18.10.2026: „neue Regler, damit ich sowas wie Sommersprossen, Falten, Farbfehler, Farbton usw. erstellen kann? Möglichst viele Regler".

1. Ohne gestellten Wert: alle neuen Anteile 0, die Größen 1, die Dichte der Sommersprossen 0,8 (wie vorher fest im Shader) — und weder Farbe, Beulen noch Gebietskarte
   nötig; sonst bekäme jede Figur einen Shaderzusatz.
2. Prozent werden Anteile: Farbton −50 → −0,5, Cellulite 100 → 1; Größen nie unter 0,25; Dichte zwischen 0,1 und 1.
3. Jeder neue Farbwert schaltet `mitFarbe` (auch negativ); Cellulite, Aknenarben, Pickel schalten `mitBeulen`; Wangen, Augenringe, Aknenarben brauchen die Gebietskarte
   (`mitGebiet`). Altersfalten allein färben nicht (sie liegen in der Faltenschicht).
4. `hautfelder` enthält jeden Regler außer den grauen Haaren — genau die Felder, die eine gespeicherte Haut trägt (`Genesis9eigenehaut`).
5. Jedes Feld hat Name, Titel, Bereich, eine Gruppe aus `GRUPPEN` und eine Hilfe; die Namen sind eindeutig; ein Standard liegt im Bereich.

Sabotage-Gegenprobe (nicht gefahren): in `mitFarbe` 'teint' streichen → Fall 3 rot; in `hautfelder` die Gruppe 'Haar' zulassen → Fall 4 rot; einem Feld die Gruppe
'Haut' (alter Name) geben → Fall 5 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

WERTE = Jsmodul('gemeinsam', 'genesis9hautebenenwerte.js')

SKRIPT = """
const { Genesis9hautebenenwerte: W } = await import(MODUL);
const nah = (was, ist, soll) => { if (Math.abs(ist - soll) > 1e-9) throw new Error(was + ': ' + ist + ' statt ' + soll); };

// 1. nichts gestellt
let w = W.wirksam({}, 0);
pruefe('neue Anteile null', [w.farbton, w.oliv, w.saettigung, w.helligkeit, w.struktur, w.teint, w.wangen, w.augenringe, w.adern, w.weite,
                             w.pigment, w.vitiligo, w.muttermale, w.pickel, w.falten, w.cellulite, w.narben], new Array(17).fill(0));
pruefe('Größen 1', [w.flecken, w.muttermaleGroesse], [1, 1]);
nah('Dichte Standard', w.dichte, 0.8);
pruefe('ohne Wert kein Zusatz', [W.mitFarbe(w), W.mitBeulen(w), W.mitGebiet(w)], [false, false, false]);

// 2. Prozent -> Anteile, Grenzen
w = W.wirksam({ hautebenen: { farbton: -50, cellulite: 100, flecken_groesse: 5, muttermale_groesse: 300, sommer_dichte: 5 } }, 0);
nah('Farbton', w.farbton, -0.5); nah('Cellulite', w.cellulite, 1); nah('Fleckengröße nie unter 0,25', w.flecken, 0.25);
nah('Male-Größe', w.muttermaleGroesse, 3); nah('Dichte nie unter 0,1', w.dichte, 0.1);

// 3. Schalter
for (const n of ['farbton', 'oliv', 'saettigung', 'helligkeit', 'struktur', 'teint', 'wangen', 'augenringe', 'adern', 'pigment', 'vitiligo', 'muttermale', 'pickel']) {
    pruefe('mitFarbe ' + n, W.mitFarbe(W.wirksam({ hautebenen: { [n]: 40 } }, 0)), true);
}
pruefe('negativ zählt', W.mitFarbe(W.wirksam({ hautebenen: { helligkeit: -30 } }, 0)), true);
for (const n of ['cellulite', 'narben', 'pickel']) pruefe('mitBeulen ' + n, W.mitBeulen(W.wirksam({ hautebenen: { [n]: 40 } }, 0)), true);
for (const n of ['wangen', 'augenringe', 'narben', 'sommer']) pruefe('mitGebiet ' + n, W.mitGebiet(W.wirksam({ hautebenen: { [n]: 40 } }, 0)), true);
pruefe('Altersfalten allein färben nicht', W.mitFarbe(W.wirksam({ hautebenen: { falten: 80 } }, 0)), false);

// 4. Felder der Haut
const haut = W.hautfelder().map(f => f.name);
pruefe('ohne graue Haare', haut.includes('ergrauen'), false);
pruefe('alle anderen', haut.length, W.FELDER.length - 1);

// 5. Vollständigkeit
const gruppen = new Set(W.GRUPPEN.map(g => g.name));
const namen = new Set();
for (const f of W.FELDER) {
    if (!f.name || !f.titel || !f.hilfe || !(f.min < f.max) || !gruppen.has(f.gruppe)) throw new Error('Feld unvollständig: ' + JSON.stringify(f));
    if (namen.has(f.name)) throw new Error('doppelt: ' + f.name);
    namen.add(f.name);
    const s = W.standard(f.name);
    if (s < f.min || s > f.max) throw new Error('Standard außerhalb des Bereichs: ' + f.name);
}
console.log(JSON.stringify({ ok: true }));
"""


class Hautregler(SimpleTestCase):
    databases = set()

    def test_zweite_welle(self):
        WERTE.laufen(SKRIPT)

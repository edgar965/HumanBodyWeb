# -*- coding: utf-8 -*-
"""`Genesis9hautebenenwerte` und `Genesis9ergrauen`: Hautebenen-Rechnung und graue Strähnen (17.10.2026), geprüft in Node. Geschrieben, nicht gelaufen.

Edgar, 17.10.2026: „Hautebenen: Hautton, Sommersprossen, Altersflecken, graue Haare, Muskel- und Fettzeichnung."

1. Ohne gestellten Wert und ohne Alter ist alles null (Sommersprossen-Größe 1): eine Figur ohne Hautebenen bekommt nie einen Shaderzusatz (`wirksam`).
2. Prozent werden Anteile (60 % Hautton → 0,6, −40 % Rötung → −0,4); die Größe hat den Standard 100 % und nie unter 0,25.
3. Altersflecken und graue Haare folgen dem Alter, der Regler hebt nur an: bei Alter 0,5 stehen sie über null, bei Regler 100 % und Alter 0 bei 1; ein kleiner Regler wird vom Alter überholt.
4. Unter Alterswert 0,2 gibt es keine Altersflecken, unter 0,23 keine grauen Haare.
5. Die Strähnen sind die Zusammenhangskomponenten der Segmente `[a, b, b]`: zwei Strähnen aus je drei Punkten ergeben zwei Nummern; der Rang läuft 0 → 1 in Punktreihenfolge.
6. `zufall` ist fest (derselbe Wert zum selben Index) und liegt in [0, 1).
7. Graue Strähnen: bei Anteil 1 sind ALLE Punkte grau (Farbe über dem Original für dunkles Haar), bei Anteil 0 stehen die Originalfarben wieder; der Wert wird gemerkt, ein zweiter Aufruf mit demselben Anteil rechnet nichts neu.

Sabotage-Gegenprobe (nicht gefahren): in `wirksam` das Maximum durch eine Summe ersetzen → Fall 3 rot; in `strangnummern` die Vereinigung weglassen → Fall 5 rot; `daten.ergrauenAnteil` nicht merken → Fall 7 rot.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

WERTE = Jsmodul('gemeinsam', 'genesis9hautebenenwerte.js')
ERGRAUEN = Jsmodul('gemeinsam', 'genesis9ergrauen.js')

SKRIPT_WERTE = """
const { Genesis9hautebenenwerte: W } = await import(MODUL);
const nah = (was, ist, soll) => { if (Math.abs(ist - soll) > 1e-6) throw new Error(was + ': ' + ist + ' statt ' + soll); };      // 1e-6: die Zellgewichte sind Float32 (0,8 → 0,80000001)

// 1. nichts gestellt, kein Alter
let w = W.wirksam({}, 0);
pruefe('alles null', [w.ton, w.roetung, w.sommer, w.altersflecken, w.muskel, w.fett, w.ergrauen], [0, 0, 0, 0, 0, 0, 0]);
pruefe('Größe Standard', w.groesse, 1);

// 2. Prozent -> Anteile
w = W.wirksam({ hautebenen: { ton: 60, roetung: -40, sommer: 50, sommer_groesse: 10, muskel: 100 } }, 0);
nah('Hautton', w.ton, 0.6); nah('Rötung', w.roetung, -0.4); nah('Sommer', w.sommer, 0.5); nah('Muskel', w.muskel, 1);
nah('Größe nie unter 0,25', w.groesse, 0.25);

// 3. Alter überholt einen kleinen Regler, der Regler hebt an
w = W.wirksam({ hautebenen: { altersflecken: 10, ergrauen: 10 } }, 0.5);
if (!(w.altersflecken > 0.1 && w.ergrauen > 0.1)) throw new Error('Alter 0,5 hebt an: ' + JSON.stringify(w));
w = W.wirksam({ hautebenen: { altersflecken: 100, ergrauen: 100 } }, 0);
pruefe('Regler 100 % ohne Alter', [w.altersflecken, w.ergrauen], [1, 1]);

// 8. Mimikfalten: Standard 100 % = 1; ohne FACS-Detail mit Wert nie aktiv, mit Regler 0 nie aktiv; die Gewichte stehen in der Reihenfolge der Atlaszellen
pruefe('Mimik Standard', W.wirksam({}, 0).mimik, 1);
const stellung = { hdwerte: { 'FACSDetails_facs_bs_BrowDownLeft_HD2': 0.8, 'body_bs_Navel_HD3': 1, 'FACSDetails_facs_bs_NoseSneerLeft_HD2': 0 } };
pruefe('aktiv mit Detail', W.mimikAktiv(stellung, 1), true);
pruefe('Regler 0', W.mimikAktiv(stellung, 0), false);
pruefe('nur ein Nabel-HD, kein FACS', W.mimikAktiv({ hdwerte: { body_bs_Navel_HD3: 1 } }, 1), false);
pruefe('ohne hdwerte', W.mimikAktiv({}, 1), false);
const ziel = new Float32Array(3);
W.mimikGewichte(stellung, ['FACSDetails_facs_bs_NoseSneerLeft_HD2', 'FACSDetails_facs_bs_BrowDownLeft_HD2', 'fehlt'], ziel);
nah('Zelle 0 (Wert 0)', ziel[0], 0); nah('Zelle 1 (BrowDownLeft)', ziel[1], 0.8); nah('Zelle 2 (nicht gestellt)', ziel[2], 0);
W.mimikGewichte({ hdwerte: { a: 9 } }, ['a'], ziel);
nah('höchstens 1,5', ziel[0], 1.5);
pruefe('mehr Kanäle als Zellen werden abgeschnitten', Array.from(W.mimikGewichte({ hdwerte: { a: 1, b: 1, c: 1, d: 1 } }, ['a', 'b', 'c', 'd'], new Float32Array(2))), [1, 1]);

// 4. Schwellen
w = W.wirksam({}, 0.2); nah('Altersflecken ab 0,2', w.altersflecken, 0);
w = W.wirksam({}, 0.23); nah('Grau ab 0,23', w.ergrauen, 0);
w = W.wirksam({}, 1); pruefe('bei Alter 1 voll', [w.altersflecken, w.ergrauen], [1, 1]);
console.log(JSON.stringify({ ok: true }));
"""

SKRIPT_ERGRAUEN = """
const { Genesis9ergrauen: E } = await import(MODUL);

// 5. zwei Straehnen aus je drei Punkten: Segmente [a, b, b]
const geo = { attributes: { position: { count: 6 } }, index: { array: [0, 1, 1, 1, 2, 2, 3, 4, 4, 4, 5, 5] }, userData: {} };
const s = E.strangnummern(geo);
pruefe('zwei Nummern', new Set(Array.from(s.id)).size, 2);
pruefe('Nummern je Punkt', Array.from(s.id), [0, 0, 0, 3, 3, 3]);
pruefe('Rang', Array.from(s.rang), [0, 0.5, 1, 0, 0.5, 1]);

// 6. feste Zufallszahl
pruefe('fest', E.zufall(7), E.zufall(7));
for (let i = 0; i < 200; i++) { const z = E.zufall(i); if (!(z >= 0 && z < 1)) throw new Error('außerhalb: ' + z); }

// 7. graue Straehnen
const farben = { array: new Float32Array(18).fill(0.02), needsUpdate: false };
const g = { attributes: { position: { count: 6 }, color: farben }, index: { array: [0, 1, 1, 1, 2, 2, 3, 4, 4, 4, 5, 5] }, userData: {} };
const netz = { geometry: g, material: { vertexColors: true } };
E._netz(netz, 1);
for (let i = 0; i < 18; i++) if (!(farben.array[i] > 0.4)) throw new Error('Anteil 1: Punkt ' + i + ' ist nicht grau: ' + farben.array[i]);
farben.needsUpdate = false;
E._netz(netz, 1);
pruefe('gleicher Anteil rechnet nicht neu', farben.needsUpdate, false);
E._netz(netz, 0);
for (let i = 0; i < 18; i++) if (Math.abs(farben.array[i] - 0.02) > 1e-6) throw new Error('Anteil 0: Original zurück, Punkt ' + i + ': ' + farben.array[i]);
console.log(JSON.stringify({ ok: true }));
"""


class Hautebenenwerte(SimpleTestCase):
    databases = set()

    def test_werte_wirksam_und_alter(self):
        WERTE.laufen(SKRIPT_WERTE)

    def test_ergrauen_straehnen_und_grau(self):
        ERGRAUEN.laufen(SKRIPT_ERGRAUEN)

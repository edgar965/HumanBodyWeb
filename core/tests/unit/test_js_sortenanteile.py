# -*- coding: utf-8 -*-
"""`Sortenanteile`: die Aufteilung von „Haar – Generisch" nach einem Reglerzug.

Edgar, 30.09.2026: „wenn ich einen anteil eines neuen haares hinzumische, soll der
anteil der anderen proportional sinken, so dass die Summe aller Anteile immer 100% ist".

Geprueft wird die Rechnung ohne DOM — die Summe bleibt 1, das Verhaeltnis der anderen
bleibt erhalten (und kehrt zurueck, wenn die neue Sorte wieder auf 0 geht), die einzige
Sorte bleibt bei 100 %, und in die gespeicherten Werte kommt genau, was von der Vorgabe
abweicht — sonst naehme der Server fuer die Grundsorte wieder 1,0 an.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('charakter/genesis9', 'sortenanteile.js')

SKRIPT = """
const { Sortenanteile } = await import(MODUL);
const nah = (a, b) => Math.abs(a - b) < 1e-9;
const pruefe = (was, ok) => { if (!ok) throw new Error(was); };
const summe = (o) => Object.values(o).reduce((s, v) => s + v, 0);

// --- 1. Eine neue Sorte hinzumischen: die anderen sinken proportional -------
let a = Sortenanteile.ziehen({'sorte.kin': 1, 'sorte.toulouse': 0, 'sorte.pixie': 0},
                             'sorte.toulouse', 0.3);
pruefe('1 kin 70', nah(a['sorte.kin'], 0.7));
pruefe('1 toulouse 30', nah(a['sorte.toulouse'], 0.3));
pruefe('1 summe', nah(summe(a), 1));

// --- 2. Eine dritte dazu: das Verhaeltnis 70 : 30 bleibt ---------------------
a = Sortenanteile.ziehen(a, 'sorte.pixie', 0.2);
pruefe('2 kin 56', nah(a['sorte.kin'], 0.56));
pruefe('2 toulouse 24', nah(a['sorte.toulouse'], 0.24));
pruefe('2 summe', nah(summe(a), 1));

// --- 3. Die dritte wieder weg: das alte Verhaeltnis kehrt zurueck ------------
a = Sortenanteile.ziehen(a, 'sorte.pixie', 0);
pruefe('3 kin 70', nah(a['sorte.kin'], 0.7));
pruefe('3 toulouse 30', nah(a['sorte.toulouse'], 0.3));

// --- 4. Die einzige Sorte laesst sich nicht herunterziehen -------------------
// Niemand koennte den Rest aufnehmen; die Summe muss 100 % sein.
const allein = Sortenanteile.ziehen({'sorte.kin': 1, 'sorte.toulouse': 0},
                                    'sorte.kin', 0.4);
pruefe('4 kin bleibt 100', nah(allein['sorte.kin'], 1));
pruefe('4 toulouse bleibt 0', nah(allein['sorte.toulouse'], 0));

// --- 5. Ganz aufgedreht: die anderen gehen auf 0 ------------------------------
const ganz = Sortenanteile.ziehen({'sorte.kin': 0.7, 'sorte.toulouse': 0.3},
                                  'sorte.toulouse', 1);
pruefe('5 kin 0', nah(ganz['sorte.kin'], 0));
pruefe('5 toulouse 1', nah(ganz['sorte.toulouse'], 1));

// --- 6. Gespeichert wird, was von der Vorgabe abweicht ------------------------
// Die Grundsorte hat die Vorgabe 1,0: steht sie auf 0,7, MUSS der Wert mit.
const regler = {'Feathered': 0.5};
Sortenanteile.eintragen(regler, {'sorte.kin': 0.7, 'sorte.toulouse': 0.3, 'sorte.pixie': 0},
                        {'sorte.kin': 1, 'sorte.toulouse': 0, 'sorte.pixie': 0});
pruefe('6 kin gespeichert', nah(regler['sorte.kin'], 0.7));
pruefe('6 toulouse gespeichert', nah(regler['sorte.toulouse'], 0.3));
pruefe('6 pixie auf Vorgabe weg', !('sorte.pixie' in regler));
pruefe('6 Morph bleibt', regler['Feathered'] === 0.5);
// Zurueck auf die Vorgabe: der Eintrag verschwindet wieder.
Sortenanteile.eintragen(regler, {'sorte.kin': 1, 'sorte.toulouse': 0},
                        {'sorte.kin': 1, 'sorte.toulouse': 0});
pruefe('6 kin auf Vorgabe weg', !('sorte.kin' in regler));

// --- 7. Nur Sortenregler zaehlen ----------------------------------------------
pruefe('7 sorte', Sortenanteile.ist('sorte.kin_hair'));
pruefe('7 morph', !Sortenanteile.ist('kin_hair.Feathered'));
pruefe('7 zuletzt', !Sortenanteile.ist('sorte_zuletzt'));

console.log(JSON.stringify({ok: true}));
"""


class Aufteilung(SimpleTestCase):
    databases = set()

    def test_die_summe_bleibt_hundert_prozent(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'))

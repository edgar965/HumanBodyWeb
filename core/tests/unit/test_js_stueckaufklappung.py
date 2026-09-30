# -*- coding: utf-8 -*-
"""`Stueckaufklappung`: was fuer ein angeklicktes Stueck aufgeklappt wurde, wieder zuklappen.

Edgar, 30.09.2026: „Wenn man mal Schuhe ausgewählt hat, zeigt der Tab die ausgewählten
Schuhe links. Wenn man woanders klickt, bleibt der Tab ‚Schuhe‘ offen. der soll wieder zu
sein, wenn man was anderes klickt, sonst ist die Navigation unmöglich."

Geprueft mit Attrappen statt DOM (die Klasse fragt nur `contains`): Was WIR geoeffnet
haben, geht beim naechsten Klick zu; was der Nutzer selbst offen hatte, bleibt; und der
Kasten um das NEU gewaehlte Stueck bleibt offen, auch wenn wir ihn vorher geoeffnet hatten.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('charakter', 'stueckaufklappung.js')

SKRIPT = """
const { Stueckaufklappung } = await import(MODUL);
const pruefe = (was, ok) => { if (!ok) throw new Error(was); };

// Ein Kasten (`<details>`) mit Zeilen darin — nur `contains` wird gefragt.
const kasten = (name, zeilen = []) => ({
    name, open: false, zeilen,
    contains(x) { return x === this || this.zeilen.includes(x); },
});
const oeffnen = (k) => Stueckaufklappung.oeffnen(
    k, k.open, () => { k.open = true; }, () => { k.open = false; });

// --- 1. Was wir oeffnen, geht beim naechsten Klick wieder zu ------------------
const schuh = { zeile: 'sneaker' };
const schuhe = kasten('Schuhe', [schuh]);
oeffnen(schuhe);
pruefe('1 offen', schuhe.open === true);
Stueckaufklappung.zuklappen();
pruefe('1 wieder zu', schuhe.open === false);

// --- 2. Was der Nutzer offen hatte, bleibt offen -------------------------------
const hosen = kasten('Hosen');
hosen.open = true;               // selbst aufgeklappt
oeffnen(hosen);
Stueckaufklappung.zuklappen();
pruefe('2 bleibt offen', hosen.open === true);

// --- 3. Das neu gewaehlte Stueck behaelt seinen Kasten -------------------------
const jeans = { zeile: 'jeans' };
const hosen2 = kasten('Hosen2', [jeans]);
const schuhe2 = kasten('Schuhe2', [schuh]);
oeffnen(schuhe2);                // Schuh gewaehlt
oeffnen(hosen2);                 // dann die Jeans: ihr Kasten ist auf
Stueckaufklappung.zuklappen(jeans);
pruefe('3 Schuhe zu', schuhe2.open === false);
pruefe('3 Hosen bleiben', hosen2.open === true);
// Ein spaeterer Klick woanders nimmt auch ihn zurueck.
Stueckaufklappung.zuklappen();
pruefe('3 Hosen danach zu', hosen2.open === false);

// --- 4. Ein verschwundenes Element wirft nicht ---------------------------------
Stueckaufklappung.oeffnen({ contains: () => false }, false, () => {},
                          () => { throw new Error('weg'); });
Stueckaufklappung.zuklappen();
pruefe('4 leer danach', Stueckaufklappung._offen.length === 0);

// --- 5. Daz-Garderobe: genau die Kategorie des gewaehlten Stuecks offen --------
// Der Befund im Chrome: „Oberteile" hatte der BAU der Liste geoeffnet, nicht diese
// Klasse — nach dem Klick auf die Hose blieb sie offen. `nurDie` schliesst jede.
const shirt = { zeile: 'shirt' }, hose = { zeile: 'hose' };
const oberteile = kasten('Oberteile', [shirt]);
const hosenK = kasten('Hosen', [hose]);
const schuheK = kasten('Schuhe', []);
oberteile.open = true;                     // vom Bau geoeffnet (Shirt war gewaehlt)
const wurzel = { querySelectorAll: () => [oberteile, hosenK, schuheK] };
Stueckaufklappung.nurDie(hose, wurzel);
pruefe('5 Hosen offen', hosenK.open === true);
pruefe('5 Oberteile zu', oberteile.open === false);
pruefe('5 Schuhe zu', schuheK.open === false);
// Woanders geklickt (Haut, GarmentCode): alle zu.
Stueckaufklappung.nurDie(null, wurzel);
pruefe('5 alle zu', !oberteile.open && !hosenK.open && !schuheK.open);

console.log(JSON.stringify({ok: true}));
"""


class Zuklappen(SimpleTestCase):
    databases = set()

    def test_nur_was_wir_geoeffnet_haben_geht_zu(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'))

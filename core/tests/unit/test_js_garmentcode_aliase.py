# -*- coding: utf-8 -*-
"""`GarmentcodeAliase`: ein Stück unter altem Namen (`gc_t-shirt`) findet seine Vorlage im Reiter.

WARUM (Edgar, 05.10.2026: „ich klicke auf das Objekt T-Shirt GarmentCode. In der Leiste links wird das
aber nicht aktiv, es ist ‚Schuhe' aktiv.")
=====================================================================
Szenen von vor dem 11.09.2026 führen ihre Stücke unter den alten Namen (`t-shirt`, `pumps` …). Die
Auswahl `#gc-vorlage` kennt seitdem nur acht Katalogstücke; `vorlageZeigen('t-shirt')` fand keine Option
und kehrte stumm zurück. Die Tabelle kommt vom Server (`/api/garmentcode/zustand/` → `aliase`).
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('charakter', 'garmentcode_aliase.js')

SKRIPT = """
const { GarmentcodeAliase } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};
GarmentcodeAliase.setzen({'t-shirt': ['oberteil', 'form_t_shirt'], 'pumps': ['schuh', 'form_pumps']});

// --- 1. Ein alter Name löst auf das Katalogstück auf, alles andere bleibt ---
pruefe('t-shirt', GarmentcodeAliase.stueck('t-shirt'), 'oberteil');
pruefe('pumps', GarmentcodeAliase.stueck('pumps'), 'schuh');
pruefe('neuer Name', GarmentcodeAliase.stueck('oberteil'), 'oberteil');
pruefe('unbekannt', GarmentcodeAliase.stueck('gibtesnicht'), 'gibtesnicht');

// --- 2. Die Form hinter dem alten Namen, sonst nichts --------------------
pruefe('form t-shirt', GarmentcodeAliase.form('t-shirt'), {art: 'form', schluessel: 'form_t_shirt'});
pruefe('form neuer Name', GarmentcodeAliase.form('oberteil'), null);

// --- 3. Ohne Tabelle (Server nicht erreicht) verhält sich alles wie bisher -
GarmentcodeAliase.setzen(undefined);
pruefe('ohne Tabelle', GarmentcodeAliase.stueck('t-shirt'), 't-shirt');
GarmentcodeAliase.setzen('kaputt');
pruefe('Tabelle falsch', GarmentcodeAliase.form('t-shirt'), null);

console.log(JSON.stringify({ok: true}));
"""


class Aliase(SimpleTestCase):
    databases = set()

    def test_alte_stuecknamen_loesen_auf(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'))

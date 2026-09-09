# -*- coding: utf-8 -*-
u"""`Reiterzuordnung`: welcher Reiter zu einem angeklickten Stueck gehoert.

WARUM (Edgar, 09.09.2026: „Klick auf die Hose aendert den Tab zu
Eigenschaften des Modells. Es soll zu GarmenCode wechseln!")
=====================================================================
`_doSubMeshClick` rief seit jeher fest `switchTab('eigenschaften')`. Bei
einem GarmentCode-Stueck ist das die falsche Seite: Dort stehen die Regler
der Kleiderbibliothek, waehrend die 71 Regler DIESES Stuecks im
GarmentCode-Reiter liegen.

Die Zuordnung haengt am PRAEFIX des Schluessels, nicht am `type` — `type`
ist bei jedem Kleidungsstueck `cloth`, gleich woher es kommt. Genau das
haelt dieser Test fest.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'reiterzuordnung.js')

SKRIPT = """
const { Reiterzuordnung } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (ist !== soll) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt '
                        + JSON.stringify(soll));
    }
};

// --- 1. GarmentCode-Stuecke gehen in ihren eigenen Reiter -----------------
pruefe('gc_hose', Reiterzuordnung.fuer('gc_hose'), 'garmentcode');
pruefe('gc_t-shirt', Reiterzuordnung.fuer('gc_t-shirt'), 'garmentcode');

// --- 2. Alles andere bleibt, wo es war ------------------------------------
// `gar_` Bibliothek, `bld_`/`prim_`/`tpl_` Kleiderbauer, Haare.
for (const schluessel of ['gar_dress01', 'bld_TOP', 'prim_PRIM_SKIRT',
                          'tpl_TPL_TSHIRT', 'hair_ballerina']) {
    pruefe(schluessel, Reiterzuordnung.fuer(schluessel), 'eigenschaften');
}

// --- 3. Kein Schluessel: der Vorgabereiter, wie bisher --------------------
pruefe('null', Reiterzuordnung.fuer(null), 'eigenschaften');
pruefe('undefined', Reiterzuordnung.fuer(undefined), 'eigenschaften');

// --- 4. Die Vorlage hinter dem Schluessel ---------------------------------
// Sie ist der zweite Teil: Ein Reiter, der die Regler eines ANDEREN
// Stuecks zeigt, ist keine Hilfe.
pruefe('vorlage hose', Reiterzuordnung.vorlageVon('gc_hose'), 'hose');
pruefe('vorlage bindestrich',
       Reiterzuordnung.vorlageVon('gc_asymmetrischer-rock'),
       'asymmetrischer-rock');
pruefe('vorlage fremd', Reiterzuordnung.vorlageVon('gar_dress01'), null);
pruefe('vorlage leer', Reiterzuordnung.vorlageVon(null), null);

// --- 5. Der Praefix muss GENAU vorn stehen --------------------------------
// Sonst zoege ein Stueck namens „magc_..." mit.
pruefe('nicht vorn', Reiterzuordnung.fuer('magc_hose'), 'eigenschaften');

console.log(JSON.stringify({ok: true}));
"""


class Zuordnung(SimpleTestCase):

    databases = []

    def test_die_zuordnung_stimmt(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'))

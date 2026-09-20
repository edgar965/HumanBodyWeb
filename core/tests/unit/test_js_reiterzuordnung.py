# -*- coding: utf-8 -*-
"""`Reiterzuordnung`: welcher Reiter zu einem angeklickten Stueck gehoert — und
welche Zeile darin (`stueckVon`, 20.09.2026).

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
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt '
                        + JSON.stringify(soll));
    }
};

// --- 1. GarmentCode-Stuecke gehen in ihren eigenen Reiter -----------------
pruefe('gc_hose', Reiterzuordnung.fuer('gc_hose'), 'garmentcode');
pruefe('gc_t-shirt', Reiterzuordnung.fuer('gc_t-shirt'), 'garmentcode');

// --- 2. Jedes Stueck geht in den Reiter, der es fuehrt (20.09.2026) ------
// Edgar: „wenn ich auf ein Asset oder Garment Code oder was auch immer
// klicke, soll in der Toolbar genau das ausgewaehlt sein."
pruefe('kld_', Reiterzuordnung.fuer('kld_dress01'), 'kleider');
pruefe('gar_', Reiterzuordnung.fuer('gar_dress01'), 'assets');
pruefe('mhk_', Reiterzuordnung.fuer('mhk_female_casualsuit01'), 'assets');
pruefe('daz_ auf HumanBody', Reiterzuordnung.fuer('daz_angie_jeans/2'), 'assets');
pruefe('Daz auf Genesis 9', Reiterzuordnung.fuer('g9_base_shirt/0'), 'assets');
// Kleiderbauer und Haare haben keine Zeile in einem Reiter: Vorgabe.
for (const schluessel of ['bld_TOP', 'prim_PRIM_SKIRT', 'tpl_TPL_TSHIRT',
                          'hair_ballerina', 'humanbody_frisur/0']) {
    pruefe(schluessel, Reiterzuordnung.fuer(schluessel), 'eigenschaften');
}

// --- 2b. Liste und Kennung hinter dem Schluessel --------------------------
pruefe('stueck gc', Reiterzuordnung.stueckVon('gc_hose'),
       {reiter: 'garmentcode', liste: 'garmentcode', kennung: 'hose'});
pruefe('stueck kld', Reiterzuordnung.stueckVon('kld_dress01'),
       {reiter: 'kleider', liste: 'kleider', kennung: 'dress01'});
pruefe('stueck gar', Reiterzuordnung.stueckVon('gar_dress01'),
       {reiter: 'assets', liste: 'garment', kennung: 'dress01'});
pruefe('stueck mhk', Reiterzuordnung.stueckVon('mhk_shoes01'),
       {reiter: 'assets', liste: 'makehuman', kennung: 'shoes01'});
pruefe('stueck daz_', Reiterzuordnung.stueckVon('daz_angie_jeans/2'),
       {reiter: 'assets', liste: 'daz', kennung: 'angie_jeans'});
pruefe('stueck g9', Reiterzuordnung.stueckVon('toulouse_hair/1'),
       {reiter: 'assets', liste: 'daz', kennung: 'toulouse_hair'});
pruefe('stueck frisur', Reiterzuordnung.stueckVon('humanbody_frisur/0'), null);
pruefe('stueck haar', Reiterzuordnung.stueckVon('hair'), null);
pruefe('stueck daz_ ohne Teil', Reiterzuordnung.stueckVon('daz_'), null);

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
    databases = set()

    def test_die_zuordnung_stimmt(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'))

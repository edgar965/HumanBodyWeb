# -*- coding: utf-8 -*-
u"""Die Gewebe-Auswahl unter „Farbe / Material" (11.09.2026).

Edgar: „du hast ja jetzt auch die Textur eingebaut, kannst du
auswahlmoeglichkeiten fuer Textur bei dem Bereich Farbe/Material
hinzufuegen".

Geprueft wird in Node, was an den Kacheln still falsch sein kann:

1. **Jede Art kachelt.** Der Sprung ueber den Rand ist nicht groesser als
   der groesste Sprung im Inneren (dieselbe Probe wie `test_js_gewebe`).
2. **Die Arten sind verschieden.** Zwei Namen fuer dasselbe Feld waeren
   eine Auswahl, die nichts auswaehlt.
3. **Koeper hat die Diagonale.** Eine Verschiebung um (1, 1) Faeden aendert
   das Feld nicht — die Reihen sind je um einen Faden versetzt.
4. **Jersey hat Staebchen.** Verschiebung um einen Faden in x aendert
   nichts (jede Zelle ein V), Verschiebung um einen HALBEN Faden schon.
5. **Die Kachelgroesse folgt der Feinheit**: 4 Faeden je cm bei 8 je
   Kachel sind die 2 cm der Leinwand, 8 je cm die Haelfte.

Und in Python, was die Verdrahtung angeht: Die Auswahlliste der Vorlage
fuehrt genau die Arten des Moduls; das Material haengt die Auswahl ein;
das Gewebe geht mit `werte()` in die Szenendatei und mit `auflegen()`
zurueck.

Sabotage-Gegenprobe: `faedenJeKachel: 7` beim Koeper macht Probe 1 rot;
eine Option `<option value="leder">` in der Vorlage macht
`test_vorlage_und_modul_fuehren_dieselben_arten` rot.
"""
import io
import re

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'gewebearten.js')

SKRIPT = """
const { GEWEBEARTEN, gewebeart, GEWEBE_VORGABE } = await import(MODUL);
const { Gewebe } = await import(MODUL.replace('gewebearten.js', 'gewebe.js'));
const pruefe = (was, bedingung, zusatz) => {
    if (!bedingung) throw new Error(was + (zusatz === undefined ? '' : ': ' + zusatz));
};
const g = 96;
const felder = {};
for (const [name, art] of Object.entries(GEWEBEARTEN)) {
    if (!art.hoehe) { pruefe('glatt ist die einzige Art ohne Hoehe', name === 'glatt'); continue; }
    const h = Gewebe.hoehenfeld(g, art.faedenJeKachel, art.hoehe);
    felder[name] = h;
    let innen = 0, randX = 0, randY = 0, min = 1, max = 0;
    for (let y = 0; y < g; y++) {
        for (let x = 0; x < g; x++) {
            const v = h[y * g + x];
            min = Math.min(min, v); max = Math.max(max, v);
            if (x > 0) innen = Math.max(innen, Math.abs(v - h[y * g + x - 1]));
            if (y > 0) innen = Math.max(innen, Math.abs(v - h[(y - 1) * g + x]));
        }
        randX = Math.max(randX, Math.abs(h[y * g] - h[y * g + g - 1]));
    }
    for (let x = 0; x < g; x++) randY = Math.max(randY, Math.abs(h[x] - h[(g - 1) * g + x]));
    // --- 1. kachelt, in x und y
    pruefe(name + ': Randsprung in x', randX <= innen + 1e-9, randX.toFixed(3) + ' > ' + innen.toFixed(3));
    pruefe(name + ': Randsprung in y', randY <= innen + 1e-9, randY.toFixed(3) + ' > ' + innen.toFixed(3));
    pruefe(name + ': Werte ausserhalb 0..1', min >= -1e-9 && max <= 1 + 1e-9, min + '..' + max);
    pruefe(name + ': Feld ist flach', max - min > 0.5, max - min);
}
// --- 2. verschieden
const namen = Object.keys(felder);
for (let i = 0; i < namen.length; i++) for (let j = i + 1; j < namen.length; j++) {
    let diff = 0;
    for (let k = 0; k < g * g; k++) diff += Math.abs(felder[namen[i]][k] - felder[namen[j]][k]);
    pruefe(namen[i] + ' und ' + namen[j] + ' sind dasselbe Feld', diff / (g * g) > 0.02, diff / (g * g));
}
// --- 3. Koeper: (1, 1) Faeden verschoben = unveraendert
const versatz = (h, faeden, dx, dy) => {
    const b = g / faeden; let d = 0;
    for (let y = 0; y < g; y++) for (let x = 0; x < g; x++) {
        const xx = (x + Math.round(dx * b) + g) % g, yy = (y + Math.round(dy * b) + g) % g;
        d += Math.abs(h[y * g + x] - h[yy * g + xx]);
    }
    return d / (g * g);
};
pruefe('Koeper: Diagonale fehlt', versatz(felder.koeper, 6, 1, 1) < 1e-6, versatz(felder.koeper, 6, 1, 1));
pruefe('Koeper: Periode 3 fehlt', versatz(felder.koeper, 6, 1, 0) > 0.02, versatz(felder.koeper, 6, 1, 0));
// --- 4. Jersey: Staebchen
pruefe('Jersey: ein Faden in x muss gleich sein', versatz(felder.jersey, 8, 1, 0) < 1e-6);
pruefe('Jersey: ein halber Faden in x muss anders sein', versatz(felder.jersey, 8, 0.5, 0) > 0.02);
// --- 5. Kachelgroesse
pruefe('4 Faeden je cm = 2 cm', Math.abs(Gewebe.kachelmeter(4, 8) - 0.02) < 1e-12);
pruefe('8 Faeden je cm = 1 cm', Math.abs(Gewebe.kachelmeter(8, 8) - 0.01) < 1e-12);
pruefe('Unsinn faellt auf KACHEL_M', Gewebe.kachelmeter(0, 8) === Gewebe.KACHEL_M);
pruefe('Vorgabe ist eine Art', gewebeart(GEWEBE_VORGABE).hoehe !== undefined);
pruefe('Unbekannt faellt auf die Vorgabe', gewebeart('leder') === gewebeart(GEWEBE_VORGABE));
console.log(JSON.stringify({ok: true, arten: Object.keys(GEWEBEARTEN)}));
"""


class GewebeartenTest(SimpleTestCase):

    databases = set()

    def test_kacheln_und_muster(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)
        self.assertEqual(ausgabe['arten'],
                         ['leinwand', 'koeper', 'jersey', 'satin', 'glatt'])

    def test_vorlage_und_modul_fuehren_dieselben_arten(self):
        vorlage = GewebeartenTest._lies('templates', '_garmentcode_material.html')
        stelle = vorlage.index('id="gc-gewebe"')
        block = vorlage[stelle:vorlage.index('</select>', stelle)]
        optionen = re.findall(r'<option value="([a-z]+)"', block)
        modul = GewebeartenTest._lies('static', 'viewer', 'gemeinsam', 'gewebearten.js')
        arten = re.findall(r'^    ([a-z]+): \{$', modul, re.M)
        self.assertEqual(optionen, arten)
        self.assertIn('{% regler "gc-faeden"', vorlage)
        self.assertIn('{% regler "gc-struktur"', vorlage)
        # Die Auswahl steht VOR den Schiebern: Das Reitergedaechtnis stellt
        # in DOM-Reihenfolge her, und die Art setzt sonst die gemerkten
        # Feinwerte zurueck.
        self.assertLess(stelle, vorlage.index('"gc-faeden"'))

    def test_das_material_haengt_die_auswahl_ein(self):
        material = GewebeartenTest._lies('static', 'viewer', 'scene', 'garmentcode_material.js')
        self.assertIn('GarmentcodeGewebe.einhaengen(GarmentcodeMaterial)', material)
        self.assertIn('gewebe: { ...Garmentstoff.GEWEBE }', material)
        auswahl = GewebeartenTest._lies('static', 'viewer', 'scene', 'garmentcode_gewebe.js')
        # Beim Seitenstart (synthetisches `change`) keine Vorgaben setzen.
        self.assertIn('if (ereignis.isTrusted)', auswahl)

    def test_das_gewebe_geht_in_die_szenendatei_und_zurueck(self):
        stoff = GewebeartenTest._lies('static', 'viewer', 'scene', 'garmentcode_stoff.js')
        self.assertIn("gewebe: m.userData?.gewebe ? { ...m.userData.gewebe } : null", stoff)
        self.assertIn("if (werte.gewebe && typeof werte.gewebe === 'object')", stoff)
        # Ein Stueck ohne UV bekommt keine Karte, behaelt aber seine Angabe.
        self.assertIn('material.userData.gewebe = wahl', stoff)
        # Die Ablage schreibt `werte()` unveraendert — das Gewebe kommt mit.
        ablage = GewebeartenTest._lies('static', 'viewer', 'scene', 'garmentcode_ablage.js')
        self.assertIn('...werte,', ablage)

    @staticmethod
    def _lies(*teile):
        return io.open(settings.BASE_DIR.joinpath(*teile), encoding='utf-8').read()

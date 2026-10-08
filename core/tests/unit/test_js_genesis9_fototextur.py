# -*- coding: utf-8 -*-
"""`Genesis9fototextur.gruppen`: was der Nutzer im Genesis-Bedienfeld wählt, gilt vor der Fotokachel (08.10.2026).

Edgar: „Texturfehler … Nägel färben sich nicht, wenn ich die über Genesis setze, auch Skin nicht usw." Die Fotokacheln eines
Modells überschrieben bis dahin die Albedo ALLER Gruppen, auch wenn ein Hautpreset oder Nagellack gewählt war. Jetzt, geprüft in
Node ohne DOM:

1. Ohne Wahl gelten die Kacheln wie bisher (Albedo, Rauheit des Modells, Diffusfarbe weg); die Serverantwort bleibt unberührt.
2. Ein Hautpreset (`haut`) gibt Kopf, Rumpf, Beine und Arme (1001–1004) frei, die Nägel nicht.
3. Ein Kopf-Preset gibt nur 1001 frei, ein Nagellack-Preset nur 1005.
4. `hautton` behält die Diffusfarbe über der Kachel, `hautglanz` die Rauheit des Presets statt der des Modells.
5. `frei` nennt genau die Kacheln der gewählten Kategorien.

Sabotage-Gegenprobe: `frei.has(...)` in `gruppen` entfernen → Fall 2 und 3 rot; `delete bilder.farbe` bedingungslos → Fall 4 rot.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'genesis9fototextur.js')

SKRIPT = """
globalThis.document = { cookie: '' };                         // Netzstufe.gewaehlt liest den Keks
const { Genesis9fototextur: F } = await import(MODUL);
const server = () => [
    { name: 'Head', kachel: 1001, bilder: { albedo: 'preset_kopf', farbe: '#ff0000', rauheit: 'preset_rauh' } },
    { name: 'Body', kachel: 1002, bilder: { albedo: 'preset_rumpf', farbe: '#ff0000' } },
    { name: 'Fingernails', kachel: 1005, bilder: { albedo: 'preset_nagel' } },
];
const kacheln = { '1001': '/k/1001', '1001:rauheit': '/k/1001r', '1002': '/k/1002', '1005': '/k/1005' };
const albedos = erg => erg.map(g => g.bilder.albedo);

// 1. Ohne Wahl
const roh = server();
let e = F.gruppen(roh, kacheln);
pruefe('ohne Wahl', albedos(e), ['/k/1001', '/k/1002', '/k/1005']);
pruefe('Diffusfarbe fällt weg', e[0].bilder.farbe, undefined);
pruefe('Rauheit des Modells', e[0].bilder.rauheit, '/k/1001r');
pruefe('Serverantwort unberührt', albedos(roh), ['preset_kopf', 'preset_rumpf', 'preset_nagel']);
pruefe('ohne Kacheln dieselbe Liste', F.gruppen(roh, {}) === roh, true);

// 2. Hautpreset
e = F.gruppen(server(), kacheln, { haut: 'G9 Feminine Skin 02 MAT', praesets: {} });
pruefe('Hautpreset gibt die Haut frei', albedos(e), ['preset_kopf', 'preset_rumpf', '/k/1005']);

// 3. Kopf- und Nagellack-Preset
e = F.gruppen(server(), kacheln, { haut: '', praesets: { kopf: 'x' } });
pruefe('Kopf-Preset', albedos(e), ['preset_kopf', '/k/1002', '/k/1005']);
e = F.gruppen(server(), kacheln, { haut: '', praesets: { nagellack: 'rot' } });
pruefe('Nagellack-Preset', albedos(e), ['/k/1001', '/k/1002', 'preset_nagel']);

// 4. Hautton und Hautglanz
e = F.gruppen(server(), kacheln, { haut: '', praesets: { hautton: 'dunkel' } });
pruefe('Hautton: Albedo bleibt die Kachel', e[0].bilder.albedo, '/k/1001');
pruefe('Hautton behält die Diffusfarbe', e[0].bilder.farbe, '#ff0000');
e = F.gruppen(server(), kacheln, { haut: '', praesets: { hautglanz: 'nass' } });
pruefe('Hautglanz behält die Rauheit des Presets', e[0].bilder.rauheit, 'preset_rauh');

// 5. frei
pruefe('frei ohne Wahl', [...F.frei(null)], []);
pruefe('frei Haut', [...F.frei({ haut: 'x' })].sort(), [1001, 1002, 1003, 1004]);
pruefe('frei Nagellack und Kopf', [...F.frei({ praesets: { nagellack: 'a', kopf: 'b', schatten: 'c' } })].sort(), [1001, 1005]);
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9fototexturWahlTest(SimpleTestCase):
    databases = set()

    def test_die_wahl_im_bedienfeld_gilt_vor_der_fotokachel(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

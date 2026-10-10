# -*- coding: utf-8 -*-
"""`Figurwahlimporte`: abgebrochene Blender-Importe als Zeilen der Modell-Liste (10.10.2026).

Edgar: „ein abgebrochener Import soll bei der Modell-Liste (mit Fehlerzeichen) sichtbar sein, damit ich ihn löschen kann". Geprüft wird die Zeile,
die der Dialog daraus baut: Name der Figur + „(Import)", der Grund in der Unterzeile samt Datum und Größe, das Warnzeichen (`warnung`), der
Bereich „gespeichert", und dass die Kennung des Imports der Schlüssel ist (eindeutig, nicht der Name der Figur — zwei Läufe derselben Figur
stehen nebeneinander). Das Datum kommt aus der Kennung (`2026.10.09.23.08.44` → `09.10.2026 23:08`).

Sabotage-Gegenprobe: in `zeile` `warnung` streichen → Fall 1 rot; in `datum` Tag und Monat vertauschen → Fall 2 rot.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'figurwahlimporte.js')

SKRIPT = """
const { Figurwahlimporte } = await import(MODUL);
const pruefe = (was, ist) => { if (!ist) throw new Error(was); };

const plan = { kennung: '2026.10.09.23.08.44', name: 'Rosemary Winters', verwaist: 'Gescheitert: Boom', mb: 121.6 };
const z = Figurwahlimporte.zeile(plan);
pruefe('Schlüssel ist die Kennung', z.name === '2026.10.09.23.08.44' && z.importKennung === z.name);
pruefe('Anzeige mit (Import)', z.anzeige === 'Rosemary Winters (Import)');
pruefe('Warnung trägt den Grund', z.warnung.includes('Abgebrochener Import') && z.warnung.includes('Gescheitert: Boom'));
pruefe('verwaist und im Bereich gespeichert', z.verwaist === true && z.bereich === 'gespeichert');
pruefe('Unterzeile: Grund, Datum, Größe', z.unterzeile === 'Gescheitert: Boom · 09.10.2026 23:08 · 121.6 MB');

pruefe('Datum aus der Kennung', Figurwahlimporte.datum('2026.10.08.11.28.06') === '08.10.2026 11:28');
pruefe('fremde Kennung bleibt', Figurwahlimporte.datum('abc') === 'abc');
console.log(JSON.stringify({ok: true}));
"""


class FigurwahlimporteTest(SimpleTestCase):
    databases = set()

    def test_zeile_eines_verwaisten_imports(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

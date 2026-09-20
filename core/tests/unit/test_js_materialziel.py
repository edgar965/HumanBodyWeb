# -*- coding: utf-8 -*-
"""`Materialziel`: welche GarmentCode-Stücke bekommen den Reglerstand?

WARUM (12.09.2026, Edgar: „bei GarmentCode - bereich Farbe/Material -
ändere ich das Gewebe, oder andere Einstellungen, tut sich nichts"): Seit
dem 09.09. wirkten die Regler nur auf ein angeklicktes Stück; die
Überschrift versprach aber „ohne Auswahl für alle GarmentCode-Stücke
dieser Figur". Die Grenze liegt jetzt beim Urheber des Ereignisses:

1. Ein gewähltes Stück bekommt den Stand — immer, und nur es.
2. Ohne Auswahl bekommt ihn das Stück der GEWÄHLTEN VORLAGE (`aktuell`),
   wenn der Nutzer das Feld bedient hat (`isTrusted`) und es hängt —
   nicht mehr alle Stücke (20.09.2026, Edgar: „möchte ein T-Shirt
   erzeugen, sobald ich die Farbe eingeben will, wird die Farbe der
   Leggings geändert").
3. Ohne Auswahl bekommt ihn NIEMAND, wenn Code das Feld gesetzt hat
   (Reitergedächtnis beim Seitenstart, Vorbild aus dem Kleider-Reiter) —
   das war der Fehler vom 09.09., als eine gespeicherte Farbe beim Laden
   überschrieben wurde.
4. Andere Kleider (`gar_*`, Haare) und leere Einträge bleiben unberührt.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('scene', 'materialziel.js')

SKRIPT = """
const { Materialziel: M } = await import(MODUL);
const shirt = { n: 'shirt' }, hose = { n: 'hose' }, schuhe = { n: 'schuhe' };
const stuecke = { 'gc_t-shirt': shirt, gc_hose: hose, 'gar_shoes/x': schuhe, gc_leer: null };

// 1. gewaehlt: nur dieses, egal wer
pruefe('gewaehlt, Nutzer', M.netze({ gewaehlt: hose, stuecke, nutzer: true }), [hose]);
pruefe('gewaehlt, Code', M.netze({ gewaehlt: hose, stuecke, nutzer: false }), [hose]);
// 2. ohne Auswahl, Nutzer: das Stueck der gewaehlten Vorlage — nicht die anderen
pruefe('Nutzer, Vorlage haengt', M.netze({ gewaehlt: null, stuecke, nutzer: true, aktuell: 'gc_hose' }), [hose]);
pruefe('Nutzer, Vorlage haengt nicht', M.netze({ gewaehlt: null, stuecke, nutzer: true, aktuell: 'gc_rock' }), []);
pruefe('Nutzer, leerer Eintrag', M.netze({ stuecke, nutzer: true, aktuell: 'gc_leer' }), []);
pruefe('Nutzer, kein gc_', M.netze({ stuecke, nutzer: true, aktuell: 'gar_shoes/x' }), []);
pruefe('Nutzer ohne Vorlage', M.netze({ gewaehlt: null, stuecke, nutzer: true }), []);
// 3. ohne Auswahl, Code: niemand
pruefe('Code nichts', M.netze({ gewaehlt: null, stuecke, nutzer: false, aktuell: 'gc_hose' }), []);
pruefe('Code nichts, Vorgabe', M.netze({ stuecke }), []);
// 4. Raender
pruefe('keine Figur', M.netze({ nutzer: true, aktuell: 'gc_hose' }), []);
pruefe('keine Stuecke', M.netze({ stuecke: {}, nutzer: true, aktuell: 'gc_hose' }), []);
pruefe('leer', M.netze(), []);
console.log(JSON.stringify({ ok: true }));
"""


class MaterialzielTest(SimpleTestCase):
    def test_nutzer_wirkt_auf_die_vorlage_code_nur_auf_die_auswahl(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

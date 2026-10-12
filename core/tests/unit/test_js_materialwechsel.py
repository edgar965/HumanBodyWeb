# -*- coding: utf-8 -*-
"""`Materialwechsel`: der eine Weg für jede Auswahl, die nur das Material der Figur ändert (12.10.2026), geprüft in Node.

Edgar: „erzeuge eine generische Methode für alle Wechsel." Haut, Augen, Brauen, Brauenstil und Makeup gingen durch sechs Methoden mit derselben Zeile; jetzt durch
`Genesis9Modell.materialWechseln` → `Materialwechsel.ausfuehren`. Die Klasse ist ohne Three.js ladbar, `Genesis9Modell` selbst nicht (die Importkette zieht die Szene nach) —
deshalb prüft ein Fall die Verdrahtung am Quelltext.

1. `ausfuehren` ruft `aendern` VOR dem Bau, baut genau einmal ohne neues Skelett (`koerperAufbauen(null, false)`) und gibt das Ergebnis des Baus zurück. Dass der Bau das Netz nicht neu holt,
   sondern die gehaltene Antwort nimmt und nur die Materialien erfragt, steht in `test_js_genesis9materialabruf.py` (`Genesis9materialabruf`, `Genesis9antwortspeicher`, 12.10.2026).
2. Wirft `aendern`, wird nichts gebaut (ein halb gesetzter Wechsel holt keinen Körper) und der Fehler kommt beim Aufrufer an.
3. Scheitert der Bau, kommt der Fehler beim Aufrufer an (kein stilles Schlucken).
4. Verdrahtung: alle sechs Wechsel (`hautSetzen`, `augenSetzen`, `augenOriginalSetzen`, `brauenSetzen`, `brauenstilSetzen`, `praesetSetzen`) gehen durch `this.materialWechseln(`, und
   außerhalb von `materialWechseln`/`koerperAufbauen` baut keine Methode mehr mit `koerperAufbauen(null, false)` selbst; die Nacharbeit (Verdeckung planen, Anatomie-Stück folgen) steht in
   `Genesis9maske.nachMaterialwechsel`, und der Bau ruft sie bei jedem Wechsel ohne neues Skelett.

Sabotage-Gegenprobe: in `ausfuehren` die Zeile `aendern();` hinter den Bau stellen → Fall 1 rot; `koerperAufbauen(null, true)` → Fall 1 rot; `aendern()` in ein `try/catch` ohne `throw` → Fall 2 rot;
eine der sechs Methoden wieder mit `this.koerperAufbauen(null, false)` → Fall 4 rot; `Anatomiehaut.nachziehen(inst)` aus `nachMaterialwechsel` streichen → Fall 4 rot. Gelaufen 12.10.2026 (2 Tests, grün); die Sabotage-Gegenprobe ist nicht gefahren.
"""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'materialwechsel.js')
GEMEINSAM = Path(settings.BASE_DIR) / 'static' / 'viewer' / 'gemeinsam'
WECHSEL = ('hautSetzen', 'augenSetzen', 'augenOriginalSetzen', 'brauenSetzen', 'brauenstilSetzen', 'praesetSetzen')


class MaterialwechselTest(SimpleTestCase):
    databases = set()

    def test_gesetzt_wird_vor_dem_bau_und_einmal_ohne_neues_skelett(self):
        skript = """
const { Materialwechsel: M } = await import(MODUL);
const figur = (bau) => { const f = { reihenfolge: [], baute: [] };
    f.koerperAufbauen = async (...argumente) => { f.reihenfolge.push('bau'); f.baute.push(argumente); return bau ? bau(f) : f; };
    return f; };

// 1. Reihenfolge, Argumente, Ergebnis
const f = figur();
const erg = await M.ausfuehren(f, () => f.reihenfolge.push('aendern'));
pruefe('erst ändern, dann bauen', f.reihenfolge, ['aendern', 'bau']);
pruefe('ohne neues Skelett, einmal', f.baute, [[null, false]]);
pruefe('Ergebnis des Baus', erg === f, true);
const anderes = { name: 'anderes' };
pruefe('gibt zurück, was der Bau liefert', await M.ausfuehren(figur(() => anderes), () => {}), anderes);

// 2. aendern wirft: kein Bau, Fehler kommt an
const g = figur();
let fehler = null;
try { await M.ausfuehren(g, () => { throw new Error('kaputt'); }); } catch (e) { fehler = e.message; }
pruefe('Fehler beim Setzen kommt an', fehler, 'kaputt');
pruefe('nichts gebaut', g.baute.length, 0);

// 3. Bau scheitert: Fehler kommt an
const h = figur(() => { throw new Error('Server'); });
fehler = null;
try { await M.ausfuehren(h, () => {}); } catch (e) { fehler = e.message; }
pruefe('Fehler im Bau kommt an', fehler, 'Server');
console.log(JSON.stringify({ ok: true }));
"""
        ausgabe = MODUL.laufen(skript)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_alle_wechsel_gehen_durch_die_eine_methode(self):
        modell = (GEMEINSAM / 'genesis9modell.js').read_text(encoding='utf-8')
        for name in WECHSEL:
            kopf = f'async {name}('
            self.assertIn(kopf, modell, name)
            rumpf = modell.split(kopf, 1)[1].split('\n    }\n', 1)[0]
            self.assertIn('this.materialWechseln(', rumpf, f'{name} geht nicht durch materialWechseln')
            self.assertNotIn('koerperAufbauen(', rumpf, f'{name} baut selbst')
        self.assertIn('Materialwechsel.ausfuehren(this, aendern)', modell)
        # Außer `materialWechseln` und dem Einhängen der Stufen ruft niemand `koerperAufbauen(null, false)`.
        self.assertEqual(modell.count('koerperAufbauen(null, false)'), 0, 'der Aufruf steht nur noch in Materialwechsel')
        self.assertIn('if (!neuesSkelett) Genesis9maske.nachMaterialwechsel(this);', modell)
        maske = (GEMEINSAM / 'genesis9maske.js').read_text(encoding='utf-8')
        nacharbeit = maske.split('static nachMaterialwechsel(inst)', 1)[1]
        self.assertIn('Hautverdeckung.planen(inst);', nacharbeit)
        self.assertIn('Anatomiehaut.nachziehen(inst);', nacharbeit)

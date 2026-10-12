# -*- coding: utf-8 -*-
"""`Genesis9materialabruf`: die Netzantwort des Körpers aus dem Speicher, mit neuen Materialien oder vom Server (12.10.2026), geprüft in Node.

Edgar: „Bei einem reinen Hautwechsel das Netz nicht neu holen und nur die Texturen tauschen" und „jede Figur soll auch ihre zweite Fassung (fein) und ultrafein im RAM halten".
Gemessen im Chrome: ein Hautwechsel holte die Netzantwort noch einmal (10 MB, Serverzeit 0,9–1,4 s); jetzt fragt `Genesis9Modell.koerperAufbauen` den Speicher der Figur
(`Genesis9antwortspeicher`, je Stufe) und holt bei anderen Materialien nur die leichte Adresse `…/material/`. `Serverabruf.netzSenden` ist eine Attrappe.

1. `adresse`: `…/netz/` und `…/netz/?stufen=0` werden zu `…/material/`; eine Figur, die selbst „netz" heißt, zerstört die Adresse nicht.
2. `stellung`: Haut, Augen, Brauenfarbe und Presets ändern sie NICHT; Brauenstil, Regler, Pose, Kleidung und die Adresse (ohne Stufe) ändern sie. `material` ändert sich nur mit diesen vier.
3. `verbinden`: setzt die Gruppen des Körpers und der Anhänge ein, behält alles andere und verändert keine der beiden Antworten; bei anderer Stufe, anderem Indexbereich,
   fehlendem oder zusätzlichem Anhang oder kaputter Antwort gibt es null.
4. `holen` + `merken`: ohne Eintrag kommt die volle Antwort (`neu`); nach `merken` liefert dieselbe Frage KEINE Anfrage und eine eigene Kopie; bei anderem Material geht NUR die
   leichte Anfrage hinaus, und nach `merken` kennt der Eintrag das neue Material; eine andere Stufe, ein anderer Brauenstil, Gruppen, die nicht passen, und eine leichte Anfrage,
   die scheitert, holen voll. Ein neuer Brauenstil ersetzt den ganzen Eintrag (die alten Stufen gehörten zum alten Netz).
5. Verdrahtung am Quelltext (`Genesis9Modell` zieht die Szene nach): `koerperAufbauen` holt über `Genesis9materialabruf.holen`, merkt erst NACH `_altesWeg()` — also nur eine
   Antwort, die wirklich gebaut wird —, `Materialwechsel` baut mit `koerperAufbauen(null, false)`, und `dispose` gibt den Speicher frei.

Sabotage-Gegenprobe (nicht gefahren): in `stellung` den Brauenstil aus dem Schlüssel nehmen → Fall 2/4 rot; die Prüfung `material.stufen !== stand.stufen` streichen → Fall 3 rot;
`merken` vor `lauf !== this._lauf` stellen → Fall 5 rot; in `holen` die Stufe (`Genesis9antwortspeicher.stufe`) weglassen → Fall 4 rot.
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'genesis9materialabruf.js')
GEMEINSAM = Path(settings.BASE_DIR) / 'static' / 'viewer' / 'gemeinsam'

SKRIPT = """
const { Genesis9materialabruf: M } = await import(MODUL);
const { Serverabruf } = await import(new URL('./serverabruf.js', MODUL).href);
const { Protokoll } = await import(new URL('./protokoll.js', MODUL).href);
Protokoll.info = () => {}; Protokoll.warnung = () => {};

const gruppe = (name, ab, anzahl, bild) => ({ name, kachel: 1002, index_ab: ab, index_anzahl: anzahl, bilder: { albedo: bild } });
const stand = () => ({ vertices: new Float32Array(6), stufen: 1, skelett: { knochen: [1] }, gruppen: [gruppe('Torso', 0, 6, 'alt.jpg'), gruppe('Legs', 6, 3, 'alt.jpg')],
    anhaenge: [{ schluessel: 'augen', name: 'Augen', punkte: 'AAA', gruppen: [gruppe('Eye Left', 0, 3, 'alt.jpg')] },
               { schluessel: 'brauen', name: 'Brauen', punkte: 'BBB', gruppen: [gruppe('Eyebrows', 0, 9, 'alt.jpg')] }] });
const material = (bild = 'neu.jpg') => ({ stufen: 1, gruppen: [gruppe('Torso', 0, 6, bild), gruppe('Legs', 6, 3, bild)],
    anhaenge: [{ schluessel: 'brauen', gruppen: [gruppe('Eyebrows', 0, 9, bild)] }, { schluessel: 'augen', gruppen: [gruppe('Eye Left', 0, 3, bild)] }] });
const nutzlast = (extra = {}) => ({ regler: { a: 1 }, haut: 'h1', augen: '01', brauen: '', brauenstil: '', praesets: {}, pose: '', ausdruck: '', griffe: [], kleidung: [], ...extra });
const NETZ = '/api/character/genesis9-figur/x/netz/';
const LEICHT = '/api/character/genesis9-figur/x/material/';

// 1. Adresse
pruefe('Adresse', M.adresse(NETZ), LEICHT);
pruefe('Adresse mit Stufe', M.adresse(NETZ + '?stufen=0'), LEICHT + '?stufen=0');
pruefe('Figur heißt netz', M.adresse('/api/character/genesis9-figur/netz/netz/'), '/api/character/genesis9-figur/netz/material/');

// 2. Stellung und Material
const grund = M.stellung(NETZ, nutzlast());
pruefe('Haut egal', M.stellung(NETZ, nutzlast({ haut: 'h2' })), grund);
pruefe('Augen egal', M.stellung(NETZ, nutzlast({ augen: '05' })), grund);
pruefe('Brauenfarbe egal', M.stellung(NETZ, nutzlast({ brauen: 'Black' })), grund);
pruefe('Presets egal', M.stellung(NETZ, nutzlast({ praesets: { wimpern: 'x' } })), grund);
pruefe('Stufe in der Adresse egal', M.stellung(NETZ + '?stufen=0', nutzlast()), grund);
for (const [was, extra] of [['Brauenstil', { brauenstil: 'card05' }], ['Regler', { regler: { a: 2 } }], ['Pose', { pose: 'p' }], ['Ausdruck', { ausdruck: 'a' }],
                            ['Griffe', { griffe: ['dolch'] }], ['Kleidung', { kleidung: [{ kennung: 'k', stil: [] }] }]]) {
    pruefe(was + ' ändert die Stellung', M.stellung(NETZ, nutzlast(extra)) !== grund, true);
    pruefe(was + ' ändert das Material nicht', M.material(nutzlast(extra)), M.material(nutzlast()));
}
pruefe('andere Figur ändert die Stellung', M.stellung('/api/character/genesis9-figur/y/netz/', nutzlast()) !== grund, true);
for (const extra of [{ haut: 'h2' }, { augen: '05' }, { brauen: 'Black' }, { praesets: { wimpern: 'x' } }]) {
    pruefe('Material ändert sich mit ' + Object.keys(extra)[0], M.material(nutzlast(extra)) !== M.material(nutzlast()), true);
}

// 3. verbinden
const s = stand(), m = material();
const vorS = JSON.stringify(s), vorM = JSON.stringify(m);
const v = M.verbinden(s, m);
pruefe('Körper-Gruppen neu', v.gruppen.map(g => g.bilder.albedo), ['neu.jpg', 'neu.jpg']);
pruefe('Reihenfolge der Anhänge wie im Stand', v.anhaenge.map(a => a.schluessel), ['augen', 'brauen']);
pruefe('Anhangsgruppen neu', v.anhaenge.map(a => a.gruppen[0].bilder.albedo), ['neu.jpg', 'neu.jpg']);
pruefe('Punkte der Anhänge bleiben', v.anhaenge.map(a => a.punkte), ['AAA', 'BBB']);
pruefe('Punkte und Skelett bleiben', [v.vertices === s.vertices, v.skelett === s.skelett, v.stufen], [true, true, 1]);
pruefe('Stand unverändert', JSON.stringify(s), vorS);
pruefe('Material unverändert', JSON.stringify(m), vorM);
const nein = (was, mat, st = stand()) => pruefe(was, M.verbinden(st, mat), null);
nein('andere Stufe', { ...material(), stufen: 0 });
{ const x = material(); x.gruppen[1].index_ab = 7; nein('anderer Indexbereich', x); }
{ const x = material(); x.gruppen[0].name = 'Arms'; nein('anderer Name', x); }
{ const x = material(); x.gruppen.pop(); nein('weniger Gruppen', x); }
{ const x = material(); x.anhaenge.pop(); nein('Anhang fehlt', x); }
{ const x = material(); x.anhaenge.push({ schluessel: 'traene', gruppen: [] }); nein('zusätzlicher Anhang', x); }
{ const x = material(); x.anhaenge[0].schluessel = 'mund'; nein('fremder Anhang', x); }
{ const x = material(); x.anhaenge[1].gruppen[0].index_anzahl = 8; nein('Anhangsbereich anders', x); }
nein('ohne Gruppen', { stufen: 1, anhaenge: [] });
nein('null', null);
pruefe('ohne Stand', M.verbinden(null, material()), null);

// 4. holen + merken
const anfragen = [];
const voll = (bild = 'voll.jpg') => ({ ...stand(), gruppen: [gruppe('Torso', 0, 6, bild), gruppe('Legs', 6, 3, bild)] });
let verhalten = (adresse) => adresse.includes('/material/') ? material() : voll();
Serverabruf.netzSenden = async (adresse, rumpf) => { anfragen.push(adresse); return verhalten(adresse, rumpf); };
const frage = (inst, extra = {}, adresse = NETZ) => M.holen(inst, adresse, nutzlast(extra));
const inst = { kleidung: {} };

let r = await frage(inst);
pruefe('leer: voll', [anfragen, r.neu, r.daten.gruppen[0].bilder.albedo, r.stufe], [[NETZ], true, 'voll.jpg', 'fein']);
M.merken(inst, r);
anfragen.length = 0;
r = await frage(inst);
pruefe('gemerkt: keine Anfrage', [anfragen, r.neu, r.daten.gruppen[0].bilder.albedo], [[], false, 'voll.jpg']);
r.daten.skelett.knochen.push(2);
pruefe('Treffer ist eine Kopie', (await frage(inst)).daten.skelett.knochen, [1]);
M.merken(inst, r);                                              // ein Treffer legt nichts neu ab
pruefe('Treffer wird nicht noch einmal abgelegt', (await frage(inst)).daten.skelett.knochen, [1]);

anfragen.length = 0;
verhalten = (adresse) => adresse.includes('/material/') ? material() : voll();
r = await frage(inst, { haut: 'h2' });
pruefe('anderes Material: nur die leichte Anfrage', [anfragen, r.neu], [[LEICHT], true]);
pruefe('… auf dem gehaltenen Netz', [r.daten.gruppen.map(g => g.bilder.albedo), r.daten.anhaenge[0].punkte], [['neu.jpg', 'neu.jpg'], 'AAA']);
M.merken(inst, r);
anfragen.length = 0;
r = await frage(inst, { haut: 'h2' });
pruefe('neues Material gemerkt: keine Anfrage', [anfragen, r.neu, r.daten.gruppen[0].bilder.albedo], [[], false, 'neu.jpg']);
r = await frage(inst, { haut: 'h1' });
pruefe('zurück auf das alte Material: wieder die leichte Anfrage', anfragen, [LEICHT]);

anfragen.length = 0;
r = await frage(inst, {}, NETZ + '?stufen=0');
pruefe('andere Stufe: voll (mit ihrer Adresse)', [anfragen, r.stufe, r.neu], [[NETZ + '?stufen=0'], 'S0', true]);
M.merken(inst, r);
anfragen.length = 0;
r = await frage(inst, {}, NETZ + '?stufen=0');
pruefe('zweite Stufe gehalten', [anfragen, r.neu], [[], false]);
r = await frage(inst, { haut: 'h2' });
pruefe('die erste Stufe liegt noch daneben', anfragen, []);

anfragen.length = 0;
r = await frage(inst, { brauenstil: 'card05' });
pruefe('anderer Brauenstil: voll', [anfragen, r.neu], [[NETZ], true]);
M.merken(inst, r);
anfragen.length = 0;
await frage(inst, {}, NETZ + '?stufen=0');
pruefe('… und die alte Stellung ist samt ihren Stufen weg', anfragen, [NETZ + '?stufen=0']);

// Gruppen passen nicht / leichte Anfrage scheitert
const frisch = () => ({ kleidung: {} });
const a = frisch(); M.merken(a, await frage(a)); anfragen.length = 0;
verhalten = (adresse) => adresse.includes('/material/') ? { ...material(), stufen: 2 } : voll();
r = await frage(a, { haut: 'h2' });
pruefe('Gruppen passen nicht: leicht, dann voll', [anfragen, r.daten.gruppen[0].bilder.albedo], [[LEICHT, NETZ], 'voll.jpg']);
anfragen.length = 0;
verhalten = (adresse) => { if (adresse.includes('/material/')) throw new Error('404'); return voll(); };
r = await frage(a, { haut: 'h3' });
pruefe('leichte Anfrage scheitert: voll', [anfragen, r.daten.gruppen[0].bilder.albedo], [[LEICHT, NETZ], 'voll.jpg']);
console.log(JSON.stringify({ ok: true }));
"""


class Genesis9materialabrufTest(SimpleTestCase):

    def test_koerperantwort_aus_dem_speicher_mit_neuen_materialien_oder_vom_server(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

    def test_verdrahtung_im_modell_und_im_materialwechsel(self):
        modell = (GEMEINSAM / 'genesis9modell.js').read_text(encoding='utf-8')
        self.assertIn("import { Genesis9materialabruf } from './genesis9materialabruf.js';", modell)
        kopf = 'async koerperAufbauen(stufen = null, skelettFrisch = true, vorBau = null) {'
        self.assertIn(kopf, modell)
        rumpf = modell.split(kopf, 1)[1].split('\n    }\n', 1)[0]
        self.assertIn('Genesis9materialabruf.holen(this, adresse, Genesis9materialabruf.nutzlast(this))', rumpf)
        self.assertNotIn('Serverabruf.netzSenden', rumpf, 'der Netzabruf läuft nur noch über Genesis9materialabruf')
        # Gemerkt wird erst, wenn gebaut wird: nach den Prüfungen auf eine überholte Antwort und nach dem Entfernen des alten Netzes.
        self.assertLess(rumpf.index('if (lauf !== this._lauf) return this;'), rumpf.index('this._altesWeg();'))
        self.assertLess(rumpf.index('this._altesWeg();'), rumpf.index('Genesis9materialabruf.merken(this, antwort);'))
        self.assertLess(rumpf.index('Genesis9materialabruf.merken(this, antwort);'), rumpf.index('Genesis9netz.bauen('), 'vor dem Bau: er verändert die Antwort')
        self.assertIn('this._antworten = null;', modell.split('dispose() {', 1)[1], 'dispose gibt den Speicher frei')
        wechsel = (GEMEINSAM / 'materialwechsel.js').read_text(encoding='utf-8')
        self.assertIn('modell.koerperAufbauen(null, false)', wechsel)
        self.assertNotIn('nurMaterial', modell + wechsel, 'der Speicher entscheidet allein (Stellung, Stufe, Material), kein Schalter am Aufrufer')

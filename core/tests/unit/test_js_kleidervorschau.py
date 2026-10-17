# -*- coding: utf-8 -*-
u"""`Kleidervorschau`: die Kleidung folgt einem neuen Körper sofort, noch vor der genauen Lage vom Server (16.10.2026), geprüft in Node.

WARUM (Edgar, 16.10.2026: „ich habe das Gewicht erhöht, Alter, es tut sich nichts … Der Regler soll viel schneller die Figur ändern können. Warum dauert das so lange?"):
Ein Reglerzug an Mann1 (Körper + T-Shirt, Boxershorts, Haar, Stiefel) brauchte 8 bis 20 s, bis sich auf dem Bildschirm etwas änderte. Gemessen (Server im Leerlauf,
`ProjektTemp/_wegwerf/mann_regler/zeit_je_stueck.py`): Körper 0,3 s, T-Shirt 3,5 s, Boxershorts 1,3 s, Haar 1,9 s, Stiefel 0,3 s — das T-Shirt verdeckt die Haut, der Körper
allein zeigt also nichts. Jetzt nimmt `Kleidervorschau` die gebundenen Stoffpunkte um die Verschiebung ihres Körperpunkts mit, sobald der Körper da ist (im Chrome gemessen:
Vorschau 0,47 mm Mittel gegen die spätere genaue Lage beim T-Shirt, 0,87 mm bei den Boxershorts — ohne Vorschau 16,6 und 22,1 mm).

1. `folgen` verschiebt jeden gebundenen Punkt um `mischung` mal die baryzentrisch gemischte Verschiebung der drei Körperpunkte; `mischung` 0 bleibt stehen; Hülle und Kugel gelten neu.
2. Nicht verschoben wird: ein Stück, das in DIESEM Lauf vom Server kam (`geometry.userData.lauf`), eines mit anderer Stufe oder Punktzahl der Bindung, eines im Stoffschwung;
   und nichts, wenn der Körper anders groß ist, auf anderer Stufe steht oder sich nicht bewegt hat.
3. `merken` liefert eine Kopie (der Körper wird danach ersetzt oder verändert).
4. `begleiten` wartet auf den Körper und gilt nur, wenn der Lauf nicht überholt wurde — sonst käme dieselbe Verschiebung zweimal; ein Fehler des Körpers wird nicht verschluckt (er gehört
   dem Aufrufer), und eine Ausnahme beim Mitnehmen wird gemeldet.
5. Die Verdrahtung am Quelltext: `Genesis9aufbau.alles` merkt den Körper VOR `koerperAufbauen`, `Genesis9kleidung.anziehen` vermerkt den Lauf, die Sanduhr steht unten in der Mitte
   mit Sekunden und der Zeiger ist `wait`.

Sabotage-Gegenprobe (nicht gefahren): in `_mitnehmen` die Prüfung `geo.userData.lauf === inst._lauf` streichen → Fall 2 rot; `inst._lauf !== lauf` in `begleiten` streichen → Fall 4 rot;
`m` aus der Rechnung nehmen → Fall 1 rot. Tests geschrieben, nicht gelaufen (nur auf Ansage).
"""
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'kleidervorschau.js')
STATIC = Path(settings.BASE_DIR) / 'static'

SKRIPT = """
const { Kleidervorschau: K } = await import(MODUL);
const { Protokoll } = await import(new URL('./protokoll.js', MODUL).href);
const warnungen = [];
Protokoll.debug = () => {}; Protokoll.warnung = (_ort, text) => warnungen.push(text);
const nah = (was, ist, soll) => {
    if (Math.abs(ist - soll) > 1e-6) throw new Error(was + ': ' + ist + ' statt ' + soll);
};

// Ein Körper aus drei Punkten; `p` = die Koordinaten.
const koerper = (p, stufen = 1) => ({ stufen, _lauf: 5, clothMeshes: {},
    bodyMesh: { geometry: { attributes: { position: { array: Float32Array.from(p), count: p.length / 3 } } } } });
const ALT = [0, 0, 0, 1, 0, 0, 0, 1, 0];
const NEU = [0.1, 0, 0, 1, 0.2, 0, 0, 1, 0.3];          // Verschiebung: v0 (0,1;0;0), v1 (0;0,2;0), v2 (0;0;0,3)

// Ein Stück mit drei Punkten: 1 voll an v0, 2 halb an v0/v1 mit mischung 0,5, 3 frei (mischung 0).
const stueck = (extra = {}, bindung = { stufen: 1 }) => ({ userData: {}, geometry: { boundingSphere: 'alt', boundingBox: 'alt', userData: { bindung, ...extra },
    attributes: { position: { array: Float32Array.from([5, 5, 5, 6, 6, 6, 7, 7, 7]), count: 3, needsUpdate: false },
                  bindung: { array: Float32Array.from([0, 1, 2, 0, 1, 2, 0, 1, 2]) },
                  bary: { array: Float32Array.from([1, 0, 0, 0.5, 0.5, 0, 1, 0, 0]) },
                  mischung: { array: Float32Array.from([1, 0.5, 0]) } } } });
const lage = (netz) => Array.from(netz.geometry.attributes.position.array);

// 1. Die Rechnung
{
    const inst = koerper(NEU); const netz = stueck(); inst.clothMeshes.hemd = netz;
    const n = K.folgen(inst, { punkte: Float32Array.from(ALT), stufen: 1 });
    pruefe('ein Stück bewegt', n, 1);
    const p = lage(netz);
    nah('Punkt 1 x', p[0], 5.1); nah('Punkt 1 y', p[1], 5); nah('Punkt 1 z', p[2], 5);
    nah('Punkt 2 x', p[3], 6.025); nah('Punkt 2 y', p[4], 6.05); nah('Punkt 2 z', p[5], 6);
    nah('Punkt 3 bleibt x', p[6], 7); nah('Punkt 3 bleibt y', p[7], 7);
    pruefe('Aktualisierung', netz.geometry.attributes.position.needsUpdate, true);
    pruefe('Kugel neu', netz.geometry.boundingSphere, null);
    pruefe('Hülle neu', netz.geometry.boundingBox, null);
}

// 2. Was nicht verschoben wird
{
    const unveraendert = [5, 5, 5, 6, 6, 6, 7, 7, 7];
    const vorher = () => ({ punkte: Float32Array.from(ALT), stufen: 1 });
    const faelle = [
        ['Stück aus diesem Lauf', stueck({ lauf: 5 })],
        ['andere Stufe der Bindung', stueck({}, { stufen: 0 })],
        ['andere Punktzahl der Bindung', stueck({}, { stufen: 1, punkte: 99 })],
    ];
    for (const [was, netz] of faelle) {
        const inst = koerper(NEU); inst.clothMeshes.hemd = netz;
        pruefe(was + ': Zahl', K.folgen(inst, vorher()), 0);
        pruefe(was + ': Lage', lage(netz), unveraendert);
    }
    const stoff = stueck(); stoff.userData.stoff = { frei: 1 };
    const inst = koerper(NEU); inst.clothMeshes.hemd = stoff;
    pruefe('Stoffschwung: Zahl', K.folgen(inst, vorher()), 0);
    pruefe('Stoffschwung: Lage', lage(stoff), unveraendert);
    const ohne = { userData: {}, geometry: { userData: {}, attributes: {} } };
    inst.clothMeshes.haar = ohne;
    pruefe('Stück ohne Bindung (Haar)', K.folgen(inst, vorher()), 0);

    const anders = koerper([...NEU, 9, 9, 9]); const netz = stueck(); anders.clothMeshes.hemd = netz;
    pruefe('anders großer Körper', K.folgen(anders, vorher()), 0);
    const stufe = koerper(NEU, 0); stufe.clothMeshes.hemd = stueck();
    pruefe('andere Stufe des Körpers', K.folgen(stufe, vorher()), 0);
    const still = koerper(ALT); const netz2 = stueck(); still.clothMeshes.hemd = netz2;
    pruefe('Körper unverändert: Zahl', K.folgen(still, vorher()), 0);
    pruefe('Körper unverändert: Lage', lage(netz2), unveraendert);
    pruefe('ohne vorher', K.folgen(koerper(NEU), null), 0);
}

// 3. merken liefert eine Kopie
{
    const inst = koerper(ALT); const m = K.merken(inst);
    inst.bodyMesh.geometry.attributes.position.array[0] = 42;
    pruefe('Kopie', m.punkte[0], 0);
    pruefe('Stufe gemerkt', m.stufen, 1);
    pruefe('ohne Körper', K.merken({ bodyMesh: null }), null);
}

// 4. begleiten
{
    const vorher = () => ({ punkte: Float32Array.from(ALT), stufen: 1 });
    const inst = koerper(NEU); const netz = stueck(); inst.clothMeshes.hemd = netz;
    const fertig = Promise.resolve(inst);
    K.begleiten(inst, vorher(), fertig);
    await fertig;
    nah('begleitet: bewegt', lage(netz)[0], 5.1);

    const ueberholt = koerper(NEU); const netz2 = stueck(); ueberholt.clothMeshes.hemd = netz2;
    const spaet = Promise.resolve(ueberholt);
    K.begleiten(ueberholt, vorher(), spaet);
    ueberholt._lauf = 6;                                  // ein neuerer Zug hat begonnen, bevor der Körper kam
    await spaet;
    nah('überholt: nicht bewegt', lage(netz2)[0], 5);

    const kaputt = Promise.reject(new Error('Körper fehlt'));
    K.begleiten(koerper(NEU), vorher(), kaputt);
    await kaputt.catch(() => {});
    pruefe('Körperfehler wird nicht von hier gemeldet', warnungen.length, 0);

    const defekt = koerper(NEU); defekt.clothMeshes.hemd = { userData: {}, geometry: null };
    defekt.clothMeshes.hemd.geometry = { get userData() { throw new Error('kaputt'); } };
    const gut = Promise.resolve(defekt);
    K.begleiten(defekt, vorher(), gut);
    await gut;
    pruefe('Ausnahme beim Mitnehmen wird gemeldet', warnungen.length, 1);
}
console.log(JSON.stringify({ ok: true }));
"""


class KleidervorschauTest(SimpleTestCase):
    databases = set()

    def test_1_die_stuecke_folgen_dem_neuen_koerper_und_nichts_wird_doppelt_verschoben(self):
        self.assertTrue(MODUL.laufen(SKRIPT).get('ok'))

    def test_2_die_verdrahtung_im_aufbau_und_in_der_kleidung(self):
        aufbau = (STATIC / 'viewer' / 'gemeinsam' / 'genesis9aufbau.js').read_text(encoding='utf-8')
        self.assertIn("import { Kleidervorschau } from './kleidervorschau.js';", aufbau)
        self.assertLess(aufbau.index('Kleidervorschau.merken(inst)'), aufbau.index('inst.koerperAufbauen(stufen)'), 'der Körper VOR dem Zug merken')
        self.assertIn('Kleidervorschau.begleiten(inst, vorher, koerper)', aufbau)
        kleidung = (STATIC / 'viewer' / 'gemeinsam' / 'genesis9kleidung.js').read_text(encoding='utf-8')
        self.assertIn('netz.geometry.userData.lauf = lauf;', kleidung, 'ein Stück vom Server für diesen Zug ist genau')

    def test_3_die_sanduhr_steht_unten_in_der_mitte_mit_sekunden_und_der_zeiger_ist_wait(self):
        sanduhr = (STATIC / 'viewer' / 'gemeinsam' / 'sanduhr.js').read_text(encoding='utf-8')
        self.assertIn("left: '50%'", sanduhr)
        self.assertIn('translateX(-50%)', sanduhr)
        self.assertIn("setInterval(Sanduhr._zeigen, 250)", sanduhr)
        self.assertIn('clearInterval(Sanduhr._zeitgeber)', sanduhr, 'die Uhr hört mit der Sanduhr auf')
        css = (STATIC / 'css' / 'stilhelfer.css').read_text(encoding='utf-8')
        self.assertIn('cursor: wait !important', css)

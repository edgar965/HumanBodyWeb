# -*- coding: utf-8 -*-
"""Das Kleidungsobjekt aus dem Netz als Stück für die Haut-Verdeckung (14.10.2026, `Meshfighautstueck`, `Meshfigurkleider._hautMelden`, `Figurhaut.stuecke`) — Edgar: Mesh-3D soll sich wie Charakter und Studio verhalten, dort kommt die Haut unter dem Stoff nicht durch.
Nicht gelaufen — läuft nur auf Ansage.

    VerschweissenTest  Punkte mit gleicher Lage werden zusammengelegt (UV-Nähte), Dreiecke mit zwei gleichen Ecken fallen weg, Lage und Reihenfolge bleiben; `visible` fragt das Netz zur Zeit der Frage
    DrahtTest          Quelltext: die Haut-Verdeckung liest `Figurhaut.stuecke` (Garderobe + angemeldete Objekte), Mesh-3D meldet das Kleidungsobjekt an und stößt die Maske bei Wechsel von Netz oder Sichtbarkeit an

Gemessen (Ballerina `…15.00.06`, Chrome): ohne Verschweißen galten 24.242 von 29.366 Punkten als Rand, die Maske verdeckte 248 Körperpunkte; mit 16.016 Punkten (3.021 Randpunkte) 24.079; „Kleider“ aus → 0, an → 24.079.
Sabotage: in `verschweissen` den Nachschlag `nummer.get` weglassen (jeder Punkt neu) → `test_nahtkopien_werden_zusammengelegt` rot; `Meshfigurkleider._hautMelden` ohne `Hautverdeckung.planen` → `DrahtTest` rot.
"""

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

STUECK = Jsmodul('meshfigur', 'meshfighautstueck.js')
WEB = Path(settings.BASE_DIR)

SKRIPT = """
const { Meshfighautstueck } = await import(MODUL);
// Zwei Dreiecke an einer UV-Naht: die Punkte 3 und 4 liegen dort, wo 1 und 2 liegen
const P = new Float32Array([0, 0, 0,  1, 0, 0,  0, 1, 0,  1, 0, 0,  0, 1, 0,  1, 1, 0]);
const T = new Uint32Array([0, 1, 2,  3, 5, 4]);
const r = Meshfighautstueck.verschweissen(P, T);
pruefe('vier Punkte statt sechs', r.punkte.length / 3, 4);
pruefe('Dreiecke zeigen auf die gemeinsamen Punkte', Array.from(r.dreiecke), [0, 1, 2, 1, 3, 2]);
pruefe('Lage unverändert', Array.from(r.punkte.slice(9, 12)), [1, 1, 0]);
// Ein Dreieck, das beim Verschweißen zwei gleiche Ecken bekommt, fällt weg
const P2 = new Float32Array([0, 0, 0,  0, 0, 0,  1, 1, 1,  2, 0, 0]);
const T2 = new Uint32Array([0, 1, 2,  0, 2, 3]);
const r2 = Meshfighautstueck.verschweissen(P2, T2);
pruefe('entartetes Dreieck weg', Array.from(r2.dreiecke), [0, 1, 2]);
// Offene Kanten vorher und nachher (Kante in genau einem Dreieck)
const offen = (t, n) => { const z = new Map(); for (let k = 0; k + 2 < t.length; k += 3) for (const [a, b] of [[t[k], t[k + 1]], [t[k + 1], t[k + 2]], [t[k + 2], t[k]]]) { const s = a < b ? a * n + b : b * n + a; z.set(s, (z.get(s) || 0) + 1); } return [...z.values()].filter(c => c === 1).length; };
pruefe('sechs offene Kanten roh', offen(T, 6), 6);
pruefe('vier nach dem Verschweißen (die gemeinsame Kante liegt in zwei Dreiecken)', offen(r.dreiecke, 4), 4);
// Die Hülle sieht aus wie ein Stück: Punkte, Index, userData, `visible` folgt dem Netz zur Zeit der Frage
let netz = { visible: true };
const geometrie = { getAttribute: () => ({ array: P }), index: { array: T } };
const stueck = new Meshfighautstueck(geometrie, () => netz);
pruefe('Punkte des Stücks', stueck.geometry.attributes.position.array.length / 3, 4);
pruefe('Index des Stücks', stueck.geometry.index.array.length / 3, 2);
pruefe('art', stueck.userData.art, 'kleidung');
pruefe('sichtbar', stueck.visible, true);
netz = { visible: false };
pruefe('ausgeblendet verdeckt nichts', stueck.visible, false);
netz = null;
pruefe('Netz weg: zählt wie bisher (die Maske prüft die Zahl der Stücke)', stueck.visible, true);
console.log(JSON.stringify({ ok: true }));
"""


class VerschweissenTest(SimpleTestCase):
    databases = set()

    def test_nahtkopien_werden_zusammengelegt(self):
        ausgabe = STUECK.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)


class DrahtTest(SimpleTestCase):
    databases = set()

    def _text(self, *teile):
        return WEB.joinpath('static', 'viewer', *teile).read_text(encoding='utf-8')

    def test_die_verdeckung_liest_garderobe_und_angemeldete_objekte(self):
        haut = self._text('gemeinsam', 'figurhaut.js')
        self.assertIn('static stuecke(inst)', haut)
        self.assertIn('...(inst?.clothMeshes || {}), ...(inst?.hautStuecke || {})', haut)
        verdeckung = self._text('gemeinsam', 'hautverdeckung.js')
        self.assertGreaterEqual(verdeckung.count('Object.entries(Hautverdeckung.stuecke(inst))'), 2, 'zaehlende UND stoffe')
        self.assertNotIn('Object.entries(inst?.clothMeshes', verdeckung, 'kein zweiter Weg an `stuecke` vorbei')

    def test_mesh3d_meldet_das_kleidungsobjekt_an(self):
        text = self._text('meshfigur', 'meshfigurkleider.js')
        self.assertIn('new Meshfighautstueck(geometrie, () => this._netz())', text)
        self.assertIn('modell.hautStuecke = geometrie ? { [Meshfigurkleider.HAUTSTUECK]: this._hautStueck } : {};', text)
        self.assertIn('Hautverdeckung.planen(modell);', text)
        # Netz (nach dem Binden ein neues Objekt) und Sichtbarkeit gehören zum Stand — sonst bliebe die Maske nach dem Ausblenden stehen
        self.assertIn('`${netz.uuid}|${netz.visible}`', text)
        # jede Meldung über `anwenden`, das die Bühne ohnehin bei jedem Stand ruft
        self.assertIn('this._hautMelden();', text)
        self.assertIn('if (modell !== this.modell) this._hautStand = null;', text)

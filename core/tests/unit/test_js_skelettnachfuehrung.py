# -*- coding: utf-8 -*-
u"""`Skelettnachfuehrung` — die drei Dinge, die still schiefgehen können.

WARUM (05.09.2026)
==================
Der Server rechnet die neuen Knochenlagen (`Gelenkanpassung`), der Browser
setzt sie. Zwischen beiden liegen drei Fallen, und keine davon wirft:

1. **Nicht neu gebunden.** Three.js merkt sich beim Binden je Knochen die
   Umkehrmatrix seiner Ruhelage. Wer einen Knochen verschiebt und
   `calculateInverses()` unterlässt, verschiebt damit das ganze Netz — der
   Körper zerreißt, und die Konsole bleibt still.
2. **Beim Binden stand eine Pose.** `calculateInverses()` liest die
   AKTUELLEN Weltmatrizen. Läuft eine Animation, brennt das laufende Bild
   als Ruhelage ein. Danach ist die Figur dauerhaft verdreht.
3. **Nur die genannten Knochen gesetzt.** Die Nachricht trägt die BEWEGTEN;
   was fehlt, gehört in die Ruhelage. Wer nur die genannten setzt, lässt
   beim Zurückdrehen des Reglers stehen, was einmal verschoben war — und
   genau dieser Fall (leere Nachricht) ist der Rückweg auf Größe 0.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'skelettnachfuehrung.js')

SKRIPT = """
const { Skelettnachfuehrung } = await import(MODUL);

// Zwei Knochen, beide ohne Eigendrehung. Blender [w,x,y,z] = [1,0,0,0].
const DATEN = { bones: [
    {name: 'DEF-spine',     parent: null,
     local_position: [0, 0, 1],   local_quaternion: [1, 0, 0, 0]},
    {name: 'DEF-spine.001', parent: 'DEF-spine',
     local_position: [0, 0, 0.5], local_quaternion: [1, 0, 0, 0]},
]};

class Quat {
    constructor(x, y, z, w) { this.set(x, y, z, w); }
    set(x, y, z, w) { this.x = x; this.y = y; this.z = z; this.w = w; return this; }
    clone() { return new Quat(this.x, this.y, this.z, this.w); }
    copy(q) { return this.set(q.x, q.y, q.z, q.w); }
    liste() { return [this.x, this.y, this.z, this.w]; }
}
class Vek {
    constructor() { this.set(0, 0, 0); }
    set(x, y, z) { this.x = x; this.y = y; this.z = z; return this; }
    liste() { return [this.x, this.y, this.z]; }
}
class Knochen {
    constructor(name) {
        this.name = name; this.position = new Vek(); this.quaternion = new Quat(0,0,0,1);
    }
}

function aufbau() {
    const spine = new Knochen('DEF-spine');
    const kind = new Knochen('DEF-spine.001');
    const protokoll = { folge: [], gebunden: 0, ruhelagen: [] };
    const skelett = {
        boneByName: {'DEF-spine': spine, 'DEF-spine.001': kind},
        skeleton: {
            bones: [spine, kind],
            calculateInverses() {
                protokoll.gebunden += 1;
                protokoll.folge.push('binden');
                // Was in DIESEM Moment steht, waere die neue Ruhelage.
                protokoll.ruhelagen.push({
                    lagen: [spine.position.liste(), kind.position.liste()],
                    drehungen: [spine.quaternion.liste(), kind.quaternion.liste()],
                });
            },
        },
    };
    const netz = { updateMatrixWorld() { protokoll.folge.push('welt'); } };
    spine.parent = netz;
    return { spine, kind, skelett, netz, protokoll };
}

const fuehrung = new Skelettnachfuehrung(DATEN);
const ergebnis = {};

// 1. Ein bewegter Knochen, der andere nicht genannt.
{
    const { spine, kind, skelett, netz, protokoll } = aufbau();
    const ok = fuehrung.anwenden(netz, skelett, {'DEF-spine': [0, 0, 2]});
    ergebnis.einer = {
        ok,
        bewegt: spine.position.liste(),
        ungenannt: kind.position.liste(),
        gebunden: protokoll.gebunden,
        folge: protokoll.folge,
    };
}

// 2. Leere Nachricht, nachdem etwas verschoben war -> alles zurueck.
{
    const { spine, kind, skelett, netz } = aufbau();
    fuehrung.anwenden(netz, skelett, {'DEF-spine': [0, 0, 2]});
    fuehrung.anwenden(netz, skelett, {});
    ergebnis.zurueck = {
        wurzel: spine.position.liste(),
        kind: kind.position.liste(),
    };
}

// 3. Waehrend einer laufenden Pose.
{
    const { spine, kind, skelett, netz, protokoll } = aufbau();
    spine.quaternion.set(0.5, 0.5, 0.5, 0.5);   // irgendein Bild der Animation
    kind.quaternion.set(0, 0.7071, 0, 0.7071);
    fuehrung.anwenden(netz, skelett, {'DEF-spine': [0, 0, 2]});
    ergebnis.pose = {
        beimBinden: protokoll.ruhelagen[0].drehungen,
        danach: [spine.quaternion.liste(), kind.quaternion.liste()],
    };
}

// 4. Kein Netz, kein Skelett, keine Daten.
{
    const { skelett, netz } = aufbau();
    ergebnis.leerlauf = {
        ohneNetz: fuehrung.anwenden(null, skelett, {}),
        ohneSkelett: fuehrung.anwenden(netz, null, {}),
        ohneDaten: new Skelettnachfuehrung({}).anwenden(netz, skelett, {}),
        brauchbar: fuehrung.brauchbar,
    };
}

// 5. Die Koordinatenwandlung: Blender (x,y,z) -> Three.js (x,z,-y).
{
    const { spine, skelett, netz } = aufbau();
    fuehrung.anwenden(netz, skelett, {'DEF-spine': [1, 2, 3]});
    ergebnis.achsen = spine.position.liste();
}

console.log(JSON.stringify(ergebnis));
"""


class SkelettnachfuehrungTest(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.e = MODUL.laufen(SKRIPT)

    def test_der_genannte_knochen_wird_gesetzt(self):
        self.assertIs(self.e['einer']['ok'], True)
        self.assertEqual(self.e['einer']['bewegt'], [0, 2, 0])

    def test_der_ungenannte_bekommt_seine_ruhelage(self):
        u"""Falle 3: Er stand vorher auf (0,0,0), weil ein frischer Knochen
        das tut. Ohne diese Zeile bliebe er dort und die Kette risse."""
        self.assertEqual(self.e['einer']['ungenannt'], [0, 0.5, 0])

    def test_es_wird_neu_gebunden(self):
        u"""Falle 1. Ohne `calculateInverses()` verschiebt der Knochen das
        Netz statt sich selbst — der Körper zerreißt, lautlos."""
        self.assertEqual(self.e['einer']['gebunden'], 1)

    def test_und_zwar_erst_nach_dem_auffrischen_der_weltmatrizen(self):
        u"""Die Reihenfolge ist der Punkt, nicht die Anzahl: Die Knochen
        hängen unter dem SkinnedMesh, dessen eigene Weltmatrix in die
        Umkehrmatrizen eingeht. Wer zuerst bindet, bindet an die Lagen von
        vorher — und sieht davon nichts.

        Das dritte Auffrischen gehört zum Zurückschreiben der Pose: Danach
        stimmen die Weltmatrizen wieder zu dem, was wirklich gesetzt ist.
        """
        self.assertEqual(self.e['einer']['folge'], ['welt', 'binden', 'welt'])

    def test_eine_leere_nachricht_holt_alles_zurueck(self):
        u"""Der Rückweg: Regler auf 0, `reset`, Körperart zurück. Ohne das
        bliebe das Skelett in der zuletzt gemeldeten Größe stehen."""
        self.assertEqual(self.e['zurueck']['wurzel'], [0, 1, 0])
        self.assertEqual(self.e['zurueck']['kind'], [0, 0.5, 0])

    def test_beim_binden_stehen_die_ruhedrehungen(self):
        u"""Falle 2: Wäre hier die laufende Pose zu sehen, würde sie als
        Ruhelage einbrennen und die Figur bliebe verdreht."""
        self.assertEqual(self.e['pose']['beimBinden'], [[0, 0, 0, 1], [0, 0, 0, 1]])

    def test_die_pose_laeuft_danach_weiter(self):
        u"""Nachbinden darf die Animation nicht anhalten."""
        self.assertEqual(self.e['pose']['danach'],
                         [[0.5, 0.5, 0.5, 0.5], [0, 0.7071, 0, 0.7071]])

    def test_ohne_netz_skelett_oder_daten_passiert_nichts(self):
        u"""Die Nachricht kann vor dem Skinning eintreffen — dann ist
        „nichts tun" richtig, nicht „werfen"."""
        self.assertIs(self.e['leerlauf']['ohneNetz'], False)
        self.assertIs(self.e['leerlauf']['ohneSkelett'], False)
        self.assertIs(self.e['leerlauf']['ohneDaten'], False)
        self.assertIs(self.e['leerlauf']['brauchbar'], True)

    def test_die_achsen_werden_gedreht(self):
        u"""Blender (x,y,z) -> Three.js (x,z,-y) — dieselbe Wandlung wie im
        Skelettbauer. Wer sie hier vergisst, legt die Figur hin."""
        self.assertEqual(self.e['achsen'], [1, 3, -2])

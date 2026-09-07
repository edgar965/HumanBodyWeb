# -*- coding: utf-8 -*-
u"""`Rigauswahl`: welche Figur bekommt Knochenlinien?

WARUM (07.09.2026, Edgar: „es gibt einen Button zum Rig ein und ausblenden.
das blendet das aber nur für HumanBody ein/aus. das soll für alle Modelle
sein die sichtbar sind."): Der alte Umschalter nahm `_selectedInst()` und
verwaltete einen einzigen `state.skeletonHelper`. Bei vier Figurarten in
einer Szene sah man das Rig genau einer Figur.

Geprüft wird die Entscheidung, nicht die Anzeige — deshalb liegt sie in
einem Modul ohne Three.js und ohne DOM:

1. Die Wurzel wird aus dem Feld gelesen, das die jeweilige Figurart führt
   (HumanBody `rigifySkeleton`, UMA `skelett`), sonst im Szenenbaum gesucht.
2. Figuren ohne Skelett (SMPL, MakeHuman) fallen heraus — sie haben keines,
   und eine leere Anzeige wäre eine Lüge.
3. Ausgeblendete Figuren bekommen keine Linien; ein Skelett ohne Körper im
   Bild ist schlimmer als keines.
4. Der Abgleich meldet `ersetzt`, wenn eine Figur unter DERSELBEN id eine
   neue Wurzel bekommt. Das ist der Fall, den man vergisst: Die
   SMPL-Formregler und der UMA-Typwechsel tauschen die Instanz aus
   (`state.characters.set(inst.id, neu)`), und wer nur ids vergleicht,
   behält Linien an einem Skelett, das nicht mehr in der Szene steht.

FEHLT `node`, ist das ein FEHLER — siehe `Jsmodul.laufen`.
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul

MODUL = Jsmodul('gemeinsam', 'rigauswahl.js')

SKRIPT = """
const { Rigauswahl: R } = await import(MODUL);
const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt ' + JSON.stringify(soll));
    }
};

// Figuren, wie die vier Arten sie halten.
const knochen = (name) => ({ name, isBone: true, parent: null });
const humanbody = { id: 'hb', group: {}, rigifySkeleton: { rootBone: knochen('DEF-spine') } };
const uma       = { id: 'uma', group: {}, quelle: 'uma', skelett: { rootBone: knochen('Root') } };
const smpl      = { id: 'smpl', group: {}, quelle: 'smpl' };
const makehuman = { id: 'mh', group: {}, quelle: 'makehuman' };

// --- 1. Die Wurzel kommt aus dem Feld der jeweiligen Art -------------------
pruefe('HumanBody', R.wurzel(humanbody).name, 'DEF-spine');
pruefe('UMA', R.wurzel(uma).name, 'Root');
pruefe('ohne Skelett', R.wurzel(smpl), null);
pruefe('ohne Figur', R.wurzel(null), null);

// --- 2. Der Ausweg: Suche im Szenenbaum ------------------------------------
// Ein importiertes GLB fuehrt sein Skelett in keinem der bekannten Felder.
const glb = { id: 'glb', group: {} };
const gefunden = knochen('Hips');
pruefe('Baumsuche greift', R.wurzel(glb, () => gefunden).name, 'Hips');
// Die Suche darf das bekannte Feld NICHT ueberschreiben.
pruefe('Feld hat Vorrang', R.wurzel(humanbody, () => gefunden).name, 'DEF-spine');

// --- 3. Sichtbarkeit -------------------------------------------------------
pruefe('ohne visible-Feld sichtbar', R.sichtbar(humanbody), true);
pruefe('visible true', R.sichtbar({ id: 'x', group: { visible: true } }), true);
pruefe('visible false', R.sichtbar({ id: 'x', group: { visible: false } }), false);
pruefe('ohne group', R.sichtbar({ id: 'x' }), true);
pruefe('keine Figur', R.sichtbar(null), false);

// --- 4. Traeger: alle sichtbaren MIT Skelett -------------------------------
const alle = [humanbody, uma, smpl, makehuman];
pruefe('vier Arten, zwei mit Rig',
       R.traeger(alle).map(t => t.inst.id), ['hb', 'uma']);
// Genau das war der Fehler: EINE Figur statt aller.
if (R.traeger(alle).length < 2) throw new Error('nur eine Figur getragen');
const versteckt = { id: 'hb2', group: { visible: false },
                    rigifySkeleton: { rootBone: knochen('DEF-spine') } };
pruefe('ausgeblendet faellt raus',
       R.traeger([humanbody, versteckt]).map(t => t.inst.id), ['hb']);
pruefe('leer', R.traeger([]), []);
pruefe('null', R.traeger(null), []);

// --- 5. Abgleich -----------------------------------------------------------
const t0 = R.traeger(alle);
let a = R.abgleich(t0, new Map());
pruefe('erst alles neu', a.neu.map(t => t.inst.id), ['hb', 'uma']);
pruefe('nichts weg', a.weg, []);

const bestand = new Map(t0.map(t => [t.inst.id, t.wurzel]));
a = R.abgleich(t0, bestand);
pruefe('unveraendert: nichts neu', a.neu, []);
pruefe('unveraendert: nichts ersetzt', a.ersetzt, []);
pruefe('unveraendert: nichts weg', a.weg, []);

// Figur verschwindet.
a = R.abgleich(R.traeger([uma]), bestand);
pruefe('verschwundene gemeldet', a.weg, ['hb']);

// DIESELBE id, NEUE Wurzel — der Fall der SMPL-/UMA-Regler.
const ersetztFigur = { id: 'hb', group: {},
                       rigifySkeleton: { rootBone: knochen('DEF-neu') } };
a = R.abgleich(R.traeger([ersetztFigur, uma]), bestand);
pruefe('neue Wurzel wird gemeldet', a.ersetzt.map(t => t.inst.id), ['hb']);
pruefe('und gilt nicht als neu', a.neu, []);
pruefe('und nicht als weg', a.weg, []);

// Ausgeblendete Figur zaehlt wie verschwunden — ihre Linien muessen fort.
a = R.abgleich(R.traeger([versteckt, uma]), new Map([['hb2', knochen('x')]]));
pruefe('ausgeblendet raeumt ab', a.weg, ['hb2']);

console.log(JSON.stringify({ok: true}));
"""


class RigauswahlTest(SimpleTestCase):

    databases = []

    def test_auswahl(self):
        ausgabe = MODUL.laufen(SKRIPT)
        self.assertTrue(ausgabe.get('ok'), ausgabe)

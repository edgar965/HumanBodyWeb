# -*- coding: utf-8 -*-
"""`Hautverdeckung`: die Haut unter der Kleidung wird nicht gezeichnet —
die Verdrahtung, geprüft am Quelltext.

Die Rechnung selbst prüft `test_js_hautmaske.py` in Node. Hier die Stellen,
die still danebengehen könnten:

* Das Modul wird überhaupt geladen (`boot.js`) und hört auf das
  Stückereignis — sonst rechnet niemand die Maske.
* Ein Stück, das über die Teilnetz-Auswahl (Entf-Taste) geht, meldet das
  Ereignis auch: Dieser Weg läuft an `GarmentcodeAnziehen.entfernen`
  vorbei, und ohne Meldung bliebe ein Loch im Körper, wo kein Stoff mehr ist.
* Der VOLLE Index bleibt am Netz, und die Stoffgrenze des Weichgewebes
  rechnet damit — die verdeckten Punkte sind genau die, an denen der Stoff
  hängt; mit dem gekürzten Index hätten sie keine Normale.
* Ohne Stücke wird der volle Index wiederhergestellt.
* Die Randdreiecke bleiben, ihre verdeckten Ecken bekommen den Einzug
  (`Hauteinzug`, Shader-Attribut `einzug` VOR dem Skinning), und die
  Lagenverdeckung (Stoff unter Stoff) hängt am selben Ereignis.
* Weichgewebe und Einzug teilen sich das Material über `Shaderpatch` —
  ein nacktes `onBeforeCompile` löschte den jeweils anderen Eingriff.
"""

from django.test import SimpleTestCase

from ..jsmodul import Jsmodul


class HautverdeckungVerdrahtungTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.modul = HautverdeckungVerdrahtungTest._lies('gemeinsam', 'hautverdeckung.js')
        self.figurhaut = HautverdeckungVerdrahtungTest._lies('gemeinsam', 'figurhaut.js')

    def test_wird_geladen_und_hoert_auf_das_stueckereignis(self):
        self.assertIn(
            "import '../gemeinsam/hautverdeckung.js';", HautverdeckungVerdrahtungTest._lies('charakter', 'boot.js')
        )
        self.assertIn('Stueckereignis.hoeren(', self.modul)
        self.assertIn('Hautverdeckung.einhaengen();', self.modul)

    def test_die_teilnetz_auswahl_meldet_das_entfernen(self):
        quelle = HautverdeckungVerdrahtungTest._lies('charakter', 'teilnetz_auswahl.js')
        self.assertIn("import { Stueckereignis } from '../gemeinsam/stueckereignis.js';", quelle)
        self.assertIn('Stueckereignis.melden(inst, target.key.slice(3), false);', quelle)

    def test_der_volle_index_bleibt_und_die_stoffgrenze_nimmt_ihn(self):
        # `merken`/`indexSetzen`/`vollerIndex` kommen seit 17.09.2026 aus `Figurhaut`.
        self.assertIn('export class Hautverdeckung extends Figurhaut {', self.modul)
        self.assertNotIn('static merken(', self.modul)
        self.assertIn('geo.userData.indexVoll = {', self.figurhaut)
        self.assertIn('index: geo.index.array.slice()', self.figurhaut)
        # Jede Maske rechnet vom vollen Index, nie vom gekuerzten (seit 09.10.2026 in `Hautrechnung`, auch im Worker).
        self.assertIn('Hautrechnung.rechnen(pos, voll.index, stoffe)', self.modul)
        self.assertIn('geo.userData.indexVoll.index', self.modul)       # `anwendenAsync` schickt den vollen Index
        rechnung = HautverdeckungVerdrahtungTest._lies('gemeinsam', 'hautrechnung.js')
        self.assertIn('Hautmaske.verdeckt(pos, index, stoffe, { ersatz, hoehe, rand, normalen })', rechnung)
        # Seit dem 13.09.2026 mit `weg` aus dem Einzug: hinter der Maskengrenze
        # bleibt ein Band versenkter Haut (`Saumband`). Die Ersatzstück-Schritte ergänzen `weg` (09.10.2026).
        self.assertIn('const weg = einzug.weg || new Uint8Array(ersatz.length);', self.modul)
        self.assertIn('Hautmaske.indexOhne(voll.index, voll.gruppen, weg,', self.modul)
        aufbau = HautverdeckungVerdrahtungTest._lies('charakter', 'weichgewebeaufbau.js')
        self.assertIn('geo.userData?.indexVoll?.index ||', aufbau)

    def test_ohne_stuecke_kommt_der_volle_index_zurueck(self):
        # Ohne Stoff, aber mit dem Loch eines verschweißten Stücks (`Stueckloch`, 09.10.2026): nur dieses Loch; sonst alles zurück.
        self.assertIn('if (!stoffe.length) return loecher ? Hautloch.nurLoecher(inst, geo, voll, loecher) : Hautverdeckung.aufheben(inst);',
                      self.modul)
        self.assertIn('Hautverdeckung.indexSetzen(geo, voll.index, voll.gruppen);', self.modul)

    def test_einzug_und_lagenverdeckung_haengen_daran(self):
        # Seit dem 13.09.2026 mit den Stoffkanten: Randecken wandern unter die
        # Kante statt nach innen (`Saumschnitt`); gerechnet in `Hautrechnung`, geschrieben von `Hauteinzug.eintragen`.
        self.assertIn('Hauteinzug.eintragen(inst.bodyMesh, rechnung.einzug);', self.modul)
        self.assertIn(
            '{ kanten: Saumschnitt.kanten(stoffe), hautnormalen: normalen }',
            HautverdeckungVerdrahtungTest._lies('gemeinsam', 'hautrechnung.js'),
        )
        self.assertIn('Hauteinzug.setzen(inst.bodyMesh, null, null);', self.modul)
        einzug = HautverdeckungVerdrahtungTest._lies('gemeinsam', 'hauteinzug.js')
        self.assertIn("Shaderpatch.hinterInclude(shader, 'begin_vertex', 'transformed += einzug;')", einzug)
        self.assertIn(
            "import './lagenverdeckung.js';", HautverdeckungVerdrahtungTest._lies('charakter', 'boot.js')
        )
        lagen = HautverdeckungVerdrahtungTest._lies('charakter', 'lagenverdeckung.js')
        self.assertIn('Stueckereignis.hoeren(', lagen)
        self.assertIn('Lagenmaske.verdeckt(koerper, stoffe)', lagen)

    def test_weichgewebe_und_einzug_teilen_sich_das_material(self):
        aufbau = HautverdeckungVerdrahtungTest._lies('charakter', 'weichgewebeaufbau.js')
        self.assertIn('Shaderpatch.klonen(alt)', aufbau)
        self.assertIn("Shaderpatch.anhaengen(mat, 'weichgewebe'", aufbau)
        self.assertNotIn('mat.onBeforeCompile =', aufbau)
        self.assertNotIn(
            'onBeforeCompile =', HautverdeckungVerdrahtungTest._lies('gemeinsam', 'hauteinzug.js')
        )

    def test_ausgezogene_kleidung_gibt_die_haut_sofort_frei(self):
        """Rainy, 10.10.2026: nach dem Ausziehen stand die nackte Haut mit Flecken und Stufen da, bis der Worker die neue Maske gerechnet hatte.
        Weniger zählende Stücke als in der gezeigten Maske → `freigeben` (voller Index, Einzug null, nur die Löcher verschweißter Stücke bleiben),
        DANN erst die Rechnung im Worker. Ein Austausch (gleiche Zahl) bleibt, wie er war.
        Sabotage: den Aufruf in `_rechnen` streichen → der zweite Teil wird rot; `_maskeAnzahl` in `anwenden` nicht setzen → der erste."""
        self.assertIn('inst._maskeAnzahl = Hautverdeckung.zaehlende(inst).length;', self.modul)
        self.assertIn('static freigeben(inst) {', self.modul)
        self.assertIn('Hautverdeckung.zaehlende(inst).length < (inst._maskeAnzahl || 0)', self.modul)
        rechnen = self.modul[self.modul.index('static _rechnen(inst) {'):]
        self.assertLess(rechnen.index('Hautverdeckung.freigeben(inst)'), rechnen.index('Hautverdeckung.anwendenAsync(inst'),
                        'erst freigeben, dann rechnen')
        freigeben = self.modul[self.modul.index('static freigeben(inst) {'):self.modul.index('static aufheben(inst) {')]
        self.assertIn('Hautloch.nurLoecher(inst, geo, voll, loecher)', freigeben)
        self.assertIn('Hautverdeckung.aufheben(inst)', freigeben)

    def test_die_gruppen_werden_neu_gesetzt(self):
        """`addGroup` zaehlt Indexeintraege; ohne `clearGroups` laegen alte
        und neue Gruppen uebereinander."""
        self.assertIn('geo.clearGroups();', self.figurhaut)
        self.assertIn('geo.addGroup(g.start, g.count, g.materialIndex)', self.figurhaut)

    @staticmethod
    def _lies(*teile):
        return Jsmodul(*teile).pfad.read_text(encoding='utf-8')

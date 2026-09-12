# -*- coding: utf-8 -*-
u"""`Hautverdeckung`: die Haut unter der Kleidung wird nicht gezeichnet —
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
        self.modul = HautverdeckungVerdrahtungTest._lies('scene', 'hautverdeckung.js')

    def test_wird_geladen_und_hoert_auf_das_stueckereignis(self):
        self.assertIn("import './hautverdeckung.js';", HautverdeckungVerdrahtungTest._lies('scene', 'boot.js'))
        self.assertIn('Stueckereignis.hoeren(', self.modul)
        self.assertIn('Hautverdeckung.einhaengen();', self.modul)

    def test_die_teilnetz_auswahl_meldet_das_entfernen(self):
        quelle = HautverdeckungVerdrahtungTest._lies('scene', 'teilnetz_auswahl.js')
        self.assertIn("import { Stueckereignis } from './garmentcode_stueckereignis.js';", quelle)
        self.assertIn("Stueckereignis.melden(inst, target.key.slice(3), false);", quelle)

    def test_der_volle_index_bleibt_und_die_stoffgrenze_nimmt_ihn(self):
        self.assertIn('geo.userData.indexVoll = {', self.modul)
        self.assertIn('index: geo.index.array.slice()', self.modul)
        # Jede Maske rechnet vom vollen Index, nie vom gekuerzten.
        self.assertIn('Hautmaske.verdeckt(geo.attributes.position.array, voll.index, stoffe)', self.modul)
        self.assertIn('Hautmaske.indexOhne(voll.index, voll.gruppen, maske)', self.modul)
        aufbau = HautverdeckungVerdrahtungTest._lies('scene', 'weichgewebeaufbau.js')
        self.assertIn('geo.userData?.indexVoll?.index ||', aufbau)

    def test_ohne_stuecke_kommt_der_volle_index_zurueck(self):
        self.assertIn('if (!stoffe.length) return Hautverdeckung.aufheben(inst);', self.modul)
        self.assertIn('Hautverdeckung.indexSetzen(geo, voll.index, voll.gruppen);', self.modul)

    def test_einzug_und_lagenverdeckung_haengen_daran(self):
        self.assertIn('Hauteinzug.setzen(inst.bodyMesh, maske, voll.index);', self.modul)
        self.assertIn('Hauteinzug.setzen(inst.bodyMesh, null, null);', self.modul)
        einzug = HautverdeckungVerdrahtungTest._lies('gemeinsam', 'hauteinzug.js')
        self.assertIn("Shaderpatch.hinterInclude(shader, 'begin_vertex', 'transformed += einzug;')", einzug)
        self.assertIn("import './lagenverdeckung.js';", HautverdeckungVerdrahtungTest._lies('scene', 'boot.js'))
        lagen = HautverdeckungVerdrahtungTest._lies('scene', 'lagenverdeckung.js')
        self.assertIn('Stueckereignis.hoeren(', lagen)
        self.assertIn('Lagenmaske.verdeckt(koerper, stoffe)', lagen)

    def test_weichgewebe_und_einzug_teilen_sich_das_material(self):
        aufbau = HautverdeckungVerdrahtungTest._lies('scene', 'weichgewebeaufbau.js')
        self.assertIn('Shaderpatch.klonen(alt)', aufbau)
        self.assertIn("Shaderpatch.anhaengen(mat, 'weichgewebe'", aufbau)
        self.assertNotIn('mat.onBeforeCompile =', aufbau)
        self.assertNotIn('onBeforeCompile =', HautverdeckungVerdrahtungTest._lies('gemeinsam', 'hauteinzug.js'))

    def test_die_gruppen_werden_neu_gesetzt(self):
        u"""`addGroup` zaehlt Indexeintraege; ohne `clearGroups` laegen alte
        und neue Gruppen uebereinander."""
        self.assertIn('geo.clearGroups();', self.modul)
        self.assertIn('geo.addGroup(g.start, g.count, g.materialIndex)', self.modul)

    @staticmethod
    def _lies(*teile):
        return Jsmodul(*teile).pfad.read_text(encoding='utf-8')

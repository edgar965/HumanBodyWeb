# -*- coding: utf-8 -*-
u"""`Anfangshaltung`: das Skelett in die Haltung von Bild 0 bringen.

WARUM (31.08.2026, Befund `jsfunktionen`)
=========================================
`placeBvhSkeleton()` war mit 92 Zeilen über die Faustregel gewachsen und tat
drei Dinge: Haltung setzen, Höhe messen, Anzeige bauen. Der erste Teil ist
jetzt die Klasse `Anfangshaltung`.

Der Bandai-Sonderfall steht in `test_js_anfangshaltung_bandai.py` — er ist
ein Thema für sich und hätte diese Datei über die Faustregel gehoben.

FEHLT `node`, ist das ein FEHLER — node ist Werkzeug dieses Projekts,
kein Zufall der Umgebung (siehe `Jsmodul.laufen`).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul
from ._skelettattrappen import FERTIG, SKELETT

MODUL = Jsmodul('anfangshaltung.js')

#: Was ein Skript ausgibt, wenn jeder Vergleich darin gehalten hat.
GESCHAFFT = {'fertig': True}


class DieHaltungAusBildNull(SimpleTestCase):
    u"""Gegeben: Eine Animation mit Dreh- und Ortsspuren."""

    def test_bild_null_landet_auf_den_knochen(self):
        self.assertEqual(MODUL.laufen(SKELETT + """
const { Anfangshaltung } = await import(MODUL);
const wurzel = new Knochen('joint_Root');
const arm = new Knochen('Arm', wurzel);
const klip = { tracks: [
    spur('Arm.quaternion', [0.1, 0.2, 0.3, 0.4, 9, 9, 9, 9]),
    spur('Arm.position', [1, 2, 3, 7, 7, 7]),
] };
new Anfangshaltung([wurzel, arm], klip).anwenden('cmu', wurzel);

// Die ERSTEN vier bzw. drei Werte — nicht die spaeteren Bilder.
pruefe('Drehung', [arm.quaternion.x, arm.quaternion.y,
                   arm.quaternion.z, arm.quaternion.w], [0.1, 0.2, 0.3, 0.4]);
pruefe('Ort', arm.position.als(), [1, 2, 3]);
""" + FERTIG), GESCHAFFT)

    def test_eine_zu_kurze_spur_wird_uebergangen(self):
        u"""Weniger als vier Werte sind keine Drehung — der Knochen bleibt."""
        self.assertEqual(MODUL.laufen(SKELETT + """
const { Anfangshaltung } = await import(MODUL);
const arm = new Knochen('Arm');
new Anfangshaltung([arm], { tracks: [spur('Arm.quaternion', [1, 2])] })
    .anwenden('cmu', arm);
pruefe('unveraendert', [arm.quaternion.x, arm.quaternion.w], [0, 0]);
""" + FERTIG), GESCHAFFT)

    def test_ein_unbekannter_knochen_stoert_nicht(self):
        u"""Eine Spur ohne Knochen darf den Lauf nicht abbrechen."""
        self.assertEqual(MODUL.laufen(SKELETT + """
const { Anfangshaltung } = await import(MODUL);
const arm = new Knochen('Arm');
const klip = { tracks: [spur('GibtsNicht.position', [5, 5, 5]),
                        spur('Arm.position', [1, 2, 3])] };
new Anfangshaltung([arm], klip).anwenden('cmu', arm);
pruefe('Arm gesetzt', arm.position.als(), [1, 2, 3]);
""" + FERTIG), GESCHAFFT)

    def test_ein_spurname_ohne_punkt_faellt_weg(self):
        self.assertEqual(MODUL.laufen(SKELETT + """
const { Anfangshaltung } = await import(MODUL);
const zerlegt = Anfangshaltung.spurenJeKnochen([spur('ohnePunkt', [1])]);
pruefe('leer', Object.keys(zerlegt), []);
""" + FERTIG), GESCHAFFT)


class OhneAnimation(SimpleTestCase):
    u"""Gegeben: Es gibt keinen Klip oder er hat keine Spuren."""

    def test_es_passiert_nichts(self):
        self.assertEqual(MODUL.laufen(SKELETT + """
const { Anfangshaltung } = await import(MODUL);
const arm = new Knochen('Arm');
pruefe('ohne Klip', new Anfangshaltung([arm], null).anwenden('cmu', arm),
       false);
pruefe('leerer Klip',
       new Anfangshaltung([arm], { tracks: [] }).anwenden('cmu', arm), false);
pruefe('Knochen unberuehrt', arm.position.als(), [0, 0, 0]);
""" + FERTIG), GESCHAFFT)

# -*- coding: utf-8 -*-
u"""`Anfangshaltung`, Bandai: die Wurzelbewegung sitzt an den Hüften.

DIE STELLE, DIE WEHTUT
======================
Bandai führt die Wurzelbewegung an `Hips` statt an `joint_Root`. Ohne das
Umlegen bewegt sich die Figur DOPPELT — einmal über die Wurzel, einmal über
die Hüfte.

Umgelegt wird dabei nicht nur am Knochen, sondern in den SPURWERTEN. Sonst
gilt die Korrektur nur fürs erste Bild, und die Animation läuft auseinander:
Die Figur steht richtig da und wandert erst im Lauf davon — im Browser die
unangenehmste Sorte Fehler, weil der erste Blick sagt „stimmt".

Deshalb hält dieser Test die Spurwerte fest, nicht nur die Knochenlage.

FEHLT `node`, ist das ein FEHLER — node ist Werkzeug dieses Projekts,
kein Zufall der Umgebung (siehe `Jsmodul.laufen`).
"""
from django.test import SimpleTestCase

from ..jsmodul import Jsmodul
from ._skelettattrappen import BANDAI_AUFBAU, FERTIG, SKELETT

MODUL = Jsmodul('anfangshaltung.js')

GESCHAFFT = {'fertig': True}


class DerBandaiSonderfall(SimpleTestCase):
    u"""Gegeben: Wurzel und Hüften, beide mit Ortsspur."""

    def test_die_bewegung_zieht_in_die_wurzelspur_um(self):
        self.assertEqual(MODUL.laufen(SKELETT + BANDAI_AUFBAU + """
const { Anfangshaltung } = await import(MODUL);
new Anfangshaltung([wurzel, hueften], klip).anwenden('bandai', wurzel);
pruefe('Wurzelspur hat die Hueftwerte', wurzelSpur.values, [1, 2, 3, 4, 5, 6]);
pruefe('Hueftspur steht auf null', hueftSpur.values, [0, 0, 0, 0, 0, 0]);
pruefe('Wurzelknochen uebernimmt', wurzel.position.als(), [1, 2, 3]);
pruefe('Hueftknochen auf null', hueften.position.als(), [0, 0, 0]);
""" + FERTIG), GESCHAFFT)

    def test_bei_einem_anderen_format_bleibt_alles(self):
        u"""Die Gegenprobe: Nur Bandai legt zusammen."""
        self.assertEqual(MODUL.laufen(SKELETT + BANDAI_AUFBAU + """
const { Anfangshaltung } = await import(MODUL);
new Anfangshaltung([wurzel, hueften], klip).anwenden('cmu', wurzel);
pruefe('Wurzelspur unveraendert', wurzelSpur.values, [0, 0, 0, 0, 0, 0]);
pruefe('Hueftspur unveraendert', hueftSpur.values, [1, 2, 3, 4, 5, 6]);
pruefe('Hueftknochen behaelt Bild 0', hueften.position.als(), [1, 2, 3]);
""" + FERTIG), GESCHAFFT)

    def test_ohne_direkte_elternschaft_passiert_nichts(self):
        u"""Hängt `Hips` nicht unmittelbar an der Wurzel, ist es ein anderes
        Rig — dann wäre das Umlegen falsch."""
        self.assertEqual(MODUL.laufen(SKELETT + """
const { Anfangshaltung } = await import(MODUL);
const wurzel = new Knochen('joint_Root');
const zwischen = new Knochen('Zwischen', wurzel);
const hueften = new Knochen('Hips', zwischen);
const hueftSpur = spur('Hips.position', [1, 2, 3]);
const klip = { tracks: [spur('joint_Root.position', [0, 0, 0]), hueftSpur] };
new Anfangshaltung([wurzel, zwischen, hueften], klip)
    .anwenden('bandai', wurzel);
pruefe('Hueftspur unveraendert', hueftSpur.values, [1, 2, 3]);
pruefe('Wurzelknochen unberuehrt', wurzel.position.als(), [0, 0, 0]);
""" + FERTIG), GESCHAFFT)

    def test_ungleich_lange_spuren_brechen_nicht(self):
        u"""Kopiert wird nur, so weit BEIDE reichen — sonst schriebe die
        Schleife über das Ende der Wurzelspur hinaus."""
        self.assertEqual(MODUL.laufen(SKELETT + """
const { Anfangshaltung } = await import(MODUL);
const wurzel = new Knochen('joint_Root');
const hueften = new Knochen('Hips', wurzel);
const wurzelSpur = spur('joint_Root.position', [0, 0, 0]);
const hueftSpur = spur('Hips.position', [1, 2, 3, 4, 5, 6]);
new Anfangshaltung([wurzel, hueften], { tracks: [wurzelSpur, hueftSpur] })
    .anwenden('bandai', wurzel);
pruefe('Wurzelspur bleibt kurz', wurzelSpur.values, [1, 2, 3]);
pruefe('Hueftspur ganz auf null', hueftSpur.values, [0, 0, 0, 0, 0, 0]);
""" + FERTIG), GESCHAFFT)

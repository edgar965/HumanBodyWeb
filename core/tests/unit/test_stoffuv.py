# -*- coding: utf-8 -*-
u"""`Stoffuv`: die UV-Koordinaten des drapierten Stoffs und ihr Maßstab.

WARUM (Edgar, 10.09.2026: „Meine Kleider sehen mir noch zu schlecht aus"):
Ohne UV kann der Browser keine Gewebestruktur auf ein Kleidungsstück legen —
und das Netz führte keine, obwohl die `*_sim.obj` daneben sie hat.

GEPRÜFT WIRD AN KUNSTNETZEN, nicht an den Dateien unter `ausgabe/`: Die
entstehen bei jedem Bau neu, und ein Test, der an ihnen hängt, wird rot,
sobald jemand ein Stück baut.

Die drei Stellen, an denen es still schiefgehen kann:

1. **Ein UV je Punkt statt je Ecke.** Ein OBJ nennt je Flächenecke ein
   eigenes; Three.js kennt nur eines je Punkt. Wird das übersehen, ist die
   Liste länger als die Punktliste — und Three.js legt sie trotzdem an,
   nur verrutscht.
2. **Eine Liste vom falschen Netz.** Passt die Länge nicht zur Punktzahl,
   muss gar nichts geliefert werden. Ein verdrehtes Gewebe sähe aus wie ein
   Simulationsfehler.
3. **Der Maßstab.** Er sagt, wie viele Meter Stoff eine UV-Einheit sind. Die
   OBJ steht in Zentimetern; wer die Umrechnung vergisst, bekommt einen
   Faktor 100 und damit eine Kachel, die über das ganze Stück läuft.
"""
import os

from django.test import SimpleTestCase

from GarmentCode.stoffuv import Stoffuv
from ._pruefablage import Pruefablage


def _schreiben(inhalt, ordner):
    pfad = os.path.join(ordner, 'probe_sim.obj')
    with open(pfad, 'w', encoding='utf-8') as datei:
        datei.write(inhalt)
    return pfad


#: Ein Quadrat aus zwei Dreiecken: 10 cm Kante, UV von 0 bis 1.
#: Damit ist der Maßstab bekannt — 10 cm je UV-Einheit, also 0,1 m.
QUADRAT = u"""v 0 0 0
v 10 0 0
v 10 10 0
v 0 10 0
vt 0 0
vt 1 0
vt 1 1
vt 0 1
f 1/1 2/2 3/3
f 1/1 3/3 4/4
"""

#: Dasselbe, aber Punkt 3 trägt in der zweiten Fläche eine andere UV — so
#: sieht eine Naht aus, an der zwei Schnittteile aneinanderstoßen.
MIT_NAHT = u"""v 0 0 0
v 10 0 0
v 10 10 0
v 0 10 0
vt 0 0
vt 1 0
vt 1 1
vt 0 1
vt 0.5 0.5
f 1/1 2/2 3/3
f 1/1 3/5 4/4
"""

OHNE_UV = u"""v 0 0 0
v 10 0 0
v 10 10 0
f 1 2 3
"""


class DieUvKommtJePunktTest(SimpleTestCase):

    databases = set()

    def test_ein_paar_je_punkt(self):
        with Pruefablage.ordner() as ordner:
            uv = Stoffuv.aus_obj(_schreiben(QUADRAT, ordner))
        self.assertEqual(len(uv), 4)
        self.assertEqual(uv.als_liste()[1], [1.0, 0.0])
        self.assertEqual(uv.mehrfach, 0)

    def test_an_einer_naht_gewinnt_die_erste_angabe(self):
        u"""Und die Stelle wird gezählt — sonst bliebe sie unbemerkt."""
        with Pruefablage.ordner() as ordner:
            uv = Stoffuv.aus_obj(_schreiben(MIT_NAHT, ordner))
        self.assertEqual(len(uv), 4)
        self.assertEqual(uv.als_liste()[2], [1.0, 1.0])
        self.assertEqual(uv.mehrfach, 1)

    def test_ohne_uv_gibt_es_nichts(self):
        with Pruefablage.ordner() as ordner:
            self.assertIsNone(Stoffuv.aus_obj(_schreiben(OHNE_UV, ordner)))

    def test_eine_fehlende_datei_wirft_nicht(self):
        self.assertIsNone(Stoffuv.aus_obj(r'A:\gibtesnicht\probe_sim.obj'))
        self.assertIsNone(Stoffuv.aus_obj(''))


class DieListeMussZumNetzPassenTest(SimpleTestCase):
    u"""Die Gegenprobe zu „es kommt schon irgendwas": Eine UV-Liste vom
    falschen Netz legt das Gewebe verdreht auf den Stoff, ohne Fehler."""

    databases = set()

    def test_falsche_punktzahl_liefert_nichts(self):
        with Pruefablage.ordner() as ordner:
            pfad = _schreiben(QUADRAT, ordner)
            self.assertIsNone(Stoffuv.aus_obj(pfad, punktzahl=99))
            self.assertIsNotNone(Stoffuv.aus_obj(pfad, punktzahl=4))


class DerMassstabIstInMeternTest(SimpleTestCase):

    databases = set()

    def test_zehn_zentimeter_je_uv_einheit(self):
        u"""Die Kante ist 10 Einheiten lang, das OBJ steht in Zentimetern —
        also 0,1 m je UV-Einheit. Ohne die Umrechnung stünde dort 10."""
        with Pruefablage.ordner() as ordner:
            uv = Stoffuv.aus_obj(_schreiben(QUADRAT, ordner))
        self.assertAlmostEqual(uv.meter_je_uv, 0.1, places=6)

    def test_ein_groesseres_netz_hat_einen_groesseren_massstab(self):
        gross = QUADRAT.replace('v 10 0 0', 'v 20 0 0') \
                       .replace('v 10 10 0', 'v 20 10 0')
        with Pruefablage.ordner() as ordner:
            uv = Stoffuv.aus_obj(_schreiben(gross, ordner))
        self.assertGreater(uv.meter_je_uv, 0.1)


class DieTeilungBehaeltDenMassstabTest(SimpleTestCase):
    u"""Ein gemeinsam simuliertes Netz wird nach Stücken zerlegt; jedes Teil
    ist ein Ausschnitt DESSELBEN Schnittmusters."""

    databases = set()

    def test_ausschnitt(self):
        with Pruefablage.ordner() as ordner:
            uv = Stoffuv.aus_obj(_schreiben(QUADRAT, ordner))
        teil = uv.teil([2, 0])
        self.assertEqual(teil.als_liste(), [[1.0, 1.0], [0.0, 0.0]])
        self.assertEqual(teil.meter_je_uv, uv.meter_je_uv)

    def test_nummern_ausserhalb_des_netzes_liefern_nichts(self):
        with Pruefablage.ordner() as ordner:
            uv = Stoffuv.aus_obj(_schreiben(QUADRAT, ordner))
        self.assertIsNone(uv.teil([0, 99]))


class DieRigDateiFuehrtDieUvTest(SimpleTestCase):
    u"""`Anziehen.ablegen` schreibt sie — sonst käme sie nie im Browser an."""

    databases = set()

    def test_uv_und_massstab_stehen_in_der_datei(self):
        import json
        from GarmentCode.anziehen import Anziehen
        with Pruefablage.ordner() as ordner:
            uv = Stoffuv.aus_obj(_schreiben(QUADRAT, ordner))
            ziel = os.path.join(ordner, 'probe_sim_rig.json')
            Anziehen.ablegen(ziel, [[0, 0, 0]] * 4, [[0, 1, 2]], None, [],
                             uv=uv)
            with open(ziel, encoding='utf-8') as datei:
                daten = json.load(datei)
        self.assertEqual(len(daten['uv']), 4)
        self.assertAlmostEqual(daten['uv_meter'], 0.1, places=6)

    def test_ohne_uv_bleiben_die_felder_weg(self):
        u"""Ein älterer Ergebnisordner hat keine — dann darf auch kein
        leeres Feld dastehen, an dem der Browser eine Karte aufhängt."""
        import json
        from GarmentCode.anziehen import Anziehen
        with Pruefablage.ordner() as ordner:
            ziel = os.path.join(ordner, 'probe_sim_rig.json')
            Anziehen.ablegen(ziel, [[0, 0, 0]] * 3, [[0, 1, 2]], None, [])
            with open(ziel, encoding='utf-8') as datei:
                daten = json.load(datei)
        self.assertNotIn('uv', daten)
        self.assertNotIn('uv_meter', daten)

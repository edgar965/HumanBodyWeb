# -*- coding: utf-8 -*-
u"""Mhskelett — das Rig, das MakeHuman selbst mitbringt.

WARUM (Edgar, 07.09.2026: „MakeHuman weiss ich nicht, welches Skeleton das
mitbringt"): Es bringt genau eines mit, `data/rigs/default.mhskel` mit 163
Knochen. Bis dahin war die MakeHuman-Figur ein reines Netz, und der
Rig-Schalter blieb fuer sie wirkungslos.

DER KERN: DIE GELENKE HAENGEN AM NETZ
=====================================
`default.mhskel` speichert keine Koordinaten, sondern je Gelenk eine Liste
von Vertexnummern; die Position ist deren Mittelwert
(`MakeHuman/makehuman/shared/skeleton.py`, `getJointPosition`). Deshalb
folgt das Skelett den 269 Modellierreglern von selbst — und genau das wird
hier geprueft, nicht nur, dass ueberhaupt Knochen herauskommen. Ein
Skelett, das bei jeder Figur gleich bleibt, saehe im Standardfall richtig
aus und waere bei einem Kind komplett falsch.

Die Reihenfolge (Eltern vor Kindern) ist der zweite Punkt: Die Datei ist
alphabetisch sortiert (`breast.L` vor `spine02`), und der Browser haengt
jeden Knochen an seinen Elternteil. Wer die Datei-Reihenfolge uebernimmt,
baut eine Hierarchie mit Loechern.
"""
import unittest


from MakeHuman.basisnetz import Mhbasisnetz
from MakeHuman.formung import Mhformung
from MakeHuman.skelett import Mhskelett


class MhskelettTest(unittest.TestCase):

    databases = set()

    @classmethod
    def setUpClass(cls):
        if not Mhskelett.vorhanden():
            raise unittest.SkipTest('default.mhskel fehlt (%s)' % Mhskelett.pfad())
        if not Mhbasisnetz.vorhanden():
            raise unittest.SkipTest('MakeHuman/base.obj fehlt')

    # ------------------------------------------------------------- Bestand

    def test_alle_knochen_der_datei_kommen_an(self):
        u"""163 Knochen — keiner faellt an fehlenden Gelenken heraus.

        Gezaehlt werden die Knochen der DATEI, nicht die Zeilen des
        Bauplans: Seit dem 07.09.2026 haengt an jedem Blatt ein Endknochen
        (`Gelenkskelett`, damit der `SkeletonHelper` den letzten Abschnitt
        zeichnet). Eine feste Gesamtzahl waere ab dann eine Zahl ueber die
        Blattzahl des Rigs und nicht mehr ueber seine Vollstaendigkeit.
        """
        rig = Mhskelett.rig()
        gebaut = Mhskelett().bauen()
        self.assertEqual(len(rig['bones']), 163)
        echte = {k['name'] for k in gebaut['knochen'] if not k['ende']}
        self.assertEqual(echte, set(rig['bones']))

    def test_endknochen_haengen_an_blaettern(self):
        u"""Jedes Blatt bekommt genau einen — und nur ein Blatt."""
        knochen = Mhskelett().bauen()['knochen']
        eltern = {k['eltern'] for k in knochen if k['eltern']}
        enden = [k for k in knochen if k['ende']]
        self.assertTrue(enden, 'kein einziger Endknochen')
        for k in enden:
            self.assertTrue(k['name'].endswith('_ende'))
            # Der Elternteil eines Endknochens hat sonst kein Kind.
            geschwister = [a for a in knochen
                           if a['eltern'] == k['eltern'] and a is not k]
            self.assertEqual(geschwister, [], k['name'])
        self.assertIn('root', eltern)

    def test_jeder_knochen_traegt_lage_und_drehung(self):
        u"""Ohne `pos`/`quat` zeichnet der Browser zwar, animiert aber falsch."""
        for k in Mhskelett().bauen()['knochen']:
            self.assertEqual(len(k['pos']), 3, k['name'])
            self.assertEqual(len(k['quat']), 4, k['name'])

    def test_genau_eine_wurzel(self):
        knochen = Mhskelett().bauen()['knochen']
        ohne = [k['name'] for k in knochen if not k['eltern']]
        self.assertEqual(ohne, ['root'])

    def test_eltern_stehen_vor_ihren_kindern(self):
        u"""Sonst haengt der Browser Knochen an noch nicht gebaute Eltern."""
        gesehen = set()
        for k in Mhskelett().bauen()['knochen']:
            if k['eltern']:
                self.assertIn(k['eltern'], gesehen,
                              '%s kommt vor seinem Elternteil %s'
                              % (k['name'], k['eltern']))
            gesehen.add(k['name'])

    def test_jeder_elternteil_ist_ein_knochen(self):
        knochen = Mhskelett().bauen()['knochen']
        namen = {k['name'] for k in knochen}
        for k in knochen:
            if k['eltern']:
                self.assertIn(k['eltern'], namen)

    # ------------------------------------------------------------ Lage

    def test_knochen_liegen_im_koerper(self):
        u"""Fuesse auf 0, Scheitel bei der Netzhoehe — nicht im Boden."""
        from MakeHuman.koerpernetz import Mhkoerpernetz
        netz = Mhkoerpernetz(('koerper',)).bauen()
        knochen = Mhskelett().bauen()['knochen']
        hoehen = [k['kopf'][1] for k in knochen]
        self.assertGreater(min(hoehen), -0.02)
        # Das oberste Gelenk sitzt im Scheitel — ein paar Millimeter
        # darueber ist der Mittelpunkt seines Gelenkwuerfels.
        self.assertLess(max(hoehen), netz['hoehe'] + 0.02)
        self.assertGreater(max(hoehen), netz['hoehe'] * 0.9)

    # ------------------------------------------------- folgt den Reglern

    def test_skelett_folgt_dem_groessenregler(self):
        u"""Der eigentliche Beleg: kleine Figur, kleines Skelett.

        Gemessen am 07.09.2026: 129,2 cm bei `height` 0 und 238,2 cm bei
        `height` 1 — dieselben Werte, die das NETZ annimmt.
        """
        klein = self._scheitel({'height': 0.0})
        gross = self._scheitel({'height': 1.0})
        self.assertLess(klein, 1.35)
        self.assertGreater(gross, 2.30)
        self.assertGreater(gross - klein, 0.9)

    def test_skelett_folgt_dem_alter(self):
        u"""Ein Kind ist kleiner — auch seine Knochen."""
        kind = self._scheitel({'age': 0.15})
        erwachsen = self._scheitel({})
        self.assertLess(kind, erwachsen - 0.3)

    def test_gegenprobe_ohne_formung_bleibt_es_gleich(self):
        u"""Ohne Regler darf sich NICHTS bewegen.

        Ohne diesen Fall koennte `_gelenkstellen` die Formung schlicht
        ignorieren und alle Faelle oben blieben trotzdem gruen — nein:
        sie wuerden rot. Aber der umgekehrte Fehler (jedes Mal etwas
        anderes) faellt nur hier auf.
        """
        self.assertAlmostEqual(self._scheitel({}), self._scheitel({}), places=9)

    def _scheitel(self, makro):
        formung = Mhformung.aus_abfrage(makro, None) if makro else None
        knochen = Mhskelett(formung).bauen()['knochen']
        return max(k['kopf'][1] for k in knochen)

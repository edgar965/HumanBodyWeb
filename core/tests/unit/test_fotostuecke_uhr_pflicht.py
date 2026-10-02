# -*- coding: utf-8 -*-
u"""Der autonome Lauf vom 01.10.2026 abends — Kunstdaten, keine echten Netze, keine Grafikkarte.

1. Messprüfung: vorne + hinten begrenzen die Tiefe nicht (`tiefe_gesehen` False), mit Seite schon.
2. Sichtkörper: der waagerechte Bezug ist der FLÄCHENschwerpunkt — dichte Punkte auf einer Seite verschieben ihn nicht.
3. Rundenauswahl: eine belegte Garderobe (`eigen_foto_`, `eigen_uhr_`) wird übernommen, auch bei schlechterer Note;
   eine Probe mit Pflichtzeile endet als „besser", nicht verworfen.
4. Kleiderwahl: Socken, Uhr und Fotostücke sind „fest" (keine Formregeln); `soll` nimmt Fotostücke statt Bibliothek
   und hängt die erkannte Uhr an; ohne Fotostücke die Bibliothek mit Socken, wenn der Fuß keine Haut zeigt.
5. Uhrerkennung: ein dunkler Ring am Unterarm eines Kunstbilds wird gefunden, ein nackter Arm nicht.
6. Fotostücke: der Höhenkern schneidet einen abgesetzten Klumpen und dünne Reste weg.
7. Fotostücke: eine beim Zurückrechnen gezerrte Fläche fällt heraus, eine umgeklappte (Seite gegen die Haut
   gewechselt) ebenso; eine unveränderte bleibt.
8. Körperoptionen: „übernehmen" ohne Kennung eines Auftrags wird „rechnen" — ein neuer Auftrag scheiterte sonst.

Sabotage: `Messpruefung.TIEFE_MIN = 0` → Fall 1 rot; `Sichtkoerper._flaechenmitte` durch den Punktmittelwert ersetzen
→ Fall 2 rot; `Rundenauswahl.PFLICHT = ()` → Fall 3 rot; `Uhrerkennung.ANTEIL = 1.0` → Fall 5 rot.
"""
import numpy as np
from django.test import SimpleTestCase
from iterationen2d3d.kleiderwahl import Kleiderwahl
from iterationen2d3d.messpruefung import Messpruefung
from iterationen2d3d.rundenauswahl import Rundenauswahl
from iterationen2d3d.sichtkoerper import Sichtkoerper

from core.dienste.fotostuecke import Fotostuecke
from core.dienste.uhrerkennung import Uhrerkennung


class AutonomerLaufTest(SimpleTestCase):
    databases = set()

    def test_1_tiefe_nur_mit_seitenansicht(self):
        self.assertFalse(Messpruefung.tiefe_gesehen([0.0, 180.0]))
        self.assertFalse(Messpruefung.tiefe_gesehen([0.0]))
        self.assertTrue(Messpruefung.tiefe_gesehen([0.0, 180.0, -90.0]))
        self.assertTrue(Messpruefung.tiefe_gesehen([0.0, 45.0]))

    def test_2_flaechenmitte_statt_punktmittel(self):
        # Ein Rechteck x ∈ [-0.1, 0.1], rechts dicht, links dünn besetzt — der Punktmittelwert liegt rechts der Mitte.
        y = np.linspace(0.0, 1.0, 101)
        # Punkte in den Pixelmitten (Maßstab 100 px/m): links einer je Pixel, rechts sechs
        links = np.array([[x, yy, 0.0] for x in np.linspace(-0.0995, -0.0005, 10) for yy in y])
        rechts = np.array([[x, yy, 0.0] for x in np.linspace(0.0005, 0.0995, 60) for yy in y])
        band = np.concatenate([links, rechts])
        self.assertGreater(float(band[:, 0].mean()), 0.03)
        mitte = Sichtkoerper._flaechenmitte(band, np.array([1.0, 0.0, 0.0]), 100.0)
        self.assertLess(abs(mitte), 0.011)

    def test_3_pflicht_uebernimmt_belegte_garderobe(self):
        a = Rundenauswahl()
        a.nach_runde(1, 0.50, ['m.haltung(20)'])
        zeile = "m.kleid_nur('eigen_foto_x_oberteil', 'eigen_uhr_l')"
        aktion, weiter = a.nach_runde(2, 0.60, [zeile])
        self.assertEqual((aktion, weiter['runde']), ('besser', 2))
        b = Rundenauswahl()
        b.nach_runde(1, 0.50, [])
        b.probe = {'seit': 2, 'runden': 2, 'zeilen': [zeile], 'letzte': {'runde': 3, 'gesamt': 0.6}}
        aktion, weiter = b.nach_runde(4, 0.55, [])
        self.assertEqual((aktion, weiter['runde']), ('besser', 4))
        c = Rundenauswahl()
        c.nach_runde(1, 0.50, [])
        aktion, _w = c.nach_runde(2, 0.60, ["m.kleid_nur('g9_base_shirt')"])
        self.assertEqual(aktion, 'probe')
        # Farbschritt: nicht schlechter genügt (unter der Toleranz besser), schlechter wird verworfen.
        d = Rundenauswahl()
        d.nach_runde(1, 0.4378, [])
        self.assertEqual(d.nach_runde(2, 0.4363, ["m.haar_farbe('#847575')"])[0], 'besser')
        self.assertEqual(d.nach_runde(3, 0.4400, ["m.haar_farbe('#999999')"])[0], 'verworfen')

    def test_4_kleiderwahl_fest_und_soll(self):
        for sorte in ('eigen_uhr_l', 'gc_crudelowsocks', 'eigen_foto_01123809_oberteil'):
            self.assertTrue(Kleiderwahl.fest(sorte), sorte)
        self.assertFalse(Kleiderwahl.fest('g9_base_shirt'))
        foto = {'oberteil': 'eigen_foto_k_oberteil', 'hose': 'eigen_foto_k_hose', 'socken': 'eigen_foto_k_socken'}
        self.assertEqual(Kleiderwahl.soll({}, {'uhr': ['l']}, foto),
                         ['eigen_foto_k_oberteil', 'eigen_foto_k_hose', 'eigen_foto_k_socken', 'eigen_uhr_l'])
        haut, stoff = (0.6, 0.4, 0.3), (0.2, 0.2, 0.25)
        baender = {'rumpf': stoff, 'oberschenkel': haut, 'unterschenkel': haut, 'fuss': stoff}
        self.assertEqual(Kleiderwahl.soll(baender), ['g9_base_shirt', 'g9_base_shorts', 'gc_crudelowsocks'])
        self.assertEqual(Kleiderwahl.fehlende(baender, ['g9_base_shirt', 'g9_base_shorts']), ['gc_crudelowsocks'])

    def test_5_uhr_am_unterarm(self):
        bild = np.full((400, 200, 3), 0.95)
        bild[:, 80:120] = (0.75, 0.55, 0.45)                     # Unterarm senkrecht, Haut
        hand, ellbogen = (100.0, 300.0), (100.0, 100.0)
        pose = [[0.0, 0.0, 1.0]] * 33
        pose[15] = [hand[0] / 200, hand[1] / 400, 1.0]
        pose[13] = [ellbogen[0] / 200, ellbogen[1] / 400, 1.0]
        erkennung = Uhrerkennung(None)
        self.assertFalse(erkennung.arm(bild, pose, 'l')[1])
        bild[285:298, 80:120] = (0.08, 0.08, 0.09)               # schwarzes Band kurz über dem Handgelenk
        self.assertTrue(erkennung.arm(bild, pose, 'l')[1])

    def test_6_hoehenkern(self):
        # zusammenhängende 2-cm-Bänder (`KERN_BAND`), darunter ein abgesetzter Klumpen und dünne Reste
        hoehe = np.concatenate([np.full(500, 0.75), np.full(500, 0.77), np.full(400, 0.79), np.full(80, 0.22),
                                np.linspace(0.3, 0.6, 15)])
        wahl = np.ones(len(hoehe), dtype=bool)
        kern = Fotostuecke._kern(wahl, hoehe)
        self.assertTrue(kern[:1400].all())
        self.assertFalse(kern[1400:].any())

    def test_7_gezerrte_und_umgeklappte_flaechen(self):
        vorher = np.array([[0, 0, 0], [0.01, 0, 0], [0, 0.01, 0], [0.01, 0.01, 0]], dtype=float)
        flaechen = np.array([[0, 1, 2], [1, 3, 2]])
        nachher = vorher.copy()
        nachher[3] = [0.05, 0.05, 0]                                # die zweite Fläche wird fünffach gezogen
        np.testing.assert_array_equal(Fotostuecke._ungedehnt(vorher, nachher, flaechen), [True, False])
        haut = np.array([[0, 0, -0.01], [1, 0, -0.01], [0, 1, -0.01]], dtype=float)   # Normale +z
        dreieck = np.array([[0, 1, 2]])
        gekippt = vorher.copy()
        gekippt[:, 2] = [0, 0, 0, 0]
        gekippt[2] = [0.01, 0.0, 0.0]
        gekippt[1] = [0.0, 0.01, 0.0]                               # erste Fläche: Ecken vertauscht → Normale −z
        ergebnis = Fotostuecke._ungeklappt(vorher, gekippt, flaechen[:1], haut, haut, dreieck)
        self.assertFalse(ergebnis[0])
        self.assertTrue(Fotostuecke._ungeklappt(vorher, vorher, flaechen[:1], haut, haut, dreieck)[0])

    def test_8_uebernehmen_ohne_kennung_rechnet(self):
        from core.dienste.engine2d3dkleiderkoerperoptionen import Engine2d3dKleiderkoerperoptionen
        self.assertEqual(Engine2d3dKleiderkoerperoptionen.pruefen({})['quelle'], 'rechnen')
        mit = Engine2d3dKleiderkoerperoptionen.pruefen({'quelle': 'uebernehmen', 'auftrag': '2026.09.29.15.42.36'})
        self.assertEqual(mit['quelle'], 'uebernehmen')

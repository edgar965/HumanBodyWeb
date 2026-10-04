# -*- coding: utf-8 -*-
"""Der Schritt „Vorbereitung" von „2D3D Kleider" (03.10.2026): die Option „Körper senkrecht stellen", die Ausrichtung selbst und die Frage, ob der Schritt „Netz" die
vorbereiteten Fotos übernehmen darf.

DER ANLASS
==========
Edgar (03.10.2026): „richte den Körper doch aus, als ersten Schritt … per Option schaltbar" und „einen ersten Vorschritt mit Hintergrund entfernen und diesen Skalierungen. Dieser Schritt
ist getrennt startbar." Gemessen an seinen vier Fotos (`ProjektTemp/_wegwerf/trellis_hf/achse_messen.py`): Neigung der Körperachse +0,9°, +0,7°, −0,8°, +4,3°; nach dem Drehen höchstens 0,05°.

WAS DIESE PRÜFUNG NICHT IST
===========================
Sie läuft ohne GPU und ohne BiRefNet an Kunstfiguren (ein schräger Balken mit Kopf). Dass das Netz durch das Ausrichten besser wird, sagt sie nicht — das ist an einem Lauf zu messen.
Eine Sabotage-Gegenprobe (Drehrichtung umkehren → `test_die_neigung_ist_nach_dem_drehen_weg` muss rot werden) gehört dazu und ist NICHT gelaufen.

BDD - GEGEBEN / DANN
====================
    Ein Auftrag ohne Angabe        ... `ausrichten` ist aus, ein ungültiger Wert wird zur Vorgabe
    Ein geneigter Körper           ... wird gemessen (Vorzeichen: unten nach rechts = positiv) und zurückgedreht
    Ein senkrechter oder zu schiefer Körper ... bleibt, mit Grund im Befund
    Die Vorbereitungs-Ablage       ... gilt nur zu denselben Fotos, Optionen und Fassung; sonst rechnet der Netz-Schritt selbst
"""

import json
import os

from django.test import SimpleTestCase

from core.dienste.engine2d3dkleiderlauf import Engine2d3dKleiderlauf
from core.dienste.engine2d3dkleideroptionen import Engine2d3dKleideroptionen

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np  # noqa: E402
from mesh_ausrichtung import Ausrichtung  # noqa: E402
from mesh_vorbereitungsstand import Vorbereitungsstand  # noqa: E402
from PIL import Image  # noqa: E402


class Kunstkoerper:
    """Ein Balken (Rumpf und Beine) mit Kopf, `grad` Grad geneigt: nach unten nach rechts = positiv."""

    @staticmethod
    def bild(grad, hoehe=600, breite=400):
        steigung = np.tan(np.radians(grad))
        ys, xs = np.mgrid[0:hoehe, 0:breite]
        mitte = breite / 2 + steigung * (ys - hoehe / 2)
        maske = (np.abs(xs - mitte) < 30) & (ys > 100) & (ys < 560)
        maske |= (np.hypot(xs - (breite / 2 + steigung * (60 - hoehe / 2)), ys - 70) < 35)
        rgba = np.zeros((hoehe, breite, 4), dtype=np.uint8)
        rgba[maske] = (120, 120, 120, 255)
        return Image.fromarray(rgba, 'RGBA')


class Kunstprofil:
    """Ein Seitenfoto aus Rechtecken: Kopf, Rumpf und Hüfte sind ein 90 px dicker Balken, `grad` Grad geneigt (nach unten nach rechts = positiv); die Beine stehen senkrecht
    nach VORN versetzt, damit die Körperachse (Schwerpunkte) eine andere Neigung hat als die Mittelachse. `nach_rechts`: Blick nach rechts (Rücken links im Bild)."""

    @staticmethod
    def bild(grad, nach_rechts=True, wulst=0, hoehe=600, breite=400):
        """`wulst`: Pixel, um die der Rumpf im Schulterband (Zeilen 150–230) nach hinten versetzt ist (die Mitte dort liegt `wulst` Pixel neben der von Kopf und Hüfte)."""
        steigung = np.tan(np.radians(grad))
        ys, xs = np.mgrid[0:hoehe, 0:breite]
        hinten = 140 + steigung * (ys - 100) - wulst * ((ys >= 150) & (ys <= 230))
        maske = (xs >= hinten) & (xs < hinten + 90) & (ys > 60) & (ys < 330)     # Kopf, Schulter, Rumpf bis zum Gesäß
        maske |= (xs >= 190) & (xs < 270) & (ys >= 330) & (ys < 560)             # Beine, senkrecht, weiter vorn
        if not nach_rechts:
            maske = maske[:, ::-1]
        rgba = np.zeros((hoehe, breite, 4), dtype=np.uint8)
        rgba[maske] = (120, 120, 120, 255)
        return Image.fromarray(rgba, 'RGBA')


class DieOption(SimpleTestCase):
    databases = set()

    def test_ohne_angabe_ist_ausrichten_aus(self):
        self.assertEqual(Engine2d3dKleideroptionen.pruefen({})['vorbereitung'], {'ausrichten': 'aus'})

    def test_mitte_bleibt_und_jeder_andere_wert_wird_zur_vorgabe(self):
        """Ein Häkchen: angehakt = `mitte`; `an` (Körperachse aller Fotos) und `ruecken` (Rückenkontur) sind verworfene Fassungen, `vielleicht` kein Wert."""
        for wert in ('an', 'ruecken', 'vielleicht', True, 1):
            self.assertEqual(Engine2d3dKleideroptionen.pruefen({'vorbereitung': {'ausrichten': wert}})['vorbereitung']['ausrichten'], 'aus', wert)
        self.assertEqual(Engine2d3dKleideroptionen.pruefen({'vorbereitung': {'ausrichten': 'mitte'}})['vorbereitung']['ausrichten'], 'mitte')

    def test_die_gruppe_steht_im_katalog_als_haken(self):
        felder = Engine2d3dKleideroptionen.katalog()['vorbereitung']['optionen']
        self.assertEqual([f['schluessel'] for f in felder], ['ausrichten'])
        self.assertEqual((felder[0]['art'], felder[0]['an'], felder[0]['aus'], felder[0]['vorgabe']), ('haken', 'mitte', 'aus', 'aus'))
        self.assertFalse(felder[0]['fein'])

    def test_die_vorbereitung_ist_der_erste_schritt(self):
        self.assertEqual(Engine2d3dKleiderlauf.SCHRITTE[0], 'vorbereitung')


class DieAusrichtung(SimpleTestCase):
    databases = set()

    def test_die_neigung_wird_mit_dem_richtigen_vorzeichen_gemessen(self):
        for grad in (4.0, -3.0):
            gemessen = Ausrichtung.messen(np.asarray(Kunstkoerper.bild(grad).getchannel('A')))
            self.assertAlmostEqual(gemessen['grad'], grad, delta=0.3, msg='Neigung %s' % grad)

    def test_die_neigung_ist_nach_dem_drehen_weg(self):
        for grad in (4.0, -3.0):
            gedreht, bericht = Ausrichtung.ausrichten(Kunstkoerper.bild(grad))
            self.assertTrue(bericht['gedreht'])
            self.assertLess(abs(bericht['nachher']), 0.3, 'Neigung %s' % grad)
            self.assertEqual(gedreht.size, (400, 600))

    def test_ein_senkrechter_koerper_bleibt_wie_er_ist(self):
        bild = Kunstkoerper.bild(0.0)
        gedreht, bericht = Ausrichtung.ausrichten(bild)
        self.assertFalse(bericht['gedreht'])
        self.assertIs(gedreht, bild)

    def test_ein_zu_schiefer_koerper_wird_nicht_gedreht(self):
        _, bericht = Ausrichtung.ausrichten(Kunstkoerper.bild(20.0))
        self.assertFalse(bericht['gedreht'])
        self.assertIn('nicht gedreht', bericht['grund'])

    def test_ohne_silhouette_gibt_es_einen_grund_statt_eines_fehlers(self):
        leer = Image.new('RGBA', (100, 100), (0, 0, 0, 0))
        gedreht, bericht = Ausrichtung.ausrichten(leer)
        self.assertIs(gedreht, leer)
        self.assertIsNone(bericht['grad'])
        self.assertTrue(Ausrichtung.zeile('x.jpg', bericht))


class DieMittelachse(SimpleTestCase):
    """`modus = 'mitte'`: bei den Seitenrollen zählt die Achse durch die Mitte von Kopf, Rumpf und Hüfte, nicht die Körperachse; danach liegen alle drei auf EINER Achse."""

    databases = set()

    def test_die_mittelachse_wird_in_beiden_blickrichtungen_mit_dem_richtigen_vorzeichen_gemessen(self):
        for grad in (4.0, -3.0):
            rechts = Ausrichtung.messen_mitte(np.asarray(Kunstprofil.bild(grad, True).getchannel('A')))
            links = Ausrichtung.messen_mitte(np.asarray(Kunstprofil.bild(grad, False).getchannel('A')))
            self.assertAlmostEqual(rechts['grad'], grad, delta=0.5, msg='rechts %s' % grad)
            self.assertAlmostEqual(links['grad'], -grad, delta=0.5, msg='links %s' % grad)  # die Spiegelung kehrt das Vorzeichen um

    def test_die_koerperachse_misst_dasselbe_profil_anders(self):
        """Die Beine stehen weiter vorn: die Achse durch die Schwerpunkte neigt sich anders als die Mittelachse — genau deshalb gibt es zwei Messungen."""
        alpha = np.asarray(Kunstprofil.bild(0.0).getchannel('A'))
        self.assertAlmostEqual(Ausrichtung.messen_mitte(alpha)['grad'], 0.0, delta=0.3)
        self.assertGreater(abs(Ausrichtung.messen(alpha)['grad']), 3.0)

    def test_nach_dem_drehen_steht_die_mittelachse_senkrecht(self):
        gedreht, bericht = Ausrichtung.ausrichten(Kunstprofil.bild(4.0), 'mitte', 'rechts')
        self.assertTrue(bericht['gedreht'])
        self.assertEqual(bericht['linie'], 'Mittelachse')
        self.assertLess(abs(bericht['nachher']), 0.5)
        self.assertLess(abs(Ausrichtung.messen_mitte(np.asarray(gedreht.getchannel('A')))['grad']), 0.5)

    def test_vorne_und_hinten_behalten_die_koerperachse(self):
        _, bericht = Ausrichtung.ausrichten(Kunstkoerper.bild(4.0), 'mitte', 'vorne')
        self.assertEqual(bericht['linie'], 'Körperachse')
        self.assertNotIn('versatz', bericht)

    def test_ohne_modus_gilt_wie_bisher_die_koerperachse(self):
        _, bericht = Ausrichtung.ausrichten(Kunstprofil.bild(4.0), rolle='rechts')
        self.assertEqual(bericht['linie'], 'Körperachse')

    def test_ein_versetzter_rumpf_wird_waagerecht_auf_die_achse_geschoben(self):
        """Kopf, Rumpf und Hüfte auf EINER senkrechten Achse — in beiden Blickrichtungen; die Dicke des Körpers (und damit die Wölbung von Rücken und Brust) bleibt."""
        for nach_rechts, rolle in ((True, 'rechts'), (False, 'links')):
            bild = Kunstprofil.bild(0.0, nach_rechts, wulst=20)
            vorher = Ausrichtung.streuung(bild)
            gedreht, bericht = Ausrichtung.ausrichten(bild, 'mitte', rolle)
            self.assertGreater(vorher, 3.0, rolle)
            self.assertLess(Ausrichtung.streuung(gedreht), 1.0, rolle)
            self.assertLess(bericht['streuung_nachher'], 1.0, rolle)
            vorher_breite = np.asarray(bild.getchannel('A'))[200] > 127
            nachher_breite = np.asarray(gedreht.getchannel('A'))[200] > 127
            self.assertAlmostEqual(nachher_breite.sum(), vorher_breite.sum(), delta=3, msg=rolle)

    def test_ein_gerader_koerper_wird_nicht_verschoben(self):
        bild = Kunstprofil.bild(0.0)
        gedreht, bericht = Ausrichtung.ausrichten(bild, 'mitte', 'rechts')
        self.assertIs(gedreht, bild)
        self.assertLess(max(abs(v) for v in bericht['versatz']), 0.5)

    def test_ein_zu_grosser_versatz_wird_nicht_ausgeglichen(self):
        gedreht, bericht = Ausrichtung.ausrichten(Kunstprofil.bild(0.0, wulst=150), 'mitte', 'rechts')
        self.assertIsNone(bericht['versatz'])
        self.assertIn('nicht auf eine Achse geschoben', Ausrichtung.zeile('seite.jpg', bericht))

    def test_die_logzeile_nennt_die_achse_und_den_versatz(self):
        _, bericht = Ausrichtung.ausrichten(Kunstprofil.bild(4.0, wulst=20), 'mitte', 'rechts')
        zeile = Ausrichtung.zeile('seite.jpg', bericht)
        self.assertIn('Mittelachse', zeile)
        self.assertIn('auf eine Achse geschoben', zeile)


class DieAblage(SimpleTestCase):
    """`Vorbereitungsstand.aktuell`: nur dieselben Fotos, Optionen und Fassung gelten."""

    databases = set()

    @staticmethod
    def _foto(ordner, name='vorne.jpg', inhalt=b'abc'):
        pfad = os.path.join(ordner, name)
        with open(pfad, 'wb') as f:
            f.write(inhalt)
        return {'datei': name, 'pfad': pfad, 'rolle': 'vorne'}

    def _ablegen(self, ordner, foto, optionen):
        Image.new('RGBA', (8, 8)).save(os.path.join(ordner, Vorbereitungsstand.stamm(foto['datei']) + '.png'))
        Vorbereitungsstand.schreiben(ordner, optionen, [{'datei': foto['datei'], 'stamm': Vorbereitungsstand.stamm(foto['datei']),
                                                         'rolle': foto['rolle'], 'quelle': Vorbereitungsstand.quelle(foto['pfad'])}])

    def test_ohne_datei_gilt_sie_nicht(self):
        with Pruefablage.ordner() as ordner:
            passt, grund = Vorbereitungsstand.aktuell(ordner, [self._foto(ordner)], {})
            self.assertFalse(passt)
            self.assertIn(Vorbereitungsstand.DATEI, grund)

    def test_dieselben_fotos_und_optionen_gelten(self):
        with Pruefablage.ordner() as ordner:
            foto = self._foto(ordner)
            self._ablegen(ordner, foto, {'ausrichten': 'an'})
            self.assertEqual(Vorbereitungsstand.aktuell(ordner, [foto], {'ausrichten': 'an'}), (True, ''))

    def test_eine_geaenderte_option_ein_ersetztes_foto_und_eine_neue_fassung_gelten_nicht(self):
        with Pruefablage.ordner() as ordner:
            foto = self._foto(ordner)
            self._ablegen(ordner, foto, {'ausrichten': 'an'})
            self.assertFalse(Vorbereitungsstand.aktuell(ordner, [foto], {'ausrichten': 'aus'})[0])
            self._foto(ordner, inhalt=b'anderes foto, andere Groesse')
            self.assertIn('geändert', Vorbereitungsstand.aktuell(ordner, [foto], {'ausrichten': 'an'})[1])
            self._ablegen(ordner, self._foto(ordner), {'ausrichten': 'an'})
            with open(os.path.join(ordner, Vorbereitungsstand.DATEI), encoding='utf-8') as f:
                stand = json.load(f)
            stand['fassung'] = Vorbereitungsstand.FASSUNG + 1
            with open(os.path.join(ordner, Vorbereitungsstand.DATEI), 'w', encoding='utf-8') as f:
                json.dump(stand, f)
            self.assertIn('Fassung', Vorbereitungsstand.aktuell(ordner, [foto], {'ausrichten': 'an'})[1])

    def test_ein_foto_mehr_oder_weniger_gilt_nicht_und_ein_foto_aus_wird_nicht_gezaehlt(self):
        with Pruefablage.ordner() as ordner:
            foto = self._foto(ordner)
            zweites = self._foto(ordner, 'hinten.jpg')
            self._ablegen(ordner, foto, {})
            self.assertEqual(Vorbereitungsstand.aktuell(ordner, [foto, {**zweites, 'rolle': 'aus'}], {}), (True, ''))
            self.assertEqual(Vorbereitungsstand.aktuell(ordner, [foto, zweites], {})[1], 'andere Fotos')

    def test_eine_fehlende_png_gilt_nicht(self):
        with Pruefablage.ordner() as ordner:
            foto = self._foto(ordner)
            self._ablegen(ordner, foto, {})
            os.remove(os.path.join(ordner, 'vorne.png'))
            self.assertIn('fehlt', Vorbereitungsstand.aktuell(ordner, [foto], {})[1])

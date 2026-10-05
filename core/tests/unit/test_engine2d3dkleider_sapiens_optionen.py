# -*- coding: utf-8 -*-
"""Die Einstellungen der Sapiens-Segmentierung und das Haar aus der Klasse „Hair" (05.10.2026).

DER ANLASS
==========
Edgar (05.10.2026): „was für andere Sapiens Klassen gibt es noch? Noch anderen Einstellungen, die du mir bisher verschwiegen hast? Baue diese alle ein und zeige mir die Optionen in der Oberfläche"
und, am Bild der Seitenansicht: „Haar textur noch auf dem Kopf". Bis dahin gab es EINE Option (`verwenden`), die Zuordnung Klasse → Stück, die Schwellen und die Modellgröße standen fest im Code, und
die Klasse `Hair` ging in „nicht Kleidung" auf.

WAS DIESE PRÜFUNG NICHT IST
===========================
Kunstdaten (kleine Stimmenmatrizen, Pfadnachbarschaft). Dass Sapiens auf Edgars Fotos die Klasse `Hair` trifft, dass 0.3B/0.6B laufen und dass das Haar-Objekt dann besser sitzt, zeigt nur der Lauf
(Karte „Segmentierung", Bericht „Haar"). Geschrieben am 05.10.2026, nicht gelaufen.

BDD - GEGEBEN / DANN
====================
    Optionen mit Unsinn und Grenzwerten    ... Vorgabe bzw. auf den Bereich geklemmt, ganzzahlig wo der Schritt ganz ist
    Schuhe = Haut, Zubehör = Oberteil      ... die Klassen wechseln das Stück; ein unbekannter Wert gilt als Vorgabe
    Flächen mit Haar-Stimmen               ... `Sapiensmaske.haar` und „keine Kleidung" (Haar ist kein Stück)
    Haar aus „sapiens"                     ... gesehene Flächen entscheidet Sapiens, ungesehene die Farbe, Gesicht und Bart bleiben geschützt
    Haar aus „beide"                       ... die Vereinigung
    Stimmen zu anderen Einstellungen       ... `Unbrauchbar` mit Grund; das Haar nimmt dann die Farbe und der Grund steht im Bericht
"""

import json
import os
from types import SimpleNamespace

from django.test import SimpleTestCase

from core.dienste.engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from core.dienste.engine2d3dkleidersegmentierung import Engine2d3dKleidersegmentierung
from core.dienste.engine2d3dkleidersegmentierungsoptionen import Engine2d3dKleidersegmentierungsoptionen as Optionen
from core.dienste.sapienshaar import Sapienshaar

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np  # noqa: E402
from Kleidung.sapiensmaske import Sapiensmaske  # noqa: E402
from Kleidung.sapienszuordnung import Sapienszuordnung  # noqa: E402
from sapiens_klassen import Sapiensklassen  # noqa: E402
from sapiens_stand import Sapiensstand  # noqa: E402
from scipy.sparse import diags  # noqa: E402


class DieOptionen(SimpleTestCase):
    def test_unsinn_wird_zur_vorgabe_und_zahlen_werden_geklemmt(self):
        o = Optionen.pruefen({'modell': '9b', 'haar': 'vielleicht', 'schuhe': 7, 'min_stimmen': '7.4', 'glaettung': 5, 'rand': -3, 'raster': 'viel', 'nah_mm': None})
        self.assertEqual((o['modell'], o['haar'], o['schuhe']), ('1b', 'farbe', 'fuesse'))
        self.assertEqual((o['min_stimmen'], o['glaettung'], o['rand'], o['raster'], o['nah_mm']), (7, 2, 0, 1600, 15))
        self.assertIsInstance(o['min_stimmen'], int)                        # Schritt 1 und ganze Vorgabe → ganze Zahl
        self.assertIsInstance(o['glaettung'], float)

    def test_die_vorgaben_sind_die_alten_festen_werte(self):
        v = Optionen.vorgaben()
        self.assertEqual((v['verwenden'], v['haar'], v['modell'], v['schuhe'], v['socken'], v['zubehoer']), ('aus', 'farbe', '1b', 'fuesse', 'fuesse', 'zubehoer'))
        self.assertEqual((v['min_stimmen'], v['glaettung'], v['nah_mm'], v['raster'], v['kante'], v['rand']), (Sapiensmaske.MIN_STIMMEN, Sapiensmaske.GLAETTUNG,
                                                                                                           Sapiensmaske.NAH_M * 1000, 1600, 2048, 5))

    def test_die_rechenoptionen_sind_auf_beiden_seiten_dieselben(self):
        self.assertEqual(Optionen.RECHENOPTIONEN, Sapiensstand.RECHENOPTIONEN)
        self.assertEqual(set(Optionen.rechenoptionen({})), set(Sapiensstand.RECHENOPTIONEN))

    def test_kopfhaut_ist_in_2d3d_kleider_sichtbar_und_steht_auf_haut(self):
        felder = {f['schluessel']: f for f in Engine2d3dKleideroptionen.katalog()['figur']['optionen']}
        self.assertEqual(felder['kopfhaut']['vorgabe'], 'haut')
        self.assertEqual(Engine2d3dKleideroptionen.figur({})['kopfhaut'], 'haut')
        self.assertEqual(Engine2d3dKleideroptionen.figur({'figur': {'kopfhaut': 'haar'}})['kopfhaut'], 'haar')      # ein gespeicherter Wert bleibt

    def test_im_katalog_stehen_die_feinen_felder_unter_einer_ueberschrift(self):
        katalog = Engine2d3dKleideroptionen.katalog()['segmentierung']
        self.assertEqual({f['schluessel'] for f in katalog['optionen'] if f.get('fein')}, {'min_stimmen', 'glaettung', 'nah_mm', 'raster', 'kante', 'rand'})
        self.assertTrue(katalog['fein_titel'])


class DieZuordnung(SimpleTestCase):
    def test_die_vorgaben_sind_die_der_wrapper_seite(self):
        self.assertEqual(Sapienszuordnung.NAMEN, Sapiensklassen.NAMEN)
        self.assertEqual(Sapienszuordnung.tabelle().tolist(), Sapiensklassen.stueck_je_klasse().tolist())
        self.assertEqual((Sapienszuordnung.STUECKE, Sapienszuordnung.HAAR), (Sapiensklassen.STUECKE, Sapiensklassen.HAAR))

    def _stueck(self, name, optionen=None):
        return int(Sapienszuordnung.tabelle(optionen)[Sapienszuordnung.NAMEN.index(name)])

    def test_schuhe_socken_und_zubehoer_folgen_den_optionen(self):
        self.assertEqual(self._stueck('Left_Shoe', {'schuhe': 'haut'}), Sapienszuordnung.KEINE)
        self.assertEqual(self._stueck('Right_Shoe', {'schuhe': 'zubehoer'}), Sapienszuordnung.ZUBEHOER)
        self.assertEqual(self._stueck('Left_Sock', {'socken': 'haut'}), Sapienszuordnung.KEINE)
        self.assertEqual(self._stueck('Apparel', {'zubehoer': 'oberteil'}), Sapienszuordnung.OBERTEIL)
        self.assertEqual(self._stueck('Left_Shoe', {'schuhe': 'haut'}) + self._stueck('Left_Sock'), Sapienszuordnung.FUESSE)      # die Socken blieben

    def test_ein_unbekannter_wert_gilt_als_vorgabe(self):
        self.assertEqual(self._stueck('Left_Shoe', {'schuhe': 'fliegen'}), Sapienszuordnung.FUESSE)
        self.assertEqual(self._stueck('Apparel', {'zubehoer': 'hose'}), Sapienszuordnung.ZUBEHOER)           # „hose" ist für Zubehör nicht erlaubt

    def test_haar_ist_immer_haar_und_der_hintergrund_hat_keine_stimme(self):
        for optionen in (None, {'schuhe': 'haut', 'zubehoer': 'haut', 'socken': 'haut'}):
            self.assertEqual(self._stueck('Hair', optionen), Sapienszuordnung.HAAR)
            self.assertEqual(self._stueck('Background', optionen), Sapienszuordnung.HINTERGRUND)
        self.assertEqual(Sapienszuordnung.matrix()[0].sum(), 0.0)

    def test_stimmen_je_klasse_werden_zu_stimmen_je_stueck(self):
        klassen = np.zeros((2, len(Sapienszuordnung.NAMEN)))
        klassen[0, Sapienszuordnung.NAMEN.index('Hair')] = 6
        klassen[0, Sapienszuordnung.NAMEN.index('Face_Neck')] = 2
        klassen[1, Sapienszuordnung.NAMEN.index('Left_Shoe')] = 5
        klassen[1, Sapienszuordnung.NAMEN.index('Background')] = 9
        stimmen = Sapienszuordnung.stimmen(klassen)
        self.assertEqual(stimmen.shape, (2, Sapienszuordnung.STUECKE))
        self.assertEqual((stimmen[0, Sapienszuordnung.HAAR], stimmen[0, Sapienszuordnung.KEINE]), (6, 2))
        self.assertEqual((stimmen[1, Sapienszuordnung.FUESSE], stimmen[1].sum()), (5, 5))                        # Hintergrund zählt nicht
        self.assertEqual(Sapienszuordnung.stimmen(klassen, {'schuhe': 'haut'})[1, Sapienszuordnung.KEINE], 5)
        with self.assertRaises(ValueError):
            Sapienszuordnung.stimmen(np.zeros((2, 5)))


class DieGewichte(SimpleTestCase):
    """Der Fehler vom 05.10.2026: mit dem Hugging-Face-Namen für 1B suchte der Lauf eine Datei, die nicht da war, und lud 4,7 GB noch einmal (bei 32 % angehalten)."""

    def test_die_1b_gewichte_liegen_unter_dem_alten_lokalen_namen(self):
        from sapiens_gewichte import Sapiensgewichte
        self.assertTrue(Sapiensgewichte.pfad('H', '1b').endswith('sapiens_1b_seg_torchscript.pt2'))
        self.assertEqual(Sapiensgewichte.eintrag('1b')[2], 4716314057)                       # Größe der schon geladenen Datei

    def test_die_anderen_groessen_tragen_den_namen_von_hugging_face_und_eine_unbekannte_wird_verweigert(self):
        from sapiens_gewichte import Sapiensgewichte
        for groesse in ('0.3b', '0.6b'):
            self.assertTrue(Sapiensgewichte.pfad('H', groesse).endswith(Sapiensgewichte.eintrag(groesse)[1]))
        self.assertEqual({g: len(Sapiensgewichte.eintrag(g)[3]) for g in Sapiensgewichte.GROESSEN}, {'0.3b': 64, '0.6b': 64, '1b': 64})        # SHA-256
        with self.assertRaises(ValueError):
            Sapiensgewichte.eintrag('9b')

    def test_eine_vorhandene_datei_der_richtigen_groesse_wird_nicht_noch_einmal_geladen(self):
        from unittest import mock

        from sapiens_gewichte import Sapiensgewichte
        with Pruefablage.ordner() as ordner:
            os.makedirs(os.path.join(ordner, 'sapiens'))
            with open(os.path.join(ordner, 'sapiens', 'test.pt2'), 'wb') as f:
                f.write(b'12345')
            tabelle = {'t': ('x/y', 'test.pt2', 5, 'a' * 64)}
            with mock.patch.dict(Sapiensgewichte.GROESSEN, tabelle), mock.patch('sapiens_gewichte.urllib.request.urlopen', side_effect=AssertionError('lädt')):
                self.assertEqual(Sapiensgewichte.beschaffen(ordner, groesse='t'), os.path.join(ordner, 'sapiens', 'test.pt2'))

    def test_die_optionswerte_der_groessen_sind_die_der_gewichte(self):
        from sapiens_gewichte import Sapiensgewichte
        werte = {w for e in Optionen.KATALOG if e['schluessel'] == 'modell' for w, _ in e['werte']}
        self.assertEqual(werte, set(Sapiensgewichte.GROESSEN))
        self.assertEqual(Optionen.vorgaben()['modell'], Sapiensgewichte.VORGABE)


class _Pfadkarte:
    def __init__(self, n):
        self._a = diags([np.ones(n - 1), np.ones(n - 1)], [-1, 1], format='csr')
        self.inhalt = np.full(n, 2e-4)

    def nachbarn(self):
        return self._a


class DieMaskeMitHaar(SimpleTestCase):
    N = 60

    def _stimmen(self):
        s = np.zeros((self.N, Sapienszuordnung.STUECKE))
        s[0:20, Sapienszuordnung.OBERTEIL] = 10
        s[20:40, Sapienszuordnung.HAAR] = 10
        s[40:60, Sapienszuordnung.KEINE] = 10
        return s

    def _verbinden(self, **einstellungen):
        mitte = np.zeros((self.N, 3))
        mitte[:, 1] = np.arange(self.N) * 0.01
        maske = Sapiensmaske(self._stimmen(), _Pfadkarte(self.N), np.full(self.N, 2e-4), mitte, kopf_ab=9.0, **einstellungen)
        return maske, maske.verbinden(np.zeros(self.N, dtype=np.int8))

    def test_haar_ist_kein_kleidungsstueck_und_steht_in_der_haarkarte(self):
        maske, (stueck, bericht) = self._verbinden()
        self.assertTrue((stueck[20:40] == 0).all())
        self.assertTrue(maske.haar[22:38].all())
        self.assertFalse(maske.haar[0:18].any())
        self.assertEqual(bericht['haar']['flaechen'], int(maske.haar.sum()))
        self.assertGreater(bericht['haar']['cm2'], 0)

    def test_die_schwellen_kommen_aus_den_optionen(self):
        maske, _ = self._verbinden(min_stimmen=1000.0)               # so viele Pixel hat keine Fläche → nichts gesehen
        self.assertFalse(maske.haar.any())
        self.assertEqual(Sapiensmaske.aus_optionen({'min_stimmen': 7, 'glaettung': 0.25, 'nah_mm': 30}), {'min_stimmen': 7.0, 'glaettung': 0.25, 'nah_m': 0.03})
        self.assertEqual(Sapiensmaske.aus_optionen({}), {})

    def test_stimmen_zu_anderen_einstellungen_werden_verweigert(self):
        stand = {'modell': '1b', 'raster': 1600, 'kante': 2048, 'rand': 5.0}
        with Pruefablage.ordner() as ordner:
            netz = os.path.join(ordner, 'mesh.glb')
            with open(netz, 'wb') as f:
                f.write(b'netz')
            stat = os.stat(netz)
            np.savez_compressed(os.path.join(ordner, Sapiensmaske.DATEI), klassen=np.ones((4, 28)), flaechen=4, fassung=Sapiensmaske.FASSUNG,
                                netz=np.array([stat.st_size, stat.st_mtime_ns]), optionen=np.array(json.dumps(stand, sort_keys=True)))
            self.assertEqual(Sapiensmaske.laden(ordner, netz, 4, stand).shape, (4, 28))
            with self.assertRaisesRegex(Sapiensmaske.Unbrauchbar, 'Einstellungen'):
                Sapiensmaske.laden(ordner, netz, 4, dict(stand, modell='0.3b'))

    def test_der_stand_der_ablage_kennt_die_einstellungen(self):
        stand = {'modell': '1b', 'raster': 1600, 'kante': 2048, 'rand': 5.0}
        with Pruefablage.ordner() as ordner:
            netz, png = os.path.join(ordner, 'mesh.glb'), os.path.join(ordner, 'vorne.png')
            for pfad in (netz, png):
                with open(pfad, 'wb') as f:
                    f.write(b'x')
            Sapiensstand.schreiben(ordner, netz, 4, [{'datei': 'vorne.jpg', 'quelle': Sapiensstand.quelle(png)}], {}, stand)
            self.assertEqual(Sapiensstand.aktuell(ordner, netz, {'vorne.jpg': png}, stand), (True, ''))
            self.assertIn('Einstellungen', Sapiensstand.aktuell(ordner, netz, {'vorne.jpg': png}, dict(stand, raster=2000))[1])
            self.assertEqual(Sapiensstand.aktuell(ordner, netz, {'vorne.jpg': png})[0], True)           # ohne Angabe wird nicht verglichen


class DasHaar(SimpleTestCase):
    N = 40

    class _Haarmaske:
        def __init__(self, n):
            self._a = diags([np.ones(n - 1), np.ones(n - 1)], [-1, 1], format='csr')
            self.inhalt = np.full(n, 1e-4)

        def nachbarn(self):
            return self._a

    def _lauf(self, ordner, quelle, einstellungen=None, **datei):
        netz = os.path.join(ordner, 'mesh.glb')
        with open(netz, 'wb') as f:
            f.write(b'netz')
        stat = os.stat(netz)
        klassen = np.zeros((self.N, 28))
        klassen[0:10, Sapienszuordnung.NAMEN.index('Hair')] = 10          # Sapiens: Haar auf 0–9
        klassen[10:20, Sapienszuordnung.NAMEN.index('Face_Neck')] = 10    # Sapiens: Haut auf 10–19
        # 20–39: kein Foto sieht sie
        stand = Optionen.rechenoptionen(einstellungen or {})
        np.savez_compressed(os.path.join(ordner, Sapiensmaske.DATEI), klassen=datei.get('klassen', klassen), flaechen=self.N, fassung=Sapiensmaske.FASSUNG,
                            netz=np.array([stat.st_size, stat.st_mtime_ns]), optionen=np.array(json.dumps(stand, sort_keys=True)))
        ablage = SimpleNamespace(arbeit=lambda *a: ordner, netzdatei=lambda original=False: netz)
        return SimpleNamespace(job=SimpleNamespace(kennung='x'), ablage=ablage, sapiens_haar=quelle, sapiens_einstellungen=Optionen.pruefen(einstellungen or {}))

    def _maske(self):
        alt = np.zeros(self.N, dtype=bool)
        alt[5:15] = True                    # die Farbe sieht Haar auf 5–14
        alt[30:35] = True                   # und auf 30–34 (kein Foto sieht sie)
        geschuetzt = np.zeros(self.N, dtype=bool)
        geschuetzt[3] = True                # Gesichtszone mitten im Sapiens-Haar
        bart = np.zeros(self.N, dtype=bool)
        bart[7] = True
        return {'haar': alt, 'geschuetzt': geschuetzt, 'bart': bart, 'unten': np.zeros(self.N, dtype=bool)}

    def test_farbe_aendert_nichts(self):
        with Pruefablage.ordner() as ordner:
            maske = self._maske()
            vorher = maske['haar'].copy()
            self.assertIsNone(Sapienshaar(self._lauf(ordner, 'farbe')).anwenden(maske, self._Haarmaske(self.N), self.N))
            self.assertIsNone(Sapienshaar(SimpleNamespace(job=None, ablage=None)).anwenden(maske, self._Haarmaske(self.N), self.N))       # „Mesh to 3D": kein Attribut
        self.assertTrue((maske['haar'] == vorher).all())

    def test_sapiens_entscheidet_wo_es_sieht_und_die_farbe_wo_nicht(self):
        with Pruefablage.ordner() as ordner:
            maske = self._maske()
            bericht = Sapienshaar(self._lauf(ordner, 'sapiens')).anwenden(maske, self._Haarmaske(self.N), self.N)
        haar = maske['haar']
        self.assertTrue(haar[0:3].all() and haar[4:7].all() and haar[8:10].all())      # Sapiens-Haar bleibt (ohne Gesichtszone 3 und Bart 7)
        self.assertFalse(haar[3] or haar[7])
        self.assertFalse(haar[10:15].any())                                           # die Farbe sah Haar, Sapiens sieht dort Haut → weg
        self.assertTrue(haar[30:35].all())                                            # kein Foto sieht sie → die Farbe gilt
        self.assertTrue(bericht['verwendet'])
        self.assertEqual((bericht['hinzu_flaechen'], bericht['weg_flaechen']), (int((haar & ~self._maske()['haar']).sum()), 5))

    def test_beide_ist_die_vereinigung(self):
        with Pruefablage.ordner() as ordner:
            maske = self._maske()
            Sapienshaar(self._lauf(ordner, 'beide')).anwenden(maske, self._Haarmaske(self.N), self.N)
        haar = maske['haar']
        self.assertTrue(haar[0:3].all() and haar[10:15].all() and haar[30:35].all())
        self.assertFalse(haar[3])                                                     # geschützt bleibt geschützt

    def test_ohne_passende_stimmen_gilt_die_farbe_und_der_grund_steht_im_bericht(self):
        with Pruefablage.ordner() as ordner:
            lauf = self._lauf(ordner, 'sapiens')
            maske = self._maske()
            vorher = maske['haar'].copy()
            bericht = Sapienshaar(lauf).anwenden(maske, self._Haarmaske(self.N), self.N + 1)       # andere Flächenzahl
        self.assertFalse(bericht['verwendet'])
        self.assertIn('Flächen', bericht['grund'])
        self.assertTrue((maske['haar'] == vorher).all())

    def test_der_schritt_laeuft_im_vollen_lauf_auch_fuer_das_haar(self):
        def schritt(**optionen):
            job = SimpleNamespace(kennung='x', optionen={'segmentierung': optionen}, ergebnis={}, bilder=[])
            return Engine2d3dKleidersegmentierung(SimpleNamespace(job=job, ablage=None, ab=None, melden=lambda *a: None))
        self.assertFalse(schritt().gebraucht())
        self.assertFalse(schritt(haar='farbe').gebraucht())
        self.assertTrue(schritt(haar='sapiens').gebraucht())
        self.assertTrue(schritt(haar='beide').gebraucht())
        self.assertTrue(schritt(verwenden='an').gebraucht())

    def test_der_koerperlauf_gibt_kleidung_und_haar_die_optionen(self):
        from core.dienste.engine2d3dkleiderkoerperlauf import Engine2d3dKleiderkoerperlauf
        aussen = SimpleNamespace(job=SimpleNamespace(optionen={'segmentierung': {'verwenden': 'an', 'haar': 'beide', 'schuhe': 'haut'}}), ablage=None, optionen={}, Angehalten=Exception)
        lauf = Engine2d3dKleiderkoerperlauf(aussen, {})
        self.assertEqual((lauf.sapiens_maske, lauf.sapiens_haar), (True, 'beide'))
        self.assertEqual((lauf.sapiens_einstellungen['schuhe'], lauf.sapiens_einstellungen['socken']), ('haut', 'fuesse'))
        ohne = Engine2d3dKleiderkoerperlauf(SimpleNamespace(job=SimpleNamespace(optionen={}), ablage=None, optionen={}, Angehalten=Exception), {})
        self.assertEqual((ohne.sapiens_maske, ohne.sapiens_haar), (False, 'farbe'))

# -*- coding: utf-8 -*-
"""Der Schritt „Kopf" von „2D3D Kleider" (07.10.2026): der Kopf wird aus den drei Fotos geschnitten und als eigenes Kopfnetz gerechnet.

DER ANLASS
==========
Edgar (07.10.2026): „mach einen extra Kopf lauf, extrahiere dazu die bilder vom Kopf, von alle drei seiten … Per Check box (default an) anwählbar. wenn das ausgewählt ist, erstellst und zeigst du die 3 Kopf Bilder
im UI und rechnest den Kopf extra." Hunyuan3D sieht jedes Bild nur als 518-px-Raster; auf einem Ganzkörperfoto bleiben dem Kopf rund 50 px.

WAS DIESE PRÜFUNG NICHT IST
===========================
Sie läuft ohne GPU, ohne Runner und ohne Server an Kunstdaten (eine Silhouette aus Ellipse, Hals und Schultern; Attrappen für Auftrag und Ablage). Dass die Ausschnitte an Edgars echten Fotos den Kopf mit Hals zeigen, ist
eine Sichtprobe (`ProjektTemp/_wegwerf/edgar/kopf_ausschnitt_probe.py`, `kopf_probe/bogen.png`); ob Hunyuan3D daraus ein besseres Gesicht rechnet und ob die Körper-Kette das Kopfnetz sauber einsetzt, zeigt nur ein Lauf.
NICHT GELAUFEN (Stand 07.10.2026): geschrieben, nicht gestartet — Tests laufen nur auf Ansage.

BDD - GEGEBEN / DANN
====================
    Eine Silhouette mit Kopf, Hals, Schultern  ... der Ausschnitt ist quadratisch, trägt den ganzen Kopf, aber keine Schultern
    Ein leeres Foto                             ... ValueError, kein stiller Ausschnitt
    Häkchen aus                                 ... der Schritt entfällt im vollen Lauf, ausdrücklich gestartet läuft er; die Körper-Kette bekommt kein Kopfnetz
    Häkchen an, Netz gerechnet                  ... `netz_fuer` gibt den Pfad, die Körper-Kette reicht ihn als `kopfnetz` an den Runner
"""

import inspect
import re
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase
from PIL import Image, ImageDraw

from core.daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from core.dienste.engine2d3dkleiderkoerperlauf import Engine2d3dKleiderkoerperlauf
from core.dienste.engine2d3dkleiderkopf import Engine2d3dKleiderkopf
from core.dienste.engine2d3dkleiderkopfausschnitt import Engine2d3dKleiderkopfausschnitt
from core.dienste.engine2d3dkleiderkopfliste import Engine2d3dKleiderkopfliste
from core.dienste.engine2d3dkleiderlauf import Engine2d3dKleiderlauf
from core.dienste.engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from core.dienste.meshfigurlauf import Meshfigurlauf


def silhouette(kopf_hoehe=90, hals_breite=40, hoehe=600):
    """Ein RGBA-Quadrat (800 px) mit einer Figur: Kopf (Ellipse), kurzer Hals, STEIL ansetzende Schultern (±20 → ±140 px auf 8 Zeilen), Rumpf bis `hoehe`."""
    bild = Image.new('RGBA', (800, 800), (0, 0, 0, 0))
    zeichner = ImageDraw.Draw(bild)
    oben = 100
    farbe = (200, 60, 60, 255)
    zeichner.ellipse((400 - 40, oben, 400 + 40, oben + kopf_hoehe), fill=farbe)                       # Kopf
    hals_oben, hals_unten = oben + kopf_hoehe - 10, oben + kopf_hoehe + 4
    zeichner.rectangle((400 - hals_breite // 2, hals_oben, 400 + hals_breite // 2, hals_unten), fill=farbe)   # Hals
    zeichner.polygon([(400 - hals_breite // 2, hals_unten), (400 + hals_breite // 2, hals_unten), (400 + 140, hals_unten + 8),
                      (400 + 140, oben + hoehe), (400 - 140, oben + hoehe), (400 - 140, hals_unten + 8)], fill=farbe)  # Schultern und Rumpf
    return bild


class DerAusschnitt(SimpleTestCase):
    def setUp(self):
        # Die Kunstfigur ist 800 px groß — in voller Auflösung messen (sonst liegt die Halszeile ±8 px daneben); echte Fotos laufen mit `TEILER` 8.
        self.enterContext(mock.patch.object(Engine2d3dKleiderkopfausschnitt, 'TEILER', 1))
        # Der Ausschnitt reicht `HALS_DAZU` der Kopfhöhe unter die Halszeile. Mit 0,06 (seit 07.10.2026; vorher 0,10) endet er bei dieser Kunstfigur ÜBER den Schultern (die ab Zeile 194 ansetzen) — dann
        # sähen weder die Prüfung noch ihre Gegenprobe je eine Schulter. Tiefer gesetzt reicht er in sie hinein, und erst dort zeigt sich, ob `HALS_SEITE` sie abschneidet.
        self.enterContext(mock.patch.object(Engine2d3dKleiderkopfausschnitt, 'HALS_DAZU', 0.35))

    def test_der_ausschnitt_ist_quadratisch_und_traegt_den_ganzen_kopf(self):
        aus, befund = Engine2d3dKleiderkopfausschnitt.ausschnitt(silhouette())
        self.assertEqual(aus.width, aus.height)
        alpha = np.asarray(aus.getchannel('A')) > 127
        zeilen = np.nonzero(alpha.any(axis=1))[0]
        self.assertGreater(zeilen[0], 0, 'über dem Scheitel bleibt ein Rand')
        spalten = np.nonzero(alpha.any(axis=0))[0]
        self.assertGreater(spalten[0], 0)
        self.assertLess(spalten[-1], aus.width - 1)
        self.assertEqual(befund['breite'], aus.width)

    def test_die_schultern_bleiben_draussen(self):
        aus, _ = Engine2d3dKleiderkopfausschnitt.ausschnitt(silhouette())
        alpha = np.asarray(aus.getchannel('A')) > 127
        # Unten im Ausschnitt steht höchstens der Hals (40 px) mit seinem Streifen je Seite, nie die Schultern, die auf 8 Zeilen von 40 auf 280 px wachsen.
        unten = alpha[-3:].sum(axis=1).max()
        self.assertLess(unten, 40 * (1 + 2 * Engine2d3dKleiderkopfausschnitt.HALS_SEITE) + 4)

    def test_sabotage_ohne_halsstumpf_stuenden_die_schultern_im_bild(self):
        """Gegenprobe: ohne die seitliche Begrenzung (`HALS_SEITE` riesig) wäre die untere Zeile breiter als der Hals — der Test oben sieht die Begrenzung also wirklich."""
        with mock.patch.object(Engine2d3dKleiderkopfausschnitt, 'HALS_SEITE', 50):
            aus, _ = Engine2d3dKleiderkopfausschnitt.ausschnitt(silhouette())
        alpha = np.asarray(aus.getchannel('A')) > 127
        self.assertGreater(alpha[-3:].sum(axis=1).max(), 40 * 1.5 + 4)

    def test_der_kopfanteil_ist_der_von_kopf_zu_koerper(self):
        _, befund = Engine2d3dKleiderkopfausschnitt.ausschnitt(silhouette(kopf_hoehe=90, hoehe=600))
        self.assertGreater(befund['kopf_anteil'], 0.12)
        self.assertLess(befund['kopf_anteil'], 0.20)

    def test_ein_leeres_foto_wirft(self):
        with self.assertRaises(ValueError):
            Engine2d3dKleiderkopfausschnitt.ausschnitt(Image.new('RGBA', (200, 200), (0, 0, 0, 0)))

    def test_ohne_halsminimum_gilt_der_rueckfall(self):
        """Langes Haar über dem Hals (Rückansicht): keine Einschnürung im Suchfenster — dann gilt `HALS_RUECKFALL`, und es gibt trotzdem einen quadratischen Ausschnitt."""
        bild = Image.new('RGBA', (800, 800), (0, 0, 0, 0))
        ImageDraw.Draw(bild).rectangle((300, 100, 500, 700), fill=(1, 2, 3, 255))      # ein Balken: Breite überall gleich, das Minimum liegt am Rand des Fensters
        aus, befund = Engine2d3dKleiderkopfausschnitt.ausschnitt(bild)
        self.assertTrue(befund['hals_rueckfall'])
        self.assertEqual(aus.width, aus.height)


class DieOptionen(SimpleTestCase):
    def test_die_gruppe_kopf_steht_im_katalog_mit_haken_modell_und_flaechen(self):
        katalog = Engine2d3dKleideroptionen.katalog()['kopf']['optionen']
        self.assertEqual([f['schluessel'] for f in katalog], ['rechnen', 'modell', 'flaechen'])
        rechnen = katalog[0]
        self.assertEqual((rechnen['art'], rechnen['vorgabe']), ('haken', 'an'), 'Edgar: Häkchen, Vorgabe an')

    def test_ungueltige_werte_werden_zur_vorgabe_und_aus_bleibt_aus(self):
        self.assertEqual(Engine2d3dKleideroptionen.kopf({'kopf': {'rechnen': 'vielleicht', 'modell': 'quatsch', 'flaechen': '7'}}),
                         {'rechnen': 'an', 'modell': 'hunyuan3d_2mv', 'flaechen': '300000'})
        self.assertEqual(Engine2d3dKleideroptionen.kopf({'kopf': {'rechnen': 'aus', 'modell': 'hunyuan3d_2'}})['rechnen'], 'aus')
        self.assertEqual(Engine2d3dKleideroptionen.kopf(None)['rechnen'], 'an')

    def test_mischen_behaelt_die_andere_gruppe(self):
        neu = Engine2d3dKleideroptionen.mischen({'iterationen': {'runden': 55}}, {'kopf': {'rechnen': 'aus'}})
        self.assertEqual((neu['kopf']['rechnen'], neu['iterationen']['runden']), ('aus', 55))


class DerLauf(SimpleTestCase):
    def test_der_schritt_steht_zwischen_netz_und_segmentierung(self):
        s = Engine2d3dKleiderlauf.SCHRITTE
        self.assertEqual((s[s.index('kopf') - 1], s[s.index('kopf') + 1]), ('netz', 'segmentierung'))
        self.assertIn('kopf', Engine2d3dKleiderlauf.BAENDER)

    def test_die_schrittfolge_kennt_ihn(self):
        self.assertIn("'kopf': lambda: Engine2d3dKleiderkopf(self).ausfuehren()", inspect.getsource(Engine2d3dKleiderlauf.schrittfolge))

    def test_ein_neuer_kopf_loest_keinen_archivlauf_aus(self):
        """Wie die Segmentierung: seine Wirkung kommt erst, wenn „Körper" neu rechnet — der trägt die Runden dann beiseite."""
        from core.dienste.iterationsarchiv import Iterationsarchiv
        self.assertFalse(Iterationsarchiv.veraltet_durch('kopf'))


class DerSchritt(SimpleTestCase):
    @staticmethod
    def _job(rechnen='an', netz=None):
        ergebnis = {'kopf': {'bilder': [], 'netz': netz}} if netz is not None else {}
        return SimpleNamespace(kennung='x', optionen={'kopf': {'rechnen': rechnen}}, ergebnis=ergebnis, bilder=[])

    def _schritt(self, rechnen, ab):
        meldungen = []
        lauf = SimpleNamespace(job=self._job(rechnen), ablage=mock.MagicMock(), ab=ab, melden=lambda *a: meldungen.append(a), sichern=lambda *a: None)
        return Engine2d3dKleiderkopf(lauf), meldungen

    def test_bei_haken_aus_entfaellt_er_im_vollen_lauf(self):
        schritt, meldungen = self._schritt('aus', None)
        with mock.patch.object(Engine2d3dKleiderkopf, '_ausschnitte') as ausschnitte:
            schritt.ausfuehren()
            self._schritt('aus', 'netz')[0].ausfuehren()              # „ab Netz" ist KEIN ausdrücklicher Start dieses Schritts
        ausschnitte.assert_not_called()
        self.assertTrue(meldungen)

    def test_ausdruecklich_gestartet_laeuft_er_auch_bei_haken_aus(self):
        schritt, _ = self._schritt('aus', 'kopf')
        with mock.patch.object(Engine2d3dKleiderkopf, '_ausschnitte', side_effect=RuntimeError('Kein vorbereitetes Foto')) as ausschnitte:
            with self.assertRaises(RuntimeError):
                schritt.ausfuehren()
        ausschnitte.assert_called_once()

    def test_mit_haken_laeuft_er_im_vollen_lauf(self):
        schritt, _ = self._schritt('an', None)
        with mock.patch.object(Engine2d3dKleiderkopf, '_ausschnitte', side_effect=RuntimeError('x')) as ausschnitte:
            with self.assertRaises(RuntimeError):
                schritt.ausfuehren()
        ausschnitte.assert_called_once()

    def test_das_kopfnetz_gilt_nur_mit_haken_und_gerechnetem_netz(self):
        ablage = mock.MagicMock()
        ablage.netzdatei.return_value = Path('kopf/mesh.glb')
        self.assertEqual(Engine2d3dKleiderkopf.netz_fuer(self._job('an', {'datei': 'mesh.glb'}), ablage), Path('kopf/mesh.glb'))
        self.assertIsNone(Engine2d3dKleiderkopf.netz_fuer(self._job('aus', {'datei': 'mesh.glb'}), ablage), 'Haken aus → kein Kopfnetz')
        self.assertIsNone(Engine2d3dKleiderkopf.netz_fuer(self._job('an', None), ablage), 'nicht gerechnet → kein Kopfnetz')
        self.assertIsNone(Engine2d3dKleiderkopf.netz_fuer(self._job('an', {}), ablage), 'Lauf nicht zu Ende → kein Kopfnetz')


class DieKoerperKette(SimpleTestCase):
    def test_2d3d_reicht_das_kopfnetz_des_schritts_an_den_runner(self):
        lauf = object.__new__(Engine2d3dKleiderkoerperlauf)
        lauf.job, lauf.ablage = SimpleNamespace(kennung='x'), mock.MagicMock()
        with mock.patch.object(Engine2d3dKleiderkopf, 'netz_fuer', return_value=Path('kopf/mesh.glb')) as netz_fuer:
            self.assertEqual(lauf.kopfnetz(), Path('kopf/mesh.glb'))
        netz_fuer.assert_called_once_with(lauf.job, lauf.ablage)

    def test_mesh_to_3d_liest_weiter_eingang_kopf(self):
        lauf = object.__new__(Meshfigurlauf)
        lauf.ablage = mock.MagicMock()
        lauf.ablage.netzdatei.return_value = Path('eingang_kopf/k.glb')
        lauf.job = SimpleNamespace(eingang={'kopf': {'datei': 'k.glb'}})
        self.assertEqual(lauf.kopfnetz(), Path('eingang_kopf/k.glb'))
        lauf.job = SimpleNamespace(eingang={})
        self.assertIsNone(lauf.kopfnetz())

    def test_der_auftrag_des_runners_benutzt_die_methode(self):
        """Nicht mehr die feste Zeile `eingang['kopf']` — sonst fände 2D3D Kleider sein Kopfnetz nie."""
        quelle = inspect.getsource(Meshfigurlauf.auftrag)
        self.assertIn('self.kopfnetz()', quelle)
        self.assertNotIn("get('kopf')", quelle)


class DieAblage(SimpleTestCase):
    def test_kopf_ist_ein_lesbarer_ordner_ohne_unterpfade(self):
        ablage = Engine2d3dKleiderablage('2026.10.07.99.99.99')
        self.assertIn('kopf', Engine2d3dKleiderablage.LESBAR)
        self.assertEqual(ablage.datei('kopf', 'ausschnitt_vorne.png').name, 'ausschnitt_vorne.png')
        with self.assertRaises(ValueError):
            ablage.datei('kopf', '../netz/mesh.glb')

    def test_das_kopfnetz_liegt_flach_in_kopf(self):
        ablage = Engine2d3dKleiderablage('2026.10.07.99.99.99')
        self.assertEqual(ablage.kopf('mesh.glb').parent.name, 'kopf')
        self.assertEqual(ablage.kopf_arbeit().name, 'kopf_arbeit')
        self.assertEqual(ablage.kopf_vorbereitet().name, 'kopf_vorbereitet')


class DieListe(SimpleTestCase):
    def test_ohne_lauf_gibt_es_keine_liste(self):
        self.assertIsNone(Engine2d3dKleiderkopfliste.von(SimpleNamespace(kennung='nichtda', optionen={}, ergebnis={})))

    def test_geaenderte_optionen_machen_die_liste_veraltet(self):
        job = SimpleNamespace(kennung='nichtda', optionen={'kopf': {'modell': 'hunyuan3d_2'}},
                              ergebnis={'kopf': {'bilder': [], 'netz': None, 'optionen': {'modell': 'hunyuan3d_2mv', 'flaechen': '300000'}}})
        liste = Engine2d3dKleiderkopfliste.von(job)
        self.assertTrue(liste['veraltet'])
        self.assertIn('modell', liste['grund'])
        self.assertEqual(liste['bilder'], [], 'Dateien, die es nicht gibt, stehen nicht in der Anzeige')


class DieSeite(SimpleTestCase):
    """Quelltext-Prüfungen der Oberfläche (kein DOM): Karte, Bausteine, Verdrahtung."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        wurzel = Path(settings.BASE_DIR)
        cls.vorlage = (wurzel / 'templates' / '_engine2d3dkleider_kopf.html').read_text(encoding='utf-8')
        cls.haupt = (wurzel / 'templates' / 'engine2d3dkleider_auftrag.html').read_text(encoding='utf-8')
        cls.js = (wurzel / 'static' / 'viewer' / 'engine2d3dkleider' / 'engine2d3dkleiderkopf.js').read_text(encoding='utf-8')
        cls.seite = (wurzel / 'static' / 'viewer' / 'engine2d3dkleider' / 'engine2d3dkleiderseite.js').read_text(encoding='utf-8')

    def test_die_karte_wird_eingebunden_und_traegt_jede_kennung_die_das_js_liest(self):
        self.assertIn('{% include "_engine2d3dkleider_kopf.html" %}', self.haupt)
        for kennung in re.findall(r"getElementById\('([^']+)'\)", self.js):
            self.assertIn('id="%s"' % kennung, self.vorlage, kennung)

    def test_der_behaelter_der_gruppe_kopf_steht_in_der_karte(self):
        """`Engine2d3dKleidereinstellungen.GRUPPEN` und `aufbauen` finden Behälter nach dem Namen `engine2d3dkleider-optionen-<gruppe>`."""
        self.assertIn('id="engine2d3dkleider-optionen-kopf"', self.vorlage)

    def test_die_seite_baut_und_zeigt_den_baustein_und_nennt_den_schritt(self):
        self.assertIn("import { Engine2d3dKleiderkopf } from './engine2d3dkleiderkopf.js';", self.seite)
        self.assertIn('new Engine2d3dKleiderkopf(this)', self.seite)
        self.assertIn('this.kopf', self.seite.split('zeigen() {', 1)[1])
        self.assertRegex(self.seite, r"kopf: 'Kopf")

    def test_der_knopf_startet_nur_diesen_schritt(self):
        self.assertIn("seite.starten('kopf', 'kopf', this.knopf)", self.js)

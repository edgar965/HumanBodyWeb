# -*- coding: utf-8 -*-
"""Tests fuer Animationsauswahl — Kategorien, Eintraege, Wertformat.

Anlass ist der Performance-Durchgang (16.08.2026): die Einstellungsseiten
lieferten alle 7.067 Animationen mit, obwohl jede Kategorie zugeklappt startet.
Festgehalten werden hier drei Dinge — dass die Seite nur noch die Koepfe
enthaelt, dass beide Wertformate stimmen, und dass ein erfundener
Kategoriename nicht aus dem BVH-Verzeichnis herausfuehrt.

Gearbeitet wird auf einem eigenen Verzeichnisbaum unter ProjektTemp, nicht auf
`HumanBody/data/` — das sind Produktionsdaten und bleiben unangetastet.
"""

import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import TestCase, override_settings

from core.dienste.animationsauswahl import Animationsauswahl


def _baum_anlegen(wurzel, inhalt):
    for kategorie, dateien in inhalt.items():
        ordner = Path(wurzel) / 'data' / 'animations' / 'bvh' / kategorie
        ordner.mkdir(parents=True, exist_ok=True)
        for datei in dateien:
            (ordner / datei).write_text('HIERARCHY\n', encoding='utf-8')


class AnimationsBaum:
    """Gemeinsamer Testbaum. Bewusst KEIN TestCase, sondern eine Beimischung —
    als Basisklasse liefen die Tests der Basis in jeder Unterklasse noch einmal.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Kein System-Temp (Vorgeschichte: Datenmuell auf C:) — ins Projekt.
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        cls.wurzel = tempfile.mkdtemp(prefix='animauswahl_', dir=str(basis))
        _baum_anlegen(cls.wurzel, {
            'Aist': ['tanz_01.bvh', 'tanz_02.bvh'],
            'Bandai 1': ['gehen.bvh'],
            'Leer': [],
            'KeineBvh': [],
        })
        (Path(cls.wurzel) / 'data' / 'animations' / 'bvh' / 'KeineBvh'
         / 'liesmich.txt').write_text('x', encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.wurzel, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.ueberschrieben = override_settings(HUMANBODY_ROOT=self.wurzel)
        self.ueberschrieben.enable()
        self.addCleanup(self.ueberschrieben.disable)


class AnimationsauswahlTest(AnimationsBaum, TestCase):

    def test_kategorien_mit_anzahl(self):
        self.assertEqual(Animationsauswahl().kategorien(),
                         [{'name': 'Aist', 'anzahl': 2},
                          {'name': 'Bandai 1', 'anzahl': 1}])

    def test_leere_ordner_fallen_raus(self):
        namen = [k['name'] for k in Animationsauswahl().kategorien()]
        self.assertNotIn('Leer', namen)
        self.assertNotIn('KeineBvh', namen)

    def test_eintraege_als_url(self):
        self.assertEqual(Animationsauswahl().eintraege('Aist'), [
            {'value': '/api/character/bvh/Aist/tanz_01/', 'label': 'tanz_01'},
            {'value': '/api/character/bvh/Aist/tanz_02/', 'label': 'tanz_02'},
        ])

    def test_eintraege_als_pfad(self):
        auswahl = Animationsauswahl(Animationsauswahl.ALS_PFAD)
        self.assertEqual(auswahl.eintraege('Bandai 1'),
                         [{'value': 'Bandai 1/gehen', 'label': 'gehen'}])

    def test_unbekannte_kategorie_bleibt_leer(self):
        self.assertEqual(Animationsauswahl().eintraege('gibtsnicht'), [])

    def test_kategorie_fuehrt_nicht_aus_dem_verzeichnis(self):
        """Der Name kommt aus der URL — geprueft wird gegen echte Ordner."""
        for versuch in ('..', '../..', '../../data', 'Aist/../Aist'):
            self.assertEqual(Animationsauswahl().eintraege(versuch), [])

    def test_fehlende_wurzel_wirft_nicht(self):
        with override_settings(HUMANBODY_ROOT=self.wurzel + '_weg'):
            self.assertEqual(Animationsauswahl().kategorien(), [])

    def test_unbekanntes_wertformat_faellt_auf_url_zurueck(self):
        self.assertEqual(Animationsauswahl('quatsch').wertformat,
                         Animationsauswahl.ALS_URL)

    def test_zerlegen_kennt_beide_wertformate(self):
        self.assertEqual(Animationsauswahl.zerlegen('/api/character/bvh/Aist/tanz_01/'),
                         ('Aist', 'tanz_01'))
        self.assertEqual(Animationsauswahl.zerlegen('Aist/tanz_01'), ('Aist', 'tanz_01'))
        for unsinn in ('', None, 'nurname', 'a/b/c/d'):
            self.assertIsNone(Animationsauswahl.zerlegen(unsinn))

    def test_vorhandene_datei_fehlt_nicht(self):
        self.assertFalse(Animationsauswahl().fehlt('/api/character/bvh/Aist/tanz_01/'))
        self.assertFalse(Animationsauswahl().fehlt(''))

    def test_geloeschte_datei_wird_gemeldet(self):
        """Der Befund: die Einstellung zeigte auf eine nicht mehr vorhandene Datei."""
        self.assertTrue(Animationsauswahl().fehlt('/api/character/bvh/Aist/weg/'))
        self.assertTrue(Animationsauswahl().fehlt('/api/character/bvh/Weg/tanz_01/'))

    def test_fehlende_prueft_mehrere_werte(self):
        auswahl = Animationsauswahl()
        self.assertEqual(
            auswahl.fehlende(['/api/character/bvh/Aist/tanz_01/',
                              '/api/character/bvh/Aist/weg/', '']),
            {'/api/character/bvh/Aist/weg/'})

    def test_seitenteil_liefert_beides(self):
        teil = Animationsauswahl().seitenteil(['/api/character/bvh/Aist/weg/'])
        self.assertEqual([k['name'] for k in teil['anim_kategorien']],
                         ['Aist', 'Bandai 1'])
        self.assertEqual(teil['anim_fehlt'], {'/api/character/bvh/Aist/weg/'})


class AnimationsEndpunktTest(AnimationsBaum, TestCase):
    """Derselbe Baum, jetzt ueber /api/animationen/<kategorie>/."""

    def test_endpunkt_liefert_eintraege(self):
        antwort = self.client.get('/api/animationen/Aist/')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(len(antwort.json()['animationen']), 2)

    def test_endpunkt_kennt_das_wertformat(self):
        antwort = self.client.get('/api/animationen/Bandai%201/?wertformat=pfad')
        self.assertEqual(antwort.json()['animationen'][0]['value'], 'Bandai 1/gehen')

    def test_endpunkt_bei_unbekannter_kategorie(self):
        antwort = self.client.get('/api/animationen/gibtsnicht/')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json()['animationen'], [])


class EinstellungsseitenTest(AnimationsBaum, TestCase):
    """Kern des Befunds: die Seiten duerfen nicht mit dem Bestand wachsen."""

    SEITEN = ('/settings/model/', '/settings/result/',
              '/settings/scene/', '/settings/theatre/')

    def test_seiten_enthalten_nur_die_koepfe(self):
        for seite in self.SEITEN:
            with self.subTest(seite=seite):
                inhalt = self.client.get(seite).content
                self.assertIn(b'anim-kategorie', inhalt)
                # tanz_01 steckt in einer Kategorie — es darf NICHT in der
                # Seite stehen, sondern kommt erst ueber den Endpunkt.
                self.assertNotIn(b'tanz_01', inhalt)

    def test_seiten_bleiben_klein(self):
        for seite in self.SEITEN:
            with self.subTest(seite=seite):
                self.assertLess(len(self.client.get(seite).content), 200_000)

    def test_theatre_bekommt_das_kurze_wertformat(self):
        inhalt = self.client.get('/settings/theatre/').content
        self.assertIn(b'data-wertformat="pfad"', inhalt)

    def test_viewer_seiten_bekommen_das_url_wertformat(self):
        inhalt = self.client.get('/settings/model/').content
        self.assertIn(b'data-wertformat="url"', inhalt)

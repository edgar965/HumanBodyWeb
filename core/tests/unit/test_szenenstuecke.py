# -*- coding: utf-8 -*-
u"""Gespeicherte Szenen behalten ihr drapiertes Netz.

BEFUND (Edgar, 10.09.2026): „FemaleGarmentCode hatte ein langes T-Shirt, beim
Laden ist das T-Shirt kurz." Die Szene merkte sich nur eine Adresse, und die
Datei dahinter wird von jedem weiteren Bau desselben Stuecktyps ueberschrieben.

Alle Tests arbeiten in einem eigenen Ordner unter `_wegwerf/` — nie in
`Assets/GarmentCode/ausgabe/` (`~/.claude/rules/tests-und-produktivdaten.md`).
"""

import json
import os
import shutil
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from GarmentCode.entwurf import Entwurf
from GarmentCode.szenenstuecke import Szenenstuecke


class AblageAufProbe(SimpleTestCase):
    u"""Legt `Entwurf.AUSGABE` fuer die Dauer des Tests um."""

    def setUp(self):
        wegwerf = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               '..', '..', '..', '_wegwerf', 'szenenprobe')
        self.wurzel = tempfile.mkdtemp(dir=os.path.abspath(
            os.path.dirname(wegwerf)), prefix='szenenprobe_')
        self.echte_ausgabe = Entwurf.AUSGABE
        Entwurf.AUSGABE = self.wurzel
        self.addCleanup(self._aufraeumen)

    def _aufraeumen(self):
        Entwurf.AUSGABE = self.echte_ausgabe
        shutil.rmtree(self.wurzel, ignore_errors=True)

    def netz_anlegen(self, ordner, dateiname, inhalt):
        ziel = os.path.join(self.wurzel, ordner)
        os.makedirs(ziel, exist_ok=True)
        pfad = os.path.join(ziel, dateiname)
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump(inhalt, datei)
        return pfad

    def gelesen(self, rig_url):
        u"""Was unter dieser Adresse wirklich liegt."""
        pfad = Szenenstuecke._quellpfad(rig_url)
        with open(pfad, encoding='utf-8') as datei:
            return json.load(datei)


class DasNetzUeberlebtDenNaechstenBau(AblageAufProbe):

    def setUp(self):
        super().setUp()
        self.netz_anlegen('t-shirt_female', 't-shirt_female_sim_rig.json',
                          {'punkte': 'LANG'})
        self.szene = [{
            'stueck': 't-shirt',
            'rig_url': '/api/garmentcode/datei/t-shirt_female/'
                       't-shirt_female_sim_rig.json/',
            'ordner': os.path.join(self.wurzel, 't-shirt_female'),
        }]

    def test_der_zeiger_wandert_in_den_szenenordner(self):
        gesichert = Szenenstuecke.sichern('FemaleGarmentCode', self.szene)
        self.assertIn('_szene_FemaleGarmentCode', gesichert[0]['rig_url'])

    def test_und_dahinter_liegt_dasselbe_netz(self):
        gesichert = Szenenstuecke.sichern('FemaleGarmentCode', self.szene)
        self.assertEqual(self.gelesen(gesichert[0]['rig_url']),
                         {'punkte': 'LANG'})

    def test_der_naechste_bau_aendert_die_szene_nicht_mehr(self):
        u"""Der eigentliche Test — genau das ist am 09.09.2026 passiert."""
        gesichert = Szenenstuecke.sichern('FemaleGarmentCode', self.szene)
        # Ein neuer Bau ueberschreibt den Arbeitsordner.
        self.netz_anlegen('t-shirt_female', 't-shirt_female_sim_rig.json',
                          {'punkte': 'KURZ'})
        self.assertEqual(self.gelesen(gesichert[0]['rig_url']),
                         {'punkte': 'LANG'})

    def test_gegenprobe_ohne_sicherung_geht_es_verloren(self):
        u"""Sonst pruefte der Test oben nur, dass Kopieren funktioniert."""
        self.netz_anlegen('t-shirt_female', 't-shirt_female_sim_rig.json',
                          {'punkte': 'KURZ'})
        self.assertEqual(self.gelesen(self.szene[0]['rig_url']),
                         {'punkte': 'KURZ'})

    def test_zweimal_speichern_kopiert_nicht_erneut(self):
        einmal = Szenenstuecke.sichern('FemaleGarmentCode', self.szene)
        zweimal = Szenenstuecke.sichern('FemaleGarmentCode', einmal)
        self.assertEqual(einmal[0]['rig_url'], zweimal[0]['rig_url'])

    def test_zwei_szenen_stoeren_sich_nicht(self):
        eine = Szenenstuecke.sichern('FigurA', self.szene)
        self.netz_anlegen('t-shirt_female', 't-shirt_female_sim_rig.json',
                          {'punkte': 'KURZ'})
        andere = Szenenstuecke.sichern('FigurB', self.szene)
        self.assertEqual(self.gelesen(eine[0]['rig_url']), {'punkte': 'LANG'})
        self.assertEqual(self.gelesen(andere[0]['rig_url']), {'punkte': 'KURZ'})

    def test_die_uebrigen_felder_bleiben(self):
        gesichert = Szenenstuecke.sichern('FemaleGarmentCode', self.szene)
        self.assertEqual(gesichert[0]['stueck'], 't-shirt')
        self.assertEqual(gesichert[0]['ordner'], self.szene[0]['ordner'])

    def test_die_eingabe_bleibt_unberuehrt(self):
        vorher = self.szene[0]['rig_url']
        Szenenstuecke.sichern('FemaleGarmentCode', self.szene)
        self.assertEqual(self.szene[0]['rig_url'], vorher)


class WasNichtGehtBlockiertDasSpeichernNicht(AblageAufProbe):
    u"""Eine Szene, die wegen eines fehlenden Netzes gar nicht gespeichert
    wird, waere schlimmer als eine, der ein Kleidungsstueck fehlt."""

    def test_fehlendes_netz_laesst_den_zeiger_stehen(self):
        szene = [{'stueck': 'hose',
                  'rig_url': '/api/garmentcode/datei/gibt_es_nicht/x_rig.json/'}]
        gesichert = Szenenstuecke.sichern('Figur', szene)
        self.assertEqual(gesichert[0]['rig_url'], szene[0]['rig_url'])

    def test_leere_liste(self):
        self.assertEqual(Szenenstuecke.sichern('Figur', []), [])

    def test_keine_liste(self):
        self.assertIsNone(Szenenstuecke.sichern('Figur', None))

    def test_eintrag_ohne_adresse(self):
        szene = [{'stueck': 'hose'}]
        self.assertEqual(Szenenstuecke.sichern('Figur', szene), szene)

    def test_fremde_adresse_wird_nicht_angefasst(self):
        szene = [{'stueck': 'hose', 'rig_url': 'https://example.com/x.json'}]
        self.assertEqual(Szenenstuecke.sichern('Figur', szene), szene)


class NiemandKommtAusDerWurzelHeraus(AblageAufProbe):
    u"""Die Adresse kommt aus dem Browser — dieselbe Vorsicht wie in der
    Ausliefer-Route."""

    def test_punkt_punkt_wird_abgewiesen(self):
        self.assertIsNone(Szenenstuecke._quellpfad(
            '/api/garmentcode/datei/../../geheim/x_rig.json/'))

    def test_zu_wenige_teile(self):
        self.assertIsNone(Szenenstuecke._quellpfad(
            '/api/garmentcode/datei/nurordner/'))

    def test_eine_gueltige_adresse_loest_auf(self):
        pfad = Szenenstuecke._quellpfad(
            '/api/garmentcode/datei/t-shirt_female/x_rig.json/')
        self.assertTrue(Path(pfad).resolve().is_relative_to(Path(self.wurzel).resolve()), pfad)


class DerOrdnernameVertraegtAllesAusDemNamensfeld(AblageAufProbe):

    def test_leerzeichen_und_umlaute_werden_ersetzt(self):
        name = Szenenstuecke.ordnername(u'Anna Müller 2')
        self.assertTrue(name.startswith('_szene_'))
        self.assertNotIn(' ', name)

    def test_leerer_name(self):
        self.assertEqual(Szenenstuecke.ordnername(''), '_szene_unbenannt')


class GeloeschteSzenenLassenNichtsLiegen(AblageAufProbe):

    def test_der_ordner_verschwindet_mit(self):
        self.netz_anlegen('t-shirt_female', 't-shirt_female_sim_rig.json',
                          {'punkte': 'LANG'})
        Szenenstuecke.sichern('FigurX', [{
            'stueck': 't-shirt',
            'rig_url': '/api/garmentcode/datei/t-shirt_female/'
                       't-shirt_female_sim_rig.json/'}])
        ordner = os.path.join(self.wurzel, Szenenstuecke.ordnername('FigurX'))
        self.assertTrue(os.path.isdir(ordner))
        self.assertTrue(Szenenstuecke.entfernen('FigurX'))
        self.assertFalse(os.path.isdir(ordner))

    def test_ohne_ordner_passiert_nichts(self):
        self.assertFalse(Szenenstuecke.entfernen('GibtEsNicht'))

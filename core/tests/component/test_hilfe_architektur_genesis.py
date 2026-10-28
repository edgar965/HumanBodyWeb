# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> Genesis: die Seite steht, hängt im Menü, und jeder genannte Baustein gibt es im Code.

WARUM (Edgar, 08.10.2026: „schreibe das hinein in eine neue Seite Hilfe - Architektur - Genesis"): Die Seite trägt das
Konzept zum Blender-Import und nennt die Klassen, auf die es aufsetzt. Eine Architekturseite mit Klassen, die es nicht
mehr gibt, ist schlimmer als keine — die Tabelle prüft beim Aufruf, dieser Test hält es fest.
"""

from django.test import Client, SimpleTestCase
from django.urls import reverse

from core.dienste.architekturgenesis import Architekturgenesis


class SeiteArchitekturGenesis(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.antwort = Client().get(reverse('hilfe_architektur_genesis'))
        cls.text = cls.antwort.content.decode('utf-8')

    def test_antwortet_und_haengt_im_menue(self):
        self.assertEqual(self.antwort.status_code, 200)
        self.assertEqual(reverse('hilfe_architektur_genesis'), '/hilfe/architektur/genesis/')
        self.assertIn('href="/hilfe/architektur/genesis/"', self.text)

    def test_jeder_baustein_gibt_es_im_code(self):
        for zeile in Architekturgenesis.bausteine() + Architekturgenesis.fitting():
            self.assertEqual(zeile['fehlt'], '', zeile['pfad'])
            self.assertGreater(zeile['zeilen'], 0, zeile['pfad'])

    def test_ein_fehlender_baustein_wird_gemeldet(self):
        """Gegenprobe: eine erfundene Klasse in einer echten Datei muss als fehlend erscheinen."""
        zeile = Architekturgenesis.zeile('Genesis9/eigenstueck.py', 'GibtEsNicht', '')
        self.assertEqual(zeile['fehlt'], 'Klasse fehlt')

    def test_der_fitting_abschnitt_steht_auf_der_seite(self):
        """11.10.2026: das Fitting der Kleider mit der Scham — Abschnitt, Bausteine-Tabelle und die Messreihe."""
        for satz in ('10. Fitting der Kleider', 'architekturGenesisFitting', 'G9stueckstarr', 'hidden_polys', 'Collision-Durchgänge'):
            self.assertIn(satz, self.text)

    def test_inhaltsverzeichnis_zeigt_auf_jede_ueberschrift(self):
        """28.10.2026, Edgar: „mach auch ein Inhaltsverzeichnis am Anfang dieser Seite mit den Überschriften“ — jeder Verweis hat sein Ziel."""
        import re
        ziele = set(re.findall(r'href="#([\w-]+)"', self.text.split('class="ag-inhalt"', 1)[1].split('</nav>', 1)[0]))
        self.assertGreaterEqual(len(ziele), 20)
        for ziel in ziele:
            self.assertIn('id="%s"' % ziel, self.text, ziel)

    def test_modell_und_mesh_stehen_auf_der_seite(self):
        """28.10.2026: das Genesis-Modell (Rig, Regler, Vergleich) und Mesh → Genesis mit Quellen und Lizenzen; die Mesh-Bausteine gibt es im Code."""
        for satz in ('138 Knochen', 'Vergleich mit den anderen Körpermodellen', 'fit_SMPL_IPNet.py', 'transfer_model', 'torch-trust-ncg', 'Apache 2.0',
                     'architekturGenesisMesh', 'G9meshipnet', 'G9meshtransfer'):
            self.assertIn(satz, self.text)
        for zeile in Architekturgenesis.mesh():
            self.assertEqual(zeile['fehlt'], '', zeile['pfad'])

    def test_die_entscheidungen_stehen_auf_der_seite(self):
        for satz in ('Entscheidungen (Edgar, 08.10.2026)', 'Strg+Alt+H', 'eigen:cute girl'):
            self.assertIn(satz, self.text)

# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> 2D3D, Reiter „MeshTo3D": Schritte, Klassenmodell und die Aussage „Mesh to 3D startet kein Blender" stehen auf der Seite und stimmen mit dem Code.

WARUM (Edgar, 11.10.2026: „füge diese Info hinzu in /hilfe/architektur/2d3d/ in neuem Tab - MeshTo3D … Auch Klassenmodell, Workflow und so weiter"): Ein Reiter, dessen Text hinter dem Code
zurückbleibt, sieht aus wie fertig. Die Tests halten fest: der Reiter steht im HTML und lässt sich über die Adresse (`#meshto3d`) wählen; die Schritte der Seite sind die von `Meshfigurlauf`
und die Schritte des Imports die von `Blendimportlauf` (neuer Schritt im Code ohne Text = Befund, kein stilles Weglassen); jede Klasse des Modells hat ihre Karte und jeder Verweis der Schrittetabelle
trifft einen Anker; die Beziehungen nennen nur Klassen des Modells; und die Aussage „kein Blender" hängt an einer Prüfung: kein Modul der Gruppen `eingang` bis `genesis` importiert `Blendimportblender`.
Geschrieben 11.10.2026, NICHT gelaufen (Tests nur auf Ansage)."""

import re
from pathlib import Path

from django.conf import settings
from django.test import Client, SimpleTestCase
from django.urls import reverse

from core.dienste.architekturmeshto3d import Architekturmeshto3d
from core.dienste.architekturmeshto3dklassen import Architekturmeshto3dklassen
from core.dienste.architekturmeshto3dschritte import Architekturmeshto3dschritte


class SeiteMeshTo3d(SimpleTestCase):
    #: Keine Datenbank: die Zeiten (fertige Aufträge) sind dann leer und sagen es — `Architekturmeshto3dzeiten.lesen` fängt den Zugriff ab; die Tests prüfen den Rest.
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.text = Client().get(reverse('hilfe_architektur_2d3d')).content.decode('utf-8')
        cls.kontext = Architekturmeshto3d.kontext()

    def test_der_reiter_steht_im_html_mit_knopf_und_flaeche(self):
        self.assertIn('data-ziel="meshto3d"', self.text)
        self.assertIn('data-reiter="meshto3d"', self.text)
        self.assertIn('Mesh to 3D: wie aus einem Menschen-Netz eine Genesis-9-Figur wird', self.text)

    def test_der_reiter_meldet_keine_befunde(self):
        self.assertEqual(self.kontext['befunde'], [], 'Text und Code stimmen nicht überein: %s' % self.kontext['befunde'])
        self.assertNotIn('Der Reiter konnte nicht gebaut werden', self.text)

    def test_die_schritte_der_seite_sind_die_von_meshfigurlauf(self):
        from core.dienste.meshfigurlauf import Meshfigurlauf

        self.assertEqual([s['schritt'] for s in self.kontext['schritte']], list(Meshfigurlauf.SCHRITTE))
        self.assertEqual({s[0] for s in Architekturmeshto3dschritte.SCHRITTE}, set(Meshfigurlauf.SCHRITTE))
        for s in self.kontext['schritte']:
            self.assertEqual((s['von'], s['bis']), tuple(Meshfigurlauf.BAENDER[s['schritt']]))

    def test_die_importschritte_der_seite_sind_die_von_blendimportlauf(self):
        from core.dienste.blendimportlauf import Blendimportlauf

        self.assertEqual({s['schritt'] for s in self.kontext['blender']['schritte']}, set(Blendimportlauf.SCHRITTE))

    def test_jede_klasse_hat_eine_karte_und_einen_anker(self):
        for g in self.kontext['klassen']['gruppen']:
            self.assertIn('id="tm-meshto3d-%s"' % g['kennung'], self.text)
            for k in g['karten']:
                self.assertIn('id="%s"' % k['anker'], self.text)
                self.assertEqual(k['fehlt'], '', '%s: %s' % (k['klasse'], k['fehlt']))

    def test_jeder_verweis_der_seite_trifft_einen_anker(self):
        flaeche = self.text.split('data-reiter="meshto3d"', 1)[1]
        ids = set(re.findall(r'\bid="([^"]+)"', self.text))
        ziele = set(re.findall(r'href="#(t[m]?-meshto3d-[^"]+|m3-[^"]+)"', flaeche))
        self.assertTrue(ziele)
        self.assertEqual(sorted(z for z in ziele if z not in ids), [])

    def test_die_beziehungen_nennen_nur_klassen_des_modells(self):
        bekannt = set(Architekturmeshto3dklassen.gruppe_von())
        for von, _wie, nach, _womit in Architekturmeshto3dklassen.alle_beziehungen():
            self.assertIn(von, bekannt)
            self.assertIn(nach, bekannt)

    def test_kein_modul_der_mesh_to_3d_gruppen_startet_blender(self):
        """Die Aussage „Mesh to 3D startet kein Blender" (Kurzfassung des Reiters) hängt an dieser Prüfung. Ausgenommen die Gruppe „Wer Mesh to 3D benutzt": der Blender-Import."""
        wurzel = Path(settings.TOOLS_ROOT)
        for kennung, _titel, _hinweis, rollen in Architekturmeshto3dklassen.GRUPPEN:
            if kennung == 'verwender':
                continue
            for _rolle, klassen in rollen:
                for datei, klasse in klassen:
                    quelltext = (wurzel / datei).read_text(encoding='utf-8')
                    for verboten in ('BLENDER_EXE', 'Blendimportblender', 'import bpy'):
                        self.assertNotIn(verboten, quelltext, '%s (%s) nennt %s' % (klasse, datei, verboten))

    def test_die_aussage_kein_blender_steht_auf_der_seite(self):
        self.assertIn('Mesh to 3D selbst startet', self.text)
        self.assertIn('Blendimportlauf.SCHRITTE', self.text)

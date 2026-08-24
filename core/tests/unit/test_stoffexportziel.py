# -*- coding: utf-8 -*-
"""Stoffexportziel — Pfadprüfungen des Kleider-Exports.

WARUM (17.08.2026)
=================
`export_cloth` war 93 Zeilen, und in der Mitte steckten drei Sicherheitsprüfungen
(Zielordner, Dateiname, Szenenname). Der Endpunkt selbst braucht Blender und ist
deshalb nicht prüfbar; diese Klasse ist es.

DER FALL AUS DER VORGESCHICHTE (Review 15.08.2026)
=================================================
Vorher stand dort `scene_name.replace('/', '_')` — nur der Schrägstrich, nicht
der Backslash, mit dem Windows Verzeichnisse trennt:

    '..\\..\\..\\evil'  ->  A:\\3DTools\\evil_blender_eevee_….mp4
    'C:\\evil'          ->  C:\\evil_blender_eevee_….mp4   (absolut ersetzt Basis)

Seither Positivliste. Genau diese zwei Eingaben stehen unten im Test.

Der Motorname im Dateinamen ist kein Schmuck: Zwei Motoren auf derselben Szene
würden sonst in dieselbe Datei schreiben, und das Ergebnis wäre je nach
Reihenfolge ein anderes.
"""

from django.test import SimpleTestCase, TestCase, override_settings

from core.dienste.stoffexportziel import Stoffexportziel
from core.safe_paths import PfadAbgelehnt


class ExportNamensstammTest(SimpleTestCase):

    def stamm(self, name):
        return Stoffexportziel({'scene_name': name}, 'warp_only').namensstamm()

    def test_pfadtrenner_werden_ersetzt(self):
        self.assertEqual(self.stamm('..\\..\\..\\evil'), 'evil')
        # Doppelpunkt UND Backslash sind je ein Unterstrich, deshalb zwei.
        self.assertEqual(self.stamm('C:\\evil'), 'C__evil')
        self.assertEqual(self.stamm('a/b'), 'a_b')

    def test_leerzeichen_wird_ersetzt_nicht_abgelehnt(self):
        """Der Name kommt aus einem Textfeld — ein Export darf nicht scheitern."""
        self.assertEqual(self.stamm('Mein Rock'), 'Mein_Rock')

    def test_umlaute_bleiben_stehen(self):
        """`ö`.isalnum() ist wahr — und im Dateinamen ist ein Umlaut harmlos.

        Das ist absichtlich so: Die Positivliste verbietet Pfad- und
        Steuerzeichen, nicht Buchstaben. Und die Hausregel für Dateinamen sagt
        ASCII für Bezeichner, nicht für Nutzereingaben.
        """
        self.assertEqual(self.stamm('Röckchen'), 'Röckchen')

    def test_leerer_name_bekommt_einen_ersatz(self):
        for leer in ('', '   ', '///', None):
            self.assertEqual(self.stamm(leer), 'scene', repr(leer))

    def test_stamm_wird_gekuerzt(self):
        self.assertEqual(len(self.stamm('a' * 200)), 60)


class DateinameTest(SimpleTestCase):

    def test_motorname_steht_im_dateinamen(self):
        ziel = Stoffexportziel({'filename': 'rock.mp4'}, 'warp_only')
        self.assertEqual(ziel.dateiname(), 'rock_warp_only.mp4')

    def test_zwei_motoren_zwei_dateien(self):
        rumpf = {'filename': 'rock.mp4'}
        self.assertNotEqual(Stoffexportziel(rumpf, 'warp_only').dateiname(),
                            Stoffexportziel(rumpf, 'blender_eevee').dateiname())

    def test_ohne_namen_kommt_szene_zeit_und_zufall(self):
        ziel = Stoffexportziel({'scene_name': 'Mein Rock'}, 'warp_only',
                               jetzt=1000)
        name = ziel.dateiname()
        self.assertTrue(name.startswith('Mein_Rock_warp_only_1000_'), name)
        self.assertTrue(name.endswith('.mp4'))

    def test_zwei_exporte_derselben_szene_ueberschreiben_sich_nicht(self):
        ziel = Stoffexportziel({'scene_name': 'Rock'}, 'warp_only', jetzt=1000)
        self.assertNotEqual(ziel.dateiname(), ziel.dateiname())

    def test_boeser_dateiname_wird_abgelehnt(self):
        """Hier wird NICHT bereinigt: Ein Dateiname kommt aus dem Programm."""
        for boese in ('..\\..\\x.mp4', 'C:\\x.mp4', 'video:1.mp4', '-i.mp4',
                      'NUL.mp4'):
            with self.assertRaises(PfadAbgelehnt, msg=boese):
                Stoffexportziel({'filename': boese}, 'warp_only').dateiname()

    def test_falsche_endung_wird_ergaenzt_nicht_abgelehnt(self):
        """`SafePath.dateiname` hängt die Endung an — der Motor schreibt MP4.

        Das ist kein Sicherheitsloch: Die Datei heißt danach `x.exe.mp4` und
        liegt im Ausgabeordner. Abzulehnen wäre strenger, als der Fall hergibt.
        """
        ziel = Stoffexportziel({'filename': 'x.exe'}, 'warp_only')
        self.assertEqual(ziel.dateiname(), 'x.exe_warp_only.mp4')


class OrdnerTest(TestCase):
    """`TestCase`, nicht `SimpleTestCase`: `SafePath.fuer_ausgabe()` liest die
    Einstellungen (die erlaubten Wurzeln) aus der Datenbank. Ohne Datenbank fing
    SafePath den Zugriffsfehler ab und arbeitete mit weniger Wurzeln — der Test
    war grün, prüfte aber nicht die echte Lage."""

    def test_ohne_wunsch_gilt_die_vorgabe(self):
        ziel = Stoffexportziel({}, 'warp_only')
        self.assertEqual(ziel.ordner('A:/vorgabe'), 'A:/vorgabe')

    def test_ausbruch_wird_abgelehnt(self):
        ziel = Stoffexportziel({'output_dir': '..\\..\\..\\Windows'}, 'warp_only')
        with self.assertRaises(PfadAbgelehnt):
            ziel.ordner('A:/vorgabe')


class AdresseTest(SimpleTestCase):

    @override_settings(MEDIA_ROOT='A:/3DTools/HumanBodyWeb/media',
                       MEDIA_URL='/media/')
    def test_datei_unter_media_bekommt_eine_url(self):
        self.assertEqual(
            Stoffexportziel.adresse('A:/3DTools/HumanBodyWeb/media/x/y.mp4'),
            '/media/x/y.mp4')

    @override_settings(MEDIA_ROOT='A:/3DTools/HumanBodyWeb/media',
                       MEDIA_URL='/media/')
    def test_datei_ausserhalb_bekommt_keine(self):
        """Eine erfundene URL wäre ein toter Link."""
        self.assertIsNone(Stoffexportziel.adresse('D:/studio/y.mp4'))


class AufloesungTest(SimpleTestCase):

    def test_werte_aus_dem_rumpf(self):
        ziel = Stoffexportziel({'width': '640', 'height': '480'}, 'warp_only')
        self.assertEqual(ziel.aufloesung(), (640, 480))

    def test_unbrauchbare_werte_fallen_auf_die_vorgabe(self):
        ziel = Stoffexportziel({'width': 'viel'}, 'warp_only')
        self.assertEqual(ziel.aufloesung(), (1920, 1080))

    def test_zu_kleine_werte_werden_angehoben(self):
        """0x0 würde den Renderer zum Absturz bringen."""
        ziel = Stoffexportziel({'width': 0, 'height': 1}, 'warp_only')
        self.assertEqual(ziel.aufloesung(), (1920, 64))

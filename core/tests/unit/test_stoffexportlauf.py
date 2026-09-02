# -*- coding: utf-8 -*-
"""Stoffexportlauf und Bereichsstoff — zwei Klassen ohne Test (27.08.2026).

Das Werkzeug `testdeckung` meldete beide als „liegt auf einem Arbeitsweg, wird
aber in keinem Test erwähnt". Geprüft wird, was den Endpunkt lenkt, nicht die
Rechnung darunter:

* `Stoffexportlauf` entscheidet, WELCHE Antwort der Aufrufer bekommt — 400 bei
  unbekanntem Motor, 403 bei abgelehntem Pfad, 500 bei fehlendem Paket. Diese
  Statuscodes sind die Schnittstelle; die Rechnung macht `collision`.
* `Bereichsstoff` liest die Regler der Anfrage. Ein Wert, den ein Regler nicht
  liefern kann, darf keine Fehlerseite ergeben.

Kein `collision`-Import: Das Paket liegt in HumanBody und braucht Blender bzw.
Warp. Geprüft wird die Schale davor.
"""

from django.test import SimpleTestCase, TestCase

from core.api.bereichsstoff import Bereichsstoff
from core.dienste.stoffexportlauf import Stoffexportlauf


class MotorwahlTest(SimpleTestCase):
    """Ein unbekannter Motorname darf nicht bis `export_mp4` durchkommen."""

    def test_bekannter_motor_gibt_keine_fehlerantwort(self):
        for motor in Stoffexportlauf.motoren():
            with self.subTest(motor=motor):
                lauf = Stoffexportlauf({'engine': motor})
                self.assertIsNone(lauf.motorfehler())

    def test_unbekannter_motor_gibt_400_mit_namen(self):
        antwort = Stoffexportlauf({'engine': 'raytracer9000'}).motorfehler()
        self.assertIsNotNone(antwort)
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('raytracer9000', antwort.content.decode())

    def test_ohne_angabe_gilt_der_ersatzmotor(self):
        lauf = Stoffexportlauf({})
        self.assertEqual(lauf.motor, Stoffexportlauf.ERSATZMOTOR)
        self.assertIsNone(lauf.motorfehler(),
                          'der Ersatzmotor muss selbst zulaessig sein')

    def test_ohne_angabe_gilt_die_ersatzguete(self):
        self.assertEqual(Stoffexportlauf({}).guete,
                         Stoffexportlauf.ERSATZGUETE)


class AusgabeordnerTest(TestCase):
    """Der eingestellte Ordner gilt nur, wenn es ihn WIRKLICH gibt."""

    def test_ohne_einstellung_der_ersatzordner(self):
        from django.conf import settings
        from core.daten.pfadvergleich import Pfadvergleich
        ordner = Stoffexportlauf.ausgabeordner()
        # `Pfadvergleich` statt `startswith`: Der Zeichenvergleich ist genau
        # der Fehler, den das Werkzeug `pfadpraefix` sucht — er hat auch in
        # einer Zusicherung nichts zu suchen.
        self.assertTrue(Pfadvergleich.liegt_unter(ordner, settings.MEDIA_ROOT),
                        ordner)
        self.assertTrue(ordner.endswith(Stoffexportlauf.ERSATZORDNER), ordner)

    def test_eingestellter_ordner_der_nicht_existiert_wird_uebergangen(self):
        """Sonst schriebe der Export ins Leere und meldete trotzdem Erfolg."""
        from core.models import AppSettings
        stand = AppSettings.load()
        stand.ui_prefs = {'studio_video_output': 'A:/gibtesnicht/xyz'}
        stand.save()
        try:
            self.assertTrue(
                Stoffexportlauf.ausgabeordner().endswith(
                    Stoffexportlauf.ERSATZORDNER))
        finally:
            stand.ui_prefs = {}
            stand.save()


class StoffexportZielpfadTest(TestCase):
    """Pfad und Dateiname kommen aus dem Anfragerumpf — beide werden geprüft."""

    def test_ausgabepfad_ausserhalb_wird_abgelehnt(self):
        lauf = Stoffexportlauf({'output_dir': 'C:/Windows/Temp',
                                'scene_name': 'x'})
        pfad, antwort = lauf.zielpfad()
        self.assertIsNone(pfad)
        self.assertEqual(antwort.status_code, 403)

    def test_gueltiger_lauf_liefert_einen_pfad(self):
        pfad, antwort = Stoffexportlauf({'scene_name': 'Ballett Probe'}).zielpfad()
        self.assertIsNone(antwort, getattr(antwort, 'content', None))
        self.assertIn('Ballett_Probe', pfad)
        self.assertTrue(pfad.endswith('.mp4'), pfad)


class BereichsstoffReglerTest(SimpleTestCase):
    """Was der Nutzer am Regler einstellt — und was ohne Angabe gilt."""

    def test_werte_aus_der_anfrage(self):
        stoff = Bereichsstoff({'z_min': '0.6', 'z_max': '1.2',
                               'include_arms': '1', 'grow': '4',
                               'looseness': '0.8', 'category': 'Tops'})
        self.assertAlmostEqual(stoff.von, 0.6)
        self.assertAlmostEqual(stoff.bis, 1.2)
        self.assertTrue(stoff.mit_armen)
        self.assertEqual(stoff.wachsen, 4)
        self.assertAlmostEqual(stoff.weite, 0.8)
        self.assertEqual(stoff.kategorie, 'Tops')

    def test_vorgaben_ohne_angabe(self):
        stoff = Bereichsstoff({})
        self.assertAlmostEqual(stoff.von, 0.0)
        self.assertAlmostEqual(stoff.bis, 1.0)
        self.assertFalse(stoff.mit_armen)
        self.assertEqual(stoff.wachsen, 2)
        self.assertIsNone(stoff.kategorie)

    def test_arme_nur_bei_genau_eins(self):
        """`include_arms` kommt als Zeichenkette — `'true'` ist NICHT `'1'`."""
        for wert, erwartet in (('1', True), ('0', False), ('true', False),
                               ('', False)):
            with self.subTest(wert=wert):
                self.assertIs(
                    Bereichsstoff({'include_arms': wert}).mit_armen, erwartet)

    def test_zweiter_abstand_waechst_mit_der_weite(self):
        """Der zweite Schub faengt die Laplace-Glaettung ein (Modul-Docstring).

        Er MUSS mit der Weite wachsen: Ein weites Stueck wird staerker
        geglaettet und zieht sich an Brust, Knie und Schulter weiter nach
        innen.
        """
        eng = Bereichsstoff({'looseness': '0.0'})
        weit = Bereichsstoff({'looseness': '1.0'})
        abstand = (lambda s: s.GRUNDABSTAND + s.weite * s.WEITENANTEIL)
        self.assertAlmostEqual(abstand(eng), Bereichsstoff.GRUNDABSTAND)
        self.assertGreater(abstand(weit), abstand(eng))

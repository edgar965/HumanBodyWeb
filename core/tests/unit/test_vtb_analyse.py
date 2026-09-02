# -*- coding: utf-8 -*-
u"""Die Foto-Analyse von VideoToBVH: Backendpruefung, Unterlauf, Masse.

DER ANLASS (01.09.2026)
=======================
Drei Backends fuehrten ihre Voraussetzungspruefung je ZWEIMAL — einmal
als `is_available()` ohne Text, einmal als `get_status()` mit Text.
Sechs Kopien derselben Kette, und nichts hielt sie zusammen: Wer eine
Bedingung nur in einer der beiden ergaenzt, bekommt ein Backend, das
„bereit" meldet und beim ersten Foto scheitert. Genau das prueft
`DieBackendpruefung`.

Dazu die zweite Doppelung: `analyze()` stand dreimal wortgleich, rund
40 Zeilen mit vier Fehlerzweigen. `DerUnterlauf` geht sie einzeln
durch — das ist der Teil, den ein Betriebslauf nie erreicht, weil er
nur bei kaputter Umgebung greift.

BDD - GEGEBEN / DANN
====================
    DieBackendpruefung  ... beantwortet beide Fragen aus einer Liste
    DerUnterlauf        ... findet das JSON und meldet jeden Fehlerfall
    DieKoerpermasse     ... traegt sechs Laengen in Metern
    DieBackendliste     ... nennt fuer jedes Backend ein ladbares Modul
"""
import json
import os
import unittest

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from backendpruefung import Backendpruefung                 # noqa: E402
from koerpermasse import Koerpermasse                       # noqa: E402
from photo_analyzer import Fotobackends                     # noqa: E402
from unterlauf import Unterlauf                             # noqa: E402


class DieBackendpruefung(unittest.TestCase):
    u"""Eine Liste, zwei Antworten — sie koennen nicht auseinanderlaufen."""

    def _pruefung(self, ordner, dateien=()):
        bedingungen = [Backendpruefung.ordner(ordner, 'Ordner fehlt')]
        for pfad, text in dateien:
            bedingungen.append(Backendpruefung.datei(pfad, text))
        return Backendpruefung('Probe', bedingungen, 'alles da')

    def test_alles_da(self):
        with Pruefablage.ordner() as ordner:
            datei = os.path.join(ordner, 'gewicht.bin')
            open(datei, 'w').close()
            pruefung = self._pruefung(ordner, [(datei, 'Gewicht fehlt')])
            self.assertTrue(pruefung.bereit())
            self.assertEqual(pruefung.stand(),
                             {'available': True, 'info': 'alles da'})

    def test_der_erste_mangel_wird_genannt(self):
        with Pruefablage.ordner() as ordner:
            pruefung = self._pruefung(
                ordner, [(os.path.join(ordner, 'fehlt.bin'), 'Gewicht fehlt')])
            self.assertFalse(pruefung.bereit())
            self.assertEqual(pruefung.stand()['info'], 'Gewicht fehlt')

    def test_die_reihenfolge_entscheidet(self):
        u"""Fehlt der Ordner, ist die Datei darin kein sinnvoller Hinweis."""
        pruefung = self._pruefung('/gibt/es/nicht',
                                  [('/gibt/es/nicht/x.bin', 'Gewicht fehlt')])
        self.assertEqual(pruefung.stand()['info'], 'Ordner fehlt')

    def test_beide_antworten_stimmen_immer_ueberein(self):
        u"""Der eigentliche Befund: zwei Ketten, die auseinanderlaufen."""
        with Pruefablage.ordner() as ordner:
            datei = os.path.join(ordner, 'gewicht.bin')
            pruefung = self._pruefung(ordner, [(datei, 'Gewicht fehlt')])
            for vorhanden in (False, True):
                if vorhanden:
                    # in der Schleife gewollt: Genau der Wechsel ist der
                    # Gegenstand — erst fehlt die Datei, dann liegt sie da.
                    open(datei, 'w').close()
                with self.subTest(datei_da=vorhanden):
                    self.assertEqual(pruefung.bereit(),
                                     pruefung.stand()['available'])

    def test_eine_von_mehreren_dateien_genuegt(self):
        u"""SMPLest-X legt seine Konfiguration an zwei moeglichen Orten ab."""
        with Pruefablage.ordner() as ordner:
            a = os.path.join(ordner, 'a.py')
            b = os.path.join(ordner, 'b.py')
            pruefung = Backendpruefung('Probe', (
                Backendpruefung.eine_von((a, b), 'Konfiguration fehlt'),))
            self.assertFalse(pruefung.bereit())
            open(b, 'w').close()
            self.assertTrue(pruefung.bereit())

    def test_jedes_echte_backend_antwortet_stimmig(self):
        u"""Auch wenn nichts installiert ist: die zwei Antworten passen."""
        for name in ('smplest_x', 'pymafx', 'hmr2'):
            with self.subTest(backend=name):
                modul = Fotobackends.laden(name)
                self.assertIsNotNone(modul)
                stand = modul.get_status()
                self.assertEqual(modul.is_available(), stand['available'])
                self.assertTrue(stand['info'])


class DerUnterlauf(unittest.TestCase):
    u"""Die Fehlerzweige, die im Betrieb nie vorkommen — bis sie es tun."""

    class Lauf:
        u"""Was `subprocess.run` zurueckgibt, nachgebildet."""

        def __init__(self, stdout='', stderr=''):
            self.stdout, self.stderr = stdout, stderr

    def _lauf(self):
        return Unterlauf('Probe', 'python.exe', 'runner.py', '.')

    def test_die_letzte_json_zeile_gilt(self):
        u"""ML-Bibliotheken schreiben ungefragt auf stdout."""
        text = ('Lade Modell...\n{"betas": [1]}\nWarnung: irgendwas\n'
                '{"betas": [2], "gender": "female"}\nfertig')
        daten = self._lauf()._auswerten(self.Lauf(text))
        self.assertEqual(daten['betas'], [2])

    def test_keine_ausgabe_ist_ein_fehler(self):
        self.assertIsNone(self._lauf()._auswerten(
            self.Lauf('', 'ImportError: kein torch')))

    def test_ausgabe_ohne_json_ist_ein_fehler(self):
        self.assertIsNone(self._lauf()._auswerten(
            self.Lauf('Lade Modell...\nAbbruch')))

    def test_kaputtes_json_ist_ein_fehler(self):
        self.assertIsNone(self._lauf()._auswerten(
            self.Lauf('{"betas": [1,,]}')))

    def test_ein_gemeldeter_fehler_ist_kein_ergebnis(self):
        u"""Der Runner meldet Fehler selbst als JSON."""
        self.assertIsNone(self._lauf()._auswerten(
            self.Lauf(json.dumps({'error': 'Keine Person erkannt'}))))

    def test_ein_fehlendes_bild_startet_nichts(self):
        self.assertIsNone(self._lauf().analysieren('/gibt/es/nicht.jpg'))

    def test_ein_fehlender_interpreter_stuerzt_nicht_ab(self):
        with Pruefablage.datei('x', endung='.jpg') as pfad:
            lauf = Unterlauf('Probe', 'C:/gibt/es/nicht.exe', 'r.py', '.')
            self.assertIsNone(lauf.analysieren(pfad))


class DieKoerpermasse(unittest.TestCase):
    u"""Sechs Laengen in Metern — die Zentimeter entstehen erst zuletzt."""

    def _masse(self):
        return Koerpermasse(hoehe=1.72, schulterbreite=0.32,
                            hueftbreite=0.12, rumpflaenge=0.46,
                            beinlaenge=0.78, armlaenge=0.52)

    def test_als_cm_liefert_sechs_felder(self):
        cm = self._masse().als_cm()
        self.assertEqual(len(cm), 6)
        self.assertEqual(cm['height_cm'], 172.0)

    def test_die_feldnamen_sind_die_des_frontends(self):
        self.assertEqual(set(self._masse().als_cm()),
                         {'height_cm', 'shoulder_cm', 'hip_cm', 'torso_cm',
                          'leg_cm', 'arm_cm'})

    def test_anteile_sind_groessenfrei(self):
        u"""Ein doppelt so grosser Mensch hat dieselben Verhaeltnisse."""
        klein = self._masse()
        gross = Koerpermasse(hoehe=3.44, schulterbreite=0.64,
                             hueftbreite=0.24, rumpflaenge=0.92,
                             beinlaenge=1.56, armlaenge=1.04)
        for a, b in zip(klein.anteile(), gross.anteile()):
            self.assertAlmostEqual(a, b, places=12)

    def test_sechs_anteile_in_fester_ordnung(self):
        from koerperanteile import Koerperanteile
        self.assertEqual(len(self._masse().anteile()),
                         len(Koerperanteile.SCHLUESSEL))

    def test_nullhoehe_ergibt_keine_division(self):
        leer = Koerpermasse(0, 0, 0, 0, 0, 0)
        self.assertEqual(leer.anteile(), [0.0] * 6)


class DieBackendliste(unittest.TestCase):
    u"""Vier Backends, vier ladbare Module, vier vollstaendige Antworten."""

    def test_jedes_backend_hat_die_drei_namen(self):
        for name in Fotobackends.EINTRAEGE:
            with self.subTest(backend=name):
                modul = Fotobackends.laden(name)
                self.assertIsNotNone(modul, '%s nicht ladbar' % name)
                for gebraucht in ('is_available', 'get_status', 'analyze'):
                    self.assertTrue(hasattr(modul, gebraucht))

    def test_die_uebersicht_ist_vollstaendig(self):
        from photo_analyzer import get_all_status
        stand = get_all_status()
        self.assertEqual(set(stand), set(Fotobackends.EINTRAEGE))
        for name, eintrag in stand.items():
            with self.subTest(backend=name):
                for feld in ('label', 'desc', 'available', 'info',
                             'quality', 'model_type'):
                    self.assertIn(feld, eintrag)

    def test_ein_unbekanntes_backend_gibt_nichts(self):
        self.assertIsNone(Fotobackends.laden('gibtesnicht'))

    def test_pflichtfelder_werden_nachgetragen(self):
        u"""Sonst muesste das Frontend jedes Feld einzeln absichern."""
        ergebnis = Fotobackends.vervollstaendigen({'betas': [0.0]}, 'hmr2')
        self.assertEqual(ergebnis['expression'], [])
        self.assertFalse(ergebnis['mock'])
        self.assertIsNone(ergebnis['measurements'])
        self.assertEqual(ergebnis['backend'], 'hmr2')

    def test_vorhandene_felder_bleiben_stehen(self):
        ergebnis = Fotobackends.vervollstaendigen(
            {'mock': True, 'backend': 'mediapipe'}, 'hmr2')
        self.assertTrue(ergebnis['mock'])
        self.assertEqual(ergebnis['backend'], 'mediapipe')

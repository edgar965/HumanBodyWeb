# -*- coding: utf-8 -*-
u"""Eigene Vorbilder der Kleiderbibliothek — Leggings (11.09.2026).

Edgar: „mach fuer leggins eine Voreinstellung fuer kleiderbibliothek, mit
Icon". Geprueft wird, was still kaputtgehen kann:

* Der Eintrag steht in der Liste der Hose — ZUERST, mit Bildadresse.
* Jeder Schnittwert zeigt auf einen echten Hosenregler und liegt in
  dessen Bereich; jeder Bauwert ist in `Passformpresets.BAU_PFADE`
  angemeldet (sonst wuerde ihn das Frontend stumm verwerfen).
* Das Icon liegt als Datei da und kommt ueber den Endpunkt — und der
  Endpunkt gibt fuer einen fremden Pfad 404, nicht die Datei.
"""
import os

from django.test import SimpleTestCase
from django.urls import reverse

from GarmentCode.eigenevorbilder import BILDORDNER, EIGENE
from GarmentCode.katalog import Katalog
from GarmentCode.passform import Passformpresets
from GarmentCode.vorbildpresets import Vorbildpresets


class EigeneVorbilderTest(SimpleTestCase):

    databases = set()

    def _leggings(self):
        liste = Vorbildpresets.fuer('hose')
        self.assertTrue(liste)
        return liste[0]

    def test_leggings_stehen_zuerst_mit_bild(self):
        erst = self._leggings()
        self.assertEqual(erst['titel'], 'Leggings')
        self.assertEqual(erst['schluessel'], 'vorbild_eigen_leggings')
        self.assertEqual(erst['bildadresse'], '/api/garmentcode/vorbildbild/leggings.png/')
        self.assertEqual(erst['werte']['bau.anliegen_mm'], 2.0)
        self.assertIn('Leggings', [v['titel'] for v in Vorbildpresets.fuer('hose')])
        self.assertGreaterEqual(Vorbildpresets.anzahl(), len(Vorbildpresets.fuer('hose')))

    def test_jeder_wert_ist_ein_regler_oder_bauwert(self):
        bereiche = self._bereiche('hose')
        for vorlage, eintraege in EIGENE.items():
            for eintrag in eintraege:
                for pfad, wert in eintrag['werte'].items():
                    if pfad.startswith('bau.'):
                        self.assertIn(pfad, Passformpresets.BAU_PFADE)
                        continue
                    self.assertIn(pfad, bereiche, '%s: %s gibt es nicht' % (vorlage, pfad))
                    bereich = bereiche[pfad]
                    if isinstance(wert, (int, float)):
                        unten, oben = bereich
                        self.assertGreaterEqual(wert, unten, pfad)
                        self.assertLessEqual(wert, oben, pfad)
                    else:
                        # Auswahl (`select_null`): der Wert muss in der Liste stehen.
                        self.assertIn(wert, bereich, pfad)

    def test_bild_liegt_da_und_kommt_ueber_den_endpunkt(self):
        for eintraege in EIGENE.values():
            for eintrag in eintraege:
                pfad = os.path.join(BILDORDNER, eintrag['bild'])
                self.assertTrue(os.path.isfile(pfad), pfad)
                with open(pfad, 'rb') as datei:
                    self.assertEqual(datei.read(8), b'\x89PNG\r\n\x1a\n')
                antwort = self.client.get(
                    reverse('garmentcode_vorbildbild', args=[eintrag['bild']]))
                self.assertEqual(antwort.status_code, 200)
                self.assertEqual(antwort['Content-Type'], 'image/png')
                antwort.close()

    def test_fremder_name_gibt_404(self):
        for name in ('nichtda.png', '..', 'x'):
            antwort = self.client.get(
                reverse('garmentcode_vorbildbild', args=[name]))
            self.assertEqual(antwort.status_code, 404, name)
        self.assertIsNone(Vorbildpresets.bildpfad('../eigenevorbilder.py'))

    def test_die_passform_kennt_den_bauwert(self):
        u"""Das Passform-Preset „Leggings" traegt denselben Bauwert."""
        presets = Katalog.passform('hose')
        leggings = [p for p in presets if p['titel'] == 'Leggings']
        self.assertEqual(len(leggings), 1, [p['titel'] for p in presets])
        self.assertEqual(leggings[0]['werte']['bau.anliegen_mm'], 2.0)
        self.assertIn('pants.flare', leggings[0]['werte'])

    def _bereiche(self, vorlage):
        werte = {}

        def sammeln(gruppen):
            for gruppe in gruppen:
                for feld in gruppe.get('felder', ()):
                    bereich = feld.get('bereich')
                    if isinstance(bereich, (list, tuple)) and bereich and all(
                            isinstance(x, (int, float)) for x in bereich):
                        werte[feld['pfad']] = (min(bereich), max(bereich))
                    else:
                        werte[feld['pfad']] = bereich
                sammeln(gruppe.get('untergruppen', ()))
        sammeln(Katalog.regler(vorlage))
        return werte


class LeggingsOhneBuendchenTest(SimpleTestCase):
    u"""Kein Ruesche-Buendchen mehr (Edgar, 11.09.2026: „an den Knoecheln
    ist es noch falsch"): `top_ruffle 1.6` raffte Stoff, den das Anlegen
    nicht entfalten kann — Dreiecksmitten bis 20 mm im Bein. Beide
    Voreinstellungen fuehren es nicht mehr; das Passform-Preset nimmt es
    beim Anhaken auch weg (`zurueck`), weil das Reitergedaechtnis die
    alte Fassung sonst weitertraegt."""

    databases = set()

    def test_keine_ruesche_in_beiden_voreinstellungen(self):
        for eintrag in EIGENE['hose']:
            self.assertNotIn('pants.cuff.top_ruffle', eintrag['werte'])
        leggings = [p for p in Katalog.passform('hose') if p['titel'] == 'Leggings'][0]
        self.assertNotIn('pants.cuff.top_ruffle', leggings['werte'])
        self.assertIn('pants.cuff.top_ruffle', leggings['zurueck'])
        self.assertIn('pants.cuff.type', leggings['zurueck'])

    def test_zurueck_nennt_nur_echte_regler(self):
        regler = set()

        def sammeln(gruppen):
            for gruppe in gruppen:
                regler.update(f['pfad'] for f in gruppe.get('felder', ()))
                sammeln(gruppe.get('untergruppen', ()))
        sammeln(Katalog.regler('hose'))
        for preset in Katalog.passform('hose'):
            for pfad in preset.get('zurueck', ()):
                self.assertIn(pfad, regler, pfad)

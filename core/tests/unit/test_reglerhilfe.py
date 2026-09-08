# -*- coding: utf-8 -*-
u"""Hilfetexte, Wertenamen und Voreinstellungen der GarmentCode-Regler.

Edgar, 08.09.2026: „ich verstehe das UI nicht … Änderungen an den Slidern
bei den Armen bringen nichts, ich weiss nicht was ArmholeCure bedeutet"
und „kannst du mir ein preset machen bei den ärmeln (checkbox) dafür?"

WAS HIER GEPRÜFT WIRD, UND WARUM GERADE DAS
===========================================
Die Texte selbst kann kein Test bewerten. Prüfbar ist aber, dass sie zu
ECHTEN Reglern gehören und dass keiner fehlt — ein Hilfetext auf einen
Pfad, den es nicht gibt, wäre stumm wirkungslos, und genau so ein Eintrag
entsteht bei jedem Upstream-Wechsel von selbst.

Dazu die Bedingungen: Sie sind der Kern der Antwort auf „bringt nichts".
Steht eine auf einem Pfad, den GarmentCode nicht führt, zeigt die
Oberfläche eine Warnung zu einem Regler, den niemand sieht.
"""
import unittest

from django.test import SimpleTestCase

from GarmentCode.katalog import Katalog
from GarmentCode.regler import Regler
from GarmentCode.reglerhilfe import Reglerhilfe
from GarmentCode.reglerpresets import Reglerpresets
from GarmentCode.reglertexte import Reglertexte


def _pfade(entwurf):
    u"""Alle Reglerpfade eines Entwurfs, flach."""
    aus = []

    def gehen(bloecke):
        for block in bloecke:
            for feld in block['felder']:
                aus.append(feld['pfad'])
            gehen(block['untergruppen'])

    gehen(Regler.fuer(entwurf))
    return aus


def _alle_pfade():
    u"""Reglerpfade über ALLE Kleidungsstücke des Katalogs.

    Ein einzelnes Stück zeigt nur seine Gruppen — ein Rock hat keinen
    Ärmel. Wer nur gegen das T-Shirt prüft, hält jeden Hosen- und
    Rocktext für einen Fehler.
    """
    aus = set()
    for name in Katalog.STUECKE:
        aus.update(_pfade(Katalog.entwurf(name)))
    return aus


class ReglertexteTest(SimpleTestCase):
    u"""Die Erklärungen gehören zu Reglern, die es gibt."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pfade = _alle_pfade()
        cls.felder = {p.rsplit('.', 1)[-1] for p in cls.pfade}

    def test_die_pfadtexte_treffen_echte_regler(self):
        u"""Ein Text auf einen Pfad, den es nicht gibt, wirkt nie."""
        fehlend = sorted(p for p in Reglertexte.PFADE
                         if p not in self.pfade)
        self.assertEqual(fehlend, [], u'Erklärung ohne Regler: %s' % fehlend)

    def test_die_feldtexte_treffen_echte_felder(self):
        fehlend = sorted(f for f in Reglertexte.FELDER if f not in self.felder)
        self.assertEqual(fehlend, [], u'Erklärung ohne Feld: %s' % fehlend)

    def test_die_aermelgruppe_ist_vollstaendig_erklaert(self):
        u"""Die Gruppe, an der Edgar hängengeblieben ist, lässt keinen aus."""
        ohne = [p for p in sorted(self.pfade)
                if p.startswith('sleeve.') and not Reglertexte.fuer(p)]
        self.assertEqual(ohne, [], u'Ärmelregler ohne Erklärung: %s' % ohne)

    def test_gegenprobe_ein_unbekannter_pfad_gibt_leer(self):
        u"""Ohne diesen Fall wäre ein Prüfer denkbar, der immer Text findet."""
        self.assertEqual(Reglertexte.fuer('quatsch.gibtsnicht'), u'')


class ReglerhilfeTest(SimpleTestCase):
    u"""Wertenamen und die stillen Bedingungen."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pfade = _alle_pfade()

    def test_die_bedingungen_treffen_echte_regler(self):
        fehlend = sorted(p for p in Reglerhilfe.BEDINGUNGEN
                         if p not in self.pfade)
        self.assertEqual(fehlend, [], u'Bedingung ohne Regler: %s' % fehlend)

    def test_die_beiden_gemeldeten_regler_tragen_ihre_bedingung(self):
        u"""`armhole_shape` und `sleeve_angle` — die Auslöser der Meldung.

        Beide tun unter einer Bedingung nichts (sleeves.py 229 bzw. 118).
        Fällt einer der Texte weg, ist die Oberfläche wieder so stumm wie
        vorher.
        """
        for pfad in ('sleeve.armhole_shape', 'sleeve.sleeve_angle'):
            self.assertTrue(Reglerhilfe.bedingung(pfad),
                            u'%s ohne Bedingungstext' % pfad)

    def test_jeder_auswahlwert_hat_einen_deutschen_namen(self):
        u"""Sonst steht wieder `ArmholeCurve` in der Liste."""
        ohne = set()
        for name in Katalog.STUECKE:
            for block in Regler.fuer(Katalog.entwurf(name)):
                ohne.update(self._ohne_namen(block))
        self.assertEqual(sorted(ohne), [],
                         u'Auswahlwerte ohne deutschen Namen: %s' % sorted(ohne))

    def _ohne_namen(self, block):
        aus = set()
        for feld in block['felder']:
            if feld['typ'] not in ('select', 'select_null'):
                continue
            for wert in feld['bereich']:
                # Zahlen brauchen keinen Namen (`panel_curve`, `num_inserts`).
                if wert is None or not isinstance(wert, str):
                    continue
                if Reglerhilfe.wert(wert) == wert:
                    aus.add(wert)
        for unter in block['untergruppen']:
            aus.update(self._ohne_namen(unter))
        return aus

    def test_die_linke_seite_erbt_ihre_bedingung(self):
        u"""Alles unter `left.` gilt nur mit dem Haken — bis auf den Haken."""
        self.assertTrue(Reglerhilfe.bedingung('left.sleeve.end_width'))
        self.assertEqual(Reglerhilfe.bedingung('left.enable_asym'), u'')

    def test_die_hilfe_kommt_als_dreiteil(self):
        hilfe = Reglerhilfe.hilfe('sleeve.end_width')
        self.assertEqual(set(hilfe), {'text', 'bedingung', 'original'})
        self.assertEqual(hilfe['original'], 'sleeve.end_width')
        self.assertIn(u'Ärmelende', hilfe['text'])


class ReglerpresetsTest(SimpleTestCase):
    u"""Die Voreinstellungen setzen nur Regler, die das Stück wirklich hat."""

    def test_jedes_preset_setzt_vorhandene_regler(self):
        pfade = _alle_pfade()
        for preset in Reglerpresets.PRESETS:
            for pfad in preset['werte']:
                self.assertIn(pfad, pfade,
                              u'Preset %s setzt %s — gibt es nicht'
                              % (preset['schluessel'], pfad))

    def test_jeder_wert_liegt_in_seinem_bereich(self):
        u"""Ein Wert daneben wird vom Server stumm verworfen."""
        bereiche = {}
        for name in Katalog.STUECKE:
            for block in Regler.fuer(Katalog.entwurf(name)):
                self._bereiche(block, bereiche)
        for preset in Reglerpresets.PRESETS:
            for pfad, wert in preset['werte'].items():
                unten, oben = bereiche[pfad]
                self.assertTrue(unten <= wert <= oben,
                                u'%s = %s liegt nicht in [%s, %s]'
                                % (pfad, wert, unten, oben))

    def _bereiche(self, block, aus):
        for feld in block['felder']:
            if feld['typ'] in ('float', 'int') and len(feld['bereich']) == 2:
                aus[feld['pfad']] = (feld['bereich'][0], feld['bereich'][1])
        for unter in block['untergruppen']:
            self._bereiche(unter, aus)

    def test_presets_erscheinen_nur_wo_ihre_gruppe_vorkommt(self):
        u"""Ein Ärmel-Preset an der Hose setzte Werte, die niemand liest."""
        self.assertTrue(Katalog.presets('t-shirt'))
        self.assertEqual(Katalog.presets('hose'), [])
        self.assertEqual(Katalog.presets('bleistiftrock'), [])

    def test_die_werte_sind_kopien(self):
        u"""Wer die Vorlage verändert, verändert sie für alle nächsten Läufe."""
        erste = Reglerpresets.werte('aermel_eng')
        erste['sleeve.end_width'] = 99
        self.assertEqual(Reglerpresets.werte('aermel_eng')['sleeve.end_width'],
                         0.2)

    def test_das_gemessene_preset_ist_das_aus_dem_bildschirmfoto(self):
        u"""Vier Werte, gegen die die Messreihe gefahren wurde.

        Ändert sie jemand, gelten die Zahlen im Hinweistext („6,1 statt
        14,2 mm") nicht mehr — und ein Hinweis mit falschen Messwerten ist
        schlimmer als keiner.
        """
        self.assertEqual(Reglerpresets.werte('aermel_eng'), {
            'sleeve.length': 1.1,
            'sleeve.connecting_width': 0.0,
            'sleeve.end_width': 0.2,
            'sleeve.sleeve_angle': 10,
        })


if __name__ == '__main__':
    unittest.main()

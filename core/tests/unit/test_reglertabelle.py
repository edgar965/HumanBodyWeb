# -*- coding: utf-8 -*-
u"""Die gemeinsame Reglertabelle — ein Name, zwei Uebersetzungen.

Der wichtigste Fall ist `test_kein_name_ist_erfunden`: Die Tabelle nennt
fremde Namen (UMA-DNA aus dem Unity-Projekt, Morphnamen aus den L2-Paketen).
Ein Tippfehler dort ergaebe im Browser einen Regler, der sich ziehen laesst
und nichts tut — ohne Fehler, ohne Logeintrag. Hier faellt er auf.

Die Umrechnung wird mit denselben Beispielwerten geprueft wie die
JS-Fassung (`test_js_reglerabbildung`), damit beide Seiten nicht
auseinanderlaufen.
"""
import os

from django.conf import settings
from django.test import SimpleTestCase

from humanbody_core import MorphData, CharacterState
from humanbody_core.regler import Reglertabelle
from UMA_Python.formregler import Formregler

from core.dienste.charakterdaten import Charakterdaten


class TabelleTest(SimpleTestCase):

    databases = set()

    def test_die_tabelle_ist_nicht_leer_und_in_drei_gruppen(self):
        gruppen = Reglertabelle.gruppen()
        self.assertEqual([g for g, _ in gruppen], [u'Körper', u'Gesicht', u'Nur UMA'])
        for _, eintraege in gruppen:
            self.assertTrue(eintraege)

    def test_namen_sind_eindeutig_und_ascii(self):
        namen = [e['name'] for e in Reglertabelle.eintraege()]
        self.assertEqual(len(namen), len(set(namen)))
        for name in namen:
            self.assertTrue(name.isascii(), name)
            self.assertEqual(name, name.lower())

    def test_jeder_eintrag_stellt_wenigstens_auf_der_uma_seite_etwas(self):
        for eintrag in Reglertabelle.eintraege():
            self.assertTrue(eintrag.get('uma'), eintrag['name'])
            self.assertTrue(eintrag.get('anzeige'), eintrag['name'])

    def test_wer_kein_morph_hat_steht_in_der_gruppe_nur_uma(self):
        u"""Sonst stuende bei HumanBody ein Regler, der dort nichts bewirkt."""
        for eintrag in Reglertabelle.eintraege():
            einseitig = not (eintrag.get('humanbody') or eintrag.get('meta'))
            self.assertEqual(einseitig, eintrag['gruppe'] == u'Nur UMA',
                             eintrag['name'])

    def test_gilt_fuer_trennt_die_welten(self):
        self.assertTrue(Reglertabelle.gilt_fuer('bauch', 'uma'))
        self.assertTrue(Reglertabelle.gilt_fuer('bauch', 'humanbody'))
        self.assertTrue(Reglertabelle.gilt_fuer('nase_schief', 'uma'))
        self.assertFalse(Reglertabelle.gilt_fuer('nase_schief', 'humanbody'))
        # Die Groesse hat keinen Morph, aber einen Metaregler.
        self.assertTrue(Reglertabelle.gilt_fuer('groesse', 'humanbody'))


class UmrechnungTest(SimpleTestCase):

    databases = set()

    def test_mitte_laesst_beide_welten_unveraendert(self):
        self.assertEqual(Reglertabelle.uma_werte('bauch', 0), {'belly': 0.5})
        self.assertEqual(Reglertabelle.humanbody_werte('bauch', 0),
                         {'Stomach_Volume': 0.0})

    def test_ausschlag_nach_beiden_seiten(self):
        self.assertEqual(Reglertabelle.uma_werte('bauch', 50), {'belly': 0.75})
        self.assertEqual(Reglertabelle.uma_werte('bauch', -100), {'belly': 0.0})
        self.assertEqual(Reglertabelle.uma_werte('bauch', 100), {'belly': 1.0})
        self.assertEqual(Reglertabelle.humanbody_werte('bauch', -30),
                         {'Stomach_Volume': -0.3})

    def test_ueber_die_grenze_wird_geklemmt_nicht_verworfen(self):
        self.assertEqual(Reglertabelle.uma_werte('bauch', 500), {'belly': 1.0})
        self.assertEqual(Reglertabelle.humanbody_werte('bauch', -500),
                         {'Stomach_Volume': -1.0})

    def test_ein_regler_stellt_alle_seine_ziele(self):
        werte = Reglertabelle.humanbody_werte('lippen', -30)
        self.assertEqual(werte, {'Mouth_UpperlipVolume': -0.3,
                                 'Mouth_LowerlipVolume': -0.3})

    def test_rueckweg_aus_uma(self):
        self.assertAlmostEqual(Reglertabelle.aus_uma('bauch', {'belly': 0.75}), 50.0)
        self.assertAlmostEqual(Reglertabelle.aus_uma('bauch', {'belly': 0.5}), 0.0)

    def test_rueckweg_aus_uma_ist_none_wenn_die_rasse_den_regler_nicht_kennt(self):
        u"""Nicht jede UMA-Rasse fuehrt jeden DNA-Namen — dann keine Zeile."""
        self.assertIsNone(Reglertabelle.aus_uma('bauch', {'height': 0.5}))

    def test_rueckweg_aus_humanbody_zaehlt_ungesetzte_morphs_als_null(self):
        u"""Drei Ziele, eines gestellt: der Regler steht bei einem Drittel."""
        wert = Reglertabelle.aus_humanbody('ohren_groesse', {'Ears_SizeX': 0.6})
        self.assertAlmostEqual(wert, 20.0)

    def test_die_groesse_traegt_eine_einheit_und_wird_nicht_hier_gerechnet(self):
        u"""cm haengt an der Figur (gemessene Hoehe) — lieber Fehler als Unsinn."""
        self.assertEqual(Reglertabelle.einheiten(), ['groesse'])
        with self.assertRaises(ValueError):
            Reglertabelle.uma_werte('groesse', 10)
        with self.assertRaises(ValueError):
            Reglertabelle.aus_humanbody('groesse', {})

    def test_unbekannter_regler_faellt_auf(self):
        with self.assertRaises(KeyError):
            Reglertabelle.fuer('gibtesnicht')


class EchteNamenTest(SimpleTestCase):
    u"""Gegen die echten Listen beider Welten — nur lesend."""

    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        md, vorgaben = Charakterdaten.morphdaten(), Charakterdaten.voreinstellungen()
        cls.morphs = set()
        cls.je_typ = {}
        for typ in MorphData.BODY_TYPES:
            zustand = CharacterState(md, vorgaben)
            zustand.set_body_type(typ)
            namen = {m['name'] for m in zustand.get_morph_list()}
            cls.je_typ[typ] = namen
            cls.morphs |= namen
        cls.uma = set()
        ordner = str(settings.UMA_UMA3_ORDNER)
        if os.path.isdir(ordner):
            formregler = Formregler(ordner)
            for geschlecht in Formregler.GRUPPEN:
                cls.uma |= {r['name'] for g in formregler.gruppen(geschlecht)
                            for r in g['regler']}

    def test_kein_name_ist_erfunden(self):
        u"""Jeder Name der Tabelle kommt in mindestens einer Rasse/einem Typ vor."""
        if not self.uma:
            self.skipTest('UMA-Projekt nicht vorhanden')
        fehlend = Reglertabelle.unbekannt(self.uma, self.morphs)
        self.assertEqual(fehlend['uma'], [])
        self.assertEqual(fehlend['humanbody'], [])

    def test_der_koerperteil_gilt_in_jedem_koerpertyp(self):
        u"""Körperregler sind ueberall da; nur Gesicht und Brust haengen am Typ.

        Belegt am 06.09.2026: `Female_Latin` und `Male_Latin` fuehren gar keine
        Gesichtsmorphs (109 statt 216), maennliche Typen keine Brustposition.
        Solche Zeilen blendet die Seite aus — deshalb steht hier nur der
        Koerperteil ohne Brust.
        """
        koerper = [e for e in Reglertabelle.eintraege()
                   if e['gruppe'] == u'Körper' and not e['name'].startswith('brust')]
        for typ, namen in self.je_typ.items():
            for eintrag in koerper:
                for morph in eintrag.get('humanbody', []):
                    self.assertIn(morph, namen, '%s in %s' % (eintrag['name'], typ))

    def test_die_tabelle_ersetzt_die_morphs_nicht(self):
        u"""HumanBody bleibt deutlich feiner als die gemeinsame Ebene."""
        self.assertLess(len(Reglertabelle.morph_namen()), len(self.morphs) / 2)

    def test_kein_uma_regler_faellt_unter_den_tisch(self):
        u"""JEDER Regler JEDER Rasse steht in der Tabelle.

        Edgar, 06.09.2026: „die sollen auch irgendwo erscheinen." Wer hier
        fehlt, ist im gemeinsamen Block unsichtbar; die männlichen Rassen
        führen eigene Regler (`chestSize`, `shoulderWidth`), die beim ersten
        Bau genau so durchgefallen waren.
        """
        if not self.uma:
            self.skipTest('UMA-Projekt nicht vorhanden')
        belegt = set(Reglertabelle.uma_namen())
        self.assertEqual(sorted(self.uma - belegt), [])

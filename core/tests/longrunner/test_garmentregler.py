# -*- coding: utf-8 -*-
u"""Regler — erreichen ALLE GarmentCode-Einstellungen die Oberflaeche?

WARUM (Edgar, 07.09.2026): „bei Ärmel fehlen mir die Konfigurationen die es
auf der webseite gibt. Überprüfe ALLE konfigurationen nochmal." Gemessen
erreichten **65 von 122** Reglern die Oberflaeche nie — verschachtelte
Gruppen (`sleeve.cuff`, `collar.component`, `left.*`), der Typ
`select_null` und eine zu enge Gruppenzuordnung.

DER ERSTE TEST IST DER WICHTIGE
===============================
`test_jeder_regler_ist_irgendwo_erreichbar` zaehlt die Blaetter der
Vorlage und haelt sie gegen das, was der Katalog zeigt. Er faellt auch bei
einem Upstream-Wechsel auf: Kommt eine neue Reglergruppe dazu, ohne dass
`GRUPPEN_JE_BAUSTEIN` sie kennt, wird er rot — statt dass die Regler still
verschwinden, wie es ein halbes Jahr lang der Fall war.

Ausgenommen ist nur `meta`: Diese drei Felder waehlen das Kleidungsstueck
selbst, und dafuer gibt es die Katalogliste.
"""
import unittest

import yaml

from GarmentCode.katalog import Katalog
from GarmentCode.regler import Regler
from GarmentCode.reglertitel import Reglertitel


def blaetter(knoten, pfad=()):
    u"""Alle Regler-dicts der Vorlage mit ihrem vollen Pfad."""
    aus = []
    for name, wert in knoten.items():
        if not isinstance(wert, dict):
            continue
        if 'v' in wert and 'type' in wert:
            aus.append('.'.join(pfad + (name,)))
        else:
            aus.extend(blaetter(wert, pfad + (name,)))
    return aus


def pfade(block, aus=None):
    u"""Alle Reglerpfade eines Gruppenblocks, auch aus Untergruppen."""
    aus = set() if aus is None else aus
    for feld in block['felder']:
        aus.add(feld['pfad'])
    for unter in block['untergruppen']:
        pfade(unter, aus)
    return aus


class ReglerdeckungTest(unittest.TestCase):

    databases = []

    @classmethod
    def setUpClass(cls):
        with open(Katalog.GRUNDLAGE, 'r', encoding='utf-8') as datei:
            cls.vorlage = yaml.safe_load(datei)['design']
        cls.alle = blaetter(cls.vorlage)
        cls.gezeigt = set()
        for name in Katalog.STUECKE:
            for gruppe in Katalog.regler(name):
                cls.gezeigt |= pfade(gruppe)

    def test_die_vorlage_hat_die_erwartete_groesse(self):
        u"""122 Regler — faellt auf, wenn der Upstream sich aendert."""
        self.assertEqual(len(self.alle), 122)

    def test_jeder_regler_ist_irgendwo_erreichbar(self):
        u"""Der Kern: kein Regler faellt still unter den Tisch."""
        fehlt = sorted(n for n in self.alle if n not in self.gezeigt)
        self.assertEqual(
            fehlt, ['meta.bottom', 'meta.upper', 'meta.wb'],
            'Diese Regler erreichen die Oberflaeche nicht: %s' % fehlt)

    def test_der_aermel_ist_vollstaendig(self):
        u"""Edgars Befund, als Fall: alle 17 Aermelregler beim T-Shirt."""
        gruppen = {g['gruppe']: g for g in Katalog.regler('t-shirt')}
        self.assertIn('sleeve', gruppen)
        aermel = pfade(gruppen['sleeve'])
        for feld in ('sleeveless', 'armhole_shape', 'length',
                     'connecting_width', 'end_width', 'sleeve_angle',
                     'opening_dir_mix', 'standing_shoulder',
                     'standing_shoulder_len', 'connect_ruffle',
                     'smoothing_coeff'):
            self.assertIn('sleeve.%s' % feld, aermel)
        for feld in ('type', 'top_ruffle', 'cuff_len', 'skirt_fraction',
                     'skirt_flare', 'skirt_ruffle'):
            self.assertIn('sleeve.cuff.%s' % feld, aermel,
                          'Manschettenregler fehlt')
        self.assertEqual(len(aermel), 17)

    def test_untergruppen_stehen_als_untergruppen(self):
        u"""Nicht flach eingehaengt — sonst heissen zwei Regler `type`."""
        sleeve = {g['gruppe']: g for g in Katalog.regler('t-shirt')}['sleeve']
        self.assertEqual([u['pfad'] for u in sleeve['untergruppen']],
                         ['sleeve.cuff'])
        self.assertNotIn('sleeve.cuff.type',
                         {f['pfad'] for f in sleeve['felder']})

    def test_meta_wird_nicht_gezeigt(self):
        u"""Wer `meta` verstellt, baut ein anderes Stueck — dafuer die Liste."""
        for name in Katalog.STUECKE:
            gruppen = [g['gruppe'] for g in Katalog.regler(name)]
            self.assertNotIn('meta', gruppen)


class ReglerwerteTest(unittest.TestCase):

    databases = []

    def entwurf(self, werte):
        return Katalog.entwurf('t-shirt', werte)

    # ------------------------------------------------------ tiefe Pfade

    def test_verschachtelter_wert_kommt_an(self):
        u"""`sleeve.cuff.cuff_len` — der Fall, den `partition` verlor.

        Die alte Fassung trennte an EINEM Punkt: Gruppe `sleeve`, Feld
        `cuff.cuff_len` — das gibt es nicht, und der Wert wurde stumm
        verworfen.
        """
        entwurf = self.entwurf({'sleeve.cuff.cuff_len': 0.6})
        self.assertAlmostEqual(entwurf['sleeve']['cuff']['cuff_len']['v'], 0.6)

    def test_vier_ebenen_tief(self):
        entwurf = self.entwurf({'left.sleeve.cuff.cuff_len': 0.7})
        self.assertAlmostEqual(
            entwurf['left']['sleeve']['cuff']['cuff_len']['v'], 0.7)

    def test_unbekannter_pfad_wird_verworfen_ohne_schaden(self):
        entwurf = self.entwurf({'gibts.nicht': 5, 'sleeve': 1,
                                'sleeve.cuff': 2})
        self.assertEqual(Regler.anwenden(entwurf, {'gibts.nicht': 5}), 0)
        # Die Struktur darf dabei nicht zerstoert werden.
        self.assertIn('v', entwurf['sleeve']['length'])

    # ------------------------------------------------------ select_null

    def test_select_null_nimmt_einen_wert(self):
        entwurf = self.entwurf({'sleeve.cuff.type': 'CuffBand'})
        self.assertEqual(entwurf['sleeve']['cuff']['type']['v'], 'CuffBand')

    def test_select_null_nimmt_nichts_zurueck(self):
        u"""Leer heisst `None` — sonst bliebe die Manschette fuer immer.

        Der Browser schickt die leere Zeichenkette; `None` steht nicht im
        `range`, also wuerde die alte Pruefung sie ablehnen und den alten
        Wert behalten.
        """
        for leer in ('', None, 'null', 'None'):
            with self.subTest(wert=leer):
                entwurf = self.entwurf({'sleeve.cuff.type': 'CuffBand'})
                Regler.anwenden(entwurf, {'sleeve.cuff.type': leer})
                self.assertIsNone(entwurf['sleeve']['cuff']['type']['v'])

    def test_select_null_lehnt_unsinn_ab(self):
        entwurf = self.entwurf({'sleeve.cuff.type': 'Quatsch'})
        self.assertIsNone(entwurf['sleeve']['cuff']['type']['v'])

    def test_none_steht_im_wertebereich(self):
        u"""Die Oberflaeche braucht einen Eintrag fuer „nichts"."""
        sleeve = {g['gruppe']: g for g in Katalog.regler('t-shirt')}['sleeve']
        cuff = sleeve['untergruppen'][0]
        typ = [f for f in cuff['felder'] if f['feld'] == 'type'][0]
        self.assertEqual(typ['typ'], 'select_null')
        self.assertIn(None, typ['bereich'])

    # ---------------------------------------------------------- baendigen

    def test_werte_werden_geklemmt(self):
        entwurf = self.entwurf({'sleeve.length': 99, 'sleeve.sleeve_angle': -5})
        self.assertAlmostEqual(entwurf['sleeve']['length']['v'], 1.15)
        self.assertEqual(entwurf['sleeve']['sleeve_angle']['v'], 10)

    def test_int_bleibt_ganz(self):
        entwurf = self.entwurf({'collar.component.depth': 5.7})
        wert = entwurf['collar']['component']['depth']['v']
        self.assertIsInstance(wert, int)
        self.assertEqual(wert, 6)

    def test_bool_versteht_die_zeichenkette(self):
        entwurf = self.entwurf({'sleeve.standing_shoulder': 'true'})
        self.assertIs(entwurf['sleeve']['standing_shoulder']['v'], True)


class ReglertitelTest(unittest.TestCase):

    databases = []

    def test_gleicher_name_verschiedene_bedeutung(self):
        u"""`cuff` heisst am Aermel Manschette, an der Hose Aufschlag."""
        self.assertEqual(Reglertitel.untergruppe('sleeve.cuff'), u'Manschette')
        self.assertEqual(Reglertitel.untergruppe('pants.cuff'), u'Aufschlag')
        self.assertEqual(Reglertitel.feld('sleeve.cuff.type'),
                         u'Manschettenform')
        self.assertEqual(Reglertitel.feld('pants.cuff.type'),
                         u'Aufschlagform')

    def test_unbekanntes_bleibt_englisch_und_lesbar(self):
        u"""Lieber ehrlich englisch als falsch geraten."""
        self.assertEqual(Reglertitel.feld('x.neu_erfunden'), 'neu erfunden')

    def test_jedes_feld_hat_einen_titel(self):
        u"""Kein Regler erscheint mit rohem Schluessel als Beschriftung."""
        roh = []
        for name in Katalog.STUECKE:
            for gruppe in Katalog.regler(name):
                roh.extend(self._ohne_titel(gruppe))
        self.assertEqual(sorted(set(roh)), [])

    def _ohne_titel(self, block):
        aus = []
        for feld in block['felder']:
            if feld['titel'] == feld['feld'] and '_' not in feld['feld']:
                # Ein einwortiger englischer Name ist erlaubt, ein
                # unuebersetzter mehrwortiger faellt hier auf.
                continue
            if feld['titel'] == feld['feld'].replace('_', ' '):
                aus.append(feld['pfad'])
        for unter in block['untergruppen']:
            aus.extend(self._ohne_titel(unter))
        return aus

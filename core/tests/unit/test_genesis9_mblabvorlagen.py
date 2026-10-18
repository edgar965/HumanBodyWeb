# -*- coding: utf-8 -*-
u"""`G9mblabvorlagen`: MB-Labs Körpertypen und Phänotypen als Katalogeinträge (17.10.2026) — Kunstdaten, keine MB-Lab-Daten, keine Ablage. Geschrieben, nicht gelaufen.

Edgar, 17.10.2026: „mach alles was offen ist" (Tabelle 8 in `genesis9-alter.md`).

1. Der Wert wird wie in HumanBody `2·v − 1` (0,5 = neutral), auf die Grenzen des Reglers geklemmt; Werte um null, unbekannte und nicht gebaute Morphs fallen weg.
2. Körpertypen und Phänotypen werden Katalogeinträge mit Grundfigur (Feminine bzw. Masculine = 1) und Standardhaut; die Anime-Basen (`an01`, `an02`) fehlen.
3. Die Namen sind eindeutig und tragen Art, Geschlecht und Datei.
4. Ohne den Ordner `tools/MB-Lab/data` gibt es keine Einträge, keinen Fehler.
5. Der Katalog nimmt sie auf (`G9charaktere.liste`).

Sabotage-Gegenprobe (nicht gefahren): in `regler` das `2.0 *` streichen → Fall 1 rot; die Anime-Prüfung in `_phaenotypen` entfernen → Fall 2 rot.
"""
import json
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.charaktere import G9charaktere
from Genesis9.mblabvorlagen import G9mblabvorlagen

from core.projekt_temp import ProjektTemp


def da(name):
    return name in ('hb:Torso_Mass', 'hb:Body_Size', 'hb:Nose_Width')


class WertTest(SimpleTestCase):
    databases = set()

    def regler(self, structural):
        with mock.patch('Genesis9.mblabvorlagen.G9hbmorphe.vorhanden', side_effect=da), \
                mock.patch('Genesis9.mblabvorlagen.G9hbmorphe.grenzen', return_value=(-1.0, 1.0)):
            return G9mblabvorlagen.regler(structural)

    def test_1_wert_2v_minus_1_geklemmt_und_ohne_unbekannte(self):
        aus = self.regler({'Torso_Mass': 0.75, 'Body_Size': 0.5, 'Nose_Width': 1.5, 'Fake': 0.9, 'Torso_Fat': 0.2})
        self.assertEqual(aus, {'hb:Torso_Mass': 0.5, 'hb:Nose_Width': 1.0}, 'neutral (0,5) fällt weg, 1,5 klemmt auf 1, unbekannte fallen weg')
        self.assertEqual(self.regler({'Torso_Mass': -0.5}), {'hb:Torso_Mass': -1.0})

    def test_1b_titel(self):
        self.assertEqual(G9mblabvorlagen._titel('type_athletic'), 'Athletic')
        self.assertEqual(G9mblabvorlagen._titel('specialtype_hero01'), 'Spezial Hero01')
        self.assertEqual(G9mblabvorlagen._titel('extreme_bodybuilder'), 'Extreme Bodybuilder')


class KatalogTest(SimpleTestCase):
    databases = set()

    def baum(self, wurzel):
        def schreiben(pfad, structural):
            pfad.parent.mkdir(parents=True, exist_ok=True)
            pfad.write_text(json.dumps({'structural': structural, 'metaproperties': {'character_mass': 0.1}}), encoding='utf-8')
        schreiben(wurzel / 'presets' / 'human_female_base' / 'type_athletic.json', {'Torso_Mass': 0.75})
        schreiben(wurzel / 'presets' / 'human_male_base' / 'type_athletic.json', {'Torso_Mass': 0.25})
        schreiben(wurzel / 'phenotypes' / 'f_as01_ptypes' / 'korean.json', {'Nose_Width': 0.9})
        schreiben(wurzel / 'phenotypes' / 'f_an01_ptypes' / 'anime.json', {'Nose_Width': 0.9})
        schreiben(wurzel / 'phenotypes' / 'm_ca01_ptypes' / 'alpinid.json', {'Torso_Mass': 0.9})

    def test_2_und_3_eintraege_grundfigur_haut_namen(self):
        with ProjektTemp.wegwerfordner(prefix='g9mblab_') as ordner:
            wurzel = Path(ordner)
            self.baum(wurzel)
            G9mblabvorlagen.vergessen()
            try:
                with mock.patch.object(G9mblabvorlagen, 'ordner', classmethod(lambda cls: wurzel)), \
                        mock.patch('Genesis9.mblabvorlagen.G9hbmorphe.vorhanden', side_effect=da), \
                        mock.patch('Genesis9.mblabvorlagen.G9hbmorphe.grenzen', return_value=(-1.0, 1.0)):
                    eintraege = G9mblabvorlagen.eintraege()
            finally:
                G9mblabvorlagen.vergessen()
        namen = [e['name'] for e in eintraege]
        self.assertEqual(sorted(namen), ['mblab_ethnie_f_as_korean', 'mblab_ethnie_m_ca_alpinid', 'mblab_typ_m_type_athletic', 'mblab_typ_w_type_athletic'])
        self.assertEqual(len(namen), len(set(namen)))
        nach = {e['name']: e for e in eintraege}
        frau = nach['mblab_typ_w_type_athletic']
        self.assertEqual(frau['regler'], {G9charaktere.FEMININE: 1.0, 'hb:Torso_Mass': 0.5})
        self.assertEqual(frau['haut'], G9charaktere.HAUT_W)
        self.assertEqual(nach['mblab_typ_m_type_athletic']['regler'], {G9charaktere.MASCULINE: 1.0, 'hb:Torso_Mass': -0.5})
        self.assertEqual(nach['mblab_ethnie_m_ca_alpinid']['haut'], G9charaktere.HAUT_M)
        self.assertNotIn('anime', ' '.join(namen), 'die Anime-Basen sind kein Mensch')
        self.assertEqual(frau['quelle'], 'MB-Lab')

    def test_4_ohne_ordner_keine_eintraege(self):
        with ProjektTemp.wegwerfordner(prefix='g9mblab_') as ordner:
            G9mblabvorlagen.vergessen()
            try:
                with mock.patch.object(G9mblabvorlagen, 'ordner', classmethod(lambda cls: Path(ordner) / 'gibt_es_nicht')):
                    self.assertEqual(G9mblabvorlagen.eintraege(), [])
            finally:
                G9mblabvorlagen.vergessen()

    def test_5_der_katalog_nimmt_sie_auf(self):
        probe = {'name': 'mblab_typ_w_probe', 'anzeige': 'Probe', 'geschlecht': 'weiblich', 'regler': {'hb:Torso_Mass': 0.5}, 'haut': G9charaktere.HAUT_W}
        G9charaktere.vergessen()
        try:
            # Die Daz-Bibliothek bleibt zu: Presets, Fremdregler und Brauen werden ersetzt, es geht nur um die Aufnahme.
            with mock.patch('Genesis9.mblabvorlagen.G9mblabvorlagen.eintraege', return_value=[probe]), \
                    mock.patch.object(G9charaktere, '_aus_presets', return_value=[]), \
                    mock.patch.object(G9charaktere, '_aus_reglern', return_value=[]), \
                    mock.patch.object(G9charaktere, '_brauen'):
                self.assertIn('mblab_typ_w_probe', G9charaktere.namen())
        finally:
            G9charaktere.vergessen()

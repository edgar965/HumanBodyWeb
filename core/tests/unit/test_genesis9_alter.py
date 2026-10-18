# -*- coding: utf-8 -*-
u"""Der Sammelregler „Alter“ (`G9alter`, 17.10.2026) — ohne Daz-Bibliothek, mit Attrappen für die Kanäle.

WARUM (Edgar, 17.10.2026: „kannst du nicht einen neuen Regler machen mit Alter, der alle aufgelisteten Regler enthält? Schau nach im HumanBody, da gibt es Regler für Alter,
kannst du das übernehmen?"): HumanBodys `age` stellt 88 (weiblich) bzw. 84 (männlich) Morph-Regler mit festen Anteilen; auf Genesis kommen die Daz-Regler für Alter dazu.
Zusagen:

1. `G9alterdaten` ist HumanBodys `morphs_meta.yaml` (`age`), Zahl für Zahl — die Datei wird nicht von Hand gepflegt.
2. HumanBodys Regel: `plus · a` über null, `−minus · a` darunter (`_apply_meta_to_morphs`); bei 0 kein Beitrag. Hier über null der GANZE Weg 18 → 100 Jahre
   (`_hb_anteil`: `(plus − minus) · a`, zweiter Durchgang 17.10.2026 — HumanBodys Nullpunkt ist 59 Jahre, die Genesis-Grundfigur jünger); darunter wie HumanBody.
2b. Die Daz-Kanäle dürfen bis an ihren Spielraum (`weit_min`/`weit_max`, ×2): Mann1 trägt `Body Older` schon mit 0,91.
3. `aufloesen`: `alter:gesamt` verschwindet, sein Beitrag steht auf den Einzelreglern, summiert mit dem, was dort schon steht, und begrenzt auf die Grenzen des Reglers.
4. Männlich oder weiblich entscheidet die Grundfigur im Rumpf; ein Daz-Regler mit `nur für` gilt nur dort.
5. `G9formung` rechnet nur mit den Einzelreglern: derselbe Fingerabdruck wie die aufgelöste Stellung; `aus_abfrage` nimmt den Schieber an und begrenzt ihn auf −1…1.
6. Der Reglerplan führt den Bereich „Alter“ gleich hinter „Figur“.
7. Älter macht keinen Bauch (`OHNE_BAUCH`, Edgar 17.10.2026: „Lebensalter Älter macht bei Ursula einen dicken Bauch“); jünger stellt den Torso weiter.
8. Kein Kind-Anteil mehr (17.10.2026, Vorschlag A „ein Alter, ein Aussehen“): „Wirkt älter / jünger“ ändert nur das Aussehen, nie die Größe — die kommt allein vom Lebensalter (`test_genesis9_alterung`).

Sabotage-Gegenprobe (nicht gefahren): in `_anteil` `plus`/`minus` vertauschen → Fall 2 rot; `aufloesen` ohne `min/max` → Fall 3b rot; `maennlich` immer False → Fall 4 rot; den Aufruf von `aufloesen` in
`G9formung.__init__` streichen → Fall 5 rot; den Bereich ans Ende des Plans legen → Fall 6 rot. Geschrieben, nicht gelaufen (nur auf Ansage).
"""
import os
from types import SimpleNamespace
from unittest import mock

import yaml
from django.conf import settings
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.alter import G9alter  # noqa: E402
from Genesis9.alterdaten import G9alterdaten  # noqa: E402
from Genesis9.formung import G9formung  # noqa: E402
from Genesis9.hbmorphe import G9hbmorphe  # noqa: E402
from Genesis9.mhmorphe import G9mhmorphe  # noqa: E402
from Genesis9.reglerplan import G9reglerplan  # noqa: E402

M, W = G9alter.MAENNLICH, G9alter.WEIBLICH
#: Alle Namen der Tabellen mit ihren Grenzen — so, als gäbe es sie alle (`G9alter._grenzen`).
GRENZEN = {k: (-1.0, 1.0) for k in G9alter.beitraege(1.0, True)} | {k: (-1.0, 1.0) for k in G9alter.beitraege(1.0, False)}


def grenzen(**eigene):
    return mock.patch.object(G9alter, '_grenzen', classmethod(lambda cls: dict(GRENZEN, **eigene)))


class AlterdatenTest(SimpleTestCase):
    databases = set()

    def test_1_die_tabelle_ist_humanbodys_meta_age(self):
        daten = os.path.dirname(str(settings.HUMANBODY_DATA_DIR))          # `HumanBody/data` — daneben `humanBody_male`
        for ordner, soll in (('humanBody', G9alterdaten.WEIBLICH), ('humanBody_male', G9alterdaten.MAENNLICH)):
            pfad = os.path.join(daten, ordner, 'morphs_meta.yaml')
            with open(pfad, encoding='utf-8') as datei:
                quelle = yaml.safe_load(datei)['age']['morphs']
            self.assertEqual({k: tuple(v) for k, v in quelle.items()}, dict(soll), ordner)


class RegelTest(SimpleTestCase):
    databases = set()

    def test_2_plus_ueber_null_minus_darunter(self):
        self.assertEqual(G9alter._anteil(0.2, -0.4, 1.0), -0.4)
        self.assertEqual(G9alter._anteil(0.2, -0.4, 0.5), -0.2)
        self.assertAlmostEqual(G9alter._anteil(0.2, -0.4, -1.0), 0.2)
        self.assertEqual(G9alter._anteil(0.2, -0.4, 0.0), 0)
        # Hier: über null der ganze Weg 18 → 100 (plus − minus), darunter wie HumanBody.
        self.assertAlmostEqual(G9alter._hb_anteil(0.2, -0.4, 1.0), -0.6)
        self.assertAlmostEqual(G9alter._hb_anteil(0.2, -0.4, 0.5), -0.3)
        self.assertAlmostEqual(G9alter._hb_anteil(0.2, -0.4, -1.0), 0.2)
        self.assertEqual(G9alter._hb_anteil(0.2, -0.4, 0.0), 0)
        weiblich = G9alter.beitraege(1.0, False)
        minus, plus = G9alterdaten.WEIBLICH['Chin_Tone']
        self.assertAlmostEqual(weiblich['hb:Chin_Tone'], plus - minus)    # −2,04 aus HumanBodys Zahlen; `aufloesen` begrenzt es
        self.assertAlmostEqual(G9alter.beitraege(-1.0, False)['hb:Torso_Tone'], 0.2)
        self.assertEqual(G9alter.beitraege(0.0, False), {})
        self.assertAlmostEqual(G9alter.beitraege(2.0, False)['hb:Chin_Tone'], plus - minus, msg='der Schieber selbst ist auf −1…1 begrenzt')

    def test_2b_daz_kanaele_bis_an_ihren_spielraum(self):
        kanaele = {k: {'min': -1.0, 'max': 1.0} for k, *_r in G9alter.DAZ}
        kanaele['body_bs_BodyOlder'] = {'min': -1.0, 'max': 1.0, 'weit_min': -2.0, 'weit_max': 2.0}
        with mock.patch('Genesis9.alter.G9morphablage.holen', return_value=SimpleNamespace(kanaele=kanaele)), \
                mock.patch('Genesis9.alter.G9hbmorphe.liste', return_value=[]):
            grenzen_ = G9alter._grenzen()
            aus = G9alter.aufloesen({M: 1.0, 'body_bs_BodyOlder': 0.91, G9alter.NAME: 1.0})
        self.assertEqual(grenzen_['body_bs_BodyOlder'], (-2.0, 2.0))
        self.assertEqual(grenzen_['200_head_bs_Ears Elderly-0xa0f8141'], (-1.0, 1.0), 'ohne Spielraum Dazʼ Grenze')
        self.assertAlmostEqual(aus['body_bs_BodyOlder'], 1.91, msg='0,91 + 1,0 — nicht an 1,0 gekappt')


class AufloesenTest(SimpleTestCase):
    databases = set()

    def test_3_der_schieber_verschwindet_und_steht_auf_den_einzelreglern(self):
        with grenzen():
            aus = G9alter.aufloesen({W: 1.0, G9alter.NAME: 1.0, 'hb:Arms_UpperarmTone': 0.5})
        self.assertNotIn(G9alter.NAME, aus)
        self.assertAlmostEqual(aus['hb:Arms_UpperarmTone'], 0.5 + G9alter.beitraege(1.0, False)['hb:Arms_UpperarmTone'], msg='summiert mit dem, was dort steht')
        self.assertIn('hb:Cheeks_SideCrease', aus)
        self.assertAlmostEqual(aus['body_bs_BodyOlder'], 1.0)
        self.assertEqual(aus[W], 1.0)

    def test_3b_jeder_wert_bleibt_in_den_grenzen_seines_reglers(self):
        with grenzen(**{'hb:Chin_Tone': (-1.0, 1.0), 'body_bs_BodyOlder': (-1.0, 0.7)}):
            aus = G9alter.aufloesen({W: 1.0, G9alter.NAME: 1.0})
        self.assertEqual(aus['hb:Chin_Tone'], -1.0, 'HumanBody setzt −2,0 an; ein HB-Morph geht nur bis −1')
        self.assertEqual(aus['body_bs_BodyOlder'], 0.7)

    def test_3c_ohne_schieber_dieselbe_stellung_und_bei_null_ohne_beitrag(self):
        vorher = {W: 1.0, 'hb:Arms_UpperarmTone': 0.3}
        self.assertIs(G9alter.aufloesen(vorher), vorher)
        self.assertEqual(G9alter.aufloesen({W: 1.0, G9alter.NAME: 0.0}), {W: 1.0})

    def test_3d_ein_name_ohne_gegenstueck_wirkt_nicht(self):
        with mock.patch.object(G9alter, '_grenzen', classmethod(lambda cls: {'hb:Arms_UpperarmTone': (-1.0, 1.0)})):
            aus = G9alter.aufloesen({W: 1.0, G9alter.NAME: 1.0})
        self.assertEqual(sorted(aus), sorted([W, 'hb:Arms_UpperarmTone']))


class DazTabelleTest(SimpleTestCase):
    databases = set()

    def test_3e_die_daz_tabelle_ist_eindeutig_und_wirkt_im_gesicht_in_beide_richtungen(self):
        namen = [zeile[0] for zeile in G9alter.DAZ]
        self.assertEqual(len(namen), len(set(namen)), 'ein Kanal steht nur einmal in der Tabelle')
        self.assertTrue(all(len(zeile) == 4 and zeile[3] in (None, 'm', 'w') for zeile in G9alter.DAZ))
        jung, alt = G9alter.beitraege(-1.0, True), G9alter.beitraege(1.0, True)
        # Jünger: größere Augen, vollere Wangen; älter: eingefallene Wangen, schmale Lippen — die Gegenrichtung entfällt je Kanal.
        self.assertGreater(jung['200_head_bs_Eyes Scale-0xa0f81b1'], 0)
        self.assertNotIn('200_head_bs_Eyes Scale-0xa0f81b1', alt)
        self.assertGreater(alt['200_head_bs_Cheeks Sink (Alt)-0xa0f819e'], 0)
        self.assertNotIn('200_head_bs_Cheeks Sink (Alt)-0xa0f819e', jung)
        self.assertLess(jung['200_head_bs_Chin Length-0xa0f81a6'], 0, 'jünger: kürzeres Kinn')


class GeschlechtTest(SimpleTestCase):
    databases = set()

    def test_4_die_grundfigur_waehlt_tabelle_und_daz_regler(self):
        self.assertTrue(G9alter.maennlich({M: 1.0}))
        self.assertFalse(G9alter.maennlich({W: 1.0}))
        self.assertFalse(G9alter.maennlich({}), 'ohne Grundfigur gilt die weibliche Tabelle (HumanBodys Vorgabe)')
        mann, frau = G9alter.beitraege(1.0, True), G9alter.beitraege(1.0, False)
        m_minus, m_plus = G9alterdaten.MAENNLICH['Arms_UpperarmTone']
        self.assertAlmostEqual(mann['hb:Arms_UpperarmTone'], m_plus - m_minus)
        self.assertAlmostEqual(frau['hb:Arms_UpperarmTone'], -0.4 - 0.1, msg='weiblich (0,1, −0,4): der Weg 18 → 100')
        self.assertIn('body_bs_PectoralsSag', mann)
        self.assertNotIn('body_bs_PectoralsSag', frau)
        self.assertIn('body_ctrl_BreastsHangForward', frau)
        self.assertNotIn('body_ctrl_BreastsHangForward', mann)
        self.assertNotIn('hb:Torso_BreastTone', mann, 'die männliche Tabelle führt ihn nicht')


class BauchUndKindTest(SimpleTestCase):
    databases = set()

    def test_7_aelter_macht_keinen_bauch_juenger_darf_flacher_werden(self):
        for maennlich in (False, True):
            alt, jung = G9alter.beitraege(1.0, maennlich), G9alter.beitraege(-1.0, maennlich)
            for name in G9alter.OHNE_BAUCH:
                self.assertNotIn(G9hbmorphe.regler(name), alt, '%s darf beim Älterwerden nicht stehen (Ursula: +92 mm Bauch)' % name)
            for kanal in G9alter.OHNE_BAUCH_DAZ:
                self.assertNotIn(kanal, alt, kanal)
            self.assertIn('hb:Torso_Tone', jung, 'jünger stellt den Torso weiter (ein flacherer Bauch schadet nicht)')
            self.assertIn('hb:Chin_Tone', alt, 'der Rest des Alters bleibt')

    def test_8_wirkt_juenger_legt_kein_kind_dazu_und_aendert_die_groesse_nicht(self):
        with mock.patch.object(G9mhmorphe, 'vorhanden', return_value=True):
            for wert in (-1.0, -0.4, 0.5, 1.0):
                aus = G9alter.beitraege(wert, False)
                self.assertEqual([k for k in aus if k.startswith('mh:')], [], 'Alter %+.1f: kein MakeHuman-Morph, also keine Größe (Lebensalter −1 und Alter −1 zählten das Kind doppelt)' % wert)

    def test_8b_der_aufruf_mit_dem_aussehen_ersetzt_den_rohen_schieber(self):
        with grenzen():
            roh = G9alter.aufloesen({W: 1.0, G9alter.NAME: 0.6})
            aussehen = G9alter.anwenden({W: 1.0, G9alter.NAME: 5.0}, 0.6)
        self.assertEqual(roh, aussehen, '`anwenden` rechnet mit dem übergebenen Aussehen, nicht mit dem Wert im Rumpf')
        self.assertNotIn(G9alter.NAME, aussehen)


class FormungTest(SimpleTestCase):
    databases = set()

    def test_5_die_formung_rechnet_nur_mit_den_einzelreglern(self):
        with grenzen():
            mit = G9formung({M: 1.0, G9alter.NAME: 0.6})
            aufgeloest = G9formung(G9alter.aufloesen({M: 1.0, G9alter.NAME: 0.6}))
            ohne = G9formung({M: 1.0})
        self.assertNotIn(G9alter.NAME, mit.regler)
        self.assertEqual(mit.regler, aufgeloest.regler)
        self.assertAlmostEqual(mit.alter_aussehen, 0.6, msg='das Aussehen steht auf der Stellung (der Server schickt es als `alter_aussehen`)')
        self.assertEqual(aufgeloest.alter_aussehen, 0.0, 'die aufgelöste Stellung trägt keinen Schieber mehr')
        self.assertNotEqual(mit.fingerabdruck(), aufgeloest.fingerabdruck(), 'gleiche Einzelregler, anderes Aussehen (Falten, graues Haar): nie dieselbe geteilte Stellung')
        self.assertNotEqual(mit.fingerabdruck(), ohne.fingerabdruck())
        self.assertTrue(mit.eigen(), 'die HB-Morphs stehen unter den fremden Reglern (`hb:`)')

    def test_5b_aus_abfrage_nimmt_den_schieber_an_und_begrenzt_ihn(self):
        kanaele = SimpleNamespace(kanaele={M: {'min': 0.0, 'max': 1.0}})
        with mock.patch('Genesis9.formung.G9morphablage.holen', return_value=kanaele), grenzen():
            zu_gross = G9formung.aus_abfrage({M: 1.0, G9alter.NAME: 5.0})
            drin = G9formung.aus_abfrage({M: 1.0, G9alter.NAME: 1.0})
        self.assertEqual(zu_gross.fingerabdruck(), drin.fingerabdruck(), '5,0 gilt wie 1,0')


class PlanTest(SimpleTestCase):
    databases = set()

    def test_6_der_bereich_alter_steht_hinter_figur(self):
        daz = [{'name': 'x', 'anzeige': 'X', 'min': 0, 'max': 1, 'vorgabe': 0, 'bereich': b, 'art': 'form'} for b in G9reglerplan.BEREICHE]
        leer = {'schluessel': 'x', 'name': 'x', 'regler': []}
        with mock.patch.object(G9reglerplan, 'holen', return_value=daz), \
                mock.patch('Genesis9.reglerplan.G9morphfamilien.bereiche', return_value=[]), \
                mock.patch('Genesis9.anhangregler.G9anhangregler.bereiche', return_value=[]), \
                mock.patch('Genesis9.schnittmorph.G9schnittmorph.bereich', return_value=leer), \
                mock.patch('Genesis9.koerperstandardmorphe.G9koerperstandardmorphe.bereich', return_value=leer), \
                mock.patch('Genesis9.koerperregionen.G9koerperregionen.bereich', return_value=leer), \
                mock.patch('Genesis9.modellmorphe.G9modellmorphe.bereich', return_value=leer), \
                mock.patch('Genesis9.verborgeneregler.G9verborgeneregler.bereiche', return_value=[]):
            schluessel = [b['schluessel'] for b in G9reglerplan.bereiche()]
        self.assertEqual(schluessel[:3], ['figur', 'alter', G9reglerplan.BEREICHE[1]])
        regler = G9alter.bereich()['regler'][0]
        self.assertEqual((regler['name'], regler['min'], regler['max'], regler['vorgabe']), (G9alter.NAME, -1.0, 1.0, 0.0))
        self.assertIn('hinweis', regler)

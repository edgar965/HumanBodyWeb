# -*- coding: utf-8 -*-
u"""Die Regler, die nur ein Anhang hat — Zähne und Augen (`G9anhangregler`, 17.10.2026) — und die Auflösung von Preset-Namen auf Kanal-IDs (`G9morphablage.aufloesen`).

WARUM (Edgar, 17.10.2026: „Ich fasse es nicht, dass du immer noch nicht alle Genesis-Regler gefunden hast … binde sie alle ein in das UI und in den Katalog"): 60 Zahnregler
(`200_teeth_bs_*`) und vier Augenregler gehören dem Mund- bzw. Augen-Anhang und hatten weder eine Zeile im Bedienfeld noch Annahme in der Formung; die Presets (`Shapes`, Posen)
nennen Kanäle ohne Daz' Kennung `-0x…` und liefen ins Leere. Zusagen:

1. Ein Anhangregler ist: sichtbar, mit eigenen Deltas, kein Körperkanal (verglichen OHNE Kennung), keine versteckte/Charaktergruppe, kein Folgename (`facs_…`, `Xxx9_head_…`).
   Zähne → `zaehne`, `head_bs_Eye…` am Augen-Anhang → `augen_eigen`, sonst Gruppe `/Base` (`head_bs_MouthSize`, `head_bs_FaceSize` — am Körper gibt es sie nicht, vierte
   Runde 17.10.2026) → `anhang_form`, anderes → keiner.
2. `angaben` nennt Grenzen nur für diese Regler; `gestellt` reicht nur ihre Werte (≠ 0) durch.
3. `G9formung.aus_abfrage` nimmt einen Zahnregler an (begrenzt auf seine Grenzen) und verwirft Unbekanntes weiter; `morphwerte` führt den Wert mit, damit der Anhang ihn rechnet.
4. `G9morphablage.aufloesen` (`G9kanalnamen`): zuerst der NAME des Modifikators (der echte Kanal vor dem Alias), dann die ID selbst, dann der sichtbare Kanal gleichen
   Namens ohne Kennung; `200_…`-Namen zuletzt über das Label; ein Alias führt zu seinem Ziel; Unbekanntes bleibt. 4c: `aus_abfrage` legt den Wert eines Alias auf sein Ziel.
5. `G9posen._ids` wendet das auf die Regler eines Presets an.

Sabotage-Gegenprobe (nicht gefahren): in `_bereich` den Vergleich mit `koerper` streichen → Fall 1 rot; `aufloesen` ohne die Kennung zu kappen → Fall 4 rot; den `update` in `G9formung.morphwerte`
streichen → Fall 3b rot. Geschrieben, nicht gelaufen (nur auf Ansage).
"""
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.anhangregler import G9anhangregler  # noqa: E402
from Genesis9.formung import G9formung  # noqa: E402
from Genesis9.morphablage import G9morphablage  # noqa: E402
from Genesis9.posen import G9posen  # noqa: E402

KOERPER = {'head_bs_MouthSize', 'head_bs_Nose'}


def steckbrief(label='x', gruppe='/Base', sichtbar=True, bis=1.0, von=0.0):
    return {'label': label, 'gruppe': gruppe, 'sichtbar': sichtbar, 'min': von, 'max': bis}


def ablage(**kanaele):
    u"""Eine Ablage aus Kunstkanälen: `{id: {sichtbar, label}}`."""
    return G9morphablage({k: dict({'id': k, 'label': k, 'sichtbar': True}, **v) for k, v in kanaele.items()}, None, None, {}, {})


class ReglerwahlTest(SimpleTestCase):
    databases = set()

    def test_1_nur_was_der_anhang_allein_hat(self):
        wahl = lambda schluessel, name, **s: G9anhangregler._bereich(schluessel, name, steckbrief(**s), True, KOERPER)       # noqa: E731
        self.assertEqual(wahl('mund', '200_teeth_bs_Teeth Length Upper', gruppe='01 Upper'), 'zaehne')
        self.assertEqual(wahl('mund', 'head_bs_TeethTuckedGumline', gruppe=''), 'zaehne')
        self.assertEqual(wahl('augen', 'head_bs_EyeIrisSizeLarger'), 'augen_eigen')
        self.assertIsNone(wahl('mund', 'head_bs_EyeIrisSizeLarger', gruppe=''), 'Augenregler zählen nur am Augen-Anhang')
        self.assertEqual(wahl('mund', 'head_bs_MouthWidth'), 'anhang_form', 'ein /Base-Regler, den nur der Anhang hat')
        self.assertEqual(wahl('augen', 'head_bs_FaceSize'), 'anhang_form')
        self.assertIsNone(wahl('wimpern', 'head_bs_EyelashesX', gruppe='/Eyelashes/Base'), 'andere Gruppen bleiben, wie sie sind')
        self.assertIsNone(wahl('mund', 'head_bs_MouthSize'), 'ein Körperkanal ist kein Anhangregler')
        self.assertIsNone(wahl('mund', 'head_bs_MouthSize-0xabc'), 'auch mit Dazʼ Kennung gleicht der Name dem Körperkanal')
        self.assertIsNone(wahl('mund', '200_teeth_bs_x', gruppe='/Hidden/200 Plus'), 'Verstecktes bleibt weg')
        self.assertIsNone(wahl('mund', '200_teeth_bs_x', gruppe='/People/Feminine'), 'Charakterteile bleiben weg')
        self.assertIsNone(wahl('mund', '200_teeth_bs_x', sichtbar=False))
        self.assertIsNone(wahl('mund', '200_teeth_bs_x', bis=0.0), 'ohne Spielraum kein Regler')
        self.assertIsNone(wahl('mund', 'facs_bs_TeethGone'), 'Folgenamen gehören dem Körper')
        self.assertIsNone(G9anhangregler._bereich('mund', '200_teeth_bs_x', steckbrief(), False, KOERPER), 'ohne eigene Deltas kein Regler')

    def test_2_grenzen_und_durchreichen(self):
        liste = [{'name': '200_teeth_bs_a', 'anzeige': 'A', 'min': -0.5, 'max': 1.0, 'vorgabe': 0.0, 'bereich': 'zaehne', 'art': 'form', 'gruppe': 'Upper'},
                 {'name': 'head_bs_EyeWholeSize', 'anzeige': 'E', 'min': -1.0, 'max': 1.0, 'vorgabe': 0.0, 'bereich': 'augen_eigen', 'art': 'form', 'gruppe': 'Base'}]
        with mock.patch.object(G9anhangregler, 'liste', classmethod(lambda cls: liste)), mock.patch.object(G9anhangregler, '_namen', None):
            self.assertEqual(G9anhangregler.angaben('200_teeth_bs_a'), {'min': -0.5, 'max': 1.0})
            self.assertIsNone(G9anhangregler.angaben('gibt_es_nicht'))
            self.assertEqual(G9anhangregler.gestellt({'200_teeth_bs_a': 0.4, 'head_bs_EyeWholeSize': 0.0, 'body_bs_x': 1.0}), {'200_teeth_bs_a': 0.4})
            aus = G9anhangregler.bereiche()
        self.assertEqual([b['schluessel'] for b in aus], ['zaehne', 'augen_eigen'])
        self.assertEqual(aus[0]['name'], u'Zähne')


class FormungTest(SimpleTestCase):
    databases = set()

    def test_3_die_formung_nimmt_zahnregler_an_und_reicht_sie_weiter(self):
        kanaele = SimpleNamespace(kanaele={})
        angaben = {'200_teeth_bs_a': {'min': -0.5, 'max': 1.0}}
        with mock.patch('Genesis9.formung.G9morphablage.holen', return_value=kanaele), \
                mock.patch.object(G9anhangregler, 'angaben', classmethod(lambda cls, n: angaben.get(n))):
            f = G9formung.aus_abfrage({'200_teeth_bs_a': 5.0, 'unbekannt': 1.0})
        self.assertEqual(f.regler, {'200_teeth_bs_a': 1.0}, 'begrenzt auf die Grenze des Reglers, Unbekanntes verworfen')

    def test_3b_morphwerte_fuehren_den_anhangwert_mit(self):
        f = G9formung({'200_teeth_bs_a': 0.7})
        formeln = SimpleNamespace(morphwerte=lambda: {'body_bs_x': 0.3})
        with mock.patch.object(G9formung, 'formeln', new_callable=mock.PropertyMock, return_value=formeln), \
                mock.patch.object(G9anhangregler, 'liste', classmethod(lambda cls: [{'name': '200_teeth_bs_a'}])), mock.patch.object(G9anhangregler, '_namen', None):
            werte = f.morphwerte()
        self.assertEqual(werte, {'body_bs_x': 0.3, '200_teeth_bs_a': 0.7})


class AufloesenTest(SimpleTestCase):
    databases = set()

    def test_4_name_zur_id(self):
        a = ablage(**{
            'body_bs_x': {},
            '200_head_bs_Cranium Width-0xa0f8174': {'label': '200+ Cranium Width'},
            'doppelt-0x1': {'sichtbar': False},
            'doppelt-0x2': {},
            '200_head_bs_Lips Thin (Alt)-0xa0f81c0': {'label': '200+ Lips Thickness'},
        })
        self.assertEqual(a.aufloesen('body_bs_x'), 'body_bs_x', 'die ID selbst gilt')
        self.assertEqual(a.aufloesen('200_head_bs_Cranium Width'), '200_head_bs_Cranium Width-0xa0f8174', 'der Name ohne Kennung findet die ID')
        self.assertEqual(a.aufloesen('doppelt'), 'doppelt-0x2', 'bei zwei Kennungen gewinnt der sichtbare Kanal')
        self.assertEqual(a.aufloesen('200_head_bs_Lips Thickness'), '200_head_bs_Lips Thin (Alt)-0xa0f81c0', 'umbenannte 200+-Kanäle über das Label')
        self.assertEqual(a.aufloesen('gibt_es_nicht'), 'gibt_es_nicht', 'Unbekanntes bleibt')

    def test_4b_name_vor_id_und_alias_zum_ziel(self):
        u"""Zweiter Durchgang (17.10.2026): Daz sucht `name://` über den NAMEN — 495 Modifikatoren heißen anders als ihre ID; ein Alias führt zu seinem Ziel."""
        a = ablage(**{
            '200_head_bs_Nose Depth Under-0xa0f81e1': {'name': '200_head_bs_Philtrum Depth'},
            '200_head_bs_Philtrum Depth Alt': {'name': 'etwas anderes'},
            'facs_ctrl_EyesSquint': {'name': 'facs_ctrl_EyeSquint', 'sichtbar': False},
            'alias_head_facs_ctrl_EyeSquint-0xa4d9cbe': {'name': 'facs_ctrl_EyeSquint', 'alias': 'facs_ctrl_EyesSquint'},
            'alias_head_facs_bs_JawForward-0x1': {'name': 'facs_bs_JawForward', 'alias': 'facs_JawForward'},
            'facs_JawForward': {'name': 'facs_JawForward'},
        })
        self.assertEqual(a.aufloesen('200_head_bs_Philtrum Depth'), '200_head_bs_Nose Depth Under-0xa0f81e1', 'der Name, nicht die ähnliche ID')
        self.assertEqual(a.aufloesen('facs_ctrl_EyeSquint'), 'facs_ctrl_EyesSquint', 'der echte Kanal vor dem Alias, auch unsichtbar')
        self.assertEqual(a.aufloesen('facs_bs_JawForward'), 'facs_JawForward', 'nur ein Alias trägt den Namen: sein Ziel')
        self.assertEqual(a.aliasziel('alias_head_facs_bs_JawForward-0x1'), 'facs_JawForward')
        self.assertEqual(a.aliasziel('facs_JawForward'), 'facs_JawForward')

    def test_4c_ein_alias_ist_in_der_formung_nur_der_griff(self):
        a = ablage(**{'alias_x': {'alias': 'x', 'min': 0.0, 'max': 1.0}, 'x': {'min': 0.0, 'max': 1.0}})
        with mock.patch('Genesis9.formung.G9morphablage.holen', return_value=a):
            f = G9formung.aus_abfrage({'alias_x': 0.6})
        self.assertEqual(f.regler, {'x': 0.6})

    def test_5_ein_preset_wird_auf_ids_gelegt(self):
        a = ablage(**{'200_head_bs_Cranium Width-0xa0f8174': {}})
        with mock.patch('Genesis9.posen.G9morphablage.holen', return_value=a):
            aus = G9posen._ids({'200_head_bs_Cranium Width': 0.4, '200_teeth_bs_x': 0.2})
        self.assertEqual(aus, {'200_head_bs_Cranium Width-0xa0f8174': 0.4, '200_teeth_bs_x': 0.2})

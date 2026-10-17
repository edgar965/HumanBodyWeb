# -*- coding: utf-8 -*-
u"""Vierte Runde „alle Regler" (17.10.2026) — Kunstdaten, keine Daz-Bibliothek.

WARUM (Edgar, 17.10.2026: „Mach noch eine Überprüfungsrunde … Schau nach, ob du jetzt nun wirklich alles hast" und „8.1 Smile nachbauen"). Gemessen
(`ProjektTemp/_wegwerf/alter/runde4_pruefen.py`, `runde4_einzeln.py`, `runde4_ab.py`):

- die Formeln der Anhänge auf einen Kanalwert (`?value`) wurden nie gerechnet: im Mund stellen die Viseme die Zunge (`facs_ctrl_vIY` → `facs_ctrl_TongueUp` 0,2 → Zungenspitze
  30°), „200+ Mouth Cavity Depth" den Mundmorph `200_Head_bs_Mouth Depth`, „Eyes Scale" die Träne — mit gegen ohne bis 10,8 mm;
- 53 Space-Valkyrie-Posen nennen ihre Knochen mit Dateiverweis (`hip:/data/…/Genesis9.dsf#hip`) — `G9posen` las „Genesis9.dsf#hip" und drehte keinen;
- `facs_ctrl_SmileFullFace`/`SmileOpenFullFace` (Damiras Smile-Presets) gibt es nur für Genesis 8.1.

Zusagen:

1. `G9anhangmorphe._formeln`: `?value`-Ausgaben werden `{morph: Name, stufe, ops}` (ID → Name wie bei den Knochenformeln); `wertformeln` nennt nur sie.
2. `G9kanalnamen.genau`: nur Name oder ID, NIE das Label — `200_Head_bs_Mouth Height` (Mund) ist nicht `200_head_bs_Mouth Height` (Körper, Lippen); `aufloesen` fände es.
3. `G9formeln.index` hängt eine Wertformel mit Körperziel an den Körperkanal (`facs_ctrl_vER` 1 → `facs_bs_TongueIn` 0,45); ein Ziel, das nur übers Label passt, nicht.
4. `G9anhangkopplung.werte` rechnet die Wertformeln auf EIGENE Kanäle ohne Körpergegenstück am Anhang (`200_Head_bs_Mouth Depth` = Cavity × 1).
5. `G9posen._lesen`: Knochen mit und ohne Dateiverweis, Kanalwerte daneben.
6. `G9smile81`: legt die beiden Kanäle mit Formeln in die Ablage — Anteile wie in Genesis 8.1, männlich gemischt über `BaseMasculine`; Lippenknochen über `posen()`;
   ohne Ziele kein Kanal; ein zweiter Aufruf ändert nichts.

Sabotage-Gegenprobe (nicht gefahren): in `_formeln` die `morph`-Verzweigung streichen → Fall 1 rot; in `genau` `aufloesen` rufen → Fall 2 und 3 (zweite Hälfte) rot;
`_anhaenge_dazu` ohne die Schleife über `wertformeln` → Fall 3 rot; `_formelwerte` nicht rufen → Fall 4 rot; in `_lesen` wieder `rsplit('/')` → Fall 5 rot; in
`_formel` den Mischteil streichen → Fall 6 (männlich) rot. Geschrieben, nicht gelaufen (nur auf Ansage).
"""
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.anhangformeln import G9anhangformeln  # noqa: E402
from Genesis9.anhangkopplung import G9anhangkopplung  # noqa: E402
from Genesis9.anhangmorphe import G9anhangmorphe  # noqa: E402
from Genesis9.formeln import G9formeln  # noqa: E402
from Genesis9.kanalnamen import G9kanalnamen  # noqa: E402
from Genesis9.morphablage import G9morphablage  # noqa: E402
from Genesis9.posen import G9posen  # noqa: E402
from Genesis9.smile81 import G9smile81  # noqa: E402


def kanal(kennung, **mehr):
    aus = {'id': kennung, 'name': kennung, 'alias': '', 'label': kennung, 'gruppe': '/Base', 'region': '', 'min': 0.0, 'max': 1.0, 'vorgabe': 0.0,
           'sichtbar': True, 'formeln': [], 'datei': 'x.dsf', 'hd': '', 'deltas': 0}
    aus.update(mehr)
    return aus


def ablage(*kanaele):
    k = {e['id']: e for e in kanaele}
    null = {e['id']: 0 for e in kanaele}
    return G9morphablage(k, np.zeros(0, dtype=np.int32), np.zeros((0, 3), dtype=np.float32), dict(null), dict(null))


def mal(eingang, faktor):
    return [{'op': 'push', 'kanal': eingang}, {'op': 'push', 'val': faktor}, {'op': 'mult'}]


class OhneBibliothek(SimpleTestCase):
    u"""`G9formeln.index` fragt die Anhänge — hier leer bzw. gestellt, nie die echte Bibliothek."""
    databases = set()
    WERTFORMELN = []

    def setUp(self):
        G9formeln.vergessen()
        self.addCleanup(G9formeln.vergessen)
        for name, liste in (('formeln', []), ('wertformeln', self.WERTFORMELN)):
            p = mock.patch.object(G9anhangformeln, name, classmethod(lambda cls, liste=liste: liste))
            p.start()
            self.addCleanup(p.stop)


class FormelnLesenTest(SimpleTestCase):
    databases = set()

    def test_1_wertformeln_neben_den_knochenformeln(self):
        roh = [{'output': 'Genesis9Mouth:/data/x/facs_bs_TongueIn.dsf#facs_bs_TongueIn?value',
                'operations': [{'op': 'push', 'url': 'Genesis9:#facs_ctrl_vER?value'}, {'op': 'push', 'val': 0.45}, {'op': 'mult'}]},
               {'output': 'Genesis9Mouth:#200_Head_bs_Mouth Depth-0xa1?value', 'stage': 'sum',
                'operations': [{'op': 'push', 'url': 'Genesis9:#200_head_bs_Mouth Cavity Depth Only?value'}, {'op': 'push', 'val': 1}, {'op': 'mult'}]},
               {'output': 'tongue01:/data/x/Genesis9Mouth.dsf#tongue01?rotation/y',
                'operations': [{'op': 'push', 'url': 'Genesis9Mouth:#facs_ctrl_TongueLeft-0xb2?value'}, {'op': 'push', 'val': 15}, {'op': 'mult'}]}]
        aus = G9anhangmorphe._formeln(roh, {'200_Head_bs_Mouth Depth-0xa1': '200_Head_bs_Mouth Depth', 'facs_ctrl_TongueLeft-0xb2': 'facs_ctrl_TongueLeft'})
        self.assertEqual(aus[0], {'morph': 'facs_bs_TongueIn', 'stufe': 'sum', 'ops': mal('facs_ctrl_vER', 0.45)})
        self.assertEqual(aus[1]['morph'], '200_Head_bs_Mouth Depth')
        self.assertEqual(aus[2], {'knochen': 'tongue01', 'kanal': 'rotation/y', 'stufe': 'sum', 'ops': mal('facs_ctrl_TongueLeft', 15)})
        morphe = G9anhangmorphe({}, formeln=aus)
        self.assertEqual([f['morph'] for f in morphe.wertformeln], ['facs_bs_TongueIn', '200_Head_bs_Mouth Depth'])


class GenauTest(SimpleTestCase):
    databases = set()

    def test_2_nur_name_oder_id(self):
        a = ablage(kanal('200_head_bs_Mouth Height-0x1', name='200_head_bs_Mouth Height', label='200+ Mouth Height'),
                   kanal('facs_bs_X'), kanal('alias_X', alias='facs_bs_X'))
        index = G9kanalnamen.von(a)
        self.assertIsNone(index.genau('200_Head_bs_Mouth Height'), 'der Mundmorph ist nicht der Lippenmorph des Körpers')
        self.assertEqual(index.aufloesen('200_Head_bs_Mouth Height'), '200_head_bs_Mouth Height-0x1', 'das Label fände ihn — darum genau')
        self.assertEqual(index.genau('200_head_bs_Mouth Height'), '200_head_bs_Mouth Height-0x1')
        self.assertEqual(index.genau('alias_X'), 'facs_bs_X')
        self.assertIsNone(index.genau('gibt_es_nicht'))


class KoerpergraphTest(OhneBibliothek):
    WERTFORMELN = [{'morph': 'facs_bs_TongueIn', 'stufe': 'sum', 'ops': mal('facs_ctrl_vER', 0.45)},
                   {'morph': '200_Head_bs_Mouth Height', 'stufe': 'sum', 'ops': mal('cav', 1.0)}]

    def test_3_wertformel_am_koerperkanal(self):
        a = ablage(kanal('facs_bs_TongueIn'), kanal('facs_ctrl_vER'), kanal('cav'),
                   kanal('200_head_bs_Mouth Height-0x1', name='200_head_bs_Mouth Height', label='200+ Mouth Height'))
        f = G9formeln({'facs_ctrl_vER': 1.0, 'cav': 1.0}, a)
        self.assertAlmostEqual(f.wert('facs_bs_TongueIn'), 0.45)
        self.assertEqual(f.wert('200_head_bs_Mouth Height-0x1'), 0.0, 'nur übers Label passend: nicht an den Körper')


class AnhangwertTest(OhneBibliothek):

    def test_4_eigener_kanal_ohne_koerpergegenstueck(self):
        a = ablage(kanal('cav'))
        morphe = G9anhangmorphe({'200_Head_bs_Mouth Depth': (np.array([0], dtype=np.int32), np.array([[0.01, 0, 0]], dtype=np.float32))},
                                formeln=[{'morph': '200_Head_bs_Mouth Depth', 'stufe': 'sum', 'ops': mal('cav', 1.0)}])
        formung = SimpleNamespace(morphwerte=lambda: {}, formeln=G9formeln({'cav': 0.5}, a))
        with mock.patch.object(G9morphablage, 'holen', return_value=a):
            werte = G9anhangkopplung.werte(morphe, formung)
            punkte = morphe.anwenden(np.zeros((1, 3)), werte)
        self.assertEqual(werte, {'200_Head_bs_Mouth Depth': 0.5})
        self.assertAlmostEqual(float(punkte[0, 0]), 0.005, places=6)


class PosenTest(SimpleTestCase):
    databases = set()

    def test_5_knochen_mit_dateiverweis(self):
        doc = SimpleNamespace(szene=lambda: {'animations': [
            {'url': 'hip:/data/DAZ%203D/Genesis%209/Base/Genesis9.dsf#hip?rotation/x/value', 'keys': [[0, 12.5]]},
            {'url': 'name://@selection/l_shoulder:?rotation/z/value', 'keys': [[0, -30.0]]},
            {'url': 'name://@selection#facs_ctrl_SmileFullFace:?value/value', 'keys': [[0, 0.4]]},
            {'url': 'name://@selection/r_hand:?rotation/y/value', 'keys': [[0, 0.0]]}]})
        knochen, regler = G9posen._lesen(doc)
        self.assertEqual(knochen, {'hip': {'rotation/x': 12.5}, 'l_shoulder': {'rotation/z': -30.0}})
        self.assertEqual(regler, {'facs_ctrl_SmileFullFace': 0.4})


class SmileTest(OhneBibliothek):

    def _ablage(self):
        return ablage(kanal('facs_ctrl_MouthSmile'), kanal('facs_ctrl_MouthDimple'), kanal('facs_ctrl_CheekSquint'),
                      kanal(G9smile81.MAENNLICH))

    def test_6_kanaele_und_anteile(self):
        a = self._ablage()
        G9smile81.anwenden(a)
        k = a.kanaele['facs_ctrl_SmileFullFace']
        self.assertEqual((k['label'], k['gruppe'], k['sichtbar'], k['deltas']), (u'Smile Full Face (8.1)', '/Pose Controls/Head/Expressions', True, 0))
        self.assertEqual({f['ziel'][1] for f in k['formeln']}, {'facs_ctrl_MouthSmile', 'facs_ctrl_MouthDimple', 'facs_ctrl_CheekSquint'},
                         'nur Ziele, die die Ablage hat')
        weiblich = G9formeln({'facs_ctrl_SmileFullFace': 1.0}, a)
        maennlich = G9formeln({'facs_ctrl_SmileFullFace': 1.0, G9smile81.MAENNLICH: 1.0}, a)
        self.assertAlmostEqual(weiblich.wert('facs_ctrl_MouthSmile'), 0.75)
        self.assertAlmostEqual(maennlich.wert('facs_ctrl_MouthSmile'), 0.65)
        self.assertAlmostEqual(maennlich.wert('facs_ctrl_CheekSquint'), 0.6)
        offen = G9formeln({'facs_ctrl_SmileOpenFullFace': 0.5}, a)
        self.assertAlmostEqual(offen.wert('facs_ctrl_MouthSmile'), 0.5)
        self.assertAlmostEqual(offen.posen()['liplowermiddle']['translation/y'], -0.15)
        self.assertAlmostEqual(offen.posen()['l_eyelidlower']['rotation/x'], 0.7125)

    def test_6b_ohne_ziele_kein_kanal_und_zweimal_gleich(self):
        leer = ablage(kanal('etwas'))
        G9smile81.anwenden(leer)
        self.assertNotIn('facs_ctrl_SmileFullFace', leer.kanaele)
        a = self._ablage()
        G9smile81.anwenden(a)
        vorher = dict(a.kanaele)
        G9smile81.anwenden(a)
        self.assertEqual(a.kanaele, vorher)

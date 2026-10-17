# -*- coding: utf-8 -*-
u"""Zweiter Durchgang „alle Genesis-Regler" (17.10.2026) — Kunstdaten, keine Daz-Bibliothek.

WARUM (Edgar, 17.10.2026: „Warum hast du diese unsichtbaren Regler nicht in das UI eingebaut? Wie kann es sein, dass Zungenregler im Server kein Ziel haben? das muss doch
ein bug sein. Die Presets können doch nicht ins Leere führen. Überprüfe nochmal intensiv alle deine Aussagen."). Drei Fehler, alle gemessen
(`ProjektTemp/_wegwerf/alter/zunge_suche.py`, `anhang_kopplung.py`, `unsichtbar_aufteilen.py`):

- die Formeln der Anhang-Morphs (Zunge drehen) wurden nie gelesen;
- ein Anhang fand seinen eigenen Morph nur über die Körper-ID und nur bei Kanälen MIT Körperdeltas — Wimpernform, Zungenmorphe, Pupille wirkten nie;
- ein Alias mit der ID seines Ziels (P3D Ursula) überschrieb den echten Kanal; die unsichtbaren wirksamen Kanäle standen nicht im Bedienfeld.

Zusagen:

1. `G9anhangkopplung.kopplung`: Körper-ID → eigener Morph über den NAMEN des Körperkanals (`head_bs_X-0x1` mit Namen `head_bs_X`); `paare` nimmt auch eigene Namen
   (Stil eines Haars) und jeden eigenen Morph höchstens einmal; `G9anhangmorphe.anwenden` rechnet die gekoppelten Deltas.
2. `G9anhangkopplung.werte`: dazu die gekoppelten Kanäle OHNE Körperdeltas (aus `formung.formeln.wert`), die `morphwerte` nicht führt.
3. `G9formeln` rechnet die Knochenformeln der Anhänge mit (`G9anhangformeln`): Tongue Left 1,0 → `tongue01?rotation/y` 15°; der Kanal ist für den Plan wirksam.
4. `G9morphablage._griff`: ein sichtbarer Alias mit derselben ID macht den unsichtbaren echten Kanal sichtbar (Label, Gruppe), seine Deltas bleiben.
5. `G9verborgeneregler.bauen`: unsichtbare wirksame Kanäle je Gruppe unter `/Hidden` ein Abschnitt „Verborgen (Daz) · …"; sichtbare ohne Bereich „Daz · …"; was im Plan steht,
   Alias und Wirkungsloses bleiben draußen.
6. `G9reglerplan._aliasgriffe`: ein sichtbarer Alias, dessen Ziel unsichtbar und wirksam ist, wird ein Regler mit dem Namen des ZIELS und dem Label des Alias.

Sabotage-Gegenprobe (nicht gefahren): in `kopplung` nur `ablage.kanaele` statt `nach_name` fragen → Fall 1 rot; in `werte` die Schleife streichen → Fall 2 rot; `_anhaenge_dazu`
in `G9formeln.index` streichen → Fall 3 rot; in `_griff` die Bedingung umdrehen → Fall 4 rot; in `bauen` den Test auf `sichtbar` streichen → Fall 5 rot. Geschrieben, nicht gelaufen
(nur auf Ansage).
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
from Genesis9.morphablage import G9morphablage  # noqa: E402
from Genesis9.reglerplan import G9reglerplan  # noqa: E402
from Genesis9.verborgeneregler import G9verborgeneregler  # noqa: E402


def kanal(kennung, **mehr):
    aus = {'id': kennung, 'name': kennung, 'alias': '', 'label': kennung, 'gruppe': '/Base', 'region': '', 'min': 0.0, 'max': 1.0, 'vorgabe': 0.0,
           'sichtbar': True, 'formeln': [], 'datei': 'x.dsf', 'hd': '', 'deltas': 0}
    aus.update(mehr)
    return aus


def ablage(*kanaele):
    k = {e['id']: e for e in kanaele}
    null = {e['id']: 0 for e in kanaele}
    return G9morphablage(k, np.zeros(0, dtype=np.int32), np.zeros((0, 3), dtype=np.float32), dict(null), dict(null))


def deltas(dx):
    return (np.array([0], dtype=np.int32), np.array([[dx, 0.0, 0.0]], dtype=np.float32))


class KopplungTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ablage = ablage(kanal('head_bs_X-0x1', name='head_bs_X'), kanal('head_bs_Wimper'))
        self.morphe = G9anhangmorphe({'head_bs_X': deltas(0.01), 'head_bs_Wimper': deltas(0.02), 'Stil': deltas(0.04)})
        holen = mock.patch.object(G9morphablage, 'holen', return_value=self.ablage)
        holen.start()
        self.addCleanup(holen.stop)

    def test_1_ueber_den_namen_gekoppelt(self):
        self.assertEqual(G9anhangkopplung.kopplung(self.morphe), {'head_bs_X-0x1': 'head_bs_X', 'head_bs_Wimper': 'head_bs_Wimper'})
        self.assertEqual(G9anhangkopplung.paare(self.morphe, {'head_bs_X-0x1': 0.5, 'Stil': 1.0, 'fremd': 1.0}),
                         {'head_bs_X-0x1': 'head_bs_X', 'Stil': 'Stil'})
        punkte = self.morphe.anwenden(np.zeros((1, 3)), {'head_bs_X-0x1': 0.5})
        self.assertAlmostEqual(float(punkte[0, 0]), 0.005, places=6)
        self.assertEqual(self.morphe.eigene({'head_bs_X-0x1': 0.5, 'fremd': 1.0}), {'head_bs_X-0x1': 0.5})

    def test_2_kanaele_ohne_koerperdeltas_kommen_dazu(self):
        formung = SimpleNamespace(morphwerte=lambda: {'head_bs_X-0x1': 0.5},
                                  formeln=SimpleNamespace(wert=lambda k: {'head_bs_Wimper': 0.7}.get(k, 0.0)))
        werte = self.morphe.werte(formung, {'Stil': 1.0})
        self.assertEqual(werte, {'head_bs_X-0x1': 0.5, 'head_bs_Wimper': 0.7, 'Stil': 1.0})


class AnhangformelnTest(SimpleTestCase):
    databases = set()

    def test_3_die_zunge_dreht_sich(self):
        formel = {'knochen': 'tongue01', 'kanal': 'rotation/y', 'stufe': 'sum',
                  'ops': [{'op': 'push', 'kanal': 'facs_ctrl_TongueLeft'}, {'op': 'push', 'val': 15}, {'op': 'mult'}]}
        a = ablage(kanal('facs_ctrl_TongueLeft', gruppe='/Pose Controls/Head/Mouth/Tongue'))
        G9formeln.vergessen()
        self.addCleanup(G9formeln.vergessen)
        with mock.patch.object(G9anhangformeln, 'formeln', classmethod(lambda cls: [formel])), \
                mock.patch.object(G9anhangformeln, 'wertformeln', classmethod(lambda cls: [])):
            posen = G9formeln({'facs_ctrl_TongueLeft': 1.0}, a).posen()
            wirksam = G9reglerplan.wirksame(a)
        self.assertEqual(posen, {'tongue01': {'rotation/y': 15.0}})
        self.assertIn('facs_ctrl_TongueLeft', wirksam)
        self.assertTrue(G9anhangformeln.ist_gelenk('center_point/z'))
        self.assertFalse(G9anhangformeln.ist_gelenk('rotation/x'))


class AliasTest(SimpleTestCase):
    databases = set()

    def test_4_alias_mit_derselben_id_ueberschreibt_den_kanal_nicht(self):
        echt = kanal('P3DUrsula_facs_bs_Innocent', sichtbar=False, gruppe='/Hidden/People', label='intern', deltas=120)
        alias = kanal('P3DUrsula_facs_bs_Innocent', alias='P3DUrsula_facs_bs_Innocent', gruppe='/Pose Controls/Head/Expressions/Ursula', label='P3D Ursula Innocent')
        G9morphablage._griff(echt, alias)
        self.assertEqual((echt['sichtbar'], echt['label'], echt['gruppe'], echt['alias'], echt['deltas']),
                         (True, 'P3D Ursula Innocent', '/Pose Controls/Head/Expressions/Ursula', '', 120))

    def test_6_sichtbarer_alias_fuer_ein_unsichtbares_ziel(self):
        a = ablage(kanal('facs_bs_JawForward', sichtbar=False, gruppe='/Pose Controls/Head/Cheek and Jaw/Sub-Components', label='intern'),
                   kanal('alias_head_facs_bs_JawForward-0x1', alias='facs_bs_JawForward', gruppe='/Pose Controls/Head/Cheek and Jaw', label='Jaw Forward'))
        aus = G9reglerplan._aliasgriffe(a, {'facs_bs_JawForward'}, set())
        self.assertEqual([(r['name'], r['anzeige'], r['bereich'], r['art']) for r in aus], [('facs_bs_JawForward', 'Jaw Forward', 'mimik', 'pose')])
        self.assertEqual(G9reglerplan._aliasgriffe(a, set(), set()), [], 'ein wirkungsloses Ziel bleibt draußen')


class VerborgenTest(SimpleTestCase):
    databases = set()

    def test_5_abschnitte_je_gruppe(self):
        a = ablage(kanal('body_cbs_hand_y28n_l', sichtbar=False, gruppe='/Hidden/Base Correctives/Hands'),
                   kanal('body_cbs_knie', sichtbar=False, gruppe='/Hidden/Base Correctives/Legs'),
                   kanal('facs_bs_ChestVolumeFixLeft', gruppe='/Tools', label='Chest Volume Fix Left'),
                   kanal('body_bs_Sichtbar', gruppe='/Full Body/Base', region='Actor'),
                   kanal('alias_x', alias='body_cbs_knie', sichtbar=False, gruppe='/Hidden/Base Correctives/Legs'),
                   kanal('ohne_wirkung', sichtbar=False, gruppe='/Hidden/Base Correctives/Legs'),
                   kanal('im_plan', sichtbar=False, gruppe='/Hidden/Base Correctives/Legs'))
        wirksam = {'body_cbs_hand_y28n_l', 'body_cbs_knie', 'facs_bs_ChestVolumeFixLeft', 'body_bs_Sichtbar', 'alias_x', 'im_plan'}
        aus = G9verborgeneregler.bauen(a, wirksam, {'im_plan'})
        self.assertEqual([(b['schluessel'], b['name']) for b in aus],
                         [('verborgen_base_correctives', u'Verborgen (Daz) · Base Correctives'), ('verborgen_tools', u'Daz · Tools')])
        self.assertEqual([r['anzeige'] for r in aus[0]['regler']], ['Hands · body_cbs_hand_y28n_l', 'Legs · body_cbs_knie'])
        self.assertTrue(all(r['art'] == 'pose' and r['bereich'] == 'verborgen_base_correctives' for r in aus[0]['regler']))
        self.assertNotIn('_sichtbar', aus[0]['regler'][0])

# -*- coding: utf-8 -*-
"""Der Spielraum der Formregler (08.10.2026, Edgar: „kannst du die Klemme ±1 nicht aufheben??").

WARUM: Genesis klemmte jeden Formregler bei Dazʼ Grenze (±1). Am Lauf `Edgar - Hunyan Regionen` blieben fünf Regler auch bei kleinster Reglersumme
(gleiche Verformung auf 0,7 mm) auf ±1: `Neck Depth back`, `Glute Crease`, `Mass Wrist`, `Taper Shin B`, `Thigh Depth` — das Netz verlangt mehr, als Daz
hergibt. Ein ausdrücklich gestellter Wert gilt jetzt bis ×2 (`G9reglergrenzen.SPIELRAUM`); die Anpassung darf ihn über die Option `koerper.spielraum`
ausnutzen. Geprüft mit Kunstkanälen, ohne Daz-Bibliothek:

1. `anwenden`: `weit_min`/`weit_max` nur an Formreglern mit Deltas — NICHT an Größen (`Proportion…`), Charakteren (`/People`, `_figure_ctrl_`),
   Posensteuerungen, Verstecktem; `min`/`max` des Bedienfelds bleiben.
2. `G9formeln.wert`: ein gestellter Wert über Dazʼ Grenze gilt bis ×2 (auch ins Minus); darüber wird er gekappt; was nur über Formeln aufsummiert wird,
   bleibt an Dazʼ Grenze (bestehende Charaktere ändern sich nicht).
3. `Meshfigurregler.grenzen`: × Faktor nur für Regler mit Spielraum UND Stufe 3 (Körperbereiche); Körpertypen/Charaktere und Eigenmorphe bleiben;
   Faktor 1 gibt die Grenzen der Ableitung unverändert zurück.
4. Option `koerper.spielraum` (aus/150/200, Vorgabe aus) und ihr Weg über Lauf und Kette.

Sabotage: in `grenzen_gestellt` die `weit_*`-Zeilen streichen → Fall 2 rot; in `Meshfigurregler.grenzen` die Stufenprüfung streichen → Fall 3 rot;
in `mit_spielraum` die `OHNE_SPIELRAUM`-Zeile streichen → Fall 1 rot.
"""
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.formeln import G9formeln
from Genesis9.reglergrenzen import G9reglergrenzen

from core.dienste.engine2d3dkleiderkoerperoptionen import Engine2d3dKleiderkoerperoptionen as O
from core.dienste.meshfigurregler import Meshfigurregler

DIENSTE = Path(__file__).resolve().parents[2] / 'dienste'


class _Ablage:
    """Kunstablage: Kanäle und wer Deltas hat."""

    def __init__(self, kanaele, mit_deltas=()):
        self.kanaele = kanaele
        self._deltas = set(mit_deltas)

    def hat_deltas(self, kennung):
        return kennung in self._deltas


def kanal(kennung, gruppe, lo=-1.0, hi=1.0):
    return {'id': kennung, 'label': kennung, 'gruppe': gruppe, 'region': '', 'min': lo, 'max': hi, 'vorgabe': 0.0, 'sichtbar': True, 'hd': '', 'formeln': []}


def formel(quelle, ziel, faktor):
    return {'ziel': ('morph', ziel, 'value'), 'stufe': 'sum',
            'ops': [{'op': 'push', 'kanal': quelle}, {'op': 'push', 'val': faktor}, {'op': 'mult'}]}


class SpielraumGenesisTest(SimpleTestCase):
    databases = set()

    def ablage(self):
        k = {
            'body_bs_MassWrist': kanal('body_bs_MassWrist', '/Full Body/Shaping'),
            'body_bs_ProportionHeight': kanal('body_bs_ProportionHeight', '/Full Body/Base', -2.0, 2.0),
            'Kin9_figure_ctrl_Character': kanal('Kin9_figure_ctrl_Character', '/People/Feminine', 0.0, 1.0),
            'body_ctrl_BreastsFlatten': kanal('body_ctrl_BreastsFlatten', '/Pose Controls/Torso', 0.0, 1.0),
            'body_cbs_x': kanal('body_cbs_x', '/Hidden/Correctives'),
            'body_ctrl_ohne': kanal('body_ctrl_ohne', '/Full Body/Base'),
            'body_bs_BodyHeavy': kanal('body_bs_BodyHeavy', '/Full Body/Shaping', 0.0, 1.0),
        }
        return _Ablage(k, mit_deltas=('body_bs_MassWrist', 'body_bs_ProportionHeight', 'Kin9_figure_ctrl_Character',
                                      'body_ctrl_BreastsFlatten', 'body_cbs_x', 'body_bs_BodyHeavy'))

    def test_1_spielraum_nur_an_formreglern(self):
        ablage = self.ablage()
        G9reglergrenzen.anwenden(ablage)
        k = ablage.kanaele
        self.assertEqual((k['body_bs_MassWrist']['weit_min'], k['body_bs_MassWrist']['weit_max']), (-2.0, 2.0))
        self.assertEqual((k['body_bs_MassWrist']['min'], k['body_bs_MassWrist']['max']), (-1.0, 1.0))       # das Bedienfeld bleibt bei Daz
        # einseitig und zweiseitig gemacht: -max..max wird ×2
        self.assertEqual((k['body_bs_BodyHeavy']['min'], k['body_bs_BodyHeavy']['weit_min'], k['body_bs_BodyHeavy']['weit_max']), (-1.0, -2.0, 2.0))
        for ohne in ('body_bs_ProportionHeight', 'Kin9_figure_ctrl_Character', 'body_ctrl_BreastsFlatten', 'body_cbs_x', 'body_ctrl_ohne'):
            self.assertNotIn('weit_max', k[ohne], ohne)

    def test_2_gestellter_wert_gilt_bis_zum_doppelten(self):
        ablage = _Ablage({
            'body_bs_MassWrist': kanal('body_bs_MassWrist', '/Full Body/Shaping'),
            'body_bs_ThighDepth': kanal('body_bs_ThighDepth', '/Full Body/Shaping'),
            'Fabrice_body_bs_body': kanal('Fabrice_body_bs_body', '/Full Body/People', 0.0, 1.0),
        }, mit_deltas=('body_bs_MassWrist', 'body_bs_ThighDepth', 'Fabrice_body_bs_body'))
        ablage.kanaele['Fabrice_body_bs_body']['formeln'] = [formel('Fabrice_body_bs_body', 'body_bs_ThighDepth', 1.4)]
        G9reglergrenzen.anwenden(ablage)
        G9formeln.vergessen()
        try:
            def wert(gesetzt, name):
                return G9formeln(gesetzt, ablage).wert(name)
            self.assertAlmostEqual(wert({'body_bs_MassWrist': 1.5}, 'body_bs_MassWrist'), 1.5)
            self.assertAlmostEqual(wert({'body_bs_MassWrist': 3.0}, 'body_bs_MassWrist'), 2.0)             # bei ×2 gekappt
            self.assertAlmostEqual(wert({'body_bs_MassWrist': -1.5}, 'body_bs_MassWrist'), -1.5)
            self.assertAlmostEqual(wert({'body_bs_MassWrist': -3.0}, 'body_bs_MassWrist'), -2.0)
            self.assertAlmostEqual(wert({'body_bs_MassWrist': 0.5}, 'body_bs_MassWrist'), 0.5)             # innerhalb Daz: unverändert
            # nur über eine Formel aufsummiert (1,4): bleibt an Dazʼ Grenze — bestehende Charaktere ändern sich nicht
            self.assertAlmostEqual(wert({'Fabrice_body_bs_body': 1.0}, 'body_bs_ThighDepth'), 1.0)
        finally:
            G9formeln.vergessen()

    def test_3_grenzen_der_anpassung_nur_fuer_koerperbereiche(self):
        daz = np.array([[-1.0, 1.0], [-1.0, 1.0], [0.0, 1.0], [-2.0, 2.0]])
        a = mock.Mock(grenzen=daz, namen=['body_bs_MassWrist', 'body_bs_BodyHeavy', 'Kin9_body_bs_Body', 'eigen:region_hals'],
                      paare={'body_bs_MassWrist': ['body_bs_MassWrist'], 'body_bs_BodyHeavy': ['body_bs_BodyHeavy'],
                             'Kin9_body_bs_Body': ['Kin9_body_bs_Body'], 'eigen:region_hals': ['eigen:region_hals']})
        plan = [{'name': 'body_bs_MassWrist', 'bereich': 'haende', 'weit_min': -2.0, 'weit_max': 2.0},
                {'name': 'body_bs_BodyHeavy', 'bereich': 'koerper', 'weit_min': -2.0, 'weit_max': 2.0},       # Körpertyp (Stufe 2): kein Spielraum
                {'name': 'Kin9_body_bs_Body', 'bereich': 'figur', 'weit_max': 2.0, 'weit_min': 0.0},          # Charakter (Stufe 2)
                {'name': 'eigen:region_hals', 'bereich': 'region'}]
        r = Meshfigurregler({}, spielraum=2.0)
        with mock.patch.object(Meshfigurregler, 'ableitung', return_value=a), \
                mock.patch('Genesis9.reglerableitung.G9reglerableitung.regler', return_value=plan):
            g = r.grenzen('koerper')
        self.assertEqual(g[0].tolist(), [-2.0, 2.0])                  # Mass Wrist: ×2
        self.assertEqual(g[1].tolist(), [-1.0, 1.0])                  # Körpertyp bleibt
        self.assertEqual(g[2].tolist(), [0.0, 1.0])                   # Charakter bleibt
        self.assertEqual(g[3].tolist(), [-2.0, 2.0])                  # Eigenmorph hat seine eigene Grenze
        # Faktor 1,5 und Faktor 1
        r15 = Meshfigurregler({}, spielraum=1.5)
        with mock.patch.object(Meshfigurregler, 'ableitung', return_value=a), \
                mock.patch('Genesis9.reglerableitung.G9reglerableitung.regler', return_value=plan):
            self.assertEqual(r15.grenzen('koerper')[0].tolist(), [-1.5, 1.5])
        r1 = Meshfigurregler({})
        with mock.patch.object(Meshfigurregler, 'ableitung', return_value=a):
            self.assertIs(r1.grenzen('koerper'), daz)

    def test_4_option_und_weg_durch_die_kette(self):
        katalog = {e['schluessel']: e for e in O.katalog()['optionen']}
        self.assertEqual(katalog['spielraum']['vorgabe'], 'aus')
        self.assertEqual([w[0] for w in katalog['spielraum']['werte']], ['aus', '150', '200'])
        self.assertEqual(O.pruefen({})['spielraum'], 'aus')
        self.assertEqual(O.pruefen({'spielraum': '200'})['spielraum'], '200')
        self.assertEqual(O.pruefen({'spielraum': '999'})['spielraum'], 'aus')
        lauf = (DIENSTE / 'engine2d3dkleiderkoerperlauf.py').read_text(encoding='utf-8')
        self.assertIn("{'150': 1.5, '200': 2.0}.get((koerperoptionen or {}).get('spielraum'), 1.0)", lauf)
        kette = (DIENSTE / 'meshfigurkette.py').read_text(encoding='utf-8')
        self.assertIn("getattr(self.lauf, 'spielraum', 1.0)", kette)

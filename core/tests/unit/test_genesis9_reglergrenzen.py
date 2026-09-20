# -*- coding: utf-8 -*-
"""`G9reglergrenzen`: einseitige Formregler (Daz 0..max) werden zweiseitig.

WARUM (Edgar, 20.09.2026: „ich kann die Brust von Kin nicht verkleinern??
… ich will Regler, die nicht bei 0 anfangen"): „Breasts Large" kam von Daz
mit 0..1; ein Charakter mit eigener Brustform liess sich darueber nicht
verkleinern. Wie Daz Studio mit „Limits off" darf der Regler jetzt ins
Minus. Geprueft mit Kunstkanaelen, ohne Daz-Bibliothek:

1. `anwenden`: 0..1 mit Deltas -> -1..1 und `daz_min` 0; 0..2 -> -2..2;
   nur-HD zaehlt wie Deltas. NICHT: Posensteuerungen, `/People` (Charaktere
   und ihre Teile), `/Hidden`, schon zweiseitige, Steuerregler ohne Deltas.
2. Zweimal anwenden aendert nichts mehr (die Regel verlangt `min == 0`).
3. `G9formeln.wert`: ein SELBST gestellter zweiseitiger Regler geht ins
   Minus; ein nur ueber Formeln negativ gezogener bleibt auf Daz' Grenze
   (Fabrice zog `Proportion Larger` auf -0,02 — das waere eine stille
   Aenderung der Figur gewesen).

Sabotage: in `zweiseitig` die `/People`-Ausnahme streichen -> Fall 1 rot;
in `G9formeln.wert` `daz_min` durch `min` ersetzen -> Fall 3 rot.
"""
from django.test import SimpleTestCase
from Genesis9.formeln import G9formeln
from Genesis9.reglergrenzen import G9reglergrenzen


class _Ablage:
    """Kunstablage: Kanaele und wer Deltas hat."""

    def __init__(self, kanaele, mit_deltas=()):
        self.kanaele = kanaele
        self._deltas = set(mit_deltas)

    def hat_deltas(self, kennung):
        return kennung in self._deltas


def kanal(kennung, gruppe, lo=0.0, hi=1.0, hd='', formeln=()):
    return {'id': kennung, 'label': kennung, 'gruppe': gruppe, 'region': '',
            'min': lo, 'max': hi, 'vorgabe': 0.0, 'sichtbar': True, 'hd': hd,
            'formeln': list(formeln)}


def formel(quelle, ziel, faktor):
    return {'ziel': ('morph', ziel, 'value'), 'stufe': 'sum',
            'ops': [{'op': 'push', 'kanal': quelle}, {'op': 'push', 'val': faktor},
                    {'op': 'mult'}]}


class ReglergrenzenTest(SimpleTestCase):
    databases = set()

    def ablage(self):
        k = {
            'body_bs_BreastSize': kanal('body_bs_BreastSize', '/Feminine'),
            'body_bs_ProportionLarger': kanal('body_bs_ProportionLarger', '/Full Body/Base', 0.0, 2.0),
            'body_bs_Nipples_HD3': kanal('body_bs_Nipples_HD3', '/Feminine', hd='x.dhdm'),
            'body_bs_GluteSize': kanal('body_bs_GluteSize', '/Base', -1.0, 1.0),
            'body_ctrl_BreastsFlatten': kanal('body_ctrl_BreastsFlatten', '/Pose Controls/Torso/Feminine'),
            'Kin9_figure_ctrl_Character': kanal('Kin9_figure_ctrl_Character', '/People/Feminine'),
            'Kin9_body_bs_Body': kanal('Kin9_body_bs_Body', '/Full Body/People/Feminine'),
            'body_ctrl_BodyFitness': kanal('body_ctrl_BodyFitness', '/Full Body/Base'),
            'body_cbs_x': kanal('body_cbs_x', '/Hidden/Correctives'),
        }
        return _Ablage(k, mit_deltas=('body_bs_BreastSize', 'body_bs_ProportionLarger',
                                      'body_bs_GluteSize', 'body_ctrl_BreastsFlatten',
                                      'Kin9_figure_ctrl_Character', 'Kin9_body_bs_Body',
                                      'body_cbs_x'))

    def test_1_zweiseitig_nur_formregler_mit_deltas(self):
        ablage = self.ablage()
        self.assertEqual(G9reglergrenzen.anwenden(ablage), 3)
        k = ablage.kanaele
        self.assertEqual((k['body_bs_BreastSize']['min'], k['body_bs_BreastSize']['daz_min']), (-1.0, 0.0))
        gross = k['body_bs_ProportionLarger']
        self.assertEqual((gross['min'], gross['max'], gross['daz_min']), (-2.0, 2.0, 0.0))
        self.assertEqual(k['body_bs_Nipples_HD3']['min'], -1.0)              # nur HD
        for bleibt in ('body_bs_GluteSize', 'body_ctrl_BreastsFlatten', 'Kin9_figure_ctrl_Character',
                       'Kin9_body_bs_Body', 'body_ctrl_BodyFitness', 'body_cbs_x'):
            self.assertNotIn('daz_min', k[bleibt], bleibt)
        self.assertEqual(k['body_bs_GluteSize']['min'], -1.0)
        self.assertEqual(k['body_ctrl_BreastsFlatten']['min'], 0.0)
        self.assertEqual(G9reglergrenzen.daz_min(k['body_bs_BreastSize']), 0.0)
        self.assertEqual(G9reglergrenzen.daz_min(k['body_bs_GluteSize']), -1.0)

    def test_2_zweimal_anwenden_aendert_nichts(self):
        ablage = self.ablage()
        G9reglergrenzen.anwenden(ablage)
        self.assertEqual(G9reglergrenzen.anwenden(ablage), 0)
        self.assertEqual(ablage.kanaele['body_bs_BreastSize']['min'], -1.0)

    def test_3_formeln_nur_selbst_gestellt_ins_minus(self):
        ablage = _Ablage({
            'body_bs_BreastSize': kanal('body_bs_BreastSize', '/Feminine'),
            'body_bs_ProportionLarger': kanal('body_bs_ProportionLarger', '/Full Body/Base', 0.0, 2.0),
            'Fabrice_body_bs_body': kanal('Fabrice_body_bs_body', '/Full Body/People', formeln=[
                formel('Fabrice_body_bs_body', 'body_bs_ProportionLarger', -0.02)]),
        }, mit_deltas=('body_bs_BreastSize', 'body_bs_ProportionLarger', 'Fabrice_body_bs_body'))
        G9reglergrenzen.anwenden(ablage)
        G9formeln.vergessen()
        try:
            # selbst gestellt: ins Minus, begrenzt auf -max
            def wert(gesetzt, kanal):
                return G9formeln(gesetzt, ablage).wert(kanal)
            self.assertAlmostEqual(wert({'body_bs_BreastSize': -0.5}, 'body_bs_BreastSize'), -0.5)
            self.assertAlmostEqual(wert({'body_bs_BreastSize': -3.0}, 'body_bs_BreastSize'), -1.0)
            # nur ueber Formeln negativ: bleibt auf Daz' Grenze 0
            f = G9formeln({'Fabrice_body_bs_body': 1.0}, ablage)
            self.assertEqual(f.wert('body_bs_ProportionLarger'), 0.0)
            # selbst gestellt UND Formel: die Summe darf negativ sein
            g = G9formeln({'Fabrice_body_bs_body': 1.0, 'body_bs_ProportionLarger': -0.5}, ablage)
            self.assertAlmostEqual(g.wert('body_bs_ProportionLarger'), -0.52)
        finally:
            G9formeln.vergessen()

# -*- coding: utf-8 -*-
"""`G9reglersperre`: Regler, die eine KI nicht stellen darf, nur der Mensch im Bedienfeld (28.10.2026).

WARUM (Edgar, 28.10.2026: „diese komischen Morphs … flaggen, damit die AI diese nicht bedienen kann, sondern nur im UI bedienbar“): In der Startfigur von EdgarTrip falteten
`hb:Shoulders_Length` und `hb:Shoulders_SizeX` die Hände; die Einpassung Mesh → Genesis übernahm sie. Geprüft mit einer Sperrliste in einem Wegwerf-Ordner, ohne Messung:

1. `aus_messung` schreibt schädliche Regler UND alle Regler der figurgebundenen Bereiche (Modell-Eigen, Kopf-Eigen, Mesh); unschädliche nicht.
2. `gesperrt`/`grund`/`erlaubt` lesen sie; neue Mesh-Regler (`eigen:mesh_*`) gelten über die Vorsilbe, auch ohne Liste.
3. `G9reglerplan._sperre_markieren` markiert im Bedienfeld (`ki_gesperrt`, Hinweis) — EINMAL, auch bei wiederholtem Aufruf (die Einträge sind zwischengespeichert; der erste Bau
   hängte den Hinweis bei jedem Aufruf neu an).
4. `G9meshgenesis` nimmt gesperrte Regler aus der Startfigur (Prüfung am Code-Pfad über `erlaubt`).
"""
import shutil
from pathlib import Path

from django.test import SimpleTestCase
from Genesis9.reglerplan import G9reglerplan
from Genesis9.reglersperre import G9reglersperre

BERICHT = {'gemessen': '2026-10-28 11:23', 'schwelle': [10, 10], 'regler': {
    'hb:Shoulders_Length': {'schaedlich': True, 'werte': {'-1.0': {'kaputt': 124, 'umgeklappt': 1948}}},
    'hb:Torso_Mass': {'schaedlich': False, 'werte': {'1.0': {'kaputt': 0, 'umgeklappt': 0}}}}}
BEREICHE = [{'schluessel': 'modell_eigen', 'name': 'Modell-Eigen', 'regler': [{'name': 'eigen:rainy_mesh_165543'}]},
            {'schluessel': 'hb_koerper', 'name': 'HB-Morphs Körper', 'regler': [{'name': 'hb:Torso_Mass'}]}]


class _Ablage:
    def __init__(self):
        self.pfad = Path(__file__).parent / 'tmp_reglersperre'
        from Genesis9.pfade import G9pfade
        self.pfade, self.alt = G9pfade, G9pfade.ablage

    def __enter__(self):
        shutil.rmtree(self.pfad, ignore_errors=True)
        self.pfade.ablage = classmethod(lambda cls: self.pfad)
        G9reglersperre.vergessen()
        return self.pfad

    def __exit__(self, *_):
        self.pfade.ablage = self.alt
        G9reglersperre.vergessen()
        shutil.rmtree(self.pfad, ignore_errors=True)


class ReglersperreTest(SimpleTestCase):
    databases = set()

    def test_1_messung_und_figurgebundene_bereiche_werden_gesperrt(self):
        with _Ablage():
            self.assertEqual(G9reglersperre.aus_messung(BERICHT, BEREICHE), 2)
            self.assertTrue(G9reglersperre.gesperrt('hb:Shoulders_Length'))
            self.assertIn('1948 umgeklappt', G9reglersperre.grund('hb:Shoulders_Length'))
            self.assertTrue(G9reglersperre.gesperrt('eigen:rainy_mesh_165543'))
            self.assertFalse(G9reglersperre.gesperrt('hb:Torso_Mass'))

    def test_2_vorsilbe_und_erlaubt_auch_ohne_liste(self):
        with _Ablage():
            self.assertTrue(G9reglersperre.gesperrt('eigen:mesh_edgartrip_l_hand'))
            self.assertFalse(G9reglersperre.gesperrt('hb:Shoulders_Length'))          # ohne Liste nur die Vorsilbe (Warnung im Log)
            self.assertEqual(G9reglersperre.erlaubt({'eigen:mesh_x_kopf': 1.0, 'body_bs_BodyHeavy': 0.2}), {'body_bs_BodyHeavy': 0.2})

    def test_3_bedienfeld_markiert_einmal(self):
        with _Ablage():
            G9reglersperre.aus_messung(BERICHT, BEREICHE)
            bereiche = [{'schluessel': 'hb_koerper', 'regler': [{'name': 'hb:Shoulders_Length', 'hinweis': 'Schulterlänge'}, {'name': 'hb:Torso_Mass'}]}]
            for _ in range(3):
                G9reglerplan._sperre_markieren(bereiche)
            gesperrt, frei = bereiche[0]['regler']
            self.assertTrue(gesperrt['ki_gesperrt'])
            self.assertEqual(gesperrt['hinweis'].count('Für KI gesperrt'), 1)
            self.assertTrue(gesperrt['hinweis'].startswith('Schulterlänge'))
            self.assertNotIn('ki_gesperrt', frei)

    def test_4_einpassung_nimmt_gesperrte_aus_der_startfigur(self):
        with _Ablage():
            G9reglersperre.aus_messung(BERICHT, BEREICHE)
            grund = {'hb:Shoulders_Length': -1.0, 'hb:Torso_Mass': 0.07, 'eigen:mesh_edgartrip_kopf': 1.0}
            self.assertEqual(G9reglersperre.erlaubt(grund), {'hb:Torso_Mass': 0.07})
            import inspect
            from Genesis9.meshgenesis import G9meshgenesis
            self.assertIn('G9reglersperre.erlaubt(grund)', inspect.getsource(G9meshgenesis.einpassen))

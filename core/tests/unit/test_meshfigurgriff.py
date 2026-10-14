# -*- coding: utf-8 -*-
"""Der Griff und der Stab in der Ruhelage (14.10.2026, `Meshfigurgriff`, `Blendimportrequisit.ruhelage_gehalten`) — Edgar: „der Zauberstab geht durch den Körper bei der Animation", „die Hand muss um den Zauberstab sein".
Nicht gelaufen — läuft nur auf Ansage.

    RuhelageTest   ein Gegenstand in der Hand behält seine Ausrichtung und wandert nur mit der Hand (Kunstdaten: die Hand dreht um 130°, der Stab bleibt senkrecht, der Abstand zur Handmitte bleibt); `ruhelage` dagegen dreht ihn mit;
                   `Meshfigurteile` wählt den Weg nach dem Kontaktteil
    GriffTest      Halter aus `ergebnis.teile`, Ziel der Suche (Sapiens-Hand binnen Reichweite), Winkel in die Haltung legen (nur gültige Haltung, nur angenommene Seiten), Stempel und Ablage, Einhängung in die Vorschau

Sabotage: in `ruhelage_gehalten` die Zeile `schritt = …` durch eine Drehung ersetzen → `test_der_stab_bleibt_senkrecht` rot; in `anwenden` die Prüfung `gueltig` streichen → `test_ohne_gueltige_haltung_wird_nichts_angelegt` rot; in `halter` die Prüfung `gehalten` streichen
→ `test_nur_gehaltene_gegenstaende_nennen_eine_hand` rot.
"""

import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportrequisit import Blendimportrequisit
from core.dienste.meshfigurgriff import Meshfigurgriff

from ._pruefablage import Pruefablage

WEB = Path(__file__).resolve().parents[3]


def drehung_x(grad):
    w = np.radians(grad)
    return np.array([[1, 0, 0], [0, np.cos(w), -np.sin(w)], [0, np.sin(w), np.cos(w)]])


class RuhelageTest(SimpleTestCase):
    HAND = 11

    def _lage(self):
        """Eine Hand von 300 Punkten: in der Haltung vorn gehoben, in der Ruhe um 130° gedreht und seitlich verschoben; dazu ein senkrechter Stab (Achse y), den die Hand an einem Punkt umschließt."""
        rng = np.random.default_rng(3)
        hand_h = rng.normal(0.0, 0.04, (300, 3)) + np.array([-0.47, 1.31, 0.43])
        r = drehung_x(130.0)
        hand_r = (hand_h - hand_h.mean(axis=0)) @ r.T + np.array([-0.68, 0.98, 0.04])
        teil = np.full(300, self.HAND)
        lage = SimpleNamespace(teil=teil, kaefig_posiert=hand_h, kaefig_ruhe=hand_r, finger_bewegt=np.zeros(300, dtype=bool), ins_netz=lambda p: np.asarray(p, dtype=np.float64), h=0.004)
        stab = np.column_stack([np.full(200, -0.43), np.linspace(0.4, 2.1, 200), np.full(200, 0.40)])      # senkrecht, 42 mm neben der Handmitte
        return lage, stab, hand_h

    def test_der_stab_bleibt_senkrecht(self):
        lage, stab, _ = self._lage()
        punkte, _ = Blendimportrequisit(lage).ruhelage_gehalten(stab, self.HAND)
        achse = np.linalg.svd(punkte - punkte.mean(axis=0), full_matrices=False)[2][0]
        self.assertAlmostEqual(abs(achse[1]), 1.0, places=6)

    def test_die_hand_haelt_ihn_an_derselben_stelle(self):
        lage, stab, hand_h = self._lage()
        punkte, schritt = Blendimportrequisit(lage).ruhelage_gehalten(stab, self.HAND)
        vorher = np.linalg.norm(hand_h.mean(axis=0)[[0, 2]] - stab[0, [0, 2]])                      # die Achse ist senkrecht: der Abstand liegt in x und z
        nachher = np.linalg.norm(lage.kaefig_ruhe.mean(axis=0)[[0, 2]] - punkte[0, [0, 2]])
        self.assertAlmostEqual(vorher, nachher, places=9, msg='Abstand der Handmitte zur Stabachse bleibt')
        self.assertGreater(schritt, 100.0, 'die Hand ist über 40 cm gewandert, der Stab mit')

    def test_ruhelage_dreht_ihn_mit_der_hand(self):
        lage, stab, _ = self._lage()
        punkte, _ = Blendimportrequisit(lage).ruhelage(stab, self.HAND)
        achse = np.linalg.svd(punkte - punkte.mean(axis=0), full_matrices=False)[2][0]
        self.assertLess(abs(achse[1]), 0.9, 'der alte Weg legt den Stab um (er stach durch den Rumpf)')

    def test_ohne_handpunkte_gilt_die_starrkoerperbewegung(self):
        lage, stab, _ = self._lage()
        lage.teil = np.full(300, 3)
        punkte, _ = Blendimportrequisit(lage).ruhelage_gehalten(stab, self.HAND)
        alt, _ = Blendimportrequisit(lage).ruhelage(stab, self.HAND)
        self.assertEqual(punkte.shape, alt.shape)

    def test_nur_die_haende_tragen(self):
        self.assertEqual(Blendimportrequisit.TRAEGER, ('l_hand', 'r_hand'))

    def test_die_teile_wahl_haengt_am_kontaktteil(self):
        text = (WEB / 'core' / 'dienste' / 'meshfigurteile.py').read_text(encoding='utf-8')
        self.assertIn("erkannt['teil'] in Blendimportrequisit.TRAEGER", text)
        self.assertIn("haelt['stabfoermig']", text, 'nur lange, dünne Gegenstände hängen an der Schwerkraft; ein Schild dreht mit dem Arm')
        self.assertIn('Meshfigurhalter.pruefen(scan, halter[0], punkte, halter[1])', text, 'welche Hand hält, entscheidet das Netz')
        self.assertIn('requisit.ruhelage_gehalten if gehalten else requisit.ruhelage', text)
        # der Blender-Import behält die Starrkörperbewegung der Hand (die Figur schließt dort beim Tragen die Faust)
        self.assertNotIn('ruhelage_gehalten', (WEB / 'core' / 'dienste' / 'blendimportstuecke.py').read_text(encoding='utf-8'))


class HalterTest(SimpleTestCase):
    """`Meshfigurhalter`: das Netz entscheidet, welche Hand einen Bestandteil hält (Handflächen von Sapiens, die ihn berühren) — nicht das nächste Körperteil der Figur."""

    def _netz(self, abstand=0.01):
        """Ein Stab (Linie, 1,7 m) und 400 Handflächen (Dreiecke) in `abstand` Meter Entfernung um seine Mitte; dazu 50 Flächen weit weg."""
        stab = np.column_stack([np.zeros(300), np.linspace(0.4, 2.1, 300), np.zeros(300)])
        rng = np.random.default_rng(5)
        mitte = np.column_stack([np.full(400, abstand), rng.uniform(1.2, 1.3, 400), rng.uniform(-0.02, 0.02, 400)])
        weit = np.column_stack([np.full(50, 0.8), rng.uniform(0.9, 1.0, 50), np.zeros(50)])
        flaechenmitten = np.vstack([mitte, weit])
        punkte = np.repeat(flaechenmitten, 3, axis=0)
        flaechen = np.arange(len(punkte)).reshape(-1, 3)
        klassen = np.zeros((len(flaechen), 28))
        klassen[:200, 14] = 10          # rechte Hand
        klassen[200:, 5] = 10           # dieselben Handflächen, von Sapiens teils als LINKE Hand gesehen — beide Etiketten zählen
        return SimpleNamespace(punkte=punkte, flaechen=flaechen), klassen, stab

    def test_die_beruehrende_hand_ist_die_naechste_figurhand(self):
        from core.dienste.meshfigurhalter import Meshfigurhalter

        scan, klassen, stab = self._netz()
        haende = {'r': np.array([0.12, 1.25, 0.2]), 'l': np.array([0.9, 1.25, 0.2])}
        h = Meshfigurhalter.pruefen(scan, klassen, stab, haende)
        self.assertEqual(h['seite'], 'r')
        self.assertTrue(h['stabfoermig'])
        self.assertEqual(h['flaechen'], 400, 'die 50 fernen Flächen berühren nichts')
        self.assertAlmostEqual(h['zentrum'][1], 1.25, delta=0.03)
        # die Seite folgt der Figurhand, nicht einem festen Etikett: stehen die Hände vertauscht, wechselt die Seite
        h2 = Meshfigurhalter.pruefen(scan, klassen, stab, {'r': haende['l'], 'l': haende['r']})
        self.assertEqual(h2['seite'], 'l')

    def test_zu_wenige_oder_zu_ferne_handflaechen_halten_nichts(self):
        from core.dienste.meshfigurhalter import Meshfigurhalter

        scan, klassen, stab = self._netz()
        haende = {'r': np.array([0.12, 1.25, 0.2]), 'l': np.array([0.9, 1.25, 0.2])}
        fern, klassen_fern, _ = self._netz(abstand=0.2)
        self.assertIsNone(Meshfigurhalter.pruefen(fern, klassen_fern, stab, haende), 'Handflächen 20 cm vom Stab berühren ihn nicht')
        wenige = klassen.copy()
        wenige[40:] = 0
        self.assertIsNone(Meshfigurhalter.pruefen(scan, wenige, stab, haende), 'unter 300 berührten Flächen ist es ein Zufall')
        self.assertIsNone(Meshfigurhalter.pruefen(scan, klassen, stab, {'r': np.array([5.0, 1.0, 0.0])}), 'keine Figurhand binnen 35 cm: keine Seite')

    def test_stabfoermig_unterscheidet_stab_und_klotz(self):
        from core.dienste.meshfigurhalter import Meshfigurhalter

        stab = np.column_stack([np.zeros(200), np.linspace(0, 1.7, 200), np.zeros(200)]) + np.random.default_rng(1).normal(0, 0.01, (200, 3))
        wuerfel = np.random.default_rng(2).uniform(-0.2, 0.2, (500, 3))
        schild = np.random.default_rng(3).uniform([-0.3, -0.3, -0.01], [0.3, 0.3, 0.01], (500, 3))
        self.assertTrue(Meshfigurhalter.stabfoermig(stab))
        self.assertFalse(Meshfigurhalter.stabfoermig(wuerfel))
        self.assertFalse(Meshfigurhalter.stabfoermig(schild), 'ein Schild ist flach und breit, kein Stab')


class GriffTest(SimpleTestCase):
    def _lauf(self, teile=None, haltung=None, stellung=None):
        job = SimpleNamespace(kennung='2026.10.99.00.00.00', ergebnis={'teile': teile or [], 'haltung': haltung} if haltung is not None else {'teile': teile or []}, stellung=lambda: stellung or {'a': 1.0})
        return SimpleNamespace(job=job, ablage=SimpleNamespace(arbeit=lambda name='': Path(self.tmp) / name))

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix='griff_', dir=Pruefablage.wurzel())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_nur_gehaltene_gegenstaende_nennen_eine_hand(self):
        teile = [{'name': 'spear', 'objekt': {'bewegung': 'starr', 'kontakt': 'r_hand', 'gehalten': True, 'haelt': {'seite': 'r', 'zentrum': [-0.42, 1.1, 0.31], 'handflaechen': 4338}}},
                 {'name': 'hat', 'objekt': {'bewegung': 'starr', 'kontakt': 'kopf', 'gehalten': False}},
                 {'name': 'bag', 'objekt': {'bewegung': 'folgt'}},
                 {'name': 'beard', 'objekt': {'hinweis': 'liegt an der Oberfläche'}}]
        self.assertEqual(Meshfigurgriff(self._lauf(teile)).halter(), {'r': {'name': 'spear', 'zentrum': [-0.42, 1.1, 0.31]}})
        self.assertEqual(Meshfigurgriff(self._lauf(teile[1:])).halter(), {})
        # ein Schild (nicht stabförmig, `gehalten` falsch) wird trotzdem gegriffen
        schild = [{'name': 'shield', 'objekt': {'gehalten': False, 'haelt': {'seite': 'l', 'zentrum': [0.3, 1.2, 0.2]}}}]
        self.assertEqual(Meshfigurgriff(self._lauf(schild)).halter(), {'l': {'name': 'shield', 'zentrum': [0.3, 1.2, 0.2]}})

    def test_ziel_sind_die_handflaechen_in_reichweite(self):
        # vier Dreiecke: nahe rechte Hand (14), ferne linke Hand (5, 50 cm weg), ferne rechte Hand (14, 60 cm weg), nahe Fläche ohne Hand-Etikett
        punkte = np.array([[0, 0, 0], [0.01, 0, 0], [0, 0.01, 0],
                           [0.5, 0, 0], [0.51, 0, 0], [0.5, 0.01, 0],
                           [0.6, 0, 0], [0.61, 0, 0], [0.6, 0.01, 0],
                           [0.02, 0.02, 0], [0.03, 0.02, 0], [0.02, 0.03, 0]], dtype=float)
        flaechen = np.arange(12).reshape(4, 3)
        klassen = np.zeros((4, 28))
        klassen[0, 14], klassen[1, 5], klassen[2, 14], klassen[3, 12] = 10, 10, 10, 10
        ziel = Meshfigurgriff(self._lauf()).ziel(SimpleNamespace(flaechen=flaechen, punkte=punkte), klassen, np.zeros(3), 'r')
        np.testing.assert_allclose(sorted(map(tuple, ziel)), sorted(map(tuple, punkte[:3])))
        # eine NAHE Fläche mit dem Etikett der anderen Hand zählt mit (am Zauberer trugen 2.005 Flächen der rechten Hand `Left_Hand`)
        klassen[3, 12], klassen[3, 5] = 0, 10
        ziel = Meshfigurgriff(self._lauf()).ziel(SimpleNamespace(flaechen=flaechen, punkte=punkte), klassen, np.zeros(3), 'r')
        self.assertEqual(len(ziel), 6)
        # zu wenige Stimmen zählen nicht
        klassen[0, 14], klassen[3, 5] = 3, 3
        self.assertEqual(len(Meshfigurgriff(self._lauf()).ziel(SimpleNamespace(flaechen=flaechen, punkte=punkte), klassen, np.zeros(3), 'r')), 0)

    def test_winkel_kommen_in_die_haltung(self):
        haltung = {'gueltig': True, 'drehung': {'r_upperarm': {'rotation/x': 10.0}}}
        lauf = self._lauf(haltung=haltung)
        bericht = {'seiten': {'r': {'uebernommen': True, 'griff': {'r_index1': {'rotation/z': 80.0}, 'r_thumb1': {'rotation/x': 20.0, 'rotation/y': 5.0}}},
                              'l': {'uebernommen': False, 'griff': {'l_index1': {'rotation/z': 70.0}}}}}
        self.assertEqual(Meshfigurgriff(lauf).anwenden(bericht), 2)
        self.assertEqual(haltung['drehung']['r_index1'], {'rotation/z': 80.0})
        self.assertEqual(haltung['drehung']['r_thumb1'], {'rotation/x': 20.0, 'rotation/y': 5.0})
        self.assertEqual(haltung['drehung']['r_upperarm'], {'rotation/x': 10.0}, 'die Gelenke der Anpassung bleiben')
        self.assertNotIn('l_index1', haltung['drehung'], 'eine abgelehnte Seite legt nichts an')

    def test_der_zuwachs_am_arm_wird_zu_den_winkeln_der_anpassung_addiert(self):
        haltung = {'gueltig': True, 'drehung': {'r_upperarm': {'rotation/x': 10.0, 'rotation/y': -4.0}}}
        bericht = {'seiten': {'r': {'uebernommen': True, 'griff': {'r_upperarm': {'rotation/x': 5.5}, 'r_hand': {'rotation/z': -12.0}, 'r_mid1': {'rotation/z': 90.0}}}}}
        Meshfigurgriff(self._lauf(haltung=haltung)).anwenden(bericht)
        self.assertEqual(haltung['drehung']['r_upperarm'], {'rotation/x': 15.5, 'rotation/y': -4.0})
        self.assertEqual(haltung['drehung']['r_hand'], {'rotation/z': -12.0}, 'ein Knochen ohne Winkel der Anpassung startet bei 0')
        self.assertEqual(haltung['drehung']['r_mid1'], {'rotation/z': 90.0})

    def test_ohne_gueltige_haltung_wird_nichts_angelegt(self):
        haltung = {'gueltig': False, 'drehung': {}}
        bericht = {'seiten': {'r': {'uebernommen': True, 'griff': {'r_index1': {'rotation/z': 80.0}}}}}
        self.assertEqual(Meshfigurgriff(self._lauf(haltung=haltung)).anwenden(bericht), 0)
        self.assertEqual(haltung['drehung'], {})
        self.assertEqual(Meshfigurgriff(self._lauf()).anwenden(bericht), 0, 'ohne Haltung im Ergebnis')

    def test_stempel_und_ablage(self):
        g = Meshfigurgriff(self._lauf())
        kaefig = np.arange(30, dtype=float).reshape(10, 3)
        ziele = {'r': np.arange(9, dtype=float).reshape(3, 3)}
        s1 = g._stempel(kaefig, {'r': 'spear'}, ziele)
        self.assertEqual(s1, g._stempel(kaefig, {'r': 'spear'}, ziele), 'gleiche Eingänge, gleicher Stempel')
        self.assertNotEqual(s1, g._stempel(kaefig + 0.01, {'r': 'spear'}, ziele), 'andere Figur')
        self.assertNotEqual(s1, g._stempel(kaefig, {'r': 'spear', 'l': 'x'}, {**ziele, 'l': ziele['r']}), 'andere Seiten')
        self.assertNotEqual(s1, g._stempel(kaefig, {'r': 'spear'}, {'r': ziele['r'] + 0.001}), 'anderes Ziel')
        self.assertIsNone(g._gemerkt(s1), 'noch nichts abgelegt')
        g._ablegen(s1, {'fassung': 1, 'seiten': {'r': {'uebernommen': False}}})
        self.assertEqual(g._gemerkt(s1), {'fassung': 1, 'seiten': {'r': {'uebernommen': False}}})
        self.assertIsNone(g._gemerkt('anderer'), 'ein anderer Stempel gilt nicht')

    def test_die_vorschau_ruft_den_griff_nach_den_objekten_und_vor_der_abnahme(self):
        text = (WEB / 'core' / 'dienste' / 'meshfigurvorschau.py').read_text(encoding='utf-8')
        self.assertIn('Meshfigurgriff.sicher(self.lauf)', text)
        self.assertLess(text.index("self.job.ergebnis['schammessung'] = scham.result()"), text.index('Meshfigurgriff.sicher(self.lauf)'))
        self.assertLess(text.index('Meshfigurgriff.sicher(self.lauf)'), text.index('Meshfigurabnahme.sicher(self.lauf)'))

    def test_die_suche_ist_die_des_blender_imports(self):
        text = (WEB / 'core' / 'dienste' / 'meshfigurgriff.py').read_text(encoding='utf-8')
        for name in ('Blendimportfingermodell', 'Blendimportfingersuche', 'Blendimporthaltung'):
            self.assertIn(name, text)

# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> 2D3D, Reiter „Workflow": jeder Baum, jede Klasse, jede Zeit hat ihren Beleg.

WARUM (Edgar, 02.10.2026: „mache einen neuen Tab, wo du den Workflow der 2D3D-Erkennung machst, mit allen Klassen und allen
Optionen (z. B. Blender) — ich brauche grafische Klassen mit Entscheidungsbäumen und Infos, was jeder Schritt kostet an
Zeit"): Ein Entscheidungsbaum, der eine Option nennt, die es nicht mehr gibt, oder eine Zeit ohne Messung, ist schlimmer als
keiner. Die Tests halten fest: die Optionen der Bäume sind die des Codes (Motoren, Modus, Knoten, Formularfelder), jede Klasse
hat eine Karte, jeder der 22 Schritte steht in genau einem Abschnitt, jede gemessene Zahl nennt ihre Quelle.
"""

import re

from django.test import Client, SimpleTestCase
from django.urls import reverse
from django.utils.html import escape

from core.dienste.architektur2d3d import Architektur2d3d
from core.dienste.architektur2d3dklassen import Architektur2d3dklassen
from core.dienste.architektur2d3dworkflow import Architektur2d3dworkflow
from core.dienste.workflowfluss import Workflowfluss
from core.dienste.workflowknoten import Workflowknoten
from core.dienste.workflowquellen import Workflowquellen
from core.dienste.workflowstrecke import Workflowstrecke
from core.dienste.workflowzeichner import Workflowzeichner
from core.dienste.workflowzeit import Workflowzeit
from core.dienste.workflowzeiten import Workflowzeiten


class SeiteWorkflow(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.text = Client().get(reverse('hilfe_architektur_2d3d')).content.decode('utf-8')
        cls.baeume = Architektur2d3dworkflow.baeume()
        cls.katalog = {k for _m, k in Architektur2d3dklassen.alle()}

    def test_beide_reiter_stehen_im_html_und_lassen_sich_umschalten(self):
        for reiter in ('ablauf', 'workflow'):
            self.assertIn('data-reiter="%s"' % reiter, self.text)
            self.assertIn('data-aktion="reiter" data-ziel="%s"' % reiter, self.text)
        self.assertIn('data-reiter-seite', self.text)
        self.assertIn('js/hilfe/architektur2d3dreiter.js', self.text)

    def test_jeder_baum_steht_auf_der_seite_und_die_kennungen_sind_eindeutig(self):
        kennungen = [b.kennung for b in self.baeume]
        self.assertEqual(len(kennungen), len(set(kennungen)))
        for baum in self.baeume:
            self.assertIn('id="%s"' % baum.anker, self.text)

    def test_jede_klasse_in_baeumen_und_fluss_hat_eine_karte(self):
        for baum in self.baeume:
            for klasse in baum.klassen():
                self.assertIn(klasse, self.katalog, '%s im Baum %s' % (klasse, baum.kennung))
                self.assertIn('id="k-%s"' % klasse, self.text)

    def test_jeder_verweis_der_seite_hat_ein_ziel(self):
        ziele = set(re.findall(r'id="([^"]+)"', self.text))
        for anker in set(re.findall(r'href="#((?:baum|k|quelle)-[^"]+)"', self.text)):
            self.assertIn(anker, ziele, anker)

    def test_jede_frage_hat_mindestens_zwei_antworten_mit_beschriftung(self):
        for baum in self.baeume:
            for knoten in baum.wurzel.alle():
                if knoten.art == Workflowknoten.FRAGE:
                    self.assertGreaterEqual(len(knoten.kinder), 2, '%s: %s' % (baum.kennung, knoten.titel))
                    for kind in knoten.kinder:
                        self.assertTrue(
                            kind.kante,
                            '%s: Antwort ohne Beschriftung unter „%s"' % (baum.kennung, knoten.titel),
                        )

    def test_jede_quelle_ist_nummeriert_und_unten_verzeichnet(self):
        nummern = set(re.findall(r'href="#quelle-(\d+)"', self.text))
        self.assertTrue(nummern)
        for nr in nummern:
            self.assertIn('id="quelle-%s"' % nr, self.text)


class OptionenSindDieDesCodes(SimpleTestCase):
    """Die Kanten der Bäume sind die Werte der Optionen — nicht von Hand daneben geschrieben."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.baeume = {b.kennung: b for b in Architektur2d3dworkflow.baeume()}

    def kanten(self, kennung):
        return [k.kante for k in self.baeume[kennung].wurzel.alle() if k.kante]

    def test_die_motoren_des_drapierens_sind_die_der_rezeptumgebung(self):
        from Genesis9.rezeptumgebung import Rezeptumgebung

        kanten = ' '.join(self.kanten('drapieren'))
        for motor in Rezeptumgebung.MOTOREN:
            self.assertIn(motor, kanten)

    def test_der_modus_der_iterationen_nennt_beide_werte(self):
        from core.dienste.iterationsoptionen import Iterationsoptionen

        kanten = ' '.join(self.kanten('modus'))
        self.assertIn(Iterationsoptionen.BEGUTACHTUNG, kanten)
        self.assertIn(Iterationsoptionen.AUTOMATISCH, kanten)

    def test_jeder_haarknoten_von_blender_steht_im_baum(self):
        from core.dienste.engine2d3dkleiderblender import Engine2d3dKleiderblender

        text = ' '.join(k.text for k in self.baeume['haarknoten'].wurzel.alle())
        for knoten in Engine2d3dKleiderblender.KNOTEN:
            self.assertIn(knoten, text)

    def test_die_quellen_des_koerpers_sind_die_des_katalogs(self):
        from core.dienste.engine2d3dkleiderkoerperoptionen import Engine2d3dKleiderkoerperoptionen

        kanten = ' '.join(self.kanten('koerper'))
        for wert, _text in Engine2d3dKleiderkoerperoptionen.KATALOG[0]['werte']:
            self.assertIn(wert, kanten)

    def test_das_netz_kennt_nur_trellis_und_nennt_jeden_sichtbaren_wert(self):
        """Edgar, 02.10.2026: „ich brauche NUR trellis in dem Workflow, kein Hunyan" — der Baum nennt die Werte, die das
        Formular dieses Bereichs zeigt (`Engine2d3dKleidernurtrellis`), und kein Hunyuan3D."""
        from core.dienste.engine2d3dkleideroptionen import Engine2d3dKleideroptionen

        katalog = Engine2d3dKleideroptionen.katalog()
        felder = {f['schluessel']: f for f in katalog['netz']['optionen']}
        self.assertNotIn('formmodell', felder)
        # Die Auflösung ist seit 02.10.2026 ein Feld der Gruppe `mesh` (Interface von TRELLIS.2).
        mesh = {f['schluessel']: f for f in katalog['mesh']['optionen']}
        kanten = ' '.join(self.kanten('netz'))
        for wert in (w['wert'] for w in mesh['aufloesung']['werte']):
            self.assertIn(wert, kanten)
        kanten_textur = ' '.join(self.kanten('textur'))
        for wert in (w['wert'] for w in felder['textur']['werte']):
            self.assertIn(wert, kanten_textur)

    def test_kein_baum_nennt_hunyuan(self):
        for baum in self.baeume.values():
            for knoten in baum.wurzel.alle():
                text = ' '.join(str(t) for t in (knoten.titel, knoten.text, knoten.kante)).lower()
                self.assertNotIn('hunyuan', text, '%s: %s' % (baum.kennung, knoten.titel))

    def test_die_kette_des_koerperschritts_ist_die_des_codes(self):
        from core.dienste.engine2d3dkleiderkoerper import Engine2d3dKleiderkoerper

        self.assertEqual(Workflowzeiten.KETTE, Engine2d3dKleiderkoerper.KETTE)

    def test_die_optionen_der_strecke_decken_das_formular_des_netzes(self):
        from core.dienste.engine2d3dkleideroptionen import Engine2d3dKleideroptionen

        netz = next(s for s in Workflowstrecke.SCHRITTE if s[0] == 'netz')
        genannt = {name for name, _werte in netz[3]}
        for schluessel in Engine2d3dKleideroptionen.SICHTBAR['netz']:
            self.assertIn(schluessel, genannt)

    def test_die_schritte_der_strecke_sind_die_des_laufs(self):
        from core.dienste.engine2d3dkleiderlauf import Engine2d3dKleiderlauf

        self.assertEqual(tuple(s[0] for s in Workflowstrecke.SCHRITTE), Engine2d3dKleiderlauf.SCHRITTE)


class FlussDeckt22Schritte(SimpleTestCase):
    def test_jeder_schritt_der_runde_steht_in_genau_einem_abschnitt(self):
        erwartet = sorted(nr for nr, *_rest in Architektur2d3d.RUNDE)
        self.assertEqual(sorted(Workflowfluss.nummern()), erwartet)

    def test_die_zeiten_der_abschnitte_haben_je_eine_quelle(self):
        for titel, _von, _bis, zeiten, _baeume in Workflowfluss.ABSCHNITTE:
            for _label, zeit in zeiten:
                self.assertTrue(zeit.gemessen, titel)
                self.assertTrue(zeit.quelle, titel)


class ZeitenSindBelegt(SimpleTestCase):
    def test_jede_gemessene_zahl_nennt_ihre_quelle(self):
        for name, wert in vars(Workflowzeiten).items():
            if isinstance(wert, Workflowzeit) and wert.gemessen:
                self.assertTrue(wert.quelle, name)

    def test_ungemessen_heisst_nicht_gemessen_und_ist_grau(self):
        z = Workflowzeit()
        self.assertEqual((z.text, z.klasse, z.wert), ('nicht gemessen', 'zx', 0.0))

    def test_die_stufen_gehen_nach_dem_groessten_wert_der_spanne(self):
        self.assertEqual(Workflowzeit(0.4).klasse, 'z0')
        self.assertEqual(Workflowzeit(1.0).klasse, 'z1')
        self.assertEqual(Workflowzeit(5.0, 59.9).klasse, 'z2')
        self.assertEqual(Workflowzeit(9.0, 120.0).klasse, 'z3')
        self.assertEqual(Workflowzeit(428.3, 752.6).klasse, 'z4')

    def test_der_text_hat_deutsches_komma_spanne_und_minuten(self):
        self.assertEqual(Workflowzeit(5.2).text, '5,2 s')
        self.assertEqual(Workflowzeit(563.1).text, '563 s (9,4 min)')
        self.assertEqual(Workflowzeit(428.3, 752.6).text, '428–753 s (bis 12,5 min)')
        self.assertEqual(Workflowzeit(0.1, unter=True).text, '< 0,1 s')

    def test_der_aufbau_der_zeitleiste_ist_die_summe_seiner_schritte(self):
        aufbau = Workflowstrecke.ZEITLEISTE
        self.assertAlmostEqual(Workflowzeiten.AUFBAU.von, sum(s for _n, s in aufbau[: Workflowstrecke.AUFBAU_SCHRITTE]), places=1)

    def test_die_koerperteile_summieren_sich_auf_die_gemessene_gesamtzeit(self):
        summe = sum(z.von for _n, z in Workflowzeiten.koerper_teile())
        self.assertAlmostEqual(summe, 871.7, places=1)


class ZeichnerMaskiertUndVerweist(SimpleTestCase):
    def zeichner(self, bekannt=()):
        return Workflowzeichner(Workflowquellen(), bekannt)

    def test_text_wird_maskiert(self):
        knoten = Workflowknoten(Workflowknoten.TAT, '<script>x</script>', 'a < b & c')
        html = self.zeichner().knoten(knoten)
        self.assertNotIn('<script>', html)
        self.assertIn(escape('a < b & c'), html)

    def test_eine_klasse_ohne_karte_wird_kein_verweis(self):
        """Gegenprobe: Der Verweis darf nicht ins Leere zeigen."""
        z = self.zeichner(bekannt=['Gibt'])
        self.assertIn('href="#k-Gibt"', z.klasse('Gibt'))
        self.assertNotIn('href', z.klasse('GibtEsNicht'))

    def test_die_quellen_werden_in_reihenfolge_des_auftretens_nummeriert(self):
        quellen = Workflowquellen()
        self.assertEqual([quellen.nummer(q) for q in ('a', 'b', 'a', 'c')], [1, 2, 1, 3])
        self.assertEqual(quellen.liste(), [(1, 'a'), (2, 'b'), (3, 'c')])

    def test_eine_zeit_ohne_quelle_hat_keine_nummer(self):
        self.assertNotIn('wf-qnr', self.zeichner().zeit(Workflowzeit(1.0)))
        self.assertIn('wf-qnr', self.zeichner().zeit(Workflowzeit(1.0, quelle='x')))

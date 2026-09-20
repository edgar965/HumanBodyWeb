# -*- coding: utf-8 -*-
"""Gemeinsam anziehen auf Genesis 9 — die Hose sitzt im Schritt.

Edgar, 20.09.2026, dreimal mit Bild von Kin1 („buggy", „Hose ist kaputt",
„nichts gelöst, phantasiere nicht. Mach dir einen Testcase für zusammen
bauen"). Der Fall ist das Simulationsergebnis seines Laufs von 19:42 (Hose +
Oberteil, `gemeinsam_genesis9_female_c7bcbae1`), abgelegt unter
`Assets/GarmentCode/test/gemeinsam_kin/` mit Kins Figurreglern. Die Drapierung
(64 s) laeuft hier nicht — alles danach schon: Korrektur, Teilung,
Hochziehen, Anlegen, Spannen, Rig (`Gemeinsamablage.verteilen_auf`, ~10 s).

Was gemessen ist und was gelten muss (Stand 21:05, `roehrenschnitt.py`):

1. Die Luft-Regel von `Stoffhochziehen` findet an Kin KEINEN Koerperschritt
   (tiefster Mittelpunkt auf dem Innenschenkel, die Oberschenkel beruehren
   sich). Mit den Flaechen des Koerpers kommt er aus der Topologie: 0,845 m,
   wo aus den zwei Beinroehren eine wird (Damm 0,834 — die Labien haengen
   als eigener Ring darunter).
2. Die Hose wird an diesen Schritt gezogen: ihre Beinroehren vereinigen
   sich bei 0,740 (Schrittnaehte 0,739/0,750), Zug 105,1 mm; der Saum
   kommt auf den Knoechel (0,095). Danach liegen beide Schrittnaehte am
   Schritt (vorn ab 0,832, hinten ab 0,840) statt 10 cm zwischen den
   Oberschenkeln — das Gewirr langer Dreiecke aus Edgars Bau 20:43 ist weg
   (Bilder im Tagebuch).
3. Einzelweg (`Stoffbindung.anziehen`) und gemeinsamer Weg
   (`Gemeinsamablage.verteilen_auf`) liefern fuer DIESELBE simulierte Hose
   dasselbe: je Punkt median 0,00 mm, p90 0,01 mm Unterschied (nur am
   Bund unter dem Oberteil bis 9 mm — `Hautmitstoff`).
4. Der Oberteil-Teil bleibt unberuehrt vom Hochziehen (0,0 mm).

Sabotage-Gegenprobe: `Stoffhochziehen._vereinigung` gibt None -> Fall 1
und 2 rot (hochgezogen 0,0); `verteilen_auf` mit anderem `anliegen_mm` als
der Einzelweg -> Fall 3 rot.
"""

import glob
import gzip
import json
import shutil
import unittest

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase
from GarmentCode.baufeineinstellung import Baufeineinstellung
from GarmentCode.gemeinsamablage import Gemeinsamablage
from GarmentCode.genesis9drapierung import Genesis9drapierung
from GarmentCode.genesis9gemeinsam import Genesis9gemeinsam
from GarmentCode.stoffbindung import Stoffbindung
from GarmentCode.stoffhochziehen import Stoffhochziehen
from GarmentCode.stoffteilung import Stoffteilung
from Genesis9.pfade import G9pfade

FIXTURE = settings.ASSETS_ROOT / 'GarmentCode' / 'test' / 'gemeinsam_kin'
NAME = 'test_gemeinsam_kin'


def fixture_da():
    return G9pfade.vorhanden() and (FIXTURE / 'sim.obj.gz').is_file()


@unittest.skipUnless(fixture_da(), 'Genesis-9-Bibliothek oder Fixture fehlt')
class GemeinsamGenesis9HoseTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wegwerf = settings.BASE_DIR / '_wegwerf' / NAME
        if cls.wegwerf.is_dir():
            shutil.rmtree(cls.wegwerf)
        ordner = cls.wegwerf / NAME
        ordner.mkdir(parents=True)
        for quelle, ziel in (('sim.obj.gz', NAME + '_sim.obj'),
                             ('sim_segmentation.txt.gz', NAME + '_sim_segmentation.txt')):
            with gzip.open(FIXTURE / quelle, 'rb') as f, open(ordner / ziel, 'wb') as g:
                shutil.copyfileobj(f, g)
        shutil.copy(FIXTURE / 'specification.json', ordner / (NAME + '_specification.json'))
        regler = json.load(open(FIXTURE / 'figur_regler.json', encoding='utf-8'))['regler']
        figur = Genesis9drapierung.figur(regler)
        cls.punkte = figur.projekt(figur.punkte())
        cls.traeger = Genesis9gemeinsam.traeger(figur, cls.punkte, figur.dreiecke())
        fein_p, _ = figur.sichtbar()
        cls.haut = figur.projekt(fein_p)
        fein = Baufeineinstellung(hautabstand_mm=1.0, aufloesung=1.0, anliegen_mm=2.0)
        cls.schnitte = []
        for vorlage in ('hose', 'oberteil'):
            teil = cls.wegwerf / (NAME + '_' + vorlage)
            teil.mkdir()
            cls.schnitte.append({'vorlage': vorlage, 'name': NAME + '_' + vorlage,
                                 'ordner': str(teil), 'teil': vorlage, 'fein': fein,
                                 'hinweise': [], 'selbstdurchdringend': False})
        ergebnis = {'netz': str(ordner / (NAME + '_sim.obj')), 'ordner': str(ordner),
                    'spezifikation': str(ordner / (NAME + '_specification.json'))}
        cls.berichte = Gemeinsamablage.verteilen_auf(ergebnis, cls.schnitte, cls.traeger)

    def test_der_koerperschritt_kommt_aus_der_topologie(self):
        fein_p, fein_f = self.traeger.sichtbar
        self.assertIsNone(Stoffhochziehen(fein_p).schritt)          # die Luft-Regel scheitert
        mit = Stoffhochziehen(fein_p, fein_f)
        self.assertTrue(mit.beruehrung)
        self.assertAlmostEqual(mit.schritt[1], 0.845, delta=0.005)
        self.assertAlmostEqual(mit.schritt[0], 0.0, delta=0.01)

    def test_die_hose_wird_an_den_schritt_gezogen(self):
        hose = next(b for b in self.berichte if b['stueck'] == 'hose')
        self.assertGreater(hose['punkte'], 11000)
        self.assertAlmostEqual(hose['anlage']['hochgezogen_mm'], 105.1, delta=5.0)
        rig = json.load(open(glob.glob(hose['ordner'] + '/*_sim_rig.json')[0], encoding='utf-8'))
        p = np.array(rig['punkte'])
        d = np.array(rig['dreiecke'])
        marken = self._marken()
        for links, rechts, mindest in (('hose__pant_f_l', 'hose__pant_f_r', 0.82),
                                       ('hose__pant_b_l', 'hose__pant_b_r', 0.83)):
            naht = self._naht(p, d, marken, links, rechts)
            self.assertGreater(len(naht), 10, links)
            self.assertGreater(p[naht, 2].min(), mindest, links)       # die Naht sitzt am Schritt
        self.assertAlmostEqual(p[:, 2].min(), 0.095, delta=0.01)        # Saum am Knoechel

    def _marken(self):
        """Panelmarke je Punkt des Hosen-Teilnetzes — aus der Segmentierung
        des ganzen Netzes ueber die Teilung (die Teile tragen keine eigene)."""
        ordner = self.wegwerf / NAME
        segmentierung = ordner / (NAME + '_sim_segmentation.txt')
        teile = Stoffteilung(str(ordner / (NAME + '_specification.json'))).teilen(
            str(ordner / (NAME + '_sim.obj')), str(segmentierung))
        gesamt = np.array([z.strip() for z in open(segmentierung, encoding='utf-8')])
        return gesamt[np.asarray(teile['hose']['indizes'], dtype=np.int64)]

    @staticmethod
    def _naht(p, d, marken, links, rechts):
        """Punkte, die Dreiecke beider Panels teilen — die Naht dazwischen."""
        def punkte_von(panel):
            m = np.zeros(len(p), dtype=bool)
            m[d[(marken[d] == panel).any(1)].ravel()] = True
            return m
        return np.flatnonzero(punkte_von(links) & punkte_von(rechts))

    def test_einzelweg_und_gemeinsamer_weg_liefern_dasselbe(self):
        hose = next(b for b in self.berichte if b['stueck'] == 'hose')
        roh = glob.glob(hose['ordner'] + '/*_hose_sim.obj')[0]
        einzel = self.wegwerf / 'einzel'
        einzel.mkdir(exist_ok=True)
        shutil.copy(roh, einzel / 'hose_sim.obj')
        # Die Bundmaske des Einzelwegs kommt aus der Segmentierung NEBEN der
        # OBJ (`Bundmaske.neben_netz`); der gemeinsame Weg hat sie aus der
        # Teilung. Ohne sie hielte das Hochziehen die Oberkante statt des
        # Bunds, und die Wege unterschieden sich um 15 mm am Bund (20.09.2026,
        # seit die Hose an Kin hochgezogen wird).
        with open(einzel / 'hose_sim_segmentation.txt', 'w', encoding='utf-8') as datei:
            datei.write('\n'.join(self._marken()) + '\n')
        antwort = Stoffbindung.anziehen(str(einzel / 'hose_sim.obj'), self.traeger, 1.0, None,
                                        anliegen_mm=2.0, getragen=None)
        pe = np.array(json.load(open(antwort['rig'], encoding='utf-8'))['punkte'])
        pg = np.array(json.load(open(glob.glob(hose['ordner'] + '/*_sim_rig.json')[0],
                                     encoding='utf-8'))['punkte'])
        self.assertEqual(len(pe), len(pg))
        unterschied = np.linalg.norm(pe - pg, axis=1) * 1000
        self.assertLess(np.median(unterschied), 0.1)
        self.assertLess(np.percentile(unterschied, 90), 0.5)

    def test_das_oberteil_bleibt_wo_es_ist(self):
        oben = next(b for b in self.berichte if b['stueck'] == 'oberteil')
        self.assertGreater(oben['punkte'], 4000)
        self.assertEqual(oben['anlage']['hochgezogen_mm'], 0.0)
        self.assertGreater(oben['rig_punkte'], 4000)

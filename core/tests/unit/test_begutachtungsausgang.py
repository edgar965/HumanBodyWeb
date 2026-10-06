# -*- coding: utf-8 -*-
"""Iteration 0 (`Begutachtungsausgang`) und das Herrenhaar als Bibliotheksstück (`Herrenhaarstueck`) — 05.10.2026, Edgar: „baue mir eine Iteration 0 ein, wo du die Vorlage und das Modell machst VOR der Iteration 1",
„lege das neue Herrenhaar auch in die Genesis Bibliothek als eigen_Herrenhaar rein".

Attrappen statt Aufträge: `SimpleNamespace` für den Auftrag, das Startrezept und die Schreibfunktionen der Bibliothek sind umgeleitet — nichts wird in `3DObjects/` geschrieben. Geschrieben, nicht gelaufen
(`testsuite-nur-auf-ansage`).

Sabotage: in `Begutachtungsausgang.rezept` die Zeile mit `Iterationsoptionen.rumpftiefe(job)` streichen → Fall 2 rot; in `nachher` den Rückgriff auf `vorher` weglassen → Fall 6 rot; in `Herrenhaarstueck.netz` die UV
je Gruppe auf `[0, 0]` setzen → Fall 9 rot; in `ablegen` `art_ordner='Hair'` streichen → Fall 11 rot.
"""

import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.dsonschreiber import G9dsonschreiber
from Genesis9.eigenstueck import G9eigenstueck
from Genesis9.gcfigurbau import G9gcfigurbau
from Genesis9.modellmitkleidern import ModellMitKleidern
from Genesis9.modellrezept import G9rezept

from core.dienste.begutachtungsausgang import Begutachtungsausgang
from core.dienste.herrenhaarstueck import Herrenhaarstueck
from core.dienste.iterationsoptionen import Iterationsoptionen
from core.dienste.standvorabkleider import Standvorabkleider

START = ["m.kleid_nur('g9_base_shirt')", "m.haar_farbe('#565656')"]


def _job(**optionen):
    return SimpleNamespace(kennung='2026.10.04.00.00.00', optionen={'iterationen': optionen} if optionen else None, ergebnis={}, stellung=lambda: {})


class DieIterationNull(SimpleTestCase):
    def test_1_das_rezept_ist_das_startrezept_mit_rumpftiefe_passform_und_gesichtsprofil(self):
        with mock.patch.object(Standvorabkleider, 'rezept', return_value=START):
            text = Begutachtungsausgang.rezept(_job())
        self.assertEqual(text.splitlines(), START + ['m.koerper_rumpftiefe()', 'm.passform(weite_cm=%s)' % Begutachtungsausgang.WEITE_CM, 'm.koerper_gesichtsprofil()'])
        self.assertTrue(text.endswith('\n'))

    def test_2_die_optionen_schalten_rumpftiefe_und_gesichtsprofil_einzeln_ab(self):
        with mock.patch.object(Standvorabkleider, 'rezept', return_value=START):
            ohne_rumpf = Begutachtungsausgang.rezept(_job(rumpftiefe='aus')).splitlines()
            ohne_gesicht = Begutachtungsausgang.rezept(_job(gesichtsprofil='aus')).splitlines()
            nichts = Begutachtungsausgang.rezept(_job(rumpftiefe='aus', gesichtsprofil='aus')).splitlines()
        self.assertEqual(ohne_rumpf, START + ['m.koerper_gesichtsprofil()'])
        self.assertEqual(ohne_gesicht, START + ['m.koerper_rumpftiefe()', 'm.passform(weite_cm=%s)' % Begutachtungsausgang.WEITE_CM])
        self.assertEqual(nichts, START)

    def test_3_ohne_fotostuecke_ist_das_rezept_leer(self):
        with mock.patch.object(Standvorabkleider, 'rezept', return_value=[]):
            self.assertEqual(Begutachtungsausgang.rezept(_job()), '')

    def test_4_das_rezept_besteht_die_pruefung_des_rezepttexts(self):
        with mock.patch.object(Standvorabkleider, 'rezept', return_value=START):
            text = Begutachtungsausgang.rezept(_job())
        namen = [zeile[1] for zeile in G9rezept.pruefen(text)]
        self.assertEqual(namen[-3:], ['koerper_rumpftiefe', 'passform', 'koerper_gesichtsprofil'])
        hilfe = [name for name, _signatur, _text in ModellMitKleidern.hilfe()]
        self.assertIn('koerper_gesichtsprofil', hilfe)                                                    # die Nachbesserungs-KI sieht beide Funktionen im Katalog
        self.assertIn('koerper_rumpftiefe', hilfe)

    def test_5_bestellung_eintrag_und_fehlt(self):
        with mock.patch.object(Standvorabkleider, 'rezept', return_value=START):
            bestellung = Begutachtungsausgang.bestellung(_job())
        self.assertEqual({k: bestellung[k] for k in ('automatisch', 'runden', 'ausgang')}, {'automatisch': False, 'runden': 1, 'ausgang': True})
        self.assertTrue(Begutachtungsausgang.verlangt(bestellung))
        self.assertFalse(Begutachtungsausgang.verlangt({}))
        self.assertFalse(Begutachtungsausgang.verlangt(None))
        job = _job()
        self.assertTrue(Begutachtungsausgang.fehlt(job))                                                  # nichts gerechnet: Iteration 0 gehört vor die bestellte Runde
        for ergebnis in ({'iterationen': [{'runde': 1}]}, {'kreislauf': {'modell': 'm'}}, {'kreislauf': {'weiter': {'modell': 'm'}}}):
            job.ergebnis = ergebnis
            self.assertFalse(Begutachtungsausgang.fehlt(job), ergebnis)
        job.ergebnis = {'iterationen': [{'runde': 1, 'art': 'begutachtung'}, {'runde': 0, 'art': 'ausgang', 'zeit': 'x'}]}
        self.assertEqual(Begutachtungsausgang.eintrag(job)['zeit'], 'x')
        job.ergebnis = {'iterationen': [{'runde': 1, 'art': 'begutachtung'}]}
        self.assertIsNone(Begutachtungsausgang.eintrag(job))

    def test_6_eine_nachtraegliche_iteration_0_aendert_den_stand_der_iterationen_nicht(self):
        job = _job()
        job.ergebnis = {'iterationen': [{'runde': 1, 'art': 'begutachtung'}, {'runde': 0, 'art': 'ausgang', 'zeit': 'alt'}],
                        'kreislauf': {'modell': 'M', 'beste': 1}, 'begutachtung': {'zustand': 'fertig', 'fertig': True}}
        original = job.ergebnis['kreislauf']
        vorher = Begutachtungsausgang.vorher(job)
        self.assertIsNot(vorher[0], original)                                                             # `vorher` ist eine Kopie, die Runde ändert das Original
        # die Runde 0 läuft: neuer Eintrag hinten, der Kreislauf wird von ihr überschrieben
        job.ergebnis['iterationen'].append({'runde': 0, 'art': 'ausgang', 'zeit': 'neu'})
        job.ergebnis['kreislauf']['modell'] = 'X'
        job.ergebnis['begutachtung'] = {'zustand': 'laeuft'}
        Begutachtungsausgang.nachher(job, vorher)
        self.assertEqual([(e['runde'], e.get('zeit')) for e in job.ergebnis['iterationen']], [(0, 'neu'), (1, None)])        # die frühere Iteration 0 ist ersetzt, nach Runde geordnet
        self.assertEqual(job.ergebnis['kreislauf'], {'modell': 'M', 'beste': 1})                          # Stand wie vorher
        self.assertEqual(job.ergebnis['begutachtung'], {'zustand': 'wartet', 'fertig': True})


class DieOptionen(SimpleTestCase):
    def test_7_rumpftiefe_und_gesichtsprofil_sind_vorgabe_an(self):
        for name in ('rumpftiefe', 'gesichtsprofil'):
            funktion = getattr(Iterationsoptionen, name)
            self.assertTrue(funktion(_job()))
            self.assertTrue(funktion(_job(runden=3)))
            self.assertFalse(funktion(_job(**{name: 'aus'})))
            self.assertEqual(Iterationsoptionen.pruefen({name: 'quatsch'})[name], 'an')
            katalog = next(e for e in Iterationsoptionen.KATALOG if e['schluessel'] == name)
            self.assertEqual([w for w, _t in katalog['werte']], ['an', 'aus'])


def _teile(ordner):
    """Zwei Teile wie `Herrenhaar.teile`: die Haarkappe (Farbe im Bild, `farbe` weiß) und eine Strähnengruppe (Farbe im Feld `farbe`)."""
    from PIL import Image
    Image.fromarray(np.full((8, 8, 3), 100, dtype=np.uint8)).save(ordner / 'kappe.png')
    kappe = {'punkte': np.array([[0.0, 1.6, 0.0], [0.1, 1.6, 0.0], [0.0, 1.7, 0.0]]), 'dreiecke': np.array([[0, 1, 2]]), 'farbe': (1.0, 1.0, 1.0), 'textur': [{'albedo': str(ordner / 'kappe.png')}]}
    straehnen = {'punkte': np.array([[0.0, 1.6, 0.1], [0.1, 1.6, 0.1], [0.0, 1.7, 0.1], [0.1, 1.7, 0.1]]), 'dreiecke': np.array([[0, 1, 2], [1, 2, 3]]), 'farbe': (0.2, 0.3, 0.4), 'textur': []}
    return [kappe, straehnen]


class DasHerrenhaarstueck(SimpleTestCase):
    def setUp(self):
        self.ordner = Path(tempfile.mkdtemp(prefix='herrenhaar_', dir=str(Path(__file__).resolve().parents[3] / 'ProjektTemp')))
        self.addCleanup(shutil.rmtree, self.ordner, True)

    def test_8_die_farbe_der_kappe_kommt_aus_ihrem_bild_die_der_straehnen_aus_dem_feld(self):
        kappe, straehnen = _teile(self.ordner)
        np.testing.assert_allclose(Herrenhaarstueck._farbe(kappe), [100 / 255.0] * 3, atol=1e-9)         # noqa: SLF001
        self.assertEqual(Herrenhaarstueck._farbe(straehnen), [0.2, 0.3, 0.4])                            # noqa: SLF001

    def test_9_ein_netz_aus_allen_teilen_mit_einem_uv_je_gruppe_in_der_mitte_ihres_farbfelds(self):
        punkte, netz, felder = Herrenhaarstueck.netz(_teile(self.ordner))
        self.assertEqual(punkte.shape, (7, 3))
        self.assertEqual(netz['flaechen'], [[0, 1, 2], [3, 4, 5], [4, 5, 6]])                              # die Strähnen hinter der Kappe, Punkte fortlaufend
        self.assertEqual(netz['flaechen_uv'], [[0, 0, 0], [1, 1, 1], [1, 1, 1]])
        np.testing.assert_allclose(netz['uvs'], [[0.25, 0.5], [0.75, 0.5]])
        self.assertEqual(felder.shape, (2, 3))

    def test_10_das_farbfeldbild_zeigt_an_der_stelle_der_uv_die_farbe_der_gruppe(self):
        from PIL import Image
        _punkte, netz, felder = Herrenhaarstueck.netz(_teile(self.ordner))
        pfad = Herrenhaarstueck.bild(felder, self.ordner / 'felder.png')
        bild = np.asarray(Image.open(pfad).convert('RGB'))
        self.assertEqual(bild.shape, (Herrenhaarstueck.FELD_PX, 2 * Herrenhaarstueck.FELD_PX, 3))
        for gruppe, (u, v) in enumerate(netz['uvs']):
            gefunden = bild[int(v * bild.shape[0]), int(u * bild.shape[1])]
            np.testing.assert_array_equal(gefunden, (np.clip(felder[gruppe], 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8))

    def test_11_der_schreiber_legt_haar_unter_hair_und_kleidung_unter_clothing_ab(self):
        wurzel = Path('/bibliothek')
        self.assertEqual(G9dsonschreiber(wurzel, 'EIGEN', 'Name', 'KENN').duf, wurzel / 'People' / 'Genesis 9' / 'Clothing' / 'EIGEN' / 'Name.duf')
        self.assertEqual(G9dsonschreiber(wurzel, 'EIGEN', 'Name', 'KENN', 'Hair').duf, wurzel / 'People' / 'Genesis 9' / 'Hair' / 'EIGEN' / 'Name.duf')

    def test_12_ablegen_schreibt_zweimal_als_haar_an_den_kopf_und_rechnet_die_ruhelage_zurueck(self):
        teile = _teile(self.ordner)
        schreiben = mock.Mock(return_value={'stueck': 'eigen_herrenhaar', 'punkte': 7, 'flaechen': 3})
        with mock.patch.object(Herrenhaarstueck, 'teile', return_value=(teile, '#565656')), \
                mock.patch.object(G9eigenstueck, 'arbeitsordner', return_value=self.ordner / 'arbeit'), \
                mock.patch.object(G9eigenstueck, 'schreiben', schreiben), \
                mock.patch.object(G9gcfigurbau, 'ruhelage', return_value=(np.zeros((7, 3)), {'rest_max_mm': 0.0})) as ruhelage, \
                mock.patch.object(G9gcfigurbau, 'pruefen', return_value={'max_mm': 0.0}):
            bilanz = Herrenhaarstueck.ablegen(_job())
        self.assertEqual(schreiben.call_count, 2)                                                         # einmal roh, einmal in der zurückgerechneten Ruhelage
        for aufruf in schreiben.call_args_list:
            self.assertEqual(aufruf.kwargs, {'heben': False, 'knochen': 'head', 'art_ordner': 'Hair'})
            self.assertEqual(aufruf.args[2:4], ('EIGEN_eigen_Herrenhaar', 'eigen_Herrenhaar'))
            self.assertEqual(aufruf.args[4], ('Follower/Hair', '/Default/Hair'))
        ruhelage.assert_called_once()
        self.assertEqual(ruhelage.call_args.args[0], 'eigen_herrenhaar')
        self.assertEqual((bilanz['gruppen'], bilanz['dreiecke'], bilanz['haarfarbe'], bilanz['auftrag']), (2, 3, '#565656', '2026.10.04.00.00.00'))
        self.assertTrue((self.ordner / 'arbeit' / 'farbfelder.png').is_file())
        self.assertTrue((self.ordner / 'arbeit' / 'herrenhaar.json').is_file())

    def test_13_ohne_herrenhaar_kein_stueck(self):
        with mock.patch('core.dienste.haarumbau.Haarumbau.herrenhaar', return_value=None), \
                mock.patch('core.dienste.kleidermodellbau.Kleidermodellbau') as bau, \
                mock.patch.object(G9rezept, 'anwenden'), \
                mock.patch.object(Standvorabkleider, 'rezept', return_value=START):
            bau.return_value.koerper.return_value = {}
            with self.assertRaises(ValueError):
                Herrenhaarstueck.teile(_job(), ablage=SimpleNamespace())

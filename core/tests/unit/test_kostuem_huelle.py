# -*- coding: utf-8 -*-
"""Kostüm-Kreislauf, Nachtrag 30.09.2026 — Optionen (Fototextur, Umriss-Hülle, Prüf-KI-Flaute), gemischte
Schrittweite des Optimierers, wiederholtes Lesen einer Antwortdatei, Löschen der Fototextur-Ansichten.

Rein rechnend, ohne Blender und ohne Ollama. Die Blender-Seite (`Kostuemhuelle`, `Fototextur`, `Projektion`) prüft nur
ein echter Lauf: Sie braucht `bpy`. Geschrieben, NICHT gelaufen (Tests laufen nur auf Ansage).
"""

import json
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.kostuemarbeiter import Kostuemarbeiter
from core.dienste.kostuemloeschung import Kostuemloeschung
from core.dienste.kostuemoptimierer import Kostuemoptimierer
from core.dienste.kostuemoptionen import Kostuemoptionen
from core.dienste.kostuemparameter import Kostuemparameter
from core.dienste.kostuemreferenz import Kostuemreferenz


class KostuemreferenzRueckansichtenTest(SimpleTestCase):
    def test_die_hinteren_schraegen_sind_hinten_links_und_hinten_rechts(self):
        # 30.09.2026 gemessen (`winkel_suche.py`): ansicht_2_4 passt bei −135° (IoU 0,867 gegen 0,725 bei +135°),
        # ansicht_2_3 gehört auf +135° — bis dahin waren beide vertauscht.
        winkel = {
            n: Kostuemreferenz.winkel_von({'original': 'ansicht_%s.jpg' % n}) for n in Kostuemreferenz.BOGEN
        }
        self.assertEqual((winkel['2_3'], winkel['2_4']), (135.0, -135.0))
        self.assertEqual((winkel['2_1'], winkel['2_2']), (35.0, -45.0))

    def test_ein_winkel_am_foto_geht_vor_dem_namen(self):
        self.assertEqual(Kostuemreferenz.winkel_von({'original': 'ansicht_2_3.jpg', 'winkel': 100}), 100.0)


class KostuemdetailTest(SimpleTestCase):
    def test_die_ausschnitte_haben_je_bereich_eine_spalte_und_zwei_zeilen(self):
        from PIL import Image

        from core.dienste.kostuembild import Kostuembild
        from core.dienste.kostuemdetail import Kostuemdetail

        groesse = (512, 768)
        maske = np.zeros((groesse[1], groesse[0]), bool)
        maske[40:740, 150:360] = True
        farbe = np.zeros(maske.shape + (3,), np.float32)
        farbe[:] = (0.2, 0.3, 0.6)
        bild = Kostuembild(farbe, maske)
        ordner = Path(
            tempfile.mkdtemp(
                prefix='kostuemdetail_', dir=str(Path(__file__).resolve().parents[3] / 'ProjektTemp')
            )
        )
        self.addCleanup(shutil.rmtree, ordner, ignore_errors=True)
        ziel = Kostuemdetail.bauen(bild, bild, ordner / 'detail.png')
        with Image.open(ziel) as tafel:
            self.assertEqual(tafel.height, 2 * Kostuemdetail.ZELLE + Kostuemdetail.SCHRIFT_HOEHE + 4)
            erwartet = sum(
                int(round((x1 - x0) * groesse[0] * Kostuemdetail.ZELLE / ((y1 - y0) * groesse[1])))
                for _, (x0, y0, x1, y1) in Kostuemdetail.BEREICHE
            )
            self.assertAlmostEqual(tafel.width, erwartet, delta=len(Kostuemdetail.BEREICHE))

    def test_die_kritik_fragt_mit_zwei_bildern_und_nennt_das_zweite_im_text(self):
        from core.dienste.kostuemkritik import Kostuemkritik

        werte = Kostuemparameter.start()
        kritik = Kostuemkritik('x')
        self.assertNotIn('ZWEITES Bild', kritik.frage(werte))
        self.assertIn('ZWEITES Bild', kritik.frage(werte, detail=True))


class KostuemoptionenNachtragTest(SimpleTestCase):
    def test_neue_optionen_haben_vorgaben(self):
        vorgaben = Kostuemoptionen.vorgaben()
        self.assertEqual((vorgaben['textur'], vorgaben['huelle']), ('an', 'an'))
        self.assertEqual(vorgaben['pruefki_stillstand'], 3)

    def test_wahl_und_zahl_werden_geprueft(self):
        roh = {'textur': 'kaputt', 'huelle': 'aus', 'pruefki_stillstand': 40, 'runden': 5000}
        aus = Kostuemoptionen.pruefen(roh)
        self.assertEqual(aus['textur'], 'an', 'unbekannter Wert → Vorgabe')
        self.assertEqual((aus['huelle'], aus['pruefki_stillstand'], aus['runden']), ('aus', 40, 5000))
        self.assertEqual(
            Kostuemoptionen.pruefen({'pruefki_stillstand': 0})['pruefki_stillstand'], 3, 'unter min'
        )

    def test_der_katalog_fuehrt_die_neuen_optionen_mit_werten(self):
        with mock.patch('core.dienste.kostuemoptionen.Ollamamodelle.mit_bildern', return_value=[]):
            katalog = {e['schluessel']: e for e in Kostuemoptionen.katalog()['optionen']}
        self.assertEqual([w['wert'] for w in katalog['huelle']['werte']], ['an', 'aus'])
        self.assertEqual([w['wert'] for w in katalog['textur']['werte']], ['an', 'aus'])


class KostuemparameterNachtragTest(SimpleTestCase):
    NEU = ('hut.seite', 'hut.kipp', 'aermel.tiefe', 'stab.krone', 'stab.vorn', 'pose.arm_vor')

    def test_neue_masse_stehen_im_schema_und_ihr_start_liegt_in_den_grenzen(self):
        schema = Kostuemparameter.schema()
        for k in self.NEU:
            self.assertIn(k, schema)
            self.assertLessEqual(schema[k]['min'], schema[k]['start'], k)
            self.assertLessEqual(schema[k]['start'], schema[k]['max'], k)

    def test_ein_alter_wertesatz_ohne_die_neuen_masse_bekommt_ihren_startwert(self):
        alt = {k: v for k, v in Kostuemparameter.start().items() if k not in self.NEU}
        neu = Kostuemparameter.pruefen(alt)
        for k in self.NEU:
            self.assertEqual(neu[k], Kostuemparameter.start()[k], k)


class KostuemoptimiererSchrittTest(SimpleTestCase):
    def test_jeder_zweite_kandidat_springt_weiter(self):
        # Flaute: `schritt` steht am Mindestwert, trotzdem müssen große Sprünge vorkommen.
        start = Kostuemparameter.start()
        schema = Kostuemparameter.schema()
        fein, grob = [], []
        o = Kostuemoptimierer('x', Kostuemoptimierer.SCHRITT_MIN)
        for runde in range(1, 60):
            for i, k in enumerate(o.kandidaten(start, 4, runde)):
                abstaende = [
                    abs(k[s] - start[s]) / (schema[s]['max'] - schema[s]['min'])
                    for s in Kostuemoptimierer.veraenderlich(start)
                    if k[s] != start[s]
                ]
                (grob if i % 2 else fein).append(np.mean(abstaende))
        self.assertGreater(np.mean(grob), 2.5 * np.mean(fein))

    def test_der_weite_sprung_ueberschreitet_die_obergrenze_nicht(self):
        o = Kostuemoptimierer('x', Kostuemoptimierer.SCHRITT_MAX)
        for k in o.kandidaten(Kostuemparameter.start(), 8, 3):
            self.assertEqual(k, Kostuemparameter.pruefen(k))


class KostuemkreislaufMischenTest(SimpleTestCase):
    @staticmethod
    def _ergebnis(name, abweichung, werte):
        return {'name': name, 'note': {'abweichung': abweichung}, 'werte': werte}

    def test_die_aenderungen_der_verlierer_gehen_als_mix_in_die_naechste_runde(self):
        from core.dienste.kostuemkreislauf import Kostuemkreislauf

        alt = Kostuemparameter.start()
        a = dict(alt, **{'hut.hoehe': alt['hut.hoehe'] + 0.02})
        b = dict(alt, **{'stab.hoehe': alt['stab.hoehe'] + 0.05})
        c = dict(alt, **{'bart.laenge': alt['bart.laenge'] + 0.03})
        ergebnisse = [
            self._ergebnis('k0', 0.20, a),
            self._ergebnis('k1', 0.21, b),
            self._ergebnis('k2', 0.30, c),  # schlechter als der Stand → zählt nicht
        ]
        mix = Kostuemkreislauf._mischen(alt, ergebnisse[0], ergebnisse, 0.25)
        self.assertEqual(mix['hut.hoehe'], a['hut.hoehe'])
        self.assertEqual(mix['stab.hoehe'], b['stab.hoehe'])
        self.assertEqual(mix['bart.laenge'], alt['bart.laenge'])

    def test_ohne_zweiten_gewinner_gibt_es_keinen_mix(self):
        from core.dienste.kostuemkreislauf import Kostuemkreislauf

        alt = Kostuemparameter.start()
        a = dict(alt, **{'hut.hoehe': alt['hut.hoehe'] + 0.02})
        ergebnisse = [self._ergebnis('k0', 0.20, a), self._ergebnis('k1', 0.40, alt)]
        self.assertIsNone(Kostuemkreislauf._mischen(alt, ergebnisse[0], ergebnisse, 0.25))


class KostuemrundeSichtTest(SimpleTestCase):
    @staticmethod
    def _runde(sicht=True, huelle=True):
        from core.dienste.kostuemrunde import Kostuemrunde

        runde = Kostuemrunde.__new__(Kostuemrunde)
        runde.sicht, runde.huelle, runde._letzte_sicht = sicht, huelle, None
        return runde

    def test_das_sichtmodell_ist_nur_alle_fuenf_minuten_faellig(self):
        runde = self._runde()
        with mock.patch('core.dienste.kostuemrunde.time.perf_counter', side_effect=[100.0, 200.0, 500.0]):
            self.assertEqual([runde.sicht_faellig() for _ in range(3)], [True, False, True])

    def test_ohne_huelle_oder_ohne_option_gibt_es_kein_sichtmodell(self):
        self.assertFalse(self._runde(huelle=False).sicht_faellig())
        self.assertFalse(self._runde(sicht=False).sicht_faellig())

    def test_das_ergebnis_eines_gescheiterten_baus_ist_leer(self):
        from core.dienste.kostuemmodell import Kostuemmodell

        leer = Kostuemmodell()
        self.assertEqual((leer.glb, leer.fotos, leer.sicht, leer.sichtfotos), (None, {}, None, {}))

    def test_die_option_sichtmodell_hat_eine_vorgabe(self):
        self.assertEqual(Kostuemoptionen.vorgaben()['sichtmodell'], 'an')


class KostuemarbeiterLesenTest(SimpleTestCase):
    def setUp(self):
        self.ordner = Path(
            tempfile.mkdtemp(
                prefix='kostuemlesen_', dir=str(Path(__file__).resolve().parents[3] / 'ProjektTemp')
            )
        )
        self.addCleanup(shutil.rmtree, self.ordner, ignore_errors=True)
        self.datei = self.ordner / 'antwort_000001.json'
        self.datei.write_text(json.dumps({'kandidaten': {}}), encoding='utf-8')

    def test_eine_verweigerte_datei_wird_wiederholt_gelesen(self):
        # 30.09.2026 01:39: ein einziges PermissionError (Windows, kurz nach `os.replace`) beendete einen Lauf.
        echt = open
        versuche = []

        def verweigern(pfad, *args, **kwargs):
            versuche.append(pfad)
            if len(versuche) < 3:
                raise PermissionError(13, 'Permission denied')
            return echt(pfad, *args, **kwargs)

        with mock.patch('builtins.open', verweigern):
            antwort = Kostuemarbeiter._lesen(self.datei)
        self.assertEqual(antwort, {'kandidaten': {}})
        self.assertEqual(len(versuche), 3)

    def test_nach_der_wartezeit_wird_ein_runtimeerror_daraus(self):
        # RuntimeError, damit `Kostuemblender` die Runde noch einmal mit frischen Arbeitern versucht.
        with (
            mock.patch('builtins.open', side_effect=PermissionError(13, 'Permission denied')),
            mock.patch.object(Kostuemarbeiter, 'LESEN_S', 0.05),
            self.assertRaises(RuntimeError),
        ):
            Kostuemarbeiter._lesen(self.datei)

    def test_eine_halbe_datei_wird_wiederholt(self):
        self.datei.write_text('{"kandidaten": ', encoding='utf-8')
        with mock.patch.object(Kostuemarbeiter, 'LESEN_S', 0.05), self.assertRaises(RuntimeError):
            Kostuemarbeiter._lesen(self.datei)


class KostuemloeschungTexturTest(SimpleTestCase):
    def test_die_fototextur_ansichten_gehen_mit_der_runde(self):
        ordner = Path(
            tempfile.mkdtemp(
                prefix='kostuemloesch_', dir=str(Path(__file__).resolve().parents[3] / 'ProjektTemp')
            )
        )
        self.addCleanup(shutil.rmtree, ordner, ignore_errors=True)
        namen = [
            'runde_007_vergleich.png',
            'runde_007_modell.glb',
            'runde_007_ansicht_+000.png',
            'runde_007_textur_+000.png',
            'runde_008_textur_+000.png',
            'runde_007_sicht.glb',
            'runde_007_sicht_+000.png',
        ]
        for n in namen:
            (ordner / n).write_bytes(b'x')
        eintrag = {
            'runde': 7,
            'dateien': {'vergleich': namen[0], 'modell': namen[1], 'sicht': namen[5]},
            'je_ansicht': [{'render': namen[2], 'textur': namen[3], 'sicht': namen[6]}, {'render': None}],
        }
        loeschung = Kostuemloeschung.__new__(Kostuemloeschung)
        loeschung.job = SimpleNamespace(kennung='x')
        loeschung.ablage = SimpleNamespace(iterationen=lambda name: ordner / name)
        loeschung._dateien_loeschen(eintrag)
        self.assertEqual(sorted(p.name for p in ordner.iterdir()), ['runde_008_textur_+000.png'])

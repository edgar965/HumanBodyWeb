# -*- coding: utf-8 -*-
"""V4Lauf — Befehl, Ausgabedeutung und Ergebnisprüfung des MocapNET-v4-Laufs.

WARUM DIESER TEST (17.08.2026)
=============================
`_run_v4_pipeline` war 120 Zeilen und völlig ungedeckt: Der echte Lauf braucht
MocapNET, MediaPipe und ein Video, also lief er in keinem Test. Beim Umbau in
`V4Lauf` sind zwei Dinge zusammengelegt worden — die Fortschrittsauswertung kommt
jetzt aus `Erkennungsfortschritt` (sie stand dort ein zweites Mal). Genau solche
Zusammenlegungen brauchen einen Beleg.

Geprüft wird ohne MocapNET, mit einem echten kleinen Python-Prozess als Wrapper
(dieselbe Art Attrappe wie in `test_pipeline_process.py`):

* Der Befehl trägt die Bauteil-Schalter des Auftrags, nicht die Vorgabe.
* `DONE:`/`STOPPED:` setzen den Ausgabepfad nur, wenn die Datei existiert —
  sonst zeigte der Auftrag auf eine Datei, die es nicht gibt.
* Rückgabewert ≠ 0 mit brauchbarer Teil-BVH -> die Teil-BVH zählt (Abbruch).
* Rückgabewert ≠ 0 ohne Datei -> `RuntimeError` mit stderr im Text.
* `PROGRESS:` schreibt Prozent und Restzeit an den Auftrag (bis 98 %, nicht 45).
"""

import os
import sys

from django.test import TestCase, override_settings

from core.pipelines.mocapnet4 import V4Lauf
from core.tests.attrappen import AuftragsAttrappe


class V4Basis(TestCase):
    """Ein Wrapper-Doppel: gibt vorgegebene Zeilen aus und endet mit `code`."""

    def setUp(self):
        from django.conf import settings
        from pathlib import Path
        self.ordner = Path(settings.BASE_DIR) / 'media' / 'tmp' / 'v4test'
        self.ordner.mkdir(parents=True, exist_ok=True)
        for datei in self.ordner.glob('*'):
            datei.unlink()

    def lauf(self, zeilen=(), code=0, params=None):
        """`V4Lauf`, dessen Wrapper-Skript die übergebenen Zeilen ausgibt."""
        skript = self.ordner / 'wrapper.py'
        skript.write_text(
            'import sys\n'
            + ''.join('print(%r, flush=True)\n' % z for z in zeilen)
            + 'sys.exit(%d)\n' % code, encoding='utf-8')
        auftrag = AuftragsAttrappe('v4', params)
        # Die Einstellungen müssen bis zum ENDE des Tests gelten, nicht nur bis
        # zum Ende dieser Methode: Beim ersten Wurf stand `fahren()` hinter dem
        # `with`-Block — damit lief das ECHTE MocapNET-Skript los.
        umgebung = override_settings(MOCAPNET_V4_SCRIPT=str(skript),
                                     MOCAPNET_V4_ROOT=str(self.ordner),
                                     PIPELINE_PYTHON=sys.executable)
        umgebung.enable()
        self.addCleanup(umgebung.disable)
        return auftrag, V4Lauf(auftrag, self.ordner / 'video.mp4', self.ordner)

    def bvh_ablegen(self, name='fertig.bvh', gross=True):
        pfad = self.ordner / name
        pfad.write_text('HIERARCHY\n' + ('x' * (200 if gross else 5)),
                        encoding='utf-8')
        return pfad


class BefehlTest(V4Basis):

    def test_auftrag_schlaegt_die_vorgabe(self):
        _, lauf = self.lauf(params={'face': True, 'hands': False,
                                    'hcd_iterations': 0})
        befehl = lauf._befehl()
        self.assertIn('--face', befehl)
        self.assertNotIn('--hands', befehl)
        self.assertEqual(befehl[befehl.index('--hcd-iterations') + 1], '0')

    def test_stoppmarke_und_ausgabe_stehen_im_befehl(self):
        _, lauf = self.lauf()
        befehl = lauf._befehl()
        self.assertIn('--stop-flag', befehl)
        self.assertEqual(befehl[befehl.index('--stop-flag') + 1], lauf.stoppmarke)
        self.assertTrue(befehl[befehl.index('--output') + 1].endswith(
            'v4_tanz.bvh'))
        self.assertIn('--headless', befehl)


class AusgabeTest(V4Basis):

    def test_done_setzt_nur_vorhandene_datei(self):
        _, lauf = self.lauf()
        lauf._gemeldeter_pfad(' /gibtsnicht/x.bvh ')
        self.assertTrue(lauf.bvh.endswith('v4_tanz.bvh'), 'unverändert')
        echt = self.bvh_ablegen()
        lauf._gemeldeter_pfad(' %s ' % echt)
        self.assertEqual(lauf.bvh, str(echt))

    def test_fortschritt_zaehlt_bis_98_prozent(self):
        auftrag, lauf = self.lauf(zeilen=['TOTAL:100', 'PROGRESS:100/100',
                                          'DONE:' + str(self.bvh_ablegen())])
        ergebnis = lauf.fahren()
        self.assertTrue(ergebnis.endswith('fertig.bvh'))
        self.assertEqual(auftrag.progress, 98,
                         'v4 macht Erkennung UND BVH — Anteil 98, nicht 45')
        self.assertIn('100 / 100 frames', auftrag.progress_detail)

    def test_stoppmarke_wird_aufgeraeumt(self):
        _, lauf = self.lauf(zeilen=['DONE:' + str(self.bvh_ablegen())])
        open(lauf.stoppmarke, 'w').close()
        lauf.fahren()
        self.assertFalse(os.path.exists(lauf.stoppmarke))


class ErgebnisTest(V4Basis):

    def test_teil_bvh_zaehlt_nach_abbruch(self):
        """Abgebrochen, aber mit Bewegung darin — das Ergebnis bleibt."""
        teil = self.bvh_ablegen('teil.bvh')
        _, lauf = self.lauf(zeilen=['STOPPED:' + str(teil)], code=1)
        self.assertEqual(lauf.fahren(), str(teil))

    def test_zu_kleine_datei_zaehlt_nicht(self):
        klein = self.bvh_ablegen('rumpf.bvh', gross=False)
        _, lauf = self.lauf(zeilen=['STOPPED:' + str(klein)], code=1)
        with self.assertRaises(RuntimeError):
            lauf.fahren()

    def test_fehlschlag_nennt_den_ausgang_und_stderr(self):
        _, lauf = self.lauf(zeilen=[], code=3)
        with self.assertRaises(RuntimeError) as gefangen:
            lauf.fahren()
        self.assertIn('exit code 3', str(gefangen.exception))

    def test_ohne_datei_ist_es_ein_fehler(self):
        """Rückgabewert 0, aber keine BVH — das darf nicht als Erfolg gelten."""
        _, lauf = self.lauf(zeilen=['TOTAL:10'], code=0)
        with self.assertRaises(RuntimeError) as gefangen:
            lauf.fahren()
        self.assertIn('BVH file not found', str(gefangen.exception))

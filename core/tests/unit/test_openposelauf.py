# -*- coding: utf-8 -*-
"""Tests fuer Openposelauf — Fortschritt, Kennung, Fehlerfaelle.

Anlass ist der Umbau vom 16.08.2026: `_run_openpose_to_csv` war mit 138 Zeilen
die laengste Funktion des Projekts und ohne einen einzigen Test — man haette sie
nur mit installiertem OpenPose und einem Video pruefen koennen.

Als Klasse ist das anders: Die Teile, an denen sich rechnen laesst (Anteil am
Gesamtfortschritt, Restzeit, Ableiten der Dateikennung), brauchen keinen
Prozess. Genau die sind hier gepruefT — zusammen mit den beiden Fehlerwegen,
die im Betrieb am meisten Aerger machen: abgebrochener Lauf und leeres
Ausgabeverzeichnis.
"""

import shutil
import tempfile
from pathlib import Path

from django.conf import settings
from django.test import TestCase

from core.models import BVHJob
from core.pipelines.openposelauf import Openposelauf


class ProzessAttrappe:
    """Tut so, als waere OpenPose gelaufen — ohne OpenPose."""

    def __init__(self, rueckgabe=0, fehlertext=''):
        self.proc = self
        self.returncode = rueckgabe
        self._fehlertext = fehlertext
        self.gewartet = False

    def poll(self):
        return self.returncode

    def warten(self, timeout=None):
        self.gewartet = True

    def fehlertext(self):
        return self._fehlertext


class LaufendeAttrappe:
    def __init__(self):
        self.eingetragen = []

    def eintragen(self, kennung, proc):
        self.eingetragen.append(kennung)


class OpenposelaufTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        cls.ordner = Path(tempfile.mkdtemp(prefix='openpose_', dir=str(basis)))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.ordner, ignore_errors=True)
        super().tearDownClass()

    def lauf(self, bildzahl=100, rueckgabe=0, fehlertext='', unterordner='a'):
        job = BVHJob.objects.create(video_file='x.mp4', pipeline='openpose')
        ausgabe = self.ordner / unterordner
        ausgabe.mkdir(exist_ok=True)
        lauf = Openposelauf(job, 'video.mp4', ausgabe, bildzahl,
                            None, LaufendeAttrappe())
        lauf._prozessattrappe = ProzessAttrappe(rueckgabe, fehlertext)
        Path(lauf.jsonordner).mkdir(parents=True, exist_ok=True)
        return lauf

    def json_anlegen(self, lauf, anzahl, kennung='clip_'):
        for i in range(anzahl):
            name = '%s%012d%s' % (kennung, i, Openposelauf.JSON_ENDUNG)
            (Path(lauf.jsonordner) / name).write_text('{}', encoding='utf-8')

    # ------------------------------------------------------------- Fortschritt

    def test_anteil_beginnt_bei_zwei_und_endet_bei_38(self):
        """Die Auftragsseite rechnet damit, dass 2D-Erkennung bei 38 % endet."""
        lauf = self.lauf(bildzahl=100)
        lauf._bildfortschritt(1, 1.0)
        self.assertGreaterEqual(lauf.job.progress, Openposelauf.VON_PROZENT)
        lauf._bildfortschritt(100, 10.0)
        self.assertEqual(lauf.job.progress, Openposelauf.BIS_PROZENT)

    def test_anteil_ueberschreitet_38_nie(self):
        """Mehr Bilder als angekuendigt darf den Balken nicht sprengen."""
        lauf = self.lauf(bildzahl=100)
        lauf._bildfortschritt(500, 10.0)
        self.assertEqual(lauf.job.progress, Openposelauf.BIS_PROZENT)

    def test_meldung_enthaelt_tempo_und_restzeit(self):
        lauf = self.lauf(bildzahl=200)
        lauf._bildfortschritt(50, 5.0)     # 10 Bilder je Sekunde
        text = lauf.job.progress_detail
        self.assertIn('50 / 200 frames', text)
        self.assertIn('10.0 fps', text)
        self.assertIn('left', text)

    def test_ohne_bekannte_bildzahl_nur_zaehler(self):
        lauf = self.lauf(bildzahl=0)
        lauf._bildfortschritt(17, 2.0)
        self.assertEqual(lauf.job.progress_detail, '17 frames processed')

    def test_kein_teilen_durch_null_bei_erstem_bild(self):
        """rechenzeit=0 kommt vor: das erste Bild ist sofort da."""
        lauf = self.lauf(bildzahl=10)
        lauf._bildfortschritt(1, 0.0)      # darf nicht werfen
        self.assertIn('1 / 10 frames', lauf.job.progress_detail)

    def test_geschriebene_bilder_zaehlen_nur_keypoints(self):
        lauf = self.lauf(unterordner='zaehlen')
        self.json_anlegen(lauf, 3)
        (Path(lauf.jsonordner) / 'liesmich.txt').write_text('x', encoding='utf-8')
        self.assertEqual(lauf._geschriebeneBilder(0), 3)

    def test_fehlendes_verzeichnis_gibt_den_ersatzwert(self):
        lauf = self.lauf(unterordner='weg')
        shutil.rmtree(lauf.jsonordner)
        self.assertEqual(lauf._geschriebeneBilder(42), 42)

    # ------------------------------------------------------------------ Kennung

    def test_kennung_aus_dateiname(self):
        self.assertEqual(
            Openposelauf._kennungAusDateiname('clip_000000000000_keypoints.json'),
            ('clip_', 12))

    def test_kennung_mit_unterstrichen_im_namen(self):
        self.assertEqual(
            Openposelauf._kennungAusDateiname('mein_video_2_00000_keypoints.json'),
            ('mein_video_2_', 5))

    def test_kennung_ohne_nummernteil(self):
        """Fehlt der Nummernteil, bleibt es bei zwoelf Stellen.

        Der Unterstrich wird dabei angehaengt, obwohl im Namen keiner uebrig
        ist — so verhielt sich schon die Vorgaengerfassung (`parts[0] + '_'`),
        und der Fall kommt in echten OpenPose-Ausgaben nicht vor. Der Test
        haelt das Verhalten fest, statt es stillschweigend zu aendern.
        """
        self.assertEqual(
            Openposelauf._kennungAusDateiname('clip_keypoints.json'), ('clip_', 12))

    # ------------------------------------------------------------- Fehlerwege

    def test_leeres_verzeichnis_meldet_klar(self):
        lauf = self.lauf(unterordner='leer')
        with self.assertRaises(RuntimeError) as fehler:
            lauf._ergebnisPruefen(ProzessAttrappe(0))
        self.assertIn('No keypoint JSON files', str(fehler.exception))

    def test_abbruch_ohne_bilder_wird_als_abbruch_gemeldet(self):
        lauf = self.lauf(unterordner='abbruch')
        (lauf.ausgabeordner / 'STOP_FLAG').write_text('', encoding='utf-8')
        with self.assertRaises(RuntimeError) as fehler:
            lauf._ergebnisPruefen(ProzessAttrappe(1))
        self.assertIn('Stopped early', str(fehler.exception))

    def test_fehlercode_nimmt_den_gesammelten_text_mit(self):
        """Der Text kommt aus dem Lesefaden — `proc.stderr.read()` waere leer."""
        lauf = self.lauf(unterordner='fehler')
        self.json_anlegen(lauf, 1)
        with self.assertRaises(RuntimeError) as fehler:
            lauf._ergebnisPruefen(ProzessAttrappe(3, 'CUDA out of memory'))
        text = str(fehler.exception)
        self.assertIn('exit code 3', text)
        self.assertIn('CUDA out of memory', text)

    def test_abbruch_mit_bildern_gilt_als_erfolg(self):
        """Wer waehrend des Laufs abbricht, hat brauchbare Teilbilder."""
        lauf = self.lauf(unterordner='teilweise')
        (lauf.ausgabeordner / 'STOP_FLAG').write_text('', encoding='utf-8')
        self.json_anlegen(lauf, 5)
        dateien = lauf._ergebnisPruefen(ProzessAttrappe(1))
        self.assertEqual(len(dateien), 5)
        self.assertEqual(lauf.job.progress, Openposelauf.BIS_PROZENT)

    def test_dateien_kommen_sortiert(self):
        lauf = self.lauf(unterordner='sortiert')
        self.json_anlegen(lauf, 12)
        dateien = lauf._ergebnisPruefen(ProzessAttrappe(0))
        self.assertEqual(dateien, sorted(dateien))
        self.assertEqual(len(dateien), 12)

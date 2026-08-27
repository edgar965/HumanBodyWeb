# -*- coding: utf-8 -*-
"""Hybridlauf — die Verzweigungen des Doppellaufs festnageln.

WARUM DIESER TEST (17.08.2026)
=============================
`_run_hybrid_pipeline` war 164 Zeilen und ist beim Umbau in Methoden zerlegt
worden (`Hybridlauf`, `Teilauftrag`). Gedeckt war davon NICHTS: Der Lauf braucht
GPU, GVHMR und MocapNET, also lief er in keinem Test. Genau deshalb ist er die
gefährlichste Sorte Umbau — ein Fehler fällt erst beim nächsten echten Video auf.

Geprüft wird, was das Projekt verantwortet, mit umgeleiteten Unter-Pipelines:

* Beide Läufe erfolgreich -> beide Dateien landen im Auftrag.
* Ein Lauf scheitert -> das Teilergebnis bleibt, die Meldung steht im Fortschritt.
* Beide scheitern -> `RuntimeError` (der Auftrag darf nicht „fertig" heißen).
* Die v4-Parameter: `hcd_iterations` MUSS 0 sein (die IK-Feinarbeit der
  BVHConverter.dll stürzt im Hybridbetrieb mit Stapelüberlauf ab).
* Die beiden Unteraufträge haben EIGENE Kennungen — sonst trifft „Abbrechen"
  beim Gesicht den Körperlauf.
* Die Gesichtsausdrücke laufen nur, wenn es eine Gesichts-BVH gibt und die
  Quelle `smplest_x` ist; ihr Fehlschlag beendet den Lauf NICHT.

UMLEITUNG: Gepatcht wird in `core.pipelines.hybridlauf`, weil eine Funktion ihre
freien Namen im Namensraum IHRES Moduls liest. Ein Patch an `smpllauf` würde ins
Leere greifen (Projektregel „Test-Umleitungen, die ins Leere greifen").
"""

from django.test import TestCase

from core.pipelines import hybridlauf
from core.pipelines.hybridlauf import Hybridlauf
from core.pipelines.teilauftrag import Teilauftrag
from core.tests.attrappen import AuftragsAttrappe


class HybridBasis(TestCase):
    """Gemeinsame Umleitung: keine echte Pipeline, kein Unterprozess."""

    def setUp(self):
        self.aufrufe = {'koerper': None, 'gesicht': None, 'ausdruck': None}
        self.koerper = lambda auftrag, video, ordner: 'body.bvh'
        self.gesicht = lambda auftrag, video, ordner: 'face.bvh'
        pruefung = self

        class Laufattrappe:
            """Steht fuer `Smpllauf`/`V4Lauf` — merkt sich den Unterauftrag.

            Seit dem 27.08.2026 uebergibt `Hybridlauf` die KLASSE an den
            Faden und ruft `.fahren()`; die Attrappe muss deshalb ebenfalls
            eine Klasse sein (vorher waren es zwei freie Funktionen).
            """

            welcher = ''

            def __init__(self, auftrag, video, ordner):
                self.auftrag, self.video, self.ordner = auftrag, video, ordner
                pruefung.aufrufe[self.welcher] = auftrag

            def fahren(self):
                macher = getattr(pruefung, self.welcher)
                return macher(self.auftrag, self.video, self.ordner)

        class Koerperattrappe(Laufattrappe):
            welcher = 'koerper'

        class Gesichtsattrappe(Laufattrappe):
            welcher = 'gesicht'

        def lauf(befehl, **kw):
            self.aufrufe['ausdruck'] = befehl
            return None

        self._alt = (hybridlauf.Smpllauf, hybridlauf.V4Lauf,
                     hybridlauf.subprocess.run, Hybridlauf.TAKT)
        hybridlauf.Smpllauf = Koerperattrappe
        hybridlauf.V4Lauf = Gesichtsattrappe
        hybridlauf.subprocess.run = lauf
        # Ohne das schläft `_verfolgen` zwei Sekunden je Runde.
        Hybridlauf.TAKT = 0.01

    def tearDown(self):
        (hybridlauf.Smpllauf, hybridlauf.V4Lauf,
         hybridlauf.subprocess.run, Hybridlauf.TAKT) = self._alt

    def fahren(self, pipeline='hybrid_gvhmr', params=None):
        from django.conf import settings
        from pathlib import Path
        ordner = Path(settings.BASE_DIR) / 'media' / 'tmp' / 'hybridtest'
        auftrag = AuftragsAttrappe(pipeline, params, kennung=42)
        ergebnis = Hybridlauf(auftrag, 'tanz.mp4', ordner).fahren()
        return auftrag, ergebnis


class HybridErfolgTest(HybridBasis):

    def test_beide_dateien_landen_im_auftrag(self):
        auftrag, ergebnis = self.fahren()
        self.assertEqual(ergebnis, ('body.bvh', 'face.bvh'))
        self.assertEqual(auftrag.bvh_file, 'body.bvh')
        self.assertEqual(auftrag.bvh_file_face, 'face.bvh')
        self.assertEqual(auftrag.progress_detail, 'Done')

    def test_eigene_kennung_je_unterauftrag(self):
        """Gleiche Kennung hieße: „Abbrechen" beim Gesicht trifft den Körper."""
        self.fahren()
        self.assertEqual(self.aufrufe['koerper'].id, '42_body')
        self.assertEqual(self.aufrufe['gesicht'].id, '42_face')

    def test_unterauftrag_schreibt_nicht_in_die_datenbank(self):
        self.fahren()
        for welcher in ('koerper', 'gesicht'):
            self.assertIsInstance(self.aufrufe[welcher], Teilauftrag)
            # `save()` darf nichts tun — sonst überschreiben sich die beiden
            # Fortschritte im echten Auftrag.
            self.assertIsNone(self.aufrufe[welcher].save())

    def test_v4_ohne_ik_feinarbeit(self):
        """`hcd_iterations` > 0 lässt BVHConverter.dll abstürzen."""
        self.fahren()
        self.assertEqual(self.aufrufe['gesicht'].pipeline_params['hcd_iterations'], 0)
        self.assertTrue(self.aufrufe['gesicht'].pipeline_params['body'])

    def test_rueckgrat_haengt_am_pipelinenamen(self):
        self.fahren('hybrid_gvhmr')
        self.assertEqual(self.aufrufe['koerper'].pipeline, 'gvhmr')
        self.fahren('hybrid_prompthmr')
        self.assertEqual(self.aufrufe['koerper'].pipeline, 'prompthmr')


class HybridTeilergebnisTest(HybridBasis):

    def test_koerper_scheitert_gesicht_bleibt(self):
        def platzt(auftrag, video, ordner):
            raise RuntimeError('kein CUDA')
        self.koerper = platzt
        auftrag, ergebnis = self.fahren()
        self.assertEqual(ergebnis, (None, 'face.bvh'))
        self.assertFalse(auftrag.bvh_file, 'nichts eingetragen')
        self.assertEqual(auftrag.bvh_file_face, 'face.bvh')
        self.assertIn('kein CUDA', auftrag.progress_detail)
        self.assertIn('partial', auftrag.progress_detail)

    def test_beide_scheitern_ist_ein_fehler(self):
        def platzt(auftrag, video, ordner):
            raise RuntimeError('nichts geht')
        self.koerper = platzt
        self.gesicht = platzt
        with self.assertRaises(RuntimeError) as gefangen:
            self.fahren()
        self.assertIn('Hybrid pipeline failed', str(gefangen.exception))


class HybridAusdrueckeTest(HybridBasis):

    def test_ausdruecke_werden_gezogen(self):
        self.fahren()
        self.assertIsNotNone(self.aufrufe['ausdruck'])
        self.assertTrue(self.aufrufe['ausdruck'][-1].endswith(
            'face_blendshapes.json'))

    def test_andere_quelle_zieht_keine_ausdruecke(self):
        self.fahren(params={'face_source': 'v4'})
        self.assertIsNone(self.aufrufe['ausdruck'])

    def test_ohne_gesichts_bvh_keine_ausdruecke(self):
        self.gesicht = lambda auftrag, video, ordner: None
        self.fahren()
        self.assertIsNone(self.aufrufe['ausdruck'])

    def test_fehlschlag_beendet_den_lauf_nicht(self):
        """Ohne Ausdrücke ist der Lauf unvollständig, aber nicht kaputt."""
        def platzt(befehl, **kw):
            raise OSError('SMPLest-X fehlt')
        hybridlauf.subprocess.run = platzt
        auftrag, ergebnis = self.fahren()
        self.assertEqual(ergebnis, ('body.bvh', 'face.bvh'))
        self.assertEqual(auftrag.progress_detail, 'Done')

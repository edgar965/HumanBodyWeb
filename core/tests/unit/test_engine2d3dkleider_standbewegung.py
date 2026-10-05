# -*- coding: utf-8 -*-
"""Die Bewegung der BVH auf der Figur vor dem Film (`Standbewegung`, 04.10.2026).

DER ANLASS
==========
Edgar (04.10.2026): „play der animation im 3Dview nicht verfügbar, Render einstellungen usw" — an einem Auftrag, der bis „Kleiderstücke" gerechnet war. Die Bühne spielt nur ab, wenn
`ergebnis.film.bewegung` steht, und die schrieb bisher allein der Schritt „film" (nach Iterationen und Export).

WAS DIESE PRÜFUNG NICHT IST
===========================
Kein Retarget, keine BVH-Datei mit Bewegung: `Engine2d3dKleiderbewegung.rechnen` ist durch eine Attrappe ersetzt. Dass die echte Bewegung auf der Figur der Bühne läuft, zeigte der Auftrag
2026.10.04.11.11.44 im Browser (489 Bilder, 16,3 s, 4,4 s Rechenzeit; das Hüftgelenk dreht sich beim Abspielen). Geschrieben am 04.10.2026; gelaufen am 04.10.2026 auf Edgars Ansage: 9 Tests, alle grün.

BDD - GEGEBEN / DANN
====================
    Ein Auftrag ohne BVH-Datei              ... nichts wird gerechnet, `ergebnis` bleibt, wie es war
    Ein Auftrag mit Figur und BVH           ... `film_bewegung.json` liegt in `ergebnis/`, `ergebnis.film` nennt Bewegung, BVH und Bilderzahl
    Dasselbe ein zweites Mal                ... gleicher Fingerabdruck, die Bewegung wird nicht neu gerechnet
    Eine neue Stellung (Körper neu)         ... die Bewegung wird neu gerechnet
    Ein Film, der schon Video ablegte       ... Video, Bilder und Bildrate bleiben stehen
    Der Lauf nach „Kleiderstücke"           ... ruft die Bewegung; scheitert sie, wird das Standmodell trotzdem gebaut
"""

import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from django.test import SimpleTestCase

from core.dienste.engine2d3dkleiderlauf import Engine2d3dKleiderlauf
from core.dienste.standbewegung import Standbewegung

from ._pruefablage import Pruefablage


class _Ablage:
    def __init__(self, wurzel):
        self.wurzel = Path(wurzel)

    def ergebnis(self, name=''):
        return self.wurzel / 'ergebnis' / name

    def arbeit(self, name=''):
        return self.wurzel / 'arbeit' / name


class DieStandbewegung(SimpleTestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='standbewegung_', dir=Pruefablage.wurzel()))
        (self.tmp / 'ergebnis').mkdir()
        self.ablage = _Ablage(self.tmp)
        self.bvh = self.tmp / 'tanz.bvh'
        self.bvh.write_text('HIERARCHY', encoding='utf-8')
        # Die echte Prüfung der Optionen liest die App-Einstellungen (Datenbank) — hier nicht: die Gruppe `film` kommt unverändert zurück.
        optionen = mock.patch('core.dienste.standbewegung.Engine2d3dKleideroptionen.film', side_effect=lambda o: dict((o or {}).get('film') or {}))
        optionen.start()
        self.addCleanup(optionen.stop)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _job(self, bvh=True, stellung=None, ergebnis=None):
        optionen = {'film': {'bvh': str(self.bvh) if bvh else ''}, 'figur': {'hoehe_cm': 170}}
        return SimpleNamespace(kennung='x', optionen=optionen, ergebnis=ergebnis if ergebnis is not None else {},
                               stellung=lambda: {'FBMHeavy': 0.5} if stellung is None else stellung)

    def _rechnen(self):
        """Die Attrappe: legt `bewegung.json` im Arbeitsordner ab wie `Engine2d3dKleiderbewegung.rechnen`."""
        def rechnen(_, bvh, aus):
            pfad = Path(aus) / 'bewegung.json'
            pfad.write_text('{"tracks": {}}', encoding='utf-8')
            return pfad, SimpleNamespace(frame_count=489)
        return mock.patch('core.dienste.standbewegung.Engine2d3dKleiderbewegung.rechnen', autospec=True, side_effect=rechnen)

    def test_ohne_bvh_datei_wird_nichts_gerechnet(self):
        job = self._job(bvh=False)
        with self._rechnen() as rechnen:
            self.assertFalse(Standbewegung(job, self.ablage).sichern())
        rechnen.assert_not_called()
        self.assertEqual(job.ergebnis, {})

    def test_ohne_figur_wird_nichts_gerechnet(self):
        with self._rechnen() as rechnen:
            self.assertFalse(Standbewegung(self._job(stellung={}), self.ablage).sichern())
        rechnen.assert_not_called()

    def test_mit_figur_und_bvh_liegt_die_bewegung_in_ergebnis_und_im_auftrag(self):
        job = self._job()
        with self._rechnen():
            self.assertTrue(Standbewegung(job, self.ablage).sichern())
        self.assertTrue((self.tmp / 'ergebnis' / 'film_bewegung.json').is_file())
        film = job.ergebnis['film']
        self.assertEqual((film['bewegung'], film['bvh'], film['bewegung_bilder']), ('film_bewegung.json', str(self.bvh), 489))
        self.assertTrue(film['bewegung_stand'])

    def test_derselbe_stand_rechnet_nicht_noch_einmal(self):
        job = self._job()
        with self._rechnen() as rechnen:
            Standbewegung(job, self.ablage).sichern()
            self.assertFalse(Standbewegung(job, self.ablage).sichern())
        self.assertEqual(rechnen.call_count, 1)

    def test_eine_neue_stellung_rechnet_neu(self):
        job = self._job()
        with self._rechnen() as rechnen:
            Standbewegung(job, self.ablage).sichern()
            neu = self._job(stellung={'FBMHeavy': 0.9}, ergebnis=job.ergebnis)
            self.assertTrue(Standbewegung(neu, self.ablage).sichern())
        self.assertEqual(rechnen.call_count, 2)

    def test_was_der_film_schritt_schon_ablegte_bleibt_stehen(self):
        job = self._job(ergebnis={'film': {'video': 'film_video.mp4', 'bilder': 300, 'bildrate': 30, 'uebersprungen': 'Keine BVH-Datei gewählt'}})
        with self._rechnen():
            Standbewegung(job, self.ablage).sichern()
        film = job.ergebnis['film']
        self.assertEqual((film['video'], film['bilder'], film['bildrate']), ('film_video.mp4', 300, 30))
        self.assertNotIn('uebersprungen', film)                    # galt nur, solange es keine BVH gab


class DerLaufMitBewegung(SimpleTestCase):
    @staticmethod
    def _lauf():
        lauf = SimpleNamespace(job=SimpleNamespace(kennung='x'), ablage=object(), gesichert=[])
        lauf.melden = lambda a, t: None
        lauf.sichern = lambda *felder: lauf.gesichert.append(felder)
        return lauf

    def test_nach_den_kleiderstuecken_kommt_die_bewegung_vor_dem_standmodell(self):
        lauf = self._lauf()
        reihenfolge = []
        with mock.patch('core.dienste.standbewegung.Standbewegung') as bewegung, \
                mock.patch('core.dienste.engine2d3dkleiderstandmodell.Engine2d3dKleiderstandmodell') as stand:
            bewegung.return_value.sichern.side_effect = lambda: reihenfolge.append('bewegung') or True
            stand.return_value.bauen.side_effect = lambda: reihenfolge.append('stand')
            Engine2d3dKleiderlauf._standmodell(lauf, ['kleiderstuecke'])
        self.assertEqual(reihenfolge, ['bewegung', 'stand'])
        self.assertEqual(lauf.gesichert, [('ergebnis',)])

    def test_scheitert_die_bewegung_wird_das_standmodell_trotzdem_gebaut(self):
        lauf = self._lauf()
        with mock.patch('core.dienste.standbewegung.Standbewegung') as bewegung, \
                mock.patch('core.dienste.engine2d3dkleiderstandmodell.Engine2d3dKleiderstandmodell') as stand:
            bewegung.return_value.sichern.side_effect = RuntimeError('BVH kaputt')
            Engine2d3dKleiderlauf._standmodell(lauf, ['kleiderstuecke'])
        stand.return_value.bauen.assert_called_once()

    def test_nach_automatischen_runden_wird_nichts_gerechnet(self):
        lauf = self._lauf()
        lauf.job.optionen = {'iterationen': {'modus': 'automatisch'}}
        with mock.patch('core.dienste.standbewegung.Standbewegung') as bewegung, \
                mock.patch('core.dienste.engine2d3dkleiderstandmodell.Engine2d3dKleiderstandmodell') as stand:
            Engine2d3dKleiderlauf._standmodell(lauf, ['iterationen'])
        bewegung.assert_not_called()
        stand.return_value.bauen.assert_not_called()

    def test_nach_den_runden_von_hand_wird_das_modell_gebaut_ohne_bewegung(self):
        lauf = self._lauf()
        lauf.job.optionen = {'iterationen': {'modus': 'begutachtung'}}
        with mock.patch('core.dienste.standbewegung.Standbewegung') as bewegung, \
                mock.patch('core.dienste.engine2d3dkleiderstandmodell.Engine2d3dKleiderstandmodell') as stand:
            Engine2d3dKleiderlauf._standmodell(lauf, ['iterationen'])
        stand.return_value.bauen.assert_called_once()
        bewegung.assert_not_called()                                 # hängt nicht an den Runden

    def test_ohne_die_iterationen_im_lauf_baut_der_modus_von_hand_nichts(self):
        lauf = self._lauf()
        lauf.job.optionen = {'iterationen': {'modus': 'begutachtung'}}
        with mock.patch('core.dienste.engine2d3dkleiderstandmodell.Engine2d3dKleiderstandmodell') as stand:
            Engine2d3dKleiderlauf._standmodell(lauf, ['export', 'film'])
        stand.return_value.bauen.assert_not_called()

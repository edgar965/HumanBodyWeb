# -*- coding: utf-8 -*-
"""Wächter für die Tonmischung und den Ausgabenamen der Kollisions-Pipelines.

WARUM (Review 15.08.2026)
-------------------------
Drei Befunde, alle am Code nachgelesen und nachgestellt:

1. **`audio_mux._resolve_url` nahm jeden absoluten Pfad.** `if os.path.isfile(url):
   return url` — damit war jede Audiodatei des Rechners ein gültiger Toneingang
   für ffmpeg. Die URLs stehen in der Projektdatei des BVH-Studios, und
   Projektdateien werden weitergegeben; die Adresse muss also nicht von diesem
   Nutzer stammen. Dasselbe für `http://…`: jede Adresse wurde abgeholt.

2. **Die Suchwurzeln zeigten auf das ALTE Projekt** `A:\\HumanBodyTest` — das noch
   auf der Platte liegt (nachgesehen: es hat `media\\uploads`, `media\\output`).
   Lag dort eine Datei mit passendem relativem Pfad, nahm der Export SIE. Der
   HTTP-Rückfall ging auf `localhost:4040`, wo nichts hört (der Server läuft auf
   8081) — jeder Fehlschlag endete in `except: return None`, und `mux_audio`
   überspringt None stillschweigend. Video ohne Ton, keine Zeile im Protokoll.

3. **`cloth_export_api`: Der Rückfall-Dateiname ersetzte nur `/`, nicht `\\`.**
   Nachgerechnet:

       scene_name='..\\..\\..\\evil' -> A:\\3DTools\\evil_blender_eevee_….mp4
       scene_name='C:\\evil'         -> C:\\evil_blender_eevee_….mp4

   Am 12.08.2026 wurden `output_dir` und `filename` auf SafePath umgestellt; der
   Zweig OHNE `filename` blieb übrig.
"""
import glob
import os
import sys

from django.conf import settings
from django.test import SimpleTestCase

from core.cloth_export_api import _namensstamm


class NamensstammTest(SimpleTestCase):
    """Der Ausgabename darf den Ausgabeordner nicht verlassen."""

    AUSGABE = r'A:\3DTools\HumanBodyWeb\media\cloth_exports'

    def _ziel(self, scene_name):
        name = '%s_blender_eevee_1_abc.mp4' % _namensstamm(scene_name)
        return os.path.normpath(os.path.join(self.AUSGABE, name))

    def test_fiese_namen_bleiben_im_ordner(self):
        for sn in ('..\\..\\..\\evil', '../../evil', 'C:\\evil', 'C:/Windows/Temp/evil',
                   'x\\..\\..\\y', '\\\\server\\freigabe\\evil', 'lpt1', 'con'):
            with self.subTest(scene_name=sn):
                ziel = self._ziel(sn)
                self.assertTrue(ziel.lower().startswith(self.AUSGABE.lower()),
                                '%r landet in %s' % (sn, ziel))

    def test_normale_namen_bleiben_lesbar(self):
        self.assertEqual(_namensstamm('Ballett Probe 2'), 'Ballett_Probe_2')
        self.assertEqual(_namensstamm('kleid-v2_final'), 'kleid-v2_final')

    def test_leerer_name_wird_scene(self):
        for leer in ('', None, '   ', '///', '...'):
            with self.subTest(wert=leer):
                self.assertEqual(_namensstamm(leer), 'scene')

    def test_name_bleibt_kurz(self):
        self.assertLessEqual(len(_namensstamm('x' * 500)), 60)


class TonquellenTest(SimpleTestCase):
    """Nur Dateien aus dem Projekt und nur der eigene Server."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        wurzel = str(getattr(settings, 'HUMANBODY_ROOT', ''))
        if wurzel and wurzel not in sys.path:
            sys.path.insert(0, wurzel)
        from collision import audio_mux
        cls.am = audio_mux

    def test_wurzeln_zeigen_auf_dieses_projekt(self):
        for w in self.am.WURZELN:
            self.assertNotIn('HumanBodyTest', w,
                             'Suchwurzel zeigt noch auf das alte Projekt: %s' % w)
        self.assertTrue(any(w.endswith('HumanBodyWeb') for w in self.am.WURZELN))

    def test_basis_url_trifft_den_laufenden_server(self):
        """4040 war der Port, auf dem nichts hört."""
        self.assertNotIn('4040', self.am.BASIS_URL)

    def test_datei_im_projekt_wird_genommen(self):
        treffer = glob.glob(os.path.join(str(settings.MEDIA_ROOT), '**', '*.*'),
                            recursive=True)
        if not treffer:
            self.skipTest('keine Datei unter MEDIA_ROOT zum Prüfen')
        self.assertEqual(self.am._resolve_url(treffer[0]), treffer[0])

    def test_datei_ausserhalb_wird_abgelehnt(self):
        fremd = glob.glob(r'C:\Windows\Media\*.wav')
        if not fremd:
            self.skipTest('keine Fremddatei zum Prüfen gefunden')
        self.assertIsNone(self.am._resolve_url(fremd[0]))

    def test_fremder_host_wird_abgelehnt(self):
        for u in ('http://169.254.169.254/latest/meta-data',
                  'http://boese.example/x.wav',
                  'https://example.org/ton.mp3',
                  'file:///C:/Windows/win.ini'):
            with self.subTest(url=u):
                self.assertIsNone(self.am._resolve_url(u))

    def test_eigener_host_ist_erlaubt(self):
        """Gegenprobe: Die Prüfung darf den eigenen Server nicht aussperren."""
        for u in ('http://127.0.0.1:8081/media/x.wav',
                  'http://localhost:8081/media/x.wav'):
            with self.subTest(url=u):
                self.assertTrue(self.am._erlaubter_host(u))

    def test_download_landet_im_projekt_nicht_in_system_temp(self):
        ziel = str(self.am._download_ziel('/media/x/lied.mp3?v=2'))
        self.assertIn('media', ziel)
        self.assertFalse(ziel.upper().startswith('C:'),
                         'Zwischendatei liegt auf C: — im Projekt verboten')
        self.assertTrue(ziel.endswith('.mp3'))

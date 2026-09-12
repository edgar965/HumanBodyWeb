# -*- coding: utf-8 -*-
u"""/process/VideoToBVH/: nach dem Hochladen ist das neue Video das gewählte.

Edgar (12.09.2026): „gerade ein neues Video hochgeladen. danach soll das
neu hochgeladene das selektierte Video sein (im Moment noch das alte
selektierte)". Die Auswahl steht in `AppSettings.ui_prefs
['selected_video_path']` und wurde bis dahin nur beim Start einer
Pipeline geschrieben (`videowahl.js`) — der Upload ließ sie stehen, und
die Seite kam mit dem Haken auf dem Video des letzten Starts zurück.

`MEDIA_ROOT` zeigt auf eine Prüfablage: Der Upload landet nicht in
`media/uploads/`, und die Liste enthält nur die Videos dieser Prüfung.
Sabotage-Gegenprobe: `Videoauswahl.merken` in `_annehmen` weglassen →
der erste Fall rot.
"""
import re
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from core.dienste.videoauswahl import Videoauswahl
from core.models import AppSettings, BVHJob
from core.tests.unit._pruefablage import Pruefablage

#: Ein Radio der Videoliste mit seinem Pfad und allem, was im Tag steht.
RADIO = re.compile(r'<input type="radio" name="selected_video" value="([^"]*)"([^>]*)>')


class NachDemHochladen(TestCase):

    DREID = '/process/VideoToBVH/'

    def setUp(self):
        self.ordner = self.enterContext(Pruefablage.ordner('upload_'))
        self.enterContext(self.settings(MEDIA_ROOT=self.ordner))
        (Path(self.ordner) / 'uploads').mkdir()
        self.alt = self.video('alt.mp4')
        self.altjob = BVHJob.objects.create(
            name='alt.mp4', video_file='uploads/alt.mp4', pipeline='gem',
            status='complete')
        self.vorlieben({'selected_video_path': Videoauswahl.pfad_von(self.altjob),
                        'last_pipeline': 'smplx'})
        self.client = Client()

    def video(self, name):
        pfad = Path(self.ordner) / 'uploads' / name
        pfad.write_bytes(b'\x00' * 16)
        return pfad

    @staticmethod
    def vorlieben(werte=None):
        gespeichert = AppSettings.load()
        if werte is not None:
            gespeichert.ui_prefs = werte
            gespeichert.save(update_fields=['ui_prefs'])
        return AppSettings.objects.get(pk=1).ui_prefs or {}

    def radios(self):
        antwort = self.client.get(self.DREID)
        self.assertEqual(antwort.status_code, 200)
        text = antwort.content.decode('utf-8')
        return {pfad: 'checked' in rest for pfad, rest in RADIO.findall(text)}

    def hochladen(self, name='neu.mp4'):
        antwort = self.client.post(self.DREID, {
            'video': SimpleUploadedFile(name, b'\x00' * 16, content_type='video/mp4'),
            'pipeline': 'v4'})
        self.assertEqual(antwort.status_code, 302)
        return BVHJob.objects.get(name=name)

    def test_das_neue_video_ist_danach_das_gewaehlte(self):
        self.assertTrue(self.radios()[Videoauswahl.pfad_von(self.altjob)],
                        'Vorbedingung: das alte Video ist gewählt')
        neu = self.hochladen()
        radios = self.radios()
        self.assertTrue(radios[Videoauswahl.pfad_von(neu)], 'das neue Video hat keinen Haken')
        self.assertFalse(radios[Videoauswahl.pfad_von(self.altjob)], 'das alte hat ihn noch')
        self.assertEqual(sum(radios.values()), 1)

    def test_die_uebrigen_vorlieben_bleiben_stehen(self):
        self.hochladen()
        self.assertEqual(self.vorlieben().get('last_pipeline'), 'smplx')

    def test_der_upload_liegt_in_der_pruefablage(self):
        u"""Sonst schriebe diese Prüfung in `media/uploads/`."""
        neu = self.hochladen()
        self.assertTrue(Videoauswahl.pfad_von(neu).startswith(
            str(Path(self.ordner).resolve())))


class DerGemerktePfad(TestCase):
    u"""`merken` schreibt genau den Pfad, den die Liste führt."""

    def setUp(self):
        self.ordner = self.enterContext(Pruefablage.ordner('upload_'))
        self.enterContext(self.settings(MEDIA_ROOT=self.ordner))
        (Path(self.ordner) / 'uploads').mkdir()
        (Path(self.ordner) / 'uploads' / 'probe.mp4').write_bytes(b'\x00')
        self.job = BVHJob.objects.create(
            name='probe.mp4', video_file='uploads/probe.mp4', pipeline='gem')

    def test_der_pfad_ist_der_listeneintrag(self):
        Videoauswahl.merken(self.job)
        gemerkt = (AppSettings.load().ui_prefs or {})[Videoauswahl.SCHLUESSEL]
        self.assertIn(gemerkt, [e['path'] for e in Videoauswahl.sammeln([self.job])])
        self.assertTrue(Path(gemerkt).is_absolute())

    def test_merken_ergaenzt_und_loescht_nichts(self):
        gespeichert = AppSettings.load()
        gespeichert.ui_prefs = {'panel_breite': 320}
        gespeichert.save(update_fields=['ui_prefs'])
        Videoauswahl.merken(self.job)
        vorlieben = AppSettings.load().ui_prefs
        self.assertEqual(vorlieben['panel_breite'], 320)
        self.assertEqual(vorlieben[Videoauswahl.SCHLUESSEL], Videoauswahl.pfad_von(self.job))

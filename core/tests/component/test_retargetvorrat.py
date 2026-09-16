# -*- coding: utf-8 -*-
u"""Retargetvorrat: der Retarget liegt neben jedem BVH, bevor der Auftrag fertig ist.

WARUM (Edgar, 16.09.2026: „keine Animation zu sehen … erst jetzt, nach ca.
1 Minute" → „Mach retarget neben BVH"): Der erste Abruf eines Ergebnisses
rechnete den Retarget (43 s bei 7.538 Bildern) — je BVH und je Ort (Auftrags-
ordner, Bibliothekskopie). Jetzt rechnet ihn der Auftragsprozess vor „complete":

1. `anlegen` rechnet für Körper, Gesicht, Hände und weitere Personen je eine
   Ablage neben dem BVH (`Retargetdaten.ablage`) und legt sie auch neben die
   Bibliothekskopie; `melden` nennt dabei die Datei.
2. Eine scheiternde Rechnung lässt den Auftrag fertig werden (Warnung im Log,
   der erste Abruf rechnet dann wie früher).
3. `Auftragsabschluss.fertig_mit_vorrat` rechnet VOR „complete" und setzt die
   Meldung; `auftragslauf.py` geht nur noch über diesen Weg.

Sabotage-Gegenprobe: in `Retargetvorrat.anlegen` das `try/except` entfernen
→ Fall 2 rot (die Ausnahme fliegt).
"""
import json
import os
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings

from core.dienste.auftragsabschluss import Auftragsabschluss
from core.dienste.retargetvorrat import Retargetvorrat
from core.models import BVHJob
from core.tests.unit._pruefablage import Pruefablage

BVH = ('HIERARCHY\nROOT Hips\n{\n OFFSET 0 0 0\n'
       ' CHANNELS 3 Zrotation Xrotation Yrotation\n End Site\n {\n'
       '  OFFSET 0 1 0\n }\n}\nMOTION\nFrames: 2\nFrame Time: 0.04\n'
       '0 0 0\n0 0 0\n')


class Ergebnisattrappe:
    def __init__(self, bilder=2):
        self.bilder = bilder

    def als_dict(self):
        return {'frame_count': self.bilder, 'duration': 0.08, 'times': [0, 0.04],
                'tracks': [], 'position_track': None, 'mapped_bones': []}

    def get(self, name, ersatz=None):
        return self.als_dict().get(name, ersatz)


class RetargetvorratTest(TestCase):

    def setUp(self):
        ablage = Pruefablage.ordner('vorrat_')
        self.ordner = Path(ablage.__enter__())
        self.addCleanup(ablage.__exit__, None, None, None)
        self.bibliothek = self.ordner / 'A_Results'
        self.bibliothek.mkdir()
        self.einstellung = override_settings(BVH_RESULTS_DIR=str(self.bibliothek))
        self.einstellung.enable()
        self.addCleanup(self.einstellung.disable)

    def _bvh(self, name):
        pfad = self.ordner / name
        pfad.write_text(BVH, encoding='utf-8')
        return str(pfad)

    def _auftrag(self):
        job = BVHJob.objects.create(name='tanz.mp4', pipeline='gem',
                                    status='processing')
        job.bvh_file = self._bvh('tanz_gem.bvh')
        job.bvh_file_face = self._bvh('tanz_face.bvh')
        job.bvh_file_personen = [self._bvh('tanz_gem_p2.bvh')]
        job.save()
        for kennung in ('gem', 'gem_face', 'gem_p2'):
            (self.bibliothek / ('tanz_%s.bvh' % kennung)).write_text(BVH,
                                                                     encoding='utf-8')
        return job

    def test_ablage_neben_bvh_und_bibliothekskopie(self):
        job = self._auftrag()
        meldungen = []
        with mock.patch('core.dienste.retargetdaten.Retargetdaten._rechnen',
                        return_value=Ergebnisattrappe(7)):
            ablagen = Retargetvorrat.anlegen(job, meldungen.append)
        self.assertEqual(len(ablagen), 6)
        for pfad in ablagen:
            self.assertTrue(pfad.is_file(), pfad)
            self.assertIn('_retarget_', pfad.name)
            with open(pfad, encoding='utf-8') as datei:
                self.assertEqual(json.load(datei)['frame_count'], 7)
        namen = sorted(p.parent.name + '/' + p.name.split('_retarget_')[0]
                       for p in ablagen)
        eigene = self.ordner.name
        self.assertEqual(namen, sorted(['A_Results/tanz_gem', 'A_Results/tanz_gem_face',
                                        'A_Results/tanz_gem_p2', eigene + '/tanz_gem',
                                        eigene + '/tanz_face',
                                        eigene + '/tanz_gem_p2']))
        self.assertEqual(meldungen, ['Bewegung wird umgesetzt (tanz_gem.bvh) …',
                                     'Bewegung wird umgesetzt (tanz_face.bvh) …',
                                     'Bewegung wird umgesetzt (tanz_gem_p2.bvh) …'])
        # Die Hashes stimmen: Auftrags-BVH und Kopie tragen denselben Schlüssel.
        schluessel = {p.name.split('_retarget_')[1] for p in ablagen}
        self.assertEqual(len(schluessel), 1)

    def test_scheitern_der_rechnung_laesst_den_auftrag_fertig_werden(self):
        job = self._auftrag()
        with mock.patch('core.dienste.retargetdaten.Retargetdaten._rechnen',
                        side_effect=RuntimeError('kaputt')):
            Auftragsabschluss.fertig_mit_vorrat(job, 'Done')
        job.refresh_from_db()
        self.assertEqual((job.status, job.progress, job.progress_detail),
                         ('complete', 100, 'Done'))
        self.assertFalse(list(self.ordner.glob('*_retarget_*')))

    def test_fertig_mit_vorrat_rechnet_vor_complete(self):
        job = self._auftrag()
        zustaende = []

        def rechnen(_self):
            zustaende.append(BVHJob.objects.get(pk=job.pk).status)
            return Ergebnisattrappe()
        with mock.patch('core.dienste.retargetdaten.Retargetdaten._rechnen', rechnen):
            Auftragsabschluss.fertig_mit_vorrat(job)
        self.assertEqual(zustaende, ['processing'] * 3)
        self.assertEqual(BVHJob.objects.get(pk=job.pk).status, 'complete')
        lauf = (settings.BASE_DIR / 'core' / 'pipelines' / 'auftragslauf.py'
                ).read_text(encoding='utf-8')
        self.assertIn('Auftragsabschluss.fertig_mit_vorrat(self.job, meldung)', lauf)
        self.assertNotIn("self.job.status = 'complete'", lauf)
        self.assertEqual(os.path.basename(job.bvh_file), 'tanz_gem.bvh')

# -*- coding: utf-8 -*-
u"""Process Videos -> Effekte, Pipeline „HumanBody-Figur (DEF-Skelett)".

WARUM (Edgar, 12.09.2026: „ich brauche was, wo ich auch mein HumanBody
Modell mit meinem DEF skeleton nutzen kann … mach mir einen Browser wo ich
meine Animationen waehlen kann und ein Modell auswahl dialog"): Neben der
Blender-Pipeline gibt es die zweite mit gespeichertem Modell; die Seite
traegt Modelle und Auftrags-BVHs als JSON fuer die Dialoge, der Start
nimmt ein Modell und eine Bibliotheksadresse an, der Befehl ruft python14
mit `figurfilm.py`. Der Film selbst (pyrender, 15 s) laeuft hier nicht —
`Effektlauf.starten` ist eine Attrappe.
"""
import json
import os
import sys
from unittest import mock

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from core.dienste.modellvorlagen import Modellvorlagen
from core.effekte.effektbefehl import Effektbefehl
from core.effekte.effektlauf import Effektlauf
from core.effekte.effektpruefung import Effektpruefung
from core.effekte.effektquellen import Effektquellen
from core.models import BVHJob, Effektauftrag
from core.tests.unit._pruefablage import Pruefablage
from effekte.figurparameter import Figurparameter

#: Drei SMPL-Gelenke reichen, damit `Skeleton.detect_format` AIST erkennt.
BVH = ('HIERARCHY\nROOT Pelvis\n{\n\tOFFSET 0 0 0\n'
       '\tCHANNELS 6 Xposition Yposition Zposition Zrotation Yrotation Xrotation\n'
       '\tJOINT Left_hip\n\t{\n\t\tOFFSET 0 0 0\n\t\tCHANNELS 3 Zrotation Yrotation Xrotation\n'
       '\t\tEnd Site\n\t\t{\n\t\t\tOFFSET 0 1 0\n\t\t}\n\t}\n'
       '\tJOINT Spine1\n\t{\n\t\tOFFSET 0 0 0\n\t\tCHANNELS 3 Zrotation Yrotation Xrotation\n'
       '\t\tEnd Site\n\t\t{\n\t\t\tOFFSET 0 1 0\n\t\t}\n\t}\n}\n'
       'MOTION\nFrames: 2\nFrame Time: 0.04\n'
       '0 0 0 0 0 0 0 0 0 0 0 0\n0 0 0 0 0 0 0 0 0 0 0 0\n')


class EffekteFigur(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._ablage = Pruefablage.ordner('effekte_figur_')
        cls.ordner = cls._ablage.__enter__()
        cls.modelle = os.path.join(cls.ordner, 'models')
        os.makedirs(cls.modelle)
        with open(os.path.join(cls.modelle, 'Probe.json'), 'w', encoding='utf-8') as datei:
            json.dump({'name': 'Probe', 'body_type': 'Female_Caucasian',
                       'morphs': {'Waist_Size': -0.2}, 'garmentcode': [],
                       'hair_style': {'name': 'Ballerina',
                                      'url': '/api/character/hairstyle/ballerina/'}}, datei)
        with open(os.path.join(cls.modelle, 'Buehne.scene.json'), 'w') as datei:
            datei.write('{}')
        cls.bvh = os.path.join(cls.ordner, 'aist.bvh')
        with open(cls.bvh, 'w', encoding='utf-8') as datei:
            datei.write(BVH)
        cls.unbekannt = os.path.join(cls.ordner, 'unbekannt.bvh')
        with open(cls.unbekannt, 'w', encoding='utf-8') as datei:
            datei.write(BVH.replace('Pelvis', 'Wurzel').replace('Left_hip', 'Ast')
                        .replace('Spine1', 'Zweig'))

    @classmethod
    def tearDownClass(cls):
        cls._ablage.__exit__(None, None, None)
        super().tearDownClass()

    def setUp(self):
        self.client = Client(HTTP_HOST='127.0.0.1')
        self._modelle = override_settings(HUMANBODY_MODELS_DIR=self.modelle)
        self._modelle.enable()
        self.addCleanup(self._modelle.disable)
        BVHJob.objects.create(name='aist.mp4', pipeline='gem', status='complete',
                              bvh_file=self.bvh, video_file='uploads/aist.mp4')

    def nutzlast(self, **extra):
        daten = {'pipeline': 'figur_def', 'bvh': self.bvh, 'modell': 'Probe',
                 'ausgabe': os.path.join(self.ordner, 'aus', 'probe.mp4'),
                 'parameter': {'bilder': 20, 'fps': 24, 'physik': 5.0}}
        daten.update(extra)
        return daten

    def starten(self, **extra):
        with mock.patch.object(Effektlauf, 'starten') as start:
            antwort = self.client.post(reverse('effekte_start'),
                                       data=json.dumps(self.nutzlast(**extra)),
                                       content_type='application/json')
        return antwort, start

    # --------------------------------------------------------------- Seite

    def test_seite_traegt_modelle_auftraege_und_die_figurfelder(self):
        antwort = self.client.get(reverse('effekte'))
        self.assertEqual(antwort.status_code, 200)
        text = antwort.content.decode('utf-8')
        self.assertIn('id="effektModelle"', text)
        self.assertIn('id="effektAuftraegeBvh"', text)
        self.assertIn('"Probe"', text)
        self.assertNotIn('Buehne', text)                  # Szenen sind keine Modelle
        for f in Figurparameter.karte():
            self.assertIn('id="figur_%s"' % f['name'], text)
        self.assertIn('data-pipeline="figur_def"', text)
        self.assertIn('id="effektAnimationKnopf"', text)
        self.assertIn('id="effektModellKnopf"', text)
        self.assertIn('data-video-ausgabe=', text)

    def test_quellen_nennen_modell_und_format(self):
        modelle = {m['name']: m for m in Effektquellen.modelle()}
        self.assertEqual(modelle['Probe']['frisur'], 'Ballerina')
        self.assertEqual(modelle['Probe']['morphs'], 1)
        self.assertNotIn('Buehne', modelle)
        eintrag = {e['name']: e for e in Effektquellen.bvh_dateien()}['aist.bvh']
        self.assertEqual(eintrag['format'], 'AIST')
        antwort = self.client.get(reverse('effekte_quellen')).json()
        self.assertEqual([m['name'] for m in antwort['modelle']], ['Probe'])
        self.assertEqual(antwort['auftraege'][0]['format'], 'AIST')

    # --------------------------------------------------------------- Start

    def test_start_mit_modell_legt_auftrag_der_figurpipeline_an(self):
        antwort, start = self.starten()
        self.assertEqual(antwort.status_code, 200, antwort.content)
        auftrag = Effektauftrag.objects.get()
        start.assert_called_once_with(auftrag)
        self.assertEqual((auftrag.pipeline, auftrag.modell, auftrag.kleid),
                         ('figur_def', 'Probe', ''))
        self.assertTrue(auftrag.mit_modell)
        self.assertEqual(auftrag.parameter['physik'], 5.0)

    def test_bibliotheksadresse_wird_zur_datei(self):
        wurzel = os.path.dirname(str(settings.HUMANBODY_BVH_DIR))
        kategorie = os.listdir(wurzel)[0] if os.path.isdir(wurzel) else ''
        namen = [d[:-4] for d in os.listdir(os.path.join(wurzel, kategorie))
                 if d.endswith('.bvh')] if kategorie else []
        if not namen:
            self.skipTest('Keine BVH-Bibliothek vorhanden')
        pfad = Effektpruefung.bvh_pfad('/api/character/bvh/%s/%s/' % (kategorie, namen[0]))
        self.assertEqual(os.path.basename(pfad), namen[0] + '.bvh')
        with self.assertRaises(ValueError):
            Effektpruefung.bvh_pfad('/api/character/bvh/%s/gibt_es_nicht_xyz/' % kategorie)

    def test_start_weist_unbekanntes_format_fehlendes_modell_und_szene_ab(self):
        for extra, erwartet in ((dict(bvh=self.unbekannt), 'Format nicht erkannt'),
                                (dict(modell='Nirgends'), 'Modell fehlt'),
                                (dict(modell='Buehne'), 'Modell fehlt'),
                                (dict(modell=''), 'Modell fehlt'),
                                (dict(parameter={'unterteilung': 2}), 'Parameter'),
                                (dict(pipeline='quatsch'), 'Unbekannte Pipeline')):
            with self.subTest(**extra):
                antwort, start = self.starten(**extra)
                self.assertEqual(antwort.status_code, 400)
                self.assertIn(erwartet, antwort.json()['error'])
                start.assert_not_called()
        self.assertEqual(Effektauftrag.objects.count(), 0)

    def test_zustand_nennt_pipeline_und_modell(self):
        auftrag = Effektauftrag.objects.create(
            name='f', pipeline='figur_def', modell='Probe', bvh_pfad=self.bvh,
            ausgabe='x.mp4', status='running')
        zustand = self.client.get(reverse('effekte_status', args=[auftrag.id])).json()
        self.assertEqual((zustand['pipeline'], zustand['modell']), ('figur_def', 'Probe'))

    # -------------------------------------------------------------- Befehl

    @override_settings(EFFEKTE_FIGUR_SKRIPT='figurfilm.py')
    def test_befehl_ruft_python14_mit_dem_figurskript_und_jedem_feld(self):
        auftrag = Effektauftrag(pipeline='figur_def', modell='Probe', bvh_pfad='a.bvh',
                                ausgabe='o.mp4', parameter={'bilder': 20, 'physik': 7.5})
        befehl = Effektbefehl(auftrag).bauen()
        self.assertEqual(befehl[:2], [sys.executable, 'figurfilm.py'])
        self.assertNotIn('--', befehl)
        self.assertEqual(befehl[befehl.index('--modell') + 1],
                         str(Modellvorlagen.pfad('Probe')))
        self.assertEqual(befehl[befehl.index('--physik') + 1], '7.5')
        for name in Figurparameter.namen():
            self.assertIn('--' + name, befehl)
        self.assertEqual(Effektbefehl(auftrag).bilder(), 20)
        auftrag.modell = 'Nirgends'
        with self.assertRaises(ValueError):
            Effektbefehl(auftrag).bauen()

    def test_das_figurskript_liegt_da_und_ist_bpy_frei(self):
        self.assertTrue(os.path.isfile(settings.EFFEKTE_FIGUR_SKRIPT))
        with open(settings.EFFEKTE_FIGUR_SKRIPT, encoding='utf-8') as datei:
            self.assertNotIn('import bpy', datei.read())

# -*- coding: utf-8 -*-
"""Freisteller-Ablauf über Dienst und Endpunkte (21.09.2026, Edgar: „schreibe dir tests, diese
buttons auf den Seiten funktionieren nicht, das Vorschaubild ist weg usw").

Was heute kaputt war und hier festgenagelt wird:
1. `bilder_sichern` warf das gerade gesetzte `freisteller`-Feld weg (es steht in NUTZERFELDERN)
   → kein `stand`, dieselbe Bildadresse, Chrome zeigte das alte Bild aus seinem Speicher.
2. Speichern löschte GVHMR/Schätzung des Bildes („kein SMPL??") — sie bleiben jetzt.
3. Jeder Eintrag im Zustand und in der Freisteller-Antwort trägt `bildstand` (mtime des
   Ausschnitts) — die Adresse wechselt auch nach Zurücksetzen.
4. Nach dem Speichern sind die Regler neutral (Striche weg), die Vorschau des Endpunkts ist
   ein PNG, die Schwelle lässt den sicheren Kern der Maske bei jedem Wert bei 1.

Runner (rembg, Hautton) sind Attrappen; die Maske kommt als Datei in die Ablage."""
import io
import json
import shutil
import tempfile
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import Client, TestCase, override_settings
from PIL import Image

from core.daten.bildmodellablage import Bildmodellablage
from core.dienste.bildmodellfreisteller import Bildmodellfreisteller
from core.models import Bildmodellauftrag

DATEI = 'bild_a.jpg'


def _bild(pfad, farbe=(120, 120, 120), person=(220, 170, 140)):
    """80×60, grauer Grund, Person als Rechteck (Zeilen 10–50, Spalten 30–50)."""
    rgb = np.zeros((60, 80, 3), dtype=np.uint8)
    rgb[:] = farbe
    rgb[10:50, 30:50] = person
    pfad.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgb, 'RGB').save(str(pfad), quality=95)


def _maske_schreiben(pfad):
    """Weiche Maske: Person 250 (nicht 255 — wie rembg), Rand 128, Grund 0."""
    m = np.zeros((60, 80), dtype=np.uint8)
    m[10:50, 30:50] = 250
    m[9, 30:50] = 128
    Image.fromarray(m, 'L').save(str(pfad))
    return {'modell': 'u2net_human_seg', 'anteil': 0.17, 'dauer_s': 0.1}


class FreistellerAblaufTest(TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(dir=str(Path(__file__).parent)))
        self.client = Client(HTTP_HOST='127.0.0.1')
        self.settings_ = override_settings(OBJECTS_ROOT=self.tmp)
        self.settings_.enable()
        self.job = Bildmodellauftrag.objects.create(
            kennung='2026.01.01.00.00.00', name='ZZ',
            bilder=[{'datei': DATEI, 'kategorie': 'koerper', 'gvhmr': {'ok': True},
                     'schaetzung': {'betas': [0.1]}}])
        self.ablage = Bildmodellablage(self.job.kennung)
        _bild(self.ablage.zuschnitt() / DATEI)
        self.dienst = Bildmodellfreisteller(self.job, self.ablage)
        # Runner-Attrappe: `maske` schreibt die Maskendatei, `hautton` misst einen Ton.
        self._runner = mock.patch.object(Bildmodellfreisteller, '_runner', side_effect=self._runner_attrappe)
        self._runner.start()

    def tearDown(self):
        self._runner.stop()
        self.settings_.disable()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _runner_attrappe(self, befehl, *argumente):
        if befehl == 'maske':
            return _maske_schreiben(Path(argumente[1]))
        if befehl == 'hautton':
            return {'textur': {'ton': [0.86, 0.67, 0.55], 'tauglich': True}}
        return {'error': 'unbekannt: %s' % befehl}

    # ------------------------------------------------------------ Dienst

    def test_speichern_behaelt_feld_und_schaetzungen(self):
        regler = dict(Bildmodellfreisteller.VORGABE,
                      striche=[{'art': 'draussen', 'breite': 0.01, 'punkte': [[0.1, 0.1], [0.2, 0.2]]}])
        eintrag = self.dienst.speichern(DATEI, regler)
        self.assertIn('stand', eintrag['freisteller'])
        self.assertEqual(eintrag['freisteller']['regler']['striche'], [])           # neutral
        self.assertEqual(eintrag['freisteller']['angewandt']['striche'], regler['striche'])
        self.assertTrue(eintrag.get('gvhmr'), 'GVHMR bleibt beim Freistellen')
        self.assertTrue(eintrag.get('schaetzung'))
        self.job.refresh_from_db()
        b = self.job.bild(DATEI)
        self.assertIn('stand', (b.get('freisteller') or {}), 'freisteller überlebt bilder_sichern')
        self.assertTrue(b.get('gvhmr'))
        self.assertTrue((self.ablage.zuschnitt() / 'vorher' / DATEI).is_file())
        self.assertTrue(self.dienst.maskenpfad(DATEI).is_file(), 'fertige Maske liegt als DIE Maske')
        aus = np.asarray(Image.open(self.ablage.zuschnitt() / DATEI).convert('RGB'))
        self.assertGreater(aus[5, 5].min(), 240, 'Grund ist weiß')
        self.assertLess(aus[30, 40].mean(), 200, 'Person bleibt')

    def test_zuruecksetzen_holt_original_und_behaelt_gvhmr(self):
        self.dienst.speichern(DATEI, dict(Bildmodellfreisteller.VORGABE))
        eintrag = self.dienst.zuruecksetzen(DATEI)
        self.assertNotIn('freisteller', eintrag)
        self.assertTrue(eintrag.get('gvhmr'))
        aus = np.asarray(Image.open(self.ablage.zuschnitt() / DATEI).convert('RGB'))
        self.assertLess(abs(int(aus[5, 5, 0]) - 120), 6, 'grauer Grund ist zurück')
        self.job.refresh_from_db()
        self.assertNotIn('freisteller', self.job.bild(DATEI))

    def test_schwelle_laesst_kern_bei_eins(self):
        maske = self.dienst.maske(DATEI)
        for schwelle in (0, 50, 90, 100):
            a = self.dienst.alpha(maske, self.dienst.regler_pruefen({'schwelle': schwelle, 'weich': 0}))
            self.assertAlmostEqual(float(a[30, 40]), 1.0, places=3, msg='Schwelle %d' % schwelle)
            self.assertAlmostEqual(float(a[5, 5]), 0.0, places=3)

    def test_bilder_sichern_behalten(self):
        self.job.bild(DATEI)['freisteller'] = {'stand': 'x'}
        self.job.bilder_sichern()
        self.job.refresh_from_db()
        self.assertNotIn('freisteller', self.job.bild(DATEI), 'ohne behalten: frisch aus der DB')
        self.job.bild(DATEI)['freisteller'] = {'stand': 'x'}
        self.job.bilder_sichern(behalten=('freisteller',))
        self.job.refresh_from_db()
        self.assertEqual(self.job.bild(DATEI)['freisteller'], {'stand': 'x'})

    # --------------------------------------------------------- Endpunkte

    def test_grundlage_fuer_die_browser_vorschau(self):
        """Bild + Maske (+ Abstandskarte bei Positivliste) in Vorschaugröße als Data-URLs."""
        basis = '/api/bildmodell/%s/freisteller/%s/grundlage/' % (self.job.id, DATEI)
        antwort = self.client.post(basis, data=json.dumps({'schwelle': 50}), content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content[:200])
        g = antwort.json()
        self.assertEqual((g['breite'], g['hoehe']), (80, 60))
        self.assertEqual(g['f'], 1.0)
        self.assertTrue(g['bild'].startswith('data:image/jpeg;base64,'))
        self.assertTrue(g['maske'].startswith('data:image/png;base64,'))
        self.assertIsNone(g['abstand'])
        self.assertEqual(g['sicher'], Bildmodellfreisteller.SICHER)
        antwort = self.client.post(basis, data=json.dumps({'positiv': True, 'toleranz': 20}),
                                   content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content[:200])
        g = antwort.json()
        self.assertTrue(g['abstand'].startswith('data:image/png;base64,'))
        self.assertEqual(g['abstand_mal'], 4.0)
        self.assertTrue(g['kern'].startswith('data:image/png;base64,'), 'der Kern für den Browser')

    def test_positivliste_nur_ausserhalb_der_figur(self):
        """Ein hautfarbener Arm neben der Netzmaske kommt dazu, ein Fleck weit weg nicht; im Kern
        (erodiertes Innere) bleibt alles, auch ein dunkler Haar-Block (Edgar: „im Moment machst du
        auch Pixel innerhalb des Kopfes weg")."""
        pfad = self.ablage.zuschnitt() / DATEI
        rgb = np.asarray(Image.open(pfad).convert('RGB')).copy()
        rgb[12:20, 32:48] = (50, 30, 20)          # Haar im Kopf (in der Maske)
        rgb[30:36, 50:64] = (220, 170, 140)       # Arm: hängt an der Maske (Spalten 30–50)
        rgb[52:58, 2:14] = (220, 170, 140)        # Fleck weit weg
        Image.fromarray(rgb, 'RGB').save(str(pfad), quality=100)
        maske = self.dienst.maske(DATEI)
        regler = self.dienst.regler_pruefen({'positiv': True, 'toleranz': 20, 'weich': 0})
        a = self.dienst.alpha(maske, regler, rgb)
        self.assertAlmostEqual(float(a[16, 40]), 1.0, places=2, msg='Haar im Kopf bleibt')
        self.assertAlmostEqual(float(a[33, 60]), 1.0, places=2, msg='Arm kommt dazu')
        self.assertAlmostEqual(float(a[55, 8]), 0.0, places=2, msg='Fleck ohne Anschluss bleibt Grund')
        self.assertAlmostEqual(float(a[5, 5]), 0.0, places=2)
        ohne = self.dienst.alpha(maske, self.dienst.regler_pruefen({'weich': 0}), rgb)
        self.assertAlmostEqual(float(ohne[33, 60]), 0.0, places=2, msg='ohne Positivliste kein Arm')
        self.assertTrue(self.dienst.regler_pruefen({'modell': 'hautton'})['positiv'], 'alte Einträge')

    def test_endpunkte_vorschau_speichern_zustand(self):
        basis = '/api/bildmodell/%s/' % self.job.id
        antwort = self.client.post(basis + 'freisteller/%s/vorschau/' % DATEI,
                                   data=json.dumps({'schwelle': 50}), content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content[:200])
        self.assertEqual(antwort['Content-Type'], 'image/png')
        png = Image.open(io.BytesIO(antwort.content))
        self.assertEqual(png.size, (80, 60))
        antwort = self.client.post(basis + 'freisteller/%s/speichern/' % DATEI,
                                   data=json.dumps({'schwelle': 50}), content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content[:200])
        bild = antwort.json()['bild']
        self.assertIn('stand', bild['freisteller'])
        self.assertIsInstance(bild.get('bildstand'), int)
        zustand = self.client.get(basis + 'zustand/').json()
        b = zustand['bilder'][0]
        self.assertIn('stand', b['freisteller'])
        self.assertIsInstance(b['bildstand'], int)
        self.assertTrue(b.get('gvhmr'))
        # Zurücksetzen: Feld weg, bildstand da — die Bildadresse bleibt eindeutig.
        antwort = self.client.post(basis + 'freisteller/%s/zuruecksetzen/' % DATEI,
                                   data='{}', content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content[:200])
        self.assertNotIn('freisteller', antwort.json()['bild'])
        self.assertIsInstance(antwort.json()['bild'].get('bildstand'), int)

# -*- coding: utf-8 -*-
u"""Genesis 9 gegen die installierte Daz-Bibliothek (18.09.2026 abends, Edgar:
„mach Lipsync", „Mach Daz' JCMs", „Gibt es Animationen dazu?"):

1. Der JCM-Graph aus `Base Correctives` + `Base Flexions`: 157 Kanaele, 117
   Morphe, 52 Eingabeknochen; `l_thigh` 35° stellt `body_cbs_thigh_x35p_l`
   auf 1, −115°/90° die Zwei-Achsen-Korrektur.
2. Die Felder-Endpunkte: 117 JCM-Felder auf Stufe 1 (Mund-Anhang dabei), 17
   Visemes mit Kieferdrehung (`Vis AA`: `lowerjaw` 5,2°), 138 Achsen.
3. Daz' Bewegungsszenen: sieben im Katalog, als BVH mit 57 Knochen
   (Gesicht, Twist, Mittelhand draussen), Format `GENESIS9`, Retarget auf
   Genesis 9 mit 54 Spuren.
4. Lippensynchronisation: eine Sekunde Rauschen -> Mundformen (nur mit
   Rhubarb).
5. Kleidung und Schalter (18.09.2026 nachts, „mach beide"): die Stueckfelder
   der Angie Jeans (sieben Teile, `thigh_x35p_l` auf der Hose), die zwei
   Schalter im Reglerplan, Fabrice stellt die Beugungen per Formel auf 1.

LongRunner: JCM-Felder 7 s beim ersten Mal, Retarget, Rhubarb. Ohne
Bibliothek uebersprungen.

Sabotage-Gegenproben: `G9zuordnung.ausnahmen` ohne den GENESIS9-Zweig ->
Fall 3 rot (Median 0,28 -> 15° p90 in der Messung, hier: Ausnahmen leer);
`G9bewegungbvh.retargetknochen` ohne `neck2` -> Fall 3 rot (Kopf haengt an
`neck1`, JOINT-Zahl 55).
"""
import json
import os
import struct
import tempfile
import unittest
from pathlib import Path

from django.conf import settings
from django.test import Client, SimpleTestCase

from Genesis9.bewegung import G9bewegungen
from Genesis9.bewegungbvh import G9bewegungbvh
from Genesis9.gelenkkorrekturen import G9gelenkkorrekturen
from Genesis9.pfade import G9pfade
from core.dienste.lippensync import Lippensync
from humanbody_core.skeleton import Skeleton
from humanbody_core.skeleton.formats.g9_zuordnung import G9zuordnung


def bibliothek_da():
    return G9pfade.vorhanden() and (G9pfade.bibliothek() / 'Scenes').is_dir()


@unittest.skipUnless(bibliothek_da(), 'Daz-Bibliothek mit Genesis 9 fehlt')
class GelenkeLipsyncTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.client = Client()

    # ------------------------------------------------------------------ JCMs

    def test_1_jcm_graph(self):
        g = G9gelenkkorrekturen.graph()
        # 157/117/52 waren die Zahlen ohne charaktereigene Correctives; seit
        # 24.09.2026 (Damira „Naturally Bending") kommen die _cbs_*-Dateien
        # der gekauften Charaktere (Damira, Ursula, Kin, Olesia) dazu — die
        # Summe haengt am Bibliotheksstand, wie hier ueblich (`tests.md`).
        self.assertEqual((len(g['kanaele']), len(g['morphe']), len(g['knochen'])),
                         (218, 164, 54))
        self.assertEqual(G9gelenkkorrekturen.werte({'l_thigh': {'rotation/x': 35}}),
                         {'body_cbs_thigh_x35p_l': 1.0})
        w = G9gelenkkorrekturen.werte(
            {'l_thigh': {'rotation/x': -115, 'rotation/z': 90}})
        self.assertAlmostEqual(w['body_cbs_thigh_x115n_z90p_l'], 1.0, places=5)
        self.assertAlmostEqual(w['body_cbs_thigh_x90n_l'], 1.0, places=5)
        # Die Beugungen haengen an `FlexionAutoStrength` (Vorgabe 0): still.
        w = G9gelenkkorrekturen.werte({'l_forearm': {'rotation/y': -110}})
        self.assertEqual(sorted(w),
                         ['body_cbs_forearm_y135n_l', 'body_cbs_forearm_y75n_l'])
        self.assertAlmostEqual(w['body_cbs_forearm_y135n_l'], 35 / 60, places=6)
        self.assertAlmostEqual(w['body_cbs_forearm_y75n_l'], 1.0, places=6)

    def test_2_felder_endpunkte(self):
        r = self.client.get('/api/character/genesis9-figur/felder/gelenke/?stufen=1')
        self.assertEqual(r.status_code, 200, r.content[:300])
        d = r.json()
        self.assertEqual(len(d['felder']['koerper']), 164)
        self.assertIn('mund', d['felder']['anhaenge'])
        self.assertEqual(len(d['achsen']), 138)
        self.assertEqual(d['achsen']['l_thigh']['r'], 'YZX')
        self.assertGreater(
            d['felder']['koerper']['body_cbs_thigh_x35p_l']['anzahl'], 1000)
        r = self.client.get('/api/character/genesis9-figur/felder/visemes/?stufen=1')
        self.assertEqual(r.status_code, 200, r.content[:300])
        d = r.json()
        self.assertEqual(len(d['visemes']), 17)
        self.assertEqual(len(d['felder']['koerper']), 17)
        self.assertEqual(len(d['felder']['anhaenge']['mund']), 17)
        kiefer = d['felder']['knochen']['facs_ctrl_vAA']['lowerjaw']
        self.assertAlmostEqual(kiefer['rotation/x'], 5.18, delta=0.05)
        self.assertNotIn('facs_ctrl_vM', d['felder']['knochen'])

    # ----------------------------------------------------------- Bewegungen

    def test_3_daz_bewegungen_als_bvh(self):
        katalog = G9bewegungen.katalog()
        self.assertEqual(sorted(katalog), ['dance', 'idle', 'jump', 'punch', 'slide',
                                           'swing', 'walking'])
        self.assertEqual(katalog['dance']['bilder'], 489)
        self.assertEqual(katalog['swing']['bilder'], 57)
        b = G9bewegungen.lesen(katalog['walking']['datei'])
        self.assertEqual(b['bilder'], 36)
        text = G9bewegungbvh.text(b)
        # 56 der Zuordnung + Kiefer + zehn Zehen (18.09.2026 abends)
        self.assertEqual(text.count('JOINT '), 67)
        self.assertIn('JOINT neck2', text)
        self.assertIn('JOINT lowerjaw', text)
        self.assertIn('JOINT r_pinkytoe1', text)
        self.assertNotIn('l_eye', text)
        self.assertNotIn('twist', text)
        self.assertNotIn('bigtoe2', text)
        namen = [z.split()[1] for z in text.split('\n')
                 if z.strip().startswith(('ROOT', 'JOINT'))]
        bauart = Skeleton.detect_format(namen)
        self.assertEqual(bauart.FORMAT, 'GENESIS9')
        self.assertEqual(len(G9zuordnung.ausnahmen(bauart)), 65)
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as ordner:
            geschrieben = G9bewegungen.bereitstellen(Path(ordner))
            self.assertEqual(len(geschrieben), 7)
            self.assertEqual(G9bewegungen.bereitstellen(Path(ordner)), [])
            marke = Path(ordner) / 'fassung.txt'
            self.assertEqual(marke.read_text(encoding='utf-8'),
                             str(G9bewegungen.BVH_FASSUNG))
            marke.write_text('1', encoding='utf-8')         # alte Fassung: alles neu
            self.assertEqual(len(G9bewegungen.bereitstellen(Path(ordner))), 7)
        wurzel = Path(settings.HUMANBODY_BVH_DIR).parent / G9bewegungen.ORDNER
        if (wurzel / 'Walking.bvh').is_file():
            r = self.client.get('/api/retarget/', {
                'category': 'Daz', 'name': 'Walking', 'target': 'genesis9',
                'figur': 'basis'})
            self.assertEqual(r.status_code, 200, r.content[:300])
            spuren = r.json()['tracks']
            self.assertEqual(len(spuren), 65)
            self.assertIn('lowerjaw', spuren)
            self.assertIn('l_bigtoe1', spuren)

    # ------------------------------------------------------------ Kleidung

    def test_5_stueckfelder_und_schalter(self):
        r = self.client.get(
            '/api/character/genesis9-figur/garderobe/angie_jeans/felder/gelenke/'
            '?stufen=1')
        self.assertEqual(r.status_code, 200, r.content[:300])
        d = r.json()
        self.assertEqual(len(d['teile']), 7)
        self.assertGreater(d['teile'][0]['body_cbs_thigh_x35p_l']['anzahl'], 1000)
        r = self.client.get(
            '/api/character/genesis9-figur/garderobe/kein_stueck/felder/gelenke/')
        self.assertEqual(r.status_code, 404)
        # Kaefigfelder fuer den Stoff-Worker (18.09.2026 abends): Daz-Punkte,
        # ohne Matrix — jede Nummer unter der Punktzahl des Teils.
        r = self.client.get(
            '/api/character/genesis9-figur/garderobe/angie_jeans/felder/gelenke/'
            '?kaefig=1')
        self.assertEqual(r.status_code, 200, r.content[:300])
        k = r.json()
        self.assertIsNone(k['stufen'])
        self.assertEqual(len(k['teile']), 7)
        from Genesis9.garderobe import G9garderobe
        folger = [f for f, lage in G9garderobe.teile('angie_jeans')]
        feld = k['teile'][0]['body_cbs_thigh_x35p_l']
        self.assertGreater(feld['anzahl'], 200)
        fein = d['teile'][0]['body_cbs_thigh_x35p_l']['anzahl']
        self.assertLess(feld['anzahl'], fein)
        import base64
        import numpy as np
        nummern = np.frombuffer(base64.b64decode(feld['n']), dtype=np.uint32)
        self.assertLess(int(nummern.max()), len(folger[0].punkte))
        r = self.client.get('/api/character/genesis9-figur/regler/')
        koerper = next(b for b in r.json()['bereiche'] if b['schluessel'] == 'koerper')
        namen = {x['name']: x for x in koerper['regler']}
        self.assertEqual(namen['body_ctrl_FlexionAutoStrength']['vorgabe'], 0.0)
        self.assertEqual(namen['body_basejointcorrectives']['vorgabe'], 1.0)
        r = self.client.post(
            '/api/character/genesis9-figur/fabrice/netz/',
            data=json.dumps({'regler': {'Fabrice_figure_ctrl_Character': 1.0},
                             'anhaenge': False}),
            content_type='application/json')
        self.assertEqual(r.status_code, 200, r.content[:300])
        # Seit 24.09.2026 kommen die externen Gate-Kanaele anderer Charaktere
        # mit (Wert 0, Fabrice ist weder Damira noch Ursula/Kin/Olesia) -
        # nur die zwei fuer Fabrice gestellten Werte pruefen.
        gelenkregler = r.json()['gelenkregler']
        self.assertEqual(gelenkregler['body_basejointcorrectives'], 1.0)
        self.assertEqual(gelenkregler['body_ctrl_FlexionAutoStrength'], 1.0)

    # -------------------------------------------------------------- Lipsync

    @unittest.skipUnless(Lippensync.verfuegbar(), 'Rhubarb Lip Sync fehlt')
    def test_4_lippensync_endpunkt(self):
        ordner = os.path.join(str(settings.MEDIA_ROOT), 'studio_audio')
        os.makedirs(ordner, exist_ok=True)
        name = 'zz_fable_test_lipsync.wav'
        pfad = os.path.join(ordner, name)
        try:
            import wave
            with wave.open(pfad, 'wb') as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(16000)
                w.writeframes(b''.join(
                    struct.pack('<h', 6000 if (i // 40) % 2 and 4000 < i < 12000 else 0)
                    for i in range(32000)))
            r = self.client.post(
                '/api/studio/lipsync/',
                data=json.dumps({'audioUrl': '/media/studio_audio/' + name}),
                content_type='application/json')
            self.assertEqual(r.status_code, 200, r.content[:300])
            d = r.json()
            self.assertEqual(d['dauer'], 2.0)
            self.assertGreaterEqual(len(d['cues']), 2)
            self.assertTrue(all(c['form'] in 'ABCDEFGHX' for c in d['cues']))
            self.assertTrue(os.path.isfile(pfad.replace('.wav', '.lipsync.json')))
        finally:
            for endung in ('.wav', '.lipsync.json'):
                p = pfad.replace('.wav', endung)
                if os.path.isfile(p):
                    os.remove(p)

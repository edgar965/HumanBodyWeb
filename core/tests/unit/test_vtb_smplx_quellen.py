# -*- coding: utf-8 -*-
u"""Die eigene SMPL-X-Pipeline, zweiter Teil (12.09.2026): Quellen, Handgelenk,
Boden, Bildfolge, Netz-Video — der Teil ohne Grafikkarte.

Edgar: „ich kann in der Pipeline konfigurieren ob mit GVHMR oder GEM usw? sehe
das nicht" / „in der pipeline fehlen die Haende und das Gesicht" / „fixe:
Finger ruhiger (SOMA->MANO), Fusskontakt/Handgelenk-Uebergabe, cap.set".

Sabotagen, die diese Faelle rot machen (gemacht): SOMA-Grundgelenk ohne die
Mittelhand verkettet -> `test_grundgelenk_verkettet_mittelhand_und_grundgelenk`;
Handgelenk als LOKALE statt Weltdrehung uebernommen ->
`test_handgelenk_nimmt_die_weltdrehung_unter_gems_unterarm`; `Bildfolge` mit
`cap.set` statt `grab` -> `test_liest_vorwaerts_und_ueberspringt_mit_grab`;
`--no_video` mit dest `video` -> `test_lift_3d_verwechselt_video_nicht_mit_dem_pfad`.
"""
import os
import re
import unittest

import numpy as np
from scipy.spatial.transform import Rotation

from ._wrappersuchpfad import Wrappersuchpfad, WRAPPERS
from ._pruefablage import Pruefablage

Wrappersuchpfad.setzen()

from bildfolge import Bildfolge                              # noqa: E402
from bodenkontakt import Bodenkontakt                        # noqa: E402
from lifterwahl import Lifterwahl                            # noqa: E402
from smplxbahn import Smplxbahn                              # noqa: E402
from smplxkoerper import Smplxkoerper                        # noqa: E402
from smplxlauf import Smplxlauf                              # noqa: E402
from smplxmischung import Smplxmischung                      # noqa: E402
from smplxreihe import Smplxreihe                            # noqa: E402
from somahaende import Somahaende                            # noqa: E402
from smplskelett import Smplskelett                          # noqa: E402


class Kameraattrappe:
    u"""`grab`/`read` zaehlen; `set` ist verboten — genau das war die Bremse."""

    def __init__(self, bilder):
        self.bilder = bilder
        self.stelle = 0
        self.gegriffen = 0
        self.gelesen = 0

    def grab(self):
        if self.stelle >= self.bilder:
            return False
        self.stelle += 1
        self.gegriffen += 1
        return True

    def read(self):
        if self.stelle >= self.bilder:
            return False, None
        self.stelle += 1
        self.gelesen += 1
        return True, 'bild%d' % (self.stelle - 1)

    def set(self, *_):
        raise AssertionError('cap.set — das war der langsame Weg')


class DieBildfolge(unittest.TestCase):

    def test_liest_vorwaerts_und_ueberspringt_mit_grab(self):
        cap = Kameraattrappe(10)
        folge = Bildfolge(cap)
        self.assertEqual(folge.bild(0), (True, 'bild0'))
        self.assertEqual(folge.bild(3), (True, 'bild3'))
        self.assertEqual(folge.bild(3), (True, 'bild3'))       # Wiederholung
        self.assertEqual(folge.bild(9), (True, 'bild9'))
        self.assertEqual(cap.gelesen, 3)
        self.assertEqual(cap.gegriffen, 7)
        self.assertEqual(folge.bild(10)[0], False)

    def test_rueckwaertssprung_ist_ein_fehler(self):
        folge = Bildfolge(Kameraattrappe(10))
        folge.bild(5)
        with self.assertRaises(ValueError):
            folge.bild(2)


class SomaNachSmplx(unittest.TestCase):

    N = 4
    NAMEN = ['Hips', 'LeftHand', 'RightHand']
    for _seite in ('Left', 'Right'):
        for _finger in ('Thumb', 'Index', 'Middle', 'Ring', 'Pinky'):
            for _g in ('1', '2', '3', '4'):
                NAMEN.append('%sHand%s%s' % (_seite, _finger, _g))

    def _params(self, drehung):
        u"""`drehung`: Name -> Achse-Winkel, alles andere null."""
        koerper = np.zeros((self.N, len(self.NAMEN) - 1, 3), np.float32)
        for name, rv in drehung.items():
            koerper[:, self.NAMEN.index(name) - 1] = rv
        return {'names': np.array(self.NAMEN), 'body_pose': koerper}

    def test_grundgelenk_verkettet_mittelhand_und_grundgelenk(self):
        soma = Somahaende(self._params({'LeftHandIndex1': [0, 0, 0.2],
                                        'LeftHandIndex2': [0, 0, 0.3],
                                        'LeftHandIndex3': [0, 0, 0.5]}), np)
        links, rechts = soma.haende(self.N)
        self.assertEqual(links.shape, (self.N, 15, 3))
        np.testing.assert_allclose(links[0, 0], [0, 0, 0.5], atol=1e-6)   # index1 = 1 o 2
        np.testing.assert_allclose(links[0, 1], [0, 0, 0.5], atol=1e-6)   # index2 = 3
        np.testing.assert_allclose(links[0, 2], 0, atol=1e-6)             # index3 = 4
        self.assertFalse(rechts.any())

    def test_daumen_zaehlt_ab_dem_sattelgelenk(self):
        soma = Somahaende(self._params({'RightHandThumb1': [0.4, 0, 0],
                                        'RightHandThumb3': [0, 0.1, 0]}), np)
        _, rechts = soma.haende(self.N)
        np.testing.assert_allclose(rechts[0, 12], [0.4, 0, 0], atol=1e-6)
        np.testing.assert_allclose(rechts[0, 14], [0, 0.1, 0], atol=1e-6)

    def test_fehlendes_gelenk_ist_ein_fehler(self):
        params = self._params({})
        params['names'] = np.array([n for n in self.NAMEN if n != 'LeftHandRing3'])
        params['body_pose'] = params['body_pose'][:, :-1]
        with self.assertRaises(KeyError):
            Somahaende(params, np).hand('left')

    def test_andere_laenge_wird_verhaeltnismaessig_verteilt(self):
        soma = Somahaende(self._params({}), np)
        # `np.rint` rundet halbe zur geraden Zahl — wie `Smplxmischung._zuordnung`.
        np.testing.assert_array_equal(soma.zuordnung(7), [0, 0, 1, 2, 2, 2, 3])


class DasHandgelenk(unittest.TestCase):

    N = 8
    ELLBOGEN = Smplskelett.NAMEN.index('Left_elbow')
    HANDGELENK = Smplskelett.NAMEN.index('Left_wrist')

    def _reihe(self, ellbogen, handgelenk):
        reihe = Smplxreihe(30.0, np)
        koerper = np.zeros((21, 3))
        koerper[self.ELLBOGEN - 1] = ellbogen
        koerper[self.HANDGELENK - 1] = handgelenk
        for _ in range(self.N):
            reihe.dazu({'smplx_root_pose': np.zeros(3), 'smplx_body_pose': koerper.reshape(-1),
                        'smplx_lhand_pose': np.zeros(45), 'smplx_rhand_pose': np.zeros(45),
                        'smplx_jaw_pose': np.zeros(3), 'smplx_expr': np.zeros(10),
                        'smplx_shape': np.zeros(10), 'cam_trans': np.zeros(3)})
        return reihe.als_felder()

    def test_handgelenk_nimmt_die_weltdrehung_unter_gems_unterarm(self):
        u"""SMPLest-X: Ellbogen 20 Grad, Handgelenk 30 Grad um x -> Welt 50.
        GEMs Ellbogen steht bei 0: das neue lokale Handgelenk muss 50 sein."""
        bahn = Smplxbahn(self.N, 30.0, np)
        m = Smplxmischung(bahn, self._reihe([np.radians(20), 0, 0], [np.radians(30), 0, 0]), np)
        m.handgelenk(0.0)
        neu = Rotation.from_rotvec(bahn.body_pose[0, self.HANDGELENK - 1])
        self.assertAlmostEqual(float(np.degrees(neu.magnitude())), 50.0, places=3)
        # Mittel ueber beide Handgelenke; das rechte bleibt bei 0.
        self.assertAlmostEqual(m.bilanz['handgelenk_korrektur_grad'], 25.0, places=1)

    def test_ohne_handgelenk_bleibt_gems_wert(self):
        bahn = Smplxbahn(self.N, 30.0, np)
        bahn.body_pose[:, self.HANDGELENK - 1] = [0.1, 0, 0]
        Smplxmischung(bahn, self._reihe([0, 0, 0], [0.5, 0, 0]), np).mischen(
            0.0, 0.0, handgelenk=False, gesicht=False)
        np.testing.assert_allclose(bahn.body_pose[:, self.HANDGELENK - 1], [[0.1, 0, 0]] * self.N)


class DerBodenkontakt(unittest.TestCase):

    N = 120

    def _bahn(self, wippe_cm=3.0, drift_cm_je_bild=0.3):
        u"""Stehende Figur (Pose null), deren Wurzel wippt und wegdriftet."""
        bahn = Smplxbahn(self.N, 60.0, np)
        # Aufrecht im Kameraraum (y unten): pi um x, wie GVHMR/GEM es liefern.
        bahn.global_orient[:] = [np.pi, 0.0, 0.0]
        t = np.arange(self.N)
        bahn.transl[:, 0] = drift_cm_je_bild * t / 100.0
        bahn.transl[:, 1] = -(wippe_cm / 100.0) * np.sin(t / 8.0)    # y unten im Kameraraum
        bahn.transl[:, 2] = 3.0
        return bahn

    def test_wippe_und_rutschen_verschwinden_im_stand(self):
        bahn = self._bahn()
        bilanz = Bodenkontakt(bahn, np).anwenden()
        self.assertTrue(bilanz['angewandt'])
        self.assertGreater(bilanz['kontakt_bilder'], self.N // 2)
        vorher, nachher = bilanz['hoehenfehler_cm']
        self.assertLess(nachher, vorher / 3)
        rutschen_vorher, rutschen_nachher = bilanz['rutschen_cm_s']
        self.assertLess(rutschen_nachher, rutschen_vorher / 3)

    def test_pose_bleibt_unangetastet(self):
        bahn = self._bahn()
        bahn.body_pose[:, 3] = [0.2, 0, 0]
        vorher = bahn.body_pose.copy()
        Bodenkontakt(bahn, np).anwenden()
        np.testing.assert_array_equal(bahn.body_pose, vorher)

    def test_ein_kurzer_kontakt_verschiebt_nicht_die_ganze_spur(self):
        u"""Ballett: 4 Standbilder von 298 — unter 5 % bleibt die Spur unangetastet."""
        bahn = self._bahn(wippe_cm=0.0, drift_cm_je_bild=5.0)
        # Sechs Bilder Stand (der Schritt setzt aus, kein Sprung danach); das
        # geglaettete Tempo laesst davon die inneren vier unter der Grenze —
        # 3 % der Bilder, zu wenig.
        schritt = np.full(self.N, 0.05)
        schritt[50:56] = 0.0
        bahn.transl[:, 0] = np.cumsum(schritt)
        vorher = bahn.transl.copy()
        bilanz = Bodenkontakt(bahn, np).anwenden()
        self.assertFalse(bilanz['angewandt'])
        self.assertTrue(3 <= bilanz['kontakt_bilder'] <= 6, bilanz)
        np.testing.assert_array_equal(bahn.transl, vorher)

    def test_ohne_stand_keine_korrektur(self):
        u"""Ein Sprung ueber alle Bilder: nichts nah am Boden -> nichts geaendert."""
        bahn = self._bahn(wippe_cm=0.0, drift_cm_je_bild=5.0)     # 300 cm/s: zu schnell
        vorher = bahn.transl.copy()
        bilanz = Bodenkontakt(bahn, np).anwenden()
        self.assertEqual(bilanz['kontakt_bilder'], 0)
        np.testing.assert_array_equal(bahn.transl, vorher)


class DieQuellen(unittest.TestCase):

    def test_koerperquellen_und_ihre_namen(self):
        self.assertEqual(Smplxkoerper.QUELLEN, ('gem', 'gvhmr', 'duomo'))
        with self.assertRaises(ValueError):
            Smplxkoerper('wham', 'v.mp4', 'z.bvh')
        for quelle in Smplxkoerper.QUELLEN:
            self.assertIn(quelle, Smplxkoerper.NAMEN)

    def test_lauf_weist_unbekannte_quellen_ab(self):
        for falsch in ({'haende': 'hamer'}, {'gesicht': 'v4'}, {'handgelenk': 'mitte'}):
            with self.assertRaises(ValueError):
                Smplxlauf('v.mp4', 'z.bvh', **falsch)

    def test_reihe_laeuft_nur_wenn_etwas_daran_haengt(self):
        self.assertTrue(Smplxlauf('v.mp4', 'z.bvh').braucht_reihe)
        self.assertFalse(Smplxlauf('v.mp4', 'z.bvh', haende='gemx', gesicht='keins',
                                   handgelenk='koerper').braucht_reihe)
        self.assertTrue(Smplxlauf('v.mp4', 'z.bvh', haende='gemx', gesicht='keins',
                                  handgelenk='hand').braucht_reihe)


class DieVerteiler(unittest.TestCase):

    NEU = ('body_source', 'hands_source', 'face_source', 'wrist_source', 'ground', 'video')

    def test_lifterwahl_kennt_die_neuen_schalter(self):
        u"""`video` heisst im Verteiler `netzvideo`: `Lifterwahl.starten(name, video, ...)`
        traegt den Pfad schon unter diesem Namen (gesehen 12.09.2026, Auftrag b22e2abb)."""
        _, erlaubt = Lifterwahl.LIFTER['smplx']
        for name in self.NEU[:-1] + ('netzvideo',):
            self.assertIn(name, erlaubt)
        self.assertNotIn('video', erlaubt)

    def test_lift_3d_verwechselt_video_nicht_mit_dem_pfad(self):
        u"""`--video` ist der Eingabepfad; `--no_video` darf nicht auf `video`
        zielen — sonst kommt `False` als Videopfad an (gesehen 12.09.2026)."""
        for datei in ('lift_3d.py', 'smplx_lift.py'):
            quelle = (WRAPPERS / datei).read_text(encoding='utf-8')
            self.assertIn("'--no_video'", quelle)
            self.assertNotRegex(quelle, r"'--no_video',\s*dest='video'")
            self.assertIn('netzvideo', quelle)

    def test_smplbefehl_reicht_quellen_und_zugaben_durch(self):
        from core.pipelines.smplbefehl import Smplbefehl

        class Auftrag:
            pipeline = 'smplx'
            pipeline_params = {'body_source': 'gvhmr', 'hands_source': 'gemx',
                               'video': False}

        class Einstellungen:
            gem_static_cam = True
            gem_smooth_sigma = 2.0
            gem_joint_limits = True
            smpl_device = 'cuda'

        zusatz = Smplbefehl(Auftrag(), Einstellungen()).zusatz()
        text = ' '.join(zusatz)
        self.assertIn('--body_source gvhmr', text)
        self.assertIn('--hands_source gemx', text)
        self.assertIn('--face_source smplestx', text)
        self.assertIn('--wrist_source hand', text)
        self.assertIn('--no_video', zusatz)
        self.assertNotIn('--no_ground', zusatz)

    def test_pipelineparameter_liest_die_auswahlen(self):
        from django.http import QueryDict
        from core.api.pipelineparameter import Pipelineparameter
        post = QueryDict('smplx_body_source=duomo&smplx_hands_source=gemx'
                         '&smplx_face_source=keins&smplx_wrist_source=koerper'
                         '&smplx_ground=on')
        p = Pipelineparameter.lesen(post, 'smplx')
        self.assertEqual((p['body_source'], p['hands_source'], p['face_source'],
                          p['wrist_source']), ('duomo', 'gemx', 'keins', 'koerper'))
        self.assertTrue(p['ground'])
        self.assertFalse(p['video'])

    def test_karte_und_js_kennen_die_felder(self):
        from django.conf import settings
        wurzel = settings.BASE_DIR
        karte = (wurzel / 'templates' / '_pipeline_smplx.html').read_text(encoding='utf-8')
        felder = (wurzel / 'static' / 'js' / 'auftraege' / 'pipelinefelder.js').read_text(
            encoding='utf-8')
        for name in self.NEU:
            self.assertIn('name="smplx_%s"' % name, karte)
            self.assertRegex(felder, r"\['%s', '(text|bool)'\]" % name)


class DasNetzvideoAufDerErgebnisseite(unittest.TestCase):

    def test_netzvideo_neben_dem_bvh_wird_gefunden(self):
        from core.api.dateien import Auftragsdateien

        class Auftrag:
            bvh_file = None

        selbst = Auftragsdateien.__new__(Auftragsdateien)
        selbst.job = Auftrag()
        self.assertIsNone(selbst._netzvideo())
        with Pruefablage.ordner('netzvideo') as ordner:
            selbst.job.bvh_file = os.path.join(ordner, 'smplx_probe.bvh')
            self.assertIsNone(selbst._netzvideo())
            pfad = os.path.join(ordner, 'smplx_probe' + Auftragsdateien.NETZVIDEO)
            with open(pfad, 'wb') as datei:
                datei.write(b'0')
            self.assertEqual(selbst._netzvideo(), pfad)

    def test_hilfe_nennt_die_neuen_stufen(self):
        from core.dienste.eigenepipeline import Eigenepipeline
        titel = {t for t, _, _ in Eigenepipeline.PLAN}
        for erwartet in ('Quellen wählbar', 'Handgelenk-Übergabe', 'Fußkontakt', 'Netz-Video'):
            self.assertIn(erwartet, titel)
        self.assertTrue(re.search(r'GEM-X', Eigenepipeline.QUELLEN[1]['laeuft']))


class DieAehnlichkeitInNode(unittest.TestCase):
    u"""`bvh_player/aehnlichkeit.js` — die Rechnung hinter der Rig-Ueberlagerung,
    wirklich in Node ausgefuehrt (das Zeichnen haengt an `three`, sie nicht)."""

    def test_massstab_und_verschiebung_werden_wiedergefunden(self):
        from django.conf import settings
        from djangobase.testhelfer import Webmodul
        from ..jsmodul import Jsmodul
        pfad = settings.BASE_DIR / 'static' / 'js' / 'bvh_player' / 'aehnlichkeit.js'
        ergebnis = Webmodul(pfad, Jsmodul.WURZELN).laufen('''
            const { Aehnlichkeit } = await import(MODUL);
            const p = [[0, 0], [1, 0], [0, 1], [1, 1], [0.5, 0.5]];
            const q = p.map(([x, y]) => [2 * x + 10, 2 * y + 20]);
            const fit = Aehnlichkeit.anpassen(p, q);
            const zuwenig = Aehnlichkeit.anpassen(p.slice(0, 2), q.slice(0, 2));
            const bild = Aehnlichkeit.abbilden(fit, 3, 4);
            console.log(JSON.stringify({ fit, zuwenig, bild }));
        ''')
        self.assertAlmostEqual(ergebnis['fit']['s'], 2.0, places=9)
        self.assertAlmostEqual(ergebnis['fit']['tx'], 10.0, places=9)
        self.assertAlmostEqual(ergebnis['fit']['ty'], 20.0, places=9)
        self.assertEqual(ergebnis['fit']['paare'], 5)
        self.assertIsNone(ergebnis['zuwenig'])
        self.assertEqual(ergebnis['bild'], [16, 28])

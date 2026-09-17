# -*- coding: utf-8 -*-
u"""SMPL-X-Skelett: Namen, Eltern, Retarget-Zuordnung, Segmentierungsuebertrag.

WARUM (Edgar, 15.09.2026: „kannst du die SMPL Modelle auf SMPL-X umstellen
(also inkl. Gesichtsknochen)?"): Die SMPL-Figur traegt jetzt 55 Gelenke —
Koerper, Kiefer, Augen, Finger. Hier steht ohne Modelldatei, was davon
Definition ist:

1. `Smplxskelett.NAMEN`: 22 Koerpergelenke aus `Smplskelett` (BVH-Namen),
   dann `Jaw`, `Left_eye`, `Right_eye`, dann die 30 Finger aus
   `Smplxfinger` — keine zweite Liste, keine Handflaechen.
2. Die Eltern: Gesicht am Kopf (15), Finger an den Handgelenken (20/21),
   `pruefen` nimmt die Wurzel auch als 4294967295 (uint32-Umlauf der
   Modelldatei) und lehnt eine vertauschte Elternliste ab.
3. `Smplxzuordnung`: DEF -> SMPL-X mit 22 Koerpern + 30 Fingern + Kiefer;
   Mixamo (mit Fingern) trifft 52 Ziele, das SMPL-X-Format sich selbst.
4. `Smplxsegmentierung.uebertragen`: jeder SMPL-X-Punkt erbt die Teile des
   SMPL-Punkts mit dem groessten Anteil — Ueberlappungen bleiben.
5. Verdrahtung als Quelltext: Retarget-Ziel `smpl` nutzt `Smplxzuordnung`,
   Dialog und Kataloge sagen „SMPL-X".

Sabotage-Gegenprobe: in `Smplxskelett.ELTERN` den Kopf der Augen auf 12
setzen -> Fall 2 rot (Modelleltern weichen ab); `'DEF-jaw': 'Jaw'` aus
`DEF_ZU_SMPLX` nehmen -> Fall 3 rot.
"""
from django.conf import settings
from django.test import SimpleTestCase

from SMPL.finger import Smplxfinger
from SMPL.skelett import Smplskelett
from SMPL.xsegmentierung import Smplxsegmentierung
from SMPL.xskelett import Smplxskelett

from ...dienste.smplxzuordnung import DEF_ZU_SMPLX, Smplxzuordnung

STATIK = settings.BASE_DIR / 'static' / 'viewer'


class SmplxskelettTest(SimpleTestCase):

    def test_55_namen_aus_den_vorhandenen_listen(self):
        namen = Smplxskelett.NAMEN
        self.assertEqual(len(namen), 55)
        self.assertEqual(namen[:22], Smplskelett.NAMEN[:22])
        self.assertEqual(namen[22:25], ('Jaw', 'Left_eye', 'Right_eye'))
        self.assertEqual(namen[25:], Smplxfinger.NAMEN)
        self.assertNotIn('Left_palm', namen)
        self.assertEqual(len(set(namen)), 55, 'doppelte Namen')

    def test_eltern_gesicht_am_kopf_finger_am_handgelenk(self):
        eltern = Smplxskelett.ELTERN
        self.assertEqual(len(eltern), 55)
        self.assertEqual(eltern[0], -1)
        self.assertEqual(eltern[22:25], (15, 15, 15))
        self.assertEqual(eltern[25], 20, 'left_index1 haengt am linken Handgelenk')
        self.assertEqual(eltern[40], 21, 'right_index1 am rechten')
        self.assertEqual(eltern[26], 25, 'left_index2 an left_index1')
        self.assertTrue(all(e < i for i, e in enumerate(eltern)),
                        'Eltern stehen vor ihren Kindern')

    def test_pruefen_nimmt_die_modellwurzel_und_lehnt_vertauschte_eltern_ab(self):
        wie_datei = [4294967295] + list(Smplxskelett.ELTERN[1:])
        self.assertTrue(Smplxskelett.pruefen(wie_datei))
        vertauscht = list(Smplxskelett.ELTERN)
        vertauscht[23] = 12
        with self.assertRaises(ValueError):
            Smplxskelett.pruefen(vertauscht)
        with self.assertRaises(ValueError):
            Smplxskelett.pruefen(list(Smplxskelett.ELTERN[:24]))

    # ------------------------------------------------------------ Zuordnung

    def test_zuordnung_deckt_koerper_finger_und_kiefer(self):
        from humanbody_core.skeleton.formats.mixamo import SkeletonMixamo
        from humanbody_core.skeleton.formats.smplx import SkeletonSMPLX
        self.assertEqual(len(DEF_ZU_SMPLX), 53)
        self.assertEqual(DEF_ZU_SMPLX['DEF-f_index.01.L'], 'left_index1')
        self.assertEqual(DEF_ZU_SMPLX['DEF-thumb.03.R'], 'right_thumb3')
        self.assertEqual(DEF_ZU_SMPLX['DEF-jaw'], 'Jaw')
        self.assertNotIn('Left_palm', DEF_ZU_SMPLX.values())
        self.assertTrue(set(DEF_ZU_SMPLX.values()) <= set(Smplxskelett.NAMEN))
        mixamo = Smplxzuordnung.fuer(SkeletonMixamo)
        self.assertEqual(sum(1 for z in mixamo.values() if z), 52)
        eigen = Smplxzuordnung.fuer(SkeletonSMPLX)
        self.assertTrue(all(bvh == ziel for bvh, ziel in eigen.items() if ziel))
        self.assertEqual(Smplxzuordnung.ausnahmen(SkeletonMixamo), [])

    # -------------------------------------------------------- Segmentierung

    def test_segmentierung_erbt_die_teile_des_groessten_anteils(self):
        seg = {'head': [0, 1], 'neck': [1, 2], 'hips': [3]}
        zuordnung = [1, 3, 0, 2, 1]      # je SMPL-X-Punkt sein SMPL-Punkt
        aus = Smplxsegmentierung.uebertragen(seg, zuordnung)
        self.assertEqual(aus, {'head': [0, 2, 4], 'neck': [0, 3, 4], 'hips': [1]})

    # ----------------------------------------------------------- Quelltext

    def test_retarget_und_browser_kennen_die_zuordnung(self):
        retarget = SmplxskelettTest._text(settings.BASE_DIR / 'core' / 'dienste' / 'retargetdaten.py')
        self.assertIn('from .smplxzuordnung import Smplxzuordnung', retarget)
        self.assertIn("kette.geometrie(), Smplxzuordnung)", retarget)
        kataloge = SmplxskelettTest._text(STATIK / 'gemeinsam' / 'figurkataloge.js')
        self.assertIn("smpl: { titel: 'SMPL-X'", kataloge)
        # Der Reiter der Szene heißt, wie `Figurkataloge` ihn nennt: Die Szene
        # baut den Dialog seit dem 17.09.2026 über den gemeinsamen `Figurwahldialog`.
        dialog = SmplxskelettTest._text(STATIK / 'scene' / 'charakterdialog.js')
        self.assertIn('new Figurwahldialog(', dialog)
        figur = SmplxskelettTest._text(settings.BASE_DIR / 'core' / 'dienste' / 'smplfigur.py')
        self.assertIn("'smplx_female'", figur)
        self.assertIn("'f_smpl_average_A40'", figur)       # bleibt ladbar

    @staticmethod
    def _text(pfad):
        return pfad.read_text(encoding='utf-8')

# -*- coding: utf-8 -*-
u"""Daz-Stuecke auf HumanBody gegen die ECHTEN Daten (19.09.2026 spaet, Edgar:
„schreib dir testcases fuer alle bugs, sind alle nicht gefixt").

Die Unit-Tests zu `G9hbsitz` und `G9hbfusspose` rechnen auf Kunstrumpfen und
Kunstfuessen — sie belegen die Rechnung, nicht den Sitz. Hier laufen die
gemeldeten Bilder selbst: Angie Jeans, Angie Top, Bardot Sandals und das
Dancing-Queen-Kleid auf der HumanBody-Grundfigur `Female_Caucasian`, dazu
das Genesis-Original als Massstab. Jeder Fall traegt die Zahl, die vor dem
Fix gemessen wurde, damit die Schwelle nicht geraten ist:

1. Bund der Jeans: auf Genesis 10,1 cm ueber der Hueftweite, auf HumanBody vor
   dem Fix 3,6 cm, danach 7,1 cm. Schwelle: hoechstens 4 cm weniger als Genesis.
2. Weite des Tops: Top-Umfang / Rumpf-Umfang an der Taille und 2 cm ueber dem
   Saum — Genesis 1,55 / 1,37, HumanBody vor dem Fix 1,74 / 1,61, danach
   1,61 / 1,41. Schwelle: hoechstens 0,10 ueber Genesis.
3. Sandale auf Genesis wie in der Datei: die Projektion auf den flachen Fuss
   darf den Schuh nicht versetzen (Regression 19.09. 21:39: `G9teilbindung`
   nahm die Daz-Bindung „alles an pelvis" als Karte — 4 cm tiefer).
4. Ferse und Ballen auf der Sandale (HumanBody): der um den Absatz gebeugte
   Fuss steht mit Ferse und Ballen zwischen 10 mm im und 15 mm ueber dem
   Fussbett (gemessen -4,1 / -3,9 mm; flacher Fuss ohne Absatz: Ballen 40 mm
   darueber; mit der Regression aus 3: Ferse 47 mm), Sohle zur Sandale median
   unter 12 mm (8,8).
5. Der Rock haengt nicht an den Haenden: unterhalb der Hueftweite kein Punkt
   des Kleids mit Gewicht an Hand-, Finger- oder Armknochen (vor dem Fix 553),
   und jeder genannte Knochen steht im Rigify-Skelett der Figur.
6. Die Jeans auf Genesis 9 (Ursula1): alle sieben Teile tragen Hautgewichte,
   nennen nur Knochen des Skeletts und sind als dForce-Stoff erkannt — sonst
   bindet `Eigenhaut` nichts und das Teil steht still.
7. Die Vorschaubilder der Garderobe: ein LVA-Stueck (Leder, RGBA mit
   durchsichtigem Grund) hat auf dem hellen Grund der Liste eine mittlere
   Helligkeit ueber 100 von 255, auf dem dunklen Seitengrund unter 50.

LongRunner: Paarung und vier Uebertragungen (rund 60 s). Ohne Daz-Bibliothek
oder HumanBody-Daten uebersprungen.

Sabotage-Gegenproben: `G9hbsitz.rumpfhoehen` gibt `aus, None` zurueck ->
Fall 1 rot (3,6 cm); `G9aufhumanbody.oertlich` liefert ueberall `massstab`
-> Fall 2 rot (1,74); `G9teilbindung.geprueft` gibt `self` zurueck -> Fall 3
und 4 rot; `G9hbteilhaut.haut` mit `bindung=None` -> Fall 5 rot.
"""
import base64
import json
import unittest
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase
from scipy.spatial import cKDTree

from Genesis9.formung import G9formung
from Genesis9.garderobe import G9garderobe
from Genesis9.pfade import G9pfade

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()
Humanbodypfad.assets()


def bibliothek_da():
    try:
        return G9pfade.vorhanden() and bool(G9pfade.people_fremd())
    except Exception:  # noqa: BLE001 — ohne Bibliothek: kein Test
        return False


def punkte_aus(teil):
    return np.frombuffer(base64.b64decode(teil['vertices']), dtype=np.float32).reshape(-1, 3).astype(np.float64)


def haut_aus(teil):
    h = teil['hautgewichte']
    idx = np.frombuffer(base64.b64decode(h['skin_indices']), dtype=np.uint16).reshape(-1, 4)
    w = np.frombuffer(base64.b64decode(h['skin_weights']), dtype=np.uint8).reshape(-1, 4) / 255.0
    return list(h['knochen']), idx, w


HAND_ODER_ARM = ('hand', 'palm', 'thumb', 'f_index', 'f_middle', 'f_ring', 'f_pinky',
                 'upper_arm', 'forearm', 'shoulder')


@unittest.skipUnless(bibliothek_da(), 'Daz-Bibliothek mit Genesis 9 und 8 fehlt')
class DazAufHumanbodySitz(SimpleTestCase):
    databases = set()
    BAUART = 'Female_Caucasian'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from core.dienste.g9aufhumanbody import G9aufhumanbody
        from core.dienste.g9garmentfigur import G9garmentfigur
        from core.dienste.g9hbsitz import G9hbsitz
        from GarmentCode.koerperdienst import Garmentkoerper
        cls.formung = G9formung({})
        cls.hoch = np.array([0.0, cls.formung.boden(), 0.0])
        g9 = G9garmentfigur({})
        cls.g9_punkte = g9.punkte()
        cls.g9_rumpf = np.asarray(g9.segmente().get('body') or [], dtype=np.int64)
        cls.traeger = G9aufhumanbody('female', cls.BAUART, {}, {})
        cls.hb_punkte = cls.traeger.figur()['punkte']
        cls.hb_rumpf = np.asarray(Garmentkoerper.segmente('female').get('body') or [], dtype=np.int64)
        cls.lg = G9hbsitz.landmarken(cls.g9_punkte, cls.g9_rumpf)
        cls.lh = G9hbsitz.landmarken(cls.hb_punkte, cls.hb_rumpf)
        cls.quelle, cls.ziel = {}, {}
        for kennung in ('angie_jeans', 'angie_top', 'bardot_sandals'):
            cls.quelle[kennung] = cls._auf_genesis(kennung)
            cls.ziel[kennung] = [cls.traeger.uebertragen(p) for p in cls.quelle[kennung]]

    @classmethod
    def _auf_genesis(cls, kennung):
        eintrag = G9garderobe.eintrag(kennung) or {}
        werte, knochen = G9garderobe.stilwerte(kennung, [])
        zusatz = dict(eintrag.get('vorgaben') or {})
        zusatz.update(werte)
        return [folger.punkte_zu(cls.formung, zusatz, drehung=knochen, lage=None) - cls.hoch
                for folger, _lage in G9garderobe.teile(kennung)
                if getattr(folger, 'ART', None) != 'strang']

    @staticmethod
    def umfang(punkte, y):
        from core.dienste.g9hbsitz import G9hbsitz
        return G9hbsitz.umfang(np.asarray(punkte), y)

    # ------------------------------------------------------------ 1. Bund

    def test_1_bund_der_jeans_sitzt_wie_auf_genesis(self):
        oben_g9 = float(np.percentile(np.vstack(self.quelle['angie_jeans'])[:, 1], 99.5))
        oben_hb = float(np.percentile(np.vstack(self.ziel['angie_jeans'])[:, 1], 99.5))
        ueber_g9 = oben_g9 - self.lg['huefte']            # gemessen 0,101
        ueber_hb = oben_hb - self.lh['huefte']            # vor dem Fix 0,036, danach 0,071
        self.assertGreater(ueber_g9, 0.08)
        self.assertGreaterEqual(ueber_hb, ueber_g9 - 0.04,
                                'Bund %.1f cm ueber der Huefte (Genesis %.1f)' % (ueber_hb * 100, ueber_g9 * 100))

    # ------------------------------------------------------------ 2. Weite

    def test_2_top_so_eng_wie_auf_genesis(self):
        top_g9, top_hb = np.vstack(self.quelle['angie_top']), np.vstack(self.ziel['angie_top'])
        rumpf_g9, rumpf_hb = self.g9_punkte[self.g9_rumpf], self.hb_punkte[self.hb_rumpf]
        saum_g9 = float(np.percentile(top_g9[:, 1], 0.5)) + 0.02
        saum_hb = float(np.percentile(top_hb[:, 1], 0.5)) + 0.02
        for name, y_g9, y_hb in (('Taille', self.lg['taille'], self.lh['taille']),
                                 ('Saum', saum_g9, saum_hb)):
            v_g9 = self.umfang(top_g9, y_g9) / self.umfang(rumpf_g9, y_g9)   # 1,55 / 1,37
            v_hb = self.umfang(top_hb, y_hb) / self.umfang(rumpf_hb, y_hb)   # 1,74 -> 1,61 / 1,61 -> 1,41
            self.assertTrue(np.isfinite(v_g9) and np.isfinite(v_hb), name)
            self.assertLessEqual(v_hb, v_g9 + 0.10, '%s: Top/Rumpf %.2f, Genesis %.2f' % (name, v_hb, v_g9))

    # ---------------------------------------------------------- 3. Sandale

    def test_3_sandale_liegt_auf_genesis_wie_in_der_datei(self):
        folger = G9garderobe.teile('bardot_sandals')[0][0]
        roh = np.asarray(folger.punkte, dtype=np.float64) - self.hoch
        projiziert = self.quelle['bardot_sandals'][0]
        rechts = projiziert[:, 0] > 0
        for name, was in (('unten', np.min), ('oben', np.max)):
            d = float(was(projiziert[rechts][:, 1]) - was(roh[rechts][:, 1]))   # Regression: -0,037
            self.assertLess(abs(d), 0.015, 'Sandale %s um %.1f cm versetzt' % (name, d * 100))

    def test_4_ferse_im_fersenbett_auf_humanbody(self):
        from core.dienste.g9hbfusspose import G9hbfusspose
        sandale = self.ziel['bardot_sandals'][0]
        rechts = sandale[sandale[:, 0] > 0]
        absatz = G9hbfusspose.absatz('bardot_sandals', self.ziel['bardot_sandals'])
        self.assertTrue(absatz, 'kein Absatz aus der Fusspose')
        haut = self.traeger.haut(self.hb_punkte)
        namen = np.array(haut['knochen'])
        fuehrend = namen[haut['index'][np.arange(len(self.hb_punkte)), haut['gewicht'].argmax(axis=1)]]
        idx = np.flatnonzero(np.isin(fuehrend, ['DEF-foot.L', 'DEF-toe.L']))    # +x wie die Sandale
        fuss = {'knochen': haut['knochen'], 'index': haut['index'][idx], 'gewicht': haut['gewicht'][idx]}
        koepfe = G9hbfusspose.koepfe('female')
        gebeugt = G9hbfusspose.gebeugt(self.hb_punkte[idx], fuss, absatz, koepfe)
        sohle = self._sohle(gebeugt)
        abstand, _n = cKDTree(rechts).query(sohle)
        self.assertLess(float(np.median(abstand)), 0.012, 'Sohle zur Sandale median %.1f mm' % (np.median(abstand) * 1000))
        # Ferse (hinterstes Sohlenende) und Ballen (unter dem Zehenkopf) stehen
        # auf der Sandale: Luft zum hoechsten Sandalenpunkt direkt darunter
        # zwischen -10 mm (im Fussbett) und +15 mm. Gemessen gebeugt: Ferse -4,1,
        # Ballen -3,9 mm; flacher Fuss: Ballen +40 mm; Regression: Ferse +47 mm.
        ferse = sohle[sohle[:, 2].argmin()]
        ballen = sohle[np.argmin(np.abs(sohle[:, 2] - koepfe['DEF-toe.L'][2]))]
        for name, punkt in (('Ferse', ferse), ('Ballen', ballen)):
            luft = self._luft(punkt, rechts)
            self.assertTrue(np.isfinite(luft), '%s: keine Sandale darunter' % name)
            self.assertGreater(luft, -0.010, '%s %.1f mm in der Sandale' % (name, -luft * 1000))
            self.assertLess(luft, 0.015, '%s %.1f mm ueber der Sandale' % (name, luft * 1000))

    @staticmethod
    def _luft(punkt, sandale, umkreis=0.02):
        u"""Meter zwischen `punkt` und dem hoechsten Sandalenpunkt darunter (xz-Umkreis)."""
        unter = sandale[(np.hypot(sandale[:, 0] - punkt[0], sandale[:, 2] - punkt[2]) < umkreis)
                        & (sandale[:, 1] < punkt[1] + 0.005)]
        return float(punkt[1] - unter[:, 1].max()) if len(unter) else float('nan')

    @staticmethod
    def _sohle(fuss):
        u"""Je Zentimeter in z der tiefste Fusspunkt."""
        aus = []
        for z in np.arange(fuss[:, 2].min(), fuss[:, 2].max(), 0.01):
            m = np.abs(fuss[:, 2] - z) < 0.005
            if m.any():
                aus.append(fuss[m][fuss[m][:, 1].argmin()])
        return np.array(aus)

    # ------------------------------------------------------------- 5. Rock

    def test_5_der_rock_haengt_nicht_an_den_haenden(self):
        from core.api.g9kleidhumanbody import G9kleidhumanbody
        rumpf = {'figurart': 'humanbody', 'geschlecht': 'female', 'bauart': self.BAUART,
                 'morphs': {}, 'meta': {}}
        antwort = G9kleidhumanbody.antwort('dancing_queen_dress',
                                           G9garderobe.eintrag('dancing_queen_dress') or {}, rumpf)
        self.assertIsInstance(antwort, dict, getattr(antwort, 'content', antwort))
        # Dasselbe Skelett, das `/api/character/rigify-skeleton/` dem Browser gibt.
        datei = Path(settings.HUMANBODY_DATA_DIR) / 'def_skeleton.json'
        self.assertTrue(datei.is_file(), datei)
        im_skelett = {k['name'] for k in json.loads(datei.read_text(encoding='utf-8'))['bones']}
        rock = 0
        for teil in antwort['teile']:
            knochen, idx, w = haut_aus(teil)
            p = punkte_aus(teil)
            self.assertTrue(set(knochen) <= im_skelett,
                            '%s: %s' % (teil['name'], sorted(set(knochen) - im_skelett)[:5]))
            an_hand = np.isin(np.array(knochen)[idx], [k for k in knochen if k.startswith('DEF-') and any(t in k for t in HAND_ODER_ARM)])
            unten = p[:, 1] < self.lh['huefte']
            rock += int(((an_hand & (w > 0.0)).any(axis=1) & unten).sum())      # vor dem Fix 553
        self.assertEqual(rock, 0, '%d Rockpunkte haengen an Hand oder Arm' % rock)

    # ------------------------------------------------------------ 6. Jeans

    def test_6_jeans_auf_genesis_binden_an_das_skelett(self):
        from core.api.g9figur import G9figur
        from core.api.g9garderobe import G9garderobeapi
        rumpf = {'figur': 'p3d_ursula', 'regler': {}, 'variante': '', 'stil': [], 'regler_stueck': {},
                 'pose': '', 'ausdruck': '', 'griffe': {}, 'getragen': [], 'rang': 0}
        antwort = G9garderobeapi._kleid('angie_jeans', G9garderobe.eintrag('angie_jeans') or {}, rumpf)
        self.assertIsInstance(antwort, dict, getattr(antwort, 'content', antwort))
        im_skelett = {k['name'] for k in G9figur.formung(rumpf, {}).skelett().bauen()['knochen']}
        self.assertEqual(len(antwort['teile']), 7)
        for teil in antwort['teile']:
            self.assertTrue(teil.get('hautgewichte'), teil['name'])
            knochen, _idx, w = haut_aus(teil)
            self.assertTrue(set(knochen) <= im_skelett, sorted(set(knochen) - im_skelett)[:5])
            self.assertTrue((w.sum(axis=1) > 0.5).all(), '%s: Punkte ohne Gewicht' % teil['name'])
            self.assertTrue(teil.get('stoff'), '%s: kein dForce-Stoff' % teil['name'])

    # ----------------------------------------------------------- 7. Icons

    def test_7_vorschaubilder_auf_hellem_grund(self):
        from PIL import Image
        from Genesis9.garderobeeintrag import G9garderobeeintrag
        eintrag = next((e for e in G9garderobe.liste() if 'lva' in e['id']), None)
        self.assertIsNotNone(eintrag, 'kein LVA-Stueck in der Garderobe')
        pfad = G9garderobeeintrag.vorschaudatei(G9garderobe.datei(eintrag))   # wie `G9vorschau.stueck`
        self.assertTrue(pfad and Path(pfad).exists(), 'Vorschaubild %s' % pfad)
        rgba = Image.open(pfad).convert('RGBA')
        hell = self._helligkeit(rgba, (0xe6, 0xe6, 0xea))     # `.garment-thumb.daz-vorschau`
        dunkel = self._helligkeit(rgba, (0x1e, 0x1e, 0x2e))
        self.assertGreater(hell, 100, 'auf hellem Grund %.0f' % hell)
        self.assertLess(dunkel, 50, 'auf dunklem Grund %.0f' % dunkel)

    @staticmethod
    def _helligkeit(rgba, grund):
        from PIL import Image
        boden = Image.new('RGBA', rgba.size, grund + (255,))
        grau = np.asarray(Image.alpha_composite(boden, rgba).convert('L'), dtype=np.float64)
        return float(grau.mean())

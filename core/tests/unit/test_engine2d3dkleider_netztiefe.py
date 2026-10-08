# -*- coding: utf-8 -*-
"""Die Rumpftiefe gegen das Seitenfoto: Messung (`Seitentiefe`) und Angleichung des Netzes (`Netztiefe`) (05.10.2026).

DER ANLASS
==========
Edgar (05.10.2026, Seitenansicht): „bauch ist viel zu dick beim Modell im vergleich zur vorlage". Gemessen am Auftrag 2026.10.04.11.11.44 war das Netz bei 0,50 und 0,55 der Körpergröße 33 und 29 mm
tiefer als die Silhouette im Seitenfoto; Körper und Hemd-Hülle folgten. Die Messgröße der Kleiderstücke vergleicht mit dem Netz und sah es nicht.

WAS DIESE PRÜFUNG NICHT IST
===========================
Kunstformen (Ellipsoid als Rumpf, eine gezeichnete Silhouette als Seitenfoto), kein echtes Netz, keine Körper-Kette. Dass das abgeleitete Netz die Kette besteht, der Körper danach flacher ist und das
Hemd besser sitzt, zeigt nur der Lauf (`ergebnis.kleiderstuecke.seitentiefe`, `ergebnis.netztiefe`). Geschrieben am 05.10.2026, nicht gelaufen.

BDD - GEGEBEN / DANN
====================
    Eine Maske, in der jede Zeile 40 px breit ist        ... Tiefe 0,04 der Maskenhöhe an jeder Höhe
    Ein Netz tiefer als das Foto                         ... Faktor < 1 im Band, nie unter `tiefe_min`, 1 außerhalb und unter der Toleranz
    Ein Netz so tief wie das Foto oder flacher           ... Faktor 1 überall — nichts zu tun, kein abgeleitetes Netz
    Punkte neben dem Rumpf (Arme)                        ... bleiben, wo sie sind; die Rückseite bleibt ebenfalls
    Das abgeleitete Netz                                 ... gleiche Flächen und Punktzahl, Rumpf flacher; ein zweiter Aufruf rechnet nicht neu
    Option aus, kein Seitenfoto, anderes Original        ... Grund im Zettel; `netzdatei()` gibt das Original
"""

import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
import trimesh
from django.test import SimpleTestCase
from PIL import Image

from core.daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from core.dienste.netztiefe import Netztiefe
from core.dienste.seitentiefe import Seitentiefe

from ._pruefablage import Pruefablage


def ellipsoid(hoehe=1.7, breite=0.40, tiefe=0.36, teilung=5):
    """Ein „Körper": Ellipsoid, Sohle bei y = 0, nach vorn (+z) tiefer als hinten nicht — symmetrisch um z = 0.

    `teilung` 5 (10.242 Punkte): mit 4 lagen in der Schicht bei 0,6 der Größe nur etwa 5 Punkte im Mittelstreifen — unter `Seitentiefe.MIN_PUNKTE` (8), die Höhe fehlte im Profil (KeyError)."""
    kugel = trimesh.creation.icosphere(subdivisions=teilung, radius=1.0)
    punkte = np.asarray(kugel.vertices) * np.array([breite, hoehe / 2.0, tiefe])
    punkte[:, 1] += hoehe / 2.0
    return trimesh.Trimesh(punkte, np.asarray(kugel.faces), process=False)


def seitenmaske(tiefe_je_hoehe, zeilen=1000, breite_px=600):
    """Maske (zeilen, breite_px): in Zeile r (von oben) so breit wie `tiefe_je_hoehe(h)` Anteile der Maskenhöhe, h = Höhenanteil von der Sohle; Person füllt die Höhe."""
    maske = np.zeros((zeilen, breite_px), dtype=bool)
    for r in range(zeilen):
        h = 1.0 - r / (zeilen - 1)
        px = int(round(tiefe_je_hoehe(h) * (zeilen - 1)))
        maske[r, breite_px // 2 - px // 2: breite_px // 2 - px // 2 + px] = px > 0
    return maske


class DieMessung(SimpleTestCase):
    def test_eine_gleichbreite_maske_hat_ueberall_dieselbe_tiefe(self):
        maske = np.zeros((1000, 300), dtype=bool)
        maske[:, 130:170] = True                                   # 40 px breit, 1000 px hoch
        profil = Seitentiefe.foto_profil(maske)
        self.assertTrue(profil)
        for wert in profil.values():
            self.assertAlmostEqual(wert, 39 / 999, places=3)

    def test_eine_leere_maske_hat_kein_profil(self):
        self.assertEqual(Seitentiefe.foto_profil(np.zeros((10, 10), dtype=bool)), {})

    def test_das_profil_eines_ellipsoids_ist_seine_tiefe_geteilt_durch_die_groesse(self):
        koerper = ellipsoid(hoehe=1.7, tiefe=0.36)
        profil = Seitentiefe.modell_profil(np.asarray(koerper.vertices), hoehen=(0.5,))
        t = profil[0.5]['tiefe'] * 1.7                              # in Metern
        self.assertAlmostEqual(t, 0.36 * 2 * 0.99, delta=0.03)       # halbe Achse 0,36 → Tiefe ≈ 0,72 (Perzentil 1…99 der Punkte)
        self.assertLess(profil[0.5]['hinten'], profil[0.5]['vorne'])

    def test_die_einheit_ist_gleichgueltig(self):
        punkte = np.asarray(ellipsoid().vertices)
        a = Seitentiefe.modell_profil(punkte, hoehen=(0.6,))[0.6]['tiefe']
        b = Seitentiefe.modell_profil(punkte * 1000.0, hoehen=(0.6,))[0.6]['tiefe']
        self.assertAlmostEqual(a, b, places=6)                      # als Anteil der Größe: Meter oder Millimeter

    def test_die_abweichung_ist_modell_minus_foto_im_band_und_in_millimetern(self):
        modell = {0.55: {'tiefe': 0.19}, 0.60: {'tiefe': 0.17}, 0.30: {'tiefe': 0.5}}
        foto = {0.55: 0.165, 0.60: 0.17, 0.30: 0.1}
        a = Seitentiefe.abweichung(modell, foto, hoehe_m=1.7)
        self.assertEqual(sorted(a['je_hoehe']), [0.55, 0.6])         # 0,30 liegt außerhalb des Bands
        self.assertAlmostEqual(a['max_mm'], 0.025 * 1700, delta=0.1)
        self.assertEqual(a['tiefer_als_foto'], 0.5)
        self.assertEqual(Seitentiefe.abweichung({}, foto), {})

    def test_das_mittel_nimmt_nur_hoehen_aller_fotos(self):
        self.assertEqual(Seitentiefe.mittel([{0.5: 0.2, 0.6: 0.3}, {0.5: 0.4}]), {0.5: 0.30000000000000004})
        self.assertEqual(Seitentiefe.mittel([]), {})


class DieFaktoren(SimpleTestCase):
    def _netz(self, tiefe):
        return {h: {'tiefe': tiefe(h), 'hinten': -0.1, 'vorne': 0.1} for h in Seitentiefe.HOEHEN}

    def test_ein_tieferes_netz_wird_im_band_verkleinert_und_nie_unter_den_grenzwert(self):
        netz = self._netz(lambda h: 0.20)
        foto = {h: 0.10 for h in Seitentiefe.HOEHEN}                # halb so tief
        f = Netztiefe(None, None).faktoren(netz, foto, 0.8, 0.03)
        self.assertAlmostEqual(min(f.values()), 0.8, places=2)       # nicht unter `tiefe_min`
        self.assertEqual(f[0.40], 1.0)                              # außerhalb des Bands (0,48–0,80)
        self.assertAlmostEqual(f[0.85], 1.0, places=3)              # 0,05 hinter dem Rand: der Schweif der Glättung (σ 0,015) reicht bis dahin — gemessen 0,9998; `anwenden` blendet am Rand ohnehin aus
        self.assertLess(f[0.60], 0.85)

    def test_ein_flacheres_netz_oder_eines_innerhalb_der_toleranz_bleibt(self):
        foto = {h: 0.18 for h in Seitentiefe.HOEHEN}
        for tiefe in (0.15, 0.18, 0.18 * 1.02):                      # flacher, gleich, 2 % tiefer bei 3 % Toleranz
            f = Netztiefe(None, None).faktoren(self._netz(lambda h, t=tiefe: t), foto, 0.8, 0.03)
            self.assertTrue(all(v == 1.0 for v in f.values()), tiefe)

    def test_der_faktor_ist_ueber_die_hoehe_geglaettet(self):
        netz = self._netz(lambda h: 0.30 if abs(h - 0.60) < 0.005 else 0.10)          # ein einzelner Ausreißer
        foto = {h: 0.10 for h in Seitentiefe.HOEHEN}
        f = Netztiefe(None, None).faktoren(netz, foto, 0.5, 0.03)
        self.assertGreater(f[0.60], 0.5)                             # nicht auf den Roh-Faktor 1/3 → 0,5 gedrückt
        self.assertLess(f[0.59], 1.0)                                # die Nachbarn zieht er mit


class DasAnwenden(SimpleTestCase):
    def _anwenden(self, punkte, faktor=0.8, hinten=-0.1):
        faktoren = {h: faktor if 0.55 <= h <= 0.7 else 1.0 for h in Seitentiefe.HOEHEN}
        return Netztiefe(None, None).anwenden(punkte, faktoren, {h: hinten for h in Seitentiefe.HOEHEN})

    def _punkte(self):
        # Punkte in Höhe 0,62 (Körpergröße 1,0: y von 0 bis 1) — Vorderseite z = +0,1 im Rumpf, ein Armpunkt weit außen, ein Punkt hinten
        return np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0],                # Sohle und Scheitel legen die Größe fest
                         [0.0, 0.62, 0.10], [0.0, 0.62, -0.10], [0.40, 0.62, 0.10],
                         [0.0, 0.30, 0.10]])

    def test_die_vorderseite_wandert_zur_rueckseite_und_die_rueckseite_bleibt(self):
        neu = self._anwenden(self._punkte())
        self.assertAlmostEqual(neu[2, 2], -0.1 + 0.8 * 0.2, places=6)         # vorn: hinten + s · Tiefe
        self.assertAlmostEqual(neu[3, 2], -0.1, places=6)                      # hinten bleibt
        self.assertTrue(np.array_equal(neu[:, [0, 1]], self._punkte()[:, [0, 1]]))       # nur z ändert sich

    def test_ein_arm_weit_ausserhalb_und_punkte_ausserhalb_des_bands_bleiben(self):
        original = self._punkte()
        neu = self._anwenden(original)
        self.assertAlmostEqual(neu[4, 2], original[4, 2], places=9)            # |x| = 0,40 = 40 % der Größe → außerhalb von QUER_NULL
        self.assertAlmostEqual(neu[5, 2], original[5, 2], places=9)            # Höhe 0,30 unterhalb des Bands
        self.assertAlmostEqual(neu[0, 2], original[0, 2], places=9)


class DerAblauf(SimpleTestCase):
    def setUp(self):
        self.ordner = Path(Pruefablage.wurzel()) / ('netztiefe_%d' % os.getpid())
        self.ordner.mkdir(parents=True, exist_ok=True)
        self.addCleanup(self._wegraeumen)
        self.original = self.ordner / 'mesh.glb'
        ellipsoid(tiefe=0.36).export(str(self.original))
        # Seitenfoto: halb so tief wie das Netz (36 cm Halbachse → Tiefe 0,72 m ≙ 0,42 der Größe; Foto 0,25)
        self.png = self.ordner / 'seite.png'
        maske = seitenmaske(lambda h: 0.25 * np.sqrt(max(0.0, 1.0 - (2.0 * h - 1.0) ** 2)))
        rgba = np.zeros(maske.shape + (4,), dtype=np.uint8)
        rgba[maske] = (120, 120, 120, 255)
        Image.fromarray(rgba, 'RGBA').save(self.png)
        self.ablage = SimpleNamespace(netzdatei=lambda original=False: self.original, arbeit=lambda n='': self.ordner / n if n else self.ordner)
        self.job = SimpleNamespace(kennung='x', optionen={'koerper': {'tiefe': 'an'}}, bilder=[], ergebnis={})

    def _wegraeumen(self):
        import shutil
        shutil.rmtree(self.ordner, ignore_errors=True)

    def _sichern(self, job=None, fotos=True):
        liste = [{'rolle': 'rechts', 'png': str(self.png)}] if fotos else []
        with mock.patch('core.dienste.engine2d3dkleidersegmentierung.Engine2d3dKleidersegmentierung.bilder_fuer', return_value=liste):
            return Netztiefe(job or self.job, self.ablage).sichern()

    def test_das_abgeleitete_netz_hat_dieselben_flaechen_und_ist_im_rumpf_flacher(self):
        bericht = self._sichern()
        self.assertTrue(bericht['aktiv'], bericht)
        original, neu = trimesh.load(str(self.original), force='mesh', process=False), trimesh.load(str(self.ordner / 'netz_tiefe.glb'), force='mesh', process=False)
        self.assertTrue(np.array_equal(np.asarray(original.faces), np.asarray(neu.faces)))
        self.assertEqual(len(original.vertices), len(neu.vertices))
        vorher = Seitentiefe.modell_profil(np.asarray(original.vertices), hoehen=(0.6,))[0.6]['tiefe']
        nachher = Seitentiefe.modell_profil(np.asarray(neu.vertices), hoehen=(0.6,))[0.6]['tiefe']
        self.assertLess(nachher, vorher * 0.95)
        self.assertGreaterEqual(nachher, vorher * 0.8 - 1e-3)                     # nie unter `tiefe_min`
        self.assertLess(bericht['staerkster_faktor'], 1.0)

    def test_ein_zweiter_aufruf_rechnet_nicht_neu(self):
        erster = self._sichern()
        zeit = (self.ordner / 'netz_tiefe.glb').stat().st_mtime_ns
        zweiter = self._sichern()
        self.assertEqual(zweiter['stand_zeit'], erster['stand_zeit'])
        self.assertEqual((self.ordner / 'netz_tiefe.glb').stat().st_mtime_ns, zeit)

    def test_ohne_option_oder_seitenfoto_steht_der_grund_im_zettel_und_es_gibt_kein_netz(self):
        aus = self._sichern(SimpleNamespace(kennung='x', optionen={'koerper': {'tiefe': 'aus'}}, bilder=[], ergebnis={}))
        self.assertFalse(aus['aktiv'])
        self.assertIn('aus', aus['grund'])
        ohne = self._sichern(fotos=False)
        self.assertFalse(ohne['aktiv'])
        self.assertIn('Seitenfoto', ohne['grund'])
        self.assertFalse((self.ordner / 'netz_tiefe.glb').exists())
        self.assertEqual(json.loads((self.ordner / 'netz_tiefe.json').read_text(encoding='utf-8'))['aktiv'], False)

    def test_ein_netz_das_nicht_tiefer_ist_als_das_foto_bleibt_ohne_ableitung(self):
        breit = self.ordner / 'seite_breit.png'
        maske = seitenmaske(lambda h: 0.6 * np.sqrt(max(0.0, 1.0 - (2.0 * h - 1.0) ** 2)))
        rgba = np.zeros(maske.shape + (4,), dtype=np.uint8)
        rgba[maske] = (120, 120, 120, 255)
        Image.fromarray(rgba, 'RGBA').save(breit)
        self.png = breit
        bericht = self._sichern()
        self.assertFalse(bericht['aktiv'])
        self.assertIn('nichts zu tun', bericht['grund'])


class DieAblage(SimpleTestCase):
    """`Engine2d3dKleiderablage.netzdatei`: das abgeleitete Netz nur, wenn es zu DIESEM Original gehört; `original=True` gibt immer das Original."""

    def setUp(self):
        self.ordner = Path(Pruefablage.wurzel()) / ('tiefenablage_%d' % os.getpid())
        (self.ordner / 'netz').mkdir(parents=True, exist_ok=True)
        (self.ordner / 'arbeit').mkdir(parents=True, exist_ok=True)
        self.addCleanup(lambda: __import__('shutil').rmtree(self.ordner, ignore_errors=True))
        self.original = self.ordner / 'netz' / 'mesh.glb'
        self.original.write_bytes(b'original')
        (self.ordner / 'arbeit' / 'netz_tiefe.glb').write_bytes(b'abgeleitet')
        self.ablage = Engine2d3dKleiderablage.__new__(Engine2d3dKleiderablage)
        self.ablage.netz = lambda name='': self.ordner / 'netz' / name if name else self.ordner / 'netz'
        self.ablage.arbeit = lambda name='': self.ordner / 'arbeit' / name if name else self.ordner / 'arbeit'
        self.ablage.kopf = lambda name='': self.ordner / 'kopf' / name if name else self.ordner / 'kopf'      # `netzdatei('kopf')` liest `kopf/mesh.glb`

    def _zettel(self, **felder):
        s = os.stat(self.original)
        (self.ordner / 'arbeit' / 'netz_tiefe.json').write_text(json.dumps(dict({'aktiv': True, 'quelle': [s.st_size, s.st_mtime_ns]}, **felder)), encoding='utf-8')

    def test_ohne_zettel_oder_bei_aus_gilt_das_original(self):
        self.assertEqual(self.ablage.netzdatei(), self.original)
        self._zettel(aktiv=False)
        self.assertEqual(self.ablage.netzdatei(), self.original)

    def test_mit_passendem_zettel_kommt_das_abgeleitete_und_mit_original_true_das_original(self):
        self._zettel()
        self.assertEqual(self.ablage.netzdatei().name, 'netz_tiefe.glb')
        self.assertEqual(self.ablage.netzdatei(original=True), self.original)
        self.assertIsNone(self.ablage.netzdatei('kopf'))

    def test_ein_neues_original_macht_den_zettel_ungueltig(self):
        self._zettel()
        self.original.write_bytes(b'ein ganz anderes netz')
        self.assertEqual(self.ablage.netzdatei(), self.original)

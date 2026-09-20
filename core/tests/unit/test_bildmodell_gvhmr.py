# -*- coding: utf-8 -*-
"""SMPL-X mit GVHMR für EIN Bild (20.09.2026) — Einzelschritt, Eintrag, Lage, Netz.

Edgar: „Die SMPL erkennung aus GVHMR ist doch ganz gut. Mach einen extra button
dafür in jeder Zeile mit der ich ein SMPL mit GVHMR erzeuge und ansehen kann,
für jedes Bild!" Ohne GVHMR, ohne Prozess:

1. `Bildmodelllauf.folge`: `schritte=['gvhmr']` ergibt diesen Schritt und danach
   Schätzung bis Vorschau (`NACH_GVHMR`, ohne Textur und Speichern) — vorher fiel
   ein unbekannter Schritt aus der Liste und der Lauf rechnete die ganze Kette
   (Sabotage im Test). Ein Lauf „ab ziel" enthält ihn nie. `melden` lässt den
   Balken beim Übergang 50 → 15 nicht zurückfallen.
2. `Bildmodellstart`: `schritte: ['gvhmr'], bild` → `ab = bis = gvhmr`,
   `optionen.gvhmr_bild`, Körperschätzer `gvhmr` und Weg `schaetzer`; ein Start
   ohne `bild` trägt nichts ein und stellt nichts um.
3. `Bildmodellgvhmr.eintrag`: Rohantwort → Feld `gvhmr` mit Netz, Höhe, Dauer,
   Stand, Kamera des Fotos (`kamera`: Netz in Kamerasicht, fx/fy/cx/cy, Fotogröße);
   Fehler → `fehler` mit Stand, ohne Netz.
4. `Smplxlage.aufstellen` (Wrapper, nur numpy): Becken über dem Ursprung, tiefster
   Punkt auf 0, Hüftachse rechts → links auf +x — auch wenn das Netz verdreht
   und verschoben hereinkommt. Sabotage: ohne die Drehung bliebe die Achse schief.
5. `netz3d`: Punkte, Dreiecke und — wenn abgelegt — das Rig (Gelenke, Eltern) und das Netz
   in der Kamera des Fotos (`kamera`) aus den `.npy` als base64, bitgleich zurück; ohne Netz
   `FileNotFoundError` mit dem Grund, ohne Kameradatei kein `kamera`.
"""

import base64
import math
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from django.test import SimpleTestCase, override_settings

from core.daten.bildmodellablage import Bildmodellablage
from core.daten.wrapperpfad import Wrapperpfad
from core.dienste.bildmodellgvhmr import Bildmodellgvhmr
from core.dienste.bildmodelllauf import Bildmodelllauf
from core.dienste.bildmodelloptionen import Bildmodelloptionen
from core.dienste.bildmodellstart import Bildmodellstart

with Wrapperpfad():
    from smplxlage import Smplxlage


class FolgeTest(SimpleTestCase):
    databases = set()

    #: Was auf den Einzelschritt folgt (Edgar, 20.09.2026: „Berechne auch die [Vorher/Nachher-
    #: Bilder] immer neu, mit dem GVHMR lauf") — bis Vorschau, ohne Textur und Speichern.
    KETTE = ['schaetzung', 'ziel', 'anpassung', 'rest', 'vorschau']

    def test_einzelschritt_mit_modell_danach(self):
        self.assertEqual(Bildmodelllauf.folge(schritte=['gvhmr']), ['gvhmr'] + self.KETTE)
        self.assertEqual(Bildmodelllauf.folge(schritte=['gvhmr', 'sichtung']),
                         ['sichtung', 'gvhmr'] + self.KETTE)
        # Was schon genannt ist, kommt nicht doppelt — und nie Textur oder Speichern.
        folge = Bildmodelllauf.folge(schritte=['gvhmr', 'vorschau'])
        self.assertEqual(folge, ['vorschau', 'gvhmr', 'schaetzung', 'ziel', 'anpassung', 'rest'])
        self.assertNotIn('textur', folge)
        self.assertNotIn('speichern', folge)

    def test_kette_ohne_einzelschritt(self):
        reihe = Bildmodelloptionen.REIHENFOLGE
        self.assertEqual(Bildmodelllauf.folge('ziel'), reihe[reihe.index('ziel'):])
        self.assertNotIn('gvhmr', Bildmodelllauf.folge())
        self.assertEqual(Bildmodelllauf.folge(schritte=['quatsch']), reihe)

    def test_sabotage_unbekannter_schritt_rechnete_alles(self):
        # So sah die alte Zeile aus — der Einzelschritt fiel heraus, die ganze Kette lief
        # (mit Sichtung und Textur); heute steht GVHMR vorn, dann Schätzung bis Vorschau.
        alt = [s for s in Bildmodelloptionen.REIHENFOLGE if s in {'gvhmr'}] or Bildmodelloptionen.REIHENFOLGE
        self.assertNotEqual(alt, Bildmodelllauf.folge(schritte=['gvhmr']))
        self.assertEqual(Bildmodelllauf.folge(schritte=['gvhmr'])[0], 'gvhmr')

    def test_balken_faellt_nach_gvhmr_nicht_zurueck(self):
        # GVHMR belegt 0–50, die Schätzung beginnt bei 15: `melden` hält den Stand.
        job = SimpleNamespace(progress=0, schritt='', progress_detail='', save=lambda **k: None)
        lauf = Bildmodelllauf.__new__(Bildmodelllauf)
        lauf.job = job
        lauf.melden('gvhmr', 1.0, 'fertig')
        self.assertEqual(job.progress, 50)
        lauf.melden('schaetzung', 0.0, 'beginnt')
        self.assertEqual((job.schritt, job.progress), ('schaetzung', 50))
        lauf.melden('vorschau', 1.0)
        self.assertEqual(job.progress, 94)


class StartTest(SimpleTestCase):
    databases = set()

    def test_schritte_und_bild(self):
        self.assertEqual(Bildmodellstart.schritte({'schritte': ['gvhmr'], 'bild': 'a.jpg'}),
                         ('gvhmr', 'gvhmr', ['gvhmr']))
        job = SimpleNamespace(optionen={'proportionen': {'taille_breite': 20}})
        optionen = Bildmodellstart.optionen(job, {'bild': 'a.jpg', 'neu': True})
        self.assertEqual((optionen['gvhmr_bild'], optionen['gvhmr_neu']), ('a.jpg', True))
        self.assertEqual(optionen['proportionen'], {'taille_breite': 20})
        self.assertNotIn('gvhmr_bild', Bildmodellstart.optionen(job, {}))

    def test_gvhmr_lauf_stellt_schaetzer_und_weg(self):
        # Mit `bild` rechnet der Lauf danach das Modell — aus GVHMR, nicht aus Silhouetten.
        job = SimpleNamespace(optionen={'koerper': 'smplest_x', 'weg': 'silhouette'})
        optionen = Bildmodellstart.optionen(job, {'bild': 'a.jpg'})
        self.assertEqual((optionen['koerper'], optionen['weg']), ('gvhmr', 'schaetzer'))
        # … und nichts formt das GVHMR-Ziel danach um (Umriss, Fotomaße, Popup-Eingaben aus).
        self.assertEqual((optionen['umriss'], optionen['fotomasse'], optionen['popup']),
                         ('aus', 'aus', 'aus'))
        # Ohne `bild` bleibt alles, wie es war.
        optionen = Bildmodellstart.optionen(job, {'ab': 'ziel'})
        self.assertEqual((optionen['koerper'], optionen['weg']), ('smplest_x', 'silhouette'))
        # Steht es schon, ändert sich nichts.
        fertig = {'koerper': 'gvhmr', 'weg': 'schaetzer', 'umriss': 'aus', 'fotomasse': 'aus', 'popup': 'aus'}
        self.assertEqual(Bildmodellstart.gvhmr_als_schaetzer(fertig), {})


class EintragTest(SimpleTestCase):
    databases = set()

    def test_antwort_wird_feld(self):
        roh = {'betas': [0.1] * 10, 'frames': 30, 'netz': 'x_gvhmr.npy', 'dreiecke': 'smplx_dreiecke.npy',
               'punkte': 10475, 'hoehe_m': 1.7613}
        e = Bildmodellgvhmr.eintrag(roh, 4.66)
        self.assertEqual((e['netz'], e['frames'], e['punkte'], e['hoehe_m'], e['dauer_s']),
                         ('x_gvhmr.npy', 30, 10475, 1.7613, 4.7))
        self.assertTrue(e['stand'])
        self.assertNotIn('fehler', e)

    def test_kamera_des_fotos_kommt_mit(self):
        # Seit 20.09. spät legt der Runner das Netz auch in der Kamera des Fotos ab (Edgar: „Immer das
        # 3D Modell in genau der gleichen pose und ausschnitt wie das 2D Bild!!!").
        roh = {'betas': [0.1] * 10, 'netz': 'x_gvhmr.npy', 'kamera': {
            'netz': 'x_gvhmr_kamera.npy', 'gelenke': 'x_gvhmr_kamera_gelenke.npy',
            'breite': 922, 'hoehe': 2626,
            'fx': 1543.8, 'fy': 1543.8, 'cx': 461.0, 'cy': 1313.0, 'unbekannt': 1}}
        e = Bildmodellgvhmr.eintrag(roh, 1.0)
        self.assertEqual(e['kamera'], {k: v for k, v in roh['kamera'].items() if k != 'unbekannt'})
        # Ein Lauf ohne Kamera (alt) oder ohne Brennweite trägt keine ein.
        self.assertNotIn('kamera', Bildmodellgvhmr.eintrag({'netz': 'x_gvhmr.npy'}, 1.0))
        self.assertNotIn('kamera', Bildmodellgvhmr.eintrag({'netz': 'x', 'kamera': {'netz': 'k.npy'}}, 1.0))

    def test_fehler_ohne_netz(self):
        e = Bildmodellgvhmr.eintrag({'error': 'Bild nicht lesbar'}, 0.2)
        self.assertEqual(e['fehler'], 'Bild nicht lesbar')
        self.assertNotIn('netz', e)
        self.assertEqual(Bildmodellgvhmr.eintrag(None)['fehler'], 'keine Antwort')


class LageTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _figur(winkel, versatz):
        """Ein Körper aus vier Punkten: Füße unten, Kopf oben, Hüften ±0,1 auf der x-Achse —
        dann um y gedreht und verschoben."""
        punkte = np.array([[0, 0, 0], [0, 1.7, 0], [0.1, 0.9, 0], [-0.1, 0.9, 0], [0, 0.9, 0.05]], float)
        gelenke = np.array([[0, 0.9, 0], [0.1, 0.9, 0], [-0.1, 0.9, 0]], float)  # Becken, links, rechts
        return Smplxlage.um_y(punkte, winkel) + versatz, Smplxlage.um_y(gelenke, winkel) + versatz

    def test_aufrecht_mittig_nach_vorn(self):
        punkte, gelenke = self._figur(math.radians(70), np.array([2.0, 0.3, -1.5]))
        aus, rig, hoehe = Smplxlage.aufstellen(punkte, gelenke)
        self.assertAlmostEqual(hoehe, 1.7, places=5)
        self.assertAlmostEqual(float(aus[:, 1].min()), 0.0, places=6)
        links, rechts = aus[2], aus[3]
        self.assertAlmostEqual(float(links[0] - rechts[0]), 0.2, places=5)
        self.assertAlmostEqual(float(links[2] - rechts[2]), 0.0, places=5)
        # Becken über dem Ursprung: x und z des Beckens sind 0 (Punkt 2/3 mitteln)
        self.assertAlmostEqual(float((links[0] + rechts[0]) / 2), 0.0, places=5)
        self.assertAlmostEqual(float(aus[4][2]), 0.05, places=5)  # der Bauch bleibt vorn (+z)
        self.assertEqual(aus.dtype, np.float32)
        # Das Rig geht denselben Weg: Becken bei (0, 0.9, 0), Hüften auf ±0,1 x
        self.assertTrue(np.allclose(rig[0], [0, 0.9, 0], atol=1e-5))
        self.assertTrue(np.allclose(rig[1], [0.1, 0.9, 0], atol=1e-5))
        self.assertEqual(rig.dtype, np.float32)

    def test_sabotage_ohne_drehung_bleibt_die_achse_schief(self):
        punkte, gelenke = self._figur(math.radians(70), np.zeros(3))
        ohne = punkte - gelenke[0]
        self.assertGreater(abs(float(ohne[2][2] - ohne[3][2])), 0.1)


class Netz3dTest(SimpleTestCase):
    databases = set()

    def test_base64_bitgleich_und_fehlend(self):
        with tempfile.TemporaryDirectory() as tmp:
            with override_settings(OBJECTS_ROOT=Path(tmp)):
                ablage = Bildmodellablage('2026.01.01.00.00.00')
                dienst = Bildmodellgvhmr(SimpleNamespace(), ablage)
                dienst.ordner().mkdir(parents=True)
                punkte = np.array([[0, 0, 0], [0, 1.6, 0.1], [0.2, 0.8, 0]], np.float32)
                dreiecke = np.array([[0, 1, 2]], np.uint32)
                np.save(dienst.ordner() / 'a_gvhmr.npy', punkte)
                np.save(dienst.ordner() / 'smplx_dreiecke.npy', dreiecke)
                eintrag = {'datei': 'a.jpg', 'gvhmr': {'netz': 'a_gvhmr.npy', 'hoehe_m': 1.6, 'betas': [1]}}
                aus = dienst.netz3d(eintrag)
                zurueck = np.frombuffer(base64.b64decode(aus['punkte']), np.float32).reshape(-1, 3)
                self.assertTrue(np.array_equal(zurueck, punkte))
                ecken = np.frombuffer(base64.b64decode(aus['dreiecke']), np.uint32).tolist()
                self.assertEqual(ecken, [0, 1, 2])
                self.assertEqual((aus['anzahl'], aus['hoehe_cm'], aus['datei']), (3, 160.0, 'a.jpg'))
                self.assertNotIn('gelenke', aus)  # ein Lauf vor dem Rig: kein Rig, kein Fehler
                # Mit Rig: Gelenke und Eltern kommen mit
                gelenke = np.array([[0, 0.9, 0], [0.1, 0.9, 0]], np.float32)
                np.save(dienst.ordner() / 'a_gvhmr_gelenke.npy', gelenke)
                eintrag['gvhmr'].update({'gelenke': 'a_gvhmr_gelenke.npy', 'eltern': [-1, 0]})
                aus = dienst.netz3d(eintrag)
                self.assertEqual(aus['eltern'], [-1, 0])
                rig = np.frombuffer(base64.b64decode(aus['gelenke']), np.float32).reshape(-1, 3)
                self.assertTrue(np.array_equal(rig, gelenke))
                with self.assertRaises(FileNotFoundError):
                    dienst.netz3d({'datei': 'b.jpg', 'gvhmr': {'fehler': 'kaputt'}})
                # Ohne Kameradatei: kein `kamera` — das Fenster zeigt die Weltlage und sagt „Neu rechnen".
                eintrag['gvhmr']['kamera'] = {'netz': 'a_gvhmr_kamera.npy', 'fx': 1500.0, 'fy': 1500.0,
                                              'cx': 461.0, 'cy': 1313.0, 'breite': 922, 'hoehe': 2626}
                self.assertIsNone(dienst.kamera(eintrag['gvhmr']))
                self.assertNotIn('kamera', dienst.netz3d(eintrag))
                # Mit Kameradatei: Punkte in Kamerasicht bitgleich, Brennweite und Fotogröße dabei.
                kamera = np.array([[0, -0.2, -1.2], [0, 1.4, -1.3], [0.2, 0.6, -1.2]], np.float32)
                np.save(dienst.ordner() / 'a_gvhmr_kamera.npy', kamera)
                aus = dienst.netz3d(eintrag)
                self.assertEqual((aus['kamera']['fx'], aus['kamera']['breite'], aus['kamera']['hoehe']),
                                 (1500.0, 922, 2626))
                sicht = np.frombuffer(base64.b64decode(aus['kamera']['punkte']), np.float32).reshape(-1, 3)
                self.assertTrue(np.array_equal(sicht, kamera))
                self.assertNotIn('gelenke', aus['kamera'])  # kein Kamera-Rig abgelegt: kein Fehler

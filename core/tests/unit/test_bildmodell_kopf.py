# -*- coding: utf-8 -*-
"""Kopf-Pipeline (22.09.2026): „Mach eine eigene Pipeline für den Kopf, wo ich FLAME und
KeenTools FaceBuilder auswählen kann, FLAME mit MICA und was es sonst noch gibt, und mehrere
Fotos auswählen kann für den Kopf." — und danach: „mach FaceBuilder OHNE Handarbeit im
Blender, automatisch, ggf. minimale Handarbeit in unserem UI" (die Verfahren laufen ohne
Runner in python10):

1. `Bildmodelllauf.folge`: der Schritt `kopf` steht zwischen Schätzung und Zielnetz, auch in
   der Kette nach dem Einzelschritt `gvhmr`.
2. `Bildmodellkopf.bilder`: Häkchen „Kopf" (`kopf_an`) zuerst, sonst ALLE Kopfbilder außer der
   Rückansicht (22.09.2026: das Hauptbild-Häkchen darf das nicht mehr auf eines verengen —
   Edgar: „warum ein Foto??"), sonst das Körperbild von vorn.
3. `Bildmodellkopf.mitteln`: zwei um Achse und Verschiebung versetzte, aber sonst gleiche
   „Köpfe" liefern nach dem Mitteln wieder denselben Kopf (Procrustes ohne Maßstab).
4. `_mica`/`_mehrbild`/`_pymafx` mit `_runner` gemockt: Ergebnis am Auftrag (`ergebnis.kopf`,
   `ergebnis.schaetzung.kopf`), Fehlerfall ohne Kopf wirft mit Hinweis, „Mehrbild" ignoriert
   `kopfmischung: erstes` (nutzt immer alle gewählten Fotos), `Bildmodellkopfkatalog` markiert
   MICA/Mehrbild als verfügbar/fehlend nach den Dateien (Mehrbild braucht kein MICA-Netz).
"""
import shutil
import tempfile
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase, TestCase, override_settings

from core.daten.bildmodellablage import Bildmodellablage
from core.dienste.bildmodellkopf import Bildmodellkopf
from core.dienste.bildmodellkopfkatalog import Bildmodellkopfkatalog
from core.dienste.bildmodelllauf import Bildmodelllauf
from core.models import Bildmodellauftrag


class FolgeTest(SimpleTestCase):
    databases = set()

    def test_kopf_zwischen_schaetzung_und_ziel(self):
        folge = Bildmodelllauf.folge()
        self.assertEqual(folge.index('kopf'), folge.index('schaetzung') + 1)
        self.assertLess(folge.index('kopf'), folge.index('ziel'))

    def test_kopf_nach_gvhmr_einzelschritt(self):
        folge = Bildmodelllauf.folge(schritte=['gvhmr'])
        self.assertIn('kopf', folge)
        self.assertLess(folge.index('gvhmr'), folge.index('kopf'))


class KopfkatalogTest(SimpleTestCase):
    databases = set()

    def test_felder_haben_mica_mehrbild_pymafx_keiner(self):
        werte = {w for w, _, _ in Bildmodellkopfkatalog.FELDER[0][2]}
        self.assertEqual(werte, {'mica', 'mehrbild', 'pymafx_flame', 'keiner'})

    def test_verfuegbarkeit_ohne_mica_ordner(self):
        with mock.patch.object(Bildmodellkopfkatalog, 'mica_ordner', return_value='/nirgends'):
            stand = Bildmodellkopfkatalog.verfuegbarkeit((True, ''))
        self.assertFalse(stand[('kopfverfahren', 'mica')][0])
        self.assertFalse(stand[('kopfverfahren', 'mehrbild')][0])
        self.assertEqual(stand[('kopfverfahren', 'pymafx_flame')], (True, ''))

    def test_mehrbild_braucht_kein_mica_netz(self):
        """Mehrbild kommt ohne `mica.tar` aus (nur FLAME2020 + insightface) — Damiras
        Einrichtung (22.09.2026) hat FLAME2020 und insightface, aber `mica.tar` separat."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'data' / 'FLAME2020').mkdir(parents=True)
            (Path(tmp) / 'data' / 'FLAME2020' / 'generic_model.pkl').write_bytes(b'x')
            with mock.patch.object(Bildmodellkopfkatalog, 'mica_ordner', return_value=tmp), \
                 mock.patch.object(Bildmodellkopfkatalog, 'INSIGHTFACE', tmp):   # Ordner existiert
                stand = Bildmodellkopfkatalog.verfuegbarkeit((True, ''))
        self.assertTrue(stand[('kopfverfahren', 'mehrbild')][0])
        self.assertFalse(stand[('kopfverfahren', 'mica')][0])
        self.assertIn('mica.tar', stand[('kopfverfahren', 'mica')][1])


def _bild(datei, kategorie='kopf', ansicht='vorne', hauptbild=False, kopf_an=None, video=False):
    return {'datei': datei, 'kategorie': kategorie, 'ansicht': ansicht, 'hauptbild': hauptbild,
            'kopf_an': kopf_an, 'video': video, 'nutzung': 'form_textur'}


class BilderauswahlTest(TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(dir=str(Path(__file__).parent)))
        self.settings_ = override_settings(OBJECTS_ROOT=self.tmp)
        self.settings_.enable()

    def tearDown(self):
        self.settings_.disable()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _dienst(self, bilder):
        job = Bildmodellauftrag.objects.create(kennung='2026.01.02.00.00.00', name='K', bilder=bilder)
        return Bildmodellkopf(job, Bildmodellablage(job.kennung), {})

    def test_haekchen_geht_vor(self):
        # Reihenfolge nach `Bildmodellfotolinien.REIHE`: Körperbilder vor Kopfbildern.
        bilder = [_bild('a.jpg', hauptbild=True), _bild('b.jpg', kopf_an=True),
                  _bild('c.jpg', kategorie='koerper', ansicht='vorne', kopf_an=True)]
        aus = self._dienst(bilder).bilder()
        self.assertEqual([b['datei'] for b in aus], ['c.jpg', 'b.jpg'])

    def test_ohne_haekchen_hauptbild_engt_nicht_ein(self):
        """Vorher griff hier fälschlich nur das Kopf-Hauptbild, auch mit weiteren Kopffotos ohne
        Häkchen daneben (Edgar, 22.09.2026: „warum ein Foto??" — „Mehrbild" braucht gerade
        mehrere Ansichten). Nur die Rückansicht fällt raus, das Hauptbild-Häkchen ist hier egal."""
        bilder = [_bild('a.jpg', hauptbild=False), _bild('b.jpg', hauptbild=True),
                  _bild('c.jpg', ansicht='hinten', hauptbild=True)]
        aus = {b['datei'] for b in self._dienst(bilder).bilder()}
        self.assertEqual(aus, {'a.jpg', 'b.jpg'})

    def test_ohne_hauptbild_alle_kopfbilder_ausser_hinten(self):
        bilder = [_bild('a.jpg', ansicht='hinten'), _bild('b.jpg', ansicht='vorne'),
                  _bild('c.jpg', ansicht='dreiviertel')]
        aus = {b['datei'] for b in self._dienst(bilder).bilder()}
        self.assertEqual(aus, {'b.jpg', 'c.jpg'})

    def test_rueckfall_koerperbild_von_vorn(self):
        bilder = [_bild('a.jpg', kategorie='koerper', ansicht='vorne'),
                  _bild('v.mp4', kategorie='kopf', video=True)]
        aus = self._dienst(bilder).bilder()
        self.assertEqual([b['datei'] for b in aus], ['a.jpg'])

    def test_keine_videos(self):
        bilder = [_bild('a.mp4', video=True, kopf_an=True)]
        self.assertEqual(self._dienst(bilder).bilder(), [])


class MittelnTest(SimpleTestCase):
    databases = set()

    def test_gemittelter_kopf_gleich_bei_starrer_bewegung(self):
        rng = np.random.default_rng(1)
        kopf = rng.normal(0, 0.05, (50, 3)).astype(np.float32)
        r = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])   # 90° um z
        bewegt = kopf @ r.T + np.array([1.0, 2.0, 3.0])
        mittel = Bildmodellkopf.mitteln([kopf, bewegt])
        # Auf den ersten Kopf gelegt: das Mittel liegt (nach der Anlage in `mitteln`) im
        # Koordinatensystem des ersten Kopfs — Abstand zu `kopf` selbst klein.
        self.assertLess(float(np.abs(mittel - kopf).max()), 1e-4)


class _RunnerAntworten:
    def __init__(self, antworten):
        self.antworten = antworten
        self.aufrufe = []

    def __call__(self, art, *argumente):
        self.aufrufe.append((art, argumente))
        return self.antworten[art]


def _maske(pfad, form=(5023, 3)):
    pfad.parent.mkdir(parents=True, exist_ok=True)
    np.save(pfad, np.zeros(form, dtype=np.float32))


class KopfLaufTest(TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(dir=str(Path(__file__).parent)))
        self.settings_ = override_settings(OBJECTS_ROOT=self.tmp)
        self.settings_.enable()
        self.job = Bildmodellauftrag.objects.create(
            kennung='2026.01.03.00.00.00', name='K',
            bilder=[_bild('a.jpg', kopf_an=True), _bild('b.jpg', kopf_an=True)])
        self.ablage = Bildmodellablage(self.job.kennung)
        (self.ablage.zuschnitt()).mkdir(parents=True, exist_ok=True)
        for datei in ('a.jpg', 'b.jpg'):
            (self.ablage.zuschnitt() / datei).write_bytes(b'x')

    def tearDown(self):
        self.settings_.disable()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_mica_traegt_kopf_ein(self):
        _maske(self.ablage.schaetzung() / 'kopf_mica_flame.npy')
        antwort = {'mica': {
            'ok': True, 'dauer_s': 1.0,
            'bilder': {'a.jpg': {'ok': True, 'det_score': 0.9, 'netz': 'a_mica_flame.npy'},
                      'b.jpg': {'ok': False, 'fehler': 'kein Gesicht gefunden'}},
            'mittel': {'netz': 'kopf_mica_flame.npy', 'code': 'kopf_mica_code.npy', 'anzahl': 1},
        }}
        dienst = Bildmodellkopf(self.job, self.ablage, {'kopfverfahren': 'mica'})
        with mock.patch.object(dienst, '_runner', _RunnerAntworten(antwort)):
            aus = dienst.ausfuehren()
        self.assertEqual(aus['netz'], 'kopf_mica_flame.npy')
        self.assertEqual(aus['punkte'], 5023)
        self.assertEqual(sum(1 for b in aus['bilder'] if b['ok']), 1)
        self.job.refresh_from_db()
        self.assertEqual(self.job.ergebnis['kopf']['netz'], 'kopf_mica_flame.npy')
        self.assertEqual(self.job.ergebnis['schaetzung']['kopf'], 'kopf_mica_flame.npy')

    def test_mica_ohne_treffer_wirft_mit_hinweis(self):
        antwort = {'mica': {'ok': False, 'error': 'auf keinem Bild ein Gesicht',
                            'bilder': {'a.jpg': {'ok': False, 'fehler': 'kein Gesicht gefunden'},
                                      'b.jpg': {'ok': False, 'fehler': 'kein Gesicht gefunden'}},
                            'mittel': None}}
        dienst = Bildmodellkopf(self.job, self.ablage, {'kopfverfahren': 'mica'})
        with mock.patch.object(dienst, '_runner', _RunnerAntworten(antwort)):
            aus = dienst.ausfuehren()
        self.assertIn('fehler', aus)
        self.assertIsNone(aus['netz'])
        self.job.refresh_from_db()
        self.assertIn('fehler', self.job.ergebnis['kopf'])

    def test_keiner_ohne_lauf(self):
        dienst = Bildmodellkopf(self.job, self.ablage, {'kopfverfahren': 'keiner'})
        aus = dienst.ausfuehren()
        self.assertIsNone(aus['netz'])
        self.assertIn('hinweis', aus)

    def test_mehrbild_traegt_kopf_ein_ohne_blender(self):
        """Automatisch — keine ZIP-/Upload-Schritte, nur der Runner mit den zwei Fotos."""
        _maske(self.ablage.schaetzung() / 'kopf_mehrbild_flame.npy')
        antwort = {'mehrbild': {
            'ok': True, 'netz': 'kopf_mehrbild_flame.npy', 'code': 'kopf_mehrbild_code.npy',
            'anzahl': 2, 'fehler_prozent': 2.4, 'spiegel_x': False, 'dauer_s': 76.1,
            'bilder': {'a.jpg': {'ok': True, 'det_score': 0.81, 'fehler_prozent': 2.06},
                      'b.jpg': {'ok': True, 'det_score': 0.89, 'fehler_prozent': 2.92}},
        }}
        dienst = Bildmodellkopf(self.job, self.ablage, {'kopfverfahren': 'mehrbild'})
        with mock.patch.object(dienst, '_runner', _RunnerAntworten(antwort)):
            aus = dienst.ausfuehren()
        self.assertEqual(aus['netz'], 'kopf_mehrbild_flame.npy')
        self.assertEqual(aus['anpassung']['fehler_prozent'], 2.4)
        self.assertEqual(sum(1 for b in aus['bilder'] if b['ok']), 2)
        self.job.refresh_from_db()
        self.assertEqual(self.job.ergebnis['kopf']['netz'], 'kopf_mehrbild_flame.npy')

    def test_mehrbild_ohne_gesicht_wirft_mit_grund(self):
        antwort = {'mehrbild': {'ok': False, 'error': 'auf keinem Foto ein Gesicht',
                                'bilder': {'a.jpg': {'ok': False, 'fehler': 'kein Gesicht gefunden'},
                                          'b.jpg': {'ok': False, 'fehler': 'kein Gesicht gefunden'}}}}
        dienst = Bildmodellkopf(self.job, self.ablage, {'kopfverfahren': 'mehrbild'})
        with mock.patch.object(dienst, '_runner', _RunnerAntworten(antwort)):
            aus = dienst.ausfuehren()
        self.assertIn('fehler', aus)
        self.assertIsNone(aus['netz'])

    def test_mehrbild_ignoriert_kopfmischung_erstes(self):
        """`kopfmischung: erstes` gilt für MICA/PyMAF-X, nicht für Mehrbild — das nutzt immer
        alle gewählten Fotos (der ganze Zweck der Bündelausgleichung)."""
        _maske(self.ablage.schaetzung() / 'kopf_mehrbild_flame.npy')
        antwort = {'mehrbild': {'ok': True, 'netz': 'kopf_mehrbild_flame.npy', 'anzahl': 2,
                                'bilder': {'a.jpg': {'ok': True}, 'b.jpg': {'ok': True}}}}
        dienst = Bildmodellkopf(self.job, self.ablage,
                                {'kopfverfahren': 'mehrbild', 'kopfmischung': 'erstes'})
        runner = _RunnerAntworten(antwort)
        with mock.patch.object(dienst, '_runner', runner):
            dienst.ausfuehren()
        # Beide Fotos wurden dem Runner übergeben, nicht nur das erste.
        self.assertEqual(len(runner.aufrufe[0][1]) - 1, 2)   # Ordner + 2 Bildpfade

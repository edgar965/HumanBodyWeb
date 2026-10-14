# -*- coding: utf-8 -*-
"""Die schneller gemachten Teile von „Mesh to 3D" (12.10.2026, `meshfigur-tempo.md`): dieselben Ergebnisse wie die Rechnung davor — Kunstdaten, kleine Netze.

* `G9teilbindung.baum` (Baum je INHALT gemerkt, nicht je Adresse),
* `Meshfigurrunner._genesis_stempel`/`_stand_gehoert_zu` (die Nachhaltung wird nur wiederholt, wenn die Figur eine andere ist),
* `Meshfigurkinematik.drehmatrix` (Rodrigues ohne Host-Sync) gegen `scipy`s Rotationsvektor,
* `Meshfigurgpusuche` (Kasten-Vorauswahl) gegen den KD-Baum — nur mit torch, CUDA und pytorch3d (python10); sonst übersprungen.

NICHT gelaufen (Tests nur auf Ansage). Sabotagen: `baum` mit `id(koerperpunkte)` statt `hash(…tobytes())` im Schlüssel macht `test_baum_folgt_dem_inhalt_nicht_der_adresse` rot; in `_genesis_stempel` die Dateibytes statt der Arrays hashen
macht `test_stempel_ist_der_inhalt_nicht_die_datei` rot (np.savez schreibt die Zeit in das Zip).
"""

import importlib.util
import json
import os
import unittest
from unittest import mock

import numpy as np

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()


def _torch_cuda():
    return importlib.util.find_spec('torch') is not None and importlib.util.find_spec('pytorch3d') is not None


class TeilbindungBaumTest(unittest.TestCase):
    def setUp(self):
        from Genesis9.teilbindung import G9teilbindung

        self.klasse = G9teilbindung
        self.klasse._baeume.clear()

    def test_gleicher_inhalt_gleicher_baum_und_gleiche_antwort(self):
        from scipy.spatial import cKDTree

        z = np.random.default_rng(1)
        koerper, anfragen = z.normal(size=(500, 3)), z.normal(size=(40, 3))
        idx = np.arange(0, 500, 3)
        a, b = self.klasse.baum(koerper, idx), self.klasse.baum(koerper.copy(), idx.copy())
        self.assertIs(a, b)
        ref = cKDTree(koerper[idx]).query(anfragen, k=3)
        gemerkt = a.query(anfragen, k=3, workers=-1)
        self.assertTrue(np.array_equal(ref[1], gemerkt[1]) and np.array_equal(ref[0], gemerkt[0]))

    def test_baum_folgt_dem_inhalt_nicht_der_adresse(self):
        z = np.random.default_rng(2)
        koerper = z.normal(size=(300, 3))
        alt = self.klasse.baum(koerper)
        koerper[:] = z.normal(size=(300, 3))            # dieselbe Adresse, anderer Inhalt
        neu = self.klasse.baum(koerper)
        self.assertIsNot(alt, neu)
        self.assertTrue(np.array_equal(neu.data, koerper))

    def test_andere_auswahl_anderer_baum_und_die_ablage_bleibt_begrenzt(self):
        koerper = np.random.default_rng(3).normal(size=(200, 3))
        self.assertIsNot(self.klasse.baum(koerper, np.arange(50)), self.klasse.baum(koerper, np.arange(60)))
        for n in range(self.klasse.BAEUME + 5):
            self.klasse.baum(koerper, np.arange(10, 10 + n % 150 + 1))
        self.assertLessEqual(len(self.klasse._baeume), self.klasse.BAEUME)


class _Teil:
    """Ein Ersatz für einen Folger: picklebar, mit `projektion()` wie der echte (`G9teileablage` ruft sie vor dem Ablegen)."""

    def __init__(self, nummer):
        self.nummer = nummer
        self.projiziert = False

    def projektion(self):
        self.projiziert = True


class TeileablageTest(unittest.TestCase):
    def setUp(self):
        from Genesis9.teileablage import G9teileablage

        self.klasse = G9teileablage
        self._ordner_alt = G9teileablage.__dict__['_ordner']
        self.klasse.vergessen()
        self.klasse._sperren.clear()

    def tearDown(self):
        self.klasse._ordner = self._ordner_alt          # `_holen` biegt den Ablageordner auf die Prüfablage um
        self.klasse.vergessen()

    def _holen(self, ordner, quelle, art='haar', fassung='1', kennung='k', bauen=None):
        from pathlib import Path

        self.klasse._ordner = classmethod(lambda cls: Path(ordner))
        zaehler = self.zaehler = getattr(self, 'zaehler', [])
        bauen = bauen or (lambda: zaehler.append(1) or [(_Teil(len(zaehler)), None)])
        # Der Bestandsschlüssel (`G9listenablage.schluessel`) rechnet die Quelle relativ zu ihrer Wurzel (Daz-Bibliothek oder eigene Bibliothek); die Prüfablage ist die eigene Wurzel.
        with mock.patch('Genesis9.pfade.G9pfade.eigene', return_value=Path(ordner)):
            return self.klasse.holen(kennung, art, lambda: [Path(quelle)], fassung, bauen)

    def test_haar_wird_einmal_gebaut_und_dann_von_der_platte_geladen_wenn_der_bestand_gleich_ist(self):
        with Pruefablage.ordner() as ordner:
            quelle = os.path.join(ordner, 'quelle.duf')
            with open(quelle, 'w', encoding='utf-8') as f:
                f.write('eins')
            erst = self._holen(ordner, quelle)
            self.assertEqual(len(self.zaehler), 1)
            self.assertTrue(erst[0][0].projiziert)                     # die Projektion gehört in die Ablage
            self.klasse.vergessen()                                     # „neuer Prozess"
            zweit = self._holen(ordner, quelle)
            self.assertEqual(len(self.zaehler), 1)                      # nicht noch einmal gebaut
            self.assertEqual(zweit[0][0].nummer, 1)
            self.assertIsNot(zweit[0][0], erst[0][0])                   # eine Kopie von der Platte
            self.assertEqual(self._holen(ordner, quelle)[0][0].nummer, 1)   # im Prozess aus dem Speicher
            self.assertEqual(len(self.zaehler), 1)

    def test_geaenderter_bestand_oder_fassung_oder_code_baut_neu(self):
        with Pruefablage.ordner() as ordner:
            quelle = os.path.join(ordner, 'quelle.duf')
            with open(quelle, 'w', encoding='utf-8') as f:
                f.write('eins')
            self._holen(ordner, quelle)
            self.klasse.vergessen()
            with open(quelle, 'w', encoding='utf-8') as f:
                f.write('zwei und länger')
            self._holen(ordner, quelle)
            self.assertEqual(len(self.zaehler), 2)                      # Größe der Quelle geändert
            self.klasse.vergessen()
            self._holen(ordner, quelle, fassung='2')
            self.assertEqual(len(self.zaehler), 3)                      # Fassung der Garderobe geändert
            self.klasse.vergessen()
            self.klasse._code = 'anderer-code'                          # Code von Genesis9 geändert
            self._holen(ordner, quelle, fassung='2')
            self.assertEqual(len(self.zaehler), 4)

    def test_kleidung_wird_nie_abgelegt_und_eine_beschaedigte_datei_baut_neu(self):
        with Pruefablage.ordner() as ordner:
            quelle = os.path.join(ordner, 'quelle.duf')
            with open(quelle, 'w', encoding='utf-8') as f:
                f.write('eins')
            self._holen(ordner, quelle, art='kleidung')
            self._holen(ordner, quelle, art='kleidung')
            self.assertEqual(len(self.zaehler), 2)                      # jedes Mal gebaut, kein Speicher
            self.assertEqual(os.listdir(ordner), ['quelle.duf'])         # nichts abgelegt
            self._holen(ordner, quelle)
            self.klasse.vergessen()
            with open(os.path.join(ordner, 'k.pkl'), 'wb') as f:
                f.write(b'kaputt')
            self._holen(ordner, quelle)
            self.assertEqual(len(self.zaehler), 4)                      # unlesbar → neu gebaut (und neu abgelegt)

    def test_der_aufrufer_bekommt_eine_eigene_liste(self):
        with Pruefablage.ordner() as ordner:
            quelle = os.path.join(ordner, 'quelle.duf')
            with open(quelle, 'w', encoding='utf-8') as f:
                f.write('eins')
            a = self._holen(ordner, quelle)
            a.append('fremd')
            self.assertEqual(len(self._holen(ordner, quelle)), 1)


class DauerlaufTest(unittest.TestCase):
    """Die Kindseite des Dauerprozesses (`Meshfigurdauerlauf.laufen`): Befehle von stdin, `[ende]` nach jedem Schritt, Ende bei `ende`, Fehler beendet mit Exitcode 1."""

    @staticmethod
    def _lauf(eingabe, runner):
        import contextlib
        import io

        from meshfigur_dauerlauf import Meshfigurdauerlauf

        aus, fehler = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(aus), contextlib.redirect_stderr(fehler):
            code = Meshfigurdauerlauf.laufen(runner, io.StringIO(eingabe))
        return code, aus.getvalue().splitlines()

    def test_jeder_schritt_endet_mit_einer_endemarke_und_ende_beendet(self):
        gerechnet = []

        class Runner:
            def __init__(self, auftrag, schritt, runde):
                gerechnet.append((auftrag, schritt, runde))

            def ausfuehren(self):
                print('[ergebnis] {}')

        code, zeilen = self._lauf('{"auftrag": "a.json", "schritt": "koerper", "runde": 2}\n\n{"auftrag": "a.json", "schritt": "rest"}\nende\n{"auftrag": "x", "schritt": "nie"}\n', Runner)
        self.assertEqual(code, 0)
        self.assertEqual(gerechnet, [('a.json', 'koerper', 2), ('a.json', 'rest', 1)])          # Runde fehlt → 1; nach „ende" nichts mehr
        self.assertEqual(zeilen, ['[ergebnis] {}', '[ende] koerper', '[ergebnis] {}', '[ende] rest'])

    def test_ein_fehler_meldet_und_beendet_den_prozess(self):
        class Runner:
            def __init__(self, auftrag, schritt, runde):
                pass

            def ausfuehren(self):
                raise ValueError('kaputt')

        code, zeilen = self._lauf('{"auftrag": "a.json", "schritt": "koerper"}\n{"auftrag": "a.json", "schritt": "rest"}\n', Runner)
        self.assertEqual(code, 1)
        self.assertEqual(zeilen, ['[fehler] {"fehler": "kaputt"}', '[ende] fehler'])                  # der zweite Befehl wird nicht mehr gelesen


class AbstimmnetzTest(unittest.TestCase):
    """`Blendimportsegmentierung._abstimmnetz`: das Abstimm-Netz wird nur gebaut, wenn Netz, Maße oder Fassung sich geändert haben."""

    def _segmentierung(self, ordner):
        from pathlib import Path

        from core.dienste.blendimportsegmentierung import Blendimportsegmentierung

        s = Blendimportsegmentierung.__new__(Blendimportsegmentierung)
        s.ordner = lambda: Path(ordner)
        s._netz = Path(ordner) / 'abstimmnetz.glb'
        return s

    def _bauen_zaehlen(self, ordner):
        from core.dienste.mesh3dnetzansicht import Mesh3dnetzansicht

        gebaut = []

        def vereinfachen(quelle, ziel, flaechen=None, farben=True):
            gebaut.append((str(quelle), flaechen))
            with open(ziel, 'wb') as f:
                f.write(b'glb')
            return 150_000, 74_961

        original = Mesh3dnetzansicht.vereinfachen
        Mesh3dnetzansicht.vereinfachen = staticmethod(vereinfachen)
        self.addCleanup(setattr, Mesh3dnetzansicht, 'vereinfachen', original)
        return gebaut

    def test_gleiches_netz_gleiche_masse_wird_nicht_noch_einmal_gebaut(self):
        with Pruefablage.ordner() as ordner:
            glb = os.path.join(ordner, 'koerper.glb')
            with open(glb, 'wb') as f:
                f.write(b'1234567890')
            gebaut = self._bauen_zaehlen(ordner)
            s = self._segmentierung(ordner)
            self.assertEqual(tuple(s._abstimmnetz(glb)), (150_000, 74_961))
            self.assertEqual(tuple(s._abstimmnetz(glb)), (150_000, 74_961))        # aus dem Vermerk, dieselben Zahlen
            self.assertEqual(len(gebaut), 1)

    def test_anderes_netz_andere_masse_oder_fehlende_datei_baut_neu(self):
        with Pruefablage.ordner() as ordner:
            glb = os.path.join(ordner, 'koerper.glb')
            with open(glb, 'wb') as f:
                f.write(b'1234567890')
            gebaut = self._bauen_zaehlen(ordner)
            s = self._segmentierung(ordner)
            s._abstimmnetz(glb)
            with open(glb, 'wb') as f:
                f.write(b'12345678901')                                             # anderes Netz (Größe)
            s._abstimmnetz(glb)
            self.assertEqual(len(gebaut), 2)
            s.PROXY_FLAECHEN = 100_000                                              # andere Maße
            s._abstimmnetz(glb)
            self.assertEqual(len(gebaut), 3)
            s._netz.unlink()                                                        # Datei weg, Vermerk bleibt
            s._abstimmnetz(glb)
            self.assertEqual(len(gebaut), 4)

    def test_ein_kaputter_vermerk_gilt_nicht(self):
        with Pruefablage.ordner() as ordner:
            glb = os.path.join(ordner, 'koerper.glb')
            with open(glb, 'wb') as f:
                f.write(b'1234567890')
            gebaut = self._bauen_zaehlen(ordner)
            s = self._segmentierung(ordner)
            s._abstimmnetz(glb)
            with open(os.path.join(ordner, 'abstimmnetz.json'), 'w', encoding='utf-8') as f:
                f.write('{kaputt')
            s._abstimmnetz(glb)
            self.assertEqual(len(gebaut), 2)


class _Daten:
    """Nur `datei(name)` — wie `Meshfigurdaten`: ein Name im Arbeitsordner."""

    def __init__(self, ordner):
        self.ordner = ordner

    def datei(self, name, art='arbeit'):
        return os.path.join(self.ordner, name)


class StandUndStempelTest(unittest.TestCase):
    def _runner(self, ordner):
        from _run_meshfigur import Meshfigurrunner

        r = Meshfigurrunner.__new__(Meshfigurrunner)
        r.daten = _Daten(ordner)
        return r

    @staticmethod
    def _figur(ordner, name='genesis_ende.npz', scale=1.0, zeit=(2020, 1, 1, 0, 0, 0)):
        """Wie `np.savez`, aber mit der Zeit der Zip-Einträge von Hand: zwei Dateien mit gleichem Inhalt und verschiedenen Bytes, ohne zu warten."""
        import io
        import zipfile

        arrays = {'punkte': np.arange(30, dtype=np.float32).reshape(10, 3) * scale, 'namen': np.array(['a', 'bb']), 'eltern': np.array([-1, 0])}
        with zipfile.ZipFile(os.path.join(ordner, name), 'w') as z:
            for schluessel, a in arrays.items():
                puffer = io.BytesIO()
                np.save(puffer, a)
                z.writestr(zipfile.ZipInfo(schluessel + '.npy', date_time=zeit), puffer.getvalue())

    def test_stempel_ist_der_inhalt_nicht_die_datei(self):
        with Pruefablage.ordner() as ordner:
            r = self._runner(ordner)
            self._figur(ordner, zeit=(2020, 1, 1, 0, 0, 0))
            erst = r._genesis_stempel('genesis_ende.npz')
            with open(os.path.join(ordner, 'genesis_ende.npz'), 'rb') as f:
                bytes_erst = f.read()
            self._figur(ordner, zeit=(2026, 10, 12, 3, 30, 10))     # derselbe Inhalt, andere Zeit im Zip
            with open(os.path.join(ordner, 'genesis_ende.npz'), 'rb') as f:
                self.assertNotEqual(bytes_erst, f.read())
            self.assertEqual(erst, r._genesis_stempel('genesis_ende.npz'))
            self._figur(ordner, scale=1.0001)
            self.assertNotEqual(erst, r._genesis_stempel('genesis_ende.npz'))

    def test_der_stand_gehoert_nur_zur_figur_fuer_die_er_gerechnet_wurde(self):
        with Pruefablage.ordner() as ordner:
            r = self._runner(ordner)
            self._figur(ordner)
            self.assertFalse(r._stand_gehoert_zu('genesis_ende.npz'))               # kein Vermerk, kein Zustand
            np.savez(os.path.join(ordner, r.ZUSTAND), theta=np.zeros((2, 3)), rg=np.zeros(3), tg=np.zeros(3))
            self.assertFalse(r._stand_gehoert_zu('genesis_ende.npz'))               # Zustand ohne Vermerk
            with open(os.path.join(ordner, r.GENESIS_STAND), 'w', encoding='utf-8') as f:
                json.dump({'datei': 'genesis_ende.npz', 'sha1': r._genesis_stempel('genesis_ende.npz')}, f)
            self.assertTrue(r._stand_gehoert_zu('genesis_ende.npz'))
            self.assertFalse(r._stand_gehoert_zu('genesis_gesicht.npz'))            # anderer Name
            self._figur(ordner, scale=2.0)                                          # andere Figur unter demselben Namen
            self.assertFalse(r._stand_gehoert_zu('genesis_ende.npz'))

    def test_ein_kaputter_vermerk_gilt_nicht(self):
        with Pruefablage.ordner() as ordner:
            r = self._runner(ordner)
            self._figur(ordner)
            np.savez(os.path.join(ordner, r.ZUSTAND), theta=np.zeros((2, 3)), rg=np.zeros(3), tg=np.zeros(3))
            with open(os.path.join(ordner, r.GENESIS_STAND), 'w', encoding='utf-8') as f:
                f.write('{kaputt')
            self.assertFalse(r._stand_gehoert_zu('genesis_ende.npz'))

    def test_die_haltung_gilt_auch_fuer_die_figur_mit_eigenmorph(self):
        """13.10.2026: der Eigenmorph ändert nur die Punkte der Ruhelage. Der Haltungsstempel lässt sie aus — die Haltung des Rest-Schritts gilt für die Figur mit Eigenmorph (statt einer zweiten Anpassung, die die Glieder
        um 6 mm verschob und die Untergrenze unter Stoff verlor). Eine andere Gelenkkette oder andere Gewichte ändern den Stempel weiter. Sabotage: `FORM = ()` → der erste Fall wird rot."""
        with Pruefablage.ordner() as ordner:
            r = self._runner(ordner)
            self._figur(ordner)
            np.savez(os.path.join(ordner, r.ZUSTAND), theta=np.zeros((2, 3)), rg=np.zeros(3), tg=np.zeros(3))
            with open(os.path.join(ordner, r.GENESIS_STAND), 'w', encoding='utf-8') as f:
                json.dump({'datei': 'genesis_ende.npz', 'sha1': r._genesis_stempel('genesis_ende.npz'), 'sha1_haltung': r._genesis_stempel('genesis_ende.npz', ohne=r.FORM)}, f)
            voll, haltung = r._genesis_stempel('genesis_ende.npz'), r._genesis_stempel('genesis_ende.npz', ohne=r.FORM)
            self._figur(ordner, scale=1.3)                                          # dieselbe Haltung, andere Form (Eigenmorph)
            self.assertNotEqual(voll, r._genesis_stempel('genesis_ende.npz'))
            self.assertEqual(haltung, r._genesis_stempel('genesis_ende.npz', ohne=r.FORM))
            self.assertTrue(r._stand_gehoert_zu('genesis_ende.npz'))
            arrays = {'punkte': np.arange(30, dtype=np.float32).reshape(10, 3), 'namen': np.array(['a', 'bb']), 'eltern': np.array([-1, 1])}   # andere Gelenkkette
            np.savez(os.path.join(ordner, 'genesis_ende.npz'), **arrays)
            self.assertFalse(r._stand_gehoert_zu('genesis_ende.npz'))

    def test_ein_vermerk_ohne_haltungsstempel_gilt_nur_bei_gleichem_inhalt(self):
        """Vermerke vor dem 13.10.2026 tragen nur `sha1` — dann gilt die alte Regel (genau diese Figur)."""
        with Pruefablage.ordner() as ordner:
            r = self._runner(ordner)
            self._figur(ordner)
            np.savez(os.path.join(ordner, r.ZUSTAND), theta=np.zeros((2, 3)), rg=np.zeros(3), tg=np.zeros(3))
            with open(os.path.join(ordner, r.GENESIS_STAND), 'w', encoding='utf-8') as f:
                json.dump({'datei': 'genesis_ende.npz', 'sha1': r._genesis_stempel('genesis_ende.npz')}, f)
            self.assertTrue(r._stand_gehoert_zu('genesis_ende.npz'))
            self._figur(ordner, scale=1.3)
            self.assertFalse(r._stand_gehoert_zu('genesis_ende.npz'))


@unittest.skipUnless(_torch_cuda(), 'torch/pytorch3d fehlen in diesem Interpreter (python10-Tests)')
class DrehmatrixTest(unittest.TestCase):
    def test_gegen_den_rotationsvektor_von_scipy_auch_bei_null_und_winzigen_winkeln(self):
        import torch
        from meshfigur_kinematik import Meshfigurkinematik
        from scipy.spatial.transform import Rotation

        z = np.random.default_rng(4)
        faelle = [np.zeros(3), np.array([1e-6, 0, 0]), np.array([0, 3e-4, 0]), np.array([0.3, 0.2, -0.4]), np.array([3.0, 0, 0])]
        faelle += [z.normal(size=3) * s for s in (0.001, 0.01, 0.1, 1.0) for _ in range(20)]
        for v in faelle:
            ist = Meshfigurkinematik.drehmatrix(torch.tensor(v, dtype=torch.float32)).numpy()
            soll = Rotation.from_rotvec(v).as_matrix()
            self.assertLess(float(np.abs(ist - soll).max()), 2e-6, v)

    def test_ableitung_ist_endlich_auch_bei_null(self):
        import torch
        from meshfigur_kinematik import Meshfigurkinematik

        for v in (np.zeros(3), np.array([1e-7, 0, 0]), np.array([0.2, 0.1, 0.0])):
            a = torch.tensor(v, dtype=torch.float32, requires_grad=True)
            Meshfigurkinematik.drehmatrix(a).sum().backward()
            self.assertTrue(bool(torch.isfinite(a.grad).all()), v)


@unittest.skipUnless(_torch_cuda(), 'torch/pytorch3d fehlen in diesem Interpreter (python10-Tests)')
class GpusucheKastenTest(unittest.TestCase):
    def test_gleiche_nachbarn_wie_der_kd_baum_und_der_rueckfall_fuer_ferne_anfragen(self):
        import torch

        if not torch.cuda.is_available():
            self.skipTest('keine CUDA-GPU')
        from meshfigur_gpusuche import Meshfigurgpusuche
        from scipy.spatial import cKDTree

        z = np.random.default_rng(5)
        w, y = z.uniform(0, 2 * np.pi, 200_000), z.uniform(0, 1.8, 200_000)
        proben = np.c_[0.2 * np.cos(w), y, 0.2 * np.sin(w)]
        n = Meshfigurgpusuche.KASTEN_AB * 2
        nah = np.c_[0.2 * np.cos(w[:n]) * 0.97, y[:n], 0.2 * np.sin(w[:n]) * 0.97]          # 6 mm hinter der Fläche
        fern = np.array([[2.0, 0.9, 0.0], [0.0, 3.0, 0.0]])                                  # weiter als RADIUS: Rückfall
        anfragen = np.vstack([nah, fern])
        such = Meshfigurgpusuche(proben)
        self.assertEqual(such.suche, 'gpu')
        abstand, index = such.naechster(anfragen)
        soll_ab, soll_ix = cKDTree(proben).query(anfragen)
        # Gleiche Entfernung; der Index darf nur bei Gleichstand (float32) ein anderer, gleich naher Punkt sein.
        self.assertLess(float(np.abs(abstand - soll_ab).max()), 1e-6)
        self.assertLess(int((index != soll_ix).sum()), 5)
        self.assertGreaterEqual(such.befund()['rueckfall'], 2)
        self.assertEqual(such.befund()['anfragen'], len(anfragen))


if __name__ == '__main__':
    unittest.main()

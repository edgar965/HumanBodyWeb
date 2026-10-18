# -*- coding: utf-8 -*-
"""Mesh-3D: Daz' Gelenkkorrekturen (JCMs) in der Animation (14.10.2026, Edgar: „JCM … warum wendest du die denn nicht an?? das mesh-3d sollte wie Charakter / Studio sein!“).

    FeldTest     `Meshfigurobjektfelder`: das Feld des Käfigs geht auf anliegende Objektpunkte über (λ = 1 bis 2 cm, 0 ab 5 cm), starre Objekte bekommen keins, Ablage mit Marke
    DrahtTest    Quelltext: Route, Hörer der Animationsleiste (`nachBild` an drei Stellen), `Meshfigurgelenke` in der Bühne, Adresse der Felder am Objekt

Sabotage: in `Meshfigurobjektfelder.nachbarschaft` `lam` durch 1 ersetzen → `test_was_weit_absteht_bekommt_kein_feld` rot; in `Engine2d3dKleideranimation._takt` den Aufruf `nachBild` streichen → `DrahtTest` rot.
Im Chrome gemessen (Spiralballerina ohne Zweitarm Kopie, Bild 316): Haut 66.719 Punkte, Kleidung 11.940 Punkte, je 68 Kanäle; Abstandsänderung Stoff zu Haut p95 1,8 mm (nur Haut) → 0,4 mm (Haut und Stoff).
"""

import shutil
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.meshfigurobjektfelder import Meshfigurobjektfelder
from core.projekt_temp import ProjektTemp
from Kleidung.hautdatei import Hautdatei

WEB = Path(settings.BASE_DIR)


def quelltext(*teile):
    return WEB.joinpath(*teile).read_text(encoding='utf-8')


class _Ablage:
    """Nur das, was `Meshfigurobjektfelder` von der Ablage eines Laufs braucht: einen Arbeitsordner."""

    def __init__(self, ordner):
        self.ordner = Path(ordner)

    def arbeit(self, name=''):
        return self.ordner / name if name else self.ordner


class FeldTest(SimpleTestCase):
    databases = set()

    def _kaefig(self):
        """Ein Käfig aus Punkten im Abstand 1 cm auf einer Platte (z = 0), und ein Feld, das jeden Punkt um 10 mm nach +z schiebt."""
        gitter = np.stack(np.meshgrid(np.arange(21) * 0.01, np.arange(21) * 0.01, [0.0]), axis=-1).reshape(-1, 3)
        felder = {'kanal': (np.arange(len(gitter), dtype=np.uint32), np.tile(np.array([0.0, 0.0, 0.01], dtype=np.float32), (len(gitter), 1)))}
        return gitter, felder

    def _uebertragen(self, abstaende):
        kaefig, felder = self._kaefig()
        punkte = np.array([[0.10, 0.10, a] for a in abstaende])          # über der Mitte der Platte, in z abgehoben
        zeilen, nachbar, mischung = Meshfigurobjektfelder.nachbarschaft(punkte, kaefig)
        return Meshfigurobjektfelder.uebertragen(felder, len(kaefig), zeilen, nachbar, mischung)

    def test_anliegender_stoff_bekommt_das_feld_der_haut(self):
        aus = self._uebertragen([0.005])
        nummern, deltas = aus['kanal']
        self.assertEqual(list(nummern), [0])
        np.testing.assert_allclose(deltas[0], [0.0, 0.0, 0.01], atol=1e-6)

    def test_im_abstand_wird_es_ausgeblendet_und_weit_weg_gilt_nichts(self):
        aus = self._uebertragen([0.005, 0.035, 0.06])
        nummern, deltas = aus['kanal']
        self.assertEqual(list(nummern), [0, 1], 'bei 6 cm (λ = 0) gibt es kein Feld')
        self.assertGreater(deltas[0][2], deltas[1][2], 'je weiter weg, desto weniger')
        self.assertGreater(deltas[1][2], 0.0, 'bei 3,5 cm gilt noch ein Teil')

    def test_was_weit_absteht_bekommt_kein_feld(self):
        self.assertEqual(self._uebertragen([0.08, 0.2]), {})

    def test_kanaele_ohne_bewegte_nachbarn_fehlen(self):
        kaefig, felder = self._kaefig()
        felder['still'] = (np.array([400], dtype=np.uint32), np.array([[0.0, 0.0, 0.01]], dtype=np.float32))       # ein Punkt weit weg von der Mitte
        zeilen, nachbar, mischung = Meshfigurobjektfelder.nachbarschaft(np.array([[0.10, 0.10, 0.005]]), kaefig)
        self.assertNotIn('still', Meshfigurobjektfelder.uebertragen(felder, len(kaefig), zeilen, nachbar, mischung))

    def test_ein_starres_objekt_bekommt_kein_feld(self):
        index, gewicht = Hautdatei.starr(10, 7)
        index = index.astype(np.uint8)
        self.assertTrue(Meshfigurobjektfelder.starr(index, Hautdatei.quantisieren(gewicht)))
        gemischt = Hautdatei.quantisieren(np.array([[0.6, 0.4, 0, 0]] * 10))
        self.assertFalse(Meshfigurobjektfelder.starr(index, gemischt), 'ein Gewicht unter 255 heißt: es folgt mehreren Knochen')
        self.assertFalse(Meshfigurobjektfelder.starr(np.array([[1, 0, 0, 0], [2, 0, 0, 0]], dtype=np.uint8), np.array([[255, 0, 0, 0]] * 2, dtype=np.uint8)), 'zwei Knochen sind nicht starr')


class AblageTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = Path(ProjektTemp.ordner(prefix='objektfelder_'))
        self.addCleanup(shutil.rmtree, self.ordner, ignore_errors=True)
        self.objekt = Meshfigurobjektfelder(_Ablage(self.ordner))

    def test_die_ablage_gilt_nur_mit_derselben_marke(self):
        felder = {'a': (np.array([1, 5], dtype=np.uint32), np.ones((2, 3), dtype=np.float32)), 'b': (np.array([2], dtype=np.uint32), np.zeros((1, 3), dtype=np.float32))}
        marke = {'fassung': 1, 'glb': [10, 20]}
        self.objekt._ablegen('kleidung.glb', marke, felder)
        zurueck = self.objekt._aus_ablage('kleidung.glb', marke)
        self.assertEqual(list(zurueck), ['a', 'b'])
        np.testing.assert_array_equal(zurueck['a'][0], [1, 5])
        self.assertIsNone(self.objekt._aus_ablage('kleidung.glb', {'fassung': 1, 'glb': [10, 21]}), 'eine neue GLB entwertet die Ablage')
        self.assertIsNone(self.objekt._aus_ablage('haar.glb', marke), 'jede Datei hat ihre eigene Ablage')


class DrahtTest(SimpleTestCase):
    databases = set()

    def test_die_route_liegt_im_meshfigur_paket(self):
        text = quelltext('core', 'urls_meshfigur.py')
        self.assertIn("'api/meshfigur/<uuid:job_id>/objektfelder/<str:name>'", text)
        self.assertIn('Meshfigurobjektfeldendpunkt.felder', text)
        self.assertIn('async def felder', quelltext('core', 'api', 'meshfigurobjektfelder.py'), 'die Rechnung darf den gemeinsamen Faden der Seite nicht belegen')

    def test_die_animationsleiste_ruft_die_gelenkkorrekturen_nach_jedem_bild(self):
        text = quelltext('static', 'viewer', 'engine2d3dkleider', 'engine2d3dkleideranimation.js')
        self.assertEqual(text.count('this.nachBild?.()'), 3, 'Wiedergabe (`_takt`), Schieber/Sprung (`_aktiv`) und Stopp')
        buehne = quelltext('static', 'viewer', 'mesh3d', 'mesh3dbuehne.js')
        self.assertIn('new Meshfigurgelenke(this.buehne)', buehne)
        self.assertIn('this.animation.nachBild = () => this.gelenke.takt()', buehne)

    def test_die_haut_wird_wie_in_studio_gerechnet_und_die_objekte_bekommen_dieselben_werte(self):
        text = quelltext('static', 'viewer', 'meshfigur', 'meshfigurgelenke.js')
        self.assertIn('Genesis9gelenke.takt(this.buehne.modell)', text)
        self.assertIn('Genesis9felder.anwenden(netz, Genesis9gelenke.GRUPPE, e.felder, werte)', text)
        self.assertIn('Genesis9felder.holenAdresse(adresse)', text)

    def test_das_objekt_nennt_seine_felder_nur_mit_hautdatei(self):
        text = quelltext('static', 'viewer', 'meshfigur', 'meshfigurhaarobjekt.js')
        self.assertIn("haut && dateiAdresse.includes('/datei/ergebnis/')", text)
        self.assertIn("replace('/datei/ergebnis/', '/objektfelder/')", text)
        # Seit 14.10.2026 auch an die Haltung gebunden (`_drehung`): deren Fassung ist nicht in der Ruhelage gerechnet — ebenfalls keine Felder.
        self.assertIn('this._haltung || this._drehung) return null', text, 'in der Haltung des Netzes steht das Objekt starr: keine Felder')
        self.assertIn('gelenkziele()', quelltext('static', 'viewer', 'meshfigur', 'meshfigurbuehne.js'))

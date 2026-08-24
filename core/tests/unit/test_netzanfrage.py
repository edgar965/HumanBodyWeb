# -*- coding: utf-8 -*-
"""Netzanfrage — die drei Zweige von `/api/character/mesh/`.

WARUM MIT ATTRAPPEN (17.08.2026)
===============================
`character_mesh` war 141 Zeilen und ist in `api/netzanfrage.Netzanfrage` zerlegt
worden. Im Betrieb läuft davon nur EIN Zweig: Der weibliche und der männliche
Grundkörper haben beide einen Catmull-Clark-Unterteiler. Der Fallback für Netze
ohne Vierecke (`_grob`, mit Dreiecksaufteilung und Materialgruppen) wird von
keinem echten Aufruf getroffen — er wäre nach dem Umbau unbelegt geblieben.

Deshalb hier Attrappen statt der echten Figur: Ein Mini-Netz mit zwei Vierecken
und zwei Materialien, ein Mini-Unterteiler. Das prüft die Verzweigungen, nicht
die Morph-Mathematik (die steckt in `humanbody_core` und hat dort ihre Tests).

UMLEITUNG: Gepatcht wird in `core.api.netzanfrage` — eine Funktion liest ihre
freien Namen im Namensraum IHRES Moduls. Ein Patch an `core.dienste.charakterdaten`
würde ins Leere greifen (Projektregel „Test-Umleitungen, die ins Leere greifen").
"""

import numpy as np
from django.test import SimpleTestCase, RequestFactory, override_settings

from core.api import netzanfrage as modul
from core.api.netzanfrage import Netzanfrage


class NetzAttrappe:
    """Was `Charakterdaten.netzdaten()` liefert — nur die gelesenen Felder."""

    def __init__(self, mit_material=True):
        self.faces = np.array([[0, 1, 2, 3], [4, 5, 6, 7]])
        self.face_materials = np.array([1, 0]) if mit_material else None
        self.material_names = ['haut', 'auge']
        self.uvs = np.zeros((8, 2), dtype=np.float32)


class UnterteilerAttrappe:
    """Was `Charakterdaten.unterteiler()` liefert."""

    def __init__(self):
        self.triangles = np.array([[0, 1, 2], [1, 2, 3], [0, 2, 3]])
        self.uvs = np.zeros((4, 2), dtype=np.float32)
        self.groups = [{'materialIndex': 0, 'start': 0, 'count': 9}]

    def subdivide(self, punkte):
        return np.repeat(punkte, 2, axis=0)

    def compute_quad_normals(self, punkte):
        return np.zeros_like(punkte)


class ZustandAttrappe:
    """`CharacterState`-Doppel: merkt sich, was gesetzt wurde."""

    letzter = None

    def __init__(self, *args):
        self.bauart = ''
        self.morphs = {}
        self.metas = {}
        ZustandAttrappe.letzter = self

    def set_body_type(self, bauart):
        self.bauart = bauart

    def set_morph(self, name, wert):
        self.morphs[name] = wert

    def set_meta(self, name, wert):
        self.metas[name] = wert

    def compute(self):
        return np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]], dtype=np.float32)


class NetzanfrageBasis(SimpleTestCase):

    def setUp(self):
        self.netz = NetzAttrappe()
        self.unterteiler = None
        pruefung = self

        class DatenAttrappe:
            @staticmethod
            def geschlecht_zu(bauart):
                return 'female'

            @staticmethod
            def morphdaten():
                return None

            @staticmethod
            def voreinstellungen():
                return None

            @staticmethod
            def netzdaten(geschlecht='female'):
                return pruefung.netz

            @staticmethod
            def unterteiler(geschlecht='female'):
                return pruefung.unterteiler

        class EinstellungenAttrappe:
            ui_prefs = {'default_pose': 'a_pose'}

            @classmethod
            def load(cls):
                return cls()

        self._alt = (modul.Charakterdaten, modul.CharacterState, modul.AppSettings)
        modul.Charakterdaten = DatenAttrappe
        modul.CharacterState = ZustandAttrappe
        modul.AppSettings = EinstellungenAttrappe

    def tearDown(self):
        (modul.Charakterdaten, modul.CharacterState,
         modul.AppSettings) = self._alt

    def anfrage(self, abfrage=''):
        bitte = RequestFactory().get('/api/character/mesh/' + abfrage)
        return Netzanfrage(bitte)


class OhneUnterteilerTest(NetzanfrageBasis):
    """Der Fallback-Zweig — im Betrieb nie getroffen, deshalb hier geprüft."""

    def test_vierecke_werden_dreiecke_mit_gruppen(self):
        anfrage = self.anfrage()
        antwort = anfrage.antwort(anfrage.punkte())
        self.assertEqual(antwort['face_count'], 4, 'zwei Vierecke = vier Dreiecke')
        self.assertEqual(antwort['groups'], [
            {'materialIndex': 0, 'start': 0, 'count': 6},
            {'materialIndex': 1, 'start': 6, 'count': 6},
        ])
        self.assertEqual(antwort['material_names'], ['haut', 'auge'])
        self.assertIn('faces', antwort)
        self.assertIn('uvs', antwort)

    def test_nur_punkte_laesst_alles_weg(self):
        anfrage = self.anfrage('?nur_punkte=1')
        antwort = anfrage.antwort(anfrage.punkte())
        for weg in ('faces', 'uvs', 'groups', 'material_names'):
            self.assertNotIn(weg, antwort)
        self.assertIn('vertices', antwort)

    def test_ohne_materialien_keine_gruppen(self):
        self.netz = NetzAttrappe(mit_material=False)
        anfrage = self.anfrage()
        antwort = anfrage.antwort(anfrage.punkte())
        self.assertNotIn('groups', antwort)
        self.assertEqual(antwort['face_count'], 4)


class MitUnterteilerTest(NetzanfrageBasis):

    def setUp(self):
        super().setUp()
        self.unterteiler = UnterteilerAttrappe()

    def test_punkte_kommen_unterteilt_und_mit_normalen(self):
        anfrage = self.anfrage()
        antwort = anfrage.antwort(anfrage.punkte())
        self.assertEqual(antwort['vertex_count'], 4, '2 Punkte, verdoppelt')
        self.assertIn('normals', antwort)
        self.assertEqual(antwort['face_count'], 3, 'aus cc.triangles')
        self.assertEqual(antwort['groups'], self.unterteiler.groups)

    def test_nur_punkte_spart_dreiecke_und_uvs(self):
        anfrage = self.anfrage('?nur_punkte=1')
        antwort = anfrage.antwort(anfrage.punkte())
        self.assertNotIn('faces', antwort)
        self.assertNotIn('uvs', antwort)
        self.assertEqual(antwort['face_count'], 3,
                         'die Zahl bleibt — die Oberfläche zeigt sie an')


class ReglerTest(NetzanfrageBasis):

    def test_morph_und_meta_werden_gesetzt(self):
        self.anfrage('?morph_Abdomen_Mass=0.5&meta_age=30').punkte()
        self.assertEqual(ZustandAttrappe.letzter.morphs, {'Abdomen_Mass': 0.5})
        self.assertEqual(ZustandAttrappe.letzter.metas, {'age': 30.0})

    def test_unlesbarer_wert_kostet_nicht_die_figur(self):
        anfrage = self.anfrage('?morph_Abdomen_Mass=viel&morph_Nose=0.2')
        self.assertIsNotNone(anfrage.punkte())
        self.assertEqual(ZustandAttrappe.letzter.morphs, {'Nose': 0.2})

    def test_ohne_punkte_kommt_none_zurueck(self):
        # `del` statt Zurücksetzen hat beim ersten Wurf die ECHTE Methode der
        # Klasse entfernt — der nächste Test lief in ein AttributeError.
        echt = ZustandAttrappe.compute
        ZustandAttrappe.compute = lambda self: None
        try:
            self.assertIsNone(self.anfrage().punkte())
        finally:
            ZustandAttrappe.compute = echt


class PoseTest(NetzanfrageBasis):
    """Die T-Pose kommt aus einer .npy-Datei — Formfehler dürfen nicht durch."""

    def temp(self):
        from django.conf import settings
        from pathlib import Path
        ordner = Path(settings.BASE_DIR) / 'media' / 'tmp' / 'posetest'
        ordner.mkdir(parents=True, exist_ok=True)
        return ordner

    def ablegen(self, feld):
        ordner = self.temp()
        np.save(ordner / Netzanfrage.TPOSE, feld)
        return ordner

    def test_passende_datei_wird_eingesetzt(self):
        ordner = self.ablegen(np.array([[9.0, 9.0, 9.0], [8.0, 8.0, 8.0]],
                                       dtype=np.float32))
        with override_settings(HUMANBODY_DATA_DIR=str(ordner)):
            punkte = self.anfrage('?pose=t_pose').punkte()
        self.assertEqual(punkte[0][0], 9.0)

    def test_falsche_punktzahl_bleibt_bei_der_a_pose(self):
        """Andere Punktzahl heißt andere Figur — einsetzen zerstört das Modell."""
        ordner = self.ablegen(np.zeros((5, 3), dtype=np.float32))
        with override_settings(HUMANBODY_DATA_DIR=str(ordner)):
            with self.assertLogs('core.api.netzanfrage', level='WARNING') as protokoll:
                punkte = self.anfrage('?pose=t_pose').punkte()
        self.assertEqual(punkte[0][0], 0.0)
        self.assertEqual(len(punkte), 2, 'die berechneten Punkte bleiben')
        self.assertIn('passt nicht', protokoll.output[0])

    def test_a_pose_liest_die_datei_nicht(self):
        with override_settings(HUMANBODY_DATA_DIR='/gibtsnicht'):
            self.assertIsNotNone(self.anfrage().punkte())

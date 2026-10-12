# -*- coding: utf-8 -*-
"""Jobseite „Mesh-3D“ (11.10.2026) und der Schritt „pose“ des Modell-Imports — ohne Blender, ohne SAM, ohne GPU.

1. `Mesh3dschritte`: Zustand je Schritt aus `stand.json` (fertig, läuft, gescheitert, übersprungen, offen); die Schritte sind die der Kette HEUTE
   (ein alter Stand ohne „pose“ zeigt ihn als „offen“).
2. `Blendimportformate`: GLB ist ein Format der Kette (Endung, Umwandeln, Einstellungen); der Katalog trägt „Pose bestimmen“.
3. `Blendimportpose`: Modus und Drehung aus den Einstellungen; `haltung` misst die Winkel gegen die Körperachse (Kunstskelett: Arme in A-Haltung, Beine gerade);
   `zusatz` gibt ohne Pose nichts, mit gültiger Pose den Pfad, mit veralteter Pose einen Fehler (kein stiller Rückfall).
4. `Mesh3dergebnisse._kategorie` kürzt die Garderobenkategorie.

Nicht gelaufen (Stand 11.10.2026) — läuft nur auf Ansage.
"""

import json
import struct
import tempfile
from pathlib import Path

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimporteinstellungen import Blendimporteinstellungen
from core.dienste.blendimportformate import Blendimportformate
from core.dienste.blendimportlauf import Blendimportlauf
from core.dienste.blendimportnetz import Blendimportnetz
from core.dienste.blendimportpose import Blendimportpose
from core.dienste.blendimportweg import Blendimportweg
from core.dienste.engine2d3dkleiderposegelenke import Engine2d3dKleiderposegelenke
from core.dienste.mesh3dergebnisse import Mesh3dergebnisse
from core.dienste.mesh3dschritte import Mesh3dschritte
from core.dienste.posebestimmung import Posebestimmung


class _Ablage:
    """Nur, was `Blendimportpose` von einer Ablage braucht: `kennung` und `arbeit()`."""

    def __init__(self, wurzel):
        self.kennung = '2026.10.11.12.00.00'
        self.wurzel = Path(wurzel)

    def arbeit(self, name=''):
        return self.wurzel / name if name else self.wurzel


class SchritteTest(SimpleTestCase):
    databases = set()

    def test_1_zustand_je_schritt(self):
        stand = {'quelle': {'format': 'blend'}, 'status': 'laeuft', 'schritt': 'figur', 'dauer': {'export': 5.0, 'umposen': 2.0, 'koerper': 3.0},
                 'ergebnis': {'export': {}, 'umposen': {'aus': True, 'grund': 'kein Rig'}, 'koerper': {}}}
        zustand = {s['schluessel']: s['zustand'] for s in Mesh3dschritte.liste(stand)}
        self.assertEqual(zustand['export'], 'fertig')
        self.assertEqual(zustand['umposen'], 'uebersprungen')
        self.assertEqual(zustand['figur'], 'laeuft')
        self.assertEqual(zustand['modell'], 'offen')

    def test_2_gescheitert_und_angehalten_stehen_am_aktuellen_schritt(self):
        for status in ('gescheitert', 'angehalten'):
            stand = {'quelle': {'format': 'blend'}, 'status': status, 'schritt': 'stuecke', 'dauer': {}, 'ergebnis': {}}
            zustand = {s['schluessel']: s['zustand'] for s in Mesh3dschritte.liste(stand)}
            self.assertEqual(zustand['stuecke'], status)

    def test_3_die_schritte_sind_die_der_kette_heute(self):
        stand = {'quelle': {'format': 'obj'}, 'schritte': ['export', 'koerper'], 'status': 'fertig', 'dauer': {'export': 1.0}, 'ergebnis': {'export': {}}}
        namen = [s['schluessel'] for s in Mesh3dschritte.liste(stand)]
        self.assertEqual(namen, list(Blendimportlauf.schritte_fuer('obj')))
        self.assertIn('pose', namen)
        self.assertEqual(namen[0], 'umwandeln')


class FormateUndKatalogTest(SimpleTestCase):
    databases = set()

    def test_1_glb_ist_ein_format_der_kette(self):
        self.assertEqual(Blendimportformate.pruefen('glb'), 'glb')
        self.assertEqual(Blendimportformate.endung('glb'), '.glb')
        self.assertTrue(Blendimportformate.umwandeln('glb'))
        self.assertEqual(Blendimportformate.einstellungen('glb').FORMAT, 'glb')
        self.assertIn('umwandeln', Blendimportlauf.schritte_fuer('glb'))

    def test_2_der_katalog_fuehrt_die_pose_und_prueft_sie(self):
        schluessel = [e['schluessel'] for e in Blendimporteinstellungen.KATALOG]
        self.assertIn('pose', schluessel)
        self.assertIn('pose_drehung', schluessel)
        for klasse in (Blendimporteinstellungen, Blendimportformate.einstellungen('fbx'), Blendimportformate.einstellungen('glb')):
            werte = klasse.pruefen({'pose': 'unsinn', 'pose_drehung': '45'})
            self.assertEqual(werte['pose'], 'aus')
            self.assertEqual(werte['pose_drehung'], '0')
            self.assertEqual(klasse.pruefen({'pose': 'sam', 'pose_drehung': '90'})['pose_drehung'], '90')

    def test_3_der_schritt_pose_liegt_zwischen_koerper_und_figur(self):
        s = Blendimportlauf.SCHRITTE
        # Seit 11.10.2026 steht dazwischen die Segmentierung des Wegs „netz“ (`Blendimportlauf.NUR_NETZ`); beim Weg „teile“ fehlt sie.
        self.assertEqual(s.index('segmentierung'), s.index('koerper') + 1)
        self.assertEqual(s.index('pose'), s.index('segmentierung') + 1)
        self.assertEqual(s.index('figur'), s.index('pose') + 1)
        self.assertNotIn('segmentierung', Blendimportlauf.schritte_fuer('blend'))
        von, bis = Blendimportlauf.BAENDER['pose']
        self.assertEqual(Blendimportlauf.BAENDER['koerper'][1], von)
        self.assertEqual(Blendimportlauf.BAENDER['figur'][0], bis)


class PoseTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _sam():
        """Ein Kunstskelett in Bildkoordinaten (y nach unten): Rumpf senkrecht, Oberarme 45° vom Körper weg, Beine gerade."""
        namen = list(Engine2d3dKleiderposegelenke.ZUORDNUNG.values())
        k2 = np.zeros((len(namen), 2))
        lage = {'left-shoulder': (-0.2, 0.0), 'right-shoulder': (0.2, 0.0), 'left-hip': (-0.1, 0.5), 'right-hip': (0.1, 0.5),
                'left-elbow': (-0.2 - 0.3, 0.3), 'right-elbow': (0.2 + 0.3, 0.3), 'left-wrist': (-0.5, 0.6), 'right-wrist': (0.5, 0.6),
                'left-knee': (-0.1, 1.0), 'right-knee': (0.1, 1.0)}
        for i, n in enumerate(namen):
            k2[i] = lage.get(n, (0.0, 0.0))
        return {'namen': namen, 'drehungen': {'0': {'k2': k2.tolist()}}}

    def test_1_modus_und_drehung(self):
        self.assertEqual(Blendimportpose.modus({'pose': 'sam'}), 'sam')
        self.assertEqual(Blendimportpose.modus({}), 'aus')
        self.assertEqual(Blendimportpose.modus(None), 'aus')
        self.assertEqual(Blendimportpose.drehung({'pose_drehung': '270'}), 270)
        self.assertEqual(Blendimportpose.drehung({'pose_drehung': '45'}), 0)
        self.assertEqual(Blendimportpose.drehung({'pose_drehung': 'x'}), 0)

    def test_2_haltung_misst_gegen_die_koerperachse(self):
        h = Blendimportpose.haltung(self._sam(), 0)
        self.assertAlmostEqual(h['rumpf_neigung_grad'], 0.0, places=1)
        self.assertAlmostEqual(h['oberarm_links_grad'], 45.0, places=0)       # 0,3 quer auf 0,3 senkrecht
        self.assertAlmostEqual(h['oberschenkel_links_grad'], 0.0, places=0)
        self.assertEqual(h['a_haltung_oberarm_grad'], Blendimportpose.A_OBERARM_GRAD)

    def test_3_haltung_ist_unabhaengig_von_der_drehung_des_bildes(self):
        sam = self._sam()
        k2 = np.asarray(sam['drehungen']['0']['k2'])
        gedreht = np.stack([-k2[:, 1], k2[:, 0]], axis=1)                       # um 90° in der Bildebene
        sam['drehungen']['90'] = {'k2': gedreht.tolist()}
        a, b = Blendimportpose.haltung(sam, 0), Blendimportpose.haltung(sam, 90)
        for schluessel in ('oberarm_links_grad', 'oberarm_rechts_grad', 'oberschenkel_links_grad'):
            self.assertAlmostEqual(a[schluessel], b[schluessel], places=1)
        self.assertAlmostEqual(b['rumpf_neigung_grad'], 90.0, places=1)

    def test_4_ohne_einstellung_kein_zusatz_mit_veralteter_pose_ein_fehler(self):
        with tempfile.TemporaryDirectory(dir=str(Path(__file__).resolve().parents[3] / 'ProjektTemp')) as ordner:
            ablage = _Ablage(ordner)
            glb = ablage.arbeit('koerper.glb')
            glb.write_bytes(b'x' * 10)
            pose_ordner = ablage.arbeit(Blendimportpose.ORDNER)
            pose_ordner.mkdir()
            (pose_ordner / 'landmarken.npz').write_bytes(b'x')
            aus = {'einstellungen': {'pose': 'aus'}}
            self.assertEqual(Blendimportpose.zusatz(ablage, aus, glb), {})
            gueltig = {'einstellungen': {'pose': 'sam', 'pose_drehung': '0'},
                       'ergebnis': {'pose': {'datei': 'landmarken.npz', 'optionen': {'pose_drehung': '0'}, 'quelle': {'koerper': Posebestimmung.stand(glb)}}}}
            self.assertEqual(Blendimportpose.zusatz(ablage, gueltig, glb), {'landmarken_hand': str(pose_ordner / 'landmarken.npz')})
            # Die Drehung wurde nach dem Lauf geändert → kein stiller Rückfall, sondern ein Fehler mit Grund.
            gueltig['einstellungen']['pose_drehung'] = '90'
            with self.assertRaisesRegex(RuntimeError, 'Drehung'):
                Blendimportpose.zusatz(ablage, gueltig, glb)
            # Nie gerechnet.
            with self.assertRaisesRegex(RuntimeError, 'noch nicht gerechnet'):
                Blendimportpose.zusatz(ablage, {'einstellungen': {'pose': 'sam'}}, glb)
            # Das Körpernetz hat sich geändert.
            gueltig['einstellungen']['pose_drehung'] = '0'
            glb.write_bytes(b'y' * 11)
            with self.assertRaisesRegex(RuntimeError, 'Körpernetz'):
                Blendimportpose.zusatz(ablage, gueltig, glb)


class WegTest(SimpleTestCase):
    """Der Weg „netz“ (ein verschmolzenes Netz, `Blendimportweg`, `Blendimportnetz`): Erkennung an der GLB, Höhe, skalierte Kopie, die drei Schritte."""
    databases = set()

    @staticmethod
    def _glb(pfad, **teile):
        """Eine GLB mit JSON-Block und einem Binärblock aus 8 Bytes; `teile` ergänzen das JSON."""
        daten = {'asset': {'version': '2.0'}, 'scene': 0, 'scenes': [{'nodes': [0]}], 'nodes': [{'mesh': 0}],
                 'meshes': [{'primitives': [{'attributes': {'POSITION': 0}, 'indices': 1}]}],
                 'accessors': [{'count': 4, 'min': [-0.2, 0.0, -0.1], 'max': [0.2, 1.0, 0.1]}, {'count': 6}]}
        daten.update(teile)
        text = json.dumps(daten).encode('utf-8')
        text += b' ' * (-len(text) % 4)
        binaer = b'BIN\x00' * 2
        kopf = b'glTF' + struct.pack('<II', 2, 12 + 8 + len(text) + 8 + len(binaer)) + struct.pack('<I', len(text)) + b'JSON'
        Path(pfad).write_bytes(kopf + text + struct.pack('<I', len(binaer)) + b'BIN\x00' + binaer)
        return binaer

    @staticmethod
    def _ordner():
        return tempfile.TemporaryDirectory(dir=str(Path(__file__).resolve().parents[3] / 'ProjektTemp'))

    def test_1_erkennung(self):
        with self._ordner() as o:
            glb = Path(o) / 'a.glb'
            self._glb(glb)
            self.assertEqual(Blendimportweg.erkennen('glb', glb)[0], 'netz')
            self._glb(glb, nodes=[{'mesh': 0}, {'mesh': 0}], scenes=[{'nodes': [0, 1]}])
            self.assertEqual(Blendimportweg.erkennen('glb', glb)[0], 'teile')
            self._glb(glb, skins=[{'joints': [0]}])
            self.assertIn('Skelett', Blendimportweg.erkennen('glb', glb)[1])
            self.assertEqual(Blendimportweg.erkennen('fbx', glb)[0], 'teile')
            (Path(o) / 'b.glb').write_bytes(b'nicht glb')
            with self.assertRaises(ValueError):
                Blendimportweg.erkennen('glb', Path(o) / 'b.glb')

    def test_2_schritte_und_stand_ohne_weg(self):
        self.assertEqual(Blendimportlauf.schritte_fuer('glb', 'netz'), ('koerper', 'segmentierung', 'pose', 'figur'))
        self.assertEqual(Blendimportlauf.schritte_fuer('glb'), Blendimportlauf.schritte_fuer('glb', None))
        self.assertEqual(Blendimportlauf.schritte_fuer('glb', 'teile'), Blendimportlauf.schritte_fuer('glb'))
        for schritt in Blendimportweg.NETZ_SCHRITTE:
            self.assertIn(schritt, Blendimportlauf.SCHRITTE)
        self.assertEqual(Blendimportweg.pruefen(None), 'teile')
        self.assertEqual(Blendimportweg.pruefen('unsinn'), 'teile')
        stand = {'quelle': {'format': 'glb'}, 'weg': 'netz', 'status': 'neu', 'dauer': {}, 'ergebnis': {}}
        self.assertEqual([s['schluessel'] for s in Mesh3dschritte.liste(stand)], ['koerper', 'segmentierung', 'pose', 'figur'])
        self.assertIn('GANZE Netz', next(s['hinweis'] for s in Mesh3dschritte.liste(stand) if s['schluessel'] == 'figur'))

    def test_3_hoehe_mit_skalierung_und_drehung_des_knotens(self):
        self.assertAlmostEqual(Blendimportnetz._hoehe({'nodes': [{'mesh': 0}], 'meshes': [{'primitives': [{'attributes': {'POSITION': 0}}]}],
                                                       'accessors': [{'min': [-0.2, 0.0, -0.1], 'max': [0.2, 1.0, 0.1]}]}), 1.0)
        halb = {'nodes': [{'mesh': 0, 'scale': [0.5, 0.5, 0.5]}], 'meshes': [{'primitives': [{'attributes': {'POSITION': 0}}]}],
                'accessors': [{'min': [-0.2, 0.0, -0.1], 'max': [0.2, 1.0, 0.1]}]}
        self.assertAlmostEqual(Blendimportnetz._hoehe(halb), 0.5)
        liegt = {'nodes': [{'mesh': 0, 'rotation': [0.0, 0.0, 0.70710678, 0.70710678]}], 'meshes': [{'primitives': [{'attributes': {'POSITION': 0}}]}],
                 'accessors': [{'min': [-0.2, 0.0, -0.1], 'max': [0.2, 1.0, 0.1]}]}
        self.assertAlmostEqual(Blendimportnetz._hoehe(liegt), 0.4, places=4)

    def test_4_skalierte_kopie_gleicher_inhalt_neuer_massstab(self):
        with self._ordner() as o:
            glb, ziel = Path(o) / 'a.glb', Path(o) / 'z.glb'
            binaer = self._glb(glb)
            daten = Blendimportweg.glb_json(glb)
            Blendimportnetz._skaliert_schreiben(glb, ziel, daten, 2.0)
            neu = Blendimportweg.glb_json(ziel)
            self.assertEqual(neu['nodes'][0]['scale'], [2.0, 2.0, 2.0])
            roh = ziel.read_bytes()
            self.assertEqual(struct.unpack('<I', roh[8:12])[0], len(roh))                 # Gesamtlänge im Kopf stimmt
            self.assertEqual(struct.unpack('<I', roh[12:16])[0] % 4, 0)                   # JSON-Block auf vier Bytes aufgefüllt
            self.assertTrue(roh.endswith(binaer))                                         # Puffer unverändert
            self.assertAlmostEqual(Blendimportnetz._hoehe(neu), 2.0)

    def test_5_schreiben_streckt_nur_ausserhalb_der_menschenhoehe(self):
        class Ablage:
            kennung = 'probe'

            def __init__(self, wurzel):
                self.wurzel = Path(wurzel)

            def arbeit(self, name=''):
                return self.wurzel / name if name else self.wurzel

        with self._ordner() as o:
            glb = Path(o) / 'a.glb'
            self._glb(glb)                                                                # 1,0 m: wie ein Bild-zu-3D-Netz ohne Maßstab
            b = Blendimportnetz(Ablage(Path(o) / 'arbeit'), lambda a, t: None).schreiben(glb)
            self.assertAlmostEqual(b['hoehe_m'], Blendimportnetz.SOLL_M, places=3)
            self.assertAlmostEqual(b['faktor'], Blendimportnetz.SOLL_M / 1.0, places=3)
            self._glb(glb, accessors=[{'count': 4, 'min': [-0.2, 0.0, -0.1], 'max': [0.2, 1.75, 0.1]}, {'count': 6}])
            b = Blendimportnetz(Ablage(Path(o) / 'arbeit2'), lambda a, t: None).schreiben(glb)
            self.assertEqual(b['faktor'], 1.0)                                            # 1,75 m: unverändert
            self.assertEqual(Path(o, 'arbeit2', 'koerper.glb').read_bytes(), glb.read_bytes())


class ErgebnisseTest(SimpleTestCase):
    databases = set()

    def test_1_kategorie_kurz(self):
        self.assertEqual(Mesh3dergebnisse._kategorie(['Follower/Wardrobe/Footwear', '/Default/Wardrobe/Footwear']), 'Footwear')
        self.assertEqual(Mesh3dergebnisse._kategorie('Follower/Hair'), 'Hair')
        self.assertEqual(Mesh3dergebnisse._kategorie(None), '')
        self.assertEqual(Mesh3dergebnisse._kategorie([]), '')

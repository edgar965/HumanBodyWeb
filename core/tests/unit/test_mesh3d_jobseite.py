# -*- coding: utf-8 -*-
"""Jobseite „Mesh-3D“, zweite Runde (11.10.2026): Kopie, Upload, Quelle ändern, leichte Netz-Ansicht, Segmentierung (Sapiens) und der Hautton aus den Sapiens-Flächen.

Ohne Blender, ohne GPU, ohne Sapiens-Modell — Kunstdaten in `ProjektTemp`, keine Datenbank (die Stellen, die sie bräuchten, sind ausgetauscht). Nicht gelaufen — läuft nur auf Ansage.

    OrdnerkopieTest       Dateien, Auslassungen, Kennungen in kleinen JSON-Dateien, Änderungszeit bleibt
    EingangTest           Pfade aus dem Browser (kein `..`, keine Sonderzeichen), Ordner nach der Datei, Endungen, Fassung
    KopienameTest         „Kopie“, „Kopie 2“ …, höchstens `NAME_MAX` Zeichen
    QuellwechselTest      Format aus der Endung der gewählten Datei, Ordner behält das Format
    NetzansichtTest       Zustand keine / unnötig / fehlt / bereit nach dem Stempel des Originals
    SegmentierungTest     Dreiecke aus dem GLB-JSON, Stimmen und Stempel für den Auftrag „Mesh to 3D“ (`fuer_figur`)
    HautmodellTest        Gruppen nach Körperteilen: der Bart (Gesicht) darf die Hände nicht überstimmen, dunkle Gruppen zählen nicht
"""

import json
import struct
import tempfile
from pathlib import Path
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportsegmentierung import Blendimportsegmentierung
from core.dienste.mesh3deingang import Mesh3deingang
from core.dienste.mesh3dkopie import Mesh3dkopie
from core.dienste.mesh3dnetzansicht import Mesh3dnetzansicht
from core.dienste.mesh3dquellwechsel import Mesh3dquellwechsel
from core.dienste.ordnerkopie import Ordnerkopie


def _ordner():
    return tempfile.TemporaryDirectory(dir=str(Path(__file__).resolve().parents[3] / 'ProjektTemp'))


class _Hochgeladen:
    """Was `Mesh3deingang` von einer hochgeladenen Datei braucht: `name` und `chunks()`."""

    def __init__(self, name, inhalt=b'x'):
        self.name = name
        self.inhalt = inhalt

    def chunks(self):
        yield self.inhalt


class OrdnerkopieTest(SimpleTestCase):
    databases = set()

    def test_1_dateien_auslassungen_und_kennungen(self):
        with _ordner() as o:
            von, nach = Path(o) / 'von', Path(o) / 'nach'
            (von / 'arbeit').mkdir(parents=True)
            (von / 'stand.json').write_text(json.dumps({'pfad': 'A:\\x\\2026.10.11.20.03.34\\a.glb'}), encoding='utf-8')
            (von / 'arbeit' / 'netz.glb').write_bytes(b'GLB' * 100)
            (von / 'arbeit' / 'halb.teil').write_bytes(b'x')
            (von / 'auftrag.pid').write_text('4711')
            kopie = Ordnerkopie(von, nach, {'2026.10.11.20.03.34': '2026.10.11.21.00.00'})
            zahl, groesse = kopie.kopieren()
            self.assertEqual(zahl, 2)
            self.assertEqual(groesse, (nach / 'stand.json').stat().st_size + 300)
            self.assertIn('2026.10.11.21.00.00', (nach / 'stand.json').read_text(encoding='utf-8'))
            self.assertNotIn('2026.10.11.20.03.34', (nach / 'stand.json').read_text(encoding='utf-8'))
            self.assertFalse((nach / 'auftrag.pid').exists())
            self.assertFalse((nach / 'arbeit' / 'halb.teil').exists())
            self.assertEqual((nach / 'arbeit' / 'netz.glb').read_bytes(), b'GLB' * 100)

    def test_2_binaerdateien_bleiben_unveraendert_mit_gleicher_zeit(self):
        with _ordner() as o:
            von, nach = Path(o) / 'von', Path(o) / 'nach'
            von.mkdir()
            (von / 'k.npz').write_bytes(b'2026.10.11.20.03.34')
            alt = (von / 'k.npz').stat().st_mtime_ns
            Ordnerkopie(von, nach, {'2026.10.11.20.03.34': 'neu'}).kopieren()
            self.assertEqual((nach / 'k.npz').read_bytes(), b'2026.10.11.20.03.34')
            self.assertEqual((nach / 'k.npz').stat().st_mtime_ns, alt)


class EingangTest(SimpleTestCase):
    databases = set()

    def test_1_pfade_aus_dem_browser_bleiben_im_zielordner(self):
        self.assertEqual(Mesh3deingang.teile('Ordner/sub\\datei.obj'), ['Ordner', 'sub', 'datei.obj'])
        self.assertEqual(Mesh3deingang.teile('../../etc/passwort'), ['etc', 'passwort'])
        self.assertEqual(Mesh3deingang.teile('C:\\Windows\\a.obj'), ['C_', 'Windows', 'a.obj'])
        self.assertEqual(Mesh3deingang.teile(''), [])

    def test_2_einzelne_datei_bekommt_einen_ordner_nach_ihrem_namen(self):
        with _ordner() as o, mock.patch.object(Mesh3deingang, 'wurzel', return_value=Path(o)):
            antwort = Mesh3deingang('glb').ablegen([_Hochgeladen('wizard character 3d model_Best.glb')], [''])
            pfad = Path(antwort['pfad'])
            self.assertEqual(pfad.parent.name, 'wizard character 3d model_Best')
            self.assertTrue(pfad.is_file())
            self.assertEqual(antwort['hauptdateien'], ['wizard character 3d model_Best.glb'])

    def test_3_ordner_behaelt_die_struktur_und_filtert_endungen(self):
        with _ordner() as o, mock.patch.object(Mesh3deingang, 'wurzel', return_value=Path(o)):
            antwort = Mesh3deingang('obj').ablegen(
                [_Hochgeladen('f.obj'), _Hochgeladen('f.mtl'), _Hochgeladen('tex.png'), _Hochgeladen('virus.exe')],
                ['Figur/f.obj', 'Figur/f.mtl', 'Figur/tex/tex.png', 'Figur/virus.exe'])
            ordner = Path(antwort['ordner'])
            self.assertTrue((ordner / 'Figur' / 'f.obj').is_file())
            self.assertTrue((ordner / 'Figur' / 'tex' / 'tex.png').is_file())
            self.assertFalse((ordner / 'Figur' / 'virus.exe').exists())
            self.assertEqual((antwort['anzahl'], antwort['ausgelassen']), (3, 1))

    def test_4_ohne_datei_des_formats_ein_fehler(self):
        with _ordner() as o, mock.patch.object(Mesh3deingang, 'wurzel', return_value=Path(o)):
            with self.assertRaises(ValueError):
                Mesh3deingang('fbx').ablegen([_Hochgeladen('f.obj')], [''])

    def test_5_mehrere_fassungen_die_hoechste_wird_gelesen(self):
        with _ordner() as o, mock.patch.object(Mesh3deingang, 'wurzel', return_value=Path(o)):
            antwort = Mesh3deingang('blend').ablegen([_Hochgeladen('cute girl 4.0.blend'), _Hochgeladen('cute girl 5.0.blend')], ['cute girl/cute girl 4.0.blend', 'cute girl/cute girl 5.0.blend'])
            self.assertEqual(Path(antwort['pfad']).name, 'cute girl 5.0.blend')


class KopienameTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _kopie(name):
        kopie = object.__new__(Mesh3dkopie)
        kopie.name = name
        return kopie

    def test_1_erste_zweite_dritte_kopie(self):
        with mock.patch.object(Mesh3dkopie, 'namen', return_value={'zauberer'}):
            self.assertEqual(self._kopie('Zauberer').neuer_name(), 'Zauberer Kopie')
        with mock.patch.object(Mesh3dkopie, 'namen', return_value={'zauberer', 'zauberer kopie'}):
            self.assertEqual(self._kopie('Zauberer').neuer_name(), 'Zauberer Kopie 2')
            self.assertEqual(self._kopie('Zauberer Kopie').neuer_name(), 'Zauberer Kopie 2')
        with mock.patch.object(Mesh3dkopie, 'namen', return_value={'zauberer', 'zauberer kopie', 'zauberer kopie 2'}):
            self.assertEqual(self._kopie('Zauberer Kopie 2').neuer_name(), 'Zauberer Kopie 3')

    def test_2_lange_namen_bleiben_unter_der_grenze(self):
        with mock.patch.object(Mesh3dkopie, 'namen', return_value=set()):
            name = self._kopie('A' * 80).neuer_name()
        self.assertLessEqual(len(name), 60)
        self.assertTrue(name.endswith(' Kopie'))


class QuellwechselTest(SimpleTestCase):
    databases = set()

    def test_1_format_aus_der_endung_ordner_behaelt_das_format(self):
        with _ordner() as o:
            for endung, format in (('.glb', 'glb'), ('.BLEND', 'blend'), ('.obj', 'obj'), ('.fbx', 'fbx')):
                datei = Path(o) / ('netz' + endung)
                datei.write_bytes(b'x')
                self.assertEqual(Mesh3dquellwechsel.format_von(str(datei), 'blend'), format)
            self.assertEqual(Mesh3dquellwechsel.format_von(o, 'glb'), 'glb')
            (Path(o) / 'text.txt').write_text('x')
            with self.assertRaises(ValueError):
                Mesh3dquellwechsel.format_von(str(Path(o) / 'text.txt'), 'glb')

    def test_2_nichts_von_dem_was_ein_lauf_schreibt_bleibt_in_der_liste_der_felder(self):
        for feld in ('quelle', 'einstellungen', 'weg', 'weg_grund', 'angelegt', 'kennung', 'bereich', 'kopie'):
            self.assertNotIn(feld, Mesh3dquellwechsel.LAUFFELDER)
        for feld in ('ergebnis', 'rollen', 'schritt', 'fortschritt', 'dauer', 'pid'):
            self.assertIn(feld, Mesh3dquellwechsel.LAUFFELDER)


class NetzansichtTest(SimpleTestCase):
    databases = set()

    def test_1_zustaende(self):
        with _ordner() as o:
            netz = Path(o) / 'koerper.glb'
            netz.write_bytes(b'x' * 200)
            ansicht = Mesh3dnetzansicht('2026.10.11.12.00.00')
            with mock.patch.object(Mesh3dnetzansicht, 'quelle', return_value=None):
                self.assertEqual(ansicht.zustand()['status'], 'keine')
            with mock.patch.object(Mesh3dnetzansicht, 'quelle', return_value=netz), mock.patch.object(Mesh3dnetzansicht, 'GROSS_BYTES', 1000):
                self.assertEqual(ansicht.zustand()['status'], 'unnoetig')
            with mock.patch.object(Mesh3dnetzansicht, 'quelle', return_value=netz), mock.patch.object(Mesh3dnetzansicht, 'GROSS_BYTES', 100):
                self.assertEqual(ansicht.zustand()['status'], 'fehlt')

    def test_1b_ein_kleines_netz_nennt_adresse_und_datei(self):
        """13.10.2026: Die Mesh-Ansicht zeigt das Netz auch ohne Auftrag „Mesh to 3D“ — dafür braucht der Zustand bei `unnoetig` Adresse und Dateinamen (der Lader wird nach der Endung gewählt)."""
        with _ordner() as o:
            netz = Path(o) / 'koerper.glb'
            netz.write_bytes(b'x' * 200)
            with mock.patch.object(Mesh3dnetzansicht, 'quelle', return_value=netz), mock.patch.object(Mesh3dnetzansicht, 'GROSS_BYTES', 1000):
                zustand = Mesh3dnetzansicht('2026.10.11.12.00.00').zustand()
            self.assertEqual(zustand['status'], 'unnoetig')
            self.assertEqual(zustand['datei'], 'koerper.glb')
            self.assertIn('/api/mesh3d/2026.10.11.12.00.00/netzansicht/?v=', zustand['adresse'])

    def test_1c_verdrahtung_der_mesh_ansicht_ohne_figur(self):
        """Wächter (Quelltext): Endpunkt liefert bei `unnoetig` das Netz selbst, die Bühne zeigt es bei fehlendem UND bei gelöschtem Auftrag „Mesh to 3D“."""
        web = Path(__file__).resolve().parents[3]
        endpunkt = (web / 'core' / 'api' / 'mesh3dnetzansicht.py').read_text(encoding='utf-8')
        self.assertIn("ansicht.zustand()['status'] == 'unnoetig'", endpunkt)
        buehne = (web / 'static' / 'viewer' / 'mesh3d' / 'mesh3dbuehne.js').read_text(encoding='utf-8')
        self.assertIn('_netzOhneFigur(z)', buehne)
        # seit 13.10.2026 mit der Ausgabe-Auswahl: eine gewählte Ausgabe (Variante) hat ihre eigene Figur, das Fehlen der ersten zählt dann nicht
        self.assertIn('if (!id || (!this.ausgabe && z.figur.fehlt))', buehne)

    def test_2_der_stempel_aendert_sich_mit_dem_original(self):
        with _ordner() as o:
            netz = Path(o) / 'koerper.glb'
            netz.write_bytes(b'x' * 10)
            erster = Mesh3dnetzansicht.stempel(netz)
            netz.write_bytes(b'x' * 11)
            self.assertNotEqual(Mesh3dnetzansicht.stempel(netz), erster)
            self.assertEqual(erster[0], Mesh3dnetzansicht.FASSUNG)


class _Ablage:
    def __init__(self, wurzel, kennung='2026.10.11.12.00.00'):
        self.wurzel = Path(wurzel)
        self.kennung = kennung

    def arbeit(self, name=''):
        return self.wurzel / 'arbeit' / name if name else self.wurzel / 'arbeit'

    def netzdatei(self, teil='koerper', original=False):
        return self.wurzel / 'eingang' / 'koerper.glb'


class SegmentierungTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _glb(pfad, dreiecke):
        daten = {'asset': {'version': '2.0'}, 'meshes': [{'primitives': [{'attributes': {'POSITION': 0}, 'indices': 1}]}],
                 'accessors': [{'count': 4}, {'count': 3 * dreiecke}]}
        text = json.dumps(daten).encode('utf-8')
        text += b' ' * (-len(text) % 4)
        Path(pfad).write_bytes(b'glTF' + struct.pack('<II', 2, 12 + 8 + len(text)) + struct.pack('<I', len(text)) + b'JSON' + text)

    def test_1_dreiecke_aus_dem_json_block(self):
        with _ordner() as o:
            glb = Path(o) / 'n.glb'
            self._glb(glb, 1_935_797)
            self.assertEqual(Blendimportsegmentierung.flaechen_von(glb), 1_935_797)
            self.assertGreater(1_935_797, Blendimportsegmentierung.PROXY_AB)

    def _vorbereiten(self, o, eingang_groesse=None):
        wurzel = Path(o)
        (wurzel / 'eingang').mkdir()
        (wurzel / 'import' / 'arbeit' / 'segmentierung').mkdir(parents=True)
        glb = wurzel / 'import' / 'arbeit' / 'koerper.glb'
        glb.write_bytes(b'g' * 100)
        eingang = wurzel / 'eingang' / 'koerper.glb'
        eingang.write_bytes(b'g' * (eingang_groesse or 100))
        np.savez_compressed(wurzel / 'import' / 'arbeit' / 'segmentierung' / 'sapiens_flaechen.npz', klassen=np.ones((4, 28), dtype=np.float32), flaechen=4,
                            netz=np.array(Blendimportsegmentierung.stempel(glb)), fassung=2)
        stand = {'ergebnis': {'segmentierung': {'datei': 'sapiens_flaechen.npz', 'optionen': {'verwenden': 'an', 'haar': 'beide'},
                                                 'quelle': {'koerper': Blendimportsegmentierung.stempel(glb)}}}}
        return _Ablage(wurzel / 'import'), _Ablage(wurzel), stand, glb

    def test_2_stimmen_gehen_mit_dem_stempel_des_eingangs_in_den_auftrag(self):
        with _ordner() as o:
            ablage, job, stand, glb = self._vorbereiten(o)
            optionen = Blendimportsegmentierung.fuer_figur(ablage, stand, job, glb)
            self.assertEqual(optionen['haar'], 'beide')
            with np.load(job.arbeit('sapiens_flaechen.npz')) as d:
                self.assertEqual(d['netz'].tolist(), Blendimportsegmentierung.stempel(job.netzdatei()))

    def test_3_ohne_passende_stimmen_gilt_der_alte_weg_mit_grund(self):
        with _ordner() as o:
            ablage, job, stand, glb = self._vorbereiten(o, eingang_groesse=99)          # das Netz im Eingang weicht ab
            self.assertIsNone(Blendimportsegmentierung.fuer_figur(ablage, stand, job, glb))
            self.assertFalse(job.arbeit('sapiens_flaechen.npz').exists())
            self.assertIsNone(Blendimportsegmentierung.fuer_figur(ablage, {'ergebnis': {}}, job, glb))
            glb.write_bytes(b'g' * 100)                                                  # gleich groß, aber neu geschrieben: eine andere Änderungszeit
            job.netzdatei().write_bytes(b'g' * 100)
            self.assertIsNone(Blendimportsegmentierung.fuer_figur(ablage, stand, job, glb))   # das Körpernetz hat sich seit der Segmentierung geändert


class HautmodellTest(SimpleTestCase):
    """`Meshfigurhautmodell.aus_gruppen` — der Hautton aus den Flächen, die Sapiens als Haut sieht (Zauberer: Bart im Gesicht, zwei Hände, dunkle Reste der Robe als „Arm“ und „Bein“)."""
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from core.daten.meshto3dpfad import Meshto3dpfad

        with Meshto3dpfad():
            from meshfigur_hautmodell import Meshfigurhautmodell
        cls.modell = Meshfigurhautmodell

    @staticmethod
    def _farbe(rgb, n):
        zufall = np.random.default_rng(1)
        return np.clip(np.asarray(rgb, dtype=np.float64) + zufall.normal(0, 3, (n, 3)), 0, 255)

    def test_1_der_bart_ueberstimmt_die_haende_nicht(self):
        gruppen = {'gesicht': self._farbe((146, 127, 114), 4000), 'hand_l': self._farbe((150, 105, 85), 1200), 'hand_r': self._farbe((148, 102, 84), 1300),
                   'arm_r': self._farbe((34, 30, 28), 300), 'bein_l': self._farbe((30, 28, 26), 290)}
        modell = self.modell.aus_gruppen(gruppen)
        self.assertIsNotNone(modell)
        self.assertEqual(sorted(modell.angenommen), ['hand_l', 'hand_r'])
        self.assertLess(abs(modell.hautton[0] - 149), 8)
        self.assertLess(abs(modell.hautton[1] - 103), 8)
        self.assertEqual(modell.befund()['quelle'], self.modell.QUELLE_SAPIENS)
        self.assertFalse(bool(modell.ist_haut(np.array([[44, 41, 40]]))[0]))          # die Robe ist keine Haut

    def test_2_eine_einzige_gruppe_oder_zu_wenig_flaechen_geben_kein_modell(self):
        self.assertIsNone(self.modell.aus_gruppen({'hand_l': self._farbe((150, 105, 85), 1200)}))
        self.assertIsNone(self.modell.aus_gruppen({'hand_l': self._farbe((150, 105, 85), 10), 'hand_r': self._farbe((150, 105, 85), 10)}))
        self.assertIsNone(self.modell.aus_gruppen({}))

    def test_3_gruppen_nach_der_staerksten_klasse_mit_mindeststimmen(self):
        klassen = np.zeros((5, 28), dtype=np.float32)
        klassen[0, 5] = 10                          # Left_Hand, genug Stimmen
        klassen[1, 14] = 3                          # Right_Hand, zu wenig
        klassen[2, 22] = 50                         # Upper_Clothing — keine Hautgruppe
        klassen[3, 2] = 6                           # Face_Neck
        klassen[3, 3] = 2                           # Hair schwächer
        gruppen = self.modell.sapiens_gruppen(klassen)
        self.assertEqual(gruppen['hand_l'].tolist(), [0])
        self.assertEqual(gruppen['hand_r'].tolist(), [])
        self.assertEqual(gruppen['gesicht'].tolist(), [3])
        self.assertTrue(all(2 not in f for f in gruppen.values()))

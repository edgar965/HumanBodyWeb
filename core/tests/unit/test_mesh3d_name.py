# -*- coding: utf-8 -*-
"""Der Name eines Mesh-3D-Auftrags lässt sich auf der Jobseite ändern (12.10.2026): Edgar: „Name des Jobs nicht änderbar (schau die 2D3D Kleider an, da ist der Name änderbar)“.

Ohne Blender, ohne GPU, ohne Datenbank, ohne Platte: der Stand des Imports ist eine Attrappe (`Blendimportablage.stand` / `stand_schreiben`). Nicht gelaufen — läuft nur auf Ansage.

    NameTest       gespeichert wird `quelle.name` UND `einstellungen.eigener_name`; gesäubert und gekürzt wie das Namensfeld des Imports; leer, unbekannt und „rechnet“ schreiben nichts
    VerdrahtungTest  Wächter (Quelltext gelesen): Route, Kopfzeile mit `data-adresse`, Bündel exportiert `Auftragname`, Seite bindet es

Sabotage-Gegenprobe: in `Mesh3dname.setzen` die Zeile mit `einstellungen` streichen → `test_1` rot; die Prüfung `Laeuft` streichen → `test_4` rot; `Blendimportquelle.eigener` durch `str(text)` ersetzen →
`test_2` rot; `Auftragname.binden()` aus der Vorlage streichen → `test_6` rot.
"""

from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from core.daten.blendimportablage import Blendimportablage
from core.dienste.blendimportarbeiter import Blendimportarbeiter
from core.dienste.blendimportquelle import Blendimportquelle
from core.dienste.mesh3dname import Mesh3dname

WEB = Path(__file__).resolve().parents[3]
KENNUNG = '2026.10.12.10.00.00'


def _stand(status='fertig'):
    return {'status': status, 'quelle': {'name': 'Zauberer', 'datei': 'x.glb', 'format': 'glb'}, 'einstellungen': {'name': 'ordner', 'eigener_name': '', 'pfad': 'x'}}


class NameTest(SimpleTestCase):
    databases = set()

    def _setzen(self, text, stand=None, lebt=False):
        stand = stand if stand is not None else _stand()
        with mock.patch.object(Blendimportablage, 'stand', return_value=stand), \
                mock.patch.object(Blendimportarbeiter, 'lebt', return_value=lebt), \
                mock.patch.object(Blendimportablage, 'stand_schreiben') as schreiben:
            try:
                name = Mesh3dname(KENNUNG).setzen(text)
            except ValueError:
                schreiben.assert_not_called()
                raise
            return name, schreiben

    def test_1_gespeichert_wird_der_name_der_quelle_und_der_eigene_name_der_einstellungen(self):
        name, schreiben = self._setzen('Zauberer Neu')
        self.assertEqual(name, 'Zauberer Neu')
        geschrieben = schreiben.call_args.args[0]
        self.assertEqual(geschrieben['quelle']['name'], 'Zauberer Neu')
        self.assertEqual(geschrieben['quelle']['datei'], 'x.glb')                       # der Rest der Quelle bleibt
        self.assertEqual((geschrieben['einstellungen']['name'], geschrieben['einstellungen']['eigener_name']), ('eigen', 'Zauberer Neu'))
        self.assertEqual(geschrieben['einstellungen']['pfad'], 'x')

    def test_2_sonderzeichen_fallen_weg_und_die_laenge_ist_begrenzt_wie_im_namensfeld(self):
        name, _ = self._setzen('  Zauberer <Name>/x  ')
        self.assertEqual(name, 'Zauberer Namex')
        lang, _ = self._setzen('a' * 100)
        self.assertEqual(lang, 'a' * Blendimportquelle.NAME_MAX)
        self.assertEqual(Blendimportquelle('x.glb', 'eigen', 'Zauberer   Zwei', '.glb').name(), 'Zauberer Zwei')    # dieselbe Regel im Import

    def test_3_ein_leerer_name_schreibt_nichts(self):
        for text in ('', '   ', '***/\\<>', None):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self._setzen(text)

    def test_4_waehrend_eines_laufs_geht_nichts(self):
        with self.assertRaises(Mesh3dname.Laeuft):
            self._setzen('Neu', _stand('laeuft'), lebt=True)
        name, _ = self._setzen('Neu', _stand('laeuft'), lebt=False)                      # Status „läuft“, aber kein Prozess mehr: umbenennen geht
        self.assertEqual(name, 'Neu')

    def test_5_ein_unbekannter_auftrag_ist_ein_fehler(self):
        with mock.patch.object(Blendimportablage, 'stand', return_value={}), self.assertRaisesRegex(ValueError, 'Kein Auftrag'):
            Mesh3dname(KENNUNG)
        with self.assertRaisesRegex(ValueError, 'Kein Auftrag'):
            Mesh3dname('../x')


class VerdrahtungTest(SimpleTestCase):
    databases = set()

    def _text(self, *teile):
        return WEB.joinpath(*teile).read_text(encoding='utf-8')

    def test_6_route_kopfzeile_buendel_und_seite_sind_verbunden(self):
        self.assertIn("name='mesh3d_name'", self._text('core', 'urls_mesh3d.py'))
        vorlage = self._text('templates', 'mesh3d_auftrag.html')
        self.assertIn("""id="auftrag-name" data-adresse="{% url 'mesh3d_name' job.kennung %}\"""", vorlage)
        self.assertIn('Auftragname.binden()', vorlage)
        self.assertIn('Auftragname }', vorlage)                                           # aus dem Bündel importiert, nicht einzeln
        self.assertIn("export { Auftragname } from '../gemeinsam/auftragname.js'", self._text('static', 'viewer', 'mesh3d', 'main.js'))

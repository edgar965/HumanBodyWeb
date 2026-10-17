# -*- coding: utf-8 -*-
"""Der Name eines Mesh-3D-Auftrags lässt sich auf der Jobseite ändern (12.10.2026): Edgar: „Name des Jobs nicht änderbar (schau die 2D3D Kleider an, da ist der Name änderbar)“.

Ohne Blender, ohne GPU, ohne Datenbank. `NameTest`: der Stand des Imports ist eine Attrappe (`Blendimportablage.stand` / `stand_schreiben`). `NameDateiTest`: eine echte Ablage in `ProjektTemp/pruefungen`.
Nicht gelaufen — läuft nur auf Ansage.

    NameTest         gespeichert wird `quelle.name` UND `einstellungen.eigener_name`; gesäubert und gekürzt wie das Namensfeld des Imports; leer und unbekannt schreiben nichts
    NameDateiTest    14.10.2026 („klicke ich auf den Editor-Stift …, es tut sich nichts“ — vorher 409 während eines Laufs): `name.json` liegt über `stand.json`, auch wenn ein Lauf den alten Namen
                     schreibt; der neue Lauf übernimmt ihn; während eines Laufs wird nur `name.json` geschrieben; Kopie und „Netz ändern“ nehmen ihn nicht mit
    VerdrahtungTest  Wächter (Quelltext gelesen): Route, Kopfzeile mit `data-adresse`, Bündel exportiert `Auftragname`, Seite bindet es

Sabotage-Gegenprobe: in `Mesh3dname.setzen` die Zeile mit `einstellungen` streichen → `test_1` rot; `Blendimportquelle.eigener` durch `str(text)` ersetzen → `test_2` rot; in `Blendimportablage.stand` die Überlagerung
streichen → `test_7` rot; in `Blendimportlauf.sichern` den Aufruf `_name_nachziehen` streichen → `test_8` rot; in `Mesh3dname.setzen` den frühen Ausstieg während des Laufs streichen → `test_9` rot;
`Auftragname.binden()` aus der Vorlage streichen → `test_6` rot.
"""

import json
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase

from core.daten.blendimportablage import Blendimportablage
from core.dienste.blendimportarbeiter import Blendimportarbeiter
from core.dienste.blendimportlauf import Blendimportlauf
from core.dienste.blendimportquelle import Blendimportquelle
from core.dienste.mesh3dname import Mesh3dname
from core.dienste.ordnerkopie import Ordnerkopie

from ._pruefablage import Pruefablage

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
                mock.patch.object(Blendimportablage, 'name_schreiben') as datei, \
                mock.patch.object(Blendimportablage, 'stand_schreiben') as schreiben:
            try:
                name = Mesh3dname(KENNUNG).setzen(text)
            except ValueError:
                schreiben.assert_not_called()
                datei.assert_not_called()
                raise
            self.name_datei = datei
            return name, schreiben

    def test_1_gespeichert_wird_der_name_der_quelle_und_der_eigene_name_der_einstellungen(self):
        name, schreiben = self._setzen('Zauberer Neu')
        self.assertEqual(name, 'Zauberer Neu')
        geschrieben = schreiben.call_args.args[0]
        self.assertEqual(geschrieben['quelle']['name'], 'Zauberer Neu')
        self.assertEqual(geschrieben['quelle']['datei'], 'x.glb')                       # der Rest der Quelle bleibt
        self.assertEqual((geschrieben['einstellungen']['name'], geschrieben['einstellungen']['eigener_name']), ('eigen', 'Zauberer Neu'))
        self.assertEqual(geschrieben['einstellungen']['pfad'], 'x')
        self.name_datei.assert_called_once_with('Zauberer Neu')

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

    def test_4_auch_waehrend_eines_laufs_wird_der_name_gesetzt(self):
        # bis 14.10.2026 war das ein 409 („Der Auftrag rechnet“) — der Stift „tat sich nichts“
        for lebt in (True, False):
            with self.subTest(lebt=lebt):
                name, _ = self._setzen('Neu', _stand('laeuft'), lebt=lebt)
                self.assertEqual(name, 'Neu')
                self.name_datei.assert_called_once_with('Neu')
        self.assertFalse(hasattr(Mesh3dname, 'Laeuft'))

    def test_5_ein_unbekannter_auftrag_ist_ein_fehler(self):
        with mock.patch.object(Blendimportablage, 'stand', return_value={}), self.assertRaisesRegex(ValueError, 'Kein Auftrag'):
            Mesh3dname(KENNUNG)
        with self.assertRaisesRegex(ValueError, 'Kein Auftrag'):
            Mesh3dname('../x')


class NameDateiTest(SimpleTestCase):
    """Eine echte Ablage (Ordner in `ProjektTemp/pruefungen`), damit `stand()`, `name.json` und der Lauf wirklich zusammenspielen."""
    databases = set()

    def _ablage(self, wurzel):
        patch = mock.patch.object(Blendimportablage, 'wurzel', classmethod(lambda cls: Path(wurzel)))
        patch.start()
        self.addCleanup(patch.stop)
        ablage = Blendimportablage(KENNUNG)
        ablage.stand_schreiben(_stand('laeuft'))
        return ablage

    def test_7_name_json_liegt_ueber_stand_json_auch_wenn_ein_lauf_den_alten_namen_schreibt(self):
        with Pruefablage.ordner() as wurzel:
            ablage = self._ablage(wurzel)
            ablage.name_schreiben('Zauberer Neu')
            stand = ablage.stand()
            self.assertEqual((stand['quelle']['name'], stand['einstellungen']['eigener_name'], stand['einstellungen']['name']), ('Zauberer Neu', 'Zauberer Neu', 'eigen'))
            self.assertEqual(stand['quelle']['datei'], 'x.glb')                          # der Rest des Stands bleibt
            ablage.stand_schreiben(_stand('laeuft'))                                     # ein Arbeitsprozess (alter Code) schreibt „Zauberer“ zurück
            self.assertEqual(ablage.stand()['quelle']['name'], 'Zauberer Neu')
            ablage.name_loeschen()
            self.assertEqual(ablage.stand()['quelle']['name'], 'Zauberer')
            ablage.name_loeschen()                                                       # eine zweite Löschung wirft nicht
            self.assertIsNone(ablage.name())

    def test_8_der_neue_lauf_uebernimmt_den_namen_und_schreibt_ihn_nicht_zurueck(self):
        with Pruefablage.ordner() as wurzel:
            ablage = self._ablage(wurzel)
            lauf = Blendimportlauf(KENNUNG)                                              # kennt „Zauberer“
            lauf.sichern(fortschritt=10)
            self.assertFalse(lauf._name_geaendert)                                       # ohne neuen Namen ändert sich nichts
            ablage.name_schreiben('Zauberer Neu')                                        # der Nutzer benennt um, während der Lauf rechnet
            lauf.sichern(fortschritt=40)
            roh = json.loads((ablage.ordner() / ablage.STAND).read_text(encoding='utf-8'))
            self.assertEqual(roh['quelle']['name'], 'Zauberer Neu')                      # in der Datei selbst, nicht nur überlagert
            self.assertEqual(roh['fortschritt'], 40)                                     # der Rest des Laufs wird geschrieben
            self.assertEqual(lauf.stand['quelle']['name'], 'Zauberer Neu')               # die folgenden Schritte rechnen mit dem neuen Namen
            self.assertTrue(lauf._name_geaendert)

    def test_9_waehrend_eines_laufs_wird_nur_name_json_geschrieben(self):
        with Pruefablage.ordner() as wurzel:
            ablage = self._ablage(wurzel)
            vorher = (ablage.ordner() / ablage.STAND).read_bytes()
            with mock.patch.object(Blendimportarbeiter, 'lebt', return_value=True), mock.patch.object(Mesh3dname, 'angleichen') as angleichen:
                name = Mesh3dname(KENNUNG).setzen('Zauberer Neu')
            self.assertEqual(name, 'Zauberer Neu')
            self.assertEqual((ablage.ordner() / ablage.STAND).read_bytes(), vorher)      # `stand.json` gehört dem Lauf: zwei Schreiber zerrissen sie
            angleichen.assert_not_called()                                               # Modell und Auftrag „Mesh to 3D“ erst nach dem Lauf
            self.assertEqual(ablage.stand()['quelle']['name'], 'Zauberer Neu')           # gesehen wird der neue Name trotzdem
            with mock.patch.object(Blendimportarbeiter, 'lebt', return_value=False), mock.patch.object(Mesh3dname, 'angleichen', return_value={}) as angleichen:
                Mesh3dname(KENNUNG).setzen('Zauberer Drei')
            angleichen.assert_called_once()                                              # ohne Lauf: wie immer, mit Angleichen
            self.assertEqual(json.loads((ablage.ordner() / ablage.STAND).read_text(encoding='utf-8'))['quelle']['name'], 'Zauberer Drei')

    def test_10_kopie_und_netz_aendern_nehmen_den_namen_nicht_mit_und_der_lauf_zieht_nach(self):
        self.assertIn('name.json', Ordnerkopie.NIE_NAMEN)                                # die Kopie hat ihren eigenen Namen
        self.assertIn('self.ablage.name_loeschen()', (WEB / 'core' / 'dienste' / 'mesh3dquellwechsel.py').read_text(encoding='utf-8'))
        lauf = (WEB / 'core' / 'dienste' / 'blendimportlauf.py').read_text(encoding='utf-8')
        self.assertIn('if self._name_geaendert:', lauf)
        self.assertIn('Mesh3dname.nachziehen(self.ablage.kennung)', lauf)
        with mock.patch.object(Mesh3dname, 'angleichen', side_effect=RuntimeError('x')), mock.patch.object(Blendimportablage, 'stand', return_value=_stand()):
            Mesh3dname.nachziehen(KENNUNG)                                               # wirft nie


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

    def test_11_der_stift_schreibt_klick_neben_sich_und_zeigt_einen_fehler_im_oeffnen(self):
        quelle = self._text('static', 'viewer', 'gemeinsam', 'auftragname.js')
        self.assertIn("klickZeigen(text = 'Klick', bleibt = false)", quelle)
        self.assertIn('this.klickZeigen();', quelle)                                      # als ERSTES im Klick, vor Diagnose und Öffnen
        self.assertIn('this.stift.after(this.klick)', quelle)                             # direkt neben dem Stift
        self.assertIn('`Klick – Fehler:', quelle)                                         # wirft bearbeiten(), bleibt der Grund auf der Seite stehen

# -*- coding: utf-8 -*-
"""Netz bearbeiten: einen zurückgenommenen gespeicherten Schnitt wiederholen (14.10.2026, Edgar: „fixe alle offenen punkte“; „Nicht gebaut“ in Abschnitt 17).

    NachfolgerTest   `Mesh3dnetzschnitt.nachfolger/wieder`: die Begleitdateien (`<Name>_bearbeitet_<Zeit>.json`) nennen die Quelle; Kette, jüngster Schnitt, fehlende Datei, gemerkte Suche
    DrahtTest        Quelltext: Knopf in der Vorlage, Werkzeug, Adresse `netzwieder`, Zustand `quelle.nachschnitt`

Sabotage: in `Mesh3dnetzschnitt.nachfolger` den Vergleich `vor.resolve() != ziel` streichen → `NachfolgerTest` rot; in `Mesh3dzustand.von` `nachschnitt` aus der Quelle nehmen → `DrahtTest` rot. Im Chrome durchgespielt (14.10.2026):
Quelle → wiederholen → der frühere Schnitt ist Quelle (44.796 Flächen) → zurücknehmen → 45.338.
"""

import json
import os
import shutil
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.mesh3deingang import Mesh3deingang
from core.dienste.mesh3dnetzschnitt import Mesh3dnetzschnitt
from core.projekt_temp import ProjektTemp

WEB = Path(settings.BASE_DIR)


def quelltext(*teile):
    return WEB.joinpath(*teile).read_text(encoding='utf-8')


class NachfolgerTest(SimpleTestCase):
    """Wiederholen eines zurückgenommenen gespeicherten Schnitts: die Datei, die aus der jetzigen Quelle entstand, steht in der Begleitdatei ihres Nachfolgers (`Mesh3dnetzschnitt.nachfolger`)."""

    databases = set()

    def setUp(self):
        self.wurzel = Path(ProjektTemp.ordner(prefix='netzwieder_'))
        self.addCleanup(shutil.rmtree, self.wurzel, ignore_errors=True)
        patcher = mock.patch.object(Mesh3deingang, 'wurzel', classmethod(lambda cls: self.wurzel))
        patcher.start()
        self.addCleanup(patcher.stop)
        Mesh3dnetzschnitt._NACH.clear()
        self.addCleanup(Mesh3dnetzschnitt._NACH.clear)

    def _glb(self, kennung, name, quelle=None, zeit=None):
        """Eine Datei im Eingangsordner; mit `quelle` eine Begleitdatei, die sie als Schnitt aus dieser Quelle ausweist."""
        ordner = self.wurzel / kennung / 'Figur'
        ordner.mkdir(parents=True, exist_ok=True)
        glb = ordner / name
        glb.write_bytes(b'glb')
        if quelle is not None:
            begleit = glb.with_suffix('.json')
            begleit.write_text(json.dumps({'quelle': {'datei': str(quelle)}}), encoding='utf-8')
            if zeit is not None:
                os.utime(begleit, (zeit, zeit))
        return glb

    def test_der_schnitt_aus_der_quelle_wird_gefunden_und_die_kette_geht_weiter(self):
        original = self._glb('2026.10.13.19.00.00', 'Figur.glb')
        eins = self._glb('2026.10.14.10.00.00', 'Figur_bearbeitet_2026.10.14.10.00.00.glb', quelle=original)
        zwei = self._glb('2026.10.14.11.00.00', 'Figur_bearbeitet_2026.10.14.11.00.00.glb', quelle=eins)
        Mesh3dnetzschnitt._NACH.clear()
        self.assertEqual(Mesh3dnetzschnitt.nachfolger(original), eins)
        self.assertEqual(Mesh3dnetzschnitt.nachfolger(eins), zwei)
        self.assertIsNone(Mesh3dnetzschnitt.nachfolger(zwei), 'nach dem letzten Schnitt gibt es nichts zu wiederholen')

    def test_bei_mehreren_schnitten_aus_derselben_quelle_gilt_der_juengste(self):
        original = self._glb('2026.10.13.19.00.00', 'Figur.glb')
        alt = self._glb('2026.10.14.10.00.00', 'Figur_bearbeitet_2026.10.14.10.00.00.glb', quelle=original, zeit=1_000_000_000)
        neu = self._glb('2026.10.14.12.00.00', 'Figur_bearbeitet_2026.10.14.12.00.00.glb', quelle=original, zeit=1_900_000_000)
        Mesh3dnetzschnitt._NACH.clear()
        self.assertEqual(Mesh3dnetzschnitt.nachfolger(original), neu)
        self.assertNotEqual(neu, alt)

    def test_ohne_datei_oder_ohne_begleitdatei_gibt_es_keinen_nachfolger(self):
        original = self._glb('2026.10.13.19.00.00', 'Figur.glb')
        weg = self._glb('2026.10.14.10.00.00', 'Figur_bearbeitet_2026.10.14.10.00.00.glb', quelle=original)
        weg.unlink()
        Mesh3dnetzschnitt._NACH.clear()
        self.assertIsNone(Mesh3dnetzschnitt.nachfolger(original), 'die Begleitdatei allein genügt nicht: die GLB fehlt')
        weg.write_bytes(b'glb')
        weg.with_suffix('.json').write_text('{kaputt', encoding='utf-8')
        Mesh3dnetzschnitt._NACH.clear()
        self.assertIsNone(Mesh3dnetzschnitt.nachfolger(original), 'eine kaputte Begleitdatei wird übergangen, nicht gemeldet')
        self.assertIsNone(Mesh3dnetzschnitt.nachfolger(''))
        self.assertIsNone(Mesh3dnetzschnitt.nachfolger(None))

    def test_ein_neuer_schnitt_wird_trotz_gemerkter_suche_gefunden(self):
        original = self._glb('2026.10.13.19.00.00', 'Figur.glb')
        self.assertIsNone(Mesh3dnetzschnitt.nachfolger(original))
        neu = self._glb('2026.10.14.10.00.00', 'Figur_bearbeitet_2026.10.14.10.00.00.glb', quelle=original)
        self.assertEqual(Mesh3dnetzschnitt.nachfolger(original), neu, 'der Eingangsordner hat sich geändert: die gemerkte Antwort gilt nicht mehr')

    def test_wieder_macht_den_nachfolger_zur_quelle(self):
        original = self._glb('2026.10.13.19.00.00', 'Figur.glb')
        eins = self._glb('2026.10.14.10.00.00', 'Figur_bearbeitet_2026.10.14.10.00.00.glb', quelle=original)
        dienst = object.__new__(Mesh3dnetzschnitt)
        dienst.stand = {'quelle': {'datei': str(original)}}
        with mock.patch.object(Mesh3dnetzschnitt, 'uebernehmen', return_value={'uebernommen': True}) as uebernehmen:
            antwort = dienst.wieder()
        uebernehmen.assert_called_once_with(eins)
        self.assertEqual(antwort, {'uebernommen': True, 'datei': str(eins)})
        dienst.stand = {'quelle': {'datei': str(eins)}}
        with self.assertRaisesRegex(ValueError, 'nichts zu wiederholen'):
            dienst.wieder()



class DrahtTest(SimpleTestCase):
    databases = set()

    def test_gespeicherten_schnitt_wiederholen_ist_von_der_vorlage_bis_zum_server_verdrahtet(self):
        self.assertIn('id="netz-wz-schnittwieder"', quelltext('templates', 'mesh3d_auftrag.html'))
        werkzeug = quelltext('static', 'viewer', 'mesh3d', 'mesh3dnetzwerkzeug.js')
        self.assertIn("'rueckgaengig', 'schnittwieder']", werkzeug)
        self.assertIn("this.knoepfe.schnittwieder.addEventListener('click', () => this._gespeichertesWieder())", werkzeug)
        self.assertIn('schnittwieder: !w || this._arbeitet || !this.seite.zustand?.quelle?.nachschnitt', werkzeug, 'aktiv nur, wenn der Server einen Nachfolger der Quelle kennt')
        self.assertIn('/netzwieder/', quelltext('static', 'viewer', 'mesh3d', 'mesh3dnetzspeichern.js'))
        self.assertIn("'api/mesh3d/<kennung:kennung>/netzwieder/', Mesh3dnetzschnittendpunkte.wieder", quelltext('core', 'urls_mesh3d.py'))
        self.assertIn('def wieder(request, kennung)', quelltext('core', 'api', 'mesh3dnetzschnitt.py'))
        self.assertIn("'nachschnitt': cls._nachschnitt(quelle.get('datei'))", quelltext('core', 'dienste', 'mesh3dzustand.py'), 'der Zustand trägt den Nachfolger der Quelle')

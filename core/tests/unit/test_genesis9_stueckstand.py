# -*- coding: utf-8 -*-
"""Ein eigenes Stück, das unter derselben Kennung neu geschrieben wird, bekommt eine neue Antwort (08.10.2026).

Gemessen am zweiten Import von „cute girl": Die `.duf` trug Detailnormale und Alpha-Schnitt, die Antwort an den Browser nicht —
der Antwortvorrat lieferte die gemerkte Antwort von vor dem Import (`G9antworten`, Schlüssel ohne Stückstand).

1. `G9stueckstand.von` gibt die Änderungszeit der `.duf` eines EIGENEN Stücks; für Daz-Inhalt, ohne Datei, ohne Eintrag 0.
2. Schreibt man die Datei neu, ändert sich der Wert — und damit der Schlüssel des Antwortvorrats; solange sie gleich bleibt,
   bleibt auch der Schlüssel gleich (der Vorrat nützt also weiter).
3. Daz-Stücke ändern ihren Schlüssel nicht, wenn jemand die Datei anfasst (`vergessen()` bleibt ihr Weg).
5. (09.10.2026, Stiefel der „Asian Female": Fuß im Browser 55°, im neu geschriebenen Stück 18°) Die Fußdrehung eines Absatzschuhs formt die
   FIGUR; der Körper-Schlüssel trägt deshalb den Stand der Stücke aus `rumpf['griffe']` (`G9stueckstand.griffe`).

Sabotage-Gegenprobe: in `von` `eintrag.get('eigen')` aus der Bedingung nehmen → Fall 3 rot; `G9stueckstand.von(eintrag)` aus
`G9antworten.schluessel` streichen → Fall 2 rot; `G9stueckstand.griffe(rumpf)` aus `G9antworten.schluessel` streichen → Fall 5 rot.

Nicht gelaufen (Stand 08.10.2026; Fall 5 09.10.2026) — läuft nur auf Ansage.
"""

import os
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.garderobe import G9garderobe
from Genesis9.stueckstand import G9stueckstand

from core.dienste.g9antworten import G9antworten

from ._pruefablage import Pruefablage


class StueckstandTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        gebaut = Pruefablage.ordner('stueckstand_')
        self.ordner = Path(gebaut.__enter__())
        self.addCleanup(gebaut.__exit__, None, None, None)
        self.duf = self.ordner / 'stueck.duf'
        self.duf.write_text('{}', encoding='utf-8')
        datei = mock.patch.object(G9garderobe, 'datei', classmethod(lambda cls, eintrag: self.duf))
        datei.start()
        self.addCleanup(datei.stop)

    def _eintrag(self, **felder):
        return {'id': 'cute_girl_shirt', 'datei': 'EIGEN/stueck.duf', 'wurzel': 'People', 'eigen': True, 'art': 'kleidung',
                **felder}

    def _schluessel(self, eintrag):
        return G9antworten.schluessel('kleid', 'cute_girl_shirt', {'regler': {}}, 1, eintrag, False)

    def _anfassen(self):
        """Die Datei neu schreiben: die Änderungszeit springt (Dateisysteme runden grob — also einen Schritt weiter)."""
        stand = self.duf.stat().st_mtime_ns
        os.utime(self.duf, ns=(stand + 5_000_000_000, stand + 5_000_000_000))

    def test_1_eigenes_stueck_gibt_den_stand_der_datei(self):
        self.assertEqual(G9stueckstand.von(self._eintrag()), self.duf.stat().st_mtime_ns)

    def test_2_neu_geschrieben_heisst_neuer_schluessel(self):
        eintrag = self._eintrag()
        vorher = self._schluessel(eintrag)
        self.assertEqual(vorher, self._schluessel(eintrag), 'ohne Änderung bleibt der Schlüssel (der Vorrat nützt)')
        self._anfassen()
        self.assertNotEqual(vorher, self._schluessel(eintrag), 'die Datei wurde neu geschrieben: neue Antwort')

    def test_3_daz_inhalt_und_fehlende_angaben_geben_null(self):
        daz = self._eintrag(eigen=False)
        self.assertEqual(G9stueckstand.von(daz), 0)
        vorher = self._schluessel(daz)
        self._anfassen()
        self.assertEqual(vorher, self._schluessel(daz), 'Daz-Inhalt: der Schlüssel bleibt (dafür gibt es vergessen())')
        self.assertEqual(G9stueckstand.von(None), 0)
        self.assertEqual(G9stueckstand.von({}), 0)
        self.assertEqual(G9stueckstand.von(self._eintrag(datei='')), 0)

    def test_4_fehlt_die_datei_bleibt_es_null_statt_eines_fehlers(self):
        self.duf.unlink()
        self.assertEqual(G9stueckstand.von(self._eintrag()), 0)

    def test_5_der_stand_eines_stuecks_mit_griff_steht_im_schluessel_des_koerpers(self):
        """Der Absatzschuh der .blend formt die FIGUR (Fußdrehung): wird er neu geschrieben, braucht der Körper eine neue Antwort."""
        mit, ohne = {'regler': {}, 'griffe': ['asian_female_schuhe']}, {'regler': {}}
        schluessel = lambda rumpf: G9antworten.schluessel('koerper', 'basis', rumpf, 1, {}, False)  # noqa: E731
        with mock.patch.object(G9garderobe, 'eintrag', return_value=self._eintrag()):
            vorher_mit, vorher_ohne = schluessel(mit), schluessel(ohne)
            self.assertEqual(vorher_mit, schluessel(mit), 'ohne Änderung bleibt der Schlüssel')
            self._anfassen()
            self.assertNotEqual(vorher_mit, schluessel(mit), 'der Schuh wurde neu geschrieben: der Körper bekommt eine neue Antwort')
            self.assertEqual(vorher_ohne, schluessel(ohne), 'ohne Griff im Rumpf ändert sich am Körper nichts')

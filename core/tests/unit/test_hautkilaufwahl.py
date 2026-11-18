# -*- coding: utf-8 -*-
"""Lauf der Haut-KI je Job (`Hautkilaufwahl`, `Fotogenesispshuman` Feld `haut_ki_lauf`, 17.11.2026). Kunstordner unter `ProjektTemp/`, wird gelöscht.

1. `laeufe`: der eingesetzte und die jüngeren mit `netz.pt`, jüngster zuerst; ältere und solche ohne `netz.pt` nicht. `auswahl`: zuerst '' = eingesetzt.
2. `kurz`: Datum + Name ohne `hautki_`.
3. `Fotogenesispshuman.setzen`: ein wählbarer Lauf landet in der job.json, '' auch, ein unbekannter oder älterer gibt ValueError; `lesen` liefert ihn zurück.

Sabotage (nicht gelaufen): in `laeufe` das `n >= eingesetzt` streichen → Fall 1 rot (der alte Lauf steht drin); in `setzen` die Prüfung `gueltig` streichen → Fall 3 rot.
Geschrieben, nicht gelaufen (Tests nur auf Ansage).
"""
import json
import os
import shutil
import unittest
from pathlib import Path
from unittest import mock

from core.dienste.fotogenesispshuman import Fotogenesispshuman
from core.dienste.hautkilaufwahl import Hautkilaufwahl

ALT, EINGESETZT, NEU, OHNE = '2026.10.25.13.41_hautki_alt', '2026.11.05.14.55_hautki_rand', '2026.11.17.00.11_hautki_atlas53', '2026.11.18.09.00_hautki_ohne_netz'


class HautkilaufwahlTest(unittest.TestCase):
    databases = []

    def setUp(self):
        self.ordner = Path(r'A:\3DTools\ProjektTemp') / ('_test_hautkilaufwahl_%d' % os.getpid())
        for name in (ALT, EINGESETZT, NEU, OHNE):
            (self.ordner / 'laeufe' / name).mkdir(parents=True)
            if name != OHNE:
                (self.ordner / 'laeufe' / name / 'netz.pt').write_bytes(b'')
        self.addCleanup(shutil.rmtree, self.ordner, True)
        for name, wert in (('ordner', self.ordner / 'laeufe'), ('eingesetzt', EINGESETZT)):
            patcher = mock.patch.object(Hautkilaufwahl, name, return_value=wert)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_1_laeufe(self):
        self.assertEqual(Hautkilaufwahl.laeufe(), [NEU, EINGESETZT])
        self.assertEqual([w for w, _t in Hautkilaufwahl.auswahl()], ['', NEU])

    def test_2_kurz(self):
        self.assertEqual(Hautkilaufwahl.kurz(NEU), '17.11. atlas53')
        self.assertEqual(Hautkilaufwahl.kurz('ohne_zeit'), 'ohne_zeit')

    def test_3_setzen(self):
        job = {'art': 'foto', 'ordner': self.ordner}
        (self.ordner / 'job.json').write_text(json.dumps({'name': 'k', 'pshuman': {'haut_ki': True}}), encoding='utf-8')
        self.assertEqual(Fotogenesispshuman.setzen(job, {'haut_ki_lauf': NEU})['haut_ki_lauf'], NEU)
        gespeichert = json.loads((self.ordner / 'job.json').read_text(encoding='utf-8'))['pshuman']
        self.assertEqual((gespeichert['haut_ki'], gespeichert['haut_ki_lauf']), (True, NEU))
        self.assertEqual(Fotogenesispshuman.setzen(job, {'haut_ki_lauf': ''})['haut_ki_lauf'], '')
        for falsch in (ALT, OHNE, 'gibt_es_nicht', 3):
            with self.assertRaises(ValueError):
                Fotogenesispshuman.setzen(job, {'haut_ki_lauf': falsch})


if __name__ == '__main__':
    unittest.main()

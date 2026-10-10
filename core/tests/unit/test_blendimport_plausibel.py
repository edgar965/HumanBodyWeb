# -*- coding: utf-8 -*-
"""Wächter gegen eine Figur, die nicht zum Körper passt — unabhängig von der Ursache (Edgar, 10.10.2026: „warum musst du immer manuelle schritte machen,
und der Import ist nicht generisch??").

Rainy, seori und Rosemary Winters waren „fertig", obwohl „Mesh to 3D" die Figur ins Leere gepasst hatte; jedes Mal war die Ursache eine andere (Maßstab,
Körper ohne Beine, Körper ohne Kopf). Gemessen an allen zehn gespeicherten Läufen (`ProjektTemp/_wegwerf/blendimport_massstab/plausibel_messung.py`):
Median des Abstands passend 0,77–1,62 mm, nicht passend 65,8 / 87,0 / 315,2 mm; Figurhöhe nach dem Maßstab passend 1,73–1,89 m, nicht passend 3,07–3,28 m.

1. Figurhöhe: die gemessenen guten Höhen bestehen, die schlechten melden; ohne Zahl kein Befund.
2. Abstand: die gemessenen guten Mediane bestehen, die schlechten melden; Schwelle genau bei 10 mm.
3. `pruefen` wirft mit dem Befund, außer „trotzdem" — ohne Befund wirft es nie.
4. `befunde` liest einen gespeicherten Stand: die Werte von Rosemary (alt) ergeben zwei Sätze, die von Rainy keinen, ein Stand ohne Zahlen keinen.
5. `markieren` hängt jedem Modell den Befund seines Imports an; ein Modell ohne Herkunft bekommt `[]`.
6. Im Lauf: „export" hält bei einer unmenschlichen Figurhöhe an, „haut" ruft die Prüfung des Abstands VOR dem Backen auf (und reicht „trotzdem" durch).

Sabotage-Gegenprobe: `MAX_MEDIAN_MM` auf 100 → Fall 2 und 4 rot; `FIGUR_M` auf (0.5, 4.0) → Fall 1 und 6 rot; in `Blendimporthaut.backen` den Aufruf `pruefen(...)`
hinter den Blender-Lauf setzen → Fall 6b rot.

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""

from unittest import mock

from django.test import SimpleTestCase

from core.dienste.blendimportlauf import Blendimportlauf
from core.dienste.blendimportplausibel import Blendimportplausibel

#: Median in mm und Anteil über 8 mm der gemessenen Läufe.
GUT = [(0.77, 0.0333), (0.82, 0.1028), (0.99, 0.1003), (1.01, 0.0984), (1.34, 0.1963), (1.62, 0.1728)]
SCHLECHT = [(65.81, 0.7329), (86.99, 0.6972), (315.18, 0.7218)]


def _abstand(median, anteil):
    return {'median_mm': median, 'ueber_8mm': anteil}


class PlausibelTest(SimpleTestCase):
    databases = set()

    def test_1_figurhoehe(self):
        for hoehe in (1.727, 1.734, 1.736, 1.887):
            self.assertIsNone(Blendimportplausibel.figurhoehe({'hoehe_figur_m': hoehe}), hoehe)
        for hoehe in (3.072, 3.178, 3.278):
            befund = Blendimportplausibel.figurhoehe({'hoehe_figur_m': hoehe})
            self.assertIn('Maßstab', befund)
            self.assertIn(('%.2f' % hoehe).replace('.', ','), befund)
        self.assertIsNone(Blendimportplausibel.figurhoehe(None))
        self.assertIsNone(Blendimportplausibel.figurhoehe({}))

    def test_2_abstand(self):
        for median, anteil in GUT:
            self.assertIsNone(Blendimportplausibel.abstand(_abstand(median, anteil)), median)
        for median, anteil in SCHLECHT:
            befund = Blendimportplausibel.abstand(_abstand(median, anteil))
            self.assertIn('passt nicht zum Körper', befund)
            self.assertIn('%.0f mm' % median, befund)
        self.assertIsNone(Blendimportplausibel.abstand(_abstand(10.0, 0.5)))
        self.assertIsNotNone(Blendimportplausibel.abstand(_abstand(10.01, 0.5)))
        self.assertIsNone(Blendimportplausibel.abstand(None))

    def test_3_pruefen(self):
        with self.assertRaises(ValueError) as fehler:
            Blendimportplausibel.pruefen('Die Figur passt nicht')
        self.assertIn('Die Figur passt nicht', str(fehler.exception))
        self.assertIn('bevor er Stunden rechnet', str(fehler.exception))
        Blendimportplausibel.pruefen('Die Figur passt nicht', trotzdem=True)
        Blendimportplausibel.pruefen(None)

    def test_4_befunde_aus_dem_stand(self):
        rosemary = {'ergebnis': {'export': {'koerper': {'hoehe_figur_m': 3.278}}, 'haut': {'abstand': _abstand(86.99, 0.6972)}}}
        rainy = {'ergebnis': {'export': {'koerper': {'hoehe_figur_m': 1.736}}, 'haut': {'abstand': _abstand(0.77, 0.0333)}}}
        self.assertEqual(len(Blendimportplausibel.befunde(rosemary)), 2)
        self.assertEqual(Blendimportplausibel.befunde(rainy), [])
        self.assertEqual(Blendimportplausibel.befunde({'ergebnis': {}}), [])
        self.assertEqual(Blendimportplausibel.befunde({}), [])

    def test_5_markieren(self):
        figuren = [{'name': 'A', 'herkunft': {'import': '1.2.3'}}, {'name': 'B', 'herkunft': {}}, {'name': 'C'}]
        with mock.patch.object(Blendimportplausibel, 'fuer_import', side_effect=lambda k: ['kaputt'] if k == '1.2.3' else []):
            aus = Blendimportplausibel.markieren(figuren)
        self.assertEqual([f['befund'] for f in aus], [['kaputt'], [], []])
        # Eine ungültige Kennung (kein Import) ergibt keinen Befund und keinen Fehler.
        self.assertEqual(Blendimportplausibel.fuer_import(None), [])
        self.assertEqual(Blendimportplausibel.fuer_import('kein import'), [])


def _lauf(unvollstaendig='anhalten'):
    """Ein `Blendimportlauf` ohne Ablage: nur, was `_export` und `_haut` anfassen."""
    lauf = object.__new__(Blendimportlauf)
    lauf.stand = {'einstellungen': {'unvollstaendig': unvollstaendig, 'kachel_px': '8192'}, 'rollen': [], 'quelle': {'datei': 'x.blend', 'name': 'x'}}
    lauf.ablage = mock.MagicMock()
    lauf.melden = mock.Mock()
    lauf.ergebnis = mock.Mock()
    lauf.inventar = mock.Mock(return_value={'netze': []})
    lauf.blend = mock.Mock(return_value='x.blend')
    lauf.job = mock.Mock()
    lauf.zusatzregler = mock.Mock(return_value={})
    return lauf


class LaufTest(SimpleTestCase):
    databases = set()

    def _export(self, hoehe):
        lauf = _lauf()
        with mock.patch('core.dienste.blendimportblender.Blendimportblender'), \
                mock.patch('core.dienste.blendimportrollen.Blendimportrollen') as rollen, \
                mock.patch('core.dienste.blendimportkoerperpruefung.Blendimportkoerperpruefung.pruefen',
                           return_value={'hoehe_figur_m': hoehe}):
            rollen.return_value.zuordnen.return_value = []
            lauf._export()
        return lauf

    def test_6a_export_haelt_bei_unmenschlicher_hoehe_an(self):
        with self.assertRaises(ValueError) as fehler:
            self._export(3.278)
        self.assertIn('Maßstab', str(fehler.exception))
        lauf = self._export(1.73)
        lauf.ergebnis.assert_called_once()

    def _haut(self, abstand, unvollstaendig='anhalten'):
        lauf = _lauf(unvollstaendig)
        zeiten = []

        def backen(blend, pruefen=None):
            pruefen(abstand)                  # der Abstand ist bekannt, BEVOR Blender backt
            zeiten.append('gebacken')
            return {}, {'abstand': abstand}

        with mock.patch('core.dienste.blendimporthaut.Blendimporthaut') as haut:
            haut.return_value.backen.side_effect = backen
            try:
                lauf._haut()
            finally:
                self.gebacken = bool(zeiten)
        return lauf

    def test_6b_haut_haelt_vor_dem_backen_an(self):
        with self.assertRaises(ValueError) as fehler:
            self._haut(_abstand(86.99, 0.6972))
        self.assertIn('passt nicht zum Körper', str(fehler.exception))
        self.assertFalse(self.gebacken)
        lauf = self._haut(_abstand(0.77, 0.0333))
        self.assertTrue(self.gebacken)
        lauf.ergebnis.assert_called_once()

    def test_6c_trotzdem_importieren_geht_durch(self):
        self._haut(_abstand(86.99, 0.6972), unvollstaendig='weiter')
        self.assertTrue(self.gebacken)

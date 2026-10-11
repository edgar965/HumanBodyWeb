# -*- coding: utf-8 -*-
"""`Dazgeograftumriss`, `Modellstuecke` und die Nummern des Zuschnitts (11.10.2026) — an Kunstflächen, ohne Daz-Bibliothek.

Edgar: „baue ein besseres cute Girl 3. Baue alle Erkenntnisse, die wir vorher hatten, in die neue Klasse hinein, sodass sie standardmäßig bei allen Modellen angewandt wird" und „Warum liegen die [Stücke von
Daz, Daz1, Daz2] noch in der Bibliothek?".

Kunstwelt: Haut = zwei Platten (vorn z = 0, hinten z = −40 mm, je 41 × 41 Punkte, Abstand 2 mm, ±40 mm); das Loch = die Dreiecke der VORDEREN Platte mit Mitte in ±20 mm, sein Ring ein Quadrat von ±20 mm;
das Geograft ein Gitter von 31 × 31 Punkten (Abstand 2 mm, ±30 mm) 5 mm über der vorderen Platte.

1. `abstand`: innen negativ, außen positiv, gleich bei jeder Höhe über der Haut; ein Punkt über der HINTEREN Platte ist außen, obwohl er in der Vorderansicht mitten im Ring liegt (der erste Versuch mit einem
   Polygon in (x, y) hielt Vorder- und Rückseite nicht auseinander: Rand des Geografts bis 85,5 mm neben dem Ring).
2. `zuschneiden`: alle übrigen Punkte liegen im Loch (plus `UEBERSTAND_M`), die Fläche entspricht dem Quadrat, jeder Punkt wird benutzt, `herkunft` nennt für alte Punkte ihre alte Nummer (gleiche Lage) und −1 für neue.
3. Eine lose Insel im Loch fällt weg und steht im Bericht; liegt das Geograft nicht über dem Loch, wirft der Schnitt `ValueError`.
4. `herkunft_ablegen` / `herkunft_lesen`: Hin und zurück; ohne Zuschnitt (`null`) und ohne Datei gibt es `None`.
5. `Dazgeograftmorphbasis._zu_zugeschnitten`: Punkt des Basis-Stücks → Punkt des zugeschnittenen, −1 für weggeschnittene — bei Stufe 1 und über die Stufen.
6. `Modellstuecke`: nur die Stücke aus `herkunft.daz_stuecke` gehen, und nur wenn kein anderes Modell sie trägt; ein Stück, das nicht (mehr) eigen ist, bleibt; `Modellablage.loeschen` ruft es nach dem Löschen der Datei.

Sabotage-Gegenprobe (nicht gelaufen): in `abstand` den Fußpunkt durch die Vorderansicht ersetzen (`ring[:, :2]` gegen `punkte[:, :2]`) macht Fall 1 rot; `UEBERSTAND_M` auf −0,005 macht Fall 2 rot (Punkte außerhalb);
`herkunft` ohne die Umrechnung (`benutzt` statt `np.where(benutzt < len(punkte), benutzt, -1)`) macht Fall 2 rot.
"""
import json
from pathlib import Path
from unittest import mock

import numpy as np
import trimesh
from django.test import SimpleTestCase, override_settings

from core.dienste.dazgeograftmorphbasis import Dazgeograftmorphbasis
from core.dienste.dazgeograftumriss import Dazgeograftumriss
from core.dienste.modellablage import Modellablage
from core.dienste.modellstuecke import Modellstuecke

from ._pruefablage import Pruefablage

N, ABSTAND = 41, 0.002


def platte(z):
    """`(punkte, dreiecke)`: Gitter 41 × 41, Abstand 2 mm, in der Ebene `z`."""
    punkte = np.array([[(i - N // 2) * ABSTAND, (j - N // 2) * ABSTAND, z] for j in range(N) for i in range(N)])
    dreiecke = []
    for j in range(N - 1):
        for i in range(N - 1):
            a = j * N + i
            dreiecke += [[a, a + 1, a + N + 1], [a, a + N + 1, a + N]]
    return punkte, np.array(dreiecke, dtype=np.int64)


def haut_und_loch():
    """`(haut, maske, ring)`: zwei Platten, das Loch nur in der vorderen."""
    vorn, d_vorn = platte(0.0)
    hinten, d_hinten = platte(-0.040)
    haut = trimesh.Trimesh(np.vstack([vorn, hinten]), np.vstack([d_vorn, d_hinten + len(vorn)]), process=False)
    mitte = haut.triangles_center
    maske = np.zeros(len(haut.faces), dtype=bool)
    maske[:len(d_vorn)] = (np.abs(mitte[:len(d_vorn), 0]) < 0.020) & (np.abs(mitte[:len(d_vorn), 1]) < 0.020)
    ring = np.array([[-0.020, -0.020, 0.0], [0.020, -0.020, 0.0], [0.020, 0.020, 0.0], [-0.020, 0.020, 0.0]])
    return haut, maske, ring


def geograft(hoehe=0.005, breite=31, mitte=(0.0, 0.0)):
    """`(punkte, dreiecke, uv_ecken)`: Gitter `breite` × `breite`, Abstand 2 mm, in der Höhe `hoehe` über der vorderen Platte."""
    punkte = np.array([[mitte[0] + (i - breite // 2) * ABSTAND, mitte[1] + (j - breite // 2) * ABSTAND, hoehe] for j in range(breite) for i in range(breite)])
    dreiecke = []
    for j in range(breite - 1):
        for i in range(breite - 1):
            a = j * breite + i
            dreiecke += [[a, a + 1, a + breite + 1], [a, a + breite + 1, a + breite]]
    dreiecke = np.array(dreiecke, dtype=np.int64)
    return punkte, dreiecke, np.zeros((len(dreiecke), 3, 2))


class DazgeograftumrissTest(SimpleTestCase):
    databases = set()

    def test_1_innen_ist_negativ_und_die_hoehe_aendert_nichts_und_die_rueckseite_ist_aussen(self):
        haut, maske, ring = haut_und_loch()
        w = Dazgeograftumriss.abstand(haut, maske, ring, np.array([[0.0, 0.0, 0.005], [0.0, 0.0, 0.015], [0.030, 0.0, 0.005], [0.0, 0.0, -0.035]]))
        self.assertAlmostEqual(float(w[0]), -0.020, delta=0.0006)
        self.assertAlmostEqual(float(w[1]), float(w[0]), delta=0.0006, msg='die Höhe über der Haut zählt nicht')
        self.assertAlmostEqual(float(w[2]), 0.010, delta=0.0006)
        self.assertGreater(float(w[3]), 0.0, 'über der hinteren Platte: außen, obwohl in der Vorderansicht mitten im Ring')

    def test_2_der_zuschnitt_behaelt_das_quadrat_und_die_nummern(self):
        haut, maske, ring = haut_und_loch()
        punkte, dreiecke, uv = geograft()
        neu, d, uv_neu, herkunft, bericht = Dazgeograftumriss.zuschneiden(punkte, dreiecke, uv, haut, maske, ring)
        w = Dazgeograftumriss.abstand(haut, maske, ring, neu) - Dazgeograftumriss.UEBERSTAND_M
        self.assertLess(float(w.max()), 0.0002, 'alle Punkte liegen im Loch (plus Überstand)')
        flaeche = float(trimesh.Trimesh(neu, d, process=False).area)
        erwartet = (0.040 + 2 * Dazgeograftumriss.UEBERSTAND_M) ** 2
        self.assertAlmostEqual(flaeche, erwartet, delta=0.03 * erwartet)
        self.assertTrue(np.array_equal(np.unique(d), np.arange(len(neu))), 'jeder Punkt wird benutzt')
        self.assertEqual(len(uv_neu), len(d))
        alt = herkunft >= 0
        self.assertEqual(int((~alt).sum()), bericht['schnittpunkte'])
        self.assertGreater(int((~alt).sum()), 0)
        self.assertLess(float(np.abs(neu[alt] - punkte[herkunft[alt]]).max()), 1e-12, 'die alte Nummer nennt denselben Punkt')
        self.assertEqual(len(np.unique(herkunft[alt])), int(alt.sum()), 'keine alte Nummer doppelt')

    def test_3_eine_lose_insel_faellt_weg_und_ohne_ueberdeckung_gibt_es_einen_fehler(self):
        haut, maske, ring = haut_und_loch()
        punkte, dreiecke, uv = geograft()
        insel, d_insel, uv_insel = geograft(hoehe=0.020, breite=4)
        ganz = (np.vstack([punkte, insel]), np.vstack([dreiecke, d_insel + len(punkte)]), np.concatenate([uv, uv_insel]))
        neu, _d, _uv, _h, bericht = Dazgeograftumriss.zuschneiden(*ganz, haut, maske, ring)
        self.assertEqual(bericht['inseln_weg'], len(d_insel))
        self.assertLess(float(neu[:, 2].max()), 0.010, 'die Insel (20 mm hoch) ist nicht dabei')
        weit, d_weit, uv_weit = geograft(mitte=(0.2, 0.0))
        with self.assertRaises(ValueError):
            Dazgeograftumriss.zuschneiden(weit, d_weit, uv_weit, haut, maske, ring)

    def test_4_die_herkunft_geht_hin_und_zurueck(self):
        with Pruefablage.ordner('umriss_') as ordner:
            duf = Path(ordner) / 'x.duf'
            ziel = Dazgeograftumriss.herkunft_ablegen(duf, 2, 16741, np.array([3, -1, 5]))
            self.assertEqual(ziel.name, 'x.herkunft.json')
            with mock.patch('Genesis9.garderobe.G9garderobe.datei', return_value=duf):
                gelesen = Dazgeograftumriss.herkunft_lesen({'id': 'x'})
                self.assertEqual((gelesen['stufe'], gelesen['nahtfrei'], gelesen['herkunft'].tolist()), (2, 16741, [3, -1, 5]))
                Dazgeograftumriss.herkunft_ablegen(duf, 2, 16741, None)
                self.assertIsNone(Dazgeograftumriss.herkunft_lesen({'id': 'x'}), 'ohne Zuschnitt (null) gilt eine ältere Datei nicht weiter')
                ziel.unlink()
                self.assertIsNone(Dazgeograftumriss.herkunft_lesen({'id': 'x'}), 'ohne Datei')

    def test_5_der_punkt_des_basis_stuecks_findet_seinen_platz_im_zugeschnittenen(self):
        stufe1 = {'stufe': 1, 'nahtfrei': 6, 'herkunft': np.array([2, 3, 5])}
        self.assertEqual(Dazgeograftmorphbasis._zu_zugeschnitten(stufe1, 6, 'frau').tolist(), [-1, -1, 0, 1, -1, 2])
        stufe2 = {'stufe': 2, 'nahtfrei': 6, 'herkunft': np.array([4, 0, 2, -1])}
        with mock.patch('core.dienste.dazgeograftstufenzuordnung.Dazgeograftstufenzuordnung.zuordnen', return_value=np.array([4, 2, 0, 5])) as zuordnen:
            self.assertEqual(Dazgeograftmorphbasis._zu_zugeschnitten(stufe2, 3, 'frau').tolist(), [0, 2, 1], 'Basis 0 → Rohpunkt 4 → Platz 0; 1 → 2 → Platz 2; 2 → 0 → Platz 1')
        zuordnen.assert_called_once_with('frau', 3, 6)


class ModellstueckeTest(SimpleTestCase):
    databases = set()

    def test_6a_nur_die_genannten_stuecke_gehen_und_nur_wenn_kein_modell_sie_traegt(self):
        daten = {'figur': {'herkunft': {'import': 'x', 'daz_stuecke': ['m_daz_scham', 'andere']}}}
        self.assertEqual(Modellstuecke.eigene(daten), ['m_daz_scham', 'andere'])
        self.assertEqual(Modellstuecke.eigene({'figur': {'herkunft': 'text'}}), [])
        self.assertEqual(Modellstuecke.eigene({}), [])
        eintraege = {'m_daz_scham': {'id': 'm_daz_scham', 'eigen': True}, 'daz_anatomie_frau': {'id': 'daz_anatomie_frau', 'eigen': False}}
        with mock.patch('core.dienste.blendimportloeschen.Blendimportloeschen.modelle_lesen', return_value=[{'name': 'n', 'import': '', 'kleidung': {'andere'}}]), \
                mock.patch('Genesis9.garderobe.G9garderobe.eintrag', side_effect=eintraege.get), \
                mock.patch('Genesis9.garderobepflege.G9garderobepflege.loeschen') as loeschen:
            weg = Modellstuecke.entfernen(['m_daz_scham', 'andere', 'daz_anatomie_frau', 'gibt_es_nicht'])
        self.assertEqual(weg, ['m_daz_scham'], '„andere" trägt ein Modell, das Daz-Stück ist nicht eigen, das letzte gibt es nicht')
        loeschen.assert_called_once_with(eintraege['m_daz_scham'])

    def test_6b_die_ablage_ruft_es_nach_dem_loeschen_der_datei(self):
        with Pruefablage.ordner('modellstuecke_') as ordner, override_settings(HUMANBODY_MODELS_DIR=Path(ordner)):
            pfad = Path(ordner) / 'm.json'
            pfad.write_text(json.dumps({'name': 'm', 'figur': {'herkunft': {'daz_stuecke': ['m_daz_scham']}}}), encoding='utf-8')
            with mock.patch('core.dienste.modellstuecke.Modellstuecke.entfernen') as entfernen, mock.patch('GarmentCode.szenenstuecke.Szenenstuecke.entfernen'):
                entfernen.side_effect = lambda kennungen: self.assertFalse(pfad.exists(), 'die Datei ist schon weg, wenn die Stücke gehen')
                self.assertTrue(Modellablage.loeschen('m'))
            entfernen.assert_called_once_with(['m_daz_scham'])
            self.assertFalse(pfad.exists())

    def test_6c_scheitert_das_entfernen_gilt_das_modell_trotzdem_als_geloescht(self):
        with Pruefablage.ordner('modellstuecke_') as ordner, override_settings(HUMANBODY_MODELS_DIR=Path(ordner)):
            pfad = Path(ordner) / 'm.json'
            pfad.write_text(json.dumps({'name': 'm', 'figur': {'herkunft': {'daz_stuecke': ['m_daz_scham']}}}), encoding='utf-8')
            with mock.patch('core.dienste.modellstuecke.Modellstuecke.entfernen', side_effect=RuntimeError('gesperrt')), \
                    mock.patch('GarmentCode.szenenstuecke.Szenenstuecke.entfernen'), self.assertLogs('core.dienste.modellablage', level='ERROR'):
                self.assertTrue(Modellablage.loeschen('m'))
            self.assertFalse(pfad.exists())

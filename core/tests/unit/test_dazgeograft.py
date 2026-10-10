# -*- coding: utf-8 -*-
"""Das Daz-Geograft „Anatomical Elements" als Stück (`Dazgeograft*`, `G9stueckgerade`, `G9penisgerade`, `G9kleidmorphebrief`) — an Kunstformen, ohne Daz-Bibliothek.

Edgar, 10.10.2026: „baue die Morphs in das UI ein". Gemessen am Produkt (`dazgeograftquelle.py`): der Penis ist auf einer Knochenkette modelliert; ohne Pose
steht er waagerecht, Dazs Default Pose hängt ihn. Die Regler rechnen deshalb auf der GERADEN Form und drehen ihre Deltas in die Pose.

Kunstwelt: Walze (Radius 15 mm, 9 cm lang) entlang +z ab (0, 0.8, 0.08) = gerade Form; die „Pose" dreht sie um 60° um x nach unten (`J` = Drehmatrix je Punkt).

1. `_im_viereck`: ein Punkt in einem UV-Viereck liegt darin, einer daneben nicht — für beide Umlaufrichtungen.
2. `G9kleidmorphebrief.regler`: ohne Steckbrief die Vorgabe („Eigen: …", −2 … 2); mit dem Feld `regler` überschreibt er Name, Grenzen und Gruppe; Unsinn (Text als Grenze) bleibt bei der Vorgabe.
3. `G9stueckgerade`: Schreiben und Lesen geben gerade Form, Drehmatrizen und Marken zurück; fehlt eine Marke, kommt ein `ValueError`; ohne Datei gibt `lesen` None.
4. `G9penisgerade.deltas` für einen Formregler (Länge): gleich `J · Delta(gerade)` — die Verlängerung geht längs der GEDREHTEN Achse, nicht längs der geraden.
5. `G9penisgerade.deltas` für die Erektion: das Ziel liegt auf der geraden Form, unabhängig von der Haltung — zwei verschiedene Ausgangslagen enden in der Wurzelmitte an derselben Stelle.

Sabotage-Gegenprobe (nicht gelaufen): in `G9penisgerade.deltas` die Zeile `einsum` durch `return d` ersetzen macht Fall 4 rot; `d + w * (pg - p)` durch `d` ersetzen macht Fall 5 rot.
Gelaufen 10.10.2026 auf Ansage: Fall 5 war zuerst rot (Prüfpunkte auf der Walzenhaut mit Gewicht 0,91, Abweichung 2,6 mm) — der Test prüft jetzt die Kernlinie.
"""
import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase
from Genesis9.kleidmorphebrief import G9kleidmorphebrief
from Genesis9.penisgerade import G9penisgerade
from Genesis9.penismorphe import G9penismorphe
from Genesis9.penismorphekatalog import G9penismorphekatalog as K
from Genesis9.stueckgerade import G9stueckgerade

from core.dienste.dazgeografthaut import Dazgeografthaut

WURZEL = np.array([0.0, 0.8, 0.08])
LAENGE = 0.09
DREHUNG = np.radians(60.0)
R = np.array([[1, 0, 0], [0, np.cos(DREHUNG), -np.sin(DREHUNG)], [0, np.sin(DREHUNG), np.cos(DREHUNG)]])


def gerade_form():
    """Walze entlang +z (15 mm Radius) mit Kernlinie auf der Achse und ein Hodensack (Kugel hinter und unter der Wurzel); `hoehe` 30 mm überall (voll Anbau).
    Auf der Haut (r = Radius) ist das Walzengewicht nur 0,91, auf der Kernlinie 1 — das Ziel der Erektion lässt sich nur dort ohne Rest prüfen."""
    walze = [WURZEL + np.array([np.cos(w) * 0.015, np.sin(w) * 0.015, t])
             for t in np.linspace(0.0, LAENGE, 20) for w in np.linspace(0, 2 * np.pi, 8, endpoint=False)]
    walze += [WURZEL + np.array([0.0, 0.0, t]) for t in np.linspace(0.0, LAENGE, 20)]
    kugel = [WURZEL + np.array([0.0, -0.04, -0.01]) + 0.025 * np.array([np.sin(th) * np.cos(w), np.sin(th) * np.sin(w), np.cos(th)])
             for th in np.linspace(0, np.pi, 8) for w in np.linspace(0, 2 * np.pi, 8, endpoint=False)]
    return np.array(walze + kugel)


def marken():
    return {'wurzel': WURZEL, 'spitze': WURZEL + np.array([0.0, 0.0, LAENGE]), 'achse': np.array([0.0, 0.0, 1.0]), 'laenge': LAENGE, 'radius': 0.015,
            'hoden': WURZEL + np.array([0.0, -0.04, -0.01]), 'hoden_radius': 0.025}


class DazgeograftTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        super().setUp()
        ordner = Path(settings.BASE_DIR) / '_wegwerf'
        ordner.mkdir(exist_ok=True)
        self.ordner = Path(tempfile.mkdtemp(dir=ordner))          # nie System-Temp (`systemtemp.md`)
        self.addCleanup(shutil.rmtree, self.ordner, True)

    def _gerade(self):
        pg = gerade_form()
        pose = (pg - WURZEL) @ R.T + WURZEL                        # um die Wurzel nach unten gedreht
        return pg, pose, {'p': pg, 'J': np.tile(R, (len(pg), 1, 1)), 'marken': marken()}

    def test_1_ein_punkt_im_uv_viereck_liegt_darin_und_einer_daneben_nicht(self):
        viereck = np.array([[0.0, 0.0], [0.2, 0.0], [0.2, 0.1], [0.0, 0.1]])
        punkte = np.array([[0.1, 0.05], [0.3, 0.05], [0.1, 0.2]])
        for ecken in (viereck, viereck[::-1]):
            self.assertEqual(Dazgeografthaut._im_viereck(punkte, ecken).tolist(), [True, False, False])

    def test_2_der_steckbrief_gibt_name_grenzen_und_gruppe(self):
        pfad = self.ordner / 'brief.json'
        vorgabe = G9kleidmorphebrief.regler(pfad, 'daz_vorhaut', 'Eigene Morphe')
        self.assertEqual((vorgabe['anzeige'], vorgabe['min'], vorgabe['max'], vorgabe['gruppe']), ('Eigen: daz_vorhaut', -2.0, 2.0, 'Eigene Morphe'))
        pfad.write_text(json.dumps({'regler': {'anzeige': 'Vorhaut', 'min': 0, 'max': 1, 'gruppe': 'Penis · Daz'}}), encoding='utf-8')
        r = G9kleidmorphebrief.regler(pfad, 'daz_vorhaut', 'Eigene Morphe')
        self.assertEqual((r['anzeige'], r['min'], r['max'], r['gruppe']), ('Vorhaut', 0.0, 1.0, 'Penis · Daz'))
        pfad.write_text(json.dumps({'regler': {'min': 'viel', 'max': True, 'anzeige': 7}}), encoding='utf-8')
        r = G9kleidmorphebrief.regler(pfad, 'daz_vorhaut', 'Eigene Morphe')
        self.assertEqual((r['anzeige'], r['min'], r['max']), ('Eigen: daz_vorhaut', -2.0, 2.0), 'Unsinn bleibt bei der Vorgabe')

    def test_3_die_gerade_form_geht_hin_und_zurueck(self):
        duf = self.ordner / 'Stueck.duf'
        pg, _pose, gerade = self._gerade()
        self.assertIsNone(G9stueckgerade.lesen(duf))
        G9stueckgerade.schreiben(duf, pg, gerade['J'], marken())
        aus = G9stueckgerade.lesen(duf)
        self.assertEqual(aus['p'].shape, pg.shape)
        self.assertAlmostEqual(float(np.abs(aus['p'] - pg).max()), 0.0, places=5)
        self.assertAlmostEqual(float(np.abs(aus['J'] - gerade['J']).max()), 0.0, places=5)
        self.assertAlmostEqual(aus['marken']['laenge'], LAENGE, places=9)
        self.assertEqual(aus['marken']['achse'].shape, (3,))
        kaputt = marken()
        del kaputt['radius']
        with self.assertRaises(ValueError):
            G9stueckgerade.schreiben(duf, pg, gerade['J'], kaputt)

    def test_4_ein_formregler_rechnet_auf_der_geraden_form_und_dreht_ins_haengende(self):
        pg, pose, gerade = self._gerade()
        eintrag = K.eintrag('pen_laenge')
        d = G9penisgerade.deltas(pose, [], eintrag, None, [30.0] * len(pg), gerade)
        gerade_d = G9penismorphe.deltas(pg, [], eintrag, None, [30.0] * len(pg), marken())
        self.assertAlmostEqual(float(np.abs(d - gerade_d @ R.T).max()), 0.0, places=9)
        spitze = np.argmax(np.linalg.norm(gerade_d, axis=1))
        achse_gedreht = R @ np.array([0.0, 0.0, 1.0])
        richtung = d[spitze] / np.linalg.norm(d[spitze])
        self.assertGreater(float(richtung @ achse_gedreht), 0.99, 'die Verlängerung geht längs der gedrehten Achse')

    def test_5_die_erektion_zielt_auf_die_gerade_form_gleich_aus_welcher_haltung(self):
        pg, pose, gerade = self._gerade()
        eintrag = K.eintrag('pen_erektion')
        hoehe = [30.0] * len(pg)
        andere = pose + np.array([0.0, -0.03, 0.01])               # eine andere Ausgangslage
        d1 = G9penisgerade.deltas(pose, [], eintrag, None, hoehe, gerade)
        d2 = G9penisgerade.deltas(andere, [], eintrag, None, hoehe, gerade)
        quer = np.hypot(pg[:, 0] - WURZEL[0], pg[:, 1] - WURZEL[1])
        mitte = np.flatnonzero((pg[:, 2] - WURZEL[2] > 0.04) & (pg[:, 2] - WURZEL[2] < 0.06) & (quer < 1e-9))     # Kernlinie des Schafts
        self.assertGreater(len(mitte), 0)
        ende1, ende2 = (pose + d1)[mitte], (andere + d2)[mitte]
        self.assertLess(float(np.abs(ende1 - ende2).max()), 1e-6, 'das Ziel hängt nicht von der Ausgangslage ab')
        self.assertGreater(float(np.linalg.norm(d1[mitte], axis=1).min()), 0.005, 'der Schaft bewegt sich')

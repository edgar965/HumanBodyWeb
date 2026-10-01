# -*- coding: utf-8 -*-
u"""2D3D Kleider, 01.10.2026 nachmittags („Fixe alles"): Haltung der Fotos, Ablagen je Auftrag, neue Automatik-Regeln,
Runden-GLB mit Rig — alles auf Kunstdaten, ohne Daz-Bibliothek, ohne Lauf, ohne Datenbank.

1. `G9haltungshaut`: ein Punkt am gedrehten Knochen dreht mit, ein halb gebundener halb, ohne Haut bleibt er; Normalen
   drehen und bleiben Länge 1; `posieren` gibt Kopien mit `ruhe` und häutet die Kurven mit.
2. `Haltungsschaetzung`: Oberarm 20° quer, gestreckt → 20° / 0°; dieselbe Figur von der Seite (Hüftlinie entlang z)
   → dasselbe Maß; unsichtbarer Ellbogen → None.
3. `IterationModell.haltung`: aus `haltung_foto` → Arme und Ellbogen; danach nichts mehr; ohne Fotos zurück zur A-Pose.
4. Auftragsnamen: `Rezeptumgebung.kuerzel`, `fotoschicht`, `auftragsname` (einmal, nicht doppelt), `vorhanden`,
   Schichtname gültig, keine dieser Hilfen steht in `hilfe()` (sonst wären sie Rezeptaufrufe).
5. `IterationKleidring`: Band daneben UND die Hälfte seiner Zellen am Deckel → `kleid_ring`; danach Schritte bis 1;
   Zellen nicht am Deckel → nichts.
6. `IterationHaare.trim`/`fototextur`: Trim nur im Sektor, der unten über das Netz ragt, und nur bei Achse 0;
   Fototextur nach drei stillen Runden, einmal.
7. `Rundenglb._zugriff`: Gewichte als normierte Bytes mit Summe 255, Knochennummern als Bytes.
8. `Begutachtungsstand.befund_fuer_regeln`: ein Befund eines anderen Renderers verliert für die Regeln die
   Renderfarben — `IterationHaare.farbe` macht dann keinen Schritt (vorher [0, 0, 0] → Tönung an den Anschlag).
(Die Gesichtsmaße je Kopfstand: `test_gesichtsvorrat.py`.)

Sabotage-Gegenproben: in `G9haltungshaut._mischen` `w4` für Normalen auf 1 → Fall 1 rot; in `Haltungsschaetzung.arm`
den Körperrahmen weglassen (Bild-x statt Hüftlinie) → Fall 2 (Seite) rot; in `IterationKleidring` die Deckelprüfung
entfernen → Fall 5 (nicht am Deckel) rot; `auftragsname` ohne `endswith`-Wächter → Fall 4 (doppelt) rot.
"""
import math

import numpy as np
from django.test import SimpleTestCase
from Genesis9.haltungshaut import G9haltungshaut
from Genesis9.kleidtexturen import G9kleidtexturen
from Genesis9.modellmitkleidern import ModellMitKleidern
from Genesis9.modellrezept import G9rezept
from Genesis9.rezeptumgebung import Rezeptumgebung
from iterationen2d3d.haltungsschaetzung import Haltungsschaetzung
from iterationen2d3d.iterationhaare import IterationHaare
from iterationen2d3d.iterationkleidring import IterationKleidring
from iterationen2d3d.iterationmodell import IterationModell


def _haltungshaut(drehung_grad=90.0):
    """Ohne Bibliothek: Knochen 'a' dreht um z durch den Ursprung, 'b' bleibt."""
    h = object.__new__(G9haltungshaut)
    h.drehung, h.boden = {'a': {}}, 0.0
    w = math.radians(drehung_grad)
    d = np.eye(4)
    d[:2, :2] = [[math.cos(w), -math.sin(w)], [math.sin(w), math.cos(w)]]
    h._verformung = {'a': d}
    return h


class HaltungshautTest(SimpleTestCase):

    databases = set()

    def test_1_punkte_normalen_kopien(self):
        h = _haltungshaut()
        haut = {'knochen': ['a', 'b'], 'index': np.array([[0, 1], [0, 1], [1, 0]]),
                'gewicht': np.array([[1.0, 0.0], [0.5, 0.5], [1.0, 0.0]])}
        p = np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
        aus = h.punkte(p, haut)
        np.testing.assert_allclose(aus[0], [0.0, 1.0, 0.0], atol=1e-12)        # ganz an 'a': 90° gedreht
        np.testing.assert_allclose(aus[1], [0.5, 0.5, 0.0], atol=1e-12)        # halb
        np.testing.assert_allclose(aus[2], [1.0, 0.0, 0.0], atol=1e-12)        # an 'b'
        np.testing.assert_allclose(h.punkte(p, None), p)
        n = h.normalen(np.array([[1.0, 0.0, 0.0]] * 3), haut)
        np.testing.assert_allclose(np.linalg.norm(n, axis=1), 1.0, atol=1e-12)
        np.testing.assert_allclose(n[0], [0.0, 1.0, 0.0], atol=1e-12)
        teil = {'punkte': p, 'haut': haut, 'normalen': None,
                'kurven': {'punkte': p.astype(np.float32), 'haut': haut}}
        neu = h.posieren([teil])[0]
        self.assertIs(neu['ruhe'], teil)
        np.testing.assert_allclose(neu['kurven']['punkte'][0], [0.0, 1.0, 0.0], atol=1e-6)
        np.testing.assert_allclose(teil['punkte'][0], [1.0, 0.0, 0.0])          # die Ruhelage bleibt
        h._verformung = {}
        self.assertEqual(h.posieren([teil]), [teil])


def _figur(seitlich, gebeugt=0.0, quer=(1.0, 0.0, 0.0), sichtbar=1.0):
    """33 Weltpunkte (y nach unten): Hüften auf der Linie `quer`, linker Arm `seitlich` Grad aus der Senkrechten."""
    q = np.asarray(quer, dtype=float)
    p = [[0.0, 0.0, 0.0, 1.0] for _ in range(33)]
    p[23], p[24] = list(0.1 * q) + [1.0], list(-0.1 * q) + [1.0]
    for seite, vz in ((0, 1.0), (1, -1.0)):
        s = np.array([0.0, -0.45, 0.0]) + vz * 0.15 * q
        a = math.radians(seitlich)
        e = s + 0.25 * (vz * math.sin(a) * q + np.array([0.0, math.cos(a), 0.0]))
        b = math.radians(seitlich + gebeugt)
        h = e + 0.25 * (vz * math.sin(b) * q + np.array([0.0, math.cos(b), 0.0]))
        for i, v in zip(Haltungsschaetzung.SEITEN[seite], (s, e, h), strict=True):
            p[i] = list(v) + [1.0]
    p[13][3] = sichtbar
    p[14][3] = sichtbar
    return p


class HaltungsschaetzungTest(SimpleTestCase):

    databases = set()

    def test_2_arm_im_koerperrahmen(self):
        s, b, _g = Haltungsschaetzung.arm(_figur(20.0), 0)
        self.assertAlmostEqual(s, 20.0, places=6)
        self.assertAlmostEqual(b, 0.0, places=4)
        seite = Haltungsschaetzung.arm(_figur(20.0, quer=(0.0, 0.0, 1.0)), 0)
        self.assertAlmostEqual(seite[0], 20.0, places=6)                          # von der Seite dasselbe Maß
        _s, b, _g = Haltungsschaetzung.arm(_figur(10.0, gebeugt=15.0), 1)
        self.assertAlmostEqual(b, 15.0, places=4)
        self.assertIsNone(Haltungsschaetzung.arm(_figur(20.0, sichtbar=0.1), 0))
        self.assertIsNone(Haltungsschaetzung.schaetzen([_figur(20.0, sichtbar=0.1)]))
        self.assertEqual(Haltungsschaetzung.schaetzen([_figur(20.0)])['arme'], 2)


class HaltungAutomatikTest(SimpleTestCase):

    databases = set()

    def test_3_haltung_aus_den_fotos(self):
        m = ModellMitKleidern()
        befund = {'haltung_foto': {'seitlich': 14.5, 'beuge': 19.6, 'arme': 5}}
        zeilen = IterationModell(m, befund).haltung()
        self.assertEqual(zeilen, ['m.haltung(28.3)', "m.haltung_gelenk('l_forearm', 'y', -6.0)",
                                  "m.haltung_gelenk('r_forearm', 'y', 6.0)"])
        G9rezept.anwenden(m, '\n'.join(zeilen))
        self.assertEqual(IterationModell(m, befund).haltung(), [])
        self.assertEqual(m.drehung()['r_forearm'], {'rotation/y': 6.0})
        self.assertEqual(IterationModell(m, {}).haltung(), ['m.haltung(0.0)'])     # ohne Fotos: A-Pose


class AuftragsnamenTest(SimpleTestCase):

    databases = set()

    def test_4_namen_je_auftrag(self):
        k = Rezeptumgebung.kuerzel('2026.09.30.23.16.51')
        self.assertEqual(k, 'j20260930231651')
        self.assertIsNone(Rezeptumgebung.kuerzel(''))
        m = ModellMitKleidern()
        self.assertEqual(m.fotoschicht(), 'foto')
        self.assertEqual(m.auftragsname('huelle'), 'huelle')
        m.umgebung = Rezeptumgebung(auftrag=k)
        self.assertEqual(m.fotoschicht(), 'foto_' + k)
        self.assertTrue(G9kleidtexturen.NAME.match(m.fotoschicht()))
        self.assertEqual(m.auftragsname('huelle'), 'huelle_' + k)
        self.assertEqual(m.auftragsname('huelle_' + k), 'huelle_' + k)               # nicht doppelt
        werte = {'s.eigen.huelle_' + k: 0.5}
        self.assertEqual(m.vorhanden(werte, 's.eigen.huelle'), 's.eigen.huelle_' + k)
        self.assertEqual(m.vorhanden({'s.eigen.huelle': 1}, 's.eigen.huelle'), 's.eigen.huelle')
        self.assertIsNone(m.vorhanden({'s.eigen.huelle_x': 1}, 's.eigen.huelle'))
        namen = {n for n, _s, _t in ModellMitKleidern.hilfe()}
        self.assertFalse(namen & {'fotoschicht', 'auftragsname', 'vorhanden'})


class KleidringTest(SimpleTestCase):

    databases = set()

    def _stuecke(self):
        return {'shirt': {'art': 'kleidung', 'baender': [0.0, 0.0, 0.0, 30.0, 0.0], 'grund_mm': 5.0,
                          'zellen': [[0.0] * 8, [0.0] * 8, [0.0] * 8, [30.0] * 8, [0.0] * 8]}}

    def test_5_ring_erst_am_deckel(self):
        m = ModellMitKleidern()
        stuecke = self._stuecke()
        grund = lambda e: float(e.get('grund_mm') or 0.0)          # noqa: E731
        self.assertEqual(IterationKleidring(m, stuecke, grund).aufrufe(), [])     # Zellen nicht am Deckel
        for j in range(4):
            m.kleidung['shirt.eigen.netz_b3s%d' % j] = -2.0
        zeilen = IterationKleidring(m, stuecke, grund).aufrufe()
        self.assertEqual(zeilen, ["m.kleid_ring('shirt', 'netz_ring_b3_eng', 0.7, weite=1.0, band=0.1, wert=0.5)"])
        m.kleidung['shirt.eigen.netz_ring_b3_eng'] = 0.5
        self.assertEqual(IterationKleidring(m, stuecke, grund).aufrufe(),
                         ["m.morph_wert('kleidung', 'shirt', 'netz_ring_b3_eng', 0.75)"])
        m.kleidung['shirt.eigen.netz_ring_b3_eng'] = 1.0
        self.assertEqual(IterationKleidring(m, stuecke, grund).aufrufe(), [])


class HaarRegelnTest(SimpleTestCase):

    databases = set()

    def test_6_trim_und_fototextur(self):
        m = ModellMitKleidern()
        m.haar_nur('kurz')
        zellen = [[0.0] * 8, [0.0] * 8, [0.0] * 8, [0.0] * 8, [0.0] * 8]
        zellen[0][2] = zellen[1][2] = 30.0
        befund = {'teile': {'kurz': {'art': 'haar', 'zellen': zellen, 'netz_abs_mm': 3.0, 'pixel': 0}}}
        zeilen = IterationHaare(m, befund).trim()
        self.assertEqual(len(zeilen), 1)
        self.assertIn("'netz_trim_s2'", zeilen[0])
        m.haar['kurz.achse.laenge'] = 0.4
        self.assertEqual(IterationHaare(m, befund).trim(), [])                    # erst die Achse
        verlauf = [{'frisur': 'kurz', 'haar_mm': 30.0 + 0.1 * i} for i in range(4)]
        self.assertEqual(IterationHaare(m, befund, verlauf).fototextur(), ["m.haar_fototextur('kurz')"])
        m.haar['kurz.bild.foto_j1'] = 1.0
        self.assertEqual(IterationHaare(m, befund, verlauf).fototextur(), [])

    def test_8_farbschritt_nur_mit_befund_desselben_renderers(self):
        from unittest import mock

        from core.dienste.begutachtungsstand import Begutachtungsstand
        from core.dienste.mitsubaszene import Mitsubaszene
        from core.dienste.renderwahl import Renderwahl
        m = ModellMitKleidern()
        m.haar_nur('kurz')
        teil = {'art': 'haar', 'pixel': 500, 'foto_farbe': [0.44, 0.37, 0.35], 'render_farbe': [0.64, 0.59, 0.52]}
        z = {'befund': {'motor': 'pyrender', 'teile': {'kurz': teil}}}
        with mock.patch.object(Renderwahl, 'gewaehlt', return_value='mitsuba'), \
                mock.patch.object(Mitsubaszene, 'mitsuba', return_value=object()):
            fremd = Begutachtungsstand.befund_fuer_regeln(z)
        with mock.patch.object(Renderwahl, 'gewaehlt', return_value='pyrender'):
            gleich = Begutachtungsstand.befund_fuer_regeln(z)
        self.assertIsNone(fremd['teile']['kurz']['render_farbe'])
        self.assertEqual(teil['render_farbe'], [0.64, 0.59, 0.52])               # der abgelegte Befund bleibt
        self.assertIs(gleich, z['befund'])
        self.assertEqual(IterationHaare(m, fremd).farbe(), [])                    # kein Schritt, nicht an den Anschlag
        self.assertEqual(len(IterationHaare(m, gleich).farbe()), 1)


class RundenglbTest(SimpleTestCase):

    databases = set()

    def test_7_hautgewichte_als_bytes(self):
        from core.dienste.rundenglb import Rundenglb
        glb = Rundenglb([{'name': 'hip', 'eltern': None, 'kopf': [0.0, 0.0, 0.0], 'pos': [0.0, 0.0, 0.0],
                          'quat': [0.0, 0.0, 0.0, 1.0]}])
        gewicht = np.array([[0.5, 0.3, 0.2, 0.0], [1.0, 0.0, 0.0, 0.0], [0.333, 0.333, 0.334, 0.0]])
        nr = glb._zugriff(gewicht, glb.FLOAT, 'VEC4', glb.ARRAY)
        zugriff = glb.gltf['accessors'][nr]
        self.assertEqual((zugriff['componentType'], zugriff.get('normalized')), (5121, True))
        ansicht = glb.gltf['bufferViews'][zugriff['bufferView']]
        roh = np.frombuffer(bytes(glb.puffer[ansicht['byteOffset']:ansicht['byteOffset'] + ansicht['byteLength']]),
                            dtype=np.uint8).reshape(-1, 4)
        np.testing.assert_array_equal(roh.sum(axis=1), 255)
        nr = glb._zugriff(np.array([[0, 1, 2, 3]]), glb.USHORT, 'VEC4', glb.ARRAY)
        self.assertEqual(glb.gltf['accessors'][nr]['componentType'], 5121)
        nr = glb._zugriff(np.array([[0, 1, 2, 300]]), glb.USHORT, 'VEC4', glb.ARRAY)
        self.assertEqual(glb.gltf['accessors'][nr]['componentType'], glb.USHORT)


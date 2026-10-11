# -*- coding: utf-8 -*-
"""`Hautbackenblendernormalen`: die Normalen eines Netzes wie Blender 5.2.2 sie aus denselben Rohdaten und denselben Punkten rechnet (10.10.2026).

Edgar: „übernimm den ganzen Code, keine Fehler! Erfinde nichts!!" — der Code ist Zeile für Zeile aus `mesh_normals.cc` (Blender v5.2.2) übernommen; dieser Test hält ihn an Blenders
EIGENER Ausgabe fest. Golden-Daten: `hautbacken_daten/blendernormalen_golden.npz` (80 Fälle, 1,3 MB; Erzeugung in `hautbacken_normalen_golden.py`): künstliche Netze (Würfel, Kugel,
Gitter, n-Eck-Prisma, nicht-mannigfaltig, Spitze), 48 Zufallsnetze, und Ausschnitte (2000 Polygone) von Rosemarys `body` (Vierecke, nur Punktnormalen), `jean` (scharfe Kanten), `hat`
und Asian_Girls `CC_Base_Body` (eigene Normalen). Je Fall die Normalen am Original UND an verformten Punkten (Biegung + Verschiebung) — das Entscheidende: mit neuen Punkten rechnet Blender
Normalen und eigene Normalen neu aus denselben Rohdaten.

1. Alle Fälle: Domain wie Blender; `punkte`/`flaechen`/`ecken` weichen höchstens `TOLERANZ` (1e-6; gemessen ≤ 1,2e-7, Ziel war 1e-5) von `vertex_normals`/`polygon_normals`/`corner_normals` ab.
2. Ohne eigene Normalen sogar bitgleich (reine float32-Rechnung in Blenders Reihenfolge); mit eigenen Normalen bleibt Sinus/Kosinus ein ulp.
3. Das Golden deckt die Zweige ab (alle drei Domains, scharfe Kanten/Polygone, eigene Normalen, n-Ecken, lose Punkte, Kanten mit drei Polygonen, echte Figuren) und ist wirklich verformt.
4. `domain` folgt `Mesh::normals_domain`.
5. Eigene Normalen folgen den Punkten; Nulldaten ergeben die automatische Normale.
6. Formen, Fehler, leeres Netz. 7. Bausteine (`safe_acos_approx`, Normalisieren).

Sabotage-Gegenprobe (am 10.10.2026 ausgeführt: jeweils rot, danach zurückgenommen):
  * in `Hautbackenblenderflaechen.punktnormalen` den Winkelfaktor durch 1 ersetzen (`faktor = np.ones_like(faktor)`) → Fall 1 und 2 rot (body, jean, Zufallsnetze);
  * in `Hautbackenblenderfaecher._verbindungen` die scharfen Polygone ignorieren (`scharf_flaeche = None`) → Fall 1 und 2 rot (fuzz_001, …);
  * in `Hautbackenblenderraeume.dekodieren` `M.PI2 - raum['beta']` durch `raum['beta']` ersetzen → Fall 1 rot (eigene Normalen, fuzz_002, …), Fall 2 bleibt grün (er prüft nur Netze ohne eigene).

Nicht gelaufen im Sinne „ganze Suite": nur dieses Modul (Edgar: „mache tests" für die neuen kleinen Tests).
"""

import os

import numpy as np
from django.test import SimpleTestCase

from core.dienste.hautbacken.hautbackenblendermathe import Hautbackenblendermathe
from core.dienste.hautbacken.hautbackenblendernormalen import Hautbackenblendernormalen

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hautbacken_daten', 'blendernormalen_golden.npz')
TOLERANZ = 1e-6
ECHTE = ('body', 'jean', 'hat', 'CC_Base_Body')


class BlendernormalenTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with np.load(GOLDEN, allow_pickle=False) as d:
            cls.daten = {k: d[k] for k in d.files}
        cls.namen = sorted({k.split('__')[0] for k in cls.daten if '__' in k})

    # ------------------------------------------------------------------ Hilfen

    def _roh(self, name):
        g = lambda a: self.daten['%s__%s' % (name, a)]  # noqa: E731
        roh = {k: g(a) for k, a in (('kanten', 'kanten'), ('ecke_kante', 'ek'), ('scharf_kante', 'sk'), ('scharf_flaeche', 'sf'), ('eigene_normale', 'en')) if '%s__%s' % (name, a) in self.daten}
        return g, roh

    def _rechnen(self, name, nach=''):
        """`(Ergebnis, Referenz)` — `nach` '' (Original) oder '2' (verformte Punkte)."""
        g, roh = self._roh(name)
        r = Hautbackenblendernormalen.berechnen(g('p' + nach), g('ps'), g('pp'), ecken_immer=True, **roh)
        return r, {'punkte': g('vn' + nach), 'flaechen': g('fn' + nach), 'ecken': g('cn' + nach)}

    # ------------------------------------------------------------------ 1, 2

    def test_1_alle_faelle_wie_blender(self):
        fehler = []
        for name in self.namen:
            for nach in ('', '2'):
                r, ref = self._rechnen(name, nach)
                if nach == '' and r['domain'] != str(self.daten['%s__domain' % name]):
                    fehler.append('%s: Domain %s statt %s' % (name, r['domain'], self.daten['%s__domain' % name]))
                for schluessel, soll in ref.items():
                    abweichung = float(np.abs(r[schluessel].astype(np.float64) - soll.astype(np.float64)).max())
                    if not abweichung <= TOLERANZ:
                        fehler.append('%s%s %s: %.3g' % (name, ' (verformt)' if nach else '', schluessel, abweichung))
        self.assertEqual([], fehler)
        self.assertGreaterEqual(len(self.namen), 80)

    def test_2_ohne_eigene_normalen_bitgleich(self):
        fehler, gezaehlt = [], 0
        for name in self.namen:
            if '%s__en' % name in self.daten:
                continue
            gezaehlt += 1
            for nach in ('', '2'):
                r, ref = self._rechnen(name, nach)
                for schluessel, soll in ref.items():
                    if not np.array_equal(r[schluessel], soll):
                        fehler.append('%s%s %s' % (name, ' (verformt)' if nach else '', schluessel))
        self.assertEqual([], fehler)
        self.assertGreaterEqual(gezaehlt, 40)

    # ------------------------------------------------------------------ 3

    def test_3_golden_deckt_die_zweige_ab(self):
        d = self.daten
        self.assertEqual({'POINT', 'FACE', 'CORNER'}, {str(d['%s__domain' % n]) for n in self.namen})
        mit = lambda a: [n for n in self.namen if '%s__%s' % (n, a) in d]  # noqa: E731
        self.assertGreaterEqual(len(mit('en')), 20)
        self.assertGreaterEqual(len([n for n in mit('sk') if d['%s__sk' % n].any()]), 20)
        self.assertGreaterEqual(len([n for n in mit('sf') if d['%s__sf' % n].any()]), 5)
        groessen = set()
        lose = drei_an_kante = 0
        for n in self.namen:
            groessen |= set(np.diff(d['%s__ps' % n]).tolist())
            lose += int((np.bincount(d['%s__pp' % n], minlength=len(d['%s__p' % n])) == 0).any())
            drei_an_kante += int((np.bincount(d['%s__ek' % n]) >= 3).any())
        self.assertTrue({3, 4}.issubset(groessen) and max(groessen) >= 5, groessen)
        self.assertGreaterEqual(lose, 1)
        self.assertGreaterEqual(drei_an_kante, 1)
        for echt in ECHTE:
            self.assertIn(echt, self.namen)
        # wirklich verformt: Blenders Normalen und die Punkte haben sich bewegt
        for n in self.namen:
            self.assertGreater(float(d['%s__bewegt' % n]), 1e-3, n)
            self.assertGreater(float(np.abs(d['%s__p2' % n] - d['%s__p' % n]).max()), 1e-4, n)
        self.assertLess(os.path.getsize(GOLDEN), 5 * 1024 * 1024)

    # ------------------------------------------------------------------ 4

    def test_4_domain_folgt_blenders_regeln(self):
        D = Hautbackenblendernormalen.domain
        alle, keine = np.ones(5, dtype=bool), np.zeros(5, dtype=bool)
        gemischt = np.array([0, 1, 0, 0, 0], dtype=bool)
        self.assertEqual('POINT', D(0, alle, alle, np.zeros((0, 2))))          # ohne Polygone immer Punkt
        self.assertEqual('POINT', D(5))
        self.assertEqual('POINT', D(5, keine, keine))
        self.assertEqual('FACE', D(5, None, alle))
        self.assertEqual('FACE', D(5, alle, None))
        self.assertEqual('FACE', D(5, alle, keine))
        self.assertEqual('CORNER', D(5, gemischt, None))
        self.assertEqual('CORNER', D(5, None, gemischt))
        self.assertEqual('CORNER', D(5, keine, keine, np.zeros((3, 2))))        # eigene Normalen: immer Ecke
        self.assertEqual('CORNER', D(5, alle, alle, np.zeros((3, 2))))          # … auch wenn sonst alles scharf wäre

    # ------------------------------------------------------------------ 5

    def test_5_eigene_normalen_folgen_den_punkten_und_nulldaten_sind_automatisch(self):
        r1, _ = self._rechnen('CC_Base_Body', '')
        r2, _ = self._rechnen('CC_Base_Body', '2')
        self.assertGreater(float(np.abs(r1['ecken'] - r2['ecken']).max()), 1e-2)        # dieselben Rohdaten, andere Punkte → andere Normalen
        for name in ('jean', 'gitter_offen_scharf', 'kugel_scharf_flach'):
            g, roh = self._roh(name)
            ohne = Hautbackenblendernormalen.berechnen(g('p2'), g('ps'), g('pp'), **roh)
            roh['eigene_normale'] = np.zeros((len(g('pp')), 2), dtype=np.int16)
            mit = Hautbackenblendernormalen.berechnen(g('p2'), g('ps'), g('pp'), **roh)
            self.assertEqual('CORNER', ohne['domain'], name)
            self.assertTrue(np.array_equal(ohne['ecken'], mit['ecken']), name)

    # ------------------------------------------------------------------ 6

    def test_6_formen_fehler_und_leeres_netz(self):
        g, roh = self._roh('wuerfel_glatt')
        r = Hautbackenblendernormalen.berechnen(g('p'), g('ps'), g('pp'), **roh)
        self.assertEqual('POINT', r['domain'])
        self.assertIsNone(r['ecken'])                                                    # Punkt-Domain: Cycles liest die Punktnormalen
        self.assertEqual((8, 3), r['punkte'].shape)
        self.assertEqual((6, 3), r['flaechen'].shape)
        self.assertEqual(np.float32, r['punkte'].dtype)
        self.assertEqual((24, 3), Hautbackenblendernormalen.berechnen(g('p'), g('ps'), g('pp'), ecken_immer=True, **roh)['ecken'].shape)
        g, roh = self._roh('wuerfel_kanten')
        r = Hautbackenblendernormalen.berechnen(g('p'), g('ps'), g('pp'), **roh)
        self.assertEqual((24, 3), r['ecken'].shape)                                      # Domain Ecke: immer
        with self.assertRaises(ValueError):
            Hautbackenblendernormalen.berechnen(g('p'), g('ps'), g('pp')[:-1], **roh)
        with self.assertRaises(ValueError):
            roh2 = dict(roh, eigene_normale=np.zeros((5, 2), dtype=np.int16))
            Hautbackenblendernormalen.berechnen(g('p'), g('ps'), g('pp'), **roh2)
        with self.assertRaises(ValueError):
            Hautbackenblendernormalen.berechnen(g('p'), g('ps'), g('pp'), scharf_kante=roh['scharf_kante'])
        with self.assertRaises(ValueError):                                              # freie Float3-Normalen sind nicht gebaut
            Hautbackenblendernormalen.berechnen(g('p'), g('ps'), g('pp'), eigene_normale=np.zeros((24, 3), dtype=np.float32))
        # leeres Netz: kein Polygon → Punktnormale = normalize(Position)
        p = np.array([[3, 0, 0], [0, 0, 0], [0, 4, 0]], dtype=np.float32)
        leer = Hautbackenblendernormalen.berechnen(p, [0], [])
        self.assertEqual((0, 3), leer['flaechen'].shape)
        self.assertTrue(np.array_equal(leer['punkte'], np.array([[1, 0, 0], [0, 0, 0], [0, 1, 0]], dtype=np.float32)))
        self.assertIsNone(leer['ecken'])

    # ------------------------------------------------------------------ 7

    def test_7_bausteine(self):
        M = Hautbackenblendermathe
        x = np.linspace(-1.0, 1.0, 20001, dtype=np.float32)
        fehler = np.abs(M.acos_naeherung(x).astype(np.float64) - np.arccos(x.astype(np.float64)))
        self.assertLess(float(fehler.max()), 4.6e-5)                                      # Blenders Angabe: bis 4,51803e-5
        self.assertEqual(0.0, float(M.acos_naeherung(np.array([1.0], dtype=np.float32))[0]))
        self.assertAlmostEqual(np.pi, float(M.acos_naeherung(np.array([-1.0], dtype=np.float32))[0]), places=6)
        v = np.array([[0, 0, 0], [1e-20, 0, 0], [3, 0, 4]], dtype=np.float32)
        n = M.normalisieren(v)
        self.assertTrue(np.array_equal(n[:2], np.zeros((2, 3), dtype=np.float32)))        # zu klein (Länge² ≤ 1e-35) → Nullvektor
        self.assertAlmostEqual(0.6, float(n[2, 0]), places=6)
        nc, laenge = M.normalisieren_c(v)
        self.assertEqual([0.0, 0.0, 5.0], laenge.tolist())
        self.assertTrue(np.array_equal(nc[:2], np.zeros((2, 3), dtype=np.float32)))

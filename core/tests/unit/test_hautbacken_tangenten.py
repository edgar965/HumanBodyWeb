# -*- coding: utf-8 -*-
"""Hautbackentangenten gegen Blender 5.2.2 und gegen CYCLES selbst (Edgar, 10.10.2026: „übernimm den
ganzen Code, keine Fehler! Erfinde nichts!!").

Die Rechnung ist MikkTSpace aus Blenders Quelltext (v5.2.2, unverändert), in eine DLL übersetzt
(`Hautbackenmikkbau`) und mit Cycles' `MikkMeshWrapper` umhüllt. Die Golden-Daten
(`hautbacken_daten/tangenten_golden.npz`, 0,7 MB) liegen ohne Blender vor:

* `tangenten`/`vorzeichen`: Blenders `mesh.calc_tangents()` (Blender mit `-t 1`, also der serielle
  MikkTSpace-Pfad — ab 10.000 Dreiecken rechnet Blender sonst parallel, und die atomaren Float-Summen
  schwanken von Lauf zu Lauf um bis zu 3,5e-6, gemessen am Körper von Rosemary Winters).
* `cyc_*`: Stichproben aus CYCLES' eigenen Tangenten — gebackenes Attribut `UV.tangent`
  (Attribute-Knoten, Emission, Float32, CPU): je Texel Dreieck, Texel und gemessener Vektor. Die
  Abtastposition der Bake-Pipeline sitzt um ~0,001–0,002 Texel neben der Texelmitte; deshalb wird je
  Dreieck ein Versatz (dx, dy) mit angepasst (wie bei `ProjektTemp/_wegwerf/hautbacken_tangenten/
  cycles_pruefung.py`). Der Rest danach ist bei Cycles' Modus 1e-7 (gemessen: höchstens 2,4e-7), bei den
  float-Normalen von `calc_tangents` 1e-5.

Netze: `kappe` (Kugelkappe mit UV-Naht, Pol und Loch), `gespiegelt` (gespiegelte UV, 240 Ecken mit
Vorzeichen -1), `wuerfel_hart` (flach), `wuerfel_glatt`, `verzerrt_glatt/flach` (Splitter, entartete
und UV-flächenlose Dreiecke), `rosemary_ausschnitt` (3.000 Dreiecke vom Körper), `jean_ausschnitt`
(scharfe Kanten, Bereich CORNER, Eckennormalen); `kappe_misch` (gemischt glatt/flach, CORNER) und
`kappe_flach` nur mit Cycles-Stichproben.

1. Punktnormalen: `punktnormalen` ist bitgleich Blenders `mesh.vertex_normals`.
2. `modus='blender'`: Tangente und Vorzeichen bitgleich Blenders `calc_tangents` — mit Blenders
   Normalen, ohne Normalen (eigene), bei `jean` mit `corner_normals`.
3. `modus='cycles'`: gegen Cycles' Bild Rest <= 1e-6 je Dreieck; die float-Normalen (`'blender'`)
   liegen bei glatten Netzen deutlich darüber (der Test kann also rot werden).
4. Das Glatt-Flag zählt: bei `kappe_misch` (Eckennormalen, 1/3 flach) stimmt Cycles nur, wenn flache
   Dreiecke `compute_normal` nehmen — „alle glatt" (die Lesart von `pack_shaders`) liegt darüber.
5. Die Golden-Daten sind nicht leer: Vorzeichen -1 und +1 kommen vor, alle Netze sind da.
6. Eingaben: falsche Formen, unbekannter Modus, Punktindex außerhalb, leeres Netz.
7. Bau: der Name der DLL trägt den Hash der Quelltexte und Schalter; ohne Visual Studio kommt eine
   Fehlermeldung mit Ursache (kein Rückfall auf eine Näherung) und es entsteht kein Bauordner.

Sabotage-Gegenprobe (am 10.10.2026 ausgeführt, jeweils DLL neu gebaut, ~6 s; danach rückgängig):
* `mikkhuelle/hautbackenmikk.cc`: `orientation ? 1.0f : -1.0f` vertauscht → Fall 2 und 2b rot.
* dort der Modus 0 ohne `decode()` (float-Normale statt `entpackt(...)`) → Fall 3 und 4 rot,
  Fall 2 bleibt grün.
* `mikkhuelle/hautbackenblender.hh`: in `normalize_math` `v / l` → `v * (1.0f / l)` (ein Bit!) →
  Fall 1 und 2b rot.
* `hautbackentangenten.py`: `ecken_normalen` ignoriert → Fall 2 (jean), 3, 4 und 6 rot.

Der Test baut die DLL beim ersten Lauf (MSVC, ~6 s) und nimmt sie danach aus
`ProjektTemp/hautbacken_bau/`. Ohne Visual Studio laufen Fall 1–6 nicht (Fehlermeldung mit Ursache).
"""

import os
import shutil

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from core.dienste.hautbacken.hautbackenmikkbau import Hautbackenmikkbau
from core.dienste.hautbacken.hautbackenmikkfehler import Hautbackenmikkfehler
from core.dienste.hautbacken.hautbackentangenten import Hautbackentangenten

GOLDEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hautbacken_daten',
                      'tangenten_golden.npz')
MIT_BLENDER = ('kappe', 'gespiegelt', 'wuerfel_hart', 'wuerfel_glatt', 'verzerrt_glatt', 'verzerrt_flach',
               'rosemary_ausschnitt', 'jean_ausschnitt')
MIT_CYCLES = ('kappe', 'wuerfel_glatt', 'kappe_misch', 'kappe_flach', 'rosemary_ausschnitt',
              'jean_ausschnitt')
#: Netze, bei denen sich die float-Normalen von calc_tangents von Cycles' gepackten Normalen merklich
#: unterscheiden (glatt schattiert).
UNTERSCHEIDBAR = ('kappe', 'wuerfel_glatt', 'kappe_misch', 'rosemary_ausschnitt', 'jean_ausschnitt')
REST_CYCLES = 1.0e-6
REST_BLENDER_UNTEN = 5.0e-6


def _bits(a):
    return np.ascontiguousarray(a, dtype=np.float32).view(np.uint32)


class TangentenTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with np.load(GOLDEN) as daten:
            namen = sorted({k.split('__')[0] for k in daten.files})
            cls.netze = {n: {k.split('__', 1)[1]: daten[k] for k in daten.files if k.split('__')[0] == n}
                         for n in namen}

    # ------------------------------------------------------------------ Hilfen

    def _rechnen(self, name, modus, glatt=None, mit_normalen=True):
        e = self.netze[name]
        ecken = e.get('ecken_normalen')
        normalen = e['normalen'] if (mit_normalen and ecken is None) else None
        return Hautbackentangenten.berechnen(
            e['punkte'], e['dreiecke'], e['uv'], normalen=normalen,
            glatt=e['glatt'] if glatt is None else glatt, ecken_normalen=ecken, modus=modus)

    def _rest_gegen_cycles(self, name, modus, glatt=None):
        """Je Dreieck der größte Rest zwischen Cycles' gemessenem Vektor und dem Feld aus den
        Eckentangenten, nach Anpassung eines Versatzes (Texel)."""
        e = self.netze[name]
        t = self._rechnen(name, modus, glatt)[0].astype(np.float64)                  # (T,3,3)
        a, b, c = (e['uv'][:, k].astype(np.float64) for k in range(3))               # (T,2) je Ecke
        det = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (c[:, 0] - a[:, 0]) * (b[:, 1] - a[:, 1])
        w_bild = float(e['cyc_groesse'])
        tri, wert = e['cyc_dreieck'], e['cyc_wert'].astype(np.float64)
        px, py = (e['cyc_ix'] + 0.5) / w_bild, (e['cyc_iy'] + 0.5) / w_bild
        u = (((px - a[tri, 0]) * (c[tri, 1] - a[tri, 1]) - (c[tri, 0] - a[tri, 0]) * (py - a[tri, 1]))
             / det[tri])
        v = (((b[tri, 0] - a[tri, 0]) * (py - a[tri, 1]) - (px - a[tri, 0]) * (b[tri, 1] - a[tri, 1]))
             / det[tri])
        vorher = (1 - u - v)[:, None] * t[tri, 0] + u[:, None] * t[tri, 1] + v[:, None] * t[tri, 2]
        r = wert - vorher                                                           # (n,3)
        # Änderung der Vorhersage je Texel in x und y (das Feld ist im Dreieck linear)
        gu, gv = t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]
        dudx, dudy = (c[:, 1] - a[:, 1]) / det, -(c[:, 0] - a[:, 0]) / det
        dvdx, dvdy = -(b[:, 1] - a[:, 1]) / det, (b[:, 0] - a[:, 0]) / det
        gx = (gu * dudx[:, None] + gv * dvdx[:, None]) / w_bild                      # (T,3)
        gy = (gu * dudy[:, None] + gv * dvdy[:, None]) / w_bild
        # Kleinste Quadrate je Dreieck für den Versatz (dx, dy) in Texeln über alle Stichproben und
        # Achsen: (n G) d = [gx.R, gy.R]
        n = np.bincount(tri, minlength=len(t)).astype(np.float64)
        summe = np.zeros((len(t), 3))
        np.add.at(summe, tri, r)
        gxy = (gx * gy).sum(1)
        gram = np.stack([np.stack([(gx * gx).sum(1), gxy], axis=1),
                         np.stack([gxy, (gy * gy).sum(1)], axis=1)], axis=1) * n[:, None, None]
        rechts = np.stack([(gx * summe).sum(1), (gy * summe).sum(1)], axis=1)
        versatz = np.einsum('tij,tj->ti', np.linalg.pinv(gram, rcond=1e-9, hermitian=True), rechts)
        rest = np.abs(r - gx[tri] * versatz[tri, 0:1] - gy[tri] * versatz[tri, 1:2]).max(axis=1)
        je_dreieck = np.zeros(len(t))
        np.maximum.at(je_dreieck, tri, rest)
        return je_dreieck[n > 0]

    # ------------------------------------------------------------------ 1 Normalen

    def test_1_punktnormalen_bitgleich_blender(self):
        for name in MIT_BLENDER:
            e = self.netze[name]
            eigene = Hautbackentangenten.punktnormalen(e['punkte'], e['dreiecke'])
            self.assertEqual(eigene.shape, e['normalen'].shape, name)
            self.assertTrue(np.array_equal(_bits(eigene), _bits(e['normalen'])),
                            '%s: Punktnormalen weichen von mesh.vertex_normals ab' % name)

    # ------------------------------------------------------------------ 2 Modus „blender“

    def test_2_blender_modus_bitgleich_calc_tangents(self):
        for name in MIT_BLENDER:
            e = self.netze[name]
            t, v = self._rechnen(name, 'blender')
            self.assertEqual(t.shape, e['tangenten'].shape, name)
            self.assertTrue(
                np.array_equal(_bits(t), _bits(e['tangenten'])),
                '%s: Tangenten weichen von Blenders calc_tangents ab (max %.3e)'
                % (name, np.abs(t.astype(np.float64) - e['tangenten']).max()))
            self.assertTrue(np.array_equal(v, e['vorzeichen']), '%s: Vorzeichen weichen ab' % name)

    def test_2b_blender_modus_mit_eigenen_normalen(self):
        for name in MIT_BLENDER:
            if 'ecken_normalen' in self.netze[name]:
                continue      # Eckennormalen (scharfe Kanten) rechnet die Hülle nicht aus den Punkten
            e = self.netze[name]
            t, v = self._rechnen(name, 'blender', mit_normalen=False)
            self.assertTrue(np.array_equal(_bits(t), _bits(e['tangenten'])), name)
            self.assertTrue(np.array_equal(v, e['vorzeichen']), name)

    def test_2c_ohne_eckennormalen_weicht_jean_ab(self):
        """Gegenprobe: die Eckennormalen tragen — nur mit Punktnormalen ist `jean` (scharfe Kanten)
        deutlich anders."""
        e = self.netze['jean_ausschnitt']
        t, _ = Hautbackentangenten.berechnen(e['punkte'], e['dreiecke'], e['uv'], normalen=e['normalen'],
                                             glatt=e['glatt'], modus='blender')
        self.assertGreater(np.abs(t.astype(np.float64) - e['tangenten']).max(), 0.1)

    # ------------------------------------------------------------------ 3 Modus „cycles“

    def test_3_cycles_modus_gegen_cycles_bild(self):
        for name in MIT_CYCLES:
            rest = self._rest_gegen_cycles(name, 'cycles')
            self.assertGreater(len(rest), 10 if name != 'wuerfel_glatt' else 5, name)
            self.assertLessEqual(rest.max(), REST_CYCLES, '%s: Rest gegen Cycles %.3e' % (name, rest.max()))

    def test_3b_float_normalen_liegen_bei_glatten_netzen_darueber(self):
        for name in UNTERSCHEIDBAR:
            rest = self._rest_gegen_cycles(name, 'blender')
            self.assertGreater(
                np.quantile(rest, 0.9), REST_BLENDER_UNTEN,
                '%s: der Test unterscheidet Cycles nicht von calc_tangents (90%% = %.3e)'
                % (name, np.quantile(rest, 0.9)))

    # ------------------------------------------------------------------ 4 Glatt-Flag

    def test_4_glatt_flag_zaehlt_bei_eckennormalen(self):
        name = 'kappe_misch'
        e = self.netze[name]
        glatt = e['glatt']
        self.assertTrue(0 < int(glatt.sum()) < len(glatt), 'kappe_misch braucht glatte UND flache Dreiecke')
        richtig = self._rest_gegen_cycles(name, 'cycles')
        alle_glatt = self._rest_gegen_cycles(name, 'cycles', glatt=np.ones(len(glatt), dtype=bool))
        self.assertLessEqual(richtig.max(), REST_CYCLES)
        self.assertGreater(alle_glatt.max(), 1.0e-5)

    # ------------------------------------------------------------------ 5 Golden nicht leer

    def test_5_golden_enthaelt_beide_vorzeichen(self):
        self.assertEqual(set(MIT_BLENDER) | set(MIT_CYCLES), set(self.netze))
        v = self.netze['gespiegelt']['vorzeichen']
        self.assertEqual(set(np.unique(v)), {-1.0, 1.0})
        self.assertGreater(int((self.netze['kappe']['vorzeichen'] < 0).sum()), 0)
        self.assertGreater(sum(len(self.netze[n]['cyc_dreieck']) for n in MIT_CYCLES), 20000)

    # ------------------------------------------------------------------ 6 Eingaben

    def test_6_eingaben(self):
        e = self.netze['wuerfel_glatt']
        p, d, uv = e['punkte'], e['dreiecke'], e['uv']
        for falsch in ({'punkte': p[:, :2]}, {'dreiecke': d[:, :2]}, {'uv_ecken': uv[:-1]},
                       {'normalen': e['normalen'][:-1]}, {'glatt': e['glatt'][:-1]},
                       {'ecken_normalen': np.zeros((len(d), 3, 2))}, {'modus': 'ungefaehr'}):
            args = dict(punkte=p, dreiecke=d, uv_ecken=uv)
            args.update(falsch)
            with self.assertRaises(ValueError, msg=str(list(falsch))):
                Hautbackentangenten.berechnen(**args)
        with self.assertRaises(Hautbackenmikkfehler):
            Hautbackentangenten.berechnen(p, d + 100, uv)
        t, v = Hautbackentangenten.berechnen(p, np.zeros((0, 3), dtype=np.int32), np.zeros((0, 3, 2)))
        self.assertEqual((t.shape, v.shape), ((0, 3, 3), (0, 3)))
        t, v = Hautbackentangenten.berechnen(p, d, uv)      # Vorgabe: alle glatt, eigene Punktnormalen
        self.assertEqual((t.shape, v.shape), ((len(d), 3, 3), (len(d), 3)))
        self.assertEqual((t.dtype, v.dtype), (np.float32, np.float32))
        self.assertTrue(np.isfinite(t).all())
        self.assertTrue(np.allclose(np.linalg.norm(t, axis=2), 1.0, atol=1e-5))

    # ------------------------------------------------------------------ 7 Bau

    def test_7_dllname_traegt_hash_und_fehlendes_visual_studio_meldet_ursache(self):
        bau = Hautbackenmikkbau()
        self.assertEqual(bau.dll_pfad().name, 'hautbacken_mikk_%s.dll' % bau.quell_hash())
        self.assertEqual(len(bau.quell_hash()), 16)

        class _AndereSchalter(Hautbackenmikkbau):
            SCHALTER = Hautbackenmikkbau.SCHALTER + ('/DANDERS',)

        self.assertNotEqual(_AndereSchalter().quell_hash(), bau.quell_hash())

        ordner = os.path.join(str(settings.TOOLS_ROOT), 'ProjektTemp', 'hautbacken_bau', '_test_ohne_vs')

        class _OhneVisualStudio(Hautbackenmikkbau):
            VSWHERE = type(Hautbackenmikkbau.VSWHERE)(os.path.join(ordner, 'gibt_es_nicht', 'vswhere.exe'))

        try:
            with self.assertRaises(Hautbackenmikkfehler) as ctx:
                _OhneVisualStudio(ordner).bauen()
            self.assertIn('vswhere.exe fehlt', str(ctx.exception))
            self.assertFalse(os.path.isdir(ordner), 'ohne Visual Studio darf kein Bauordner entstehen')
        finally:
            shutil.rmtree(ordner, ignore_errors=True)

# -*- coding: utf-8 -*-
"""`hautbacken/closure` — die gebackene Normale als gewichtetes Mittel der Closure-Normalen des Principled BSDF (`surface_shader_average_normal`, Cycles v5.2.2), ohne Blender, mit Fällen,
die von Hand nachzurechnen sind. Der Vergleich mit Blender selbst (49 Materialien) steht in `test_hautbacken_zoo.py`.

Eingänge wie im Principled BSDF von Blender 5.2: Diffus nimmt die Normale des Graphen `n`; Glanz, Metall und Untergrund `ensure_valid_specular_reflection(n)` (nur mit „Bump Map Correction");
der Coat `sd->N` (die geglättete Normale — ein unverbundener „Coat Normal" hängt Cycles an den Geometry-Knoten), die Sheen-Schicht `normalize(mix(n, sd->N, coat_weight))`.

Sabotage-Gegenprobe (11.10.2026, je eine Änderung in `hautclosurekernel.py`, danach rückgängig): siehe Ende der Datei.
"""

import math

import numpy as np
import warp as wp
from django.test import SimpleTestCase

from core.dienste.hautbacken.closure import Hautclosure
from core.dienste.hautbacken.closure.hautclosure import EINGAENGE
from core.dienste.hautbacken.closure.hautclosurekernel import normale_mittel
from core.dienste.hautbacken.graph import hautalphakernel as alpha_kern
from core.dienste.hautbacken.graph.hautalpha import Hautalpha

GERAET = 'cuda:0'
Z = (0.0, 0.0, 1.0)
#: Vorgaben des Principled BSDF in Blender 5.2 (Eingang → Wert), der Kern liest sie als Felder.
VORGABE = {'basis': (0.8, 0.8, 0.8), 'metallisch': 0.0, 'rauheit': 0.5, 'ior': 1.5, 'spec_stufe': 0.5, 'spec_tint': (1.0, 1.0, 1.0), 'aniso': 0.0,
           'sheen_g': 0.0, 'sheen_r': 0.5, 'sheen_t': (1.0, 1.0, 1.0), 'coat_g': 0.0, 'coat_r': 0.03, 'coat_i': 1.5, 'coat_t': (1.0, 1.0, 1.0), 'trans_g': 0.0,
           'sss_g': 0.0, 'sss_radius': (1.0, 0.2, 0.1), 'sss_skala': 0.05}
SKALARE = ('metallisch', 'rauheit', 'ior', 'spec_stufe', 'aniso', 'sheen_g', 'sheen_r', 'coat_g', 'coat_r', 'coat_i', 'trans_g', 'sss_g', 'sss_skala')


def geneigt(grad):
    """Einheitsvektor, um `grad` von der z-Achse geneigt."""
    w = math.radians(grad)
    return (math.sin(w), 0.0, math.cos(w))


def winkel(a, b):
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    return math.degrees(math.acos(float(np.clip(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), -1.0, 1.0))))


class Kern:
    """Startet `normale_mittel` für eine Liste von Normalen mit den Vorgaben (und überschriebenen Eingängen)."""
    closure = None

    @classmethod
    def laden(cls):
        wp.init()
        if cls.closure is None:
            cls.closure = Hautclosure(GERAET)
        return cls.closure

    @classmethod
    def mittel(cls, normalen, ng=Z, n_glatt=Z, rueck=0, korrektur=1, multi=1, coat_n=None, **eingaenge):
        """`coat_n`: die verbundene Coat-Normale (None = unverbunden → `sd->N`)."""
        t = cls.laden().tabellen
        k = len(normalen)
        werte = {**VORGABE, **eingaenge}

        def feld(name):
            w = werte[name]
            if name in SKALARE:
                return wp.array(np.full(k, w, dtype=np.float32), dtype=wp.float32, device=GERAET)
            return wp.array(np.tile(np.asarray(w, dtype=np.float32), (k, 1)), dtype=wp.vec3, device=GERAET)

        vec = lambda a: wp.array(np.asarray(a, dtype=np.float32).reshape(-1, 3) if np.ndim(a) > 1 else np.tile(np.asarray(a, dtype=np.float32), (k, 1)), dtype=wp.vec3, device=GERAET)   # noqa: E731
        aus = wp.zeros(k, dtype=wp.vec3, device=GERAET)
        wp.launch(normale_mittel, dim=k, inputs=[vec(normalen), vec(ng), vec(n_glatt), wp.array(np.full(k, rueck, dtype=np.int32), dtype=wp.int32, device=GERAET),
                                                 feld('basis'), feld('metallisch'), feld('rauheit'), feld('ior'), feld('spec_stufe'), feld('spec_tint'), feld('aniso'),
                                                 feld('sheen_g'), feld('sheen_r'), feld('sheen_t'), feld('coat_g'), feld('coat_r'), feld('coat_i'), feld('coat_t'),
                                                 vec(n_glatt if coat_n is None else coat_n), int(coat_n is not None), feld('trans_g'),
                                                 feld('sss_g'), feld('sss_radius'), feld('sss_skala'), int(multi), 0, int(korrektur),
                                                 t['ggx_E'], t['ggx_Eavg'], t['ggx_gen_schlick_ior_s'], t['sheen_ltc'],
                                                 t['ggx_glass_E'], t['ggx_glass_Eavg'], t['ggx_glass_inv_E'], t['ggx_glass_inv_Eavg'], aus], device=GERAET)
        return aus.numpy()


class ClosureMittelTest(SimpleTestCase):
    databases = set()

    # ------------------------------------------------------------------ Normale gleich Fläche, nur Diffus

    def test_1_n_gleich_flaeche_gibt_die_normale_mit_allen_schichten(self):
        """Liegen `n`, `sd->N` und `Ng` aufeinander, haben alle Closures dieselbe Normale — auch mit Coat, Sheen, Metall und Untergrund."""
        aus = Kern.mittel([Z], coat_g=1.0, sheen_g=1.0, metallisch=0.5, sss_g=0.5)[0]
        self.assertLess(winkel(aus, Z), 0.01)

    def test_2_nur_diffus_nimmt_die_normale_des_graphen_ohne_jede_korrektur(self):
        """Ohne Glanz (`Specular IOR Level` 0 → η = 1), Metall, Coat, Sheen und Untergrund ist nur die Diffus-Closure da, und sie bekommt `n` unverändert, wie stark geneigt auch."""
        for grad in (0, 30, 60, 85):
            n = geneigt(grad)
            for korrektur in (0, 1):
                aus = Kern.mittel([n], spec_stufe=0.0, korrektur=korrektur)[0]
                self.assertLess(winkel(aus, n), 0.01, (grad, korrektur))

    # ------------------------------------------------------------------ Glanz

    def test_3_glanz_wird_bei_starker_neigung_zur_flaeche_gehoben_und_nur_mit_korrektur(self):
        """Glatte Fläche (`wi = Ng`): über 44,7° Neigung fiele die Spiegelung unter die Fläche, Cycles hebt die Normale der Glanz-Closure an; das Mittel liegt dann zwischen `n` und Ng.
        Ohne „Bump Map Correction" bleibt alles bei `n`."""
        stark, schwach = geneigt(70), geneigt(30)
        self.assertLess(winkel(Kern.mittel([stark], korrektur=0)[0], stark), 0.01)
        gehoben = winkel(Kern.mittel([stark], korrektur=1)[0], Z)
        self.assertLess(gehoben, 69.0)
        self.assertGreater(gehoben, 30.0)                                  # das Mittel bleibt zwischen den Closures: Diffus (n) hat Gewicht
        self.assertLess(winkel(Kern.mittel([schwach], korrektur=1)[0], schwach), 0.01)

    # ------------------------------------------------------------------ Coat

    def test_4_die_coat_normale_ist_die_geglaettete_normale_nicht_die_der_normalenkarte(self):
        """Nur Coat + Diffus (kein Glanz): Der Coat hat die Normale `sd->N` = Ng (Z), Diffus die geneigte `n` (60°). Von Hand: Coat-Gewicht ≈ 1 (glatt, `coat_weight` 1), Diffus
        ≈ 0,8·(1 − F) ≈ 0,77 (F ≈ 0,04 bei senkrechtem Blick) → Mittel = Z·1 + n·0,77: Winkel zu Z = atan2(0,77·sin60°, 1 + 0,77·cos60°) = 25,7°. Das gilt mit und ohne Korrektur —
        der Coat ändert sich mit dem Schalter nicht, `sd->N` liegt schon auf der Fläche."""
        n = geneigt(60)
        for korrektur in (0, 1):
            w = winkel(Kern.mittel([n], spec_stufe=0.0, coat_g=1.0, korrektur=korrektur)[0], Z)
            self.assertAlmostEqual(w, 25.7, delta=3.0, msg=korrektur)

    def test_5_mehr_coat_zieht_die_normale_naeher_an_die_flaeche(self):
        n = geneigt(60)
        w = [winkel(Kern.mittel([n], spec_stufe=0.0, coat_g=g)[0], Z) for g in (0.0, 0.25, 0.5, 1.0)]
        self.assertAlmostEqual(w[0], 60.0, delta=0.01)
        for a, b in zip(w, w[1:], strict=False):
            self.assertGreater(a - b, 2.0, w)                              # gemessen 11,10,9 Grad pro Schritt; Rauschen der Gleitkommazahlen wäre ≪ 0,01

    def test_6_die_coat_normale_folgt_der_geglaetteten_normale_nicht_ng(self):
        """Ist `sd->N` gegen Ng geneigt (glatte Fläche, Dreiecksrand), zieht der Coat zu `sd->N`. Von Hand: `n` bei 60°, `sd->N` bei 20° (40° auseinander), Gewichte Coat 1 und Diffus
        ≈ 0,77 → Mittel = ns·1 + n·0,77: Winkel zu ns = atan2(0,77·sin40°, 1 + 0,77·cos40°) = 17,3°. Zöge der Coat zu `n` (oder zu Ng), läge es bei 0° bzw. 20°–40°."""
        ns = geneigt(20)
        aus = Kern.mittel([geneigt(60)], n_glatt=ns, spec_stufe=0.0, coat_g=1.0)[0]
        self.assertAlmostEqual(winkel(aus, ns), 17.3, delta=3.0)

    def test_7_sheen_mit_coat_nimmt_eine_gemischte_normale(self):
        """Sheen-Normale = normalize(mix(n, sd->N, coat_weight)). Isoliert: eine riesige Sheen-Tönung (1e6; die Albedo der Sheen-Closure ist nur ~0,01, mit 100 bliebe Diffus übrig)
        lässt der obersten Schicht das ganze Licht (`closure_layering_weight` → 0), Coat und Diffus bekommen Gewicht 0, nur die Sheen-Closure bleibt, und das Mittel IST ihre Normale.
        Von Hand mit `n` bei 60°, `sd->N` = Z: Coat 0 → 60°; Coat 0,5 → normalize(0,5·(sin60°, cos60°) + 0,5·(0, 1)) = (0,433, 0,75) → 30,0°; Coat 1 → 0°."""
        n = geneigt(60)
        for coat, erwartet in ((0.0, 60.0), (0.5, 30.0), (1.0, 0.0)):
            aus = Kern.mittel([n], spec_stufe=0.0, sheen_g=1.0, sheen_r=0.3, sheen_t=(1.0e6, 1.0e6, 1.0e6), coat_g=coat)[0]
            self.assertAlmostEqual(winkel(aus, Z), erwartet, delta=0.1, msg=coat)

    # ------------------------------------------------------------------ verbundene Coat-Normale

    def test_7c_eine_verbundene_coat_normale_ersetzt_sd_n(self):
        """Wie Test 6, aber die Coat-Normale kommt aus dem Graphen (20° geneigt, `sd->N` = Z): Mittel = coat·1 + n·0,77 → 17,3° zur Coat-Normale. Unverbunden zählt `sd->N` (Z), egal was im
        Feld steht; eine verbundene Nullnormale fällt auf `sd->N` zurück (`safe_normalize_fallback`)."""
        n, nc = geneigt(60), geneigt(20)
        verbunden = Kern.mittel([n], spec_stufe=0.0, coat_g=1.0, coat_n=nc)[0]
        self.assertAlmostEqual(winkel(verbunden, nc), 17.3, delta=3.0)
        unverbunden = Kern.mittel([n], spec_stufe=0.0, coat_g=1.0)[0]
        self.assertAlmostEqual(winkel(unverbunden, Z), 25.7, delta=3.0)
        null = Kern.mittel([n], spec_stufe=0.0, coat_g=1.0, coat_n=(0.0, 0.0, 0.0))[0]
        self.assertLess(winkel(null, unverbunden), 0.01)

    def test_7d_die_verbundene_coat_normale_geht_auch_in_die_sheen_normale_ein(self):
        """Sheen-Normale = normalize(mix(n, coat_normal, c)) — mit der Sheen-Tönung 1e6 (Test 7) ist sie das ganze Mittel. Coat 0,5, `n` bei 60°, Coat-Normale bei 20°:
        normalize(0,5·(sin60°, cos60°) + 0,5·(sin20°, cos20°)) = Mittelwinkel 40,0°."""
        aus = Kern.mittel([geneigt(60)], spec_stufe=0.0, sheen_g=1.0, sheen_r=0.3, sheen_t=(1.0e6, 1.0e6, 1.0e6), coat_g=0.5, coat_n=geneigt(20))[0]
        self.assertAlmostEqual(winkel(aus, Z), 40.0, delta=0.1)

    # ------------------------------------------------------------------ Transmission

    def test_7e_transmission_hat_das_gewicht_und_die_normale_eines_metalls_ohne_energieerhaltung(self):
        """Ohne Glanz (`Specular IOR Level` 0) und mit weißer Basis ist das Glas-Closure `transmission · weight`, der Rest `(1 − transmission)` Diffus — wie Metall (`metallic · weight`, Rest
        Diffus), solange keine Energieerhaltung eingreift (GGX; bei Multi-GGX und weißer Basis ist Fss = 1, also auch keine). Beide bekommen die gültige Normale, Diffus `n`: das Mittel ist
        dasselbe. Stark geneigt (70°) hebt die Korrektur die Normale des Glases; ohne Korrektur bleibt alles bei `n`."""
        n = geneigt(70)
        weiss = {'basis': (1.0, 1.0, 1.0), 'spec_stufe': 0.0}
        for anteil in (0.3, 0.5, 1.0):
            for multi in (0, 1):
                glas = Kern.mittel([n], multi=multi, trans_g=anteil, **weiss)[0]
                metall = Kern.mittel([n], multi=0, metallisch=anteil, **weiss)[0]
                self.assertLess(winkel(glas, metall), 0.01, (anteil, multi))
        voll = winkel(Kern.mittel([n], trans_g=1.0, **weiss)[0], n)
        self.assertGreater(voll, 5.0)                                            # das Glas allein steht nicht auf `n`, sondern auf der gehobenen Normale
        self.assertLess(winkel(Kern.mittel([n], trans_g=1.0, korrektur=0, **weiss)[0], n), 0.01)
        self.assertLess(winkel(Kern.mittel([n], trans_g=0.0, **weiss)[0], n), 0.01)    # ohne Transmission und ohne Glanz nur Diffus

    def test_7f_transmission_nimmt_den_schichten_darunter_nur_ihren_anteil(self):
        """Die Schichten unter dem Glas behalten `1 − transmission` ohne Albedo-Abzug: mit Glanz (η ≠ 1) und Transmission 1 bleibt für Glanz und Diffus nichts übrig; das Mittel ist die
        Glas-Normale allein (= die des Metalls mit Anteil 1)."""
        n = geneigt(70)
        glas = Kern.mittel([n], trans_g=1.0, multi=0)[0]
        metall = Kern.mittel([n], metallisch=1.0, multi=0)[0]
        self.assertLess(winkel(glas, metall), 0.01)

    # ------------------------------------------------------------------ Alpha

    def test_7b_der_normal_pass_faellt_unter_alpha_0_5_weg(self):
        """`hautalphakernel.nullen`: Alpha < 0,5 → Nullvektor (Blender schreibt dort (128,128,128)), ab 0,5 unverändert (`average(alpha) >= pass_alpha_threshold`); Alpha außerhalb 0…1 wird geklemmt.
        Darüber ändert Alpha die gebackene Normale nicht (Zoo `glanz_alpha_fest`: 0,01 Stufen Abweichung gegen Blender, mit einer Transparent-Closure im Mittel wären es 12)."""
        wp.init()
        alpha = [-0.3, 0.0, 0.2, 0.4999, 0.5, 0.9, 1.0, 1.7]
        welt = np.tile(np.array([0.0, 0.6, 0.8], dtype=np.float32), (len(alpha), 1))
        aus = wp.zeros(len(alpha), dtype=wp.vec3, device=GERAET)
        wp.launch(alpha_kern.nullen, dim=len(alpha), inputs=[wp.array(np.asarray(alpha, dtype=np.float32), dtype=wp.float32, device=GERAET), Hautalpha.SCHWELLE,
                                                             wp.array(welt, dtype=wp.vec3, device=GERAET), aus], device=GERAET)
        erwartet = [0, 0, 0, 0, 1, 1, 1, 1]
        self.assertEqual([int(np.linalg.norm(v) > 0.5) for v in aus.numpy()], erwartet)
        self.assertEqual(Hautalpha.SCHWELLE, 0.5)

    # ------------------------------------------------------------------ Aufrufer: Gründe und Auslöser

    @staticmethod
    def _spec(**ueberschrieben):
        p = {name: {'wert': 0.0} for name, _ in EINGAENGE}
        p.update(ueberschrieben)
        return {'principled': p, 'principled_eig': {'distribution': 'MULTI_GGX'}}

    def test_8_was_das_modell_nicht_rechnet_wird_benannt(self):
        spec = self._spec()
        self.assertEqual(Hautclosure.grund(spec), '')
        self.assertIn('älterer Export', Hautclosure.grund({}))
        for eingang, wert, stichwort in (('Thin Wall', {'wert': 1.0}, 'Thin Wall'), ('Thin Film Thickness', {'wert': 200.0}, 'Dünnfilm')):
            spec = self._spec(**{eingang: wert})
            self.assertIn(stichwort, Hautclosure.grund(spec), eingang)
        for eingang, wert in (('Transmission Weight', {'wert': 1.0}), ('Transmission Weight', {'von': ['x', 0]}), ('Coat Normal', {'von': ['x', 0]})):   # seit 12.10.2026 gerechnet
            self.assertEqual(Hautclosure.grund(self._spec(**{eingang: wert})), '', eingang)
        for alpha in ({'wert': 0.5}, {'wert': 1.0}, {'von': ['x', 0]}):         # Alpha ist kein Grund mehr (Hautalpha + unveränderte Richtung), verbunden oder fest
            self.assertEqual(Hautclosure.grund(self._spec(Alpha=alpha)), '', alpha)
        spec = self._spec()
        spec['principled_eig'] = {'distribution': 'RANDOM_WALK'}
        self.assertIn('Verteilung', Hautclosure.grund(spec))

    def test_9_lack_moeglich_wenn_das_gewicht_verbunden_oder_positiv_ist(self):
        self.assertFalse(Hautclosure.lack_moeglich(self._spec()))
        self.assertFalse(Hautclosure.lack_moeglich({}))
        self.assertTrue(Hautclosure.lack_moeglich(self._spec(**{'Coat Weight': {'wert': 0.5}})))
        self.assertTrue(Hautclosure.lack_moeglich(self._spec(**{'Coat Weight': {'von': ['x', 0]}})))
        self.assertFalse(Hautclosure.lack_moeglich(self._spec(**{'Coat Weight': {'wert': 0.0}})))

    def test_10_alpha_unter_der_schwelle_des_normal_passes_ist_moeglich(self):
        """`Hautalpha.moeglich`: Alpha unter 0,5 (verbunden oder fest) → der Normal-Pass kann wegfallen; sonst rechnet `Hautalpha` nichts."""
        ohne, eins, halb, schwach = self._spec(), self._spec(Alpha={'wert': 1.0}), self._spec(Alpha={'wert': 0.7}), self._spec(Alpha={'wert': 0.3})
        verbunden = self._spec(Alpha={'von': ['x', 0]})
        self.assertEqual([Hautalpha.moeglich(s) for s in (ohne, eins, halb, schwach, verbunden)], [False, False, False, True, True])


# Sabotage-Gegenprobe (11.10.2026, je eine Änderung in `hautclosurekernel.py`, danach rückgängig, nur diese Datei, ~9 s):
# * Coat-Normale `n` statt `sd->N` (beide Zeilen)           → Test 4 rot (Korrektur aus) und Test 6 rot (Winkel zu ns 40° statt 17,3°)
# * Sheen-Normale `n` statt `normalize(mix(n, sd->N, c))`   → Test 7 rot (59,99° statt 30,0° bei Coat 0,5)
# * `gueltig` immer korrigiert (Schalter ignoriert)         → Test 3 rot
# * `gueltig` nie korrigiert                                → Test 3 rot
# Alpha (`hautalpha.py`): Schwelle 0,5 → 0,0 macht den Zoo-Test 4 rot (siehe dort); hier prüft Test 7b die Schwelle selbst (`Hautalpha.SCHWELLE == 0.5`, Nullvektor unter 0,5).
# 12.10.2026 (Fälle 7c–7f): die Erwartungswerte sind mit `ProjektTemp/_wegwerf/cycles_vergleich/closure_testwerte.py` am Kern nachgerechnet (17,26° / 25,67° / 40,00° / Glas = Metall auf 0,00°);
# die Sabotage-Gegenprobe dieser Fälle wurde nicht per Testlauf gemacht — gegen Blender zeigt der Zoo (`test_hautbacken_zoo.py`, Fußzeile) für Transmission, Coat-Normale, Tangente und die
# Glas-Energieerhaltung je eine rote Änderung.
# Gegen Blender (Zoo, `test_hautbacken_zoo.py` Test 4): vor der Coat-Normalen-Korrektur lagen `glanz_lack` bei 25,4, `glanz_lack_halb_tint` 19,6, `glanz_sheen_lack` 34,5 und `glanz_alles`
# 23,2 Stufen Mittel (Grenze 0,5); mit der Korrektur, aber nur an den Texeln mit nötiger Glanz-Korrektur (nicht an allen), noch `glanz_lack` 0,88 / p99 39 (102 Texel).

# -*- coding: utf-8 -*-
"""Blender-Import: Abnahme der Stücke (Stufe 7 des Konzepts) und die Befunde, die sie ans Licht brachte (09.10.2026).

Edgar: „das muss doch generisch für jedes Modell gelten" — das Konzept `Docu/konzepte/2026-10-09_blend-import-kleidung-in-die-ruhelage-konzept.md`
und danach der Bau von Haltungstreue, Kantenverzerrung, Kontaktbogen, `h`-Einheiten, Requisit-Klasse und dem gedämpften Fixpunkt. Gemessen an
drei Modellen (cute girl, Asian Female, Fallout ranger).

1. Kantenverzerrung: Anteil der Kanten außerhalb 0,75…1,33 und größte Streckung (`Blendimportpruefung.kanten`).
2. Die Schwellen lösen Hinweise aus (`warnungen`) — nie stilles Durchlaufen.
3. Die Inselgrenze rechnet in Einheiten der Stückkante, begrenzt durch eine Fläche in `h²` (`Blendimportlage.insel_punkte`):
   0,5 mm Kante (BH) → größere Grenze, 11 mm (Pullover) → kleinere, ein Netz mittlerer Kante bleibt bei 150 Punkten.
4. Der volle Schritt des Fixpunkts `q ← q + (Ziel − Folgen(q))` kann schwingen (Stiefel am Rist: 13,4 mm blieben stehen); der halbe Schritt mit
   bestem Stand je Punkt kommt an (`G9gcfigurbau._daempfen`).
5. Ein Stück, das zu weit vom Körper hängt, geht starr mit dem Teil, das es berührt (`Blendimportrequisit`): die Waffe des „Fallout ranger"
   berührt den Rumpf, hängt aber im Median 77 mm vom Käfig — Stoff am Körper bleibt, was er ist.
6. Der Schuh steht flach (Edgar: „der Stiefel soll flach am Boden sitzen"): das Original steht auf Zehenspitzen (Sohle des Stiefels 21–33° geneigt,
   gemessen im Browser 28–31°), die Drehung des Körperfußes (55°) hätte den Stiefel mit schräger Sohle gestellt. `Blendimportfuss.waagrecht`
   dreht den Fuß so, dass die Sohle waagrecht liegt — ein Keilschuh bekommt den Fußwinkel seines Keils, eine flache Sohle Fuß 0°.
7. Die Sohle kommt aus der Form des Schuhs, nicht aus der Fußachse des Körpers (`Blendimportsohle`). Die erste Fassung teilte die Schuhlänge entlang der Fußachse
   des Körpers (Asian Female: Fuß steckt im Stiefel) und zerstörte beim Fallout ranger — Körper ohne Füße, Körperfuß 57°, flacher Stiefel — die flache Sohle
   (Zusatz −75°). Fall 7: flacher Stiefel mit hohem Schaft bleibt flach, derselbe Stiefel auf Zehenspitzen (35°) wird gerade gestellt, Absatzschuh mit Spitzenfeder,
   eine Kugel hat keine Sohle, dünne Punktmengen.
8. Wo der Körper den Fuß nicht trägt (Punkte im Fußteil gegen Käfigpunkte, ICP-Rest in `h`), sagt der Bericht es (`verlaesslich`, `hinweise`).
9. Die Schwellen der Abnahme (Kantenverzerrung, Haltungstreue in `h`) halten an den gemessenen Werten dreier Modelle (`KalibrierungTest`): anliegende Stücke ohne Hinweis,
   hängende (Hemd-Ärmel, Mantel) und der zerstörte Stiefel mit; „frei hängend" allein warnt nicht mehr, wo die Haltungstreue gemessen ist.
10. Die Kopplung beim Entzerren ist auf drei Stückkanten begrenzt (`Blendimportlage.KOPPELN_E`): ein dichtes Netz (BH, Kante 0,5 mm) koppelte ganze Nachbarschaften.

Sabotage-Gegenprobe: in `kanten` die Ober- und Untergrenze streichen → Fall 1 rot; in `insel_punkte` die Begrenzung weglassen → Fall 3 rot;
`DAEMPFUNG` auf 1,0 setzen → Fall 4 rot; in `erkennen` die Abstandsbedingung streichen → Fall 5b rot; in `neigung` das Vorzeichen von `winkel` umdrehen → Fall 6, 6b
und 7 rot (gemessen: 6, 6b, 6c, 7b, 7c); in `nachstellen` `abs(rest) >= SOHLE_TOLERANZ` zu `False` machen → Fall 6c rot; `SPANNE_ANTEIL` auf 0 setzen → Fall 7d rot;
`FUSS_DECKUNG_MIN` auf 0 UND `FUSS_REST_H_MAX` auf 1e9 setzen → Fall 8b rot; `HALTUNG_P99_H` auf 2,5 setzen → Fall 9 und 9b rot; `KOPPELN_E` auf `float('inf')` setzen →
Fall 10 und 10b rot (`ProjektTemp/_wegwerf/sabotage_abnahme2.py <vorzeichen|spanne|zuverlaessig|schwelle|kopplung>`).

Alles an Kunstdaten, ohne Datenbank.
"""

import unittest
from types import SimpleNamespace

import numpy as np
from Genesis9.gcfigurbau import G9gcfigurbau
from Genesis9.koerperteile import G9koerperteile
from scipy.spatial import cKDTree

from core.dienste.blendimportbogen import Blendimportbogen
from core.dienste.blendimportfuss import Blendimportfuss
from core.dienste.blendimportlage import Blendimportlage
from core.dienste.blendimportpruefung import Blendimportpruefung
from core.dienste.blendimportrequisit import Blendimportrequisit
from core.dienste.blendimportsohle import Blendimportsohle


def _gitter(n, kante):
    """n × n Punkte in der Ebene z = 0 mit Kantenlänge `kante`, in Dreiecken."""
    x, y = np.meshgrid(np.arange(n) * kante, np.arange(n) * kante)
    punkte = np.column_stack([x.ravel(), y.ravel(), np.zeros(n * n)])
    dreiecke = []
    for i in range(n - 1):
        for j in range(n - 1):
            a = i * n + j
            dreiecke += [[a, a + 1, a + n], [a + 1, a + n + 1, a + n]]
    return punkte, np.array(dreiecke)


class KantenUndHinweiseTest(unittest.TestCase):
    def test_1_kanten(self):
        p, d = _gitter(6, 0.01)
        gleich = Blendimportpruefung.kanten(p, p, d)
        self.assertEqual(gleich['ausserhalb'], 0.0)
        self.assertAlmostEqual(gleich['streckung_max'], 1.0)
        gedehnt = p.copy()
        gedehnt[:, 0] *= 2.0                                # jede waagrechte Kante doppelt so lang
        s = Blendimportpruefung.kanten(gedehnt, p, d)
        self.assertGreater(s['ausserhalb'], 0.3)
        self.assertAlmostEqual(s['streckung_max'], 2.0, places=2)     # die waagrechten Kanten; die Diagonalen wachsen auf 1,58

    def test_2_hinweise_mit_schwellen(self):
        gut = {'ausserhalb': 0.001, 'streckung_max': 1.4, 'streckung_min': 0.8}
        haltung = {'median_mm': 1.0, 'p99_mm': 4.0, 'ueber_25': 0.0}
        self.assertEqual(Blendimportpruefung.warnungen(gut, {'frei_anteil': 0.1}, haltung), [])
        schlecht = {'ausserhalb': 0.06, 'streckung_max': 3.4, 'streckung_min': 0.2}
        aus = Blendimportpruefung.warnungen(schlecht, {'frei_anteil': 0.6}, {'median_mm': 2.0, 'p99_mm': 74.0, 'ueber_25': 0.045})
        self.assertEqual(len(aus), 2, '„frei hängend" warnt nicht mehr, wo die Haltungstreue gemessen ist: sie sagt, ob es sitzt')
        self.assertIn('Kantenverzerrung', aus[0])
        self.assertIn('Haltungstreue', aus[1])
        self.assertEqual(Blendimportpruefung.warnungen(gut, {}, {'fehler': 'Punktzahl'}), [], 'ein Fehler der Haltungsmessung ist kein Hinweis')
        ungemessen = Blendimportpruefung.warnungen(gut, {'frei_anteil': 0.9}, None)
        self.assertEqual(len(ungemessen), 1, 'ohne Haltungstreue bleibt der Hinweis „Sitz ungeprüft"')
        self.assertIn('hängen frei', ungemessen[0])

    def test_2b_bogen_findet_verzerrte_dreiecke(self):
        p, d = _gitter(6, 0.01)
        ruhe = p.copy()
        ruhe[0] += np.array([0.02, 0.0, 0.0])               # eine Ecke weit weg: ihre Dreiecke haben verzerrte Kanten
        schlecht = Blendimportbogen.schlechte_dreiecke(ruhe, p, d)
        self.assertTrue(schlecht[(d == 0).any(axis=1)].all(), 'jedes Dreieck der Ecke zählt')
        self.assertLess(schlecht.sum(), len(d) / 3, 'die übrigen bleiben unmarkiert')


class InselGrenzeTest(unittest.TestCase):
    def test_3_einheiten_der_stueckkante(self):
        lage = SimpleNamespace(h=0.004, INSEL_E2=Blendimportlage.INSEL_E2, INSEL_FLAECHE_H2=Blendimportlage.INSEL_FLAECHE_H2)

        def grenze(kante):
            p, d = _gitter(8, kante)
            return Blendimportlage.insel_punkte(lage, p, d)

        self.assertEqual(grenze(0.006), 150, 'mittlere Kante: 150 Punkte wie bisher')
        self.assertGreater(grenze(0.0005), 1000, 'dichtes Netz (BH): die Fläche zählt, nicht die Punktzahl')
        self.assertLess(grenze(0.013), 120, 'grobes Netz (Socke): sonst wären 150 Punkte 230 cm²')
        flaeche = lambda k: grenze(k) * 0.87 * k ** 2          # noqa: E731
        self.assertLessEqual(flaeche(0.013), 940 * 0.004 ** 2 * 1.05)
        self.assertGreaterEqual(flaeche(0.0005), 25 * 0.004 ** 2 * 0.95)


class _Folger:
    """Folgen(q) = 2,5 · q: der volle Schritt q ← q + (z − 2,5 q) schwingt auseinander (Faktor −1,5), der halbe (Faktor 0,25) kommt an."""

    def __init__(self):
        self.punkte = None
        self._projektion = None

    def punkte_zu(self, formung):
        return 2.5 * self.punkte


class FixpunktTest(unittest.TestCase):
    def test_4_halber_schritt_kommt_an(self):
        folger, formung = _Folger(), SimpleNamespace(boden=lambda: 0.0)
        ziel = np.random.default_rng(1).uniform(-0.1, 0.1, (50, 3))
        q = ziel.copy()
        for _ in range(G9gcfigurbau.DURCHGAENGE):                # der volle Schritt: schwingt
            q = q + (ziel - G9gcfigurbau.folgen(folger, formung, q))
        voll = np.linalg.norm(ziel - G9gcfigurbau.folgen(folger, formung, q), axis=1).max()
        self.assertGreater(voll, 0.01, 'der volle Schritt kommt hier nicht an')
        neu, rest, gedaempft = G9gcfigurbau._daempfen(folger, formung, ziel, q)
        self.assertTrue(gedaempft)
        self.assertLess(rest.max(), G9gcfigurbau.GENUG_M)
        np.testing.assert_allclose(neu, ziel / 2.5, atol=1e-4)

    def test_4b_nie_schlechter_als_die_erste_phase(self):
        folger, formung = _Folger(), SimpleNamespace(boden=lambda: 0.0)
        ziel = np.full((5, 3), 0.1)
        q = ziel / 2.5                                          # schon am Ziel
        neu, rest, gedaempft = G9gcfigurbau._daempfen(folger, formung, ziel, q)
        self.assertFalse(gedaempft, 'nichts zu verbessern: die erste Phase bleibt')
        np.testing.assert_allclose(neu, q)


class RequisitTest(unittest.TestCase):
    """Zwei Käfigteile als Punktwolken: Rumpf (Kasten bei x = 0) und rechte Hand (Kasten bei x = 0,3; in der Haltung um 90° um z gedreht
    und verschoben, bei y = 0,3 neben dem Rumpf-Ende)."""

    R = np.array([[0.0, -1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    T = np.array([0.02, 0.0, 0.0])

    def _lage(self):
        zufall = np.random.default_rng(3)
        rumpf = zufall.uniform([-0.01, 0.0, 0.0], [0.01, 0.2, 0.2], (300, 3))
        hand_ruhe = zufall.uniform([0.3, 0.0, 0.0], [0.34, 0.1, 0.05], (150, 3))
        hand_posiert = hand_ruhe @ self.R.T + self.T
        posiert, ruhe = np.vstack([rumpf, hand_posiert]), np.vstack([rumpf, hand_ruhe])
        teil = np.array([G9koerperteile.NUMMER['rumpf']] * 300 + [G9koerperteile.NUMMER['r_hand']] * 150)
        baum = cKDTree(posiert)
        return SimpleNamespace(h=0.004, teil=teil, kaefig_posiert=posiert, kaefig_ruhe=ruhe, ins_netz=lambda p: np.asarray(p, dtype=np.float64),
                               entposen=lambda: SimpleNamespace(baum=baum)), hand_posiert, hand_ruhe

    def test_5_requisit_geht_starr_mit_dem_teil_das_es_beruehrt(self):
        lage, hand_posiert, hand_ruhe = self._lage()
        n = 200
        waffe = np.column_stack([np.full(n, 0.1), np.linspace(0.0, 0.2, n), np.linspace(0.0, 0.2, n)])   # 10 cm vor dem Rumpf: frei, im Mittel näher am Rumpf
        versatz = np.array([0.004, 0.004, 0.0])
        waffe[:12] = hand_posiert[:12] + versatz                                                         # der Griff liegt auf der Hand
        req = Blendimportrequisit(lage)
        e = req.erkennen(waffe)
        self.assertIsNotNone(e)
        self.assertEqual(e['teil'], 'r_hand', 'die Berührung zählt, nicht der Mittelwert')
        self.assertEqual(e['knochen'], 'r_hand')
        ruhe, rundlauf = req.ruhelage(waffe, e['nummer'])
        self.assertLess(rundlauf, 0.01, 'die Käfigpunkte des Teils bewegen sich starr')
        np.testing.assert_allclose(ruhe[:12], hand_ruhe[:12] + self.R.T @ versatz, atol=1e-6)         # Griff am Ort der Hand in Ruhe

    def test_5b_stoff_am_koerper_bleibt_stoff(self):
        lage, _, _ = self._lage()
        stoff = np.column_stack([np.full(100, 0.022), np.linspace(0.0, 0.2, 100), np.linspace(0.0, 0.2, 100)])   # 12 mm vor dem Rumpf
        self.assertIsNone(Blendimportrequisit(lage).erkennen(stoff))


class SohleWaagrechtTest(unittest.TestCase):
    """`Blendimportfuss.waagrecht`: Zusatzdrehung (Grad, + = Spitze unten), bei der die Sohle waagrecht liegt."""

    @staticmethod
    def _dreh(grad):
        c, s = np.cos(np.radians(grad)), np.sin(np.radians(grad))
        return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])

    @staticmethod
    def _fuss(h=0.004):
        """Ein Fuß-Gerüst ohne Lage — nur `lage.h` (Käfigeinheit), wie es `waagrecht` und `nachstellen` brauchen."""
        f = Blendimportfuss.__new__(Blendimportfuss)
        f.lage, f.schuhe, f._seiten = SimpleNamespace(h=h), None, None
        return f

    @staticmethod
    def _schuh(sohle_y):
        """Schuh im Achsensystem des flachen Fußes (Spitze +z): Sohle `sohle_y(z)`, drei Breiten, Oberseite 3 cm darüber."""
        z = np.linspace(-0.1, 0.1, 60)
        return np.array([[x, sohle_y(z)[i] + dicke, zz] for i, zz in enumerate(z) for x in (-0.03, 0.0, 0.03) for dicke in (0.0, 0.03)])

    def _zusatz(self, schuh_fuss, fuss_grad):
        """Der Schuh am Fuß, der `fuss_grad` gegen den Unterschenkel gedreht ist: was verlangt `waagrecht`?"""
        q = self._dreh(fuss_grad)
        return self._fuss().waagrecht(schuh_fuss @ q.T)

    def test_6_keilschuh_bekommt_den_fusswinkel_seines_keils(self):
        keil = np.degrees(np.arctan(0.08 / 0.2))                   # Sohle steigt von der Ferse (−8 cm) zur Spitze (0) auf 20 cm
        schuh = self._schuh(lambda z: -0.08 + (z + 0.1) * 0.4)
        zusatz = self._zusatz(schuh, 50.0)
        self.assertAlmostEqual(50.0 + zusatz, keil, delta=0.6, msg='Fuß im Schuh steht danach im Keilwinkel, die Sohle ist waagrecht')

    def test_6b_flache_sohle_stellt_den_fuss_flach(self):
        schuh = self._schuh(lambda z: np.zeros_like(z))
        self.assertAlmostEqual(self._zusatz(schuh, 40.0), -40.0, delta=0.6)
        self.assertAlmostEqual(self._zusatz(schuh, 0.0), 0.0, delta=0.6, msg='ein Schuh, der schon flach steht, bleibt es')

    def _fuss_mit_ruhe(self, fuss_grad):
        """Ein Fuß-Gerüst ohne Lage: Seite `l`, Fuß `fuss_grad` gegen den Unterschenkel, der Schuh (Keil 21,8°) so, wie er dort sitzt."""
        f = self._fuss()
        schuh = self._schuh(lambda z: -0.08 + (z + 0.1) * 0.4)
        q = self._dreh(fuss_grad)
        ruhe = schuh @ q.T
        f._seiten = [{'seite': 'l', 'q': q, 'winkel': fuss_grad, 'waagrecht_grad': 0.0, 'punkte': ruhe}]
        return f, schuh

    def test_6c_nachstellen_misst_die_sohle_am_ergebnis(self):
        """Der Käfig-Kabsch stellt die Sohle nicht wie die starre Rechnung: am Ergebnis messen und `Q` nachstellen (Edgar: „immer noch nicht horizontal")."""
        keil = np.degrees(np.arctan(0.08 / 0.2))
        f, schuh = self._fuss_mit_ruhe(keil + 6.0)                    # die Sohle steht noch 6° geneigt
        self.assertTrue(f.nachstellen(schuh @ f._seiten[0]['q'].T, schuh @ f._seiten[0]['q'].T))
        self.assertAlmostEqual(f._seiten[0]['winkel'], keil, delta=0.6)
        self.assertAlmostEqual(f._seiten[0]['waagrecht_grad'], -6.0, delta=0.6)
        neu = schuh @ f._seiten[0]['q'].T
        self.assertFalse(f.nachstellen(neu, neu), 'danach steht sie waagrecht: nichts mehr zu tun')

    def test_6d_unter_der_toleranz_bleibt_es(self):
        keil = np.degrees(np.arctan(0.08 / 0.2))
        f, schuh = self._fuss_mit_ruhe(keil + 0.5)
        ruhe = schuh @ f._seiten[0]['q'].T
        self.assertFalse(f.nachstellen(ruhe, ruhe))
        self.assertEqual(f._seiten[0]['waagrecht_grad'], 0.0)


class SohleAusDerFormTest(unittest.TestCase):
    """`Blendimportsohle.neigung`: die Sohle aus der Form des Schuhs, im Rahmen des Unterschenkels (Länge z, Höhe y) — ohne Fußachse des Körpers."""

    BAND = 0.004                       # 1 h

    @staticmethod
    def _dreh(grad):
        c, s = np.cos(np.radians(grad)), np.sin(np.radians(grad))
        return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]])

    @staticmethod
    def _stiefel(sohle, schaft=0.25, absatz=None):
        """Ein Stiefel, Spitze +z: Sohle `sohle(z)` (m) von z = −0,12 bis 0,14, darüber 4 cm Leder, hinten ein Schaft bis `schaft` Höhe (Rückwand bei z = −0,12 … −0,05).
        `absatz` (Höhe m): ein Block unter der Ferse, der die Sohle dort tiefer legt (Absatzschuh: Ferse und Ballen berühren, dazwischen Luft)."""
        z = np.arange(-0.12, 0.1401, 0.002)
        unten = np.array([sohle(v) for v in z])
        if absatz:
            unten = np.where(z < -0.07, -absatz, unten)
        punkte = [[x, y, v] for x in (-0.04, 0.0, 0.04) for v, u in zip(z, unten, strict=True) for y in (u, u + 0.04)]
        for v in np.arange(-0.12, -0.05, 0.004):                      # Schaftrückseite und -vorderseite
            for y in np.arange(0.0, schaft, 0.004):
                punkte += [[x, y, v] for x in (-0.04, 0.0, 0.04)]
        return np.array(punkte)

    @classmethod
    def _flach(cls, z):
        """Wie die Sohle des Fallout ranger gemessen: Ferse 3 mm, Mitte 0, Spitze bis 14 mm nach oben gebogen."""
        return 0.003 * np.clip(-z / 0.12, 0.0, 1.0) + 0.014 * (np.clip((z - 0.05) / 0.09, 0.0, 1.0)) ** 2

    def _neigung(self, schuh):
        return Blendimportsohle.neigung(schuh, self.BAND)

    def test_7_flacher_stiefel_bleibt_flach_auch_mit_hohem_schaft(self):
        """Der Fall, an dem die erste Fassung scheiterte: eine flache Sohle, ein hoher Schaft, kein Körperfuß — die Sohle muss ~0° bleiben (vorher −75°)."""
        w = self._neigung(self._stiefel(self._flach))
        self.assertIsNotNone(w)
        self.assertLess(abs(w), 2.0)

    def test_7b_derselbe_stiefel_auf_zehenspitzen_wird_gerade_gestellt(self):
        for grad in (20.0, 35.0, -15.0):
            schuh = self._stiefel(self._flach) @ self._dreh(grad).T
            w = self._neigung(schuh)
            self.assertIsNotNone(w, 'bei %.0f°' % grad)
            self.assertAlmostEqual(w, -grad, delta=2.5, msg='um %.0f° geneigte Sohle braucht die Gegendrehung' % grad)

    def test_7c_absatzschuh_steht_auf_ferse_und_spitze(self):
        """Ein Block von 8 cm unter der Ferse, die Vorderfüße flach: die Sohle ist die Linie Fersenunterkante → Spitze, sie steigt nach vorn (21°). Der Schuh wird um Spitze-nach-unten
        gedreht — der Fuß im Schuh bekommt den Winkel des Absatzes."""
        flach = self._neigung(self._stiefel(lambda z: 0.0))
        self.assertLess(abs(flach), 2.0)
        w = self._neigung(self._stiefel(lambda z: 0.0, absatz=0.08))
        self.assertIsNotNone(w)
        self.assertAlmostEqual(w, np.degrees(np.arctan(0.08 / 0.21)), delta=3.0)

    def test_7d_eine_kugel_hat_keine_sohle(self):
        zufall = np.random.default_rng(4)
        v = zufall.normal(size=(3000, 3))
        kugel = 0.05 * v / np.linalg.norm(v, axis=1, keepdims=True)
        self.assertIsNone(self._neigung(kugel), 'keine Kante der unteren Hülle deckt einen nennenswerten Teil der Länge ab')

    def test_7e_zu_wenige_oder_flache_punkte(self):
        self.assertIsNone(self._neigung(np.zeros((2, 3))))
        self.assertIsNone(self._neigung(np.column_stack([np.linspace(0, 1, 50), np.zeros(50), np.zeros(50)])), 'alle Punkte auf einer Geraden (Länge null in z): keine Hülle')

    def test_7f_zehn_prozent_der_punkte_treffen_auf_zwei_grad(self):
        """Wie an Asian Female und Fallout gemessen (`SCHUH_MINDEST`): zufällige 10 % behalten die Neigung auf wenige Grad."""
        schuh = self._stiefel(self._flach) @ self._dreh(30.0).T
        voll = self._neigung(schuh)
        zufall = np.random.default_rng(7)
        for _ in range(5):
            teil = schuh[zufall.random(len(schuh)) < 0.10]
            self.assertAlmostEqual(self._neigung(teil), voll, delta=3.0)

    def test_7g_die_fussachse_des_koerpers_spielt_keine_rolle(self):
        """`waagrecht` liest die Form, nicht `Q`: derselbe Schuh liefert dieselbe Antwort, gleich wie der Körperfuß steht."""
        f = SohleWaagrechtTest._fuss()
        schuh = self._stiefel(self._flach)
        self.assertAlmostEqual(f.waagrecht(schuh), f.waagrecht(schuh.copy()), places=9)
        import inspect
        self.assertEqual(list(inspect.signature(Blendimportfuss.waagrecht).parameters), ['self', 'schuh'])


class FussZuverlaessigkeitTest(unittest.TestCase):
    """Wo der Körper den Fuß nicht trägt (Fallout ranger: 333 Körperpunkte im Fußteil gegen 2.166 Käfigpunkte), ist der Fußwinkel keine Messung."""

    def _fuss(self, koerperpunkte, mit_schuhen=False):
        zufall = np.random.default_rng(2)
        n_fuss, n_bein = 400, 400
        fuss = zufall.uniform([-0.04, 0.0, -0.1], [0.04, 0.08, 0.15], (n_fuss, 3))
        bein = zufall.uniform([-0.05, 0.1, -0.05], [0.05, 0.45, 0.05], (n_bein, 3))
        punkte = np.vstack([fuss, bein])
        teil = np.array([G9koerperteile.NUMMER['l_fuss']] * n_fuss + [G9koerperteile.NUMMER['l_unterschenkel']] * n_bein)
        lage = SimpleNamespace(teil=teil, kaefig_ruhe=punkte, kaefig_posiert=punkte, h=0.004)
        koerper = fuss[zufall.integers(0, n_fuss, koerperpunkte)] + zufall.normal(scale=0.0005, size=(koerperpunkte, 3))
        schuhe = fuss + np.array([0.0, -0.01, 0.0]) if mit_schuhen else None
        return Blendimportfuss(lage, koerper, np.full(koerperpunkte, G9koerperteile.NUMMER['l_fuss']), schuhe)

    def test_8_getragener_fuss_ist_verlaesslich(self):
        f = self._fuss(600)                                                          # 1,5 Körperpunkte je Käfigpunkt (Asian Female 1,46)
        s = f.seiten()[0]
        self.assertTrue(s['verlaesslich'])
        self.assertAlmostEqual(s['deckung'], 1.5, places=2)
        self.assertEqual(f.hinweise(), [])

    def test_8b_fehlender_fuss_wird_gemeldet(self):
        f = self._fuss(60)                                                           # 0,15 (Fallout ranger)
        s = f.seiten()[0]
        self.assertFalse(s['verlaesslich'])
        hinweise = f.hinweise()
        self.assertEqual(len(hinweise), 1)
        self.assertIn('trägt ihn nicht', hinweise[0])
        self.assertIn('Linker', hinweise[0])
        self.assertEqual(f.bericht()['seiten'][0]['verlaesslich'], False)

    def test_8c_koerper_ohne_fuesse_mit_schuhen_hat_trotzdem_eine_seite(self):
        """Rainy, 10.10.2026: der Körper endet bei 0,911 m, kein Körperpunkt im Fußteil — bis dahin gab es keine Seite, keinen Griff und keine waagrechte Sohle;
        gemessen im Browser stand der Stiefel 62 mm unter dem Boden, die Sohle −62 … +7 mm. Mit Schuhen kommt der Fußwinkel aus dem Käfig (ohne Nachzug an
        Körperpunkten), die Sohle stellt `waagrecht`; `verlaesslich` bleibt falsch, der Hinweis erscheint.
        Sabotage: die Bedingung `elif self.schuhe is not None` in `Blendimportfuss.seiten` streichen → dieser Fall wird rot."""
        f = self._fuss(0, mit_schuhen=True)
        seiten = f.seiten()
        self.assertEqual(len(seiten), 1)
        self.assertEqual(seiten[0]['deckung'], 0.0)
        self.assertFalse(seiten[0]['verlaesslich'])
        self.assertEqual(len(f.hinweise()), 1)

    def test_8d_koerper_ohne_fuesse_ohne_schuhe_bleibt_ohne_seite(self):
        """Ohne Schuhe gibt es nichts, was sich flach stellen ließe — wie bisher keine Seite."""
        self.assertEqual(self._fuss(0).seiten(), [])


class KalibrierungTest(unittest.TestCase):
    """Die Schwellen der Abnahme an den Messwerten dreier Modelle (`stand.json` der Läufe 09.10.2026 und die Proben zu cute girl, in `blendimportpruefung.py` beschrieben):
    anliegende Stücke ohne Hinweis, hängende und der zerstörte Stiefel mit."""

    # (Stück, h mm, Median, p99, über 25 mm, Kanten außerhalb, größte Streckung, frei hängend, erwartet)
    MESSUNGEN = [
        ('Asian Female BH', 3.96, 2.9, 7.2, 0.0, 0.0005, 1.43, 0.069, set()),
        ('Asian Female Socke links', 3.96, 0.2, 10.7, 0.0, 0.0213, 1.64, 0.003, set()),
        ('Asian Female Socke rechts', 3.96, 0.2, 10.8, 0.0, 0.0219, 1.70, 0.004, set()),
        ('Asian Female Stiefel (Zehenspitzenfuß)', 3.96, 3.1, 6.2, 0.0, 0.0012, 1.64, 0.414, set()),
        ('Asian Female Stiefel (Sohle waagrecht)', 3.96, 4.6, 10.9, 0.0, 0.0177, 2.04, 0.414, set()),
        ('Asian Female Hemd', 3.96, 1.9, 40.9, 0.0241, 0.0602, 3.41, 0.54, {'kanten', 'haltung'}),
        ('Asian Female Shorts', 3.96, 2.3, 7.1, 0.0, 0.0003, 1.37, 0.148, set()),
        ('Asian Female Höschen mit Strapsen', 3.96, 2.0, 6.7, 0.0, 0.007, 1.70, 0.204, set()),
        ('Fallout Rüstung', 3.93, 0.8, 3.5, 0.0, 0.0001, 1.27, 0.346, set()),
        ('Fallout Mantel', 3.93, 1.3, 108.0, 0.0607, 0.0047, 2.07, 0.65, {'haltung'}),
        ('Fallout Hose', 3.93, 0.1, 1.8, 0.0, 0.0, 1.04, 0.021, set()),
        ('Fallout Augen als Stück', 3.93, 0.5, 1.0, 0.0, 0.0, 1.0, 1.0, set()),
        ('Fallout Helm', 3.93, 0.8, 3.0, 0.0, 0.0, 1.17, 0.984, set()),
        ('Fallout Jeans', 3.93, 0.3, 2.8, 0.0, 0.0001, 1.15, 0.116, set()),
        ('Fallout Seil', 3.93, 0.9, 4.5, 0.0, 0.0013, 1.23, 0.865, set()),
        ('Fallout Stiefel (zerstörte Sohle)', 3.93, 2.7, 28.4, 0.0162, 0.0788, 4.13, 0.88, {'kanten', 'haltung'}),
        ('cute girl Jeans', 4.25, 1.1, 17.0, 0.0, 0.0, 1.12, 0.09, set()),
        ('cute girl Pullover', 4.25, 1.2, 9.3, 0.0, 0.0012, 1.30, 0.60, set()),
    ]

    @staticmethod
    def _arten(warnungen):
        return {a for a, wort in (('kanten', 'Kantenverzerrung'), ('haltung', 'Haltungstreue'), ('frei', 'hängen frei')) if any(wort in w for w in warnungen)}

    def test_9_schwellen_trennen_die_gemessenen_stuecke(self):
        for name, h, median, p99, ueber, kanten, streckung, frei, erwartet in self.MESSUNGEN:
            aus = Blendimportpruefung.warnungen({'ausserhalb': kanten, 'streckung_max': streckung, 'streckung_min': 0.5}, {'frei_anteil': frei, 'h_mm': h},
                                                {'median_mm': median, 'p99_mm': p99, 'ueber_25': ueber})
            self.assertEqual(self._arten(aus), erwartet, '%s: %s' % (name, aus))

    def test_9b_die_schwelle_wandert_mit_der_kaefigeinheit(self):
        """Dieselbe Abweichung (20 mm) ist bei h = 3 mm ein Hinweis (> 6 h), bei h = 4 mm nicht (< 6 h = 24 mm)."""
        haltung = {'median_mm': 1.0, 'p99_mm': 20.0, 'ueber_25': 0.0}
        gut = {'ausserhalb': 0.0, 'streckung_max': 1.0, 'streckung_min': 1.0}
        self.assertEqual(self._arten(Blendimportpruefung.warnungen(gut, {'h_mm': 3.0}, haltung)), {'haltung'})
        self.assertEqual(self._arten(Blendimportpruefung.warnungen(gut, {'h_mm': 4.0}, haltung)), set())


class KopplungTest(unittest.TestCase):
    """`Blendimportlage.KOPPELN_E`: die Kopplung beim Entzerren höchstens drei Stückkanten — ein dichtes Netz koppelt sonst jeden Punkt mit dem ganzen Umkreis."""

    def _koppeln(self, kante):
        """Die Kopplungsweite (m), die `stueck_ruhelage` an `entzerren` übergibt, für ein Gitter mit dieser Kantenlänge."""
        punkte, dreiecke = _gitter(6, kante)
        n = len(punkte)
        gesehen = {}

        class Ent:
            baum = SimpleNamespace(query=lambda p: (np.zeros(len(p)), np.zeros(len(p), dtype=int)))

            @staticmethod
            def teile_von(netz, erlaubt, normalen, kaefig, abstand=False):
                return np.zeros(n, dtype=int), np.full(n, 0.01)

            @staticmethod
            def teile_inseln(teile, dreiecke, insel, abstand=None, ab=0.0):
                return teile

            @staticmethod
            def teile_glaetten(teile, dreiecke, gewicht=None, runden=0):
                return teile

            @staticmethod
            def ruhelage(netz, teile):
                return netz

            @staticmethod
            def entzerren(ruhe, netz, dreiecke, abstand, koppeln, anker, reichweite):
                gesehen['koppeln'] = koppeln
                return ruhe

        lage = Blendimportlage.__new__(Blendimportlage)
        lage._h, lage._entposen = 0.004, Ent
        lage.ins_netz = lambda p: np.asarray(p, dtype=np.float64)
        lage.kaefig_normalen = lambda: np.tile([0.0, 0.0, 1.0], (n, 1))
        Blendimportlage.stueck_ruhelage(lage, punkte, dreiecke, None)
        return gesehen['koppeln']

    def test_10_dichtes_netz_koppelt_enger(self):
        self.assertAlmostEqual(self._koppeln(0.010), 0.004, places=9, msg='Kante 10 mm: wie bisher 1 h = 4 mm')
        self.assertAlmostEqual(self._koppeln(0.0005), 0.0015, places=9, msg='Kante 0,5 mm (BH): 3 Kanten = 1,5 mm statt 4 mm')

    def test_10b_grenze_ist_eine_konstante_der_lage(self):
        self.assertEqual(Blendimportlage.KOPPELN_E, 3.0)


if __name__ == '__main__':
    unittest.main()

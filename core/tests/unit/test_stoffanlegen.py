# -*- coding: utf-8 -*-
"""`Stoffanlegen`: Stoff auf festen Hautabstand ziehen — in beide Richtungen.

Kunstkoerper: eine Kugel (Radius 10 cm, geschlossen, nach aussen gewickelt).
Stoff: ein Ring von Punkten darum, teils 5 cm entfernt, teils IN der Kugel.
Nach dem Anlegen muss jeder Punkt `abstand_mm` vor der Oberflaeche liegen —
der abstehende herangezogen, der eingesunkene herausgeholt. Ein offener
Rand darf dabei nicht wandern (Saum), und was weit weg haengt (> UMKREIS),
bleibt, wo es ist.

Sabotage-Gegenprobe: `soll - tiefe` -> `soll + tiefe` in `_anlegen` macht
`test_abstehender_stoff_kommt_heran` rot; Rand mit den inneren Nachbarn
geglaettet (`innen` weg) macht `test_offener_rand_wandert_nicht` rot;
`_seiten_setzen` ohne Baeume macht `test_unter_dem_schritt_zaehlt_nur_das_eigene_bein` rot.
"""

import numpy as np
from django.test import SimpleTestCase
from GarmentCode.stoffanlegen import Stoffanlegen


class StoffanlegenTest(SimpleTestCase):
    databases = set()

    def _abstand(self, punkte, radius=0.10):
        return np.linalg.norm(punkte, axis=1) - radius

    def test_abstehender_stoff_kommt_heran(self):
        kv, kf = StoffanlegenTest._kugel()
        stoff, dreiecke = StoffanlegenTest._streifen([(0.15, -0.02), (0.15, 0.0), (0.15, 0.02)])
        neu, bilanz = Stoffanlegen.aus_netz(kv, kf, dreiecke).anlegen(stoff, 3.0)
        abstand = self._abstand(neu) * 1000
        self.assertLess(np.abs(abstand - 3.0).max(), 0.6, abstand)
        self.assertEqual(bilanz['angelegt'], len(stoff))
        self.assertGreater(bilanz['median_weg_mm'], 40)

    def test_eingesunkener_stoff_kommt_heraus(self):
        kv, kf = StoffanlegenTest._kugel()
        stoff, dreiecke = StoffanlegenTest._streifen([(0.09, -0.02), (0.09, 0.0), (0.09, 0.02)])
        neu, _ = Stoffanlegen.aus_netz(kv, kf, dreiecke).anlegen(stoff, 2.0)
        abstand = self._abstand(neu) * 1000
        self.assertGreater(abstand.min(), 1.4)
        self.assertLess(np.abs(abstand - 2.0).max(), 0.6)

    def test_weit_entfernter_stoff_bleibt(self):
        kv, kf = StoffanlegenTest._kugel()
        stoff, dreiecke = StoffanlegenTest._streifen([(0.40, -0.02), (0.40, 0.0), (0.40, 0.02)])
        neu, bilanz = Stoffanlegen.aus_netz(kv, kf, dreiecke).anlegen(stoff, 2.0)
        np.testing.assert_allclose(neu, stoff)
        self.assertEqual(bilanz['angelegt'], 0)

    def test_offener_rand_wandert_nicht(self):
        """Der Saum liegt an, bleibt aber auf seiner Hoehe."""
        kv, kf = StoffanlegenTest._kugel()
        stoff, dreiecke = StoffanlegenTest._streifen(
            [(0.14, -0.03), (0.14, -0.01), (0.14, 0.01), (0.14, 0.03)]
        )
        neu, _ = Stoffanlegen.aus_netz(kv, kf, dreiecke).anlegen(stoff, 2.0)
        rand = np.arange(48)  # unterster Ring
        # Tangentiale Lage: Winkel um die z-Achse bis auf die Schraege der
        # Eckpunktnormale (Ikosaeder, gemessen 1 Grad) unveraendert …
        alt = np.arctan2(stoff[rand, 1], stoff[rand, 0])
        jetzt = np.arctan2(neu[rand, 1], neu[rand, 0])
        self.assertLess(np.abs(np.angle(np.exp(1j * (jetzt - alt)))).max(), 0.03)
        # … und die Hoehe bleibt bis auf den Weg entlang der Normale: 3 cm
        # unter dem Aequator zeigt sie 0,3 nach unten, 38 mm Weg machen
        # 11 mm in z (gemessen 9,8). Mit Glaettung am Rand waeren es 23,8.
        self.assertLess(np.abs(neu[rand, 2] - stoff[rand, 2]).max(), 0.015)

    def test_unter_dem_schritt_zaehlt_nur_das_eigene_bein(self):
        """Zwei Beine, ungleich dick: Ein Stoffpunkt rechts der Mitte legt
        sich an das RECHTE Bein, auch wenn das linke naeher ist.

        Kunstkoerper: linkes Bein Radius 10 cm (Innenseite bei x = -2 cm),
        rechtes Bein Radius 6 cm (Innenseite bei x = +6 cm), Rumpf darueber
        mit dem Schritt bei z 0,80. Ein Stoffpunkt bei x = +1 cm ist dem
        linken Bein 3 cm nah, dem rechten 5 cm — am linken angelegt
        spannte sich ein Steg zwischen den Beinen (der Befund vom
        11.09.2026). Ohne die Seitenregel landet er bei x < 0.
        """
        import trimesh

        teile = []
        # trimesh-Zylinder haben nur an den Deckeln Punkte; das Anlegen
        # sucht Koerperpunkte, also Mantel unterteilen (Kanten <= 3 cm).
        for x0, radius in ((-0.12, 0.10), (0.12, 0.06)):
            bein = trimesh.creation.cylinder(radius=radius, height=0.80, sections=48)
            bein.apply_translation([x0, 0.0, 0.40])
            teile.append(bein.subdivide_to_size(0.03))
        rumpf = trimesh.creation.cylinder(radius=0.22, height=0.80, sections=48)
        rumpf.apply_translation([0.0, 0.0, 1.20])
        teile.append(rumpf.subdivide_to_size(0.03))
        koerper = trimesh.util.concatenate(teile)
        kv, kf = np.asarray(koerper.vertices), np.asarray(koerper.faces)
        stoff = np.array(
            [[0.01, 0.0, 0.40], [0.02, 0.0, 0.40], [0.0, 0.0, 0.40], [0.01, 0.01, 0.40], [0.01, -0.01, 0.40]]
        )
        dreiecke = np.array([[0, 1, 3], [0, 3, 2], [0, 2, 4], [0, 4, 1]])
        anleger = Stoffanlegen.aus_netz(kv, kf, dreiecke)
        self.assertIsNotNone(anleger, 'Kunstkoerper ohne Schritt')
        neu, _ = anleger.anlegen(stoff, 2.0)
        self.assertGreater(neu[0, 0], 0.04, neu[0])
        self.assertAlmostEqual(neu[0, 0], 0.058, delta=0.004)
        # Gegenprobe: ohne Seiten liegt der naechste Punkt am linken Bein.
        _, index = anleger.baum.query(stoff[0])
        self.assertLess(kv[index][0], 0.0, 'die Gegenprobe traegt nicht: naechster Punkt rechts')

    def test_hose_wird_hochgezogen_und_saum_kommt_auf_den_knoechel(self):
        """Am Kunstkoerper aus `test_stoffhochziehen`: Der Hosenschritt
        landet am Koerperschritt, der Saum nicht unter der Ferse."""
        import trimesh
        from GarmentCode.stoffhochziehen import Stoffhochziehen

        from .test_stoffhochziehen import _hose, _koerper

        kv = _koerper()
        # Ein Netz aus der Punktwolke: konvexe Huelle je Teil reicht fuer
        # Normalen, die nach aussen zeigen.
        teile = [
            trimesh.PointCloud(kv[kv[:, 0] < -0.02]).convex_hull,
            trimesh.PointCloud(kv[kv[:, 0] > 0.02]).convex_hull,
            trimesh.PointCloud(kv[kv[:, 2] >= 0.80]).convex_hull,
        ]
        netz = trimesh.util.concatenate(teile)
        hose = _hose()
        hoch = Stoffhochziehen(np.asarray(netz.vertices))
        self.assertIsNotNone(hoch.schritt)
        neu, bilanz = hoch.anwenden(hose)
        self.assertGreater(bilanz['hochgezogen_mm'], 100)
        self.assertGreater(bilanz['saum_gehoben_mm'], 50)
        self.assertGreater(neu[:, 2].min(), 0.03)

    def test_die_schlussrunde_hebt_nur_heraus(self):
        """`nur_heraus` (24.09.2026): Die Schlussrunden nach der Glaettung ziehen
        nichts mehr heran — ein volles Anlegen dort klappte im Schritt der Harem
        Pants 21 Dreiecke wieder um. Abstehendes bleibt, Eingesunkenes kommt heraus.
        Sabotage: `np.maximum(weg, 0.0)` weglassen -> rot."""
        kv, kf = StoffanlegenTest._kugel()
        ab, dreiecke = StoffanlegenTest._streifen([(0.13, -0.01), (0.13, 0.01)])
        anleger = Stoffanlegen.aus_netz(kv, kf, dreiecke)
        neu, nah = anleger._anlegen(ab, 0.002, nur_heraus=True)
        self.assertTrue(nah.all())
        np.testing.assert_allclose(neu, ab)
        drin, _ = StoffanlegenTest._streifen([(0.09, -0.01), (0.09, 0.01)])
        neu, _ = anleger._anlegen(drin, 0.002, nur_heraus=True)
        self.assertGreater((self._abstand(neu) * 1000).min(), 1.4)

    def test_umgeklappte_falten_werden_zur_faltenzone(self):
        """`_faltengewicht` (24.09.2026, Harem Pants an den Knoecheln): Klappt das
        Anlegen ein Dreieck um, wo der Stoff vorher tief stand, gehoeren seine
        Punkte (Gewicht 1) und ihre Nachbarn zur Faltenzone; ohne Umklappen keine.
        Sabotage: die Pruefung `kipp` immer False -> rot."""
        kv, kf = StoffanlegenTest._kugel()
        stoff, dreiecke = StoffanlegenTest._streifen([(0.13, -0.01), (0.13, 0.01)])
        anleger = Stoffanlegen.aus_netz(kv, kf, dreiecke)
        kanten = anleger._nachbarschaft(len(stoff))
        flach = stoff * (0.102 / 0.13)
        self.assertIsNone(anleger._faltengewicht(stoff, flach, kanten))
        verdreht = flach.copy()
        verdreht[[0, 1]] = verdreht[[1, 0]]  # zwei Nachbarn im Ring vertauscht
        gewicht = anleger._faltengewicht(stoff, verdreht, kanten)
        self.assertEqual((gewicht[0], gewicht[1]), (1.0, 1.0))
        self.assertLess(gewicht[24], 0.5)  # gegenueber im Ring: weit weg
        soll = anleger._faltensoll(stoff, 0.002, gewicht)
        self.assertGreater(soll[0], 0.002)
        self.assertAlmostEqual(soll[24], 0.002, delta=0.002)

    def test_bilanz_nennt_den_hautabstand(self):
        kv, kf = StoffanlegenTest._kugel()
        stoff, dreiecke = StoffanlegenTest._streifen([(0.13, -0.01), (0.13, 0.01)])
        _, bilanz = Stoffanlegen.aus_netz(kv, kf, dreiecke).anlegen(stoff, 2.5)
        self.assertAlmostEqual(bilanz['haut_median_mm'], 2.5, delta=0.3)
        self.assertEqual(bilanz['abstand_mm'], 2.5)

    @staticmethod
    def _kugel(radius=0.10):
        import trimesh

        k = trimesh.creation.icosphere(subdivisions=4, radius=radius)
        return np.asarray(k.vertices), np.asarray(k.faces)

    @staticmethod
    def _ring(radius, hoehe=0.0, n=48):
        w = np.linspace(0, 2 * np.pi, n, endpoint=False)
        return np.column_stack([radius * np.cos(w), radius * np.sin(w), np.full(n, hoehe)])

    @staticmethod
    def _streifen(radien, n=48):
        """Ringe uebereinander als Dreiecksstreifen — mit offenem oberem und
        unterem Rand, wie ein Hosenbein."""
        punkte = np.vstack([StoffanlegenTest._ring(r, h) for r, h in radien])
        dreiecke = []
        for reihe in range(len(radien) - 1):
            a, b = reihe * n, (reihe + 1) * n
            for i in range(n):
                j = (i + 1) % n
                dreiecke.append([a + i, a + j, b + i])
                dreiecke.append([a + j, b + j, b + i])
        return punkte, np.asarray(dreiecke)

# -*- coding: utf-8 -*-
"""Haut-Kachel um das Scham-Stück mit Originalfarbe (Edgar, 09.10.2026: „auch die Textur und Farbe soll an die Figur / an den Rand
angepasst werden"): `Blendimportumfeld` an einer Kunstfläche, ohne Genesis, Blender und Datenbank.

Gemessen am Modell „cute girl" (Kachel 1002, Chrome `chrome_farbvergleich.js`): am Rand des Stücks (201, 145, 130), die Haut daneben
(233, 209, 195) — die Fehlstellen des Backens hatten die helle Ersatzfarbe von „Mesh to 3D" bekommen. Kunstwelt hier: die „Figur" ist
ein Quadrat von 20 cm bei z = 0 (UV = Ort/20 cm, Kachel 1002), das „Original" eine zweite Fläche mit einem Farbverlauf (R = 255·u), das
„Stück" ein Punkt in der Ecke (0, 0).

1. Eine Fehlstelle nahe am Stück (≤ `RADIUS_M`) bekommt die Farbe des Originals an dieser Stelle (R ≈ 255·u).
2. Weit weg (über `RADIUS_M + AUSLAUF_M`) bleibt die bisherige Füllung; dazwischen ist es eine Mischung. Texel OHNE Fehlstelle ändern sich nie.
3. Liegt die Fläche des Originals weiter als `ABSTAND_MAX_M` hinter der Figur (anderes Körperteil), bleibt die Füllung.
4. `texel` nimmt auch den Saum um eine Insel mit (Zugabe `RAND`), aber nicht mehr — dort lesen Filter und Mip-Stufen.
5. Ohne Dreieck nahe am Stück (Kachel ohne Treffer) bleibt alles, wie es ist.
6. Texel weit vom Original (anderes Körperteil) kosten keinen Weg zur Fläche; nahe Texel gehen durch die Flächensuche (`Hbdreiecksuche.uv`).
7. Die Flächensuche liefert dieselbe UV und denselben Abstand wie `trimesh.proximity.closest_point` (10.10.2026: sie ersetzt ihn; am Kugelnetz 5,8× schneller).

Sabotage-Gegenprobe: `RAND` = 0 → Fall 4 rot; `RADIUS_M` sehr groß → Fall 2 rot; `ABSTAND_MAX_M` sehr groß → Fall 3 rot; die Prüfung `gefunden`
streichen → Fall 3 rot; die Kachelwahl `f['kachel'] == kachel` streichen → Fall 5 rot; die Vorprüfung `nah_genug` streichen → Fall 6 rot;
`Hbdreiecksuche.K` auf 1 → Fall 7 kann kippen.

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""

from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.blendimportumfeld import Blendimportumfeld


class UmfeldTest(SimpleTestCase):
    databases = set()

    KACHEL = 1002
    GROESSE_M = 0.2
    PX = 80

    @classmethod
    def _flaeche(cls, z, von=0.0, bis=1.0, zellen=10, kachel=None):
        """Ein Quadrat der Seite `GROESSE_M·(bis − von)` bei Höhe `z`; UV = Ort / `GROESSE_M`. Punkte, Dreiecke, UV je Punkt."""
        achse = np.linspace(von, bis, zellen + 1) * cls.GROESSE_M
        punkte = np.array([[x, y, z] for x in achse for y in achse])
        uv = punkte[:, :2] / cls.GROESSE_M
        dreiecke = []
        for i in range(zellen):
            for j in range(zellen):
                a, b, c, d = i * (zellen + 1) + j, (i + 1) * (zellen + 1) + j, i * (zellen + 1) + j + 1, (i + 1) * (zellen + 1) + j + 1
                dreiecke += [[a, b, c], [b, d, c]]
        return punkte, np.array(dreiecke), uv

    def _umfeld(self, original_z=-0.003, von=0.0, bis=1.0, kachel=None, stueck=(0.0, 0.0, 0.0)):
        punkte, dreiecke, uv = self._flaeche(0.0, von, bis)
        figur = {'punkte': punkte, 'dreiecke': dreiecke, 'uv': uv,
                 'kachel': np.full(len(dreiecke), kachel if kachel is not None else self.KACHEL)}
        op, od, ouv = self._flaeche(original_z)
        bild = np.zeros((64, 64, 3), dtype=np.uint8)
        bild[..., 0] = np.round(np.linspace(0, 255, 64))[None, :]          # R wächst mit u
        bild[..., 1], bild[..., 2] = 90, 60
        original = {'punkte': op, 'dreiecke': od, 'uv_ecken': ouv[od]}
        return Blendimportumfeld(np.array([stueck]), figur, original, bild), figur

    def _kachel(self):
        return np.full((self.PX, self.PX, 3), 128, dtype=np.uint8), np.ones((self.PX, self.PX), dtype=bool)

    def _ort_von(self, zeile, spalte):
        """(x, y) in m des Texels (UV: v nach oben, Zeile 0 oben)."""
        return (spalte + 0.5) / self.PX * self.GROESSE_M, (1.0 - (zeile + 0.5) / self.PX) * self.GROESSE_M

    def test_1_eine_fehlstelle_nahe_am_stueck_bekommt_die_farbe_des_originals(self):
        umfeld, _ = self._umfeld()
        farbe, leer = self._kachel()
        # Das Stück sitzt bei (0, 0): unten links, also Zeile PX−1, Spalte 0.
        umfeld.fuellen(self.KACHEL, farbe, leer)
        zeile, spalte = self.PX - 6, 5                                          # ≈ (0,013 | 0,013) m vom Stück
        x, _ = self._ort_von(zeile, spalte)
        erwartet = 255.0 * x / self.GROESSE_M
        self.assertLess(abs(float(farbe[zeile, spalte, 0]) - erwartet), 8.0, farbe[zeile, spalte])
        self.assertEqual(int(farbe[zeile, spalte, 1]), 90)
        self.assertGreater(umfeld.bericht['gefuellt'], 100)

    def test_2_weit_weg_bleibt_die_fuellung_und_texel_ohne_fehlstelle_aendern_sich_nie(self):
        umfeld, _ = self._umfeld()
        farbe, leer = self._kachel()
        gueltig = (slice(self.PX - 12, self.PX - 4), slice(3, 12))             # nahe am Stück: ein gültiges Backergebnis
        leer[gueltig] = False
        farbe[gueltig] = (10, 20, 30)
        umfeld.fuellen(self.KACHEL, farbe, leer)
        self.assertTrue((farbe[gueltig] == (10, 20, 30)).all(), 'Treffer des Backens bleiben, wie sie sind')
        # Die Ecke gegenüber liegt 0,28 m vom Stück: weit über RADIUS_M + AUSLAUF_M (0,09 m).
        self.assertTrue((farbe[:6, -6:] == 128).all(), farbe[:6, -6:].reshape(-1, 3)[0])
        mitte = farbe[self.PX - 1 - 20, 20]                                      # etwa 0,07 m vom Stück: Mischung
        self.assertNotEqual(tuple(mitte), (128, 128, 128))
        self.assertGreater(int(mitte[0]), 70)                                   # zwischen Original (≈ 65) und Füllung (128)

    def test_3_ein_anderes_koerperteil_hinter_der_figur_zaehlt_nicht(self):
        umfeld, _ = self._umfeld(original_z=-0.08)                              # 80 mm dahinter: weit über ABSTAND_MAX_M
        farbe, leer = self._kachel()
        umfeld.fuellen(self.KACHEL, farbe, leer)
        self.assertTrue((farbe == 128).all())
        self.assertEqual(umfeld.bericht['gefuellt'], 0)

    def test_4_texel_nimmt_den_saum_um_die_insel_mit_aber_nicht_mehr(self):
        umfeld, figur = self._umfeld(von=0.25, bis=0.75)
        farbe, leer = self._kachel()
        zeile, spalte, eigner, lam = umfeld.texel(np.arange(len(figur['dreiecke'])), leer)
        # Die Insel liegt zwischen u 0,25 … 0,75 = Spalten 20 … 59.
        self.assertTrue(((spalte == 19) | (spalte == 60)).any(), 'ein Texel Saum um die Insel gehört dazu')
        self.assertFalse(((spalte <= 16) | (spalte >= 63)).any(), 'weiter weg nicht')
        self.assertGreater(len(zeile), 40 * 40)
        self.assertTrue(np.allclose(lam.sum(axis=1), 1.0))

    def test_6_weit_entfernte_texel_kosten_keinen_weg_zur_flaeche(self):
        """Fallout ranger, Kachel 1003: 2,29 Mio. Texel im Umfeld, 1,32 Mio. davon ohne Original in Reichweite — der Weg zur Fläche für
        alle kostete Minuten im Import. Der nächste Eckpunkt entscheidet vorab."""
        from core.dienste.hbdreiecksuche import Hbdreiecksuche

        for abstand_z, erwartet_aufrufe in ((-0.08, 0), (-0.003, 1)):
            umfeld, _ = self._umfeld(original_z=abstand_z)
            farbe, leer = self._kachel()
            with mock.patch.object(Hbdreiecksuche, 'uv', autospec=True, side_effect=Hbdreiecksuche.uv) as weg:
                umfeld.fuellen(self.KACHEL, farbe, leer)
            self.assertEqual(int(weg.call_count > 0), erwartet_aufrufe, 'Abstand %s' % abstand_z)

    def test_7_die_flaechensuche_liefert_dieselbe_uv_und_denselben_abstand_wie_trimesh(self):
        """Rosemary (10.10.2026), Kachel 1001: `trimesh.proximity.closest_point` brauchte je 200.000 Texel 2–3 Minuten; `Hbdreiecksuche`
        rechnet dasselbe schneller. Gleiche Zahlen an einer verwackelten Kugel, Punkte 0–30 mm von der Fläche (gemessen mit 6.000 Punkten,
        Unterteilung 5: größte Abstandsabweichung 0,001 mm, UV 3e-5; 0,259 gegen 0,045 ms je Punkt; mit den Werten dieses Tests 0,0004 mm / 1,7e-4)."""
        import trimesh

        from core.dienste.hbdreiecksuche import Hbdreiecksuche

        rng = np.random.default_rng(3)
        kugel = trimesh.creation.icosphere(subdivisions=4, radius=0.9)
        punkte = kugel.vertices + rng.normal(scale=0.002, size=kugel.vertices.shape)
        ecken = kugel.faces
        v = punkte[ecken]
        uv_ecken = np.stack([np.arctan2(v[..., 1], v[..., 0]) / (2 * np.pi) + 0.5, np.arcsin(np.clip(v[..., 2] / 0.9, -1, 1)) / np.pi + 0.5], axis=-1)
        r = rng.normal(size=(500, 3))
        orte = r / np.linalg.norm(r, axis=1, keepdims=True) * (0.9 + rng.uniform(-0.03, 0.03, size=(500, 1)))
        flaeche = trimesh.Trimesh(punkte, ecken, process=False)
        nah, abstand_alt, dreieck = trimesh.proximity.closest_point(flaeche, orte)
        schwer = trimesh.triangles.points_to_barycentric(flaeche.triangles[dreieck], nah)
        uv_alt = (uv_ecken[dreieck] * schwer[..., None]).sum(axis=1)
        uv_neu, abstand_neu = Hbdreiecksuche(punkte, ecken, uv_ecken).uv(orte)
        self.assertLess(float(np.abs(abstand_neu - abstand_alt).max()), 5e-5)           # 0,05 mm
        self.assertLess(float(np.abs(uv_neu - uv_alt).max()), 1e-3)

    def test_5_eine_kachel_ohne_dreieck_im_umfeld_aendert_nichts(self):
        umfeld, _ = self._umfeld(kachel=1001)
        farbe, leer = self._kachel()
        umfeld.fuellen(self.KACHEL, farbe, leer)
        self.assertTrue((farbe == 128).all())
        self.assertEqual(umfeld.bericht['dreiecke'], 0)

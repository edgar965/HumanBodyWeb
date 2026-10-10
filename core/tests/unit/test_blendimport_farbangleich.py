# -*- coding: utf-8 -*-
"""Ersatzfüllung einer Haut-Kachel im Ton der gebackenen Nachbarschaft (Edgar, 10.10.2026: „texturfehler bei der Hand bei Modell asian"):
`Blendimportfarbangleich` an Kunstbildern, ohne Genesis, Blender und Datenbank.

Gemessen an Asian, Kachel 1004 (Daumenwurzel): Die Ersatzkachel von „Mesh to 3D" (2048²) stand grünlich-beige zwischen rosa Streifen des
Originals, und ein Loch von 4 weißen Pixeln mit hellem Hof (237–250 in Haut von 115–135) blieb als weißes Loch im Daumen.

1. `stopfen` füllt ein kleines weißes Loch samt seinem hellen Hof mit dem Hautton daneben; der große weiße Hintergrund bleibt weiß.
2. Eine Kerbe, die nur DIAGONAL am Hintergrund hängt, gehört zum Hintergrund (Achter-Nachbarschaft) und wird nicht gefüllt.
3. `hinten` bringt die Ersatzfarbe in den Ton des Gebackenen daneben (Versatz = Gebackenes − Ersatz).
4. Wo ringsum nichts Gebackenes liegt, bleibt es bei der Ersatzfarbe.
5. Nur Fehlstellen ändern sich: die Pixel außerhalb sind die der (hochgerechneten) Ersatzkachel; weißer Hintergrund bleibt weiß.

Sabotage-Gegenprobe: den Hof weglassen (`HOF_PX` = 0, `HELL` über 255) → Fall 1 rot; die Achter-Nachbarschaft (`structure=np.ones((3, 3))`)
streichen → Fall 2 rot; den Versatz auf 0 setzen → Fall 3 rot; `~(weiss & ~tasche)` streichen (der Hintergrund bekäme Hautton) → Fall 1 rot.
Fall 4 und 5 haben keine eigene Sabotage geprüft.

Trockenlauf ohne Django (10.10.2026, `ProjektTemp/_wegwerf/import_serie/farbangleich_trockenlauf.py`, Stubs für `core` und `django.test`): alle fünf
Fälle grün, jede der vier Sabotagen macht genau den genannten Fall rot. Nicht über `manage.py test` gelaufen — das läuft nur auf Ansage.
"""

import numpy as np
from django.test import SimpleTestCase
from PIL import Image

from core.dienste.blendimportfarbangleich import Blendimportfarbangleich


class FarbangleichTest(SimpleTestCase):
    databases = set()

    HAUT = (120, 100, 90)

    def _ersatz(self, groesse=40):
        bild = np.empty((groesse, groesse, 3), dtype=np.uint8)
        bild[:] = self.HAUT
        bild[:, :10] = 255                                              # der große weiße Hintergrund (400 Pixel, über TASCHE_MAX)
        return bild

    def test_1_ein_kleines_loch_samt_hof_wird_mit_hautton_gefuellt_der_hintergrund_bleibt(self):
        bild = self._ersatz()
        bild[16:23, 11:18] = 240                                        # der Hof
        bild[18:21, 13:16] = 255                                        # das Loch (9 Pixel), 4 Pixel vom Hintergrund (Spalten 0–9)
        neu = Blendimportfarbangleich.stopfen(bild)
        self.assertEqual(tuple(neu[19, 14]), self.HAUT)
        self.assertEqual(tuple(neu[16, 11]), self.HAUT, 'der Hof geht mit')
        self.assertTrue((neu[:, :10] == 255).all(), 'der Hintergrund bleibt, auch in Reichweite des Hofs')
        self.assertEqual(tuple(neu[30, 30]), self.HAUT)
        self.assertTrue((bild[18:21, 13:16] == 255).all(), 'die Eingabe bleibt unverändert')

    def test_2_eine_kerbe_die_nur_diagonal_am_hintergrund_haengt_ist_kein_loch(self):
        bild = np.empty((40, 40, 3), dtype=np.uint8)
        bild[:] = self.HAUT
        bild[:20, :10] = 255                                            # Hintergrund, oben bis Spalte 9 …
        bild[20:, :9] = 255                                             # … unten bis Spalte 8
        bild[20, 10] = 255                                              # nur über die Diagonale (19, 9) verbunden
        neu = Blendimportfarbangleich.stopfen(bild)
        self.assertEqual(tuple(neu[20, 10]), (255, 255, 255))

    def test_3_die_ersatzfarbe_wandert_in_den_ton_des_gebackenen(self):
        ersatz = Image.fromarray(np.full((16, 16, 3), (200, 150, 140), dtype=np.uint8))
        farbe = np.full((64, 64, 3), (180, 120, 110), dtype=np.uint8)
        fehlstelle = np.zeros((64, 64), dtype=bool)
        fehlstelle[24:40, 24:40] = True
        farbe[fehlstelle] = 0
        hinten = Blendimportfarbangleich.hinten(ersatz, farbe, fehlstelle)
        mitte = hinten[28:36, 28:36].reshape(-1, 3).astype(int)
        self.assertLessEqual(int(np.abs(mitte - (180, 120, 110)).max()), 3, mitte[0])

    def test_4_ohne_gebackene_nachbarschaft_bleibt_die_ersatzfarbe(self):
        ersatz = Image.fromarray(np.full((16, 16, 3), (200, 150, 140), dtype=np.uint8))
        farbe = np.zeros((64, 64, 3), dtype=np.uint8)
        hinten = Blendimportfarbangleich.hinten(ersatz, farbe, np.ones((64, 64), dtype=bool))
        self.assertEqual(tuple(hinten[32, 32]), (200, 150, 140))

    def test_5_nur_fehlstellen_aendern_sich_und_der_weisse_hintergrund_bleibt_weiss(self):
        grob = np.full((32, 32, 3), (200, 150, 140), dtype=np.uint8)
        grob[:, :8] = 255                                               # 256 Pixel: über TASCHE_MAX, also Hintergrund und kein Loch
        farbe = np.full((128, 128, 3), (180, 120, 110), dtype=np.uint8)
        fehlstelle = np.zeros((128, 128), dtype=bool)
        fehlstelle[:, :64] = True                                       # links alles Fehlstelle, auch der weiße Hintergrund
        farbe[fehlstelle] = 0
        hinten = Blendimportfarbangleich.hinten(Image.fromarray(grob), farbe, fehlstelle)
        # Nicht auf 255 prüfen: die Hochrechnung der Ersatzkachel lässt am Rand des Weißes 251 stehen (gemessen).
        self.assertGreaterEqual(int(hinten[:, :28].min()), Blendimportfarbangleich.WEISS, 'der weiße Hintergrund bleibt weiß')
        reine_ersatzfarbe = np.asarray(Image.fromarray(grob).resize((128, 128), Image.LANCZOS))
        self.assertTrue((hinten[:, 80:] == reine_ersatzfarbe[:, 80:]).all(), 'außerhalb der Fehlstellen gilt die Ersatzkachel unverändert')

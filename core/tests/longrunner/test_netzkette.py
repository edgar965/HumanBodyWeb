# -*- coding: utf-8 -*-
"""Longrunner: die ganze Netz-Kette einmal durch, mit den echten Daten.

WARUM EIGENE ART: Dieser Test lädt die Produktivdaten beider Geschlechter
(Netz, Gewichte, Morphs), baut den Catmull-Clark-Unterteiler und reicht die
Skin-Gewichte durch die Unterteilung. Das braucht Sekunden bis Minuten und
belegt hunderte Megabyte — in `unit` gehört es nicht hin, sonst fährt niemand
mehr die schnellen Tests bei jeder Änderung.

WAS ER FESTHÄLT — die Zahlen, an denen zwei Fehler schon gehangen haben:

* **18.210 bzw. 17.996 Basisvertices.** Die männlichen `.npy`-Dateien wurden
  einmal von 437 KB auf 218 KB halbiert (Vertexzahl halbiert) und haben den
  männlichen Charakter zerstört. Der Test rechnet beide Zahlen nach — und zwar
  GETRENNT: Die beiden Netze sind nicht topologiegleich.
* **70.851 bzw. 69.995 Untervertices.** Blenders ausgewertetes Netz (nach
  SubSurf) hat eine ANDERE Vertex-Reihenfolge als dieser Unterteiler. Deshalb
  werden die Basisgewichte exportiert und durchgereicht, nicht die fertigen.
* **Vier Einflüsse je Vertex.** Bei Rest-Pose sind alle Knochenmatrizen die
  Einheitsmatrix — ein falsch zugeordnetes Gewicht fällt dort NICHT auf. Der
  Test prüft daher die Struktur, nicht das Bild.

LESEN, NICHT SCHREIBEN: Der Test fasst `HumanBody/data/` nur lesend an.
"""

import json
import time

from django.test import SimpleTestCase

from core.dienste.charakterdaten import Charakterdaten


class NetzketteTest(SimpleTestCase):
    """Netz laden, unterteilen, Gewichte durchreichen — für beide Geschlechter."""

    #: Geschlecht -> (Vierecke, Basisvertices, Untervertices, Dreiecke).
    #: **Die beiden Netze sind NICHT topologiegleich** — das war die erste
    #: Annahme dieses Tests und sie war falsch (gemessen am 17.08.2026, weiblich
    #: 17.288 Vierecke, männlich 17.074). Wer hier eine Zahl für beide einträgt,
    #: baut sich einen Test, der bei einem echten Datenschaden grün bleibt.
    NETZE = {
        'female': (17288, 18210, 70851, 138304),
        'male': (17074, 17996, 69995, 136592),
    }
    #: Obergrenze für den ganzen Durchlauf. Großzügig — es ist ein Longrunner;
    #: die Grenze fängt nur ein Verhalten ab, das aus dem Ruder läuft.
    GRENZE_S = 300

    def test_beide_geschlechter_laufen_durch(self):
        start = time.time()
        for geschlecht in self.NETZE:
            with self.subTest(geschlecht=geschlecht):
                self._eines(geschlecht)
        self.assertLess(time.time() - start, self.GRENZE_S)

    def _eines(self, geschlecht):
        vierecke, basis, unter, dreiecke = self.NETZE[geschlecht]
        netz = Charakterdaten.netzdaten(geschlecht)
        self.assertIsNotNone(netz.faces, 'faces fehlen — Daten unvollständig')
        self.assertEqual(netz.faces.shape, (vierecke, 4),
                         'Der Unterteiler braucht Vierecke, keine Dreiecke')
        self.assertEqual(int(netz.faces.max()) + 1, basis)

        cc = Charakterdaten.unterteiler(geschlecht)
        self.assertIsNotNone(cc, 'kein Unterteiler — faces passen nicht')
        self.assertEqual(cc.sub_vertex_count, unter)
        self.assertEqual(len(cc.triangles), dreiecke)

    def test_gewichte_kommen_durch_die_unterteilung(self):
        """Vier Einflüsse je Vertex, Summe 1, und am Ende so viele Einträge wie
        das unterteilte Netz Vertices hat.

        Bei Rest-Pose sind alle Knochenmatrizen die Einheitsmatrix — eine
        falsche Zuordnung fällt dort NICHT auf, das Netz sieht richtig aus.
        Deshalb prüft dieser Test die Struktur und nicht das Bild.
        """
        from core.dienste.skingewichte import Skingewichte
        for geschlecht, (_v, basis, unter, _d) in self.NETZE.items():
            with self.subTest(geschlecht=geschlecht):
                indices, werte = Skingewichte.arrays(geschlecht)
                self.assertEqual(indices.shape, (basis, Skingewichte.EINFLUESSE))
                self.assertEqual(werte.shape, indices.shape)
                # Normiert: Ein Vertex ohne Gewichte hat Summe 0, sonst 1.
                summen = werte.sum(axis=1)
                self.assertTrue(
                    all(abs(s) < 1e-4 or abs(s - 1.0) < 1e-4 for s in summen),
                    'Gewichtssummen sind weder 0 noch 1 — nicht normiert')

                text = Skingewichte.propagiert_json(
                    geschlecht, Charakterdaten.unterteiler(geschlecht))
                self.assertIsNotNone(text, 'keine propagierten Gewichte')
                daten = json.loads(text)
                self.assertEqual(len(daten['weights']), unter,
                                 'die Zahl der Gewichte passt nicht zum '
                                 'unterteilten Netz — genau die Verschiebung, '
                                 'die bei Rest-Pose unsichtbar bleibt')
                self.assertTrue(daten['bone_names'])

    def test_der_unterteiler_wird_nur_einmal_gebaut(self):
        """Zweiter Abruf kommt aus dem Klassen-Zwischenspeicher.

        Ohne den würde jede Netz-Anfrage der Oberfläche die 138.304 Dreiecke neu
        bauen. Gemessen wird die ZWEITE Anfrage gegen eine großzügige Grenze —
        nicht das Verhältnis zur ersten: Läuft nebenher etwas, schwanken
        Sekundenwerte um Faktor 1,5 und mehr.
        """
        Charakterdaten.unterteiler('female')          # aufwärmen
        start = time.time()
        wieder = Charakterdaten.unterteiler('female')
        dauer = time.time() - start
        self.assertIsNotNone(wieder)
        self.assertLess(dauer, 0.5,
                        'zweiter Abruf dauerte %.2f s — der Zwischenspeicher '
                        'greift nicht' % dauer)

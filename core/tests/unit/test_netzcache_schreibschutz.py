# -*- coding: utf-8 -*-
"""Der Netz-Zwischenspeicher gibt keine beschreibbaren Felder heraus.

ANLASS: Review-Befund „Mögliche mutable Rückgabe gecachter NumPy-Arrays"
(Nemotron, Bereich `mesh_api`). Er stand dort als RÜCKFRAGE — das Modell hatte
den Code der drei verdächtigen Stellen nicht gesehen und bat darum. Am
28.08.2026 nachgeprüft:

* `Netzantwort.feld()` liest nur (`ascontiguousarray` + `tobytes`) — harmlos.
* `Charakterdaten.netzdaten()` gibt das GEMERKTE `MeshData` heraus, nicht eine
  Kopie. Wer `netz.faces[0] = …` schreibt, ändert es für jede weitere Anfrage
  dieses Prozesses.

Nachgezählt schreibt heute niemand hinein (acht Aufrufer, alle lesend). Genau
deshalb dieser Test: Der Schaden entstünde erst beim nächsten Aufrufer, und
zwar still — erste Anfrage richtig, zweite falsch, Serverneustart „behebt" es.

WARUM SPERREN UND NICHT KOPIEREN
================================
Kopieren hieße, 18.210 Punkte und 17.288 Flächen bei JEDER Anfrage zu
duplizieren, damit niemand schreibt, der ohnehin nicht schreibt. Die Sperre
kostet nichts und meldet den Fehler an der Stelle, an der er entsteht.
"""

import numpy as np
from django.test import TestCase

from core.dienste.charakterdaten import Charakterdaten


class NetzcacheSchreibschutzTest(TestCase):
    """`TestCase` und nicht `SimpleTestCase`: Das Laden liest Einstellungen."""

    def test_alle_gemerkten_felder_sind_gesperrt(self):
        netz = Charakterdaten.netzdaten('female')
        for name in Charakterdaten.NETZFELDER:
            feld = getattr(netz, name, None)
            if not isinstance(feld, np.ndarray):
                continue
            with self.subTest(feld=name):
                self.assertFalse(
                    feld.flags.writeable,
                    '%s ist beschreibbar — ein Aufrufer kann damit den '
                    'Zwischenspeicher des ganzen Prozesses vergiften' % name)

    def test_schreiben_wirft_statt_still_zu_wirken(self):
        """DER KERN: Aus stillem Schaden wird eine Ausnahme."""
        netz = Charakterdaten.netzdaten('female')
        with self.assertRaises(ValueError):
            netz.faces[0, 0] = 999

    def test_der_zweite_abruf_ist_dasselbe_objekt(self):
        """Ohne das wäre der Schutz sinnlos — dann gäbe es ja Kopien.

        Er belegt zugleich, warum es ihn braucht: Alle Aufrufer teilen sich
        EIN Objekt.
        """
        self.assertIs(Charakterdaten.netzdaten('female'),
                      Charakterdaten.netzdaten('female'))

    def test_lesen_geht_weiterhin(self):
        """Die Gegenprobe: Der Schutz darf die Aufrufer nicht lahmlegen.

        Alle acht lesen über Indizierung — genau das muss weiter gehen.
        """
        netz = Charakterdaten.netzdaten('female')
        self.assertEqual(netz.faces.shape[1], 4, 'Vierecke erwartet')
        self.assertGreater(int(netz.faces[0].max()), -1)
        self.assertIsInstance(netz.faces[:5].tolist(), list)

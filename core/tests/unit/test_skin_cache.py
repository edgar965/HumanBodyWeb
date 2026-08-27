# -*- coding: utf-8 -*-
"""Wächter für die zwischengespeicherten Skin-Arrays.

WARUM (Review 13.08.2026)
-------------------------
`Skingewichte.arrays` (bis zum Umbau am 15.08.2026 `_get_base_skin_arrays` in
character_api.py) legt zwei NumPy-Arrays im Klassenspeicher ab und gibt sie an
jede folgende Anfrage heraus — dieselben Objekte, nicht Kopien. Der
Server bearbeitet Anfragen in Fäden; ein einziges `indices[0, 0] = 99` in einer
künftigen Funktion würde die Gewichte für ALLE weiteren Anfragen vergiften, bis
zum nächsten Serverstart und ohne jede Spur im Protokoll.

Heute liest jede der sieben Aufrufstellen über Fancy-Indexing (`body_si[nearest]`),
und das kopiert — es gibt also keinen Mutations-Pfad. Der Schreibschutz kostet
nichts und macht aus dem stillen Schaden einen sofortigen Fehler.

Der Test prüft ZUSÄTZLICH, dass das Lesen weiter funktioniert: Ein Schreibschutz,
der die Auslieferung kaputt macht, wäre schlimmer als das Problem.
"""
import numpy as np
from django.test import TestCase

from core.dienste.skingewichte import Skingewichte


class SkinArrayCacheTest(TestCase):
    """Braucht die echten Produktivdaten (nur lesend)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.arrays = Skingewichte.arrays('female')

    def setUp(self):
        # KEIN skipTest: `skin_weights_base.json` liegt fuer beide
        # Geschlechter IM Repo (`HumanBody/data/humanBody*/`). Fehlt sie,
        # ist das der Befund und nicht der Grund, die Pruefung wegzulassen —
        # ein uebersprungener Fall sieht in der Auswertung aus wie ein
        # bestandener (27.08.2026).
        self.assertIsNotNone(
            self.arrays,
            'skin_weights_base.json fehlt — die Produktivdaten sind '
            'versioniert, ihr Fehlen ist eine Regression')

    def test_zwischengespeicherte_arrays_sind_schreibgeschuetzt(self):
        indices, weights = self.arrays
        self.assertFalse(indices.flags.writeable, 'indices ist beschreibbar')
        self.assertFalse(weights.flags.writeable, 'weights ist beschreibbar')
        with self.assertRaises(ValueError):
            indices[0, 0] = 99

    def test_zweiter_aufruf_liefert_dasselbe_objekt(self):
        """Der Zwischenspeicher soll greifen — sonst wird bei jeder Anfrage neu
        über alle 18.000 Vertices gerechnet."""
        nochmal = Skingewichte.arrays('female')
        self.assertIs(nochmal[0], self.arrays[0])

    def test_lesen_geht_weiter_wie_die_aufrufstellen_es_tun(self):
        """Fancy-Indexing wie in `character_cloth` / `garment_fit` — das kopiert
        und muss trotz Schreibschutz ein beschreibbares Ergebnis liefern."""
        indices, weights = self.arrays
        auswahl = np.array([0, 1, 2])
        kopie = indices[auswahl]
        self.assertTrue(kopie.flags.writeable,
                        'die Kopie muss beschreibbar sein, sonst brechen die Aufrufer')
        kopie[0, 0] = 7                       # darf NICHT werfen
        self.assertEqual(indices.shape[1], 4)
        self.assertEqual(weights.shape[1], 4)

    def test_gewichte_summieren_sich_auf_eins(self):
        """Nebenbefund festhalten: Die vier Einflüsse werden auf 1 normiert
        (`bw / total`). GPU-Skinning verlangt das."""
        _, weights = self.arrays
        summen = weights.sum(axis=1)
        belegt = summen > 0
        self.assertTrue(np.allclose(summen[belegt], 1.0, atol=1e-4),
                        'Gewichtssummen weichen von 1 ab: %s' % summen[belegt][:5])

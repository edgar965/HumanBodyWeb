# -*- coding: utf-8 -*-
"""Blickrichtung einer Seitenansicht aus der Silhouette (`mesh_blickrichtung`, 03.10.2026) und die Wahl der Seitenrolle in
Pixal3D Mehrbild (`mesh_pixal3d._seitenrollen`). Kunstfiguren aus Rechtecken: keine Datenbank, keine Grafikkarte, kein torch."""

import numpy as np
from django.test import SimpleTestCase

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from mesh_blickrichtung import Blickrichtung  # noqa: E402  (erst nach dem Suchpfad)


def profil(nach_rechts=True, fuss=0.03, hoehe=1000, breite=600):
    """Stehende Figur im Profil als Alpha-Feld: Körper 60 px breit mittig, Kopf etwas breiter, die Füße ragen um `fuss` (Anteil der
    Höhe) nach vorn. `nach_rechts=False` ist die Spiegelung."""
    alpha = np.zeros((hoehe + 100, breite), np.uint8)
    mitte = breite // 2
    oben = 50
    alpha[oben:oben + int(0.11 * hoehe), mitte - 40:mitte + 40] = 255        # Kopf
    alpha[oben + int(0.11 * hoehe):oben + int(0.30 * hoehe), mitte - 20:mitte + 20] = 255  # Hals und Schulter
    alpha[oben + int(0.30 * hoehe):oben + hoehe, mitte - 30:mitte + 30] = 255  # Rumpf und Beine
    alpha[oben + int(0.96 * hoehe):oben + hoehe, mitte - 30:mitte + 30 + int(fuss * hoehe * 2)] = 255  # Füße nach vorn
    return alpha if nach_rechts else alpha[:, ::-1]


class BlickrichtungTest(SimpleTestCase):
    def test_zehen_nach_rechts_ist_blick_nach_rechts(self):
        aus = Blickrichtung.messen(profil(True))
        self.assertEqual(aus['urteil'], 'rechts')
        self.assertGreater(aus['fuss'], 0)

    def test_die_spiegelung_gibt_das_gegenteil(self):
        aus = Blickrichtung.messen(profil(False))
        self.assertEqual(aus['urteil'], 'links')
        self.assertLess(aus['fuss'], 0)

    def test_ohne_fussvorsprung_gibt_es_kein_urteil(self):
        aus = Blickrichtung.messen(profil(True, fuss=0.0))
        self.assertIsNone(aus['urteil'])
        self.assertIn('zu schwach', aus['grund'])

    def test_leeres_bild_gibt_kein_urteil_und_keinen_fehler(self):
        aus = Blickrichtung.messen(np.zeros((100, 100), np.uint8))
        self.assertIsNone(aus['urteil'])

    def test_halbtransparente_ausleufer_zaehlen_nicht(self):
        alpha = profil(True)
        alpha[alpha > 0] = 255
        alpha[:, :10] = 40  # schwaches Alpha links: unter der Schwelle
        self.assertEqual(Blickrichtung.messen(alpha)['urteil'], 'rechts')

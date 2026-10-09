# -*- coding: utf-8 -*-
"""Nachformung der Scham: die Bausteine ohne Genesis-Bau (Edgar, 08.10.2026: „baue dir neue Regler, falls Genesis die nicht hat!").

Die Genesis-Figur hat im Venushügel keine Form für das, was das Original dort hat (gemessen: bis 22 mm Abstand im Mittelschnitt).
`Blendimportnachformung` zieht die Käfigpunkte im Beckenkasten zum Original und legt das Ergebnis als EIGENEN Regler ab
(`eigen:<Eigenmorph>_scham`). Hier die Teile, die ohne Käfig, Bibliothek und Datenbank prüfbar sind:

1. `kasten` wählt Punkte nur in der Beckenhöhe, innerhalb der Breite und auf der Vorderseite — und skaliert mit der Körperhöhe.
2. `verschiebung` ist der Vektor zum nächsten Punkt des Originals, nur in der Maske, ohne Ausreißer über 40 mm.
3. `zusammenfuehren` addiert ein Zusatzfeld auf einen bestehenden Morph (dicht) und lässt kleine Reste weg.
4. `zusatzregler` liest die neuen Regler aus dem Stand eines Imports; ohne Nachformung ist die Antwort leer.

Sabotage-Gegenprobe: in `kasten` die Vorderseitenbedingung streichen → Fall 1 rot; den Ausreißerfilter in `verschiebung` streichen →
Fall 2 rot; in `zusammenfuehren` `dicht += zusatz` streichen → Fall 3 rot.

Nicht gelaufen (Stand 08.10.2026) — läuft nur auf Ansage.
"""

import numpy as np
import trimesh
from django.test import SimpleTestCase

from core.dienste.blendimportnachformung import Blendimportnachformung


class NachformungTest(SimpleTestCase):
    databases = set()

    def test_1_der_kasten_nimmt_nur_die_vordere_beckenhoehe(self):
        punkte = np.array([
            [0.00, 0.86, 0.05],     # drin: Beckenhöhe, Mitte, vorn
            [0.00, 0.86, -0.05],    # Rückseite
            [0.00, 1.20, 0.05],     # zu hoch (Bauch)
            [0.00, 0.40, 0.05],     # zu tief (Knie)
            [0.20, 0.86, 0.05],     # zu weit seitlich
            [0.00, 0.78, 0.04],     # drin: unterer Rand
        ])
        # „Vorn" heißt: vor der Mitte der Figur (Median von z) — ein Rumpf hat so viel vorn wie hinten.
        mitte = np.tile([0.0, 0.5, 0.0], (8, 1))
        gesamt = np.vstack([punkte, mitte])
        maske = Blendimportnachformung.kasten(gesamt, 'scham', 0.0, 1.75)
        self.assertEqual(maske[:6].tolist(), [True, False, False, False, False, True])
        self.assertFalse(maske[6:].any())
        # Doppelte Körperhöhe, alles doppelt so groß: dieselbe Auswahl (der Kasten skaliert mit der Körperhöhe).
        gross = Blendimportnachformung.kasten(gesamt * 2.0, 'scham', 0.0, 3.5)
        self.assertEqual(gross.tolist(), maske.tolist())

    def test_2_verschiebung_zeigt_zum_original_ohne_ausreisser(self):
        flaeche = trimesh.Trimesh(vertices=[[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0]], faces=[[0, 1, 2], [0, 2, 3]], process=False)
        punkte = np.array([[0.0, 0.0, 0.01], [0.2, 0.1, -0.02], [0.0, 0.0, 0.10], [0.3, 0.3, 0.01]])
        maske = np.array([True, True, True, False])
        v = Blendimportnachformung.verschiebung(punkte, flaeche, maske)
        self.assertTrue(np.allclose(v[0], [0, 0, -0.01], atol=1e-9))
        self.assertTrue(np.allclose(v[1], [0, 0, 0.02], atol=1e-9))
        self.assertTrue(np.allclose(v[2], 0.0), '10 cm weg: ein anderes Körperteil, kein Ziel')
        self.assertTrue(np.allclose(v[3], 0.0), 'außerhalb der Maske bleibt 0')
        self.assertTrue(np.allclose(Blendimportnachformung.verschiebung(punkte, flaeche, np.zeros(4, dtype=bool)), 0.0))

    def test_3_zusammenfuehren_addiert_dicht_und_laesst_kleines_weg(self):
        zusatz = np.zeros((5, 3))
        zusatz[1] = [0.002, 0.0, 0.0]
        zusatz[4] = [0.00001, 0.0, 0.0]                     # 0,01 mm: unter `MINDESTENS`
        nummern, deltas = Blendimportnachformung.zusammenfuehren(np.array([1, 3]), np.array([[0.001, 0, 0], [0, 0.003, 0]]), zusatz)
        self.assertEqual(nummern.tolist(), [1, 3])
        self.assertTrue(np.allclose(deltas, [[0.003, 0, 0], [0, 0.003, 0]], atol=1e-7), 'Punkt 1: alt + neu')
        leer, _ = Blendimportnachformung.zusammenfuehren(None, None, np.zeros((3, 3)))
        self.assertEqual(len(leer), 0)

    def test_4_die_neuen_regler_stehen_im_stand_des_imports(self):
        stand = {'ergebnis': {'nachformung': {'regler': {'eigen:x_scham': 1.0}, 'scham': {}}}}
        self.assertEqual(Blendimportnachformung.zusatzregler(stand), {'eigen:x_scham': 1.0})
        self.assertEqual(Blendimportnachformung.zusatzregler({'ergebnis': {'nachformung': {'fehler': 'x'}}}), {})
        self.assertEqual(Blendimportnachformung.zusatzregler({}), {})
        self.assertEqual(Blendimportnachformung.zusatzregler(None), {})

    def test_5_bei_scham_objekt_entfaellt_die_nachformung(self):
        """Edgar, 09.10.2026: „die hat im moment zwei mal Geschlechtsorgane" — die facettierte Nachformung der Figur lag unter dem
        Scham-Stück. Mit `scham = objekt` kommt die Scham nur als Stück; mit `figur` läuft die Nachformung wie bisher.
        Sabotage: die Bedingung in `Blendimportlauf._nachformung` streichen → der erste Teil wird rot."""
        from unittest import mock

        from core.dienste.blendimportlauf import Blendimportlauf
        lauf = Blendimportlauf.__new__(Blendimportlauf)
        lauf.ergebnis = mock.Mock()
        lauf.inventar = lambda: {}
        lauf.ablage, lauf.melden = object(), None
        with mock.patch('core.dienste.blendimportnachformung.Blendimportnachformung') as nachformung:
            lauf.stand = {'einstellungen': {'scham': 'objekt'}, 'rollen': [], 'quelle': {'name': 'x'}}
            lauf._nachformung(job=None)
            nachformung.assert_not_called()
            schritt, wert = lauf.ergebnis.call_args[0]
            self.assertEqual(schritt, 'nachformung')
            self.assertIn('aus', wert)
            self.assertEqual(Blendimportnachformung.zusatzregler({'ergebnis': {'nachformung': wert}}), {})
            lauf.stand = {'einstellungen': {'scham': 'figur'}, 'rollen': [], 'quelle': {'name': 'x'}}
            nachformung.return_value.formen.return_value = {'regler': {'eigen:x_scham': 1.0}}
            lauf._nachformung(job=None)
            nachformung.assert_called_once()
            self.assertEqual(lauf.ergebnis.call_args[0], ('nachformung', {'regler': {'eigen:x_scham': 1.0}}))

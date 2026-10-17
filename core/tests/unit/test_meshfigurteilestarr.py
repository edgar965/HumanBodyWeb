# -*- coding: utf-8 -*-
"""Mesh to 3D: ein Bestandteil geht nur starr mit EINEM Körperteil, wenn er überwiegend dort hängt (14.10.2026, Bart des Zauberers).

Gemessen am Zauberer (`bart_anteil.py`): Bart 49 % Rumpf / 47 % Kopf, Hut 100 % Kopf, Tasche 100 % Oberschenkel, Stab 56 % Hand (wird aber gehalten).
1. Hängt ein Stück zu `STARR_ANTEIL` oder mehr am erkannten Teil, bleibt es starr (`erkannt` kommt unverändert zurück).
2. Hängt es darunter und wird nicht gehalten, folgt es den nahen Knochen (None).
3. Ein gehaltenes Stück bleibt starr, auch bei kleinem Anteil — und der Anteil wird dann nicht einmal gerechnet.

Sabotage-Gegenprobe: `>=` durch `<` ersetzen → `test_1` und `test_3` rot; `haelt or` streichen → `test_3` rot; `STARR_ANTEIL` auf 0.4 → `test_2` rot.

Nicht gelaufen — läuft nur auf Ansage.
"""

from types import SimpleNamespace

from django.test import SimpleTestCase

from core.dienste.meshfigurteile import Meshfigurteile


def requisit(anteil):
    """Attrappe mit der Signatur von `Blendimportrequisit.anteil_teil` (Punkte, Nummer) → Anteil; merkt sich die Aufrufe."""
    aufrufe = []

    def anteil_teil(punkte, nummer):
        aufrufe.append(nummer)
        return anteil

    return SimpleNamespace(anteil_teil=anteil_teil, aufrufe=aufrufe)


class StarrNurBeiAnteilTest(SimpleTestCase):
    databases = set()

    ERKANNT = {'teil': 'kopf', 'nummer': 3, 'knochen': 'head'}

    def test_1_ueberwiegend_an_einem_teil_bleibt_starr(self):
        r = requisit(1.0)
        self.assertIs(Meshfigurteile._starr_nur_bei_anteil(r, self.ERKANNT, None, None), self.ERKANNT)
        self.assertEqual(r.aufrufe, [3])
        grenze = requisit(Meshfigurteile.STARR_ANTEIL)
        self.assertIs(Meshfigurteile._starr_nur_bei_anteil(grenze, self.ERKANNT, None, None), self.ERKANNT)

    def test_2_verteilt_auf_mehrere_teile_folgt_den_knochen(self):
        self.assertIsNone(Meshfigurteile._starr_nur_bei_anteil(requisit(0.49), self.ERKANNT, None, None))
        self.assertIsNone(Meshfigurteile._starr_nur_bei_anteil(requisit(0.0), self.ERKANNT, None, None))

    def test_3_gehaltenes_bleibt_starr_ohne_den_anteil_zu_rechnen(self):
        r = requisit(0.1)
        haelt = {'seite': 'r', 'stabfoermig': True}
        self.assertIs(Meshfigurteile._starr_nur_bei_anteil(r, self.ERKANNT, haelt, None), self.ERKANNT)
        self.assertEqual(r.aufrufe, [])

    def test_4_schwelle_liegt_zwischen_den_gemessenen_werten(self):
        self.assertGreater(Meshfigurteile.STARR_ANTEIL, 0.49)        # Bart am Rumpf
        self.assertLessEqual(Meshfigurteile.STARR_ANTEIL, 1.0)       # Hut, Tasche

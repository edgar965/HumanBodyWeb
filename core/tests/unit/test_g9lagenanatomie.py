# -*- coding: utf-8 -*-
u"""G9lagenanatomie — getragene Anatomien liegen unter jedem Stück, das ihnen nahe kommt (19.10.2026).

Anlass: `mh_cortu_cargo_pants` an Matt0 — der grobe Käfig brachte im Schritt keine 20 Punkte binnen 3 cm, `G9lagen.einordnen` ordnete das Geograft gar nicht
ein, Anhebung und Drapierer liefen nicht, die Hose lag ganz hinter dem Genital. Kunstdaten, ohne Daz-Bibliothek.

1. Eine Anatomie, die die Einordnung überging, kommt nach innen, wenn ein Käfigpunkt binnen `naehe` an ihr liegt.
2. ... und nicht, wenn sie weiter weg ist (Hut, Schuh).
3. Eine außen eingeordnete Anatomie kommt nach innen (die Regel vom 11.10.2026), Kleidung bleibt, wo sie war.
4. Ist das angefragte Stück selbst eine Anatomie, bleibt nur die andere Anatomie innen, Kleidung kommt nach außen; nichts wird über die Nähe ergänzt.

Geschrieben 19.10.2026, gelaufen auf Ansage: grün. Sabotage (gedacht): `_nah` immer leer zurückgeben → Fall 1 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.g9lagenanatomie import G9lagenanatomie

ANATOMIEN = {'daz_anatomie_mann', 'daz_anatomie_frau'}


def ist_anatomie(kennung):
    return kennung in ANATOMIEN


class Lagenanatomie(SimpleTestCase):
    databases = set()

    def test_1_bis_4(self):
        kaefig = np.array([[0.0, 0.0, 0.0], [0.1, 0.0, 0.0]])
        nah = np.array([[0.0, 0.02, 0.0]])
        fern = np.array([[0.0, 0.5, 0.0]])
        # 1.
        innen, aussen = G9lagenanatomie.unten('hose', kaefig, [('daz_anatomie_mann', nah, False)], [], [], ist_anatomie, 0.03)
        self.assertEqual((innen, aussen), (['daz_anatomie_mann'], []))
        # 2.
        innen, aussen = G9lagenanatomie.unten('hut', kaefig, [('daz_anatomie_mann', fern, False)], [], [], ist_anatomie, 0.03)
        self.assertEqual((innen, aussen), ([], []))
        # 3.
        innen, aussen = G9lagenanatomie.unten('hose', kaefig, [('daz_anatomie_frau', nah, False), ('shirt', nah, True)], [], ['daz_anatomie_frau', 'shirt'],
                                              ist_anatomie, 0.03)
        self.assertEqual((innen, aussen), (['daz_anatomie_frau'], ['shirt']))
        # 4.
        innen, aussen = G9lagenanatomie.unten('daz_anatomie_mann', kaefig, [('daz_anatomie_frau', nah, False), ('slip', nah, False)],
                                              ['daz_anatomie_frau', 'slip'], [], ist_anatomie, 0.03)
        self.assertEqual((innen, aussen), (['daz_anatomie_frau'], ['slip']))

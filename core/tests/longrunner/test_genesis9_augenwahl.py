# -*- coding: utf-8 -*-
u"""Jede Augenwahl der Toolbar liefert einen Augapfel MIT Pupille (09.10.2026, Wächter gegen den dritten Rückfall).

Edgar: „Augen ändern funktioniert nicht beim aktuellen Modell Damira", „das Augenproblem ist schon öfter aufgetreten, alle Modelle sollen
alle Augen kriegen können". Der dritte Rückfall (nach Fotokachel und Ersatz-Augen am 08.10.): sechs der 42 Presets (Amala, Fabrice, Kat,
Laura, Matt, Ty) lieferten nur die Lederhaut — weiße, glasige Augen —, weil `G9material` bei geschichteten Bildern die erste Ebene nahm
(`G9augenebenen`). Kein Server-Log, keine Ausnahme, die Seite lud mit 200.

Der Wächter geht über ALLE Einträge von `G9hautpresets.augen()` (auch die, die später dazukommen): Beide Augäpfel haben ein Albedo-Bild,
das die Bibliothek (oder `augen/<hash>.jpg`) auflöst, und in der oberen Hälfte jeder Kartenhälfte liegt ein dunkler Block — die Pupille.
Gemessen am 09.10.2026: Alle 42 Karten haben ihn (höchster Wert 28,7 von 255), die reine Lederhaut (`Genesis9_Eyes_Sclera_01.jpg`) liegt bei 99,3.

Sabotage-Gegenprobe: in `G9augenebenen.bild` die Zeile `gelegt = cls._vormerken(eintrag)` durch `gelegt = None` ersetzen → sechs Presets rot.

LongRunner (42 Karten à 4096²). Nicht gelaufen (09.10.2026) — läuft nur auf Ansage.
"""
import unittest

import numpy as np
from django.test import SimpleTestCase
from Genesis9.hautpresets import G9hautpresets
from Genesis9.material import G9material
from Genesis9.pfade import G9pfade
from PIL import Image

#: Dunkelster 9×9-Block der Augenhälfte (0–255): die Pupille liegt weit darunter, die reine Lederhaut bei ~100.
PUPILLE = 70


def _dunkelster_block(datei):
    u"""Dunkelster Block je Kartenhälfte (links, rechts) im Augenbereich der oberen Hälfte."""
    grau = np.asarray(Image.open(datei).convert('RGB').resize((512, 512)).convert('L')).astype(float)
    werte = []
    for spalten in (slice(0, 256), slice(256, 512)):
        block = grau[20:240, spalten]
        glatt = (block[:-8, :-8] + block[4:-4, 4:-4] + block[8:, 8:]) / 3
        werte.append(float(glatt.min()))
    return werte


@unittest.skipUnless(G9pfade.vorhanden(), 'Daz-Bibliothek mit Genesis 9 fehlt')
class AugenwahlTest(SimpleTestCase):
    databases = set()

    def test_jedes_augenpreset_hat_eine_pupille(self):
        presets = G9hautpresets.augen()
        self.assertGreater(len(presets), 30, 'die Augenliste ist leer oder fast leer')
        fehler = []
        for eintrag in presets:
            bilder = G9hautpresets.augenbilder(eintrag['id'])
            for gruppe in ('Eye Left', 'Eye Right'):
                albedo = (bilder.get(gruppe) or {}).get('albedo')
                datei = G9material.datei(albedo) if albedo else None
                if datei is None:
                    fehler.append('%s: %s ohne auflösbares Albedo (%s)' % (eintrag['id'], gruppe, albedo))
                    continue
                dunkel = max(_dunkelster_block(datei))
                if dunkel >= PUPILLE:
                    fehler.append('%s: %s ohne Pupille (dunkelster Block %.1f)' % (eintrag['id'], gruppe, dunkel))
        self.assertEqual(fehler, [], '\n'.join(fehler))

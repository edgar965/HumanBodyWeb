# -*- coding: utf-8 -*-
u"""Exportbildprüfung — ein gerendertes Exportbild auf farblose Stellen ansehen.

WOZU (26.09.2026): Edgar hat dreimal hintereinander dasselbe gemeldet — „immer
noch Fehler" — und jedes Mal war es eine ANDERE Ursache, aber IMMER dieselbe
Erscheinung: eine Stelle der Figur, die im fremden Programm weiß oder grau
ist, wo im Browser Farbe war.

  * Hals, Knie, Finger hellgrau  -> Bildkarten standen auf dem Kopf
  * Augen weiß ohne Iris         -> durchsichtige Hornhaut davor
  * Brauen schneeweiß            -> `Kd` ging beim Schreiben verloren

Ein Test, der die Datei strukturell prüft (Flächen da? Material zugeordnet?),
hat alle drei durchgelassen. Diese Prüfung fragt stattdessen das, was Edgar
fragt: SIEHT DIE FIGUR RICHTIG AUS? Gemessen wird der Anteil farbloser
Bildpunkte auf der Figur — insgesamt und je Höhenstreifen, damit man weiß, wo.

Das Bild kommt aus `blender/exportbild.py` (Hintergrund durchsichtig, also ist
die Figur genau das, was Alpha > 0 hat).

GRENZEN, ehrlich benannt:
- Grau ist nicht immer falsch: graue Kleidung, ein Metallknopf, ein grauer
  Schuh. Deshalb gibt es `ausnahme_streifen` und eine großzügige Schwelle —
  die Prüfung soll einen weißen Hals finden, nicht über einen grauen Gürtel
  stolpern (`~/.claude/rules/analysewerkzeuge.md`: Fehlalarme sind teurer).
- Sie sagt nicht, WARUM eine Stelle farblos ist. Dafür ist
  `Exportkartenpruefung` da, die in den Karten nachsieht.
"""
from pathlib import Path


class Exportbildpruefung:

    #: Als farblos gilt ein Punkt, dessen Kanäle höchstens so weit
    #: auseinanderliegen UND der hell genug ist. Haut hat bei Damira1
    #: R−B ≈ 55, die Fehlstellen lagen unter 15.
    SPANNE = 20
    HELL = 120

    #: So viele Höhenstreifen — 10 reicht, um Kopf, Rumpf, Beine und Füße
    #: auseinanderzuhalten, ohne auf einzelne Pixel hereinzufallen.
    STREIFEN = 10

    def __init__(self, png_pfad):
        self.pfad = Path(png_pfad)

    def bericht(self):
        u"""
        `{punkte, farblos, anteil, streifen: [{nr, von, bis, punkte, farblos,
        anteil}], schlimmster}` — Streifen 0 ist OBEN (Kopf).
        """
        import numpy as np
        from PIL import Image

        bild = Image.open(self.pfad).convert('RGBA')
        feld = np.asarray(bild, dtype=np.int16)
        figur = feld[:, :, 3] > 128
        rgb = feld[:, :, :3]
        spanne = rgb.max(axis=2) - rgb.min(axis=2)
        hell = rgb.max(axis=2) >= self.HELL
        farblos = figur & (spanne <= self.SPANNE) & hell

        hoehe = feld.shape[0]
        streifen = []
        for nr in range(self.STREIFEN):
            von = nr * hoehe // self.STREIFEN
            bis = (nr + 1) * hoehe // self.STREIFEN
            f = int(figur[von:bis].sum())
            g = int(farblos[von:bis].sum())
            streifen.append({'nr': nr, 'von': von, 'bis': bis, 'punkte': f,
                             'farblos': g, 'anteil': (g / f) if f else 0.0})

        gesamt = int(figur.sum())
        weg = int(farblos.sum())
        mit_inhalt = [s for s in streifen if s['punkte'] > 200]
        schlimmster = max(mit_inhalt, key=lambda s: s['anteil'], default=None)
        return {'punkte': gesamt, 'farblos': weg,
                'anteil': (weg / gesamt) if gesamt else 0.0,
                'streifen': streifen, 'schlimmster': schlimmster}

    @staticmethod
    def zeilen(bericht):
        aus = [f'Figur: {bericht["punkte"]:,} Bildpunkte, farblos {bericht["farblos"]:,} '
               f'({100 * bericht["anteil"]:.1f} %)']
        for s in bericht['streifen']:
            if not s['punkte']:
                continue
            balken = '#' * int(60 * s['anteil'])
            aus.append(f'  Streifen {s["nr"]} (y {s["von"]}–{s["bis"]}): '
                       f'{s["punkte"]:>7,} Punkte, farblos {100 * s["anteil"]:>5.1f} % {balken}')
        return aus

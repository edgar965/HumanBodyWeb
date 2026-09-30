# -*- coding: utf-8 -*-
u"""Exportgrauteile — welche Objekte einer `.obj` sind GEWOLLT grau oder weiß?

WOZU (30.09.2026): `Exportbildpruefung` zählt „farblose" Bildpunkte, damit ein
weißer Hals oder ein weißes Knie auffällt. Sie kann aber nicht unterscheiden,
ob eine Stelle farblos ist, weil die Farbe VERLOREN ging, oder weil das Teil
so gemeint ist. Der Fall lief am 30.09. rot, obwohl die Ausgabe stimmte: Der
Export „TanzfigurK_2" trägt Sneakers mit weißgrauer Sohle, Zunge und
Schnürung — der Fußstreifen war zu 29,7 % „farblos", das Bild selbst (Blender,
700×1000) zeigte eine richtige Figur.

ZWEI WEGE, ein Teil als gewollt grau zu erkennen (Gemessen an `TanzfigurK_2`):

1. **Die Karte ist an den belegten Stellen selbst farblos.** Je Werkstoff mit
   Karte wird in der UV-Mitte jeder Fläche nachgesehen (`flaechentexel`,
   dieselbe Abtastung wie `Exportkartenpruefung`). Sneakers: fünf Objekte mit
   95–100 % farblosen Flächen; Augen (Lederhaut) 10 %, Jeans-Bund 14 %, alle
   übrigen unter 2 %. Ein Objekt gilt ab `ANTEIL` (50 %) als weiß. NICHT die
   Karte als Ganzes ansehen: die Hautkarten sind zu 36–48 % grau, aber als
   leerer Rand zwischen den UV-Inseln, den keine Fläche trifft.
2. **Flachfarbe ohne Karte, deren `Kd` grau ist** (Sohle und Schnürung, `Kd`
   0,58 / 0,56 / 0,14). Hier zählen alle Bedingungen zugleich, sonst bleibt das
   Objekt im Bild:
   - kein `map_Kd` und kein `map_d`;
   - `Kd` steht in der `.mtl` (ein fehlendes `Kd` ist der Vorfall „schneeweiße
     Brauen") und ist grau (Spanne höchstens `SPANNE`);
   - `Kd` ist NICHT das Standardweiß (Höchstwert unter `WEISS`) — ein
     verlorenes `Kd` kommt als (1, 1, 1) an;
   - `Kd` ist hell genug, um im Bild als farblos zu zählen (`DUNKEL`):
     Dunkelbraun der Brauen (≈ 0,02) bleibt gemessen;
   - das Objekt ist deckend (`d` ≥ `DECKEND`): die fast durchsichtige Hornhaut
     vor der Iris (`d` 0,12) ist der zweite alte Vorfall.

GRENZEN, ehrlich: Ein Teil, das wirklich reinweiß (1, 1, 1) sein soll, bleibt
ohne Karte ein Befund — von einem verlorenen `Kd` unterscheidet es sich nur an
der Quelle im Browser. Ein ausgenommenes Objekt fehlt im Bild; dass seine Karte
richtig steht, prüft weiter `Exportkartenpruefung`, die Farbe im Umriss
`Exportfleckenpruefung`.
"""
from .exportkartenpruefung import Exportkartenpruefung
from .objwerkstoffe import Objwerkstoffe


class Exportgrauteile:

    #: Größter Abstand zwischen Rot, Grün und Blau, bei dem eine Farbe als
    #: grau gilt (0,08 ≈ 20 von 255 — wie `Exportbildpruefung.SPANNE`).
    SPANNE = 0.08
    #: Ab hier ist `Kd` das OBJ-Standardweiß, nicht eine gewählte Farbe.
    WEISS = 0.95
    #: Darunter rendert ein Grau schwarz oder dunkel, nie „farblos hell"
    #: (`Exportbildpruefung.HELL`) — die Brauen (`Kd` ≈ 0,02) bleiben im Bild.
    DUNKEL = 0.1
    #: Darunter zählt ein Werkstoff als durchsichtige Schale.
    DECKEND = 0.5
    #: Ein Texel (0..255) zählt als hell, wenn sein größter Kanal so hoch ist.
    #: Das Bild leuchtet mit Stärke 1,6 (`exportbild.kamera_und_licht`); ein
    #: Texel von ≈ 100 erscheint dort mit ≈ 120, der Schwelle von
    #: `Exportbildpruefung.HELL`. Die Trennung ist grob (Sneakers 95–100 %,
    #: alles andere unter 15 %) — auf den genauen Wert kommt es nicht an.
    TEXEL_HELL = 100
    #: Und so nah an Grau (Spanne der Kanäle von 255).
    TEXEL_SPANNE = 20
    #: So viele Flächen eines Objekts müssen auf farblosen Texeln liegen.
    ANTEIL = 0.5

    def __init__(self, obj_pfad):
        self.obj_pfad = obj_pfad
        self.werkstoffe = Objwerkstoffe(obj_pfad)

    def gewollt_grau(self, wert):
        u"""`wert` ist ein Block aus `Objwerkstoffe.werkstoffwerte()`."""
        farbe = wert['Kd']
        if wert['karte'] or farbe is None or wert['d'] < self.DECKEND:
            return False
        return max(farbe) - min(farbe) <= self.SPANNE and self.DUNKEL <= max(farbe) < self.WEISS

    def werkstoffe_mit_weisser_karte(self):
        u"""Namen der Werkstoffe, deren Karte an den belegten Stellen
        überwiegend farblos ist."""
        weiss = set()
        for name, texel in Exportkartenpruefung(self.obj_pfad).flaechentexel().items():
            if not len(texel):
                continue
            farblos = ((texel.max(axis=1) - texel.min(axis=1)) <= self.TEXEL_SPANNE) \
                & (texel.max(axis=1) >= self.TEXEL_HELL)
            if farblos.mean() >= self.ANTEIL:
                weiss.add(name)
        return weiss

    def objekte(self):
        u"""Sortierte Namen der Objekte, die gewollt grau oder weiß sind."""
        werte = self.werkstoffe.werkstoffwerte()
        gewollt = {name for name, wert in werte.items() if self.gewollt_grau(wert)}
        gewollt |= self.werkstoffe_mit_weisser_karte()
        if not gewollt:
            return []
        return sorted(o for o, m in self.werkstoffe.objekt_werkstoff().items() if m in gewollt)

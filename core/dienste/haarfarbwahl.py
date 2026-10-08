# -*- coding: utf-8 -*-
"""Haarfarbwahl — welche Fotos die Haarfarbe des Auftrags bestimmen (08.10.2026, N1 „Edgar: das Haar wird grau").

Der Schritt „Segmentierung" misst je Foto den Median der Pixel der Klasse Haar (`segmentierung.json`: `bilder[].haarfarbe`, `haar_pixel`) und mittelt nach Pixeln. An N1 (zwei Fotos einer Person) ergab das Grau:
vorne (147, 107, 75), dunkelblond; hinten (176, 171, 193) — das Rückfoto hat einen Blaustich (Kopfzone Blau 204 über Rot 173, nur 84,7 % warme Hautpixel gegen 99,5 % vorn), ein Mittel aus beiden (164, 145, 146)
trifft keins der Fotos und wurde im Modell zu #9b9b9b.

Regel: Ein Haarton mit Blaustich — Blau um mehr als `BLAU_UEBER_ROT` über Rot — ist kein natürlicher Haarton, sondern ein Farbstich des Fotos (oder gefärbtes Haar; dann zeigen es alle Fotos). Solange ein anderes Foto einen Haarton
ohne Blaustich hat, zählen die mit Blaustich nicht. Zeigen alle Fotos Blaustich oder gibt es nur eines, gilt das Mittel wie bisher. Der Wert 8 (von 255) ist ein Anhaltswert, an EINEM Auftrag gemessen (N1: +17 im Rückfoto,
−72 im Vorderfoto); die Haarfarben der Auftragsfotos mit gemessener Segmentierung wurden nicht durchgesehen.
"""

__all__ = ['Haarfarbwahl']


class Haarfarbwahl:
    BLAU_UEBER_ROT = 8

    @classmethod
    def blaustich(cls, rgb):
        """True, wenn das Blau des Haartons (0–255) um mehr als `BLAU_UEBER_ROT` über dem Rot liegt."""
        return float(rgb[2]) - float(rgb[0]) > cls.BLAU_UEBER_ROT

    @classmethod
    def waehlen(cls, bilder):
        """`(rgb 0–255 oder None, ausgelassen)` aus den Fotoeinträgen von `segmentierung.json` (`rolle`, `haarfarbe`, `haar_pixel`): das nach Haarpixeln gewichtete Mittel der Fotos ohne Blaustich —
        `ausgelassen` ist `{rolle: rgb}` der Fotos, die dafür wegfielen. Ohne Fotoeinträge mit Haarfarbe: `(None, {})`."""
        mit = [b for b in bilder or [] if b.get('haarfarbe') and b.get('haar_pixel')]
        if not mit:
            return None, {}
        gut = [b for b in mit if not cls.blaustich(b['haarfarbe'])]
        zaehlen = gut or mit
        ausgelassen = {str(b.get('rolle')): [int(c) for c in b['haarfarbe']] for b in mit if b not in zaehlen}
        gewicht = sum(float(b['haar_pixel']) for b in zaehlen)
        rgb = [sum(float(b['haarfarbe'][k]) * float(b['haar_pixel']) for b in zaehlen) / gewicht for k in range(3)]
        return [int(round(c)) for c in rgb], ausgelassen

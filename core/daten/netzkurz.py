# -*- coding: utf-8 -*-
u"""Netzkurz — ein float32-Feld als 16 Bit über den Draht (19.10.2026).

Edgar, 19.10.2026: „hast du 64 bit Zahlen in json? das ist doch nicht nötig, 16 oder maximal 32 Bit würden doch ausreichen … stelle auf 16 bit um".
Gemessen am Vorrat (6 Antworten, Genesis grob, 9,3 MB): float32 4,83 MB (Punkte, Normalen, UV, Dicke), uint32 2,59 MB (Dreiecke), uint16 1,15 MB
(Knochennummern), uint8 0,58 MB (Gewichte). Die float32-Felder sind die Hälfte — sie gehen jetzt als uint16 im Rahmen des Feldes:

    wert = ab + q · schritt          q = 0 … 65535,  schritt = (max − min) / 65534

Auflösung: eine Figur von 2 m → 0,03 mm je Stufe (größter Fehler die Hälfte), Normalen (−1 … 1) 3·10⁻⁵, UV einer Kachel (0 … 1) 1,5·10⁻⁵ (bei 4096 px
0,06 Pixel). **Die Null bleibt genau Null** (`ab` liegt auf dem Raster, `ab + q₀·schritt` ist dann exakt 0 — beide Seiten rechnen dasselbe Produkt in double):
Felder wie `mischung` fragen `<= 0`. Ohne Vorzeichenwechsel kommt das Minimum exakt zurück (sonst wie jeder Wert auf eine halbe Stufe); gleiche Werte bleiben
gleich (Nahtkopien), ungleiche können gleich werden.

Nicht gekürzt: kleine Felder (unter `AB_ANZAHL` Werten — Skelett, Matrizen, Kanäle der Gelenkfelder: dort spart es nichts), Felder mit NaN/∞, Felder,
deren Spanne 0 ist (ein Wert — float32 bleibt kürzer zu erklären als zu sparen). Der Browser bekommt das nur, wenn er es bestellt hat
(`Netzausgabe.will_binaer`: `Accept: …;kodierung=u16`), sonst wie bisher float32 — ein Tab mit altem Code liest also nie 16 Bit als float32.

NUMMERN WERDEN NIE GEKÜRZT (12.11.2026, Edgar an Olesia1: „das T-Shirt sitzt oben nicht (kein Saum), und die Schuhe haben Texturprobleme, oder haut geht
durch“): Ein Feld, das Nummern trägt statt Messwerte, reist als `Netzfeld` mit `genau` und bleibt float32 (`Netzpaket._ersetzen` fragt danach, hier wird
dafür nichts gerechnet). Die Oberflächenbindung schickt je Stoffpunkt drei KÖRPERPUNKT-NUMMERN als float32 (`G9netzantwort`, `bindung.dreieck`: der Shader
liest Attribute als Gleitkomma). Auf der feinen Stufe reichen sie bis 104.479, das Raster war dort 1,59 — gemessen im Chrome an Olesia1: von 176.484 Nummern
der Angie Sneakers kamen 238 ganzzahlig an, 39.186 von 58.828 Punkten nannten drei Körperpunkte, die kein Dreieck des Körpers sind, 8.395 davon lagen über
5 cm auseinander. Der Shader schob solche Punkte schon in der Ruhelage bis 40 mm (Stacheln an Kragen, Seitennaht und Schuhspitze; mit abgeschalteter Bindung
waren Kragen und Schuh sauber). Gefolgert, nicht an weiteren Stücken gemessen: Das galt seit dem 19.10.2026 für jedes gebundene Daz-Stück der feinen Stufe; der
Käfig (Nummern bis 27.086, Raster 0,41, Fehler höchstens 0,21) rundete noch richtig. Ebenso markiert: Knochennummern, die als float32 reisen
(`Netzantwort.NUMMERN`, `skin_indices`) — Threes Shader schneidet ab (`int(i)`, three 0.170.0 `skinning_pars_vertex.glsl.js`), 56,9993 wäre Knochen 56. Ob
eine Figurart davon betroffen war, ist nicht gemessen.
"""
import torch
from KoerperKI_alle.torchfeld import Torchfeld

__all__ = ['Netzkurz']


class Netzkurz:

    #: Darunter lohnt das Kürzen nicht (Kopf statt Nutzlast).
    AB_ANZAHL = 4096
    STUFEN = 65534

    @classmethod
    def packen(cls, rohdaten, anzahl):
        u"""`(bytes uint16, {'ab', 'schritt'})` für die float32-Bytes `rohdaten` — oder None (nicht kürzen)."""
        if anzahl < cls.AB_ANZAHL:
            return None
        w = Torchfeld.astype(torch.frombuffer(bytearray(rohdaten), dtype=torch.float32, count=anzahl).to(Torchfeld.KARTE), torch.float64)
        if not Torchfeld.isfinite(w).all():
            return None
        lo, hi = float(w.min()), float(w.max())
        if hi <= lo:
            return None
        schritt = (hi - lo) / cls.STUFEN
        if lo < 0.0 < hi:                       # die Null auf das Raster: ab = −q₀·schritt
            ab = -float(Torchfeld.round(-lo / schritt)) * schritt
        else:
            ab = lo
        q = Torchfeld.astype(Torchfeld.clip(Torchfeld.round((w - ab) / schritt), 0, 65535), Torchfeld.dtype('<u2'))
        return Torchfeld.als_bytes(q), {'ab': ab, 'schritt': schritt}

    @staticmethod
    def entpacken(rohdaten, anzahl, kurz):
        u"""Die float32-Bytes zurück (Gegenprobe, Werkzeuge) — dieselbe Rechnung wie `gemeinsam/netzpaket.js`."""
        q = Torchfeld.astype(torch.frombuffer(bytearray(rohdaten), dtype='<u2', count=anzahl).to(Torchfeld.KARTE), torch.float64)
        return Torchfeld.als_bytes(Torchfeld.astype(float(kurz['ab']) + q * float(kurz['schritt']), torch.float32))

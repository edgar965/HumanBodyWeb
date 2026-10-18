# -*- coding: utf-8 -*-
u"""Mhaehnlichkeit — Kinder-Morphs als Ähnlichkeit plus Rest auf den Genesis-Käfig legen (17.10.2026).

Edgar, 17.10.2026 (Baby mit Rippen- und Bartfalten, Arm überm Kopf, „Altersregler sind kacke“): „Hast du diese Alters-Regler erfunden? … Schau nach, was es bei HumanBody oder MakeHuman
gibt. Vielleicht Export nach Genesis, Altersmorph, Export zurück?“ MakeHumans Alterskurve ist echt (Baby 1 Jahr, Kind 10, jung 25, alt 90); der Fehler lag im ÜBERTRAGEN.

DER FEHLER: `Mhklonuebertragung` legt ein MakeHuman-Delta durch die Rahmen der Glieder auf den Käfig — sauber für Zentimeter, nicht für ein Baby (Delta am Kopf 99 cm: der Körper
schrumpft auf 38 %). Jede Unschärfe der Rahmen, jede falsch gewählte Nachbarschaft wächst mit dem Delta: Rauheit des Felds Mittel 0,90 mm, 99 % 4,3 mm; der Kopfknochen stand 128 mm vor
der Hüfte (Vorgabe 16 mm dahinter), das Skelett-Overlay und die Haut zeigten Zacken.

DER WEG HIER (der Rundlauf, den Edgar vorschlug, nur ohne den Umweg): Ein Kind ist im Wesentlichen ein VERKLEINERTER Erwachsener. Diesen Teil rechnet man nicht durch Rahmen, sondern exakt:

    s      Höhenverhältnis, das MakeHumans Ziel selbst erreicht (Baby 0,379, Kind 0,793)
    C      der beste Mittelpunkt der Verkleinerung (kleinste Quadrate): auf der Körperachse, wenige Zentimeter unter dem Boden (`G9aehnlichkeit`)
    Rest   Delta − (s − 1)·(P − C)  — nur die Proportionen (Kopf größer, Beine kürzer): Baby höchstens 4,3 cm (statt 99), Kind 3,6 cm (statt 33)
    Feld   (s − 1)·(Käfig − C)  +  Rest über den Klon

`Rest` geht durch die bewährte Übertragung — dort ist der Fehler ein Vielfaches kleiner. Gemessen (`ProjektTemp/_wegwerf/hautebenen/kind_aehnlichkeit.py`, `kind_zentrum.py`): Rauheit Baby 0,90 → 0,41 mm
(99 %: 4,3 → 1,5), Kind 0,35 → 0,23; Kopfknochen gegen Hüfte Baby +128 → −13 mm, Kind +39 → −7 mm — ohne jede Haltungskorrektur. Der erste Mittelpunkt war die Fußmitte (15 cm vor der Körperachse:
Rest 10 cm); mit der Achse sinkt er auf 2,2 cm.

DIE GELENKE: Für die Ähnlichkeit sind sie bekannt (`(s − 1)·(Gelenk − C)`, Kopf und Ende); nur der Rest wird aus der Haut geschätzt (`G9gelenkversatz.fuer_morph(…, aehnlich=…)`) —
sonst schöbe die Schätzung aus der Haut (Oberflächenpunkte um das Gelenk) die Wirbelsäulengelenke beim Baby um rund 100 mm daneben (gemessen: `spine4` +98 mm bei reiner Ähnlichkeit).
"""
import numpy as np
from Genesis9.aehnlichkeit import G9aehnlichkeit
from Genesis9.basisnetz import G9basisnetz

__all__ = ['Mhaehnlichkeit']


class Mhaehnlichkeit:
    u"""`feld(delta_dm)` -> `(feld, rest, s, unter, zentrum)` für die Kinder-Morphs (`G9aehnlichkeit.MORPHS`: Baby, Kind)."""

    def __init__(self, bauer):
        u"""`bauer`: `Mhmorpheaufgenesis` (vorbereitet: Vorgabefigur, Klon-Übertragung)."""
        self.bauer = bauer

    @classmethod
    def ist(cls, kennung):
        return G9aehnlichkeit.ist(kennung)

    def zerlegen(self, delta):
        u"""`(s, unter, zentrum, rest)` für ein hm08-Delta (dm): Höhenverhältnis, Abstand des besten Mittelpunkts unter dem Boden (m), der Mittelpunkt in MakeHuman (dm) und das Delta ohne die Ähnlichkeit (dm)."""
        koerper = self.bauer.uebertragung.koerper
        p0 = np.asarray(self.bauer.vorgabe, dtype=np.float64)
        delta = np.asarray(delta, dtype=np.float64)
        s = float(np.ptp((p0 + delta)[koerper][:, 1])) / float(np.ptp(p0[koerper][:, 1]))
        beste_hoehe = float((p0[koerper][:, 1] - delta[koerper][:, 1] / (s - 1.0)).mean())          # kleinste Quadrate: C = Mittel(P − Δ/(s − 1)); x und z liegen auf der Körperachse
        zentrum = np.array([0.0, beste_hoehe, 0.0])
        unter = (float(p0[koerper][:, 1].min()) - beste_hoehe) * self.bauer.METER
        return s, unter, zentrum, delta - (s - 1.0) * (p0 - zentrum)

    def feld(self, delta):
        u"""`(feld, rest, s, unter, zentrum)`: das Käfigfeld (m) = Ähnlichkeit + übertragener Rest, dazu der Rest allein (für die Gelenke), `s`, der Abstand `unter` und der Mittelpunkt im Rahmen des Käfigs."""
        s, unter, _zentrum_mh, rest_dm = self.zerlegen(delta)
        rest = self.bauer.uebertragung.uebertragen(rest_dm * self.bauer.METER)
        basis = np.asarray(G9basisnetz.holen().punkte, dtype=np.float64)
        zentrum = G9aehnlichkeit.zentrum(float(basis[:, 1].min()), unter)
        return (s - 1.0) * (basis - zentrum) + rest, rest, s, unter, zentrum

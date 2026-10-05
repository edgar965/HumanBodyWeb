# -*- coding: utf-8 -*-
u"""G9hbschuhpassung — ein Daz-Schuh als GANZES an den HumanBody-Fuss (05.10.2026).

WARUM (Edgar, 05.10.2026: „Angie_Sneakers passt nicht auf Modell F2_ShirtLeggins, große Zehe geht durch den Schuh“, danach „nichts
geändert“): `G9aufhumanbody.uebertragen` setzt jeden Punkt einzeln ueber die Rahmen oder die Verschiebung der naechsten Koerperpunkte —
fuer Stoff richtig, fuer einen Schuh nicht. Gemessen an F2_ShirtLeggins (`_wegwerf/edgar/schuh_ueberstand.py`, linker Schuh): Genesis
roh Kappe und Sohle gleich weit vorn (−0,3 mm); nach der Uebertragung steht die Kappe 3,9 mm VOR der Sohle, nach dem Heben aus der Haut
4,9 mm — der HumanBody-Fuss ist laenger (Zehe 231 mm), die Spitze des Schuhs lag bei 211–221 mm, und `hinaus` schob Sohle und Kappe
unterschiedlich weit nach vorn. Die dunkle Kappe ragt dann als Zehenform ueber die weisse Sohle hinaus.

Ein Schuh ist ein fester Koerper: Er wird mit EINER affinen Abbildung vom Genesis-Fuss auf den HumanBody-Fuss gelegt (kleinste Quadrate
ueber die gepaarten Fusspunkte der Paarung, `paarung['zu']`), Sohle und Kappe behalten ihre Lage zueinander. Hoeher als `VOLL_BIS` ueber
dem Boden (Stiefelschaft) geht die Passung in die Punkt-fuer-Punkt-Uebertragung ueber (`AUS_AB`), `hinaus` hebt den Rest aus der Haut.
"""
import numpy as np

__all__ = ['G9hbschuhpassung']


class G9hbschuhpassung:
    u"""`passen(traeger, punkte, bindung)` -> (M, 3) Schuhpunkte auf der HumanBody-Figur."""

    #: Genesis-Punkte des Fusses fuer die Abbildung: unter dieser Hoehe (Knoechel), Meter.
    FUSS_HOEHE = 0.08
    #: Bis hierher (Hoehe des Schuhpunkts auf Genesis) gilt die Passung ganz, bis `AUS_AB` nimmt sie linear ab.
    VOLL_BIS = 0.10
    AUS_AB = 0.20
    #: Seitenabstand von der Mitte: weiter innen ist es kein Fuss mehr.
    SEITE_AB = 0.02
    MINDESTPUNKTE = 200
    #: Ausreisser der Paarung (Abstand zur Abbildung ueber diesem Vielfachen des Medians) fliegen einmal raus.
    AUSREISSER = 3.0
    #: Groesster Hub eines unterteilten Punkts (Meter) und Nachbarn fuer die Glaettung des Hubs (`heben`).
    HUB_MAX = 0.006
    GLAETTUNG = 12

    @classmethod
    def passen(cls, traeger, punkte, bindung=None):
        u"""Die Schuhpunkte (Genesis-Grundkoerper) auf der HumanBody-Figur: Passung des Fusses je Seite, oben die Uebertragung."""
        p = np.asarray(punkte, dtype=np.float64)
        punktweise = traeger.uebertragen(p, bindung=bindung)
        if not len(p):
            return punktweise
        gewicht = np.clip((cls.AUS_AB - p[:, 1]) / (cls.AUS_AB - cls.VOLL_BIS), 0.0, 1.0)
        fest = punktweise.copy()
        for seite in (1.0, -1.0):
            maske = (p[:, 0] * seite > 0.0) & (gewicht > 0.0)
            if not maske.any():
                continue
            abbildung = cls.abbildung(traeger, seite)
            if abbildung is None:
                gewicht[maske] = 0.0
                continue
            fest[maske] = cls.merkmale(p[maske]) @ abbildung
        gewicht[(p[:, 0] == 0.0)] = 0.0
        return gewicht[:, None] * fest + (1.0 - gewicht[:, None]) * punktweise

    @classmethod
    def heben(cls, traeger, punkte, abstand):
        u"""Die (unterteilten) Schuhpunkte aus der Haut heben — OHNE Spitzen: `traeger.hinaus` schiebt einzelne Punkte im Vorfuss
        (zwischen den Zehen) bis 27 mm weit, in beliebige Richtung (gemessen an F2_ShirtLeggins, 25 Punkte ueber 8 mm); das sind die
        Beulen auf der Kappe. Der Hub wird auf `HUB_MAX` gekuerzt und als Feld ueber `GLAETTUNG` Nachbarn geglaettet, wie
        `G9aufhumanbody.uebertragen` es mit der Verschiebung tut."""
        p = np.asarray(punkte, dtype=np.float64)
        if not len(p):
            return p
        hub = traeger.hinaus(p, abstand) - p
        laenge = np.linalg.norm(hub, axis=1)
        zu_lang = laenge > cls.HUB_MAX
        hub[zu_lang] *= (cls.HUB_MAX / laenge[zu_lang])[:, None]
        return p + traeger.geglaettet(p, hub, cls.GLAETTUNG)

    @staticmethod
    def merkmale(p):
        u"""(n, 6) Basis der Abbildung: 1, x, y, z, z², x·z — affin, dazu die Streckung der Zehen (z²) und ihr Schwenk nach innen (x·z)."""
        x, y, z = p[:, 0], p[:, 1], p[:, 2]
        return np.stack([np.ones_like(x), x, y, z, z * z, x * z], axis=1)

    @classmethod
    def abbildung(cls, traeger, seite):
        u"""(6, 3) Abbildung Genesis-Fuss -> HumanBody-Fuss dieser Seite (+1 = links, x > 0), None ohne genug Paare."""
        paar = traeger.paarung
        g9 = np.asarray(paar['g9_punkte'])
        zu = np.asarray(paar['zu'])
        wahl = (g9[:, 1] < cls.FUSS_HOEHE) & (g9[:, 0] * seite > cls.SEITE_AB) & (zu >= 0)
        if int(wahl.sum()) < cls.MINDESTPUNKTE:
            return None
        von = cls.merkmale(g9[wahl])
        nach = np.asarray(traeger.figur()['punkte'])[zu[wahl]]
        abb = np.linalg.lstsq(von, nach, rcond=None)[0]
        rest = np.linalg.norm(von @ abb - nach, axis=1)
        behalten = rest <= cls.AUSREISSER * max(float(np.median(rest)), 1e-6)
        if int(behalten.sum()) >= cls.MINDESTPUNKTE:
            abb = np.linalg.lstsq(von[behalten], nach[behalten], rcond=None)[0]
        return abb

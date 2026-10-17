# -*- coding: utf-8 -*-
"""Meshfigurhalter — welche Hand hält einen Bestandteil des Netzes? Aus dem NETZ, nicht aus der Lage der Figurhand (14.10.2026).

Anlass: Am Zauberer fand `Blendimportrequisit.erkennen` den Stab einmal an `r_hand` (Lauf `…23.18.43`, Handmitte 42 mm von der Stabachse), einmal am Unterarm (Lauf `…01.44.31`, 82 mm) — derselbe Stab, dasselbe Netz. Die Hand der Figur ist in der Anpassung
kaum festgelegt (Handfläche Gewicht 0,1, Finger 0,0): zwei Läufe stellten sie um 5,2 cm (Median, größter 8,2 cm) verschieden, der ganze Käfig stimmte auf 2,1 mm. Wer „nächstes Körperteil“ fragt, bekommt je nach Lauf Hand oder Unterarm, und der Griff,
der Stab in der Ruhelage und seine Bindung an die Hand hingen daran.

Hier entscheidet das Netz: Flächen, die Sapiens als Hand sieht (`Left_Hand`/`Right_Hand`, beide Etiketten — am Zauberer trugen 2.005 Flächen der rechten Hand das linke), und die den Bestandteil berühren (Mitte der Fläche höchstens `NAH_M` von einem
Punkt des Bestandteils: am Zauberer-Stab 4.338 Handflächen binnen 4 cm der Achse). Ab `MIN_FLAECHEN` berührten Handflächen gilt der Bestandteil als gehalten; ihre Mitte (`zentrum`) ist, wo die echte Faust liegt. Die Seite ist die Figurhand, die dieser Mitte am nächsten ist
(höchstens `MAX_ENTFERNUNG_M`). `stabfoermig` (längste durch zweitlängste Ausdehnung ab `STAB_VERHAELTNIS`): Stab, Schwert, Schirm hängen an der Schwerkraft (Ruhelage: `Blendimportrequisit.ruhelage_gehalten`), ein Schild nicht.
"""

import numpy as np

__all__ = ['Meshfigurhalter']


class Meshfigurhalter:
    #: Sapiens (Goliath, `sapiens_klassen`): `Left_Hand` 5, `Right_Hand` 14 — beide gelten für jede Seite.
    HAND_KLASSEN = (5, 14)
    MIN_STIMMEN = 4.0
    #: Eine Handfläche berührt den Bestandteil, wenn ihre Mitte so nah (m) an einem seiner Punkte liegt.
    NAH_M = 0.03
    #: Weniger berührte Handflächen sind ein Zufall (Zauberer-Stab: 4.338 binnen 4 cm).
    MIN_FLAECHEN = 300
    #: Die Seite ist die Figurhand, die der Mitte der berührenden Handflächen am nächsten liegt, aber höchstens so weit entfernt (m): die Hand der Anpassung steht bis zu 25 cm neben der Netzhand (Zauberer).
    MAX_ENTFERNUNG_M = 0.35
    #: Längste durch zweitlängste Ausdehnung (Hauptachsen der Punkte): der Zauberer-Stab 1,73 m × 6 cm.
    STAB_VERHAELTNIS = 4.0

    @classmethod
    def haendeflaechen(cls, klassen):
        """(F,) bool — die Flächen, die Sapiens als Hand sieht (beide Etiketten, mindestens `MIN_STIMMEN` Pixel); `klassen` (F, 28) Stimmen oder None."""
        if klassen is None:
            return None
        return (klassen.max(axis=1) >= cls.MIN_STIMMEN) & np.isin(klassen.argmax(axis=1), cls.HAND_KLASSEN)

    @classmethod
    def pruefen(cls, scan, klassen, bestandteil, haende):
        """`{seite, zentrum, flaechen, stabfoermig}` oder `None`. `scan` mit `punkte`/`flaechen` (Lage des Netzes), `klassen` (F, 28) Sapiens-Stimmen, `bestandteil` (P, 3) Punkte des Bestandteils,
        `haende` `{'r': (3,), 'l': (3,)}` — die Handmitten der Figur in der Haltung."""
        from scipy.spatial import cKDTree

        flaechen, punkte = np.asarray(scan.flaechen), np.asarray(scan.punkte)
        gesehen = cls.haendeflaechen(klassen)
        if not gesehen.any() or not len(bestandteil):
            return None
        mitten = punkte[flaechen[gesehen]].mean(axis=1)
        abstand, _ = cKDTree(np.asarray(bestandteil)).query(mitten, workers=-1)
        beruehrt = abstand < cls.NAH_M
        if int(beruehrt.sum()) < cls.MIN_FLAECHEN:
            return None
        zentrum = mitten[beruehrt].mean(axis=0)
        seite, naechste = None, cls.MAX_ENTFERNUNG_M
        for s, mitte in haende.items():
            d = float(np.linalg.norm(np.asarray(mitte) - zentrum))
            if d < naechste:
                seite, naechste = s, d
        if seite is None:
            return None
        return {'seite': seite, 'zentrum': [round(float(x), 4) for x in zentrum], 'flaechen': int(beruehrt.sum()), 'stabfoermig': cls.stabfoermig(bestandteil)}

    @classmethod
    def stabfoermig(cls, punkte):
        """Ist der Gegenstand lang und dünn (Stab, Schwert, Schirm)?"""
        p = np.asarray(punkte, dtype=np.float64)
        if len(p) < 10:
            return False
        s = np.linalg.svd(p - p.mean(axis=0), compute_uv=False)
        return bool(s[1] > 0 and s[0] / s[1] >= cls.STAB_VERHAELTNIS)

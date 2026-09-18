# -*- coding: utf-8 -*-
"""Netzmasse — Punkte, Vierecke und Dreiecke auf EINE Vergleichsgröße bringen.

Edgar (17.09.2026): „ich verstehe die Tabelle nicht: einmal Punkte, einmal
Vierecke, einmal Dreiecke? Mach irgendetwas, mit dem man alles vergleichen
kann" — „mach getrennte Spalten für die Punkte, Vierecke".

Die Hersteller nennen, was ihnen passt: Punkte (VFace, Daz), Vierecke
(3D Scan Store), Dreiecke (Triplegangers, UMA, SMPL) oder „Polygone" (Eisko).
Vergleichbar wird das über die **Dreieckszahl**: Ein Viereck sind zwei
Dreiecke, und in einem geschlossenen Vierecknetz gibt es etwa so viele
Flächen wie Punkte (Euler: F ≈ V), also Dreiecke ≈ 2 × Punkte. Was so
abgeleitet ist, trägt ein „≈" — gegebene Zahlen stehen ohne.

Eine Zeile bringt die rohen Angaben mit (`punkte`, `vierecke`, `dreiecke`,
jeweils Basisnetz oder None; `stufen` = Zahl der Unterteilungen; `hoechste`
+ `hoechste_einheit`, wenn der Hersteller die oberste Stufe selbst beziffert)
und bekommt hier `basis_*`-Texte, `basis_dreiecke`, `hoechst_dreiecke` und
`hoechst_text` dazu. Jede Unterteilung vervierfacht die Flächen.
"""

__all__ = ["Netzmasse"]


class Netzmasse:
    #: Faktor auf Dreiecke je Einheit, in der ein Hersteller zählt.
    FAKTOR = {"dreiecke": 1, "polygone": 1, "vierecke": 2, "punkte": 2}

    @staticmethod
    def zahl(n):
        """1234567 → „1.234.567" (deutsche Tausenderpunkte)."""
        return "{:,}".format(int(n)).replace(",", ".")

    @classmethod
    def basis_dreiecke(cls, z):
        """Dreiecke des Basisnetzes: gegeben, sonst aus Vierecken, sonst aus
        Punkten. Liefert (Zahl, abgeleitet?) oder (None, False)."""
        if z.get("dreiecke") is not None:
            return z["dreiecke"], False
        if z.get("vierecke") is not None:
            return z["vierecke"] * 2, True
        if z.get("punkte") is not None:
            return z["punkte"] * 2, True
        return None, False

    @classmethod
    def hoechst_dreiecke(cls, z):
        """Dreiecke der höchsten Stufe: vom Hersteller beziffert, sonst
        Basis × 4 je Unterteilung, sonst die Basis selbst."""
        if z.get("hoechste") is not None:
            faktor = cls.FAKTOR[z.get("hoechste_einheit", "dreiecke")]
            return z["hoechste"] * faktor, faktor != 1
        basis, abgeleitet = cls.basis_dreiecke(z)
        if basis is None:
            return None, False
        stufen = z.get("stufen") or 0
        return basis * 4**stufen, abgeleitet or stufen > 0

    @classmethod
    def text(cls, n, abgeleitet):
        if n is None:
            return "–"
        return ("≈ " if abgeleitet else "") + cls.zahl(n)

    @classmethod
    def ergaenzen(cls, z):
        """Die Zeile um Texte und Sortierschlüssel ergänzt (neue Kopie)."""
        punkte, vierecke = z.get("punkte"), z.get("vierecke")
        basis, basis_ab = cls.basis_dreiecke(z)
        hoechst, hoechst_ab = cls.hoechst_dreiecke(z)
        return dict(
            z,
            stufen=z.get("stufen") or 0,
            basis_punkte_text=cls.text(punkte if punkte is not None else vierecke, punkte is None),
            basis_vierecke_text=cls.text(
                vierecke if vierecke is not None else (punkte if z.get("dreiecke") is None else None),
                vierecke is None,
            ),
            basis_dreiecke=basis,
            basis_dreiecke_text=cls.text(basis, basis_ab),
            hoechst_dreiecke=hoechst,
            hoechst_text=cls.text(hoechst, hoechst_ab),
            stufen_text=z.get("stufen_text")
            or (
                "%d Unterteilung%s" % (z["stufen"], "" if z["stufen"] == 1 else "en")
                if z.get("stufen")
                else "keine"
            ),
        )

    @classmethod
    def rangfolge(cls, zeilen):
        """Alle Zeilen ergänzt, absteigend nach `hoechst_dreiecke`; Rang 1..n
        für Zeilen mit Zahl und ohne `ohne_rang`-Grund, die übrigen am Ende
        mit `rang` None. Gleiche Dichte behält die Reihenfolge der Liste."""
        fertig = [cls.ergaenzen(z) for z in zeilen]
        mit = [z for z in fertig if z["hoechst_dreiecke"] is not None and not z.get("ohne_rang")]
        ohne = [z for z in fertig if z not in mit]
        mit.sort(key=lambda z: -z["hoechst_dreiecke"])
        for rang, z in enumerate(mit, 1):
            z["rang"] = rang
        for z in ohne:
            z["rang"] = None
        return mit + ohne

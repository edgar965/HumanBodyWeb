# -*- coding: utf-8 -*-
"""Blendimportschamhoehe — wie hoch steht jeder Punkt des Genital-Stücks über der Haut der Figur? (10.10.2026)

Die Regler des Penis (`G9penismorphe`) müssen wissen, WAS am Stück Anbau ist (Penis, Hoden) und was Haut. Aus der Form des Stücks allein
ließ sich das nicht lesen: Das Stück der BodyParts3D-Haut ist ein Sattel um den Schritt (20 cm tief), eine Ausgleichsebene durch seinen Rand
liegt quer (Normale entlang x, gemessen 10.10.2026). Beim Import ist die Antwort bekannt — der Abstand jedes Stückpunkts zur Figurfläche —
und wird mit dem Stück abgelegt (`G9stueckersatz.schreiben(hoehe_mm=…)`).

VORZEICHEN: plus = vor der Figurfläche (außen), minus = dahinter (das Stück liegt bis 25 mm HINTER der Haut, `Blendimportscham.HAUT_TIEFE_MM`).
Die Richtung der Flächennormalen entscheidet; sie gilt nicht als gegeben: stünden die Punkte, die mehr als `SICHER_MM` von der Fläche weg sind,
überwiegend „hinter" ihr, ist die Fläche nach innen gewickelt und das Vorzeichen wird für alle gedreht.
"""
import numpy as np

__all__ = ['Blendimportschamhoehe']


class Blendimportschamhoehe:
    #: Ab dieser Entfernung (mm) zählt ein Punkt für die Prüfung der Wicklung.
    SICHER_MM = 8.0

    @classmethod
    def ueber_figur(cls, punkte, flaeche):
        """`(N,)` Höhe (mm, mit Vorzeichen) jedes Punkts über der Figurfläche `flaeche` (trimesh, Ruhelage); Punkte in Metern."""
        import trimesh

        p = np.asarray(punkte, dtype=np.float64)
        nah, abstand, dreieck = trimesh.proximity.closest_point(flaeche, p)
        vorzeichen = np.sign(((p - nah) * flaeche.face_normals[dreieck]).sum(axis=1))
        vorzeichen[vorzeichen == 0.0] = 1.0
        hoehe = abstand * 1000.0 * vorzeichen
        weit = np.abs(hoehe) > cls.SICHER_MM
        if int(weit.sum()) and float(np.sign(hoehe[weit]).mean()) < 0.0:
            hoehe = -hoehe
        return hoehe

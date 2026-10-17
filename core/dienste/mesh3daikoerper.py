# -*- coding: utf-8 -*-
"""Mesh3daikoerper — die Zeile „Nur Körper (ohne Kleider)“ der ATTRAPPE auf der Seite „Mesh3D-AI“ (14.10.2026).

Edgar: „eine neue Zeile (zweite Zeile von oben): NUR Körper (also ohne Kleider).“ Die Aufgabe dieser Zeile ist die schwerste: aus der Außenfläche MIT Kleidern den Körper darunter zu finden. Die Eingabe ist deshalb dieselbe wie in der
Zeile „Ganzer Körper“ (Außenfläche mit Stoff, Seite zeichnet sie aus den Daten des ganzen Körpers), gewünscht ist die nackte Figur in der Pose, nur Haut. Hier ist alles erfunden: dieselben 22 Gelenke wie das Dummy-Gerüst (`Mesh3daigeruest`), alle in Hautfarbe,
dünner als mit Kleidern, mit mehr Rauschen als beim ganzen Körper (unter weiter Kleidung ist der Körper schwerer zu finden — eine Annahme für die Attrappe, keine Messung). KEIN Genesis-Körper.

    Mesh3daikoerper.beschreibung()                         -> {titel, punkte: [{name, gruppe, eltern, radius, farbe, textur}], fehler_rot_mm, schwelle_mm}
    Mesh3daikoerper.soll(winkel, lagen, drehungen, zufall) -> {soll: [[x, y, z]…]}
"""

from .mesh3daigeruest import Mesh3daigeruest

__all__ = ['Mesh3daikoerper']


class Mesh3daikoerper:
    SCHLUESSEL = 'koerper_nackt'
    TITEL = 'Nur Körper (ohne Kleider)'
    FEHLER_ROT_MM = 50
    SCHWELLE_MM = 10
    #: Rauschen des Dummy-„Netzes“ in m (Training / Prüfposen): mehr als beim ganzen Körper, weil der Stoff den Körper verdeckt.
    RAUSCHEN = {'training': 0.005, 'pruefung': 0.020}
    EINGABE_PUNKTE = 4096
    HAUT = 0xE0B394
    #: Dicke der Haut-Kapsel am Gelenk (m): nach Name, sonst nach Gruppe — wie die Kapseln des ganzen Körpers (Seite, `Mesh3daikapseln`), aber ohne Stoffdicke.
    RADIUS_NAME = {'Scheitel': 0.080, 'Kopf': 0.048, 'Hals': 0.042, 'Brust': 0.105, 'Bauch': 0.092}
    RADIUS_GRUPPE = {'rumpf': 0.090, 'kopf': 0.048, 'arm': 0.034, 'hand': 0.028, 'bein': 0.058, 'fuss': 0.036}

    @classmethod
    def beschreibung(cls):
        punkte = []
        for name, eltern, _versatz, gruppe in Mesh3daigeruest.GELENKE:
            punkte.append({'name': name, 'gruppe': gruppe, 'eltern': Mesh3daigeruest.index(eltern) if eltern else -1,
                           'radius': cls.RADIUS_NAME.get(name, cls.RADIUS_GRUPPE[gruppe]), 'farbe': cls.HAUT, 'textur': 'haut'})
        return {'titel': cls.TITEL, 'punkte': punkte, 'fehler_rot_mm': cls.FEHLER_ROT_MM, 'schwelle_mm': cls.SCHWELLE_MM}

    @classmethod
    def soll(cls, winkel, lagen, drehungen, zufall):
        """Die Gelenke der Pose — dieselben Lagen wie beim ganzen Körper; Haut und Stoff teilen das Gerüst."""
        return {'soll': [[round(w, 4) for w in lage] for lage in lagen]}

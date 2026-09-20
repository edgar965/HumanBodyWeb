# -*- coding: utf-8 -*-
"""Bildmodellbildvorgaben — die Wahl je Bild, die schon beim Hochladen mitkommt.

Aus `Bildmodellbildtypen` herausgelöst (20.09.2026, die Datei stand bei 315
Zeilen): das Upload-Feld `typen` (JSON, `{datei: {haupt, neben, nutzung,
kamera}}`) — die Testfallbilder und „Bild für die Textur" kennen ihren Typ,
bevor die Sichtung läuft — und die bekannte Kamera eines gerenderten
Testfallbilds. Die Werte selbst definiert `Bildmodellbildtypen`.
"""

from .bildmodellbildtypen import Bildmodellbildtypen

__all__ = ['Bildmodellbildvorgaben']


class Bildmodellbildvorgaben:

    @classmethod
    def pruefen(cls, roh, namen):
        """`{datei: {haupt, neben, nutzung}}` aus dem Upload-Feld `typen` (JSON) — nur für
        die eben abgelegten Dateien, nur bekannte Werte (19.09.2026: die Testfallbilder und
        „Bild für die Textur" kennen ihren Typ, bevor die Sichtung läuft)."""
        import json

        if not roh:
            return {}
        try:
            daten = json.loads(roh) if isinstance(roh, str) else roh
        except ValueError:
            return {}
        if not isinstance(daten, dict):
            return {}
        T = Bildmodellbildtypen
        haupt = {w for w, _, _, _ in T.HAUPT}
        neben = {w for w, _, _, _, _ in T.NEBEN} | {w for w, _, _, _ in T.HAUPTBILD}
        nutzung = {w for w, _, _ in T.NUTZUNG}
        aus = {}
        for name in namen:
            wahl = daten.get(name)
            if not isinstance(wahl, dict):
                continue
            sauber = {}
            if wahl.get('haupt') in haupt:
                sauber['haupt'] = wahl['haupt']
            if wahl.get('neben') in neben:
                sauber['neben'] = wahl['neben']
            if wahl.get('nutzung') in nutzung:
                sauber['nutzung'] = wahl['nutzung']
            kamera = cls.kamera(wahl.get('kamera'))
            if kamera:
                sauber['kamera'] = kamera
            if sauber:
                aus[name] = sauber
        return aus

    @staticmethod
    def kamera(roh):
        """Die bekannte Kamera eines gerenderten Testfallbilds (`Testfallbilder._kameraDaten`):
        Weltmatrix der Kamera und der Figur (16 Zahlen, spaltenweise wie three.js), Öffnungswinkel
        (Grad, senkrecht), Bildgröße — oder None, wenn etwas fehlt oder keine Zahl ist."""
        if not isinstance(roh, dict):
            return None
        try:
            matrix = [float(v) for v in roh.get('matrix') or []]
            figur = [float(v) for v in roh.get('figur') or [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]]
            fov, breite, hoehe = float(roh.get('fov')), int(roh.get('breite')), int(roh.get('hoehe'))
        except (TypeError, ValueError):
            return None
        if len(matrix) != 16 or len(figur) != 16 or not (1.0 <= fov <= 170.0) or breite < 8 or hoehe < 8:
            return None
        return {'matrix': matrix, 'figur': figur, 'fov': fov, 'breite': breite, 'hoehe': hoehe}

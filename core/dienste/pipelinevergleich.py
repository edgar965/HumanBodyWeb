# -*- coding: utf-8 -*-
u"""Pipelinevergleich — alle Video-nach-BVH-Pipelines mit Messwerten und Rang.

Die Seite Hilfe -> Video to BVH zeigt diese Daten; die Vorlage rechnet
nichts. Die Zahlen stammen aus EINEM Lauf aller Pipelines auf demselben
Video (`MESSUNG`), ausgefuehrt ueber die Web-API — genau der Weg des
Knopfs „Process". Die Eintraege selbst stehen nach Familie getrennt in
`pipelinevergleich_3d.Pipelines3d` und `pipelinevergleich_2d.Pipelines2d`
(Dateigrenze 300 Zeilen).

Die Anzeigenamen kommen aus `BVHJob.PIPELINE_CHOICES`, nicht aus den
Eintraegen: Sonst hiesse dieselbe Pipeline hier und in der Auftragsliste
irgendwann verschieden (so geschehen in den Uploadvorlagen, 28.08.2026).
"""
from ..models import BVHJob
from .pipelinevergleich_2d import Pipelines2d
from .pipelinevergleich_3d import Pipelines3d


class Pipelinevergleich:
    u"""Alle Pipelines, nach Rang sortiert, mit Anzeigenamen aus dem Modell."""

    # Dictionary gewollt: geht so in die Vorlage.
    MESSUNG = {
        'video': '001_ShyrinKurz.mp4',
        'beschreibung': 'Ballett auf einer Bühne, eine Person, statische Kamera',
        'bilder': 298, 'fps': 60, 'masse': '1280 × 720',
        'datum': '12.09.2026',
        'ordner': 'HumanBodyWeb/media/output/vergleich_001_ShyrinKurz/',
        'skripte': 'HumanBodyWeb/_wegwerf/vergleich_001/',
    }

    #: Spalte -> Bedeutung, fuer die Legende unter der Tabelle.
    SPALTEN = (
        ('Art', '2D + Lifter: ein 2D-Erkenner liefert Bildpunkte, MocapNET v2.1 hebt sie '
                'Bild für Bild nach 3D. 3D: das Verfahren schätzt den Körper direkt. '
                'Hybrid: SMPL-Körper plus Gesicht und Hände aus MocapNET v4.'),
        ('Gelenke', 'Zahl der Gelenke in der BVH-Datei (ohne Endpunkte).'),
        ('Dauer (s)', 'Wanduhrzeit des Auftrags vom Anlegen bis „complete" oder „failed", '
                      'auf diesem Rechner (RTX PRO 4500), Video 298 Bilder.'),
        ('Δ ViTPose (px)', 'Mittlerer Pixelabstand des projizierten BVH-Skeletts zu den '
                           'ViTPose-Punkten der GVHMR-Vorstufe — zwölf Gelenke (Hüften, Knie, '
                           'Knöchel, Schultern, Ellbogen, Handgelenke), nur Punkte mit '
                           'Sicherheit > 0,5, bei 1280 × 720. Kleiner ist besser.'),
        ('Ruhe Wurzel', 'Mittlere Beschleunigung der Wurzel (Hüfte) in cm je Bild², aus der '
                        'BVH-Datei. Hohe Werte sind Zittern der Kamerabahn, nicht Bewegung.'),
        ('Ruhe Pose', 'Dasselbe für alle Gelenke relativ zur Hüfte, cm je Bild² — das '
                      'Zittern der Pose selbst.'),
        ('Boden (cm)', 'Mittlere Höhe des tiefsten Gelenks. 0 heißt: die Füße stehen auf y = 0. '
                       'Stark negativ heißt: die Figur steht im Kameraraum, nicht auf einem Boden.'),
        ('Zustand', 'läuft: BVH fertig. teilweise: nur ein Teil (etwa nur das Gesicht). '
                    'gescheitert: kein BVH; der Grund steht unter der Tabelle.'),
    )

    ZUSTAND = {'laeuft': 'läuft', 'teilweise': 'teilweise', 'gescheitert': 'gescheitert'}

    FELDER = ('schluessel', 'art', 'verfahren', 'gelenke', 'haende', 'gesicht', 'kamera',
              'dauer_s', 'ueberlagerung_px', 'ruhe_wurzel', 'ruhe_pose', 'boden_cm',
              'zustand', 'zustand_grund', 'vorteile', 'nachteile', 'rang', 'begruendung')

    @classmethod
    def alle(cls):
        u"""Alle Eintraege, mit `name` aus dem Modell und `zustand_text`."""
        namen = dict(BVHJob.PIPELINE_CHOICES)
        eintraege = []
        for roh in Pipelines3d.EINTRAEGE + Pipelines2d.EINTRAEGE:
            # Dictionary gewollt: geht so in die Vorlage.
            eintrag = dict(roh)
            eintrag['name'] = namen[eintrag['schluessel']]
            eintrag['kennung'] = eintrag['schluessel']
            # Eine Variante (12.09.2026): dieselbe Pipeline mit anderer
            # Bestellung, eigene Zeile — Name und Kennung sagen, welche.
            eintrag.setdefault('variante', '')
            if eintrag['variante']:
                eintrag['name'] += ' · ' + eintrag['variante']
                eintrag['kennung'] += ' · ' + eintrag.get('variante_kennung', '')
            # Das Skelettvideo des Laufs im Vergleichsordner — Varianten und
            # Nachmessungen (gemx_s4) nennen ihres selbst.
            eintrag.setdefault('video', '%s_skelett.mp4' % eintrag['schluessel'])
            eintrag['zustand_text'] = cls.ZUSTAND[eintrag['zustand']]
            eintraege.append(eintrag)
        return eintraege

    @classmethod
    def rangfolge(cls):
        u"""Nach Rang; wer keinen hat (kein Ergebnis), steht am Ende.

        Einen Rang bekommen nur die, die ein BVH liefern (Edgar, 12.09.2026:
        „das ranking von 1-10"; seit der Neubewertung 1-12) — ein Rang fuer
        „liefert nichts" sagt nichts."""
        return sorted(cls.alle(), key=lambda e: (e['rang'] is None, e['rang'] or 0))

    @classmethod
    def mit_rang(cls):
        return [e for e in cls.alle() if e['rang'] is not None]

    @classmethod
    def nicht_gelaufen(cls):
        return [e for e in cls.rangfolge() if e['zustand'] != 'laeuft']

    @classmethod
    def schluessel(cls):
        u"""Jede Pipeline einmal, Varianten nicht doppelt."""
        return list(dict.fromkeys(e['schluessel'] for e in cls.alle()))

    @classmethod
    def grundeintraege(cls):
        u"""Die Eintraege ohne Variante — genau einer je Pipeline."""
        return [e for e in cls.alle() if not e['variante']]

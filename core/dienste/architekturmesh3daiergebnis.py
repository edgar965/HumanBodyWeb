# -*- coding: utf-8 -*-
"""Architekturmesh3daiergebnis — die Läufe von Ursula1 nebeneinander, für „Kurz erklärt“ auf Hilfe → Architektur → Mesh3DAI (16.10.2026).

Gleiche Proben in allen Läufen (50 Training, 15 Prüfposen, 125 Spagat-Bilder), Fehler = Mittel über die 138 Gelenke in mm (`maße.<gruppe>.netz_mm` in `lauf_ergebnis.json`).
Die Zahlen liest die Seite beim Aufruf aus den Läufen; fehlt ein Lauf, steht „—“. Je ein Lauf je Zeile — die Streuung von Lauf zu Lauf ist nicht gemessen.
"""

import json

from .mesh3daidatensatz import Mesh3daidatensatz

__all__ = ['Architekturmesh3daiergebnis']


class Architekturmesh3daiergebnis:
    #: (Ordner unter `_laeufe` oder `_diagnose`, was das Netz anders macht)
    LAEUFE = (
        ('2026.10.16.00.37_posen50_plan_e480', 'Ein Vektor für die ganze Figur → 138 freie Punkte (480 Epochen)'),
        ('2026.10.16.09.52_kanaele_e2400', 'Ein Vektor für die ganze Figur → Daz-Winkel (2.400 Epochen)'),
        ('2026.10.16.11.51_stimmen_e480', 'Stimmen je Punkt'),
        ('2026.10.16.11.58_stimmen_aufmerk_e480', 'Stimmen, Gewichte überwacht'),
        ('2026.10.16.12.03_stimmen_aufmerk_dreh30_e480', 'Stimmen, Gewichte überwacht, Drehung ±30° im Training'),
        ('2026.10.16.13.58_stimmen_alle4', 'wie davor, ein Netz für vier Jobs (Ursula1, Damira0, Mann1, Matt0)'),
        ('2026.10.16.15.13_stimmen_alle4_farbe_gieren', 'wie davor, Zufallsfarben + Drehung um die Hochachse bis ±180° (Gegenlauf zu den Abkürzungen)'),
    )

    @classmethod
    def zeilen(cls, modell='Ursula1', form_lauf=None):
        """`form_lauf` = jüngster Lauf mit Formkopf (`Architekturmesh3daiform.lauf()`), als letzte Zeile."""
        ordner = Mesh3daidatensatz.ordner(modell)
        aus = []
        laeufe = list(cls.LAEUFE) + ([(form_lauf.name, 'Stimmen + Formkopf, vier Jobs + 40 Formvarianten, Zufallsfarben, ±30°')] if form_lauf is not None else [])
        for name, text in laeufe:
            datei = next((o / name / 'lauf_ergebnis.json' for o in (ordner / '_laeufe', ordner / '_diagnose') if (o / name / 'lauf_ergebnis.json').is_file()), None)
            e = json.loads(datei.read_text(encoding='utf-8')) if datei else {}
            m = e.get('maße') or {}
            aus.append({'lauf': name, 'text': text, 'da': bool(datei),
                        'training': (m.get('training') or {}).get('netz_mm'), 'pruefung': (m.get('pruefung') or {}).get('netz_mm'), 'spagat': (m.get('spagat') or {}).get('netz_mm'),
                        'pruefung_median': (m.get('pruefung') or {}).get('netz_median_mm'), 'dauer_s': e.get('dauer_s'), 'parameter': e.get('parameter'), 'epochen': e.get('epochen'),
                        'daten': len(e.get('training_daten') or []) or 1})
        return aus

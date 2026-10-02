# -*- coding: utf-8 -*-
"""Architektur2d3dmessung — gemessene Dauern und offene Befunde der Iterationen von „2D3D Kleider" (02.10.2026).

Quelle der Rundenzeiten: `auftrag.log` des Auftrags 2026.10.01.20.10.04 („test3"), Lauf vom 02.10.2026 00:17–00:19,
drei automatische Runden (9–11) über die Server-API, Renderbreite 128. Ein Abschnitt reicht von einer Meldung der Runde
bis zur nächsten (`Begutachtungswerkzeug.takt`) — „Rendern 3 von 3" enthält deshalb auch Netznote, Befund und
Gesichtsmaße. Die Zahlen des Körperschritts stammen aus `ergebnis.dauer_koerper` desselben Auftrags (01.10.2026,
Summe 871,7 s), VOR Frühstopp und Frisur-Überspringen.
"""

__all__ = ['Architektur2d3dmessung']


class Architektur2d3dmessung:
    QUELLE = 'auftrag.log von 2026.10.01.20.10.04, Runden 9–11, 02.10.2026 00:17–00:19'
    #: (Abschnitt, was darin steckt, Runde 9 kalt, Runde 10, Runde 11) in Sekunden.
    RUNDE = [
        ('Modell bauen', 'Kleidermodellbau, Haarzonen, Haltung häuten, Kennfarben-Render je Blickwinkel (das Rezept '
         'der Automatik und sein Anwenden liegen davor und kosten < 0,1 s)', 44.8, 5.2, 5.3),
        ('Fotoprojektion', 'Haut aus den Fotos — einmal je Körper, danach übersprungen', 0.0, 0.0, 0.0),
        ('Rendern 1 von 3', 'Mitsuba-Render + Note; im ersten Bild der Szenenaufbau', 5.8, 2.7, 3.4),
        ('Rendern 2 von 3', 'Render + Note', 0.1, 0.1, 0.1),
        ('Rendern 3 von 3', 'Render + Note, dann Netznote, Befund, Messgüte, Gesichtsmaße '
         '(Kopf-Render 1024², 4 Saaten)', 12.2, 13.3, 12.9),
        ('ablegen', 'Tafel, Einzelbilder, Formbezug, Gesamtnote, Rundenauswahl, Ergebnis speichern', 6.2, 6.4, 7.1),
    ]
    RUNDE_GESAMT = (69.1, 27.7, 28.8)
    LAUF_GESAMT_S = 133
    ZIEL_S = '2–3'
    #: Körperschritt (vor den Änderungen vom 02.10.2026), `ergebnis.dauer_koerper` desselben Auftrags:
    #: (Teil, Sekunden, was seither geändert ist).
    FRUEHSTOPP = 'Frühstopp: hält an, wenn der Verlust über 50 Schritte um < 0,2 % fällt (vorher immer alle Schritte)'
    KOERPER = [
        ('koerper (Fit der Körpermorphs)', 217.9, FRUEHSTOPP),
        ('textur (Hautkacheln backen)', 210.1, '—'),
        ('frisur (Kandidaten messen)', 161.1, 'übersprungen, wenn Netz und Option gleich blieben'),
        ('gesicht (Fit der Gesichtsmorphs)', 152.0, FRUEHSTOPP),
        ('vorschau', 40.3, 'bleibt (die Auftragsliste zeigt sie)'),
        ('erkennung', 37.9, '—'),
        ('rest', 30.8, '—'),
        ('haar', 10.9, '—'),
        ('kleidung', 10.7, '—'),
    ]
    KOERPER_GESAMT_S = 872.0
    #: Was am 02.10.2026 schon schneller gemacht wurde — (Maßnahme, Wirkung).
    SCHON = [
        ('Teilevorrat: Kleidung und Haar je Prozess aufbewahren, solange ihr Bauplan gleich bleibt',
         'Modell bauen kalt 41,7 s → warm 0,1 s für das Modell selbst'),
        ('Keine GLB je Runde', '56 MB je Runde weniger; der Zeitanteil ist nicht getrennt gemessen'),
        ('Kein Standmodell nach reinen Runden', '20 s je Lauf weniger'),
        ('Renderbreite 128 statt 256', 'die Note rechnet ohnehin auf 128 × 192; Zeitanteil nicht getrennt gemessen'),
        ('Mund: Mimikregler beim Lesen filtern', 'statt 872 s Körper neu rechnen: 0 s'),
    ]
    #: Wo die übrigen ~27 s stecken und was als Nächstes kommt (noch nicht umgesetzt).
    NAECHSTES = [
        ('Gesichtsmaße', 'Kopf-Render 1024² mit 4 Saaten jede Runde',
         'nur rechnen, wenn sich am Kopf etwas geändert hat'),
        ('Kennfarben-Render', 'ein eigener Render je Blickwinkel nur für die Masken',
         'Masken im selben Durchgang wie das Farbbild'),
        ('Ablegen', 'Tafel und Einzelbilder auch für verworfene Runden', 'Tafel nur für übernommene Runden'),
        ('Mitsuba-Szene', 'Schlüssel ist die id der Arrays — neue Arrays je Runde bauen die Szene neu',
         'Schlüssel aus dem Inhalt der Dreiecke, nur Punkte tauschen'),
        ('Prozessstart', 'jeder Lauf ein neuer Prozess: Module laden, Vorrat kalt (Runde 9: 69 s)',
         'mehrere Runden je Lauf; ein dauerhafter Rechenprozess wäre der nächste Schritt'),
    ]
    #: Beim Schreiben der Seite gefunden (02.10.2026), noch nicht behoben.
    OFFEN = [
        ('Spalte „Abweichung" ist nicht die Gesamtnote',
         'Rundentabelle und Kurve zeigen note.abweichung (Foto + Netz); über die beste Runde entscheidet die '
         'Gesamtnote (Foto + Farbe der Teile + Gesicht), sie steht nur in der Notiz. In den Runden 9–11 stand die '
         'Abweichung bei 1,173, die Gesamtnote bewegte sich (0,3849 → 0,3830).'),
        ('Prüf-KI nicht in der Tabelle', 'Die Rundentabelle zeigt r.kritik; die Prüf-KI der Begutachtung schreibt nach '
         'kreislauf.kritiken und erscheint nur als Zusatz im Kommentar.'),
        ('„automatisch" doppelt belegt', 'Optionswert modus = automatisch (die alte Optimierer-Schleife, '
         'Iterationsrunde) gegen naechste.automatisch (Rezepte aus IterationModell im Modus „begutachtung").'),
        ('README des Ordners 2d3DIterationen veraltet', 'nennt Morph-Deckel ±2 (Code 1,0), Frisurwechsel nach 3 Runden '
         '(Code: aus) und die Haltung als Rücknahme auf die A-Pose (Code: folgt den Fotos).'),
        ('kreislauf.glb',
         'steht auf modell.glb, obwohl keine Runden-GLB mehr entsteht; gebaut wird sie erst beim Export.'),
    ]

    @classmethod
    def kontext(cls):
        return {
            'quelle': cls.QUELLE,
            'runde': [{'abschnitt': a, 'was': w, 'werte': (r9, r10, r11)} for a, w, r9, r10, r11 in cls.RUNDE],
            'runde_gesamt': cls.RUNDE_GESAMT,
            'lauf_gesamt': cls.LAUF_GESAMT_S,
            'ziel': cls.ZIEL_S,
            'koerper': [{'teil': t, 'sekunden': s, 'seither': g} for t, s, g in cls.KOERPER],
            'koerper_gesamt': cls.KOERPER_GESAMT_S,
            'schon': [{'massnahme': m, 'wirkung': w} for m, w in cls.SCHON],
            'naechstes': [{'wo': a, 'warum': b, 'was': c} for a, b, c in cls.NAECHSTES],
            'offen': [{'was': a, 'befund': b} for a, b in cls.OFFEN],
        }

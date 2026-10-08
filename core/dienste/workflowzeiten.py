# -*- coding: utf-8 -*-
"""Workflowzeiten — die gemessenen Dauern des Workflow-Reiters, jede mit ihrer Quelle (Hilfe → Architektur → 2D3D, 02.10.2026).

Edgar: „Infos, was jeder Schritt kostet an Zeit". Gelesen am 02.10.2026 aus der Datenbank (`Engine2d3dKleiderauftrag.ergebnis`:
`dauer`, `dauer_koerper`, `iterationen[].sekunden`) und aus dem `auftrag.log` des Auftrags 2026.10.01.20.10.04; die
Abschnittszeiten der Runden stehen dort als „<x> s Runde <n>: <Abschnitt>". Was nicht gemessen ist, hat `Workflowzeit()` ohne
Wert und erscheint als „nicht gemessen". Fremde Zahlen (Regeldateien, Klassenkommentare) tragen die Fundstelle als Quelle.
"""

from .architektur2d3dmessung import Architektur2d3dmessung
from .workflowzeit import Workflowzeit as Z

__all__ = ['Workflowzeiten']


class Workflowzeiten:
    DB = 'Datenbank, ergebnis.dauer der Aufträge 2026.09.30.21.02.25 – 2026.10.01.20.10.04 (gelesen 02.10.2026)'
    LOG = 'auftrag.log von 2026.10.01.20.10.04, Abschnitte „<s> s Runde <n>: …"'
    OPT = 'Optionstexte im Code (Meshoptionen, Iterationsoptionen) — nicht nachgemessen'
    NOTE = 'Regeldatei ortsmorphe.md (30.09.2026) — Messung der Parallelsitzung'
    ROUNDTRIP = 'Stoffsolver/werkzeug/_vergleich/roundtrip/*_blender.json (lauf_s), 02.10.2026'
    ZEITEN = ('Stoffsolver/README.md, Abschnitt „Messungen" (02.10.2026): werkzeug/blender_zeiten.py, Median von 2–3 abwechselnden '
              'Läufen als eigener Prozess über denselben Auftrag, Z oben, nichts angeheftet')
    #: Voller Lauf vom 06.10.2026 (Pipeline-Test der Parallelsitzung auf der Kopie von „Sapiens 3", ab Schritt vorbereitung, alle Schritte neu).
    NEULAUF = 'Datenbank, ergebnis.dauer des Auftrags 2026.10.06.14.10.22 (voller Lauf, gelesen 06.10.2026 14:41)'
    #: Zwei Runden desselben Laufs mit dem Stand vom 06.10.2026 (Iteration 0 und eine automatische Runde, Prozess kalt).
    SAP4 = 'auftrag.log von 2026.10.06.00.33.38 („Edgar - Sapiens 4"), Runden 0 und 1 (06.10.2026)'

    # ------------------------------------------------------------------ Lauf (je Auftrag einmal)
    VORBEREITUNG = Z(55.9, quelle=NEULAUF, hinweis='BiRefNet laden, Freistellen und Zuschnitt je Foto, Licht ausgleichen; ein Lauf')
    SEGMENTIERUNG = Z(
        23.0,
        30.0,
        'Auftrag 2026.10.01.20.10.04, Schritt allein gestartet, zwei Läufe (23 s und 30 s Auftragszeit), 3 Fotos, 94.970 Flächen, 04.10.2026',
        'optional (segmentierung.verwenden); Sapiens-1B laden (rund 7 s), je Foto segmentieren, Netz je Ansicht rastern und abstimmen. Beim ersten Lauf kommen die 4,7 GB '
        'Gewichte dazu (Download ~6 min bei 11 MB/s, nicht im Auftrag gemessen)',
    )
    #: Der Kopf-Lauf (07.10.2026) ist noch in keinem vollen Auftrag gelaufen — keine Zahl statt einer geschätzten (der Kopflauf vom 27.09.2026, `…13.23.11`, brauchte 798 s, aber aus EINEM Foto und ohne Ausschnitt).
    KOPF = Z(hinweis='optional (kopf.rechnen); drei Kopfausschnitte schneiden (CPU, unter 1 s je Foto gemessen), dann Hunyuan3D-2mv mit Texturmalerei auf 300.000 Flächen — am 07.10.2026 noch nicht gerechnet')
    NETZ = Z(
        384.3,
        752.6,
        DB + ': 8 Aufträge, 7 verschiedene Werte (alle TRELLIS.2); dazu ' + NEULAUF + ': 384,3 s (hoch, Textur ki, 100.000 Flächen)',
        'je nach Auflösung, Textur und Flächenzahl',
    )
    NETZ_SCHNELL = Z(466.9, quelle=DB + ': …21.02.25, Auflösung schnell, Textur fotos_ki, 500.000 Flächen')
    NETZ_HOCH_FOTOSKI = Z(428.3, quelle=DB + ': …22.03.11, Auflösung hoch, Textur fotos_ki, 500.000 Flächen')
    NETZ_HOCH_KI = Z(
        384.3, 752.6, DB + ': vier Läufe, Auflösung hoch, Textur ki (100.000 oder 500.000 Flächen); ' + NEULAUF + ': 384,3 s (100.000 Flächen)'
    )
    NETZ_HOCH_FOTOS = Z(705.1, quelle=DB + ': …23.16.52, Auflösung hoch, Textur fotos, 500.000 Flächen')
    NETZ_FOTOSKI = Z(
        428.3,
        466.9,
        DB + ': …22.03.11 (hoch, 428,3 s) und …21.02.25 (schnell, 466,9 s), beide 500.000 Flächen',
    )
    #: Die sechs Schritte vor den Iterationen des Auftrags 2026.10.06.14.10.22: 55,9 + 384,3 + 28,0 + 877,0 + 1,7 + 297,9 s (= 1.644,8 s; Test `test_der_aufbau_der_zeitleiste…`).
    AUFBAU = Z(1644.8, quelle=NEULAUF + ' — vorbereitung 55,9 s + netz 384,3 s + segmentierung 28,0 s + koerper 877,0 s + grundfigur 1,7 s + kleiderstuecke 297,9 s')
    KOERPER_UEBERNEHMEN = Z(0.0, quelle=DB + ': …21.02.25, Quelle uebernehmen (auf 0,1 s gerundet)')
    KOERPER_RECHNEN = Z(694.8, 984.1, DB + ': 6 Aufträge mit Quelle rechnen, 5 verschiedene Werte')
    GRUNDFIGUR = Z(1.7, 2.3, DB + ': 7 Aufträge')
    KLEIDERSTUECKE = Z(
        47.2,
        297.9,
        'Auftrag 2026.10.04.11.11.44, 04.10.2026: Schritt allein 47,2 s (ergebnis.dauer, Stücke schon gebaut und gemerkt: bauen 0 s, messen samt Bibliotheks-Anker 47,2 s); '
        'Obergrenze = ' + NEULAUF + ': 297,9 s im vollen Lauf (Log: „bauen 248 s, messen 50 s"); davor als Obergrenze 212,4 s = 47,2 s + 165,2 s '
        '(Fotostuecke.holen() allein, zweiter von zwei Läufen mit 140,6 s und 165,2 s, getrennt gemessen — Summe zweier Messungen, nicht als ein Lauf)',
        'Fotostücke bauen (beim ersten Mal), Stücknote messen, danach das Standmodell für die Bühne (21,8 s warm, 51,1 s kalt; steht im Band „Modell des Stands“, nicht in der Schrittzeit)',
    )
    EXPORT = Z(1.8, 3.4, DB + ': 5 Aufträge')
    FILM = Z(
        34.1,
        357.7,
        DB + ': …21.02.25 (34,1 s), …14.08.48 (41,0 s), …12.38.09 (69,4 s); ' + NEULAUF + ': 357,7 s',
        'film.bilder 10, 320 × 480 px in den ersten drei Aufträgen, 300 Bilder im Lauf …14.10.22; ohne BVH-Datei übersprungen',
    )
    SPEICHERN = Z(0.0, 0.4, DB + ': …21.02.25 (0,0 s), …14.08.48 (0,4 s)')
    KEINE = Z()

    # ------------------------------------------------------------------ eine Runde
    #: Runden 10–11 (02.10.2026 00:18): zweite und dritte Runde EINES Laufs — der Vorrat ist warm.
    WARM = LOG + ', Runden 10–11 (00:18, zweite und dritte Runde eines Laufs)'
    #: Runden 20–23 (02.10.2026 09:42–09:55): je Lauf eine Runde — Prozess und Vorrat kalt.
    KALT = LOG + ', Runden 20–23 (09:42–09:55, je Lauf eine Runde)'
    LAUFANFANG = Z(
        6.3,
        8.2,
        'Dauer des Laufs („wartet/fertig in … s") minus Summe der Abschnitte, Runden 20–22 (' + LOG + ')',
        'Prozess starten, Vorlagen laden, Haltung der Fotos, Startmodell, Rezept anwenden; mit den '
        'Haar-Morphen des Rezepts von Runde 23: 21,5 s',
    )
    REZEPT = Z(
        0.1,
        quelle=Architektur2d3dmessung.QUELLE,
        hinweis='Rezept der Automatik schreiben und anwenden',
        unter=True,
    )
    BAUEN_WARM = Z(5.2, 5.3, WARM)
    BAUEN_KALT = Z(36.6, 62.4, KALT + '; dazu ' + SAP4 + ': 36,6 s (Runde 0) und 49,5 s (Runde 1)')
    FOTOPROJEKTION_NICHT = Z(
        0.0, quelle=WARM + ' und ' + KALT, hinweis='Haut ist einmal je Körper projiziert'
    )
    FOTOPROJEKTION_STUECK = Z(16.0, 43.7, LOG + ', Runden 17–19; ' + SAP4 + ': 36,8 s (Runde 1, Hose und Hemd); ' + NEULAUF + ' (Log): 43,7 s in Iteration 0 (die Haut erstmals je Körper, kein Stück gewünscht)',
                              'Stücke auf Wunsch (kleid_fototextur); die Haut je Körper einmal; seit 06.10.2026 zählt auch das Seitenfoto')
    RENDERN_1 = Z(8.7, 11.8, KALT + '; ' + SAP4 + ': 9,0 s und 11,8 s', 'im ersten Bild der Szenenaufbau (warm: 2,7–3,4 s)')
    RENDERN_2 = Z(0.1, 0.3, WARM + ' und ' + KALT + '; ' + SAP4)
    RENDERN_3 = Z(6.7, 14.7, KALT + '; ' + SAP4 + ': 6,7 s und 9,6 s', 'danach Netznote, Befund, Messgüte, Gesichtsmaße (warm: 12,9–13,3 s); der Belichtungsabgleich (06.10.2026) liegt zwischen den Bildern')
    PRUEFBILDER = Z(21.1, 33.4, KALT + '; ' + SAP4 + ': 22,8 s und 33,1 s; ' + NEULAUF + ' (Log): 33,4 s', 'Kopftafel in Prüfbreite (die Vergleichstafel entsteht im Abschnitt ablegen, Begutachtungsrunde._ablegen); vor Runde 20 7,7–12,9 s')
    ABLEGEN = Z(5.9, 14.5, KALT + '; ' + SAP4 + ': 9,1 s und 14,5 s')
    RUNDE_WARM = Z(
        27.7,
        28.8,
        WARM,
        'Summe der Abschnitte (ohne Prüfbilder, die damals noch kein eigener Abschnitt waren)',
    )
    RUNDE_KALT = Z(98.1, 155.6, KALT + '; ' + SAP4 + ': Runde 0 = 98,1 s, Runde 1 = 155,6 s (Summe der Abschnitte)', 'Summe der Abschnitte')
    RUNDE_ALLE = Z(
        27.7,
        155.6,
        WARM + ' und ' + KALT + '; ' + SAP4,
        'warm 27,7–28,8 s (Folgerunde im selben Lauf), kalt 98,1–155,6 s (erste Runde eines Laufs)',
    )
    LAUF_EINE_RUNDE = Z(
        116.0,
        191.0,
        LOG + ', Läufe der Runden 20–23 („wartet/fertig in … s"); ' + SAP4 + ': „fertig in 191 s" (Runde 1 samt Standmodell 18,3 s)',
        'Dauer eines Laufs mit einer Runde',
    )

    # ------------------------------------------------------------------ Optionen und Motoren
    VORRAT_KALT = Z(
        41.7,
        quelle='Klassenkommentar Teilevorrat (Auftrag …20.10.04)',
        hinweis='Kleidermodellbau.teile kalt: Kleidung 28,9 s + Haar 10,9 s',
    )
    NEWTON_ERST = Z(
        142.0, quelle=NOTE, hinweis='Base Shirt, 24 Bilder, 7.552 Punkte — Warp-Kernel erstmals übersetzt'
    )
    NEWTON_WARM = Z(
        14.2, quelle=NOTE, hinweis='errechnet: 24 Bilder × 0,59 s (590 ms je Bild) — nicht einzeln gemessen'
    )
    BLENDER_START = Z(
        4.0, 9.0, 'Klassenkommentar Engine2d3dKleiderblender (30.09.2026): „Blender 5.2.2: Start 4–9 s"'
    )
    BLENDER_HOSE = Z(
        19.5, quelle=ZEITEN, hinweis='Hose 3.123 Punkte, 24 Bilder, Qualität 6 — ganzer Prozess (Skript 18,3 s, Start 1,2 s)'
    )
    BLENDER_OBERTEIL = Z(
        55.0, quelle=ZEITEN, hinweis='Oberteil 17.552 Punkte, 24 Bilder — ganzer Prozess (Skript 53,8 s, Start 1,2 s)'
    )
    SOLVER_HOSE = Z(
        2.1, quelle=ZEITEN, hinweis='Hose 3.123 Punkte, 24 Bilder, GPU — ganzer Prozess, davon Python und Importe 0,5 s; am 02.10.2026 vor dem Ausbau des Solvers gemessen'
    )
    SOLVER_OBERTEIL = Z(
        2.3, quelle=ZEITEN, hinweis='Oberteil 17.552 Punkte, 24 Bilder, GPU — ganzer Prozess; Blender braucht dafür 55 s; am 02.10.2026 vor dem Ausbau des Solvers gemessen'
    )
    SOLVER_OHNE_GPU = Z(
        462.0,
        quelle='Stoffsolver/README.md (02.10.2026): Host-Weg (NumPy), Hose, 12 Bilder, blender_roundtrip.py --host',
        hinweis='ohne CUDA-GPU — deshalb lehnt der Motor das ab; Blender braucht für dieselbe Hose 10 s',
    )
    BLENDER_HAAR = Z(
        2.4,
        6.0,
        NOTE,
        'am Pixie (236.136 Punkte, 21.755 Strähnen): 2,4 s Rechnung, 6 s mit Start; '
        'welcher Knoten, nennt die Quelle nicht',
    )
    RENDER_MITSUBA = Z(
        72.0, quelle='Einstellungen → 2D3D Kleider (Hilfetext): dieselbe Runde „72 gegen 62 s"'
    )
    RENDER_PYRENDER = Z(
        62.0, quelle='Einstellungen → 2D3D Kleider (Hilfetext): dieselbe Runde „72 gegen 62 s"'
    )
    PRUEFKI = Z(
        20.0, 60.0, OPT + ' (Iterationsoptionen.pruefki_stillstand: „20–60 s"; pruefki_alle nennt 1–3 min)'
    )

    #: Die Kette des Körperschritts in ihrer Reihenfolge (`Engine2d3dKleiderkoerper.KETTE` — ein Test hält beide gleich).
    KETTE = (
        'erkennung',
        'haar',
        'kleidung',
        'kalibrierung',
        'koerper',
        'gesicht',
        'rest',
        'textur',
        'vorschau',
        'frisur',
    )
    DB_KOERPER = 'ergebnis.dauer_koerper des Auftrags 2026.10.01.20.10.04 (Datenbank, 01.10.2026)'

    @classmethod
    def koerper_teile(cls):
        """Die zehn Teile des Körperschritts (Quelle rechnen) in Reihenfolge der Kette — [(Name, Workflowzeit)]. Die Sekunden
        stehen in `Architektur2d3dmessung.KOERPER`; `kalibrierung` fehlt dort und steht im Auftrag mit 0,0 s."""
        gemessen = {t.split(' ')[0]: (t, s, seither) for t, s, seither in Architektur2d3dmessung.KOERPER}
        gemessen['kalibrierung'] = ('kalibrierung', 0.0, '—')
        aus = []
        for schluessel in cls.KETTE:
            name, sekunden, seither = gemessen[schluessel]
            aus.append((name, Z(sekunden, quelle=cls.DB_KOERPER, hinweis='' if seither == '—' else seither)))
        return aus

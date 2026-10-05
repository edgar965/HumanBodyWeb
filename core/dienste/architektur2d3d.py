# -*- coding: utf-8 -*-
"""Architektur2d3d — die Daten der Seite Hilfe → Architektur → 2D3D (02.10.2026).

Edgar: „in welchem Schritt schaut die KI auf das Ergebnis und baut den Code für die nächste Runde? Schreibe alles über
die Implementierung der 2D3D Iterationen in eine neue Seite". Hier stehen der Lauf, die Schritte einer Runde und die
drei Wege, auf denen das Rezept der nächsten Runde entsteht; die Klassen liest `Architektur2d3dklassen` aus dem Code,
Messungen und offene Befunde führt `Architektur2d3dmessung`. Jede Klasse ist als (Modul, Klasse) genannt — der Test
`test_hilfe_architektur_2d3d` prüft, dass es sie gibt.
"""

from .architektur2d3dklassen import Architektur2d3dklassen
from .architektur2d3dmessung import Architektur2d3dmessung
from .architektur2d3dblender import Architektur2d3dblender
from .architektur2d3dwerkzeuge import Architektur2d3dwerkzeuge
from .architektur2d3dworkflow import Architektur2d3dworkflow

__all__ = ['Architektur2d3d']


class Architektur2d3d:
    STAND = '02.10.2026'
    #: Die Schritte von Engine2d3dKleiderlauf.SCHRITTE — (Schritt, Klasse, was er tut).
    LAUF = [
        ('vorbereitung', 'Engine2d3dKleidervorbereitung', 'Die Fotos aufbereiten: Hintergrund entfernen (BiRefNet), auf Wunsch den Körper '
         'senkrecht stellen, Zuschnitt als Quadrat um die Silhouette, Licht ausgleichen. Getrennt startbar; der Schritt „netz" übernimmt die Bilder.'),
        ('netz', 'Engine2d3dKleidernetz', 'TRELLIS baut aus den Fotos ein texturiertes Netz (Vorgabe 100.000 Flächen). Es '
         'dient nur noch dem Körperfit und als Herkunft der Fotostücke — die Runden richten sich nach den Fotos.'),
        ('segmentierung', 'Engine2d3dKleidersegmentierung', 'OPTIONAL: Sapiens (Körperteil-Modell) zerlegt die vorbereiteten Fotos in Oberteil, Hose, Socken/Schuhe, '
         'Zubehör und Haut; die Etiketten gehen mit der Projektion der Fotofarbe auf die Flächen des Netzes (verdeckte Flächen stimmen nicht ab). Bei Option „An" nimmt der '
         'Schritt „kleidung" der Körper-Kette sie für die Kleidungsmaske statt Farbe und Lage. Läuft im vollen Lauf nur bei „An", ausdrücklich gestartet immer.'),
        ('koerper', 'Engine2d3dKleiderkoerper', 'Genesis-9-Figur per Adam-Fit der Morphs an das Netz '
         '(Meshfigurregistrierung, mit Frühstopp), Hautkacheln backen, Frisurkandidaten messen.'),
        ('grundfigur', 'Engine2d3dKleidergrundfigur',
         'Die Figur mit Rig in A-Pose: grundkoerper.glb, Stellung für Bühne und Export.'),
        ('kleiderstuecke', 'Engine2d3dKleiderstuecke',
         'Oberteil, Hose und Socken aus dem Netz als eigene Genesis-Stücke bauen (Fotostuecke: Form aus der angepassten Figur, Farbe aus dem Netz, Maske der Segmentierung) und messen '
         '(Kleiderstuecknote: Deckung, Treue, F-Wert gegen die Maskenflächen, Aufbau, Körper gegen Haut, Bibliotheks-Anker). Die Bühne trägt sie danach schon vor Runde 1.'),
        ('iterationen', 'Iterationskreislauf → Begutachtungsrunde', 'Die Runden (unten). Modus „begutachtung" '
         '(Vorgabe): je Lauf 1 Runde mit Rezept von Hand oder bis 50 automatische Runden.'),
        ('export', 'Engine2d3dKleiderexport', 'Die beste Runde als GLB mit Rig.'),
        ('film', 'Engine2d3dKleiderfilm', 'BVH retargeten und rendern (ohne BVH übersprungen).'),
        ('speichern', 'Engine2d3dKleiderspeichern', 'Ablage in output/Export/Engine2d3dKleider.'),
    ]
    #: Edgars Vorgabe für die Runden (30.09.2026, nachgeschärft 02.10.2026).
    VORGABE = ('Nach JEDER Runde prüft Fable das Ergebnis und optimiert den Code. „jede iteration wird von dir '
               'begutachtet, und dann neuer Code erzeugt" (Edgar, 30.09.2026) — „Vorgabe ist, du überprüfst und '
               'optimierst den Code" (02.10.2026).')
    #: (Schritt, was Fable tut) — die Schleife der Vorgabe.
    PRUEFSCHLEIFE = [
        ('1. Runde rechnen', 'genau eine Runde (Reiter „Iterationen" → „Runde rechnen" bzw. POST …/begutachtung/).'),
        ('2. Ansehen', 'die Vergleichstafel iterationen/runde_NNN_vergleich.png: oben die Fotos, unten die Renders aus '
         'denselben Winkeln — Teil für Teil: Umriss, Kleider (Säume, Ausschnitt, Risse, Länge), Haut, Gesicht und '
         'Mund, Haar (Deckung, Farbe je Zone), Zubehör.'),
        ('3. Benennen', 'was nicht wie auf dem Foto aussieht, mit Ort (Blickwinkel, Körperteil).'),
        ('4. Code verbessern', 'die Klasse, die den Fehler erzeugt (2d3DIterationen/, Genesis9/, core/dienste/) — so, '
         'dass er beim nächsten Modell schon in Runde 1 nicht mehr entsteht; nur wo allein dieses Modell betroffen '
         'ist, ein Rezept m.xxx(…). Die Korrektur steht als Kommentar an der Stelle im Code.'),
        ('5. Festhalten', 'im Kommentar der Runde: was gesehen, was geändert. Dann zurück zu 1.'),
    ]
    #: Wer schreibt das Rezept der nächsten Runde? (Weg, wann, wer sieht was an, Klassen)
    WEGE = [
        ('Vorgabe: Fable prüft und optimiert', 'nach JEDER Runde (Schleife oben)',
         'Fable sieht die Vergleichstafel an, verbessert die Klassen oder schreibt ein Rezept und startet genau eine '
         'Runde. Der Server prüft ein Rezept (G9rezept.pruefen), bevor er rechnet.',
         'engine2d3dkleiderbegutachtung.js, Engine2d3dKleiderbegutachtungsendpunkte'),
        ('Automatik (Regeln) — erfüllt die Vorgabe NICHT', 'automatisch = true, Schritt 7–8 jeder Runde',
         'KEINE Prüfung: IterationModell liest nur MESSWERTE der letzten Runde (Abstände Stoff/Haar zum Netz je '
         'Band, Farben je Teil, Haltung aus den Fotolandmarken, Messgüte) und schreibt daraus Rezeptzeilen nach festen '
         'Regeln. Das Bild sieht niemand an, Code wird nicht verbessert. Nur zum Feinstellen (Farben, Längen) '
         'zwischen zwei Prüfungen.',
         'IterationModell, IterationKleider, IterationTextur, IterationHaare'),
        ('Prüf-KI (Ollama, Bild)', 'Schritt 9, nur bei Option „Prüf-KI" ≠ aus — Vorgabe AUS',
         'Ein lokales Bildmodell bekommt die Vergleichstafel und eine Frage (Begutachtungsprompt), antwortet JSON '
         'mit Urteil, Ähnlichkeit 1–10 und höchstens 8 Rezeptzeilen. Jede Zeile wird einzeln geprüft und HINTER das '
         'Rezept der Automatik gehängt; „fertig" bei Ähnlichkeit ≥ 8 beendet den Lauf. Fällig alle 5 Runden oder nach '
         '3 Runden ohne Besserung.',
         'Begutachtungskritik, Begutachtungsprompt, Ollamamodelle'),
    ]
    #: Die Runde in Reihenfolge — (Nr., wann, was, Klassen, Abschnitt im Log takt).
    RUNDE = [
        (1, 'je Lauf', 'Arbeitsprozess starten: manage.py engine2d3dkleider_fahren --ab iterationen --bis iterationen — ein '
         'eigener Prozess, der alle Module bei SEINEM Start lädt', 'Engine2d3dKleiderarbeiter, Engine2d3dKleiderlauf', ''),
        (2, 'je Lauf', 'Modus wählen: „begutachtung" → Begutachtungsrunde', 'Iterationskreislauf', ''),
        (3, 'je Lauf', 'Blickwinkel der Fotos aus den Posenlandmarken (fehlt der Winkel am Foto)',
         'Blickwinkelschaetzung, Blickwinkel', ''),
        (4, 'je Lauf', 'Vorlagen laden: Bild, Maske, Winkel, Gewicht; Fotos mit anderer Kleidung nur für die Form',
         'Iterationsreferenz', ''),
        (5, 'je Lauf', 'Haltung der Fotos: Arme seitlich, Ellbogenbeuge, Beinspreizung', 'Haltungsfotos, '
         'Haltungsschaetzung', ''),
        (6, 'je Lauf', 'Startmodell: die beste Runde (oder die laufende Probe), sonst Frisur aus dem Körperschritt, '
         'keine Kleider', 'ModellMitKleidern', ''),
        (7, 'je Runde', 'Befund für die Regeln sammeln: Messung der letzten Runde, Zubehör (Uhr, Bart), Fotostücke, '
         'Haarzonen', 'Begutachtungsstand, Begutachtungswerkzeug, Fotostuecke, Uhrerkennung', ''),
        (8, 'je Runde', 'Rezept schreiben: Haltung → [Körper, Gesicht nur bei Form an] → Kleider → Textur → Haar',
         'IterationModell', ''),
        (9, 'je Runde', 'Gesperrte Zeilen streichen; Prüf-KI anhängen, wenn fällig. Steht die Auflösungsstufe still '
         '(3 Runden ohne Besserung) oder findet die Automatik nichts mehr: Messrunde in doppelter Auflösung (bis zur '
         'Auflösung der Fotos), erst danach endet ein Lauf',
         'Rundenauswahl, Begutachtungskritik, Aufloesungsstufe', ''),
        (10, 'je Runde', 'Rezept anwenden: jede Zeile ist ein Methodenaufruf am Modell, geprüft über den Syntaxbaum '
         '(kein exec)', 'G9rezept, Rezeptumgebung, Sichtkoerper', ''),
        (11, 'je Runde', 'Modell bauen (A-Pose): Körper mit Augen, Mund, Wimpern, Brauen; Kleider, Haar; Kleidung und '
         'Haar aus dem Vorrat, wenn ihr Bauplan gleich blieb', 'Kleidermodellbau, Koerperanhaenge, Teilevorrat',
         'Modell bauen'),
        (12, 'je Runde', 'Haarfarbe je Kopfzone, dann in die Haltung der Fotos häuten', 'Haarzonen, G9haltungshaut',
         'Modell bauen'),
        (13, 'je Runde', 'Kennfarben-Render je Blickwinkel: welcher Pixel gehört zu welchem Teil',
         'Begutachtungsbefund, Teilmasken, Genesishaarrender', 'Modell bauen'),
        (14, 'je Runde', 'Fotoprojektion: Haut einmal je Körper aus den Fotos, Haarzonen messen, Stücke auf Wunsch',
         'Koerperfotoprojektion, Haarzonen, Kleidfotoprojektion', 'Fotoprojektion'),
        (15, 'je Runde', 'Render je Blickwinkel (Mitsuba, mindestens 384 px breit) und Note gegen das Foto in der '
         'Auflösungsstufe: (1 − IoU) + Farbe, Farbraster wächst mit (8 × 12 je 128 × 192)',
         'Genesishaarrender, Iterationsbild, Iterationsnote, Aufloesungsstufe', 'Rendern i von n'),
        (16, 'je Runde', '3D-Note gegen das Netz (60.000 Proben): mm/50 + (1 − Deckung)', 'Iterationsnetznote',
         'Rendern n von n'),
        (17, 'je Runde', 'Befund messen: Abstände je Band und Sektor, Farben, Kanten, Hautabstand, Messgüte',
         'Befundmessung, Netzmengen, Bandbreite, Hautabstand, Messpruefung', 'Rendern n von n'),
        (18, 'je Runde', 'Gesichtsmaße: Kopf-Render 1024², 4 Saaten, Landmarken gegen das Foto', 'Gesichtsmasse',
         'Rendern n von n'),
        (19, 'je Runde', 'Prüfbilder für die Prüfung durch Fable: Kopftafel (Foto- gegen Render-Kopf aus jedem '
         'Fotowinkel, 384²); die Vergleichstafel in Prüfbreite entsteht erst beim Ablegen (Schritt 20, '
         'Begutachtungsrunde._ablegen)', 'Pruefbilder', 'Prüfbilder'),
        (20, 'je Runde', 'Ablegen: Vergleichstafel (Prüfbreite), Kopftafel, Einzelrenders, Formbezug, Eintrag in '
         'ergebnis.iterationen', 'Pruefbilder, Iterationstafel, Iterationsrunde, Kleidermodellbau', 'ablegen'),
        (21, 'je Runde', 'Gesamtnote (Foto + Farbe der Teile + Gesicht) und Rundenauswahl: übernehmen, Probe oder '
         'verwerfen (Zeilen gesperrt); eine Messrunde setzt die Bezugsnote neu', 'Begutachtungsstand, Gesamtnote, '
         'Rundenauswahl', 'ablegen'),
        (22, 'nach dem Lauf', 'Automatik endet „Fertig · beste Runde N, Note x", ein Rezept von Hand mit „Wartet"',
         'Begutachtungsrunde, Engine2d3dKleiderlauf', ''),
    ]
    #: Festgelegt von Edgar — im Code an der Stelle vermerkt, die sie umsetzt.
    REGELN = [
        ('Nach jeder Runde prüft Fable und optimiert den Code',
         'Schleife oben; automatische Blöcke ersetzen sie nicht.'),
        ('Zwischenergebnisse in höherer Auflösung, inkrementell bis zur Auflösung der Fotos',
         'Aufloesungsstufe (128 → 256 → … → Figur im Foto, test3: 2485 px), Prüfbilder ≥ 384 px plus Kopftafel.'),
        ('Die Fotos sind die Vorlage, nicht das TRELLIS-Netz', 'Haut aus den Fotos (Koerperfotoprojektion), Haarzonen '
         'aus den Fotos; das Netz bleibt nur für den Körperfit und die Herkunft der Stücke.'),
        ('Eine Runde dauert 2–3 s', 'Ziel, noch nicht erreicht — Messung unten.'),
        ('Keine GLB je Runde', 'Der Vergleich aus den Blickwinkeln der Fotos genügt; die GLB der besten Runde '
         'entsteht erst beim Export (Begutachtungswerkzeug.bestes_glb).'),
        ('Automatische Runden enden „Fertig"', '„Wartet" nur nach einem Rezept von Hand.'),
        ('Ein fertiger Auftrag lässt sich weiterrechnen', 'Knopf „Weiterrechnen" in der Auftragsliste (1–50 Runden).'),
        ('Mund geschlossen', 'Mimikregler (Lip Part, Lip Gaps, Mouth Opening) werden beim Lesen der Stellung gefiltert '
         '(Meshfigurregler.ohne_mimik).'),
        ('Nichts rechnet ohne Auftrag', 'Runden startet nur Edgar oder ein ausdrücklicher Auftrag, immer über die '
         'Server-API.'),
    ]

    @classmethod
    def kontext(cls):
        gruppen = Architektur2d3dklassen.gruppen()
        return {
            'stand': cls.STAND,
            'vorgabe': cls.VORGABE,
            'pruefschleife': [{'schritt': s, 'was': w} for s, w in cls.PRUEFSCHLEIFE],
            'lauf': [{'schritt': s, 'klasse': k, 'was': w} for s, k, w in cls.LAUF],
            'wege': [{'weg': a, 'wann': b, 'wer': c, 'klassen': d} for a, b, c, d in cls.WEGE],
            'runde': [{'nr': n, 'wann': w, 'was': t, 'klassen': k, 'takt': a} for n, w, t, k, a in cls.RUNDE],
            'regeln': [{'regel': r, 'umsetzung': u} for r, u in cls.REGELN],
            'gruppen': gruppen,
            'messung': Architektur2d3dmessung.kontext(),
            'workflow': Architektur2d3dworkflow.kontext(gruppen, cls.LAUF, cls.RUNDE),
            'werkzeuge': Architektur2d3dwerkzeuge.kontext(),
            'blender': Architektur2d3dblender.kontext(),
        }

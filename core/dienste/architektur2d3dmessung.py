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
    #: Zwei Runden mit dem Stand vom 06.10.2026 (Auftrag „Edgar - Sapiens 4", `auftrag.log`, Prozess je Lauf kalt): Iteration 0 und die automatische Runde danach.
    #: (Abschnitt, Iteration 0, Runde 1) in Sekunden — dieselben Abschnitte wie oben, dazu „Prüfbilder", das damals noch kein eigener Abschnitt war.
    SAPIENS_QUELLE = 'auftrag.log von 2026.10.06.00.33.38 („Edgar - Sapiens 4"), Runde 0 um 00:35–00:36 und Runde 1 um 00:37–00:39, 06.10.2026'
    SAPIENS_RUNDE = [
        ('Modell bauen', 36.6, 49.5),
        ('Fotoprojektion', 13.7, 36.8),
        ('Rendern 1 von 3', 9.0, 11.8),
        ('Rendern 2 von 3', 0.2, 0.3),
        ('Rendern 3 von 3', 6.7, 9.6),
        ('Prüfbilder', 22.8, 33.1),
        ('ablegen', 9.1, 14.5),
    ]
    SAPIENS_GESAMT = (98.1, 155.6)
    #: Der ganze Lauf nach der Runde: „fertig in 191 s" (Runde 1 samt Standmodell der Bühne, 18,3 s).
    SAPIENS_LAUF_S = 191
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
        ('Kein Standmodell nach reinen Runden', '20 s je Lauf weniger — seit 05.10.2026 nur noch im Modus „automatisch": Im Modus „Begutachtung" baut der Lauf es am Ende (Edgar), 40–50 s zusätzlich'),
        ('Note und Befund auf 128 × 192 statt 256', 'die Renders der Runde entstehen in max(Auflösungsstufe, tafelbreite 384) wegen der '
         'Prüfbilder (Begutachtungsrunde, Zeile 166); Zeitanteil nicht getrennt gemessen'),
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

    #: Beim Durchsehen der Seite am 06.10.2026 gefunden oder gemessen (Auftrag „Edgar - Sapiens 4" und seine Kopie, Läufe …14.10.22 und …14.20.55) — mit dem, was dazu gemessen ist.
    OFFEN_NEU = [
        ('Die Runden fassen die Form nicht an',
         'Option iterationen.form steht auf „aus" (Vorgabe, seit 01.10.2026: die Regeln schoben die Beine von „.51" 40 Runden lang an den Anschlag). Gemessen an Sapiens 4, Runde 1: Gesamtnote 0,3522 = '
         'Umriss (1 − IoU 0,820) 0,180 (51 %) + Haar 0,098 (28 %) + Gesicht 0,045 (13 %) + Farbe 0,030 (8,5 %). Runde 1 brachte in Sapiens 3, 4 und 5 nur 0,010–0,012 (rund 3 %), fast nur aus der Farbe der Teile '
         '(Sapiens 4: 0,0191 → 0,0107); in der Kopie …10.57.22 (Belichtungsabgleich, Seitenfoto zählt für die Farbe) 0,031, weil ihre Iteration 0 schlechter beginnt (Farbe der Teile 0,0328). '
         'Haar (0,0976) und Gesicht (0,0447) blieben in allen exakt gleich — das ist keine Störung (gelesen und gezählt 06.10.2026): Runde 1 besteht in Sapiens 3, Sapiens 4 und der Kopie …14.20.55 aus Zeilen für Hemd (Zellenmorphe, Farbe, '
         'Fototextur, in Sapiens 3 auch die Hülle) und aus haar_nur, haar_anteil, haar_umfaerben — keine, die die Form des Haars oder den Körper ändert. Der Haarterm misst die FORM des Kopfhaars im Kennbild (Haarabgleich._ansicht, Flachfarben je Teil, ohne Textur: '
         'IoU je Ansicht 0,2966 / 0,9032 / 0,6291 in Runde 0 und 1 gleich), der Gesichtsterm kommt aus dem Gesichtsvorrat, geschlüsselt auf die Körperpunkte (die Verhältnisse sind in beiden Runden bitgleich). '
         'Farbrunden können deshalb beide Terme, zusammen 41 % der Note, nicht bewegen; dafür braucht es Zeilen für die Form des Haars (haar_morph, haar_gruppe_weg …) — von Hand, die Automatik schreibt sie nicht. '
         'Nachtrag 06.10.2026 (gemessen an …14.20.55, Runden 0 bis 5): Zeilen für die Garderobenfrisur — haar_achse (Runde 2), haar_heben (Runde 5) — erreichen das Haar nicht, solange iterationen.haarumbau auf der Vorgabe herren steht: '
         'Gerendert wird das eigene Herrenhaar, der Haarterm blieb in allen sechs Runden bei 0,0976. Wirksam sind haar_farbe (Kopfmessung statt Teilmaske: Render ÷ Foto 0,77 → 0,92, Gesamtnote 0,3458 → 0,3424) und haar_ansatz (neu, hebt den Haaransatz vorn; 20°: Haarterm 0,0976 → 0,0940, Gesamtnote 0,3389).'),
        ('Wo der Umriss verloren geht',
         'Gemessen 06.10.2026 an Iteration 1 von Sapiens 4 (128 × 192, Anteil der Vereinigung): vorn fehlt 7,2 % und 10,2 % sind zu viel, hinten 11,3 % und 10,0 %, von der Seite 8,6 % und 6,6 %. Größte Posten: '
         'hinten die Höhenbänder 4–7 (Schulter bis Hüfte, die Arme) fehlen mit 7,4 %; von der Seite fehlen in den Bändern 10–12 (Unterschenkel, Füße) 5,6 % und im Bauch (Bänder 5–7) sind 2,3 % zu viel. '
         'Gesehen auf der Tafel (nicht gemessen): die Füße stehen im Foto in V-Stellung, im Render parallel.'),
        ('Ablagen ohne Fassung im Namen: Atlanten und Zellenmorphe (neue Zellenmorphe tragen seit 06.10.2026 das Kürzel — im Code behoben, nicht gelaufen)',
         'Die Foto-Atlanten (3DObjects/models/Genesis9/kleidtexturen/*foto_<kürzel>_f1.png) tragen die Kennung des Auftrags; ein Probelauf mit echter Kennung überschreibt sie (die Atlanten von Sapiens 4 stammen von '
         '09:57 statt 00:38, im JSON „ansichten: [0, 180]" — ohne Seitenfoto). Die Zellenmorphe der Automatik (kleidmorphe/<Stück>__netz_b<i>s<j>_f1.npz, 288 Dateien) trugen KEINE Auftragskennung: 36 wurden am '
         '06.10.2026 neu geschrieben (4 um 09 Uhr, 32 um 13 Uhr, nach dem Lauf von Sapiens 4 um 00:37); ob sich ihr Inhalt änderte, ist nicht geprüft. Das Modell von Iteration 1 ist deshalb als Bild erhalten, '
         'als Modell nicht gesichert. Geändert (IterationKleider, Auftragskürzel durch Begutachtungsautomatik und IterationModell): ein NEUER Zellenmorph heißt netz_b<i>s<j>_<kürzel>, ein schon gestellter wird unter seinem Namen weitergestellt. '
         'Die 288 alten Dateien bleiben unter dem alten Namen und sind damit ab jetzt eingefroren — wiederherstellen lässt sich der Stand von vor dem 06.10.2026 daraus nicht.'),
        ('Eine Kopie nimmt die Atlanten nicht mit (im Code behoben 06.10.2026, nicht gelaufen)',
         'Aus dem Code gelesen, nicht gemessen: Engine2d3dKleiderauftragskopie kopierte den Auftragsordner; die Atlanten liegen außerhalb. Für die Kopie …14.20.55 wurden die sieben Dateien von Hand unter dem Kürzel der Kopie angelegt (die '
         'Körper-Ortsmorphe eigenmorphe/ort_*_<kürzel> gar nicht). Jetzt legt Engine2d3dKleiderauftragsablagen alle Dateien aus kleidtexturen, kleidmorphe und eigenmorphe mit dem Kürzel der Quelle unter dem der Kopie neu an (nichts überschrieben) '
         'und setzt das Kürzel in den JSON-Feldern der Zeile um. Nicht kopiert: die Fotostücke der Bibliothek (eigen_foto_<acht Ziffern>_…) — die Kopie nennt sie weiter beim Namen der Quelle.'),
        ('Ein Neulauf in einer Kopie hängt an die Runden der Quelle an (im Code behoben 06.10.2026, nicht gelaufen)',
         'Gemessen am Lauf …14.10.22 (voll, alle Schritte neu, 06.10.2026): seine Iteration 0 wurde Runde 2 (art ausgang, auswahl verworfen, beste Runde 1) und die Rundenauswahl verwarf sie gegen Runde 1 der Quelle — Gesamtnote 0,3975 gegen 0,3516, '
         'obwohl Netz, Körper und Haar neu gerechnet waren. Beide Noten stammen von verschiedenen Netzen; der Vergleich sagt nichts über die Güte der Änderungen. Das Feld uebernommen der Runde heißt nur „ohne Fehler" (war True), die Auswahl steht in auswahl.aktion. '
         'Jetzt legt Iterationsarchiv die Runden beiseite (iterationen/frueher/<Zeitstempel>/ergebnis.json, die runde_*-Dateien ziehen mit, ergebnis.fruehere_runden führt eine Zeile), BEVOR vorbereitung, netz oder koerper neu rechnet; nichts wird gelöscht. '
         'Der Lauf …14.10.22 selbst behält seinen Zustand. Seine Runden 3 bis 5 (gelesen 06.10.2026, 15:30–15:32): Runde 3 = 0,4021 „übernommen — beste Runde", obwohl schlechter als Runde 1 der Quelle (0,3516) und als die eigene Iteration 0 (0,3975) — '
         'gelesen im Code: Rundenauswahl.pflicht lässt jede Runde mit m.kleid_nur(…, \'eigen_foto_…\') gelten, und die Automatik schrieb die neuen Fotostücke des Neulaufs (eigen_foto_06141022_…) in Runde 3 so hinein; nicht anders nachgestellt. '
         'Runde 4 = 0,4070 und Runde 5 = 0,4255 liefen als Probe (beste Runde 3). Der Vergleichswert war also kein neuer Bezug, sondern die Pflichtregel; die Note des alten Netzes (0,3516) hat sie nicht mehr gebremst. Seit 06.10.2026 gilt eine Runde mit Pflichtzeile nur noch bei besserer Note (umgebaut in der Parallelsitzung, von mir nicht geprüft); eine schlechtere startet eine Probe.'),
        ('Eine blasse warme Linie am Ärmelvorderrand',
         'Gesehen in Iteration 1 (06.10.2026), Ursache nicht bestimmt; die orangen Linien an den Armlöchern sind seit dem Haltungsabstand weg (Baum „Sitz").'),
    ]
    #: Seitenvermerk für die alten Einträge unten.
    OFFEN_ALT_STAND = '02.10.2026 — am 06.10.2026 nicht neu geprüft'

    @classmethod
    def kontext(cls):
        return {
            'quelle': cls.QUELLE,
            'sapiens': {
                'quelle': cls.SAPIENS_QUELLE,
                'runde': [{'abschnitt': a, 'werte': (r0, r1)} for a, r0, r1 in cls.SAPIENS_RUNDE],
                'gesamt': cls.SAPIENS_GESAMT,
                'lauf': cls.SAPIENS_LAUF_S,
            },
            'offen_neu': [{'was': a, 'befund': b} for a, b in cls.OFFEN_NEU],
            'offen_alt_stand': cls.OFFEN_ALT_STAND,
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

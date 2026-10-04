# -*- coding: utf-8 -*-
"""Werkzeugrezeptkleidung — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: Kleider per Rezept anziehen und einstellen.

Reine Daten (Schema: `ProjektTemp/_wegwerf/stoff_ausbau/AUFTRAG_TOOLS.md`); gelesen von `Architektur2d3dwerkzeuge`.
Jede Zeile ist gegen den Code gelesen (03.10.2026); Zahlen tragen Fundstelle und Datum, was nicht gemessen ist, steht
als „nicht gemessen".
"""

__all__ = ['Werkzeugrezeptkleidung']


class Werkzeugrezeptkleidung:
    G = 'Genesis9/'
    A = 'HumanBodyWeb/core/api/'

    KENNUNG = 'rezeptkleidung'
    TITEL = 'Kleider anziehen und einstellen (Rezept)'
    EINLEITUNG = (
        'Ein Rezept ist Text: je Zeile ein Aufruf m.<funktion>(…) an ein ModellMitKleidern (Genesis9/modellmitkleidern.py). '
        'Es ist kein Python, sondern wird mit ast gelesen — nur Literale als Argumente. Reihenfolge: 1. die Kennungen der '
        'Stücke aus der Garderobe lesen (Gruppe „Garderobe“, GET …/garderobe/), 2. anziehen (kleid_nur, kleid_anteil), '
        '3. Passform, Übergang und Farbe stellen, 4. bauen und ansehen (Gruppe „Bau ohne Browser“). Die Aufrufe dieser '
        'Gruppe ändern nur Regler im Zustand; gerechnet wird erst beim Bau. Die rechnenden Aufrufe (Morphe, Ring, Hülle, '
        'Drapieren, Haar-Operationen, Texturschichten) stehen in den Gruppen „Kleider formen“, „Drapieren …“, '
        '„Haar formen“ und „Textur“.')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Rezept lesen, prüfen und anwenden',
         'Führt einen Rezepttext (eine Zeile je Aufruf) auf einem ModellMitKleidern aus. Erlaubt sind nur Aufrufe '
         'm.<funktion>(Literale); alles andere wirft ValueError mit Zeilennummer.',
         'python',
         "import sys\n"
         "sys.path[:0] = ['A:/3DTools', 'A:/3DTools/2d3DIterationen', 'A:/3DTools/Assets']\n"
         "from Genesis9.modellmitkleidern import ModellMitKleidern\n"
         "from Genesis9.modellrezept import G9rezept\n"
         "m = ModellMitKleidern()\n"
         "G9rezept.anwenden(m, \"m.kleid_nur('g9_base_shirt', 'angie_jeans')\\nm.passform(laenge_cm=-4)\")\n"
         "m.kleidung        # {'sorte.g9_base_shirt': 1.0, 'sorte.angie_jeans': 1.0, 'passform:laenge': -4.0}",
         [(G + 'modellrezept.py', 'G9rezept'), (G + 'modellmitkleidern.py', 'ModellMitKleidern')],
         'Ergebnis von anwenden: [(Zeile, Aufruf als Text)]. G9rezept.pruefen(text) prüft nur (ValueError mit Zeile, keine '
         'Wirkung). Argumente: Zahlen, Zeichenketten, None, True/False, Listen, Tupel, Wörterbücher (ast.literal_eval); '
         '**argumente und fremde Namen gehen nicht. Scheitert Zeile n, sind die Zeilen davor schon wirksam. Im Django-'
         'Prozess stehen die Pfade schon im sys.path (HumanBodyWeb/ui/settings/wurzeln.py: TOOLS_ROOT, 2d3DIterationen, '
         'Assets, HumanBody). Quelle: Genesis9/modellrezept.py, Test core/tests/unit/test_modellmitkleidern.py.'),

        ('Funktionsliste: welche Aufrufe gibt es?',
         'Liefert alle Rezeptfunktionen mit Signatur und erstem Docstring-Satz — direkt aus dem Code, aktueller als diese '
         'Seite. Zuerst hier nachsehen, wenn ein Name oder eine Vorgabe unklar ist.',
         'api',
         'GET /api/engine2d3dkleider/funktionen/\n'
         'oder in Python: from Genesis9.modellrezept import G9rezept; print(G9rezept.hilfetext())',
         [(A + 'engine2d3dkleiderbegutachtung.py', 'Engine2d3dKleiderbegutachtungsendpunkte'),
          (G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'modellrezept.py', 'G9rezept')],
         'Antwort {objekt: "m", funktionen: [{name, signatur, text}]}; braucht keinen Auftrag. Nicht in der Liste stehen die '
         'Abfragen aus ModellMitKleidern.KEINE_AUFRUFE (als_dict, aus, hilfe, getragene, kleidung_modell, kleider, frisuren, '
         'regler_stueck, stueckfarbe, gruppenfarben, fotoschicht, auftragsname, vorhanden). Die Liste umfasst auch die '
         'Körperaufrufe (koerper_regler, haltung, koerper_ort, …) — die gehören zur Gruppe Körper (T1).'),

        ('Rezept in einem Auftrag einreichen (Runde rechnen)',
         'Prüft ein Rezept, legt es ab und rechnet die nächste Runde des Auftrags im Arbeitsprozess: anwenden, bauen, '
         'rendern, benoten.',
         'api',
         'POST /api/engine2d3dkleider/<job_id>/begutachtung/   {aufrufe: "m.kleid_nur(…)\\nm.passform(…)", kommentar: "…"}\n'
         '→ {ok: true, pid}   | 400 {error: "Rezept: …"} | 409 {error: "Auftrag läuft schon"} oder GPU belegt',
         [(A + 'engine2d3dkleiderbegutachtung.py', 'Engine2d3dKleiderbegutachtungsendpunkte'),
          (G + 'modellrezept.py', 'G9rezept'), ('HumanBodyWeb/core/dienste/engine2d3dkleiderarbeiter.py', 'Engine2d3dKleiderarbeiter'),
          ('HumanBodyWeb/core/dienste/engine2d3dkleidergpu.py', 'Engine2d3dKleidergpu'),
          ('HumanBodyWeb/core/dienste/begutachtungsrunde.py', 'Begutachtungsrunde')],
         'STARTET eine Runde und belegt die GPU — nur auf Ansage (die Schleife selbst beschreibt die Gruppe Bildvergleich, T4). '
         'Der Endpunkt prüft nur (G9rezept.pruefen, höchstens 20.000 Zeichen); angewandt wird im Arbeitsprozess auf das Modell '
         'der letzten Runde (Begutachtungsrunde._runde mit Rezeptumgebung: Sichtkörper, Drapierer, Haar-Dynamik). Ein Fehler '
         'beim Anwenden (unbekanntes Stück …) steht in der Runde (fehler), das Modell bleibt. {automatisch: true, runden: n} '
         'lässt IterationModell n Runden schreiben (höchstens RUNDEN_HOECHSTENS = 50). Gemessen: Runde 2 32 s, Runde 3 36 s (Auftrag '
         '„Edgar - TEST“, 30.09.2026), 45–55 s je Runde bei 512 px (Auftrag .51, 01.10.2026), 43–44 s je Runde im Block '
         '(Begutachtungswerkzeug.takt, 02.10.2026). Der Arbeitsprozess muss über die Server-API starten: ein Prozess, den ein '
         'Skript anstößt, stirbt mit dem Skript (engine2d3dkleider.md, 01.10.2026).'),

        ('Wirksame Aufrufe eines Auftrags lesen',
         'Liefert alle wirksamen Aufrufe der übernommenen Runden als wiederverwendbaren Text — der Weg zu diesem Modell.',
         'api',
         'GET /api/engine2d3dkleider/<job_id>/rezept/   → text/plain (mit ?laden=1 als Download rezept_<kennung>.py)',
         [(A + 'engine2d3dkleiderbegutachtung.py', 'Engine2d3dKleiderbegutachtungsendpunkte'), (G + 'modellrezept.py', 'G9rezept')],
         'Kopf „# Rezept <Name> (<Kennung>)“ und „# m = ModellMitKleidern()“, dann je Runde ein Kommentar und ihre Zeilen '
         '(runde["aufrufe"]). Dasselbe Rezept lässt sich auf einer anderen Figur noch einmal anwenden (G9rezept.anwenden). '
         'Zeilen aus Pinsel und Maler stehen als m.bild_wert(…) bzw. m.morph_wert(…)/m.koerper_regler(…) darin.'),

        ('Kleidungsstücke anziehen (nur diese)',
         'Zieht genau die genannten Stücke an, jedes mit Anteil 1; alle bisher gesetzten Stücke gehen auf 0.',
         'rezept',
         "m.kleid_nur('g9_base_shirt', 'angie_jeans')",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'kleidgenerischwahl.py', 'G9kleidgenerischwahl')],
         'Kennung = id aus der Garderobenliste (geslugter .duf-Name: g9_base_shirt, angie_jeans; mb_… MakeHuman, gc_… '
         'GarmentCode, eigen_… eigene Stücke). Eine '
         'unbekannte Kennung wird still ignoriert (G9kleidgenerischwahl.anteile). Höchstens 4 Stücke werden zugleich gebaut '
         '(HOECHSTENS), jedes kostet einen eigenen Netzbau. Falle: kleid_nur legt für das erste Stück der Liste „Alle '
         'Kategorien“ keinen Regler an, ein Stück ohne gesetzten Regler gilt als Vorgabe 1,0 (nur das erste der Liste) — '
         'anders als haar_anteil, das die Grundsorte ausdrücklich auf 0 setzt. An Kunstdaten nachgerechnet (03.10.2026, '
         'G9kleidgenerischwahl.anteile: aus {sorte.zweites: 1} wird {erstes: 1, zweites: 1}). Welches Stück an der echten '
         'Bibliothek das erste ist, ist nicht bestätigt: die gemerkte Liste (Genesis9/ablage/garderobe.json, 480 Einträge, '
         'gelesen 03.10.2026) beginnt mit g9_base_bikini, g9_base_bra, g9_base_shirt, g9_base_shorts — das erste Oberteil '
         'dürfte g9_base_shirt sein, was die Falle in der Praxis verdeckt. Nach dem Anziehen m.kleider() lesen und prüfen, '
         'was wirklich getragen wird. Quelle: Genesis9/kleidgenerischwahl.py (anteile), Genesis9/modellhaar.py (haar_anteil).'),

        ('Anteil eines Stücks setzen (Mischen)',
         'Stellt den Anteil eines Kleidungsstücks (0…1). Wo sich zwei Stücke überdecken, steht eine Fläche aus dem '
         'Verhältnis ihrer Anteile; 0 nimmt das Stück weg.',
         'rezept',
         "m.kleid_anteil('g9_base_shirt', 1.0)\nm.kleid_anteil('gc_dress_shift', 0.3)",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'kleidgenerischwahl.py', 'G9kleidgenerischwahl')],
         'Anteile sind voneinander unabhängig, die Summe muss nicht 100 % sein (anders als beim Haar); Anteile unter 0,005 '
         'fallen weg (KLEINSTER). Das Stück mit dem größten Anteil trägt die Fläche der Überlappung; bei Gleichstand das '
         'zuletzt bewegte (sorte_zuletzt, schickt nur der Browser), dann das später genannte. Gemischt wird über die Haut, '
         'nicht über Inseln wie beim Haar. Gemessen 30.09.2026 (genesis9-garderobe.md): Base Shirt × GC Dress Shift 100:30 '
         '— das Shirt bewegt sich im Median 0,8 mm (p90 3,0, max 9,6), über den Endpunkt 4,4 s kalt, 0,0 s aus dem Vorrat. '
         'Grenze: wo der Zuschnitt einen Rand lässt, öffnet sich im Stoffschwung ein Spalt. Die Kennung im Beispiel '
         '(gc_dress_shift) ist nur ein Muster — vorher in der Garderobenliste nachsehen.'),

        ('Ein Stück ablegen',
         'Setzt den Anteil eines Stücks auf 0 (Kurzform von kleid_anteil(kennung, 0.0)).',
         'rezept',
         "m.kleid_aus('angie_jeans')",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'kleidgenerischwahl.py', 'G9kleidgenerischwahl')],
         'Stehen danach ALLE Anteile auf 0, gilt wieder das erste Stück der Liste als getragen '
         '(G9kleidgenerischwahl.anteile: „Stehen alle auf 0, gilt die Grundsorte“, damit eine Figur nicht aus Versehen '
         'nackt wird). Der Bau über Kleidermodellbau kennt deshalb kein „nackt“; kleidung_modell() lässt den Eintrag '
         'dagegen weg, wenn kein Anteil über 0 steht (gelesen, nicht ausprobiert).'),

        ('Alle Kleidungsstücke ablegen',
         'Setzt jeden schon gesetzten Kleideranteil auf 0.',
         'rezept',
         "m.kleid_alle_aus()",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern')],
         'Nullt nur Regler, die im Modell schon stehen (list(self.kleidung)); ein nie gesetztes Stück bleibt auf seiner '
         'Vorgabe — siehe kleid_nur. Gleiche Grenze wie kleid_aus (Grundsorte). Quelle: Genesis9/modellmitkleidern.py.'),

        ('Daz-Morph eines Stücks stellen',
         'Stellt einen echten Daz-Morph des Stücks (die Regler, die Daz mitliefert, etwa Adj Inflate).',
         'rezept',
         "m.kleid_morph('g9_base_shirt', 'body_bs_LoosenCollars', 0.3)",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern')],
         'kanal = der name des Reglers in der Reglerliste des Stücks (GET …/garderobe/, Feld regler[].name); ein Name, den '
         'das Stück nicht hat, bleibt wirkungslos (G9garderobe.reglerwerte nimmt nur Namen aus eintrag[regler]). Gelesen aus '
         'der gemerkten Liste (03.10.2026): g9_base_shirt hat body_bs_ExpandAll, FitOverPants1…3, body_bs_LoosenButtocks, '
         '…Collars, …Midriff, …Neck, …Thighs, …WaistLower, …WaistUpper (alle 0…1), angie_jeans body_bs_ExpandAll, '
         '…LoosenButtocks, …Knees, …Thighs, …WaistLower, …WaistUpper; dazu bei jedem Kleidungsstück passform:laenge und '
         'passform:weite (die setzt m.passform). Wertebereich je Regler min/max in derselben Liste. Der Schlüssel im Modell ist '
         '<kennung>.<kanal>. Eigene Morphe (eigen.*) baut man nicht hiermit, sondern in der Gruppe „Kleider formen“.'),

        ('Passform: Länge und Weite aller Kleider',
         'Verschiebt den Käfig der Kleider am Körper entlang: Saum länger oder kürzer, Stoff weiter oder enger.',
         'rezept',
         "m.passform(laenge_cm=-4.0, weite_cm=1.0)",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'folger.py', 'G9folger'),
          (G + 'passform.py', 'G9passform')],
         'Länge −20…20 cm, Weite −3…+6 cm (gekappt), Vorgabe 0; gilt für jedes Stück der Art kleidung (nicht für Haar). '
         'Länger (+): der Saum wandert am Körper entlang. Kürzer (−): ein Schnitt, keine Stauchung (G9passform.kuerzen, '
         'höchstens KUERZUNG 0,7 der Höhe, die Flächen darunter fallen aus dem Netz). Weite läuft entlang der HAUTNORMALE, '
         'enger als 3 mm über der Haut geht nicht (MINDEST). Gemessen 20.09.2026 (genesis9-passform.md): 40–90 ms je Stück '
         'für die Länge, ein neuer Stand der Haut 0,5 s. Grenze: ein loses Stück zwischen zwei Gliedern (Bardot Top hinter '
         'der Achsel) reißt beim Vorbeugen weiter.'),

        ('Breite des weichen Rands beim Mischen',
         'Stellt, wie weit die Mischung zweier Stücke am Rand der Überlappung ausläuft.',
         'rezept',
         "m.uebergang(3.0)",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'kleidgenerischwahl.py', 'G9kleidgenerischwahl')],
         '0,5…10 cm, Vorgabe 3 cm (UEBERGANG_CM); am Server in Metern gelesen (G9kleidgenerischwahl.uebergang). Wirkt nur, '
         'wenn mindestens zwei Stücke über 0 stehen. Quelle: Genesis9/kleidgenerischwahl.py.'),

        ('Textur des 2.–4. Stücks in die Überlappung mischen',
         'Stellt, wie viel Farbe des 2., 3. oder 4. Stücks (nach Anteil geordnet) in der Überlappung mitmischt.',
         'rezept',
         "m.textur_mischen(2, 0.5)",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'kleidgenerischwahl.py', 'G9kleidgenerischwahl')],
         'rang 2…4, Anteil 0…1, ändert nur die Farbe, nicht die Form. Wichtig: diese Regler gelten NUR im Browser (Shader, '
         'HumanBodyWeb/static/viewer/gemeinsam/kleidfarbmischung.js) und gehen nie an den Bau '
         '(G9kleidgenerischwahl.ohne_textur) — im Python-Bau '
         '(Runde, Render, Standmodell) bleibt der Aufruf ohne Wirkung (gelesen, nicht ausprobiert).'),

        ('Umfärbung aller Kleider',
         'Tönt alle Kleider mit einer Farbe (#rrggbb); die Textur bleibt, wird getönt.',
         'rezept',
         "m.kleid_farbe('#6f6f78')",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern')],
         'Vorgabe #6f6f78 (FARBEN). Rechenregel im Bau: Textur × 2 × Tönung, auf 0…1 begrenzt (Kleidermodellbau._textur) — '
         'ein dunkles Daz-Shirt (Mittel 0,067) lässt sich damit nie aufhellen; erst kleid_umfaerben (Gruppe „Textur“), '
         'dann tönen. Falsches Format wirft ValueError („Farbe als #rrggbb“). Quelle: .claude/rules/engine2d3dkleider.md '
         '(01.10.2026, „Eine Regel ohne geprüfte Messung zerstört das Modell still“).'),

        ('Umfärbung eines einzelnen Stücks',
         'Tönt ein Stück mit eigener Farbe; die anderen Stücke behalten kleid_farbe.',
         'rezept',
         "m.kleid_farbe_je_stueck('g9_base_shirt', '#222222')",
         [(G + 'modelltextur.py', 'ModellTexturMixin'), (G + 'modellmitkleidern.py', 'ModellMitKleidern')],
         "Leere Farbe ('') nimmt die eigene Tönung zurück. Stoff und Material geben ModellMitKleidern.gruppenfarben() je "
         'Materialgruppe der .duf weiter. Die Automatik (IterationKleider.farbe) schreibt genau diese Zeile je Stück: eine '
         'gemeinsame Tönung traf schwarzes Shirt und helle Shorts nie zugleich (01.10.2026, 2d3DIterationen/README.md).'),

        ('Zustand lesen: was trägt das Modell?',
         'Fragt ab, welche Stücke und Frisuren der Zustand gerade trägt — vor dem Bau, um Überraschungen zu sehen.',
         'python',
         "m.kleider()       # [(kennung, anteil, regler_stueck)] der getragenen Kleider, stärkstes zuerst\n"
         "m.frisuren()      # dasselbe für die Frisuren (Summe der Anteile 1)\n"
         "m.getragene()     # [{kennung, stil, regler_stueck}] in Anziehreihenfolge — der Rumpf getragen\n"
         "m.kleidung_modell()  # das Feld figur.kleidung eines gespeicherten Modells",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'kleidgenerisch.py', 'G9kleidgenerisch')],
         'kleider() löst über G9kleidgenerisch.mischung_aufloesen auf, also MIT der Vorgabe-Regel (leer ⇒ erstes Stück). '
         'Das Ergebnis ist das, was der Bau trägt — nicht unbedingt das, was im Rezept stand. Quelle: Genesis9/'
         'modellmitkleidern.py.'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('G9rezept', 'ruft', 'ModellMitKleidern',
         'ModellMitKleidern.hilfe(): die erlaubten Funktionen; beim Anwenden getattr(modell, name)(*args, **kwargs)'),
        ('Engine2d3dKleiderbegutachtungsendpunkte', 'ruft', 'G9rezept',
         'G9rezept.pruefen(): prüft ein eingereichtes Rezept vor dem Start der Runde; funktionen() liefert die Liste'),
        ('Engine2d3dKleiderbegutachtungsendpunkte', 'ruft', 'ModellMitKleidern',
         'ModellMitKleidern.hilfe(): Antwort von GET funktionen/'),
        ('Engine2d3dKleiderbegutachtungsendpunkte', 'ruft', 'Engine2d3dKleiderarbeiter',
         'Engine2d3dKleiderarbeiter.starten(job, ab, bis) und lebt(job): startet den Arbeitsprozess für den Schritt iterationen'),
        ('Engine2d3dKleiderbegutachtungsendpunkte', 'ruft', 'Engine2d3dKleidergpu',
         'Engine2d3dKleidergpu.belegt_durch(job): 409, wenn die GPU belegt ist'),
        ('Begutachtungsrunde', 'ruft', 'G9rezept', 'G9rezept.anwenden(modell, aufrufe): _runde() wendet das Rezept an'),
        ('ModellMitKleidern', 'ruft', 'G9kleidgenerisch',
         'G9kleidgenerisch.mischung_aufloesen(): kleider() liefert die getragenen Stücke; die Konstanten PASSFORM, '
         'UEBERGANG, TEXTUR, HOECHSTENS legen die Reglerschlüssel fest'),
        ('G9kleidgenerisch', 'ruft', 'G9kleidgenerischwahl',
         'erbt anteile(), mischung(), regler_von(), uebergang(), ohne_textur(): Anteile und Reihenfolge der Stücke'),
        ('ModellMitKleidern', 'ruft', 'ModellTexturMixin', 'erbt kleid_farbe_je_stueck(), stueckfarbe(), bild_wert()'),
        ('G9folger', 'ruft', 'G9passform', 'G9passform.anwenden(): Länge und Weite auf den Käfigpunkten (punkte_zu)'),
    ]

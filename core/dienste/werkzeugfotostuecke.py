# -*- coding: utf-8 -*-
"""Werkzeugfotostuecke — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: Stücke aus Fotos und eigene Stücke.

Kleidung aus dem Netz der Fotos (Schritt „kleidung", Fotostücke), Uhr, eigenes Stück aus einem OBJ. Reine Daten
(Schema: `ProjektTemp/_wegwerf/stoff_ausbau/AUFTRAG_TOOLS.md`); gelesen von `Architektur2d3dwerkzeuge`. Jede Zeile ist
gegen den Code gelesen (03.10.2026); Zahlen tragen Fundstelle und Datum.
"""

__all__ = ['Werkzeugfotostuecke']


class Werkzeugfotostuecke:
    G = 'Genesis9/'
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'
    K = 'Kleidung/'

    KENNUNG = 'fotostuecke'
    TITEL = 'Stücke aus Fotos und eigene Stücke (Fotostücke, Uhr, OBJ)'
    EINLEITUNG = (
        'Statt ein Bibliotheksstück an das Foto zu zwingen, kann man aus dem Netz der Fotos EIGENE Genesis-Stücke bauen — '
        'Form UND Farbe aus den Fotos — und sie wie jedes Garderobenstück anziehen. Reihenfolge: 1. Schritt „kleidung“ von '
        '„Mesh to 3D“ teilt das Netz in Haut und Stücke (kleidung_maske.npz), 2. Fotostuecke.holen() baut daraus die Stücke '
        'oberteil, hose, socken (Kennung eigen_foto_…), 3. das Rezept zieht sie mit m.kleid_nur(<Kennung>) an. Zubehör '
        '(Uhr) und beliebige OBJ-Netze gehen über eigene Wege. Alle diese Stücke liegen in der eigenen Bibliothek '
        '(Hersteller EIGEN), werden nie simuliert und folgen der Haut über die Gewichte der drei nächsten Hautpunkte.')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Schritt „kleidung“: die Kleidung aus dem Netz schneiden',
         'Trennt im Netz der Fotos Haut und Kleidung (Oberteil, Hose, Socken/Schuhe, Zubehör) und legt die Maske für die '
         'Fotostücke ab.',
         'api',
         'POST /api/meshfigur/<job_id>/starten/   {"ab": "kleidung", "optionen": {"kleidung": "weich", "kleidungszug": 60, '
         '"kleidungsabstand_mm": 8}}\n'
         '→ {ok, pid, neu_eingelesen}   Ablage arbeit/kleidung_maske.npz, ergebnis/kleidung_<ohne|nur>_<vorn|seite|hinten>.png, '
         'ergebnis/kleidung.glb',
         [(A + 'meshfigur.py', 'Meshfigurendpunkte'), (D + 'meshfigurkleidung.py', 'Meshfigurkleidung'),
          (K + 'kleidungsmaske.py', 'Kleidungsmaske'), (K + 'kleidungsteilung.py', 'Kleidungsteilung'),
          (K + 'kleidungsentposen.py', 'Kleidungsentposen')],
         '„ab“ rechnet den Schritt UND alles danach (Kalibrierung, Ketten, Textur, Vorschau neu); der Lauf startet über den '
         'Arbeiter, nicht im Server. Reihenfolge der Schritte: erkennung, haar, kleidung, kalibrierung, koerper, gesicht, rest, '
         'textur, vorschau, frisur, speichern. Optionen (Meshfiguroptionen): kleidung weich (Vorgabe: der Stoff zieht schwach '
         '— die Haut liegt knapp darunter) | ignorieren | wie_haut (alte Regel); kleidungszug 0…100 % (Vorgabe 60, nur bei '
         'weich); kleidungsabstand_mm 0…40 (Vorgabe 8). Haut und Stoff trennt der Hautton der KAHLEN Stellen (Gesicht, Hände, '
         'Unterarme, Unterschenkel), nicht der von Rumpf und Oberschenkeln. Stücke nach LAGE, nicht nach Form: über der '
         'Hüftlandmarke − 4 cm Oberteil, bis 12 cm über dem Knöchel Hose, darunter Füße; ein Kleid heißt Oberteil plus Hose '
         '(Kleidungsmaske). Lauf 13.42.12 (mesh-kleidung.md, 29.09.2026): 57,5 % der Körperfläche, Oberteil 12.252 cm² '
         '(0,84–1,44 m), Hose 2.710 cm², Füße 2.951 cm², Zubehör 50 cm² (die Uhr). Ein Wegwerfskript nur für den '
         'Haarschritt liegt unter ProjektTemp/_wegwerf/meshto3d/haar_schritt.py; für „kleidung“ ist keins bekannt — '
         'ab=kleidung rechnet alles danach neu. Der Start eines Laufs steht in der Gruppe Körper (T1).'),

        ('Fotostücke bauen: Oberteil, Hose, Socken aus dem Netz der Fotos',
         'Baut aus der Kleidungsmaske drei eigene Garderobenstücke mit Form aus der angepassten Figur und Farbe aus dem Netz.',
         'python',
         "from core.dienste.fotostuecke import Fotostuecke\n"
         "stuecke = Fotostuecke(job).holen()      # job: Engine2d3dKleiderauftrag; Ablage ist Engine2d3dKleiderablage(job.kennung)\n"
         "# → {'oberteil': '<Garderobenkennung>', 'hose': '…', 'socken': '…'}  — leer ohne Kleidung oder Figur",
         [(D + 'fotostuecke.py', 'Fotostuecke'), (D + 'fotohuelle.py', 'Fotohuelle'), (D + 'huellenschnitt.py', 'Huellenschnitt'),
          (K + 'kleidungsentposen.py', 'Kleidungsentposen'), (G + 'eigenstueck.py', 'G9eigenstueck'),
          (G + 'gcfigurbau.py', 'G9gcfigurbau'), (G + 'mbkategorien.py', 'G9mbkategorien'),
          (D + 'begutachtungswerkzeug.py', 'Begutachtungswerkzeug')],
         'Läuft im Django-Prozess/Arbeitsprozess (braucht den Auftrag und seine Dateien). Voraussetzung: arbeit/'
         'kleidung_maske.npz, genesis_ende.npz, posiert.npy und das Netz des Auftrags; sonst leer mit {fehler}. Weniger als '
         '500 Flächen ist kein Stück (FLAECHEN_MIN). Ein zweiter Aufruf baut nur neu, wenn sich Netz, Maske, Figur oder '
         'FASSUNG (20, seit 02.10.2026: der Stoff liegt auf den Schultern auf) geändert haben; der Stand steht in '
         'job.ergebnis["fotostuecke"]. Die Fassung steht in der Kennung (…_f20): ein neu gebautes Stück ist ein anderes '
         'Stück. Form: FORM „huelle“ = Hülle der angepassten Figur (Fotohuelle: nächste Netzfläche bis 5 cm, Abstand 3–30 mm, '
         'Säume als ebene Linien durch Huellenschnitt) — seit Fassung 13, vorher das Netz selbst, das unter den Ärmeln riss. '
         'Dauer beim ersten Mal ~150 s (Docstring Begutachtungswerkzeug.fotostuecke), danach aus dem Auftrag. Grenzen '
         '(Docstring): warmfarbene Kleidung (rot, orange, beige) fiele mit der Haut heraus (HAUT_ABSTAND 0,10); ein Haar-Stück '
         'baut die Hüllen-Fassung nicht (nur oberteil, hose, socken). Fotostücke ersetzen die Bibliotheksstücke in der '
         'Kleiderwahl und werden nie simuliert (G9stoff: eigene Stücke, die nie simuliert werden).'),

        ('Fotostücke anziehen (Rezept)',
         'Zieht die gebauten Fotostücke an wie jedes Garderobenstück; die Kennungen kommen aus Fotostuecke.holen().',
         'rezept',
         "m.kleid_nur('eigen_foto_<kürzel>_oberteil_f20', 'eigen_foto_<kürzel>_hose_f20', 'eigen_foto_<kürzel>_socken_f20')",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (D + 'fotostuecke.py', 'Fotostuecke')],
         'Die Kennung nicht erraten: sie ist der geslugte .duf-Name, den holen() als Wert liefert (bilanz["stueck"]); '
         'Präfix eigen_foto_, danach Kürzel des Auftrags (letzte 8 Zeichen der Kennung ohne Punkte), Stückname und Fassung '
         '(so in der gemerkten Liste: eigen_foto_01123809_oberteil_f18; ältere Stände ohne _f<Fassung>). '
         'Die Automatik zieht sie selbst an (Kleiderwahl.soll, wenn befund["fotostuecke"] gesetzt ist) und lässt sie von '
         'Hülle, Weite, Zonen-Morphen und Drapieren aus (Kleiderwahl.fest: sie SIND schon die Form des Netzes). '
         'Fotofarbe über kleid_fototextur ist bei ihnen nicht nötig: Farbe kommt aus dem Netz; die Annahme, die Netzfarbe '
         'sei Foto, war bis 02.10.2026 falsch (TRELLIS-Malerei; IterationTextur). Quelle: Kleiderwahl.FOTO, Fotostuecke.'),

        ('Armbanduhr aus den Fotos',
         'Erkennt, ob und an welchem Arm die Person auf den Fotos eine Armbanduhr trägt, und baut dafür ein eigenes Stück.',
         'python',
         "from Genesis9.uhrstueck import G9uhrstueck\n"
         "G9uhrstueck.bauen(seite='l', farbe=(0.05, 0.05, 0.06))   # → Bilanz; bilanz['stueck'] z. B. 'eigen_uhr_l'\n"
         "# Erkennung: Uhrerkennung(ablage).erkennen(referenzen) → {seite: {'gefunden': bool, …}}",
         [(D + 'uhrerkennung.py', 'Uhrerkennung'), (G + 'uhrstueck.py', 'G9uhrstueck'), (G + 'eigenstueck.py', 'G9eigenstueck'),
          (D + 'begutachtungswerkzeug.py', 'Begutachtungswerkzeug')],
         'Die Runde baut es selbst (Begutachtungswerkzeug.zubehoer): erkannt wird je Arm an Querstreifen über dem Unterarm '
         '(dunkler als die Haut und kaum bunt); fehlt eine eigen_uhr_<seite> in der Garderobe, wird sie gebaut (~1 s). '
         '„links“ ist der linke Arm der PERSON (MediaPipe 15/16 Handgelenk, 13/14 Ellbogen). Form: Band um das Handgelenk '
         '(Querschnitt + 3 mm Luft) und flaches Gehäuse auf dem Handrücken, 2 cm vom Gelenk Richtung Ellbogen. Gemessen am '
         'Testauftrag 2026.10.01.12.38.09: schwarze Uhr links, rechts nichts (Docstring). Die Uhr ist ein festes Stück: '
         'keine Hülle, keine Weite, keine Zonen-Morphe, nicht drapiert.'),

        ('Eigenes Stück aus einem OBJ (Server)',
         'Lädt ein OBJ hoch, bringt es grob auf die Grundfigur, schreibt es als Genesis-Stück und rendert Proben auf Genesis '
         'und HumanBody.',
         'api',
         'POST /api/character/eigenstueck/bauen/   multipart: name, kategorie, einheit, oben, zentrieren, massstab, versatz_cm, '
         'farbe, probe, Dateien obj / mtl / textur\n'
         '→ {bilanz, proben: {genesis: {bild, pixel, teile}, humanbody: {…}}}\n'
         'GET /api/character/eigenstueck/<kennung>/<bild>/   probe_genesis9.png | probe_humanbody.png',
         [(A + 'eigenstueck.py', 'Eigenstueckapi'), (G + 'eigenstueck.py', 'G9eigenstueck'), (G + 'objleser.py', 'G9objleser'),
          (G + 'mbkategorien.py', 'G9mbkategorien'), (D + 'eigenstueckprobe.py', 'Eigenstueckprobe')],
         'name Pflicht (sonst 400, höchstens 80 Zeichen); kategorie aus G9mbkategorien.ORDNER (Vorgabe tops); einheit '
         'auto|m|dm|cm|mm; oben y|z; zentrieren „1“; massstab 0,01…100; versatz_cm −200…200; farbe #rrggbb (sonst .mtl oder '
         'Grau); probe „1“ (Vorgabe) rechnet die Bilder. Höchstens 200 MB je Datei, Namen durch SafePath.dateiname. Die '
         'Platzierung ist GROB: sie trifft Einheit und Achse und schiebt die Mitte auf die Körpermitte, zieht aber nichts an '
         'die Haut — wie gut das Stück liegt, steht in der Bilanz (Hautabstand, Punkte im Körper, Punkte fern > 15 cm). Das '
         'Formular steht auf Hilfe → Kleidung → Vergleich (unten). Kosten: nicht gemessen. Quelle: HumanBodyWeb/core/api/'
         'eigenstueck.py (25.09.2026).'),

        ('Eigenes Stück aus einem OBJ (Python)',
         'Dieselbe Rechnung ohne HTTP: OBJ lesen, platzieren, heben, gewichten, schreiben.',
         'python',
         "from Genesis9.eigenstueck import G9eigenstueck\n"
         "bilanz = G9eigenstueck.bauen('A:/…/mein_shirt.obj', 'Mein Shirt', ordner='tops', farbe=None, einheit='auto', oben='y')\n"
         "bilanz['stueck']      # Kennung in der Garderobe (eigen_… slug aus dem .duf-Namen)",
         [(G + 'eigenstueck.py', 'G9eigenstueck'), (G + 'objleser.py', 'G9objleser'), (G + 'mbkategorien.py', 'G9mbkategorien')],
         'Schreibt in die eigene Bibliothek (Hersteller EIGEN, 3DObjects/models/Genesis9/eigene_stuecke/<Kennung>) und lässt die '
         'Garderobe neu lesen (G9mbstuecke.vergessen). Die Garderobe schlüsselt nach dem geslugten .duf-Namen, nicht nach der '
         'Netzkennung des Schreibers: wer das Stück sofort holen will, nimmt stueck aus der Bilanz. Die Genesis-Lage ist die '
         'der Grundfigur G9formung({}) auf Stufe 0: Meter, Y oben, Füße 0. Ein Stück, das schon in Genesis-Lage liegt '
         '(GarmentCode-Stapel, Fotostücke), schreibt G9eigenstueck.schreiben(roh, netz, kennung, anzeige, kategorie, '
         'material, heben=False). Nicht ausprobiert (nur gelesen).'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Meshfigurkleidung', 'ruft', 'Kleidungsmaske', 'Kleidungsmaske(…).rechnen(): kleidung, stueck, haut je Fläche'),
        ('Meshfigurkleidung', 'ruft', 'Kleidungsteilung', 'Kleidungsteilung: Teilnetze „ohne Kleidung“ und „nur Kleidung“, kennzahlen()'),
        ('Begutachtungswerkzeug', 'ruft', 'Fotostuecke', 'Fotostuecke(job, ablage).holen(): fotostuecke()'),
        ('Begutachtungswerkzeug', 'ruft', 'Uhrerkennung', 'Uhrerkennung(ablage).erkennen(referenzen): zubehoer()'),
        ('Begutachtungswerkzeug', 'ruft', 'G9uhrstueck', 'G9uhrstueck.bauen(seite): fehlt eigen_uhr_<seite> in der Garderobe'),
        ('Fotostuecke', 'ruft', 'Kleidungsentposen', 'Kleidungsentposen(koerper, posiert): rechnet das Netz in die Ruhelage zurück'),
        ('Fotostuecke', 'ruft', 'Huellenschnitt', 'Huellenschnitt.halsgewichte(): Rundhals-Gewichte'),
        ('Fotostuecke', 'ruft', 'Fotohuelle', 'Fotohuelle(scan, stueck, haut, …).bauen(nummer): Form aus der Figur, Farbe aus dem Netz'),
        ('Fotohuelle', 'ruft', 'Huellenschnitt', 'Huellenschnitt.feld() und schneiden(): glatte, ebene Säume statt Treppe'),
        ('Fotostuecke', 'ruft', 'G9eigenstueck', 'G9eigenstueck.schreiben(): Stück schreiben (Hersteller EIGEN); kennung_und_name()'),
        ('Fotostuecke', 'ruft', 'G9gcfigurbau', 'G9gcfigurbau.ruhelage() und pruefen(): Ruhelage auf der Grundfigur'),
        ('Fotostuecke', 'ruft', 'G9mbkategorien', 'G9mbkategorien.fuer(ordner, name): Kategorie des Stücks'),
        ('G9uhrstueck', 'ruft', 'G9eigenstueck', 'G9eigenstueck.koerper() und bauen(): Uhr aus der Grundfigur, geschrieben wie jedes eigene Stück'),
        ('Eigenstueckapi', 'ruft', 'G9eigenstueck', 'G9eigenstueck.bauen(obj, name, …): POST bauen'),
        ('Eigenstueckapi', 'ruft', 'Eigenstueckprobe', 'Eigenstueckprobe.genesis() und humanbody(): die Probebilder'),
        ('G9eigenstueck', 'ruft', 'G9objleser', 'G9objleser.lesen(obj): Netz, UV je Ecke, Material'),
    ]

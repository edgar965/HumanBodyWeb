# -*- coding: utf-8 -*-
"""Werkzeugkleidunghilfe — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: die Hilfeseiten Kleidung.

Menü Hilfe → Kleidung (`HumanBodyWeb/ui/settings/djangobase_menue.py`) und die Klassen, die ihre Daten halten. Reine Daten
(Schema: `ProjektTemp/_wegwerf/stoff_ausbau/AUFTRAG_TOOLS.md`); gelesen von `Architektur2d3dwerkzeuge`. Jede Zeile ist
gegen den Code gelesen (03.10.2026).
"""

__all__ = ['Werkzeugkleidunghilfe']


class Werkzeugkleidunghilfe:
    A = 'HumanBodyWeb/core/api/'
    K = 'Assets/kleidung/'

    KENNUNG = 'kleidunghilfe'
    TITEL = 'Hilfeseiten Kleidung (Menü Hilfe → Kleidung)'
    EINLEITUNG = (
        'Die Seiten unter Hilfe → Kleidung sind die Dokumentation der Kleidungswege dieses Projekts. Jede hat dieselbe '
        'Regel: Zahlen und Zustände stehen in einer Datenklasse (Assets/kleidung/*.py), nicht im HTML — „eine Zahl im HTML ist '
        'eine Behauptung, die niemand mehr nachrechnet“. Wer wissen will, wie Kleidung zum Genesis-Modell kommt, liest '
        'zuerst „Genesis“ und „2D3D Kleider“; wer die Messwerte zum Anliegen an die Haut braucht, „Fitting“. Die Seiten '
        'sind reine Anzeige (GET), sie ändern nichts. Die Seite „Körperphysik“ (Velocity Skinning, '
        '/hilfe/kleidung/koerperphysik/) betrifft den Körper, nicht Kleider am Genesis-Modell, und steht hier nicht.')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Hilfe → Kleidung → Allgemein',
         'Die sechs Kleidungsverfahren nebeneinander (fünf nehmen ein fertiges Netz und bringen es an einen Körper, eines '
         'konstruiert das Stück) und warum MakeHuman in Millisekunden anzieht und GarmentCode in Sekunden.',
         'seite',
         '/hilfe/kleidung/   (Menü Hilfe → Kleidung → Allgemein)',
         [(A + 'hilfe_kleidung.py', 'KleidungAllgemein'), (K + 'verfahren.py', 'Kleidungsverfahren'),
          (K + 'tempo.py', 'Kleidungstempo')],
         'Daten aus Kleidungsverfahren.alle() und unterschied(), Tempo aus Kleidungstempo (08.09.2026: der Unterschied ist '
         'ein anderes VERFAHREN — MakeHuman rechnet keine Physik; der GPU→CPU-Transfer je Frame in run_sim kostet gemessen '
         '0,8 %). Jede Zahl trägt ihre Quelle in beleg; was nicht gemessen ist, steht ausdrücklich da.'),

        ('Hilfe → Kleidung → GarmentCode',
         'Der GarmentCode-Weg Schritt für Schritt (Schnitt, Drapierung, Nacharbeit, Anziehen; drei Figurarten) mit den '
         'Testfällen.',
         'seite',
         '/hilfe/kleidung/garmentcode/   (Menü Hilfe → Kleidung → GarmentCode)',
         [(A + 'hilfe_garmentcode.py', 'KleidungGarmentcode'), ('Assets/GarmentCode/messreihen.py', 'Garmentcodemessung')],
         'Die Messwerte kommen bei jedem Aufruf frisch aus den YAML-Dateien (Garmentcodemessung); fehlt eine, sagt die Seite '
         'das, statt eine leere Tabelle zu zeigen, die wie „alles gut“ aussieht. 165 gemessene Kombinationen '
         '(Docstring KleidungGarmentcode). Nachgezogen 25.09.2026 gegen den Code (Dateien umgezogen, Nacharbeit als eigener '
         'Schritt, Anziehen über Dreiecke).'),

        ('Hilfe → Kleidung → Genesis',
         'Die Daz-Garderobe gegen die GarmentCode-Kleiderbibliothek: warum die beiden nicht zusammenpassen, der DSON-Leser, '
         'der Vergleich und der Weg, ein MakeHuman-Stück in ein Genesis-Asset zu verwandeln.',
         'seite',
         '/hilfe/kleidung/genesis/   (Menü Hilfe → Kleidung → Genesis)',
         [(A + 'hilfe_genesis.py', 'KleidungGenesis'), (K + 'genesis.py', 'Kleidungsgenesis')],
         'Abschnitte: Bibliotheken, warum nicht, Leser, Vergleich, Weg, Stand, Risiken, Daz-Stücke (Kleidungsgenesis). Befunde '
         'vom 25.09.2026: Leser gelesen, DSON-Aufbau am G9 Base Shirt (G9BaseShirt.dsf, UV-Set default.dsf), Kleiderbibliothek '
         'und Paarungen (G9hbknochen, mblab_ankerung). Edgar (25.09.2026): „bisher hat noch jede Anpassung HumanBody → '
         'Genesis nicht funktioniert“. Vorschlag steht als Vorschlag.'),

        ('Hilfe → Kleidung → 2D3D Kleider',
         'Der Plan hinter „Haar – Generisch“: der Bestand der 18 Frisuren, warum sie kein gemeinsames Netz haben, die drei '
         'Schichten, was die Engine verstellt, Gemessenes und Offenes.',
         'seite',
         '/hilfe/kleidung/engine2d3dkleider/   (Menü Hilfe → Kleidung → 2D3D Kleider)',
         [(A + 'hilfe_engine2d3dkleider.py', 'KleidungEngine2d3dKleider'),
          (K + 'engine2d3dkleider.py', 'Kleidungsengine2d3dkleider')],
         'Abschnitte (Kleidungsengine2d3dkleider): haare() (die 18 Frisuren mit Reglerzahl, Stilen, Farben, Netzen, Klon, '
         'Knochen), mehrteilig(), klone(), warum_nicht(), schichten(), wo(), achsen(), gemessen(), engine(). Die Tabelle '
         'HAARE dort ist die Quelle für das Frisur-Inventar der Gruppe „Haar“. Stand der Zahlen: 30.09.2026 (ACHSEN_STAPEL_S 45, '
         'ASSET_REGLER 412, HAAREIGEN_S 64).'),

        ('Hilfe → Kleidung → Vergleich',
         'MakeHuman, Genesis 9, GarmentCode und UMA Schritt für Schritt (Tabelle), der komplette Ablauf je Bibliothek mit '
         'Klassen und Dateien, die Empfehlung — und das Formular „Eigenes Stück aus OBJ“.',
         'seite',
         '/hilfe/kleidung/vergleich/   (Menü Hilfe → Kleidung → Vergleich)',
         [(A + 'hilfe_kleidungvergleich.py', 'KleidungVergleich'), (K + 'schrittvergleich.py', 'Kleidungsschritte'),
          (K + 'ablaufvergleich.py', 'Kleidungsablauf'), (K + 'empfehlung.py', 'Kleidungsempfehlung')],
         'Tabelle nach djangoBase-Format (ziehbare Breiten, Abschnittszeilen, Sortieren für alle Spalten aus: die Zeilen sind '
         'eine Abfolge von Schritten). Laufzeiten sind die in Modulköpfen und Rules gemessenen, nicht neu gemessen '
         '(Kleidungsschritte). Das Formular unten ruft POST /api/character/eigenstueck/bauen/ (Gruppe „Stücke aus Fotos und '
         'eigene Stücke“). Die Empfehlung ist eine Architekturempfehlung, keine Messreihe (Kleidungsempfehlung).'),

        ('Hilfe → Kleidung → Neu',
         'Analyse der fünf Systeme (UMA, MakeHuman, GarmentCode, Genesis, HumanBody) und der Stufenplan für „Unified“.',
         'seite',
         '/hilfe/kleidung/neu/   (Menü Hilfe → Kleidung → Neu)',
         [(A + 'hilfe_neu.py', 'KleidungNeu'), (K + 'vergleich.py', 'Vergleich')],
         'Antwort in einem Satz: zusammenführbar sind die fünf Welten nicht über ein gemeinsames NETZ (vier unverträgliche '
         'Topologien), sondern über die Schicht darüber — und seit 08.09.2026 auch darunter, weil UMAs Konformer in Python '
         'vorliegt (Docstring KleidungNeu). Bestände laut Docstring von Vergleich: UMA 912 Assets, MakeHuman 1.280 Targets, 165 '
         '.mhclo, GarmentCode 8 Katalogstücke (15 am 08.09.2026, seit dem Umbau auf Formen 8).'),

        ('Hilfe → Kleidung → Kleiderphysik',
         'Welcher offene Code Stoff auf einem GEHENDEN Körper rechnen kann (MP4-Export des Theatre-Moduls) und was davon auf '
         'dieser Maschine gemessen wurde.',
         'seite',
         '/hilfe/kleidung/physik/   (Menü Hilfe → Kleidung → Kleiderphysik)',
         [(A + 'hilfe_kleiderphysik.py', 'KleidungPhysik'), (K + 'physik.py', 'Kleiderphysik')],
         'Randbedingung Edgar (10.09.2026): „blenderCloth nutze ich nicht, garmentCode ist bisher am besten“ — Blender steht '
         'dort nur noch als Messzeile, nicht als Empfehlung (Kleiderphysik). Abschnitte: Bestand, Kandidaten, Messaufbau, '
         'Messung, Kette. Das ist der Hintergrund für „Blender nur nach Ansage“ (Gruppe „Drapieren …“). Die eigenen '
         'Löser (Newton, Stoffsolver) kamen nach dieser Seite dazu und stehen in Hilfe → Architektur → 2D3D.'),

        ('Hilfe → Kleidung → Fitting',
         'Warum Haut durch Kleidung kam, wie andere es lösen und die vier Schichten (Maske, Oberflächenbindung, Kapseln, '
         'Abnahme) mit Stand und Messwerten.',
         'seite',
         '/hilfe/kleidung/fitting/   (Menü Hilfe → Kleidung → Fitting)',
         [(A + 'hilfe_fitting.py', 'KleidungFitting'), (K + 'fitting.py', 'Kleidungsfitting')],
         'Abschnitte (Kleidungsfitting): vorfaelle, ursachen, andere, schichten, abnahme, stand, nicht, quellen; KOLLISION_MM '
         'steht in der Klasse. Anlass Edgar 21.09.2026: „Mach ein besseres Konzept, da wir dieses Problem schon 20 Mal '
         'hatten“. Die Abnahme rechnet der Befehl manage.py durchschimmern_probe (Gruppe „Bau ohne Browser“) — NICHT '
         'nebenbei starten. Konzept: Docu/konzepte/2026-09-21_kleidung-ohne-durchschimmern-konzept.md.'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('KleidungAllgemein', 'ruft', 'Kleidungsverfahren', 'Kleidungsverfahren.alle() und unterschied(): die sechs Verfahren'),
        ('KleidungAllgemein', 'ruft', 'Kleidungstempo', 'Kleidungstempo: Tempo MakeHuman gegen GarmentCode'),
        ('KleidungGarmentcode', 'ruft', 'Garmentcodemessung', 'Garmentcodemessung: Messwerte frisch aus den YAML-Dateien'),
        ('KleidungGenesis', 'ruft', 'Kleidungsgenesis',
         'bibliotheken(), warum_nicht(), leser(), vergleich(), weg(), stand(), risiken(): die Tabellen'),
        ('KleidungEngine2d3dKleider', 'ruft', 'Kleidungsengine2d3dkleider',
         'haare(), mehrteilig(), klone(), warum_nicht(), schichten(), wo(), achsen(), gemessen(), engine()'),
        ('KleidungVergleich', 'ruft', 'Kleidungsschritte', 'Kleidungsschritte: die Tabelle der vier Bibliotheken'),
        ('KleidungVergleich', 'ruft', 'Kleidungsablauf', 'Kleidungsablauf: der komplette Weg mit Klassen und Dateien'),
        ('KleidungVergleich', 'ruft', 'Kleidungsempfehlung', 'Kleidungsempfehlung: welcher Weg trägt'),
        ('KleidungNeu', 'ruft', 'Vergleich', 'Vergleich: Stammdaten der fünf Welten und des Stufenplans'),
        ('KleidungPhysik', 'ruft', 'Kleiderphysik', 'Kleiderphysik.bestand(), kandidaten(), messaufbau(), messung()'),
        ('KleidungFitting', 'ruft', 'Kleidungsfitting',
         'vorfaelle(), ursachen(), andere(), schichten(), abnahme(), stand(), nicht(), quellen()'),
    ]

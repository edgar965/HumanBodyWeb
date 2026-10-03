# -*- coding: utf-8 -*-
"""Werkzeuggarderobe — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: die Garderobe (Bibliothek, Kategorien, Nachbau).

Reine Daten (Schema: `ProjektTemp/_wegwerf/stoff_ausbau/AUFTRAG_TOOLS.md`); gelesen von `Architektur2d3dwerkzeuge`.
Jede Zeile ist gegen den Code gelesen (03.10.2026); Zahlen tragen Fundstelle und Datum.
"""

__all__ = ['Werkzeuggarderobe']


class Werkzeuggarderobe:
    G = 'Genesis9/'
    A = 'HumanBodyWeb/core/api/'

    KENNUNG = 'garderobe'
    TITEL = 'Garderobe: Bibliothek, Kategorien, Stücke nachbauen'
    EINLEITUNG = (
        'Die Garderobe ist die Liste aller Stücke, die ein Genesis-9-Modell tragen kann: Daz-Bibliothek (Kleidung, Haare, '
        'Requisiten, auch die Klone Genesis 1, 2, 3, 8), dazu die eigene Bibliothek (MakeHuman-Stücke, GarmentCode-Stücke, '
        'eigene Stücke). Jedes Stück hat eine Kennung (id), der geslugte .duf-Name: Daz ohne festes Präfix (g9_base_shirt, '
        'angie_jeans, kin_hair), mb_… MakeHuman, gc_… GarmentCode, eigen_… eigene. '
        'Reihenfolge: 1. die Liste lesen und die Kennung finden, 2. das Stück anziehen (Gruppen „Kleider anziehen …“, '
        '„Haar“), 3. bei Bedarf Stücke nachbauen (Zeile „MakeHuman-/GarmentCode-Bibliothek als Genesis-Stücke“ oder die '
        'Gruppe „Stücke aus Fotos und eigene Stücke“). Die Daz-Bibliothek wird nie beschrieben; Edgars Einteilung und alle '
        'eigenen Stücke liegen daneben unter 3DObjects/Genesis9/.')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Garderobe in Python lesen',
         'Liest die Stücke der Garderobe: Liste, ein Eintrag, die Teile eines Stücks.',
         'python',
         "from Genesis9.garderobe import G9garderobe\n"
         "G9garderobe.liste()                    # [{id, name, art, kategorie?, regler, varianten, zeigbar, …}]\n"
         "G9garderobe.eintrag('g9_base_shirt')   # ein Eintrag oder None\n"
         "G9garderobe.teile('g9_base_shirt')     # [(G9folger, lage)] — die Teile mit ihrer Hautbindung",
         [(G + 'garderobe.py', 'G9garderobe'), (G + 'garderobeeintrag.py', 'G9garderobeeintrag')],
         'Braucht die Daz-Bibliothek (G9pfade.vorhanden). Art kleidung, haar, requisit (ORDNER Clothing, Hair, Props); ein Stück '
         'ist eine .duf vom Typ wearable, ein Stück ohne Flächen und Stränge steht mit zeigbar: false und Grund in der Liste. '
         'Haare: das Pixie-Haar ist STRANGHAAR (236.136 Punkte, keine Flächen). Die Liste ist eine Ablage je Bibliotheksstand '
         '(G9listenablage); G9garderobe.vergessen() lässt sie neu lesen. Quelle: Genesis9/garderobe.py.'),

        ('Kategorien lesen und verschieben (Server)',
         'Liest Edgars Einteilung der Garderobe in Kategorien (wie bei GarmentCode) oder verschiebt ein Stück in eine andere.',
         'api',
         'GET /api/character/genesis9-figur/garderobe/kategorien/\n'
         '→ {kategorien: [Name], zuordnung: {kennung: Name}}\n'
         'POST /api/character/genesis9-figur/garderobe/kategorien/   {kennung, kategorie}  → derselbe Stand danach',
         [(A + 'g9garderobekategorien.py', 'G9garderobekategorienapi'), (G + 'garderobekategorien.py', 'G9garderobekategorien'),
          (G + 'dazkategorien.py', 'G9dazkategorien'), (G + 'garderobe.py', 'G9garderobe')],
         '400 bei untauglichem Namen (höchstens 40 Zeichen), 404 bei unbekanntem Stück. Die Einteilung liegt NEBEN der '
         'Bibliothek (3DObjects/Genesis9/garderobe_kategorien.json); wer nicht in zuordnung steht, gehört zur Vorgabe aus '
         'Daz’ Metadaten (Runtime/Support/*.dsx: Kategorie vor ContentType). Vorgaben in dieser Reihenfolge: Oberteile, '
         'Hosen, Shorts, Röcke, Kleider, Anzüge, Outfits, Unterwäsche, Schuhe, Kopfbedeckung, Rüstung, Zubehör, Haare, '
         'Requisiten (G9dazkategorien.REIHENFOLGE); eine eigene Kategorie lebt, solange ein Stück darin liegt. Stand '
         '20.09.2026: alle 121 Stücke der damaligen Bibliothek haben einen Eintrag (genesis9-garderobe.md). Ein verschobenes '
         'Stück wandert in den Sammeleintrag „Kleidung – Generisch“ der neuen Kategorie mit.'),

        ('Stück in eine andere Kategorie legen (Python)',
         'Dasselbe wie der POST, ohne HTTP; Zurücksetzen auf die Vorgabe nimmt den Eintrag aus zuordnung.',
         'python',
         "from Genesis9.garderobekategorien import G9garderobekategorien\n"
         "G9garderobekategorien.laden()     # {kategorien, zuordnung}\n"
         "G9garderobekategorien.verschieben('g9_base_shirt', 'Outfits', vorgabe='Oberteile')",
         [(G + 'garderobekategorien.py', 'G9garderobekategorien'), (G + 'dazkategorien.py', 'G9dazkategorien')],
         'ValueError bei untauglichem Namen. vorgabe = die Vorgabekategorie des Stücks (G9garderobekategorien.vorgabe(eintrag)); '
         'ist der Zielname die Vorgabe, verschwindet der Eintrag aus zuordnung. Das Ergebnis ist Edgars Entscheidung und '
         'gehört nicht in Skripte, die „mal eben“ aufräumen. Quelle: Genesis9/garderobekategorien.py.'),

        ('Kategorien im Browser (Kontextmenü)',
         'Zeigt die Garderobe nach Kategorien und lässt ein Stück per Kontextmenü verschieben.',
         'seite',
         'Szene /Charakter/ (Menü Dashboard → Charakter) → Reiter Assets → Genesis: Kategorien aufklappen; Rechtsklick auf ein '
         'Stück → „Verschieben nach …“ oder „Neue Kategorie …“',
         [(A + 'g9garderobekategorien.py', 'G9garderobekategorienapi'), (G + 'garderobekategorien.py', 'G9garderobekategorien')],
         'Frontend: HumanBodyWeb/static/viewer/charakter/genesis9/genesis9garderobekategorien.js (Kontextmenü Kontextmenue) '
         'und genesis9garderobe.js. Alle Kategorien sind beim Laden zu, offen nur die des gewählten Stücks (Vorgabe seit '
         '21.09.2026, nach jedem Auswahlwechsel genau diese; kein localStorage-Gedächtnis — Edgar 30.09.2026: „das hatte ich '
         'schon 10 Mal in Auftrag gegeben“, engine2d3dkleider.md). Der Fehler „Kategorie nicht gefunden“ bei Edgars Tab war '
         'ein seit Stunden offener Tab mit altem Bündel (genesis9-garderobe.md, 21.09.2026): erst messen, was der Server '
         'liefert.'),

        ('MakeHuman-/GarmentCode-Bibliothek als Genesis-Stücke bauen',
         'Schreibt jedes Stück der MakeHuman-Bibliothek (164 Ordner, 165 Stücke) als Genesis-9-Stück in die eigene Bibliothek.',
         'cli',
         'cd A:/3DTools && python14/Scripts/python.exe -m Genesis9.mbstuecke',
         [(G + 'mbstuecke.py', 'G9mbstuecke'), (G + 'mhklon.py', 'G9mhklon'), (G + 'mhstueck.py', 'G9mhstueck'),
          (G + 'mbkategorien.py', 'G9mbkategorien')],
         'Der Weg je Stück: Klon (G9mhklon: Knochenrahmen, nichtstarres ICP) → auswerten (G9mhstueck: Material, Stärke, '
         'Glanz) → aus der Haut heben (3 mm) → Gewichte der 3 nächsten Hautpunkte → DSON schreiben. alle() fängt Fehler je '
         'Stück ab und meldet sie, statt den Lauf abzubrechen (106 von 165 schlugen einmal an einem .mhclo-Parser fehl, '
         '25.09.2026). Läuft über die GANZE Bibliothek, schreibt in die eigene Bibliothek (3DObjects/Genesis9/bibliothek) '
         'und belegt den Rechner: nur auf Ansage; Dauer nicht gemessen. Danach die Garderobe neu lesen lassen '
         '(G9mbstuecke.vergessen(); der laufende Server hielt die Liste im Speicher und wurde bisher neu gestartet — '
         'ein Neustart ist hier nicht Sache dieser Seite). Kategorie aus G9mbkategorien (Name schlägt Ordner: suit/uniform → '
         'Anzüge, armor → Rüstung). Die GarmentCode-Stücke baut ein anderer Befehl (Gruppe „GarmentCode-Katalog …“).'),

        ('Garderobe neu lesen lassen (Python)',
         'Verwirft die gemerkten Listen, Dokumente und Folger, nachdem ein Stück geschrieben wurde.',
         'python',
         "from Genesis9.mbstuecke import G9mbstuecke\n"
         "G9mbstuecke.vergessen()    # G9dson, G9folger, G9garderobe, G9dazkategorien",
         [(G + 'mbstuecke.py', 'G9mbstuecke'), (G + 'garderobe.py', 'G9garderobe'), (G + 'dazkategorien.py', 'G9dazkategorien')],
         'Die Garderobe schlüsselt nach dem geslugten .duf-Namen, nicht nach der Netzkennung des Schreibers: ein geschriebenes '
         'Stück holt man mit bilanz["stueck"]. Für eigene Stücke genügt das Vergessen, kein Serverneustart '
         '(genesis9-garderobe.md, 25.09.2026); G9garderobe.liste() liest außerdem neu, wenn sich die .dsx der eigenen Wurzel '
         'ändern (G9eigenstand, haar.md 29.09.2026: „Haar Eigen“ schreibt der Arbeitsprozess).'),

        ('Regel: Daz-Bibliothek nie beschreiben, eigene Stücke in zweiter Wurzel',
         'Hält fest, wohin Stücke geschrieben werden dürfen.',
         'regel',
         'Daz-Bibliothek nur lesen. Eigene Stücke: 3DObjects/Genesis9/bibliothek (Daz-Aufbau), Ablagen daneben: '
         'gc_stuecke/, eigene_stuecke/, kleidmorphe/, haarachsen/, haarzusatz/, kleidtexturen/.',
         [(G + 'garderobe.py', 'G9garderobe'), (G + 'eigenstand.py', 'G9eigenstand')],
         'G9pfade.finden sucht jede Adresse in beiden Wurzeln (Daz zuerst); Einträge aus der zweiten tragen eigen. Die '
         'Kategorie eines eigenen Stücks steht in einer eigenen .dsx. Ein Bestandsschlüssel ändert sich nur, wenn es eigene '
         'Dateien gibt — sonst baut jede Ablage neu (genesis9-garderobe.md, 25.09.2026). Ablagen, die mehrere Läufe '
         'beschreiben, tragen den Namen der Fassung (…_f1): sonst liest ein Lauf still die Datei eines anderen '
         '(artefakte-benennen). Fehlt die Datei: kein Ergebnis und Warnung im Log, nie still die eines anderen Laufs.'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('G9garderobe', 'ruft', 'G9garderobeeintrag', 'G9garderobeeintrag.lesen(), regler(), varianten(), stile(): der Eintrag je .duf'),
        ('G9garderobe', 'ruft', 'G9eigenstand', 'G9eigenstand: liest neu, wenn sich die .dsx der eigenen Wurzel ändern'),
        ('G9garderobe', 'ruft', 'G9garderobekategorien', 'G9garderobekategorien.kategorie(eintrag): erkennt Schuhe in teile() (starre Zehen)'),
        ('G9garderobekategorien', 'ruft', 'G9dazkategorien', 'G9dazkategorien.REIHENFOLGE und vorgabe(): Vorgabekategorien'),
        ('G9garderobekategorienapi', 'ruft', 'G9garderobekategorien', 'laden() für GET, verschieben(kennung, kategorie, vorgabe) für POST'),
        ('G9garderobekategorienapi', 'ruft', 'G9garderobe', 'G9garderobe.eintrag(kennung): 404 bei unbekanntem Stück'),
        ('G9mbstuecke', 'ruft', 'G9mhklon', 'G9mhklon: Klon der MakeHuman-Fläche auf Genesis (Knochenrahmen, ICP)'),
        ('G9mbstuecke', 'ruft', 'G9mhstueck', 'G9mhstueck(verzeichnis, mhclo_datei): Stück auswerten, Material, Stärke, Glanz'),
        ('G9mbstuecke', 'ruft', 'G9mbkategorien', 'G9mbkategorien.fuer(ordner, name): Kategorie des geschriebenen Stücks'),
        ('G9mbstuecke', 'ruft', 'G9garderobe', 'G9garderobe.vergessen(): vergessen() nach dem Schreiben'),
        ('G9mbstuecke', 'ruft', 'G9dazkategorien', 'G9dazkategorien.vergessen(): vergessen() nach dem Schreiben'),
    ]

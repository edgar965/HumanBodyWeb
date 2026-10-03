# -*- coding: utf-8 -*-
"""Werkzeugkleidform — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: Kleider formen (eigene Morphe).

Reine Daten (Schema: `ProjektTemp/_wegwerf/stoff_ausbau/AUFTRAG_TOOLS.md`); gelesen von `Architektur2d3dwerkzeuge`.
Jede Zeile ist gegen den Code gelesen (03.10.2026); Zahlen tragen Fundstelle und Datum.
"""

__all__ = ['Werkzeugkleidform']


class Werkzeugkleidform:
    G = 'Genesis9/'
    A = 'HumanBodyWeb/core/api/'

    KENNUNG = 'kleidform'
    TITEL = 'Kleider formen: eigene Morphe, Ort, Ring, Hülle, Welle, Pinsel'
    EINLEITUNG = (
        'Ein Daz-Stück hat nur die Morphe, die Daz mitliefert. Was ein Foto verlangt — längerer Saum, weiter Bauch, '
        'aufgestellter Kragen — gibt es dort nicht; hier entsteht es als EIGENER MORPH: Deltas auf dem Käfig des Stücks, '
        'abgelegt neben der Bibliothek (3DObjects/Genesis9/kleidmorphe/<kennung>__<name>_f1.npz), linear wie jeder Daz-Morph, '
        'gestellt über den Regler <kennung>.eigen.<name> (−2…2, Gruppe „Eigene Morphe“). Reihenfolge: 1. Morph bauen '
        '(morph_neu, morph_ort, kleid_welle, kleid_ring, kleid_huelle — jeder Aufruf baut UND stellt auf wert), 2. mit '
        'morph_wert nachstellen. Alle brauchen die Daz-Bibliothek und ein zeigbares Stück (sonst ValueError „… ist kein '
        'zeigbares Stück der Garderobe“). Gerechnet wird auf der Grundfigur in der Lage der Bühne (Meter, Y oben, Füße 0); '
        'ein zweiter Bau desselben Namens ersetzt den ersten. Der Ort ist ein Wörterbuch: {band: (von, bis)} Höhenanteil, '
        '{sektor: (a°, b°)} um die Senkrechte (0 vorn = +z, positiv links = +x, über ±180 erlaubt), {landmarke: name, '
        'radius_cm}, {kugel: [x, y, z], radius_cm}, {welle: {laenge_cm, richtung}}; die Gewichte multiplizieren sich.')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Neuen Morph in einer Richtung bauen',
         'Baut einen Morph an einem Stück oder einer Frisur: Höhenbereich, Richtung, Weg, optional eine Seite; stellt ihn.',
         'rezept',
         "m.morph_neu('kleidung', 'g9_base_shirt', 'saum_lang', richtung='unten', weg_cm=3.0, von=0.0, bis=0.2)",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'kleidmorphe.py', 'G9kleidmorphe')],
         'art haar|kleidung; richtung aussen|innen (radial von der Achse), oben|unten|vorn|hinten oder [x, y, z]; von/bis = '
         'Höhenbereich am Stück (0 unten, 1 oben); seite links|rechts (Seite der Figur, links = +x) oder None; weich = '
         'Hermite-Auslauf als Anteil der Stückhöhe. Name: Kleinbuchstaben, Ziffern, Unterstrich, beginnt mit Buchstaben, '
         'höchstens 41 Zeichen (G9kleidmorphe.NAME), sonst ValueError. Der Regler steht danach auch in der Garderobenliste '
         'und in beiden Sammeleinträgen. Kosten: nicht gemessen. Quelle: Genesis9/kleidmorphe.py (30.09.2026).'),

        ('Morph an einem Ort bauen',
         'Baut einen Morph, der nur an einem Ort wirkt (Band × Sektor, Kugel um eine Landmarke, Welle) und der Hautnormale '
         'folgen kann — Beule am Bauch, Saum an einer Seite.',
         'rezept',
         "m.morph_ort('kleidung', 'g9_base_shirt', 'bauch_vor', {'landmarke': 'bauch', 'radius_cm': 8}, weg_cm=2.0, richtung='haut')\n"
         "m.morph_ort('kleidung', 'g9_base_shirt', 'links_weit', {'band': (0.0, 1.0), 'sektor': (40, 140)}, weg_cm=2.0)",
         [(G + 'modellform.py', 'ModellFormMixin'), (G + 'kleidmorphe.py', 'G9kleidmorphe'),
          (G + 'ortsmorph.py', 'G9ortsmorph')],
         'richtung haut = Normale des nächsten Hautpunkts der Grundfigur (auch aussen|innen|oben|unten|vorn|hinten|[x, y, z]); '
         'weg_cm darf negativ sein. Landmarken (G9ortsmorph.landmarken, einmal je Prozess, 0,7 s): scheitel, stirn, nacken, '
         'schlaefe_l/_r, ohr_l/_r, kinn, brust, ruecken, bauch, taille_l/_r, po, huefte_l/_r, schulter_l/_r, knie_l/_r, '
         'wade_l/_r, ellbogen_l/_r. Ohne Band entscheidet bei Kugel und Landmarke die Kugel allein. Gemessen 30.09.2026 '
         '(ortsmorphe.md): „Links“ am Base Shirt 3.732 Punkte, alle x > 0, 19 mm. Fallen: das Base Shirt ändert beim Bau mit '
         'Welle, Ring oder Hülle seine Punktzahl (7.334 → 7.347/7.398/7.455), ein Punktvergleich je Nummer geht dort nicht; '
         'ein Morph am Shirt verschiebt die Shorts darunter mit (bis 14 mm, Lagenrechnung; ortsmorphe.md, 01.10.2026).'),

        ('Eigenen Morph nachstellen',
         'Stellt einen schon gebauten eigenen Morph (eigen.<name>) auf einen Wert; auch für die festen Regler.',
         'rezept',
         "m.morph_wert('kleidung', 'g9_base_shirt', 'saum_lang', 0.5)",
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern')],
         'Wert linear, Regler −2…2 (negativ kehrt die Richtung um). art haar legt den Wert in m.haar, sonst in m.kleidung; '
         'der Schlüssel ist <kennung>.eigen.<name>. Ein Name ohne gebaute Ablage wirkt nicht (G9kleidmorphe.deltas gibt '
         'None). In einer Runde heißen Morphe, die aus den Fotos eines Auftrags entstehen, <name>_<auftrag> '
         '(ModellFormMixin.auftragsname) — mit m.vorhanden(werte, schluessel) auffindbar.'),

        ('Welle: Großfalten an einem Ort',
         'Legt eine Welle (Wellenlänge, Tiefe) über einen Ort des Stücks — Falten am Saum oder längs.',
         'rezept',
         "m.kleid_welle('g9_base_shirt', 'falten_saum', {'band': (0.0, 0.25)}, laenge_cm=6.0, tiefe_cm=1.0, richtung='quer')",
         [(G + 'modellform.py', 'ModellFormMixin'), (G + 'ortsmorph.py', 'G9ortsmorph'),
          (G + 'kleidmorphe.py', 'G9kleidmorphe')],
         'Wellenlänge mindestens 3 cm auf dem Käfig (Docstring); tiefe_cm = Ausschlag entlang der Hautnormale. richtung '
         'quer = Welle um das Stück, laengs = über die Höhe — bei kleid_falten (Gruppe „Textur“) ist es umgekehrt '
         'benannt, nicht verwechseln. Für Feinfalten in der Normalkarte kleid_falten nehmen, nicht die Welle.'),

        ('Ring: Weite eines Höhenrings',
         'Setzt einen Höhenring des Stücks auf ein Vielfaches des Körperrings darunter (parametrisch wie ein Ringmantel).',
         'rezept',
         "m.kleid_ring('g9_base_shirt', 'huefte_weit', 0.3, weite=1.3)",
         [(G + 'modellform.py', 'ModellFormMixin'), (G + 'kleidring.py', 'G9kleidring'),
          (G + 'kleidmorphe.py', 'G9kleidmorphe')],
         'hoehe 0 unten … 1 oben; weite × Halbbreite, tiefe × Halbtiefe des Körperrings (1,0 = am Körper — die Kollision hebt '
         'auf 3 mm —, 1,3 = 30 % weiter); sektor (a°, b°) nur dort; band 0,06 Ringhöhe. Grenze: der Körperring nimmt Rumpf, '
         'Becken und Beine ohne Arme — an Schulter- und Ärmelhöhe zählt der Stückring die Ärmel mit, dort ist der Faktor '
         'nur ein Anhalt (Modulkopf kleidring.py). Gebaut für Rumpf unter der Achsel, Rock, Hosenbein.'),

        ('Hülle: dem Umriss der Fotos folgen',
         'Zieht jeden Ringpunkt des Stücks waagerecht bis an den Rand des Sichtkörpers (Silhouetten der Fotos).',
         'rezept',
         "m.kleid_huelle('g9_base_shirt', staerke=0.7, von=0.0, bis=1.0)",
         [(G + 'modellform.py', 'ModellFormMixin'), (G + 'rezeptumgebung.py', 'Rezeptumgebung'),
          (G + 'huellenmorph.py', 'G9huellenmorph')],
         'Braucht die Runde (Rezeptumgebung.sicht): ohne Sichtkörper ValueError. staerke 0,7 ist im Kostüm-Weg gemessen '
         '(1,0 → 0,2659, 0,7 → 0,2666, mit 0,7 bleibt der Rock glatter); der Weg je Punkt ist auf 15 cm gedeckelt '
         '(HOECHSTENS_M), damit ein Loch in der Silhouette den Stoff nicht 40 cm zieht. Der Name ist huelle (in einer '
         'Runde huelle_<auftrag>). Die Automatik lässt kleine Stücke (Socken, Uhr) und Fotostücke aus: die Hülle zog die '
         'Socken zwischen die Füße (Runde 14, 01.10.2026, Kleiderwahl.fest) — von Hand bleibt es möglich.'),

        ('Feste Form-Regler (11 je Stück)',
         'Elf fertig definierte Ortsmorphe an jedem Kleidungsstück, sofort in jeder Liste; bauen beim ersten Zug.',
         'rezept',
         "m.morph_wert('kleidung', 'g9_base_shirt', 'form_weite_unten', 1.0)\n"
         "# Namen: form_weite_unten, form_weite_mitte, form_weite_oben, form_vorn, form_hinten, form_links, form_rechts,\n"
         "#        form_saum, form_oben_auf, form_falten_saum, form_falten_laengs",
         [(G + 'standardmorphe.py', 'G9standardmorphe'), (G + 'kleidmorphe.py', 'G9kleidmorphe'),
          (G + 'modellmitkleidern.py', 'ModellMitKleidern')],
         'Im UI: Szene (/Charakter/) → Assets → Genesis → Stück → Gruppe „Form (Ort)“. Wert −2…2, negativ kehrt um '
         '(Weite −1 = enger). Der erste Zug baut die Ablage (G9kleidmorphe.deltas ruft G9standardmorphe.bauen): Base Shirt '
         '„Links“ erster Zug 0,42 s, danach 22 ms (Chrome, Netz-Endpunkt, 30.09.2026, ortsmorphe.md). Der Lazy-Bau darf '
         'nicht das Ablageschloss halten (Deadlock, _bauschloss). Die Haar-Entsprechung (13 Regler „Operationen“) steht in '
         'der Gruppe „Haar formen“.'),

        ('Freies Morph-Formular (Server)',
         'Baut einen Ortsmorph mit eigenem Namen an einem Stück — dieselbe Rechnung wie morph_ort, von der Szene aus.',
         'api',
         "POST /api/character/genesis9-figur/garderobe/<kennung>/morph/\n"
         "{name, ort: {band: [von, bis], sektor: [a, b], landmarke, radius_cm, kugel: [x, y, z], welle: {laenge_cm, richtung}},\n"
         " richtung, weg_cm, seite, weich}\n"
         "→ {regler: {name: 'eigen.<name>', anzeige, min, max, vorgabe, gruppe}, brief, form}",
         [(A + 'g9morphformular.py', 'G9morphformularapi'), (G + 'kleidmorphe.py', 'G9kleidmorphe'),
          (G + 'ortsmorph.py', 'G9ortsmorph')],
         'Name Kleinbuchstaben/Ziffern/Unterstrich, sonst 400. Grenzen im Server gesäubert: weg_cm −20…20, weich 0,01…0,5, '
         'radius_cm 0,5…60, Wellenlänge 1…60 cm; unbekannte Landmarken fallen weg; ohne Ort und mit richtung ≠ haut gilt '
         'das ganze Band 0…1. Der Browser (static/viewer/charakter/genesis9/genesis9morphformular.js) hängt den Regler '
         'sofort an und stellt ihn auf 1. Der Körper-Zweig …/genesis9-figur/morph/ gehört zur Gruppe Körper (T1). '
         'Quelle: HumanBodyWeb/core/api/g9morphformular.py (01.10.2026).'),

        ('Landmarken der Grundfigur lesen',
         'Liefert die benannten Punkte (Bauch, Stirn, Schläfe …), die ein Ort als Landmarke nehmen kann.',
         'api',
         'GET /api/character/genesis9-figur/landmarken/ → {landmarken: {name: [x, y, z]}}',
         [(A + 'g9morphformular.py', 'G9morphformularapi'), (G + 'ortsmorph.py', 'G9ortsmorph')],
         '404 ohne Daz-Bibliothek. Die Werte sind gemessen (Extreme und Schwerpunkte je Körperteil der Grundfigur), nicht '
         'geschätzt, und stehen im Steckbrief jedes Morphs, der sie benutzt.'),

        ('Form-Pinsel auf dem Modell der Runde',
         'Ziehen, Drücken, Aufblasen, Glätten, Flach, Greifen mit Strichen aus der Bühne; das Ergebnis ist ein eigener Morph.',
         'api',
         "POST /api/engine2d3dkleider/<job_id>/formen/\n"
         "{kennung, art: kleidung|haar|koerper, name, modus, radius_cm, staerke, striche: [{p: [x, y, z], n: [x, y, z], d?: [x, y, z]}]}\n"
         "→ {brief, regler, rezept: Zeile}",
         [(A + 'engine2d3dkleiderformen.py', 'Engine2d3dKleiderformendpunkte'), (G + 'formpinsel.py', 'G9formpinsel'),
          (G + 'kleidmorphe.py', 'G9kleidmorphe')],
         'Modi: ziehen, druecken, aufblasen, glaetten, flach, greifen (G9formpinsel.MODI). Die Striche kommen aus dem Raycast '
         'der Bühne (Knopf „Formen“, engine2d3dkleiderformen.js); von Hand sind sie nur sinnvoll, wenn man Punkt und Normale '
         'kennt. Während der Auftrag rechnet: 409. Weil es ein Morph ist, bleiben UV und Gruppen — die Fotoprojektion der '
         'nächsten Runde läuft auf der geformten Fläche. Gemessen 01.10.2026 (ortsmorphe.md, Base Shirt): Ziehen 131 Punkte '
         'bis 9,6 mm, Glätten weiter 7,8 mm. Für art koerper schreibt der Pinsel eigen:form_<name> (Gruppe Körper, T1).'),

        ('Eigene Morphe eines Stücks auflisten',
         'Fragt ab, welche eigenen Morphe und festen Regler ein Stück schon hat.',
         'python',
         "from Genesis9.kleidmorphe import G9kleidmorphe\n"
         "G9kleidmorphe.namen('g9_base_shirt')            # sortierte Namen der gebauten Morphe\n"
         "G9kleidmorphe.regler('g9_base_shirt', 'kleidung')  # Regler: eigene + feste + Textur-Schichten",
         [(G + 'kleidmorphe.py', 'G9kleidmorphe')],
         'Die Ablage liegt unter 3DObjects/Genesis9/kleidmorphe/, die Fassung (f1) steht im Dateinamen. Für Haar art '
         '"haar" angeben: dann kommen Strähnendicke und Zusatzsträhnen dazu. Quelle: Genesis9/kleidmorphe.py.'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('ModellMitKleidern', 'ruft', 'G9kleidmorphe',
         'G9kleidmorphe.bauen(kennung, name, form): Deltas auf dem Käfig rechnen und ablegen (morph_neu)'),
        ('ModellFormMixin', 'ruft', 'G9kleidmorphe',
         'G9kleidmorphe.bauen(): morph_ort und kleid_welle; G9kleidmorphe.ablegen(): Ring und Hülle'),
        ('ModellFormMixin', 'ruft', 'G9kleidring', 'G9kleidring.bauen(): kleid_ring'),
        ('ModellFormMixin', 'ruft', 'G9huellenmorph', 'G9huellenmorph.bauen(sicht, …): kleid_huelle'),
        ('ModellFormMixin', 'ruft', 'Rezeptumgebung', 'Rezeptumgebung.sicht(): Sichtkörper der Fotos, sonst ValueError'),
        ('G9kleidmorphe', 'ruft', 'G9ortsmorph',
         'G9ortsmorph.deltas(): Gewicht Band × Sektor × Kugel × Welle, Richtung Hautnormale'),
        ('G9kleidring', 'ruft', 'G9kleidmorphe', 'G9kleidmorphe.kaefige() und ablegen(): Käfig lesen, Ringmorph speichern'),
        ('G9huellenmorph', 'ruft', 'G9kleidmorphe', 'G9kleidmorphe.kaefige() und ablegen()'),
        ('G9standardmorphe', 'ruft', 'G9kleidmorphe', 'G9kleidmorphe.bauen(): baut einen festen Regler beim ersten Zug'),
        ('G9kleidmorphe', 'ruft', 'G9standardmorphe', 'G9standardmorphe.bauen() und ist_standard(): deltas() baut lazy'),
        ('G9morphformularapi', 'ruft', 'G9kleidmorphe', 'G9kleidmorphe.bauen(): POST …/garderobe/<kennung>/morph/'),
        ('G9morphformularapi', 'ruft', 'G9ortsmorph', 'G9ortsmorph.landmarken(): GET …/landmarken/'),
        ('Engine2d3dKleiderformendpunkte', 'ruft', 'G9formpinsel', 'G9formpinsel.stueck(): Striche → eigener Morph'),
        ('G9formpinsel', 'ruft', 'G9kleidmorphe', 'G9kleidmorphe.kaefige(), deltas(), ablegen(): weiterformen auf demselben Namen'),
    ]

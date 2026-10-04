# -*- coding: utf-8 -*-
"""Werkzeughaarform — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: Haar formen (Operationen, Strähnen, Dichte).

Die Haar-Operationen nach Blenders Hair-Node-Muster, als Morphe auf dem Käfig einer Frisur. Reine Daten (Schema:
`ProjektTemp/_wegwerf/stoff_ausbau/AUFTRAG_TOOLS.md`); gelesen von `Architektur2d3dwerkzeuge`. Jede Zeile ist gegen den
Code gelesen (03.10.2026); Zahlen tragen Fundstelle und Datum. Blenders Haar-Knoten und die Haar-Dynamik stehen in der
Gruppe „Drapieren und Haar-Simulation“.
"""

__all__ = ['Werkzeughaarform']


class Werkzeughaarform:
    G = 'Genesis9/'

    KENNUNG = 'haarform'
    TITEL = 'Haar formen: Trim, Clump, Noise, Locken, Zopf, Strähnen, Dichte'
    EINLEITUNG = (
        'Jede Operation ist eine Funktion mit Zahlenparametern und einem Gewicht je Punkt aus einem ORT; das Ergebnis ist '
        'ein eigener Morph der Frisur (<sorte>.eigen.<name>, −2…2), linear wie die Formachsen, abgelegt neben der '
        'Bibliothek (3DObjects/Genesis9/kleidmorphe/). Jeder Aufruf baut den Morph UND stellt ihn auf wert; ein zweiter '
        'Bau desselben Namens ersetzt den ersten. Der Ort ist ein Wörterbuch: {landmarke: schlaefe_l|schlaefe_r|ohr_l|ohr_r|'
        'stirn|nacken|scheitel, radius_cm: 6} oder {sektor: (a°, b°)} um die Kopfachse (0 vorn, positiv links); ohne Ort '
        'wirkt die Operation überall unter der Nackenlinie, die Kappe an der Kopfhaut bleibt. Mit Ort zählt Haar „frei von '
        'der Kopfhaut“ ab 8 mm — sonst bewegte „Pony nach vorn“ nur 4 Punkte (gemessen 30.09.2026, ortsmorphe.md). '
        'Operationen gelten für Kartenhaar und Stranghaar; für Stranghaar gibt es zusätzlich Dicke, Duplizieren und '
        'Interpolieren. Name: Kleinbuchstaben, Ziffern, Unterstrich (G9kleidmorphe.NAME). Reihenfolge: 1. Frisur wählen und '
        'Länge (Gruppe „Haar“), 2. Operationen, 3. Dicke und Dichte. Die Automatik schreibt trim, anlegen und heben '
        '(IterationHaare, IterationHaarfoto), nie Dynamik und nie Blender.')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Trim: Haar kürzen oder verlängern',
         'Der hängende Teil der Frisur wird faktor-mal so lang (0,5 = halb, 1,5 = länger).',
         'rezept',
         "m.haar_trim('kin_hair', 'kuerzer', faktor=0.5, ort=None)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haarops.py', 'G9haarops'), (G + 'kleidmorphe.py', 'G9kleidmorphe'),
          (G + 'haareigenmorphe.py', 'G9haareigenmorphe')],
         'Nach der Länge der Formachse (G9haareigenmorphe.laenge, Faktor 1,9) mit freiem Faktor und Ortsgewicht; danach aus '
         'dem Körper gehoben. Die Automatik schreibt trim erst, wenn die Längenachse bei 0 steht, je Sektor mit Ort: nach '
         'dem Netz (IterationHaare.trim) oder nach den Fotos, wo die unteren Bänder zu einem Anteil auf Haut liegen '
         '(IterationHaarfoto.trim, 02.10.2026).'),

        ('Haaransatz heben',
         'Haar unter einer Höhe (Anteil der Frisurhöhe von unten) rückt im Ort auf diese Höhe.',
         'rezept',
         "m.haar_heben('kin_hair', 'ansatz', hoehe=0.8, ort={'landmarke': 'stirn', 'radius_cm': 9})",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haarops.py', 'G9haarops')],
         'Eingeführt 02.10.2026 (Prüfung Runde 19: die Frisur saß bis auf die Stirn). Das Ortsgewicht allein gilt (Haar, das '
         'der Haut anliegt, soll mit — G9haarops.AUF_HAUT), danach wird aus dem Körper gehoben. Die Automatik schreibt es aus '
         'Form nach den Fotos (IterationHaarfoto.heben).'),

        ('Clump: Strähnen zu Büscheln',
         'Punkte ziehen sich zu ihrem Büschel (Schwerpunkt ihrer Gruppe in x/z) zusammen.',
         'rezept',
         "m.haar_clump('mavick_hair', 'buescheln', staerke=0.5)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haarops.py', 'G9haarops')],
         'staerke 0…1; Büschelzahl ≈ Punktzahl/300 (k-Mittel in x/z mit festem Zufall). Zeit: die erste Fassung (scipy kmeans2 '
         'minit „++“) hing am Mavick Hair (576.309 Punkte, k = 1.921) über 20 Minuten (py-spy: _kpp → cdist) und hätte den '
         'Server-Faden festgehalten; jetzt Startmitten aus den Punkten + 6 Lloyd-Schritte mit KD-Baum: 1,6 s (ortsmorphe.md, '
         '01.10.2026).'),

        ('Noise: Frizz',
         'Das hängende Haar bekommt glatte Wellen (kein Zufall, feste Phase aus der Lage).',
         'rezept',
         "m.haar_noise('kin_hair', 'frizz', staerke=0.5, laenge_cm=4.0)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haarops.py', 'G9haarops')],
         'staerke 0…1 = bis 12 mm Ausschlag (NOISE_MAX_M); laenge_cm = Wellenlänge, mindestens 0,5 cm. Der Morph bleibt '
         'stets derselbe (keine Zufallszahl), zwei Aufrufe mit gleichen Zahlen sind bitgleich.'),

        ('Straighten: hängendes Haar fällt senkrecht',
         'Hängendes Haar fällt senkrecht im Radius der Nackenlinie.',
         'rezept',
         "m.haar_straighten('toulouse_hair', 'glatt', staerke=0.7)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haarops.py', 'G9haarops')],
         'staerke 0…1; der Radius ist der Median der Punkte nahe der Nackenlinie (±2 cm), 0,1 m ohne solche Punkte.'),

        ('Biegen: Haar im Ort in eine Richtung',
         'Das Haar im Ort wandert in eine Richtung um weg_cm; die Wurzel bleibt, die Spitze wandert (Strähne ins Gesicht, '
         'hinters Ohr).',
         'rezept',
         "m.haar_biegen('kin_hair', 'pony_vor', {'landmarke': 'stirn', 'radius_cm': 9}, richtung='vorn', weg_cm=3.0)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haarops.py', 'G9haarops'), (G + 'ortsmorph.py', 'G9ortsmorph')],
         'Braucht einen ort (sonst ValueError „biegen braucht einen ort“). richtung vorn|hinten|aussen|innen|oben|unten|'
         '[x, y, z] oder haut. weg_cm darf negativ sein. Die festen Regler „Pony nach vorn“ und „Seiten hinters Ohr“ '
         '(op_pony_vorn, op_hinter_ohr) sind Biegen mit festem Ort.'),

        ('Anlegen: Haar an die Kopfhaut ziehen',
         'Haar, das weiter als abstand_mm von der Kopfhaut absteht, rückt um staerke heran (Shrinkwrap).',
         'rezept',
         "m.haar_anlegen('kin_hair', 'anliegend', abstand_mm=8.0, staerke=0.7, ort=None)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haarops.py', 'G9haarops')],
         'staerke 0…1 entlang der Hautnormale des nächsten Körperpunkts (Grundfigur). Die Automatik prüft die oberen zwei '
         'Bänder: steht das Haar in einem Sektor > 8 mm außerhalb des Netzes, schreibt sie haar_anlegen mit Ort (Band × '
         'Sektor) und erhöht danach +0,25 je Runde bis 1,5 (IterationHaare.anlegen). Blenders Shrinkwrap mit Zielobjekt: '
         'haar_knoten (nur nach Ansage, Gruppe „Drapieren …“).'),

        ('Locken (Curl)',
         'Das hängende Haar kreist um seine Fallrichtung; der Radius wächst zur Spitze.',
         'rezept',
         "m.haar_curl('kin_hair', 'locken', radius_cm=2.0, windungen=8.0)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haarops.py', 'G9haarops')],
         'windungen je Meter hängendem Haar; die Locke verkürzt das Haar (Spitze wird hochgezogen — Blenders Curl kürzt '
         'ebenso). Auf Karten eine Näherung; Blenders Curl Hair Curves auf Stranghaar: haar_knoten(…, curl), nur nach Ansage. '
         'Seit 01.10.2026 (ortsmorphe.md).'),

        ('Zopf (Braid)',
         'Drei Bündel des hängenden Haars im Ort winden sich um die Zopfmitte.',
         'rezept',
         "m.haar_braid('kin_hair', 'zopf', breite_cm=3.0, windungen=6.0, ort={'sektor': (120, -120)})",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haarops.py', 'G9haarops')],
         'Der Vorgabe-Ort ist der Sektor hinten (120 … −120); breite_cm = Breite des Zopfs, windungen je Meter. Auf Karten '
         'eine Näherung, auf Strähnen ein Zopf. Seit 01.10.2026 (ortsmorphe.md).'),

        ('Feste Operations-Regler (13 je Frisur)',
         'Dreizehn fertig definierte Haar-Operationen an jeder Frisur, sofort in jeder Liste; bauen beim ersten Zug.',
         'rezept',
         "m.morph_wert('haar', 'kin_hair', 'op_trim', 1.0)\n"
         "# Namen: op_trim, op_clump, op_noise, op_straighten, op_anlegen, op_pony_trim, op_pony_vorn, op_links_trim,\n"
         "#        op_rechts_trim, op_nacken_trim, op_hinter_ohr, op_curl, op_braid",
         [(G + 'standardmorphe.py', 'G9standardmorphe'), (G + 'haarops.py', 'G9haarops'), (G + 'kleidmorphe.py', 'G9kleidmorphe'),
          (G + 'modellmitkleidern.py', 'ModellMitKleidern')],
         'Im UI: Szene → Assets → Genesis → Frisur → Gruppe „Operationen“. Wert −2…2, negativ kehrt um (Trim −1 = länger). Der '
         'erste Zug baut die Ablage, „ein Zug ein bis drei Sekunden einmal“ (Docstring G9standardmorphe, 30.09.2026), '
         'danach aus der Ablage. Pony: Ort Stirn, Radius 9 cm; links/rechts: Sektor (30, 150) / (−150, −30); Nacken: Sektor '
         '(150, −150).'),

        ('Strähnendicke (Stranghaar)',
         'Stellt die Breite der Strähnen von der Wurzel zur Spitze in mm — im Render und in der GLB der Runde.',
         'rezept',
         "m.haar_profil('g9_base_dforce_pixie_hair', wurzel_mm=1.5, spitze_mm=0.5)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haarprofil.py', 'G9haarprofil')],
         'Wurzel und Spitze 0…6 mm (MAX_MM), Vorgaben 1,5 und 0,5. Ohne Stranghaar ohne Wirkung. Stranghaar war im Render '
         'und in der Runden-GLB unsichtbar (entartete Linien) — jetzt je Segment ein Band, kameraunabhängig; 1,23 Mio. Punkte '
         'in 0,5 s (ortsmorphe.md, 01.10.2026). Im Browser bleiben Strähnen Linien. Gilt für Pixie, Hime Cut, Viola.'),

        ('Dichteres Stranghaar: Strähnen duplizieren',
         'Legt je Strähne anzahl Kopien an, quer um radius_mm versetzt — als Zusatzsträhnen neben der Bibliothek.',
         'rezept',
         "m.haar_duplizieren('g9_base_dforce_pixie_hair', 'dichter', anzahl=1, radius_mm=4.0, wert=1.0)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haarzusatz.py', 'G9haarzusatz'), (G + 'strangzusatz.py', 'G9strangzusatz'),
          (G + 'kleidmorphe.py', 'G9kleidmorphe')],
         'Nur Stranghaar hat Strähnen (ein Eintrag, der keine Frisur ist, wirft ValueError „… ist keine Frisur“; Kartenhaar '
         'liefert keine Zusatzsträhnen — dafür clump/noise/trim). Regler str.<name> = Anteil der Zusatzsträhnen 0…1, '
         'feste Saat. Eine Zusatzsträhne liegt als REZEPT aus vorhandenen Punkten (Σ gewicht·punkt[quelle] + '
         'versatz), damit sie Auto-Fit, Morphen und Haltung folgt. Gemessen 01.10.2026 (ortsmorphe.md): Pixie 2,5 s; im Bau '
         'wird das Strang-Teil zu G9strangzusatz (Anwenden 0,9 s bei 614.209 Punkten).'),

        ('Zwischensträhnen interpolieren',
         'Legt zwischen jeder Strähne und ihrer nächsten Nachbarin anzahl neue Strähnen an.',
         'rezept',
         "m.haar_interpolieren('g9_base_dforce_pixie_hair', 'zwischen', anzahl=1, wert=1.0)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haarzusatz.py', 'G9haarzusatz'), (G + 'strangzusatz.py', 'G9strangzusatz')],
         'Folgen beiden Leitsträhnen; Regler str.<name> = Anteil 0…1; Nachbarsuche bis NACHBAR_M 0,03 m. Gemessen '
         '01.10.2026 (ortsmorphe.md): Pixie 1,4 s. Blenders Interpolate/Generate über haar_knoten (nur nach Ansage) liefern '
         'andere Strähnen mit Kopfhaut-Bindung; diese Python-Fassung geht immer.'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('ModellHaarMixin', 'ruft', 'G9haarops', 'G9haarops.bauen(sorte, name, operation, ort, **parameter): _haarop()'),
        ('ModellHaarMixin', 'ruft', 'G9haarzusatz', 'duplizieren() und interpolieren() je Strang-Teil, ablegen(): _haarzusatz()'),
        ('ModellHaarMixin', 'ruft', 'G9haarprofil', 'G9haarprofil.PRAEFIX und MAX_MM: haar_profil()'),
        ('ModellHaarMixin', 'ruft', 'G9kleidmorphe', 'G9kleidmorphe.kaefige(sorte): _haarzusatz() liest die Teile'),
        ('G9haarops', 'ruft', 'G9kleidmorphe', 'G9kleidmorphe.kaefige() und ablegen(): Käfig lesen, Morph speichern'),
        ('G9haarops', 'ruft', 'G9haareigenmorphe', 'G9haareigenmorphe(punkte, kopf, koerper): Kopfmitte, Nackenlinie, haengt'),
        ('G9haarops', 'ruft', 'G9ortsmorph', 'G9ortsmorph.gewicht() und richtung(): Ortsgewicht und Richtung'),
        ('G9haarzusatz', 'ruft', 'G9strangzusatz', 'G9strangzusatz(folger, saetze): anwenden() erweitert das Strang-Teil'),
        ('G9standardmorphe', 'ruft', 'G9haarops', 'G9haarops.bauen(): baut einen festen Operationsregler beim ersten Zug'),
        ('G9kleidmorphe', 'ruft', 'G9standardmorphe', 'G9standardmorphe.bauen() und ist_standard(): deltas() baut lazy'),
    ]

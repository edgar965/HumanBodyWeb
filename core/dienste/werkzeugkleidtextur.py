# -*- coding: utf-8 -*-
"""Werkzeugkleidtextur — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: Textur von Kleidern und Haar.

Fototextur, Decal, Falten, Umfärbung. Reine Daten (Schema: `ProjektTemp/_wegwerf/stoff_ausbau/AUFTRAG_TOOLS.md`);
gelesen von `Architektur2d3dwerkzeuge`. Jede Zeile ist gegen den Code gelesen (03.10.2026); Zahlen tragen Fundstelle
und Datum.
"""

__all__ = ['Werkzeugkleidtextur']


class Werkzeugkleidtextur:
    G = 'Genesis9/'
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'

    KENNUNG = 'kleidtextur'
    TITEL = 'Textur: Fotoprojektion, Decal, Falten, Umfärbung (Kleider und Haar)'
    EINLEITUNG = (
        'Eine Texturschicht ist ein Bild je Materialgruppe im UV-Raum neben der Bibliothek '
        '(3DObjects/Genesis9/kleidtexturen/<kennung>__<gruppe>__<schicht>_f1.png), gestellt über den Regler '
        '<kennung>.bild.<schicht> (Gruppe „Textur“, 0…1, Falten bis 2). Beim Bau (G9stueckteile.netze → '
        'G9kleidtexturen.anwenden) wird sie über die Daz-Bilder der Gruppe komponiert; Browser, Szene und Render sehen '
        'dasselbe. Schichtnamen: foto, foto_<kürzel>, grau, decal_<name>, falten_<name> (G9kleidtexturen.NAME). Reihenfolge: '
        '1. Form fertig machen (Gruppen „Kleider formen“, „Drapieren …“) — die Fotofarbe wanderte sonst mit jeder '
        'Formänderung, 2. Fotoprojektion, 3. Falten, 4. Decal für Aufdrucke, 5. Tönung (m.kleid_farbe_je_stueck, Gruppe „Kleider '
        'anziehen …“). Texturen von Haut und Körper gehören zur Gruppe Körper (T1).')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Fotofarbe auf ein Kleidungsstück (Projektion je Texel)',
         'Holt die Farbe des Stücks aus den Fotos der Runde (Aufdruck, Streifen, Stickerei) und legt sie als Schicht ab.',
         'rezept',
         "m.kleid_fototextur('g9_base_shirt', staerke=1.0)",
         [(G + 'modelltextur.py', 'ModellTexturMixin'), (D + 'begutachtungswerkzeug.py', 'Begutachtungswerkzeug'),
          (D + 'kleidfotoprojektion.py', 'Kleidfotoprojektion'), (G + 'kleidfototextur.py', 'G9kleidfototextur'),
          (G + 'kleidtexturen.py', 'G9kleidtexturen')],
         'Der Aufruf merkt nur den Wunsch (modell.fotowuensche) und stellt den Regler bild.foto_<auftrag>; die RUNDE '
         'projiziert nach dem Bau (Kleidfotoprojektion.bauen): Kennfarbenrender in 512 × 768, Teilmasken, Push-Pull-Füllung '
         'der Lücken, Gewicht Normale·Blick⁴. Ohne Runde (Bühne, Skript) bleibt der Regler ohne Schicht wirkungslos. staerke '
         '0…1 = Anteil gegenüber der Daz-Textur. Gemessen 01.10.2026 (ortsmorphe.md): Kunstfoto am Base Shirt 89 % der Texel '
         'getroffen, 4,4 s; Texelraum ohne Torch (Pillow malt je Dreieck seine Nummer, NumPy rechnet die Baryzentrik) Base '
         'Shirt 2,2 s. Grenze: die Fotos zeigen hängende Arme, das Modell steht in A-Pose — die Fotoprojektion holt sich die '
         'Armhaut (hautfarbene Flecken unter dem Ärmel; engine2d3dkleider.md, 01.10.2026; Abhilfe: Hautmaske oder nur '
         'Ansichten ohne Arm vor dem Stück, offen). Die Automatik schreibt die Zeile erst, wenn die Form drei Runden lang '
         'stillsteht (IterationTextur.still).'),

        ('Fotofarbe auf eine Frisur',
         'Wie kleid_fototextur, für eine Frisur der Garderobe.',
         'rezept',
         "m.haar_fototextur('mavick_hair', staerke=1.0)",
         [(G + 'modelltextur.py', 'ModellTexturMixin'), (D + 'kleidfotoprojektion.py', 'Kleidfotoprojektion'),
          (G + 'kleidtexturen.py', 'G9kleidtexturen')],
         'Gleicher Weg und gleiche Grenzen wie bei Kleidern. Keiner der beiden Renderer (Mitsuba, pyrender) liest '
         'Deckkraftkarten (ortsmorphe.md, 01.10.2026). Die Haartönung wirkt je Renderer verschieden (Mitsuba rechnet '
         'Mehrfachstreuung zwischen den Haarkarten): Mavick mit Daz-Bild 131/109/84 unter Mitsuba gegen 152/140/124 unter '
         'pyrender, mit Schicht grau 161 gegen 155 — einen Farbschritt nie über den Renderer hinweg bewerten.'),

        ('Aufdruck, Streifen, Emblem: Decal an einem Ort',
         'Legt eine Farbfläche an einen Ort des Stücks (Band × Sektor, Landmarke, Kugel) in die Textur.',
         'rezept',
         "m.kleid_decal('g9_base_shirt', 'streifen', {'band': (0.4, 0.5)}, farbe='#ffffff', deckung=0.8)",
         [(G + 'modelltextur.py', 'ModellTexturMixin'), (G + 'kleiddecal.py', 'G9kleiddecal'),
          (G + 'kleidtexturen.py', 'G9kleidtexturen'), (G + 'uvraster.py', 'G9uvraster')],
         'ort wie bei morph_ort (Gruppe „Kleider formen“); farbe #rrggbb, deckung 0…1; gestellt als bild.decal_<name>. '
         'Gemessen 01.10.2026 (ortsmorphe.md): Decal am Base Shirt 0,4 s, ein Decal mit 4.098 roten Pixeln ist im Render zu '
         'sehen; die Runden-GLB trägt je Gruppe ihr Bild. Grenze: nur mit Farbe, nicht mit einem Bild (engine2d3dkleider.md, '
         'Review 01.10.2026). Der Name heißt in einer Runde decal_<name>_<auftrag>.'),

        ('Feinfalten als Normalkarte',
         'Legt Feinfalten (Abstand, Tiefe, Richtung) als Normalkarte über das Stück; optional nur an einem Ort.',
         'rezept',
         "m.kleid_falten('g9_base_shirt', 'saum', ort={'band': (0.0, 0.3)}, abstand_cm=4.0, tiefe=0.5, richtung='laengs')",
         [(G + 'modelltextur.py', 'ModellTexturMixin'), (G + 'faltenkarte.py', 'G9faltenkarte'),
          (G + 'kleidtexturen.py', 'G9kleidtexturen')],
         'richtung laengs = Falten quer um das Stück, quer = senkrecht hängend (bei kleid_welle ist es umgekehrt benannt); '
         'gestellt als bild.falten_<name>, Wert 0…2. Gemessen 01.10.2026: Base Shirt 1,1 s. Das ist eine Normalkarte, keine '
         'Geometrie: Großfalten gehören in kleid_welle oder kleid_drapieren. Die Automatik schreibt die Zeile, wenn das Foto '
         'unter der Maske des Stücks deutlich mehr Kantenenergie hat als der Render (IterationTextur.falten).'),

        ('Falten aus einer Simulation backen',
         'Wandelt die Verschiebung des Morphs aus kleid_drapieren je Texel in eine Normalkarte (Relief ohne die Form).',
         'rezept',
         "m.kleid_falten_backen('g9_base_shirt', 'sim', quelle='drapiert', staerke=1.0)",
         [(G + 'modelltextur.py', 'ModellTexturMixin'), (G + 'faltenbacken.py', 'G9faltenbacken'),
          (G + 'kleidmorphe.py', 'G9kleidmorphe'), (G + 'uvraster.py', 'G9uvraster')],
         'Braucht den Morph quelle (eigen.drapiert aus kleid_drapieren; in einer Runde drapiert_<auftrag> — die Suche '
         'übernimmt m.vorhanden). Normale der verschobenen Fläche im Tangentenraum der Grundfläche (Lengyel-Tangenten). '
         'Gemessen 01.10.2026 (ortsmorphe.md): Base Shirt aus drapiert 2,6 s, 90 % der Shirt-Texel gekippt. Gebacken wird '
         'aus dem Ergebnis des gewählten Motors (Newton, Stoffsolver oder Blender); der Aufruf ist unabhängig vom Motor.'),

        ('Daz-Farbe durch Grau ersetzen (Kleid)',
         'Entsättigt die Daz-Albedo des Stücks auf ein neutrales Grau (Schicht grau, ohne Datei), damit die Tönung jede '
         'Farbe trifft.',
         'rezept',
         "m.kleid_umfaerben('g9_base_shirt', staerke=1.0)",
         [(G + 'modelltextur.py', 'ModellTexturMixin'), (G + 'kleidtexturen.py', 'G9kleidtexturen')],
         'Ohne diese Schicht trifft m.kleid_farbe_je_stueck ein schwarzes Daz-Shirt (Mittel 0,067) nie: Bild × 2 × Tönung '
         'kann es nicht aufhellen (engine2d3dkleider.md, 01.10.2026; Render 0,15 gegen Foto 0,35 bei Tönung #ffffff). Die '
         'Automatik schreibt kleid_umfaerben + kleid_farbe_je_stueck selbst, wenn Farbangleich.unerreichbar es meldet.'),

        ('Daz-Farbe durch Grau ersetzen (Haar)',
         'Dasselbe für eine Frisur: blondes Haar lässt sich sonst nicht grau oder schwarz tönen.',
         'rezept',
         "m.haar_umfaerben('mavick_hair', staerke=1.0)",
         [(G + 'modelltextur.py', 'ModellTexturMixin'), (G + 'kleidtexturen.py', 'G9kleidtexturen')],
         'Danach m.haar_farbe oder m.haar_zonenfarbe (Gruppe „Haar“). Der Bart (mavick_beard) wird von der Automatik '
         'ebenfalls mit haar_umfaerben gefärbt (IterationHaare.bart).'),

        ('Texturschicht direkt stellen',
         'Stellt eine bestehende Schicht (foto, decal_<name>, falten_<name>) auf einen Wert; der Weg für Pinsel und Rezeptliste.',
         'rezept',
         "m.bild_wert('kleidung', 'g9_base_shirt', 'decal_streifen', 0.5)",
         [(G + 'modelltextur.py', 'ModellTexturMixin'), (G + 'kleidtexturen.py', 'G9kleidtexturen')],
         'art haar|kleidung; Wert 0…2 (Falten bis 2). Ungültiger Schichtname wirft ValueError („schicht: foto | decal_<name> | '
         'falten_<name>“). Eine Schicht ohne Datei wirkt nicht; gebaut wird sie von kleid_decal, kleid_falten, '
         'kleid_falten_backen, der Fotoprojektion der Runde und dem Mal-Endpunkt. Quelle: Genesis9/modelltextur.py.'),

        ('Von Hand auf das Modell der Runde malen',
         'Malt Striche aus der Bühne in eine Decal-Schicht des Stücks; sofort sichtbar, die nächste Runde baut damit.',
         'api',
         'POST /api/engine2d3dkleider/<job_id>/malen/\n'
         '{kennung, art: kleidung|haar, name, farbe, radius, deckung, striche: [{gruppe: slug, u, v}]}\n'
         '→ {brief, regler: "<kennung>.bild.decal_<name>", rezept: Zeile}',
         [(A + 'engine2d3dkleidermalen.py', 'Engine2d3dKleidermalendpunkte'), (G + 'kleidpinsel.py', 'G9kleidpinsel'),
          (G + 'kleidtexturen.py', 'G9kleidtexturen')],
         'Während der Auftrag rechnet: 409. Die Bühne nimmt die Striche per Raycast auf die GLB der Runde auf (Knoten '
         '…_g<k>__<slug> nennt die Gruppe, uv in glTF-Konvention); Knopf „Malen“ (HumanBodyWeb/static/viewer/'
         'engine2d3dkleider/engine2d3dkleidermalen.js). Der Regler bild.decal_<name> wird im Modell des Kreislaufs auf 1 '
         'gestellt, die Rezeptliste bekommt die Zeile m.bild_wert(…). Gemessen 01.10.2026: 20 Striche 0,05 s. Höchstens '
         '5.000 Punkte je Aufruf (G9kleidpinsel.HOECHSTENS_PUNKTE), Schicht 1024 px (GROESSE).'),

        ('Regel: Schichtnamen, Ablage und Fassung',
         'Hält fest, wie Schichten heißen und wo sie liegen — Schichten mehrerer Aufträge überschreiben sich sonst still.',
         'regel',
         'Schicht heißt foto_<kürzel> (Auftrag), decal_<name>_<kürzel> usw.; Ablage …/kleidtexturen/ mit _f1 im Namen.',
         [(G + 'kleidtexturen.py', 'G9kleidtexturen'), (G + 'modelltextur.py', 'ModellTexturMixin')],
         'Seit 01.10.2026 tragen Fotoschicht und Decal den Auftrag im Namen (Rezeptumgebung.kuerzel → j<ziffern>; '
         'ModellTexturMixin.fotoschicht) — zwei Aufträge mit demselben Stück überschrieben sich vorher still '
         '(ortsmorphe.md). Wer eine Schicht sucht: m.vorhanden(werte, schluessel) findet sie mit oder ohne Auftragskürzel. '
         'Die Daz-Farbe wird beim Komponieren eingerechnet (Farbfaktor der Gruppe), damit eine Fotofarbe nicht noch einmal '
         'getönt wird (G9kleidtexturen.anwenden).'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('ModellTexturMixin', 'ruft', 'G9kleidtexturen', 'G9kleidtexturen.NAME: prüft den Schichtnamen in bild_wert()'),
        ('ModellTexturMixin', 'ruft', 'G9kleiddecal', 'G9kleiddecal.bauen(kennung, name, ort, farbe, deckung): kleid_decal'),
        ('ModellTexturMixin', 'ruft', 'G9faltenkarte', 'G9faltenkarte.bauen(kennung, name, ort, abstand_cm, tiefe, richtung): kleid_falten'),
        ('ModellTexturMixin', 'ruft', 'G9faltenbacken', 'G9faltenbacken.bauen(kennung, name, quelle, staerke): kleid_falten_backen'),
        ('Begutachtungswerkzeug', 'ruft', 'Kleidfotoprojektion', 'Kleidfotoprojektion(ablage, render, aus).bauen(modell, teile, referenzen)'),
        ('Kleidfotoprojektion', 'ruft', 'G9uvraster', 'G9uvraster: Teile in den UV-Raum rastern (Texelraum je Gruppe)'),
        ('Kleidfotoprojektion', 'ruft', 'G9kleidfototextur', 'G9kleidfototextur.bauen(): legt die Schicht foto ab'),
        ('G9kleidfototextur', 'ruft', 'G9kleidtexturen', 'G9kleidtexturen.ablegen(kennung, schicht, bilder, brief)'),
        ('G9kleiddecal', 'ruft', 'G9kleidtexturen', 'G9kleidtexturen.raster(), lage(), ablegen(): Texelraum und Schicht'),
        ('G9faltenkarte', 'ruft', 'G9kleidtexturen', 'G9kleidtexturen.raster(), lage(), ablegen()'),
        ('G9faltenbacken', 'ruft', 'G9kleidmorphe', 'G9kleidmorphe.deltas() und kaefige(): die Verschiebung des Morphs quelle'),
        ('G9faltenbacken', 'ruft', 'G9uvraster', 'G9uvraster.karte(): Normalen im Tangentenraum je Texel'),
        ('Engine2d3dKleidermalendpunkte', 'ruft', 'G9kleidpinsel', 'G9kleidpinsel.malen(kennung, name, striche, farbe, radius_texel, deckung)'),
        ('G9kleidpinsel', 'ruft', 'G9kleidtexturen', 'G9kleidtexturen.pfad(), slug(), ablegen(): Decal-Schicht je Gruppe'),
    ]

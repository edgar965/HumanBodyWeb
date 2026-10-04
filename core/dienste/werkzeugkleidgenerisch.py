# -*- coding: utf-8 -*-
"""Werkzeugkleidgenerisch — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: „Kleidung – Generisch".

Reine Daten (Schema: `ProjektTemp/_wegwerf/stoff_ausbau/AUFTRAG_TOOLS.md`); gelesen von `Architektur2d3dwerkzeuge`.
Jede Zeile ist gegen den Code gelesen (03.10.2026); Zahlen tragen Fundstelle und Datum.
"""

__all__ = ['Werkzeugkleidgenerisch']


class Werkzeugkleidgenerisch:
    G = 'Genesis9/'
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'

    KENNUNG = 'kleidgenerisch'
    TITEL = 'Kleidung – Generisch (ein Eintrag je Kategorie, Mischen über die Haut)'
    EINLEITUNG = (
        '„Kleidung – Generisch“ fasst alle Kleidungsstücke einer Kategorie unter EINEM Eintrag ohne eigenes Netz zusammen — '
        'je Kategorie einer (kleidung_generisch_<kategorie>), dazu „Alle Kategorien“ (kleidung_generisch_alle) für '
        'Mischungen über Kategorien hinweg. Wer ein Kostüm zusammenstellt, kennt je Platz eine Wahl statt 390 Zeilen. '
        'Reihenfolge: 1. den Sammeleintrag in der Garderobenliste finden (GET …/garderobe/), 2. Anteile je Stück stellen '
        '(sorte.<kennung> im Rumpf, im Rezept kleid_nur / kleid_anteil — Gruppe „Kleider anziehen …“), 3. Passform, Übergang '
        'und Textur-Regler stellen, 4. das Netz anfragen (POST …/<eintrag>/netz/). Es gibt KEINE neue Geometrie im Eintrag: '
        'er wählt Stücke, reicht die Regler weiter, und der Bau mischt. Wo zwei Stücke dieselbe Hautstelle bedecken, steht '
        'EINE Fläche aus ihrem Verhältnis. Stand der Bibliothek 30.09.2026: 390 Stücke (165 MakeHuman, 172 GarmentCode, '
        '53 Daz) in 12 Kategorien (genesis9-garderobe.md); die gemerkte Liste (Genesis9/ablage/garderobe.json, gelesen '
        '03.10.2026) zählt 411 Kleidungsstücke (davon 21 eigene eigen_…, Fotostücke und Uhr), 18 Frisuren und 51 Requisiten.')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Sammeleinträge in der Szene',
         'Zeigt die Einträge „Kleidung – Generisch: <Kategorie>“ in ihrer Kategorie vorn und „Alle Kategorien“ ganz oben im '
         'Assets-Reiter; je Stück ein Anteilsregler.',
         'seite',
         'Szene /Charakter/ (Menü Dashboard → Charakter) → Reiter Assets → Genesis → Kategorie oder „Alle Kategorien“ → '
         'Anteil „<Stück>“, Gruppen „Passform“, „Mischung“, „Textur“',
         [(A + 'g9garderobe.py', 'G9garderobeapi'), (G + 'kleidgenerisch.py', 'G9kleidgenerisch')],
         'Alle Kästen sind beim Laden zu (Edgar, 30.09.2026; kein localStorage-Gedächtnis, engine2d3dkleider.md). Der '
         'Server setzt oben: true am Eintrag „Alle Kategorien“; die Frontend-Dateien sind HumanBodyWeb/static/viewer/'
         'charakter/genesis9/genesis9garderobe.js (Aufbau), genesis9stueckregler.js (Regler) und HumanBodyWeb/static/viewer/'
         'gemeinsam/kleidfarbmischung.js (Textur-Regler im Shader). „Alle Kategorien“ führt nur den Anteil je Stück '
         '(396 Regler statt Tausender; die Morphe der Stücke bleiben draußen, genesis9-garderobe.md 30.09.2026). Farbvarianten '
         'und Stile führt der Sammeleintrag nicht — dafür die Zeile des Stücks selbst nehmen.'),

        ('Garderobenliste lesen (mit den Sammeleinträgen)',
         'Liefert alle Stücke der Garderobe — vorn „Haar – Generisch“, dann die Kleidungs-Sammeleinträge, dann die einzelnen '
         'Stücke — mit Kategorie, Reglern und Varianten.',
         'api',
         'GET /api/character/genesis9-figur/garderobe/\n'
         '→ {stuecke: [{id, name, art, kategorie, varianten, stile, regler, vorschau, zeigbar, hinweis, generisch?, sorten?, '
         'oben?}], anzahl}',
         [(A + 'g9garderobe.py', 'G9garderobeapi'), (G + 'kleidgenerisch.py', 'G9kleidgenerisch'),
          (G + 'garderobe.py', 'G9garderobe')],
         'Die Kennungen (id) für Rezepte kommen von hier. Sammeleinträge tragen generisch: true, den Zähler sorten und die '
         'Reglerlisten (Anteil, Passform, Mischung, Textur). Kosten: die Listenantwort kostet warm rund 2,75 s '
         '(G9dazkategorien.vorgabe ~6 ms je Eintrag, 390 Stücke 2,3 s, deshalb je Listenobjekt gemerkt: '
         'G9kleidgenerisch._vorgaben; gemessen 30.09.2026, genesis9-garderobe.md); ohne Daz-Bibliothek kommt '
         '{stuecke: [], anzahl: 0, fehler}. Die Einteilung nach Kategorien liegt neben der Bibliothek (Gruppe „Garderobe“).'),

        ('Sammeleintrag anfragen: Stücke anziehen und mischen',
         'Baut das Netz des Sammeleintrags: ein Stück allein wie gewohnt, mehrere Stücke über 0 als EINE gemischte Fläche.',
         'api',
         'POST /api/character/genesis9-figur/garderobe/<kennung>/netz/   (kennung: kleidung_generisch_alle oder '
         'kleidung_generisch_<kategorie>)\n'
         '{regler: {…Genesis-Regler der Figur…},\n'
         ' regler_stueck: {"sorte.g9_base_shirt": 1, "sorte.gc_dress_shift": 0.3, "mischung:uebergang": 3, '
         '"passform:laenge": -4},\n'
         ' getragen: [{kennung, stil, regler_stueck}], rang: 0}\n'
         '→ {kennung, teile: [{name, vertices, faces, normals, uvs, gruppen, hautgewichte, knochen, …}], boden, stufen, '
         'innen, aussen, art}',
         [(A + 'g9garderobe.py', 'G9garderobeapi'), (G + 'kleidgenerisch.py', 'G9kleidgenerisch'),
          (D + 'g9kleidmischbau.py', 'G9kleidmischbau'), (G + 'kleidmischflaeche.py', 'G9kleidmischflaeche'),
          (G + 'kleidmischung.py', 'G9kleidmischung'), (G + 'kleidfarbe.py', 'G9kleidfarbe')],
         'GET und POST sind erlaubt; unbekannte Kategorie: 404 „Kein Kleidungsstück in dieser Kategorie“. Mehr als ein Stück '
         'über 0 (len(folge) > 1): jedes wird wie ein gewöhnliches gebaut (G9garderobeapi._kleid), die Teile hängen an der '
         'Haut, und G9kleidmischung mischt dort, wo beide dieselbe Hautstelle bedecken: Versatz = Σ aᵢ·oᵢ / Σ aᵢ, Auslauf '
         'über mischung:uebergang. Die Textur-Regler gehören nicht in den Schlüssel (G9kleidgenerisch.ohne_textur). Auf '
         'einer HumanBody-Figur dasselbe mit figurart: humanbody (Bauweg G9kleidhumanbody.antwort). Gemessen 30.09.2026 '
         '(genesis9-garderobe.md): Base Shirt × GC Dress Shift 100:30 über den Endpunkt 4,4 s kalt (Stufe 2), 0,0 s aus dem '
         'Vorrat; Grundfigur, Lücke am Rand ≤ 8 mm bei Kante 5,5 mm; auf HumanBody Base Shirt 100 % + Dancing Queen Dress '
         '60 % kalt 59,6 s (zwei Stückbauten, Server belegt). Grenze: Wo der Zuschnitt einen Rand lässt, öffnet sich im '
         'Stoffschwung ein Spalt (das schwingende Stück folgt dem Käfig, das gehäutete nicht).'),

        ('Sammeleintrag in Python auflösen',
         'Liest aus einem Wertesatz die getragenen Stücke und ihre Anteile — dieselbe Regel wie Server und Rezept.',
         'python',
         "from Genesis9.kleidgenerisch import G9kleidgenerisch\n"
         "G9kleidgenerisch.kennung('Röcke')            # 'kleidung_generisch_roecke' (Umlaute ausgeschrieben)\n"
         "G9kleidgenerisch.mischung_aufloesen('kleidung_generisch_alle', {'sorte.g9_base_shirt': 1.0, 'sorte.gc_dress_shift': 0.3})\n"
         "# → ([(kennung, anteil, regler_stueck), …], uebergang_m)   — leer, wenn es den Eintrag nicht (mehr) gibt\n"
         "G9kleidgenerisch.aufloesen('kleidung_generisch_roecke', werte)   # (stück_kennung, regler_stueck) des stärksten Stücks",
         [(G + 'kleidgenerisch.py', 'G9kleidgenerisch'), (G + 'kleidgenerischwahl.py', 'G9kleidgenerischwahl'),
          (G + 'garderobe.py', 'G9garderobe')],
         'gruppen() und die Eintragsliste brauchen die Daz-Bibliothek (G9garderobe.liste, G9garderobekategorien); '
         'G9kleidgenerischwahl (anteile, mischung, regler_von) kennt nur eine Stückliste und ist ohne Bibliothek prüfbar. '
         'getragene_aufloesen(roh) ersetzt in getragen[] den Sammeleintrag durch das echte (stärkste) Stück — sonst rechnet '
         'die Kollision (G9lagenanfrage) das Kleid durch die Schuhe. Die Mischung kennt seit 03.10.2026 KEINE Stückgrenze '
         'mehr (HOECHSTENS = None; vorher 4, Edgar „unbegrenzt"); TEXTUR_RAENGE = 4 gilt nur für die Textur-Regler des '
         'Browser-Shaders. Quelle: Genesis9/kleidgenerisch.py, kleidgenerischwahl.py (30.09.2026).'),

        ('Regel: Anteile bei Kleidung und bei Haar',
         'Hält fest, wie sich die Anteile hier von „Haar – Generisch“ unterscheiden — häufiger Denkfehler.',
         'regel',
         'Kleidung: Anteile unabhängig, keine Summe 100 %, 0 = fehlt, Vorgabe = erstes Stück 1,0. Haar: Anteile sind eine '
         'AUFTEILUNG, Summe immer 100 %.',
         [(G + 'kleidgenerischwahl.py', 'G9kleidgenerischwahl'), (G + 'haargenerisch.py', 'G9haargenerisch')],
         'Edgar (30.09.2026): Kleidung „Die Summe der Mischungen muss nicht 100 % ergeben“; Haar „der Anteil der anderen '
         'proportional sinken, so dass die Summe aller Anteile immer 100 % ist“. Beide benutzen dieselben Schlüssel '
         'sorte.<kennung>; das Zeichen mischbar: true am Eintrag schaltet im Browser die Normierung (Sortenanteile) nur '
         'für Haar ein. Bei Kleidung wäre ein „Anteil an Inseln“ falsch: ein Stück hat 1–70 Inseln (Outfits bis 341), jede '
         'ein TEIL des Stücks (Ärmel, Vorderteil, Bund) — ein 30-%-Anteil ließe Ärmel oder Rücken fehlen (gemessen '
         '30.09.2026, 6 Stücke je Kategorie, genesis9-garderobe.md). Beide Gruppen: Wo nichts gesetzt ist, gilt die '
         'Grundsorte — bei Kleidung das erste Stück der Liste, bei Haar kin_hair.'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('G9garderobeapi', 'ruft', 'G9kleidgenerisch',
         'eintraege() für die Liste; mischung_aufloesen(), aufloesen(), getragene_aufloesen() in kleidnetz()'),
        ('G9garderobeapi', 'ruft', 'G9garderobe', 'G9garderobe.liste() und eintrag(): die Stücke und ihre Regler'),
        ('G9garderobeapi', 'ruft', 'G9haargenerisch', 'G9haargenerisch.ist_generisch(): „Haar – Generisch“ baut G9haarmischbau, nicht diese Mischung'),
        ('G9garderobeapi', 'ruft', 'G9kleidmischbau',
         'G9kleidmischbau.antwort(rumpf, kleid, kennung, folge, uebergang, koerper): die Mischung mehrerer Stücke'),
        ('G9kleidgenerisch', 'ruft', 'G9kleidgenerischwahl',
         'erbt anteile(), mischung(), regler_von(), uebergang(), ohne_textur(), sorte()'),
        ('G9kleidgenerisch', 'ruft', 'G9garderobe', 'G9garderobe.liste(): gruppen() sortiert die Stücke nach Kategorie'),
        ('G9kleidmischbau', 'ruft', 'G9kleidmischflaeche',
         'G9kleidmischflaeche.aus_netz(): Hautstelle und Versatz je Punkt; stoff_misch() für den Stoffschwung'),
        ('G9kleidmischbau', 'ruft', 'G9kleidmischung',
         'G9kleidmischung.mischen(flaechen, anteile, reihenfolge, uebergang): die gemischte Fläche'),
        ('G9kleidmischbau', 'ruft', 'G9kleidfarbe', 'G9kleidfarbe.farben(netz): Farbe je Teil für den Textur-Regler (fremd)'),
    ]

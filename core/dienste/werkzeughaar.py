# -*- coding: utf-8 -*-
"""Werkzeughaar — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: Haar wählen, mischen, färben („Haar – Generisch").

Reine Daten (Schema: `ProjektTemp/_wegwerf/stoff_ausbau/AUFTRAG_TOOLS.md`); gelesen von `Architektur2d3dwerkzeuge`.
Jede Zeile ist gegen den Code gelesen (03.10.2026); Zahlen tragen Fundstelle und Datum.
"""

__all__ = ['Werkzeughaar']


class Werkzeughaar:
    G = 'Genesis9/'
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'

    KENNUNG = 'haar'
    TITEL = 'Haar: Frisuren wählen, mischen, Länge, Farbe, Zonen, Bart (Haar – Generisch)'
    EINLEITUNG = (
        '„Haar – Generisch“ (Kennung haar_generisch) ist ein Sammeleintrag ohne eigenes Netz: er führt die Regler ALLER '
        'Frisuren der Garderobe — je Frisur eine Gruppe mit ihrem Namen — und baut eine Mischung. Zwei Frisurnetze lassen '
        'sich nicht ineinander morphen (eigene Punktzahl, UV, Texturen); deshalb haben alle Frisuren dieselben fünf '
        'Formachsen, und die Mischung trägt die Strähnen beider Sorten nebeneinander. Reihenfolge: 1. Frisur wählen '
        '(haar_nur / haar_anteil), 2. Form (haar_achse, Operationen in der Gruppe „Haar formen“), 3. Farbe (haar_farbe, '
        'haar_zonenfarbe, Gruppe „Textur“ für haar_umfaerben), 4. Bart dazu. Stile und Farbvarianten der Bibliothek '
        'kennt das Rezept nicht (stil leer, variante leer in kleidung_modell()); wer sie braucht, nimmt die Zeile der '
        'Frisur selbst in der Szene.')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Haar – Generisch in der Szene',
         'Zeigt den Sammeleintrag als ersten der Kategorie „Haare“; je Frisur eine aufklappbare Gruppe mit Anteil, Morphen, '
         'Formachsen und Ortsreglern.',
         'seite',
         'Szene /Charakter/ (Menü Dashboard → Charakter) → Reiter Assets → Genesis → Haare → „Haar – Generisch“; Regler '
         'sorte.<kennung>, <kennung>.<kanal>, <kennung>.achse.<name>, <kennung>.ort.*, <kennung>.str.*, <kennung>.profil.*, '
         '<kennung>.eigen.*',
         [(G + 'haargenerisch.py', 'G9haargenerisch'), (A + 'g9garderobe.py', 'G9garderobeapi'),
          (G + 'haarachsen.py', 'G9haarachsen')],
         'Stand 30.09.2026 (engine2d3dkleider.md): 412 Regler in 18 Gruppen, alle gemessen wirksam (304 Daz-Morphe + 90 '
         'Formachsen); seither dazu die Ortsregler je Sorte, Strähnendicke, Zusatzsträhnen und die 13 festen Operationen. '
         'Die GETRAGENE Frisur steht auf 100 %, die anderen auf 0 — sonst verdrängte der kleinste Anteil einer anderen Sorte '
         'die getragene. Im Browser normiert HumanBodyWeb/static/viewer/charakter/genesis9/sortenanteile.js sichtbar: der '
         'gezogene Regler bekommt seinen Wert, die anderen skalieren proportional; das alte Verhältnis kehrt zurück, wenn die '
         'neue Sorte wieder auf 0 geht. Alle Kästen sind beim Laden zu (kein Gedächtnis).'),

        ('Regel: die 18 Frisuren und was sie können',
         'Das Inventar der Frisuren — Kennung, Name, Daz-Regler, Netze, Klon — damit man die richtige Kennung hat.',
         'regel',
         'kin_hair, dforce_mk_hime_cut_hair, mavick_hair, mavick_beard, eirgrid_hair_g9, eirgrid_hair_g9_with_dforce, '
         'g9_base_dforce_pixie_hair, hs_viola_hair_g9, genesis_9_toon_base_anime_hair, haar_eigen, toulouse_hair, '
         'mavick_hair_style, charm_hair, basic_hair, aldora_hair, duke_hair, sallymae_hair, wildmane_hair',
         [(G + 'haargenerisch.py', 'G9haargenerisch'), (G + 'haarachsen.py', 'G9haarachsen')],
         'Quelle: Assets/kleidung/engine2d3dkleider.py (HAARE, 30.09.2026) — die Tabelle der Seite Hilfe → Kleidung → 2D3D '
         'Kleider. Daz-Regler je Frisur: Kin 4, Hime Cut 24, Mavick 4, Mavick Beard 0, Eirgrid 27 (mit 14 eigenen Knochen: '
         'Zopf), Pixie 4 (2 Netze), Viola 2 (3 Netze), Toon 20 (2 Netze), Haar Eigen 5, Toulouse 28, Charm 39, Basic 23, '
         'Aldora 17, Duke 16, SallyMae 26, WildMane 34. STRANGHAAR sind Pixie, Hime Cut und Viola (Karten haben die '
         'übrigen); der Bart (…_beard) ist eine Sorte, keine Frisur. Klone (Daz-Frisuren anderer Figuren, per Auto-Fit): '
         'Toulouse, Mavick Hair Style, Charm, Basic, Aldora, Duke, SallyMae, WildMane.'),

        ('Frisur wählen: nur diese, volle Dichte',
         'Setzt alle Sorten auf 0 und die genannte Frisur auf 1.',
         'rezept',
         "m.haar_nur('mavick_hair')",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haargenerisch.py', 'G9haargenerisch')],
         'Nullt auch die Bartsorten (sie beginnen ebenfalls mit sorte.) — einen Bart danach wieder mit haar_anteil dazuholen '
         '(IterationHaare.bart macht genau das, wenn die Frisur wechselt). Kennung exakt wie in der Garderobenliste (siehe '
         '„die 18 Frisuren“). Quelle: Genesis9/modellhaar.py.'),

        ('Anteil einer Frisur setzen (Mischen), auch nach Ort',
         'Stellt den Anteil einer Frisur; die Anteile sind eine Aufteilung (Summe 100 %). Mit ort trägt die Sorte ihre '
         'Strähnen nur dort — ein Pony aus Sorte B, der Rest Sorte A.',
         'rezept',
         "m.haar_anteil('toulouse_hair', 0.3)\n"
         "m.haar_anteil('mavick_hair', 0.4, {'sektor': (-40, 40), 'band': (0.5, 1.0)})",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haargenerisch.py', 'G9haargenerisch'),
          (G + 'haarmischung.py', 'G9haarmischung'), (D + 'g9haarmischbau.py', 'G9haarmischbau')],
         'anteil 0…1; G9haargenerisch.anteile normiert auf 100 % (Bartsorten _beard ausgenommen), höchstens 4 Sorten '
         '(HOECHSTENS), unter 0,005 fällt weg. haar_anteil legt für die Grundsorte kin_hair ausdrücklich den Regler 0 an — '
         'sonst trug „Edgar - Hoch“ Kin UND Mavick (30.09.2026, Runde 1). Die erste Sorte (Hauptsorte, größter Anteil, bei '
         'Gleichstand die zuletzt bewegte) bringt die Kappe mit, die übrigen nur Strähnen (zwei Kappen flimmerten): Pixie 60 + '
         'Basic 40 → 1 Kappe, Basic 60 + Pixie 40 → 0. Mischen über die Strähnendichte: ganze Inseln, nie jede n-te Fläche, '
         'Nahtkopien über die Lage verbunden, feste Saat je Sorte und Teil (gleiche Anteile = gleiche Bytes). Inseln: Kin '
         '4.225, Mavick 32.316, Toulouse 236, Basic 62, die größte höchstens 15 % (engine2d3dkleider.md, 30.09.2026). '
         'ort: sektor in Grad um die Kopfachse (0 vorn, positiv links) und/oder band 0…1; die Strähnen mit Schwerpunkt im '
         'Ort gelten als geeignet (G9haarmischung.eignung). Gemessen 30.09.2026: 70 % Kin + 30 % Toulouse → 288.787 + 10.931 '
         'Punkte, Endpunkt 1,5 s kalt, 0,02 s aus dem Vorrat; auf HumanBody Kin 70 + Toulouse 30 → 291.203 + 10.931 '
         '(genesis9-humanbody.md).'),

        ('Keine Bibliotheksfrisur (bekannte Grenze)',
         'Setzt alle Sorten auf 0, auch die Grundsorte — gedacht für Haar aus dem Netz der Fotos als eigenes Stück.',
         'rezept',
         "m.haar_keins()",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haargenerisch.py', 'G9haargenerisch')],
         'Macht NICHT kahl: stehen alle Sorten auf 0, gilt die Grundsorte kin_hair wieder als 1,0 (G9haargenerisch.anteile: '
         '„eine Figur wird nicht aus Versehen kahl“; Kleiderwahl.py Zeile 52: haar_keins „ließ die Grundsorte stehen, Runde '
         '17“). Deshalb ist IterationHaare.FOTOHAAR aus und das Haar bleibt eine Bibliotheksfrisur. Kahl bekommt man nur '
         'über kleidung_modell() (lässt den Eintrag weg, wenn kein Anteil über 0 steht) — der Python-Bau über '
         'Kleidermodellbau._haar trägt weiter Kin Hair (gelesen, nicht ausprobiert).'),

        ('Daz-Morph einer Frisur stellen',
         'Stellt einen echten Daz-Morph der Frisur (Pony, Länge, Zopfform …).',
         'rezept',
         "m.haar_morph('kin_hair', '<Kanalname aus der Reglerliste>', 0.5)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haargenerisch.py', 'G9haargenerisch')],
         'kanal = name des Reglers in der Reglerliste der Frisur (GET …/garderobe/, regler[].name); unbekannte Namen '
         'bleiben wirkungslos. Der Schlüssel im Modell ist <kennung>.<kanal>. Zahl der Daz-Regler je Frisur: siehe „die 18 '
         'Frisuren“ (zusammen 304 Daz-Morphe, 30.09.2026).'),

        ('Formachse einer Frisur: Länge, Kurz, Dichte, Wellig, Dutt',
         'Stellt eine der fünf gemeinsamen Formachsen — an jeder Frisur gleich — auf 0…1.',
         'rezept',
         "m.haar_achse('kin_hair', 'laenge', 0.7)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haarachsen.py', 'G9haarachsen'),
          (G + 'haareigenmorphe.py', 'G9haareigenmorphe')],
         'achse ∈ laenge, kurz, dichte, wellig, dutt (sonst ValueError). Die Achsen sind Deltas NEBEN der Bibliothek '
         '(3DObjects/Genesis9/haarachsen/<kennung>_f1.npz), linear wie Daz-Morphe, für alle 18 Frisuren vorhanden '
         '(Verzeichnis gelesen 03.10.2026; Bau 45 s für alle am 30.09.2026). Fehlt die Ablage einer Frisur, ist der Aufruf '
         'STILL wirkungslos (G9haarachsen.anwenden gibt die Käfige unverändert zurück) — dann bauen (Zeile „Formachsen '
         'bauen“). achse.laenge = 1 bewegt 13,7 % (Duke) bis 100 % (Mavick Beard) der Punkte, größter Weg 42,2 mm (Basic) bis '
         '428,4 mm (Kin Hair) (engine2d3dkleider.md, 30.09.2026). Gegenprobe gegen „Haar Eigen“: gleiche Wege. Die '
         'Automatik sucht die Länge per Bergsuche gegen den Haarabstand zum Netz (IterationHaare.laenge).'),

        ('Haarfarbe der ganzen Frisur',
         'Tönt die Frisur mit einer Farbe (#rrggbb); die Textur bleibt, wird getönt.',
         'rezept',
         "m.haar_farbe('#47332a')",
         [(G + 'modellhaar.py', 'ModellHaarMixin')],
         'Vorgabe #47332a (FARBEN). Tönung × 2 × Textur, begrenzt auf 0…1: blondes Haar lässt sich so nicht grau oder '
         'schwarz tönen — erst m.haar_umfaerben (Gruppe „Textur“). Ein ZIELWERT als Tönung trifft nie (Mavick blieb blond); '
         'die Automatik rechnet Tönung × (Foto ÷ Render), gedämpft 0,7 (Farbangleich). Falsches Format: ValueError.'),

        ('Haarfarbe je Kopfzone (oben, hinten, vorn, seite)',
         'Stellt eine eigene Farbe für eine Zone des Kopfhaars — die Fotos zeigen das Haar oben heller als hinten.',
         'rezept',
         "m.haar_zonenfarbe('oben', '#8a8580')",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (D + 'haarzonen.py', 'Haarzonen')],
         'zone ∈ oben, hinten, vorn, seite (sonst ValueError). Gebaut als Farbfaktor je Zone = Zonenfarbe ÷ Haarfarbe, auf '
         '0,4…2,5 begrenzt (Haarzonen.faktoren) — also nur zusammen mit haar_farbe sinnvoll. Wirkt nur auf Kartenhaar mit '
         'Textur (Strähnen ohne Textur und Bart bleiben außen); die Zone ergibt sich aus der Richtung des '
         'Dreiecksschwerpunkts von der Kopfmitte (oben ab y > 0,55, hinten/vorn ab |z| > 0,35). Messung aus den Fotos: '
         'Haarzonen.messen (einmal je Frisur, ergebnis.haarzonen). Befund Edgar 01.10.2026: „das haar hat oben eine andere '
         'Farbe als unten“ (Haarzonen.py, 02.10.2026).'),

        ('Bart dazuholen',
         'Zieht den Bart (eigene Sorte, außerhalb der 100-%-Normierung) zusätzlich zur Frisur an.',
         'rezept',
         "m.haar_anteil('mavick_beard', 1.0)",
         [(G + 'modellhaar.py', 'ModellHaarMixin'), (G + 'haargenerisch.py', 'G9haargenerisch'),
          (D + 'haarzonen.py', 'Haarzonen')],
         'Bartsorten enden auf _beard (G9haargenerisch.ZUSATZ): ihr Anteil bleibt ihre Dichte 0…1, sie normieren sich '
         'nicht mit der Frisur (sonst kostete ein Bart die halbe Frisur), sind nie Kappe und stehen in der Reihenfolge '
         'hinten (01.10.2026). Ob die Fotos einen Bart zeigen, steht in befund["zubehoer"]["bart"]: mindestens 300 Flächen '
         'in der Bartzone der Haarmaske und nur auf der männlichen Grundfigur (Begutachtungswerkzeug.BART_MIN, _bart; '
         'Testauftrag 2026.10.01.12.38.09: 2.064). Der Bart bekommt keine Zonenfarbe (Haarzonen.OHNE); die Automatik färbt '
         'ihn wie die Frisur mit haar_umfaerben (IterationHaare.bart).'),

        ('Sammeleintrag anfragen: Frisuren mischen (Server)',
         'Baut das Netz der Mischung: jede Sorte mit Anteil wird gebaut und auf ihren Anteil an Strähnen ausgedünnt.',
         'api',
         'POST /api/character/genesis9-figur/garderobe/haar_generisch/netz/\n'
         '{regler: {…}, regler_stueck: {"sorte.kin_hair": 0.7, "sorte.toulouse_hair": 0.3, "kin_hair.achse.laenge": 0.5}, '
         'getragen: [], rang: 1}\n'
         '→ {kennung: "haar_generisch", teile: […], boden, stufen, innen, aussen, art: "haar"}',
         [(A + 'g9garderobe.py', 'G9garderobeapi'), (G + 'haargenerisch.py', 'G9haargenerisch'),
          (D + 'g9haarmischbau.py', 'G9haarmischbau'), (G + 'haarmischung.py', 'G9haarmischung'),
          (D + 'g9stueckteile.py', 'G9stueckteile'), (G + 'haarachsen.py', 'G9haarachsen')],
         'Die Kennung bleibt haar_generisch; der Browser hängt die Teile darunter ein (haar_generisch/0…n), die Farbe des '
         'Eintrags färbt alle. Die Kappe kommt nur von der Hauptsorte. Der Stoffschwung (dForce) eines gemischten Haars '
         'fällt beim Ausdünnen weg (stoff, Käfigbezug). Auf einer HumanBody-Figur dasselbe über deren Bauweg '
         '(G9kleidhumanbody.antwort, G9hbstrang für Stranghaar: Stichprobe ≤ 40.000 Punkte): Kin Hair kostete dort kalt 88 s, '
         'seit 30.09.2026 abends 68 s (genesis9-humanbody.md). Die fünf Achsen wirken dort auf dem Genesis-Grundkörper '
         'VOR der Übertragung.'),

        ('Haar-Sammeleintrag in Python auflösen',
         'Liest aus einem Wertesatz die getragenen Frisuren mit Anteilen (Summe 1) und die Hauptsorte.',
         'python',
         "from Genesis9.haargenerisch import G9haargenerisch\n"
         "G9haargenerisch.mischung({'sorte.kin_hair': 0.7, 'sorte.toulouse_hair': 0.3})   # [(kennung, anteil, regler_stueck), …]\n"
         "G9haargenerisch.aufloesen(werte)   # (kennung, regler_stueck) der Hauptsorte — oder (None, {})",
         [(G + 'haargenerisch.py', 'G9haargenerisch')],
         'anteile, mischung, sorte und aufloesen brauchen die Daz-Bibliothek (frisuren() liest G9garderobe.liste()). '
         'Bartsorten stehen hinten und zählen nicht in die Summe. Quelle: Genesis9/haargenerisch.py (30.09.2026).'),

        ('Formachsen bauen (alle Frisuren)',
         'Rechnet die fünf Formachsen als Deltas für jede Frisur der Garderobe und legt sie neben der Bibliothek ab.',
         'cli',
         'cd A:/3DTools && python14/Scripts/python.exe -m Genesis9.haarachsen [--nur <teilwort>] [--neu]',
         [(G + 'haarachsen.py', 'G9haarachsen'), (G + 'haareigenmorphe.py', 'G9haareigenmorphe')],
         '--nur beschränkt auf Frisuren, deren Kennung das Teilwort enthält; --neu baut auch Aktuelles neu. Je Frisur 0,2 bis '
         '6,0 s, alle 18 zusammen 45 s (Assets/kleidung/engine2d3dkleider.py ACHSEN_STAPEL_S, 30.09.2026). Die Ablage trägt die '
         'Fassung im Namen (…_f1) und prüft den Bestand der Bibliothek (G9bestand): ändert sich die Bibliothek, baut der nächste '
         'Lauf neu. Heute vorhanden: alle 18 (Verzeichnis 3DObjects/Genesis9/haarachsen gelesen, 03.10.2026). Nur dann '
         'laufen lassen, wenn eine Frisur fehlt.'),

        ('„Haar Eigen“ bauen (geklonte Frisur mit Formreglern)',
         'Klont Kin Hair in die eigene Bibliothek, mit Länge, Kurz, Dichte, Wellig, Dutt als Daz-Morphe und den Farbpresets.',
         'cli',
         'cd A:/3DTools && python14/Scripts/python.exe -m Genesis9.haareigen [Vorlage]',
         [(G + 'haareigen.py', 'G9haareigen'), (G + 'haareigenmorphe.py', 'G9haareigenmorphe')],
         'Gebaut beim ersten Lauf von „Mesh to 3D“ (G9haareigen.sicherstellen, 64 s; haar.md 29.09.2026) oder von Hand. Netz mit '
         'den Vorgaben eingerechnet, Materialien/UV/Bilder/Hautbindung der Vorlage, 10 Farbpresets; Ablage '
         '3DObjects/Genesis9/eigene_stuecke/Haar_Eigen/bilanz.json und People/Genesis 9/Hair/EIGEN/Haar Eigen/ in der '
         'eigenen Bibliothek. Grenzen der Klon-Bauart: genau ein Netz, kein Klon, keine eigenen Knochen (daher die '
         'Formachsen für alle Frisuren ohne Klon). Der Server liest die Liste neu, wenn sich die .dsx der eigenen Wurzel '
         'ändern (G9eigenstand).'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('ModellHaarMixin', 'ruft', 'G9haargenerisch', 'G9haargenerisch.VORGABE und ZUSATZ: haar_anteil() legt die Grundsorte auf 0, haar_keins() setzt alle'),
        ('ModellHaarMixin', 'ruft', 'G9haarachsen', 'G9haarachsen.KANAELE und PRAEFIX: haar_achse() prüft den Kanal'),
        ('G9garderobeapi', 'ruft', 'G9haargenerisch', 'eintrag() für die Liste; ist_generisch() erkennt den Sammeleintrag in kleidnetz()'),
        ('G9garderobeapi', 'ruft', 'G9haarachsen', 'G9haarachsen.erweitern(): fünf Achsen je Frisur in der Liste'),
        ('G9garderobeapi', 'ruft', 'G9haarmischbau', 'G9haarmischbau.antwort(rumpf, kleid): die Mischung'),
        ('G9haarmischbau', 'ruft', 'G9haargenerisch', 'G9haargenerisch.mischung(): Aufteilung (kennung, anteil, regler)'),
        ('G9haarmischbau', 'ruft', 'G9haarmischung', 'G9haarmischung.ausduennen(), ort_aus(), eignung(): Strähnen je Sorte'),
        ('G9stueckteile', 'ruft', 'G9haarachsen', 'G9haarachsen.anwenden(): Achsen auf den Käfig (linear)'),
        ('G9haarachsen', 'ruft', 'G9haareigenmorphe', 'G9haareigenmorphe(punkte, kopf, koerper): rechnet je Achse die Deltas'),
        ('G9haareigen', 'ruft', 'G9haareigenmorphe', 'G9haareigenmorphe.steckbrief(): Wege der fünf Regler im Klon'),
        ('G9haargenerisch', 'ruft', 'G9haarachsen', 'G9haarachsen.vorhanden() und regler(): Formachsen je Frisur in regler()'),
    ]

# -*- coding: utf-8 -*-
"""Werkzeugkleiderautomatik — Reiter „Tools" der Seite Architektur 2D3D, Gruppe T2: Rezeptregeln für Kleider und Haar.

Der Ordner `2d3DIterationen` (Paket `iterationen2d3d`): die Regeln, die eine automatische Runde von selbst als Rezeptzeilen
schreibt. Reine Daten (Schema: `ProjektTemp/_wegwerf/stoff_ausbau/AUFTRAG_TOOLS.md`); gelesen von
`Architektur2d3dwerkzeuge`. Jede Zeile ist gegen den Code gelesen (03.10.2026); Zahlen tragen Fundstelle und Datum.
"""

__all__ = ['Werkzeugkleiderautomatik']


class Werkzeugkleiderautomatik:
    P = '2d3DIterationen/iterationen2d3d/'

    KENNUNG = 'kleiderautomatik'
    TITEL = 'Automatik: Rezeptregeln für Kleider und Haar (2d3DIterationen)'
    EINLEITUNG = (
        'Eine automatische Runde ist ein Rezept wie eines von Hand: IterationModell(modell, befund, verlauf, kandidaten).rezept() '
        'liefert Text, eine Zeile je Aufruf; die Begutachtungsrunde wendet ihn mit G9rezept an und legt ihn ab (aufrufe, '
        'automatisch: true). Die Klassen ändern das Modell NICHT selbst — jede Änderung bleibt als Rezept nachlesbar und '
        'wiederholbar (GET …/rezept/). Ohne Django, nur NumPy: Zustand ist ModellMitKleidern, Eingang der Befund der '
        'letzten Runde (Befundmessung). Wer ein Modell an Fotos anpasst, schreibt dieselben Zeilen von Hand; die Regeln hier '
        'zeigen, welche Zeile bei welchem Befund gilt. Die Automatik rechnet nie Blender und keine Haar-Dynamik, und ihre '
        'Gesamtnote ist ein Hilfsmaß: nach JEDER Runde sieht Fable die Vergleichstafel an und verbessert den Code '
        '(Vorgabe Edgar 30.09./02.10.2026, engine2d3dkleider.md). Eine Schleife starten darf nur, wer dazu den Auftrag hat '
        '(Gruppe Bildvergleich, T4).')

    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Rezept einer Runde aus dem Befund (Einstieg)',
         'Schreibt, was die Runde tun soll: Haltung, Körper/Gesicht (nur mit form), Kleider, Textur, Haar — als Rezepttext.',
         'python',
         "import sys\n"
         "sys.path[:0] = ['A:/3DTools', 'A:/3DTools/2d3DIterationen']\n"
         "from iterationen2d3d.iterationmodell import IterationModell\n"
         "text = IterationModell(m, befund, verlauf, kandidaten, form=False).rezept()   # '' ohne Änderung\n"
         "zeilen = IterationModell(m, befund, verlauf, kandidaten).aufrufe()            # nur die Liste",
         [(P + 'iterationmodell.py', 'IterationModell'), (P + 'iterationkleider.py', 'IterationKleider'),
          (P + 'iterationtextur.py', 'IterationTextur'), (P + 'iterationhaare.py', 'IterationHaare')],
         'm = ModellMitKleidern; befund = Messung der letzten Runde (Befundmessung.befund plus note, haltung); verlauf = '
         'Kurzbefunde aller Runden (IterationModell.verlaufseintrag); kandidaten = Frisuren aus „Mesh to 3D“. Reihenfolge in '
         'aufrufe(): haltung, [Körper, Gesicht nur bei form], Kleider, Textur, Haar. Die A-Pose bleibt die Bauhaltung: gebaut '
         'wird in A-Pose, die Runde häutet für Render und Note in die Haltung der Fotos (G9haltungshaut; Edgar 30.09.2026: '
         '„Das Modell soll in A-Pose angezeigt werden“). Quelle: 2d3DIterationen/README.md.'),

        ('Kleider: anziehen, Farbe, Weite, Hülle, Morphe, Drapieren',
         'Die Regeln für die Kleider — jede schreibt Rezeptzeilen aus dem Befund.',
         'python',
         "from iterationen2d3d.iterationkleider import IterationKleider\n"
         "IterationKleider(m, befund, verlauf).aufrufe()   # anziehen | farbe + weite + huelle + morphe + kleidring + drapieren",
         [(P + 'iterationkleider.py', 'IterationKleider'), (P + 'iterationkleidring.py', 'IterationKleidring'),
          (P + 'kleiderwahl.py', 'Kleiderwahl'), (P + 'farbangleich.py', 'Farbangleich')],
         'anziehen: ohne Kleider die Stücke der Kleiderwahl, mit Kleidern die, die noch fehlen; farbe: kleid_farbe_je_stueck '
         '(Tönung × Foto ÷ Render, gedämpft; bei unerreichbarer Farbe erst kleid_umfaerben); weite: passform(weite_cm) um '
         '−WEITE_DAEMPFUNG (0,35) × (Stoffabstand − Körperabstand) cm, ein Stück mit Rest > 50 mm (WEITE_REST_MAX_MM) zählt '
         'nicht; huelle: kleid_huelle, wenn ein Stück deutlich von der Silhouette absteht; morphe: je Band × Sektor ab '
         'BAND_MM 8 mm ein Ortsmorph netz_b<i>s<j> in Hautrichtung (MORPH_DAEMPFUNG 0,35, weich MORPH_WEICH 0,3), Luft zur Haut '
         'mindestens 3 mm (HAUT_MIN_MM); drapieren: einmal je Stück, wenn der Stoffabstand drei Runden lang innerhalb 2 mm '
         'steht und die Weite nichts mehr meldet — immer mit dem Vorgabe-Motor newton, 24 Bilder (DRAPE_BILDER). Abweichung '
         'Doku gegen Code: README.md und engine2d3dkleider.md nennen die Zellenmorphe „±2 cm“, im Code steht '
         'MORPH_MAX = 1.0 (cm) (Stand 03.10.2026). Messregel: Ziel ist „Stoff so weit vom Netz wie der Körper selbst“ '
         '(Grundlinie je Stück im Kasten des Stücks, grund_mm) — mit dem Körpermittel lief die Weite in elf Runden an den '
         'Anschlag („Edgar - Hoch“, 30.09.2026).'),

        ('Welche Stücke trägt die Figur zuerst? (Kleiderwahl)',
         'Bestimmt aus den Farben der Körperbänder des Fotos, ob Haut oder Stoff, und wählt Oberteil, Shorts oder Hose, Socken.',
         'python',
         "from iterationen2d3d.kleiderwahl import Kleiderwahl\n"
         "Kleiderwahl.soll(koerper_baender, zubehoer=None, fotostuecke=None)   # → ['g9_base_shirt', 'g9_base_shorts', …]\n"
         "Kleiderwahl.fehlende(koerper_baender, getragen, zubehoer=None)",
         [(P + 'kleiderwahl.py', 'Kleiderwahl')],
         'Vorgaben: g9_base_shirt (Oberteil, wenn das Rumpfband keine Haut zeigt), g9_base_shorts (Oberschenkelband zeigt '
         'Haut) oder angie_jeans (sonst), gc_crudelowsocks (Fuß bedeckt, Bein nackt), eigen_uhr_<seite> (Zubehör). Haut = '
         'rötlich-warm (r > g > b und r − b > HAUT_ABSTAND 0,12) — keine Erkennung von Kleidungsstücken, nur Haut oder '
         'nicht; ein Kleid heißt Oberteil plus Hose. Mit Fotostücken (befund["fotostuecke"]) ersetzen diese die '
         'Bibliotheksstücke (FOTO_REIHE oberteil, hose, socken); fest(sorte) nennt Stücke ohne Formregeln (Socken, Uhr, '
         'Fotostücke). Quelle: Job „Edgar - TEST“, 30.09.2026 (Shirt + Shorts).'),

        ('Textur: Fotoprojektion, Falten, Decal nach Befund',
         'Schreibt kleid_fototextur, kleid_falten und kleid_decal, wenn die Form steht und das Foto mehr zeigt als der Render.',
         'python',
         "from iterationen2d3d.iterationtextur import IterationTextur\n"
         "IterationTextur(m, befund, verlauf).aufrufe()   # fotostuecke + fototextur + falten + decal",
         [(P + 'iterationtextur.py', 'IterationTextur')],
         'fototextur: einmal je Stück, wenn die Form drei Runden lang stillsteht (STILL_MM 2); falten: wenn das Foto unter '
         'der Maske mehr Kantenenergie hat als der Render (KANTEN 0,02) und die Fototextur schon liegt (Abstand 4 cm, Tiefe '
         '0,5); decal: wenn die Fotofarbe eines Höhenbands um mehr als DECAL_ABSTAND 0,18 vom Mittel des Stücks abweicht '
         '(Deckung 0,8). Feste Stücke (Socken, Uhr, Fotostücke) sind ausgenommen: ihre Farbe war TRELLIS-Malerei, nicht Foto — '
         'die Annahme war bis 02.10.2026 falsch; unter der Maske von Uhr und Socken liegt im Foto Haut (Runde 20 wollte die '
         'Uhr hautbraun bemalen).'),

        ('Haar: Frisur, Farbe, Länge, Anlegen, Bart, Fototextur',
         'Die Regeln für das Haar nach dem Befund gegen das Netz.',
         'python',
         "from iterationen2d3d.iterationhaare import IterationHaare\n"
         "IterationHaare(m, befund, verlauf, kandidaten).aufrufe()   # Frisur | Bart + Farbe/Zonen + Länge/Anlegen/Trim + Fototextur",
         [(P + 'iterationhaare.py', 'IterationHaare'), (P + 'schrittsuche.py', 'Schrittsuche'),
          (P + 'farbangleich.py', 'Farbangleich')],
         'frisur: bleibt die Kandidatin aus „Mesh to 3D“; der Wechsel nach 3 Runden ohne Besserung des Haarabstands ist AUS '
         '(WECHSELN = False: der Abstand misst die Schale, nach drei stillen Runden kam Pixie statt der gemessen besten '
         'Mavick) — README.md beschreibt ihn noch als aktiv. FOTOHAAR = False (Haar aus dem Netz als Stück: Band über den '
         'Augen, haar_keins ließ die Grundsorte stehen). laenge: Formachse per Schrittsuche (Start 0, Schritt 0,2, 0…1) '
         'gegen den Haarabstand, erst ab LAENGE_AB_MM 6 mm; anlegen: Sektor der oberen Bänder > ANLEGEN_AB_MM außerhalb des '
         'Netzes → haar_anlegen mit Ort, danach +0,25 je Runde bis 1,5; bart: mavick_beard + haar_umfaerben, wenn die '
         'Haarmaske einen Bart zeigt. Mit Fotoabgleich (befund["haarabgleich"], Selbsttest treffer ≥ 0,7) übernimmt '
         'IterationHaarfoto Länge, trim, heben und anlegen nach den FOTOS — die Netzregeln legten sonst eine angedrückte '
         'Kappe mit Vorhang an (Prüfung Runde 19, 02.10.2026). Quelle: 2d3DIterationen/README.md, iterationhaarfoto.py.'),

        ('Bergsuche und Farbangleich (Bausteine)',
         'Die zwei gemeinsamen Bausteine der Regeln: ein Wert pro Runde per Bergsuche, die Tönung als Verhältnis Foto ÷ Render.',
         'python',
         "from iterationen2d3d.schrittsuche import Schrittsuche\n"
         "Schrittsuche(start=0.0, schritt=0.2, lo=0.0, hi=1.0).naechster([(0.2, 34.4), (0.4, 34.8)])   # → 0.3 (zurück, halber Schritt)\n"
         "from iterationen2d3d.farbangleich import Farbangleich\n"
         "Farbangleich.naechste(alt_hex, foto_rgb, render_rgb, pixel)   # neue Tönung #rrggbb oder None",
         [(P + 'schrittsuche.py', 'Schrittsuche'), (P + 'farbangleich.py', 'Farbangleich')],
         'Schrittsuche: ohne Verlauf der Startwert, mit einem Punkt ein Schritt nach oben (am Anschlag nach unten), danach '
         'weiter in die Richtung, die geholfen hat, sonst zurück mit halbem Schritt; unter KLEINSTER (0,2 des Startschritts) '
         'bleibt der Wert stehen (None). Farbangleich: Tönung = alte Tönung × (Foto ÷ Render), gedämpft 0,7 — ein ZIELWERT '
         'als Tönung trifft nie (Mavick blieb blond); unerreichbar() meldet, wenn die Daz-Farbe die Tönung verhindert '
         '(dann kleid_umfaerben/haar_umfaerben). Der Beispielverlauf ist ausgedacht und nur ein Muster der Form [(wert, maß)]; '
         'Rechenergebnis des Beispiels nicht ausgeführt.'),
    ]

    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('IterationModell', 'ruft', 'IterationKleider', 'IterationKleider(modell, befund, verlauf).aufrufe(): Kleider'),
        ('IterationModell', 'ruft', 'IterationTextur', 'IterationTextur(modell, befund, verlauf).aufrufe(): Textur'),
        ('IterationModell', 'ruft', 'IterationHaare', 'IterationHaare(modell, befund, verlauf, kandidaten).aufrufe(): Haar'),
        ('IterationKleider', 'ruft', 'Kleiderwahl', 'Kleiderwahl.soll() und fehlende(): anziehen(); fest(): Stücke ohne Formregeln'),
        ('IterationKleider', 'ruft', 'Farbangleich', 'Farbangleich.naechste(), unerreichbar(), start_grau(): farbe()'),
        ('IterationKleider', 'ruft', 'IterationKleidring', 'IterationKleidring(modell, grosse, grund).aufrufe(): kleid_ring'),
        ('IterationTextur', 'ruft', 'Kleiderwahl', 'Kleiderwahl.fest(): ohne Socken, Uhr, Fotostücke'),
        ('IterationHaare', 'ruft', 'Schrittsuche', 'LAENGE.naechster(verlauf): Länge der Formachse'),
        ('IterationHaare', 'ruft', 'Farbangleich', 'Farbangleich.naechste(): Haarfarbe'),
    ]

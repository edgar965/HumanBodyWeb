# -*- coding: utf-8 -*-
"""Werkzeugbildbefund — Gruppe „Bildvergleich: Gesichtsmaße gegen das Foto und Befundmessung“ des Reiters „Tools“ (03.10.2026).

Schema und Leser: `Architektur2d3dwerkzeuge`. Gelesen im Code: `Gesichtsmasse`, `Gesichtsvorrat`, `Haarabgleich`, `Begutachtungsbefund`,
`Befundmessung`, `Teilmasken`, `Bandbreite`, `Sichtkoerper`, `Messpruefung`, `Hautabstand`, `Begutachtungsrunde._runde`. Gelaufen ist hier nichts.
"""

__all__ = ['Werkzeugbildbefund']


class Werkzeugbildbefund:
    D = 'HumanBodyWeb/core/dienste/'
    P = '2d3DIterationen/iterationen2d3d/'
    RENDER = ('HumanBodyWeb/core/dienste/genesishaarrender.py', 'Genesishaarrender')
    KENNUNG = 'bildbefund'
    TITEL = 'Bildvergleich: Gesichtsmaße gegen das Foto und Befundmessung'
    EINLEITUNG = (
        'Neben der Note misst jede Runde einen Befund: Abstände und Farben je Teil, Breiten je Körperband, Gesichtsmaße, Kopfhaar. Aus ihm '
        'lesen die Regeln der Automatik — und Fable — WO ein Unterschied liegt (die Note sagt nur, DASS einer da ist). Reihenfolge in der '
        'Runde: 1. Kennfarben-Render je Blickwinkel (Teilmasken), 2. Render mit Texturen, 3. Befund messen (Befundmessung), 4. Messgüte '
        'prüfen (Messpruefung), 5. Gesichtsmaße und Kopfhaar gegen die Fotos. Vorher da sein muss ein Bezugsnetz (ohne es bleiben die '
        'Netzzahlen None, die Farben werden trotzdem gemessen) und die Landmarken der Fotos (Gruppe „Fotos und Blickwinkel“).'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Gesichtsmaße gegen das Foto',
         'Misst Breite, Augenabstand, Nase, Mund, Kinn auf dem Vorderfoto UND auf dem Kopf-Render mit demselben Detektor; das Verhältnis sagt, was zu ändern ist.',
         'python',
         '\n'.join((
             'from core.dienste.gesichtsmasse import Gesichtsmasse',
             'Gesichtsmasse(ablage, render).befund(teile, referenzen, aus_ordner)',
             '# → {foto, render, verhaeltnis, ansicht, winkel, kopfregler, fassung} oder None',
             'Gesichtsmasse(ablage, render).eintragen(befund, teile, referenzen, aus_ordner)   # schreibt befund["gesicht"]',
         )),
         [(D + 'gesichtsmasse.py', 'Gesichtsmasse'), (D + 'gesichtsvorrat.py', 'Gesichtsvorrat'),
          (D + 'fotolandmarken.py', 'Fotolandmarken'), RENDER],
         'Je Maß eine Strecke zwischen MediaPipe-Landmarken, geteilt durch die Gesichtshöhe Stirn (10) – Kinn (152): breite (234/454), augen '
         '(468/473), nase (129/358), nase_laenge (168/4), mund (61/291), kinn (17/152) und augen_hoehe (Stirn bis Augenmitte). verhaeltnis = '
         'Foto ÷ Render: über 1 heißt, das Maß ist im Foto größer als im Modell. Nur am Vorderfoto (|Winkel| ≤ 30°, VORN_BIS; das dem '
         'Winkel 0 nächste); ohne Vorderfoto oder erkanntes Gesicht kein Befund (None), ohne Abbruch der Runde. Der Kopf-Render (1024², alle '
         'Teile) wird über vier Saaten gerendert und je Maß der Median genommen — die Landmarken springen sonst um 1–2 %, mehr als '
         'Rundenauswahl.TOLERANZ (0,002); je Kopfstand wird nur einmal gemessen (Gesichtsvorrat, gesicht_vorrat.json im Arbeitsordner, höchstens '
         '200 Einträge, FASSUNG 3 im Schlüssel). Auf Ganzkörperfotos findet der FaceLandmarker das Gesicht erst im Kopfausschnitt der Pose '
         '(Wrapper-Fassung 2). Kosten: je Render ≈ 0,45 s bei 1024² (Kommentar bei SAATEN, nicht nachgemessen); Landmarken siehe Gruppe '
         '„Fotos und Blickwinkel“. kopfregler() nennt die sechs Suchworte der Kopfregler (Face Upper Width, Eyes Distance, Eyes Height A, '
         'Nose Width Lower, Lips Width, Chin Length); gestellt werden sie von IterationGesicht, hier wird nur gemessen. Quelle: Docstrings '
         'von Gesichtsmasse und Gesichtsvorrat, ortsmorphe.md (01.10.2026).'),

        ('Gesichtsmaße zweier Bilder vergleichen',
         'Der kleinste Weg zu EINEM Gesichtsvergleich ohne Runde: zwei Bilder, Landmarken, Verhältnis der Maße.',
         'python',
         '\n'.join((
             'from core.dienste.fotolandmarken import Fotolandmarken',
             'from core.dienste.gesichtsmasse import Gesichtsmasse',
             'b = Fotolandmarken(ablage).holen([foto_pfad, kopfrender_pfad])   # {dateiname: {gesicht, breite, hoehe, …}}',
             "m1 = Gesichtsmasse.masse(b[foto_pfad.name]['gesicht'], b[foto_pfad.name]['breite'], b[foto_pfad.name]['hoehe'])",
             "m2 = Gesichtsmasse.masse(b[kopfrender_pfad.name]['gesicht'], b[kopfrender_pfad.name]['breite'], b[kopfrender_pfad.name]['hoehe'])",
             '{k: round(m1[k] / m2[k], 4) for k in m1 if m1 and m2 and k in m2}   # > 1: im ersten Bild größer',
         )),
         [(D + 'gesichtsmasse.py', 'Gesichtsmasse'), (D + 'fotolandmarken.py', 'Fotolandmarken')],
         'Das macht Gesichtsmasse.befund im Kern auch; zusammengesetzt aus den gelesenen Signaturen, nicht ausgeführt. Das zweite Bild ist '
         'ein Kopf-Render (Genesishaarrender.bild_kopf, am besten 1024²) oder jedes andere Gesichtsbild. masse() braucht die 478 Punkte '
         'UND die Bildgröße: Ohne sie ist jede Breite um das Seitenverhältnis gestaucht (Foto 2123 × 4041: Gesichtsbreite 1,78 statt 0,94; '
         'engine2d3dkleider.md, 01.10.2026). Kosten: Wrapper ≈ 2 s Start + ≈ 0,3 s je Bild (Docstring Fotolandmarken). Ein Einzelwurf '
         'rauscht um 1–2 % je Maß (Docstring Gesichtsvorrat) — genau dagegen mittelt die Runde über vier Saaten. Fotolandmarken legt '
         'arbeit/fotolandmarken.json in der Ablage an: die Ablage des Auftrags nehmen, zu dem die Fotos gehören.'),

        ('Kopfhaar gegen das Foto',
         'Das Haar im Kopfausschnitt gegen die Fotos, je Höhenband und Sektor — sieht Ohren, Nacken und Stirn, die das Netz nicht zeigt.',
         'python',
         '\n'.join((
             'from core.dienste.haarabgleich import Haarabgleich',
             'Haarabgleich(ablage, render).eintragen(befund, teile, referenzen, modell_hoehe, aus_ordner)   # → befund["haarabgleich"] oder None',
         )),
         [(D + 'haarabgleich.py', 'Haarabgleich'), (D + 'pruefbilder.py', 'Pruefbilder'), RENDER],
         'befund["haarabgleich"]: teile[sorte] {haut, leer} (5 Bänder × 8 Sektoren: Anteil der gesehenen Frisurpunkte, an denen das Foto Haut '
         'zeigt bzw. nichts), ansichten[winkel] {iou, zuviel, fehlt, hals}, fehler (1 − mittlere IoU des Kopfhaars; der Haarterm der '
         'Gesamtnote, mal 0,25), treffer (Selbsttest der Abbildung), fassung (2). Foto-Haar = in der Figur und nicht hautfarben (Buntheit '
         'über der Otsu-Schwelle des Fotos, begrenzt auf 0,12–0,32; Mehrheitsfilter 5 px); unter der Halszeile zählt nichts — langes Haar '
         'über den Schultern sieht diese Messung nicht; Bartstoppeln zählen als Haut. Render: Kennfarben (Kopfhaar, Bart, Rest) im '
         'Kopfausschnitt 256², das Foto wird waagerecht auf dessen Kopfmitte gelegt. Anlass: Prüfung Runde 19 (Fable, Auftrag '
         '2026.10.01.20.10.04) — Haar über den Ohren und als Keil im Nacken, die Haarregeln maßen nur gegen das TRELLIS-Netz. Kosten: im '
         'Log-Abschnitt „Prüfbilder“ mit der Kopftafel (21,1–24,0 s kalt; Workflowzeiten), nicht getrennt gemessen. Quelle: Docstring '
         'Haarabgleich (02.10.2026).'),

        ('Befund einer Runde messen',
         'Abstände zum Netz, Farben und Kanten je Teil, Breiten je Körperband — die Zahlen, aus denen die Regeln ablesen.',
         'python',
         '\n'.join((
             'from core.dienste.begutachtungsbefund import Begutachtungsbefund',
             'messung = Begutachtungsbefund(netznote, sicht)                    # netznote: Iterationsnetznote oder None; sicht: Sichtkoerper oder None',
             'messung.masken(render, teile, referenz, pfad, (128, 192))         # je Ansicht: Kennfarben-Render → Teilmasken',
             'messung.render_dazu(referenz, render_als_iterationsbild)          # danach der Render mit Texturen (128 × 192)',
             'befund = messung.befund(teile)   # → {teile: {sorte: {…}}, koerper_baender, koerper_huelle}',
         )),
         [(D + 'begutachtungsbefund.py', 'Begutachtungsbefund'), (P + 'befundmessung.py', 'Befundmessung'), (P + 'netzmengen.py', 'Netzmengen'),
          (P + 'teilmasken.py', 'Teilmasken'), (D + 'begutachtungsrunde.py', 'Begutachtungsrunde')],
         'Je Teil: art, netz_mm und netz_abs_mm (Abstand zum Netz MIT Vorzeichen: + außen, − innen), baender (5 Höhenbänder), zellen (5 Bänder × 8 '
         'Sektoren), grund_mm (Abstand des Körpers zum Netz im Kasten des Teils plus 2 cm — die Grundlinie, an der der Stoff gemessen wird), '
         'huelle_mm (Weg bis zum Rand des Sichtkörpers), pixel, foto_farbe und render_farbe (Mittel unter der Maske des Teils über alle '
         'Ansichten), kanten_foto/kanten_render, farbbaender, bei Stücken haut_zellen/haut_min_mm/haut_innen. koerper_baender: Fotofarbe in '
         'Höhenbändern (fuss, unterschenkel, oberschenkel, rumpf, kopf); koerper_huelle: Breite je Körperband, Foto gegen Render. Die Normalen '
         'des Netzes müssen nach außen zeigen — Iterationsnetznote richtet sie am Vorzeichen des Volumens aus (eine Eichung am Schwerpunkt '
         'kippte das Vorzeichen: Er liegt bei einer Figur in der Lücke zwischen den Beinen, 30.09.2026). Netzmengen: Stoff misst nur gegen '
         'die Stofffläche des Netzes, Haar gegen alles außer Stoff, der Körper gegen alle Proben (Flächenlabels arbeit/kleidung_maske.npz; '
         'ohne Labels oder unter 100 Proben zählen alle). Läuft im Log-Abschnitt „Rendern 3 von 3“: 12,6–14,7 s kalt mit Netznote, Messgüte '
         'und Gesichtsmaßen (Workflowzeiten.RENDERN_3, auftrag.log …20.10.04). Quelle: Docstrings Begutachtungsbefund, Befundmessung, Netzmengen.'),

        ('Kennfarben: welcher Pixel gehört zu welchem Teil',
         'Ein zweiter Render mit einer Kennfarbe je Teil; daraus entsteht die Maske jedes Teils, gleiche Verdeckung wie im Bild.',
         'python',
         '\n'.join((
             'from iterationen2d3d.teilmasken import Teilmasken',
             'Teilmasken.messen(len(teile), kennbild)   # kennbild(farben, block) → (farbe (H, B, 3), maske (H, B)); → Masken (H, B) bool je Teil',
             'Teilmasken.farben(anzahl, ab=0)           # Kennfarben für einen Block von höchstens 7 Teilen',
             'Teilmasken.zuordnen(farbe, maske, anzahl, ab=0)',
             "# Kennbild: render.bild_teile([(punkte, dreiecke, farben[i]) …], winkel, pfad, groesse=(128, 192), kennung=True)",
         )),
         [(P + 'teilmasken.py', 'Teilmasken'), RENDER, (D + 'iterationsbild.py', 'Iterationsbild')],
         'Gesättigte Grundfarben (rot, grün, blau, gelb, magenta, cyan, weiß), unbeleuchtet und ohne Mischkante (Mitsuba: Albedo mit einer '
         'Abtastung); zuordnen liest je Pixel, welche Kanäle an sind (ab 50 % des hellsten). Höchstens 7 Teile je Bild; mehr Teile teilen sich '
         'in Blöcken, die Teile anderer Blöcke sind schwarz (sie verdecken weiter, zählen nicht). Bis 01.10.2026 abends liefen die Farben '
         'zyklisch: Der 7. Teil (der Bart) trug die Kennfarbe des Körpers und bekam dessen Maske, 4.176 px Hautton zählten als „Haar“ '
         '(Docstring Teilmasken). Läuft je Ansicht im Log-Abschnitt „Modell bauen“ (Architektur2d3dmessung.RUNDE); die Fotoprojektion '
         'braucht die Masken vor dem eigentlichen Render.'),

        ('Breite je Körperband: Foto gegen Render',
         'Wie viel breiter (mm je Seite) die Figur im Foto als im Render ist — unabhängig davon, wo die Beine stehen.',
         'python',
         '\n'.join((
             'from iterationen2d3d.bandbreite import Bandbreite',
             'Bandbreite.messen([(foto_maske, render_maske), …], Befundmessung.KOERPERBAENDER, hoehe_m)',
             '# → {fuss, unterschenkel, oberschenkel, rumpf, kopf}: mm je Seite, + = Foto breiter, None ohne genug Zeilen',
         )),
         [(P + 'bandbreite.py', 'Bandbreite'), (P + 'befundmessung.py', 'Befundmessung')],
         'Je Bildzeile des Bands die zusammenhängenden Läufe der Maske (Füße, Unterschenkel, Oberschenkel zwei, Rumpf und Kopf einer; die der '
         'Bildmitte nächsten, hängende Hände fallen heraus); eine Zeile zählt nur, wenn Foto und Render gleich viele Läufe haben. Ergebnis je '
         'Band der Median über alle Zeilen und Ansichten (mindestens 3 Zeilen). Masken auf der normierten Fläche (Iterationsbild). Ersetzt '
         'seit 01.10.2026 den Abstand der Körperpunkte zum Sichtkörper, der die Stellung mitmaß: nur 37 % der Körperpunkte lagen im Umriss, '
         'gemeldet wurde „Bein 80–130 mm zu dick“, die Dickenregler liefen an den Anschlag (Docstring Bandbreite). Auflösung: ein '
         'Bildpunkt ≈ 1 cm bei 192 px Flächenhöhe, der Median über ≈ 100 Zeilen liegt darunter (Docstring).'),

        ('Sichtkörper der Fotos',
         'Die Umrisse aller Fotos als Körper im Raum (visual hull): Ist ein Punkt in den Silhouetten, wie weit reicht der Körper?',
         'python',
         '\n'.join((
             'from iterationen2d3d.sichtkoerper import Sichtkoerper',
             'sicht = Sichtkoerper([(winkel, maske), …], hoehe_m, koerper_punkte)   # Masken der Fotos auf der normierten Fläche',
             'sicht.innen(punkte)          # (N,) Anteil der Ansichten, die den Punkt in der Silhouette sehen, 0…1',
             'sicht.ist_innen(punkte)      # (N,) bool: Anteil ≥ 0,85 (ANTEIL)',
             'sicht.rand(start, richtung)  # Weg in m je Strahl bis zum Rand (Schritt 5 mm, höchstens 0,8 m)',
             'sicht.netz()                 # → (punkte, dreiecke): der Sichtkörper als Netz',
         )),
         [(P + 'sichtkoerper.py', 'Sichtkoerper')],
         'Nach dem Muster von Kostuemhuelle/Kostuemsichtkoerper (BlenderModel), in NumPy. Grenzen (Docstring): mit zwei bis drei Fotos ist er '
         'zwischen den Ansichten eine „dicke Puppe“, er trifft Umrisse, keine Wölbungen — deshalb Ziel der Rezepte kleid_huelle und '
         'koerper_huelle, nicht Modell; bei 128 × 192 ist ein Bildpunkt ≈ 1 cm; ANTEIL 0,85 heißt bei zwei bis drei Fotos „alle“. Die Runde '
         'baut ihn je Lauf und Modellhöhe (Begutachtungswerkzeug.sichtkoerper, auf den cm gerundet). Ohne zwei Ansichten mindestens 30° '
         'auseinander begrenzt er die Tiefe nicht (Zeile Messgüte).'),

        ('Darf man der Messung trauen: Messgüte',
         'Selbsttest je Runde: Passen Render, Fotos und Modell übereinander? Sonst ruhen die Regeln, die auf dem Umriss beruhen.',
         'python',
         '\n'.join((
             'from iterationen2d3d.messpruefung import Messpruefung',
             'Messpruefung.pruefen([(winkel, foto_maske, render_maske), …], hoehe_m, koerper_punkte)',
             '# → {projektion, foto_rumpf, tiefe_gesehen, gueltig, huelle_gueltig}   (im Befund: befund.messguete)',
             "Messpruefung.erlaubt(befund, 'gueltig')   # darf eine Regel die Messung nutzen?",
         )),
         [(P + 'messpruefung.py', 'Messpruefung'), (P + 'sichtkoerper.py', 'Sichtkoerper')],
         'projektion: Der Sichtkörper aus den RENDERS muss den eigenen Körper enthalten, Anteil ≥ 0,95 (PROJEKTION_MIN) — sonst stimmen '
         'Projektion und Normierung von Render und Messung nicht zusammen, und KEINE Messung gegen die Fotos gilt (gueltig). foto_rumpf: Der '
         'Sichtkörper aus den FOTOS muss den Rumpf enthalten (Körperpunkte zwischen 45 und 75 % der Höhe, nahe der Achse), Anteil ≥ 0,8 '
         '(FOTO_MIN) — sonst liegen Modell und Fotos nicht übereinander, die Hüllenregeln ruhen (huelle_gueltig). tiefe_gesehen: mindestens '
         'zwei Ansichten ≥ 30° auseinander (TIEFE_MIN, auf 180° gefaltet) — vorne und hinten allein sehen denselben Umriss. Anlass: '
         'IterationKoerper glaubte 40 Runden lang einer Messung, bei der nur 37 % der Körperpunkte im Umriss lagen; und ein Zelt-Shirt '
         '(Hülle 70–166 mm über dem Netz) im Testauftrag 2026.10.01.12.38.09, nur vorne/hinten. Ohne befund.messguete (ältere Befunde) '
         'gibt erlaubt() True. Quelle: Docstring Messpruefung (01.10.2026).'),

        ('Luft zwischen Stoff und Haut',
         'Der Abstand eines Stücks zur Körperfläche der Runde (+ außen, − in der Haut) — das Maß gegen das Durchschimmern.',
         'python',
         '\n'.join((
             'from iterationen2d3d.hautabstand import Hautabstand',
             'haut = Hautabstand.aus_teilen(teile)          # None ohne Körperteil mit Dreiecken',
             'haut.signiert(punkte)                         # (N,) in m: + außerhalb der Körperfläche, − darin',
             'haut.messen(punkte, befundmessung.zellen)     # → {haut_zellen, haut_min_mm, haut_innen}',
         )),
         [(P + 'hautabstand.py', 'Hautabstand'), (P + 'befundmessung.py', 'Befundmessung')],
         'Anlass: Edgar „Bei der Animation soll die Haut nicht durch die Kleider schimmern“ (30.09.2026). Gemessen wird in der A-Pose; das '
         'Durchschimmern in der Bewegung (Film) ist damit NICHT gemessen, nur die Luft, die es dafür braucht (Docstring). '
         'IterationKleider.morphe hält je Zelle mindestens HAUT_MIN_MM = 3 mm. Das ist ein Messen des Modells gegen sich selbst, nicht '
         'gegen das Foto; die Zeile steht hier, weil das Ergebnis im Befund liegt.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('Begutachtungsrunde', 'ruft', 'Begutachtungsbefund', 'masken(), render_dazu(), befund(teile)'),
        ('Begutachtungsrunde', 'ruft', 'Messpruefung', 'pruefen(ansichten, hoehe, koerper): befund.messguete'),
        ('Begutachtungsrunde', 'ruft', 'Gesichtsmasse', 'eintragen(befund, teile, referenzen, aus)'),
        ('Begutachtungsrunde', 'ruft', 'Haarabgleich', 'eintragen(befund, teile, referenzen, hoehe, aus)'),
        ('Begutachtungsbefund', 'ruft', 'Befundmessung', 'Befundmessung(proben, normalen, sicht, labels); befund(teile, ansichten, formansichten)'),
        ('Begutachtungsbefund', 'ruft', 'Teilmasken', 'messen(anzahl, kennbild): Kennfarben → Masken je Teil'),
        ('Begutachtungsbefund', 'ruft', 'Genesishaarrender', 'bild_teile(kennung=True): das Kennfarbenbild'),
        ('Begutachtungsbefund', 'ruft', 'Iterationsbild', 'aus_render(pfad): das Kennbild lesen'),
        ('Befundmessung', 'ruft', 'Netzmengen', 'menge(art): Proben je Teilart'),
        ('Befundmessung', 'ruft', 'Bandbreite', 'messen(): koerper_huelle'),
        ('Befundmessung', 'ruft', 'Hautabstand', 'aus_teilen(teile), messen(punkte, zellen)'),
        ('Befundmessung', 'ruft', 'Sichtkoerper', 'rand(start, richtung): huelle_mm je Band'),
        ('Messpruefung', 'ruft', 'Sichtkoerper', 'Sichtkoerper(ansichten, hoehe, koerper).ist_innen(): Selbsttest'),
        ('Gesichtsmasse', 'ruft', 'Gesichtsvorrat', 'schluessel(), holen(), ablegen()'),
        ('Gesichtsmasse', 'ruft', 'Fotolandmarken', 'holen(pfade): Landmarken auf Foto und Kopf-Render'),
        ('Gesichtsmasse', 'ruft', 'Genesishaarrender', 'bild_kopf(): der Kopf-Render je Saat'),
        ('Haarabgleich', 'ruft', 'Pruefbilder', 'kopfausschnitt(): der Foto-Kopf im Ausschnitt des Renders'),
        ('Haarabgleich', 'ruft', 'Genesishaarrender', 'bild_kopf(kennung=True): Kennfarben im selben Ausschnitt'),
    ]

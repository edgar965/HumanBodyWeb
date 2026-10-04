# -*- coding: utf-8 -*-
"""Werkzeughaltung — Gruppe „Haltung, A-Pose, Rig und Posen“ des Reiters „Tools“ der Seite Hilfe → Architektur → 2D3D (03.10.2026).

Schema: `Architektur2d3dwerkzeuge`. Gelesen am 03.10.2026: `ModellKoerperMixin`, `ModellMitKleidern`, `G9haltungshaut`, `Haltungsschaetzung`, `Haltungsfotos`,
`G9skelett`, `G9figurrigglb`, `G9posen`, `G9gelenkkorrekturen`, die Endpunkte `Skelettdaten`, `G9garderobeapi.posen`, `G9felderapi`.
"""

__all__ = ['Werkzeughaltung']


class Werkzeughaltung:
    G = 'Genesis9/'
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'
    P = '2d3DIterationen/iterationen2d3d/'

    KENNUNG = 'haltung'
    TITEL = 'Haltung, A-Pose, Rig und Posen'
    EINLEITUNG = (
        'Genesis 9 wird in der A-Pose gebaut, gezeigt und exportiert (Edgar, 30.09.2026); die Haltung der Fotos wirkt nur in Render, Note, Befund und '
        'Fotoprojektion. Reihenfolge: 1. die Haltung der Fotos messen (Gruppe „Bildvergleich: Fotos und Blickwinkel“: Haltungsfotos, Haltungsschaetzung), '
        '2. m.haltung für beide Arme, m.haltung_gelenk für Ellbogen und Beine, 3. die Runde häutet Körper, Kleider und Haar mit G9haltungshaut in diese '
        'Haltung. Das Rig (Skelett mit 138 Knochen) liefert GET /api/character/genesis9-skeleton/.'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Arme senken (Haltung)',
         'Senkt beide Oberarme aus der A-Pose um so viele Grad — nur für Render, Note, Befund und Fotoprojektion.',
         'rezept',
         'm.haltung(arme_grad=35.0)',
         [(G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'modellrezept.py', 'G9rezept')],
         'Signatur haltung(arme_grad=35.0). Wertebereich 0…43 Grad (ARME_HOECHSTENS): in der A-Pose stehen die Oberarme 43° zur Senkrechten; bei 55° stand die '
         'Hand bei x 0,08 m im Rumpf (Hüfte 0,18 m), gemessen 30.09.2026 am Bauplan der Grundfigur. Die Automatik schreibt m.haltung(42,8 − Oberarmwinkel der '
         'Fotos, gemessen von Haltungsschaetzung.schaetzen: seitlich, beuge, beine) mit 1° Toleranz (IterationModell, seit 01.10.2026); ohne Fotolandmarken bleibt es die A-Pose. An Edgars '
         'Fotos (.51, 01.10.2026): vorn 12,7° / 15,9° seitlich, Ellbogen 23° / 21°. Prüf-KI: verboten.'),
        ('Einzelnes Gelenk drehen',
         'Dreht ein Gelenk der Haltung (Ellbogen, Oberschenkel, Kopf …) um eine Achse — ebenfalls nur für Render, Note und Befund.',
         'rezept',
         "m.haltung_gelenk('r_forearm', 'y', 20.0)\nm.haltung_gelenk('l_thigh', 'z', 6.0)",
         [(G + 'modellkoerper.py', 'ModellKoerperMixin'), (G + 'modellmitkleidern.py', 'ModellMitKleidern'), (G + 'modellrezept.py', 'G9rezept')],
         'Signatur haltung_gelenk(knochen, kanal, grad). knochen aus ModellKoerperMixin.GELENKE (l_forearm, r_forearm, l_upperarm, r_upperarm, head, neck1, '
         'l_thigh, r_thigh, l_shin, r_shin, spine2, pelvis), kanal x | y | z, grad −90…90 (Daz-Kanal rotation/<kanal>). Gemessen 01.10.2026 '
         '(IterationModell): r_forearm rotation/y +g beugt den Ellbogen nach vorn, links gilt −g; l_thigh rotation/z +g spreizt das linke Bein um g°, rechts −g. '
         'Die A-Pose der Grundfigur hat Ellbogen 13,6° und Beine 4,1° je Bein (Probe haltung_probe.py / bein_probe.py). Die Arme am besten mit haltung(). '
         'Prüf-KI: verboten.'),
        ('In die Haltung häuten',
         'Häutet Körper, Kleider und Haar einer Runde von der A-Pose in die Haltung der Fotos — für Render, Note, Befund und Fotoprojektion.',
         'python',
         'from Genesis9.haltungshaut import G9haltungshaut\n'
         'G9haltungshaut(stellung, drehung, boden).posieren(teile)   # flache Kopien mit neuen punkte, normalen, kurven',
         [(G + 'haltungshaut.py', 'G9haltungshaut'), (G + 'formung.py', 'G9formung'), (G + 'knochenmatrizen.py', 'G9knochenmatrizen')],
         'Je Teil mit seiner Haut, lineare Hautmischung D_b = M_b(Stellung + Drehung) · M_b(Stellung)⁻¹ (G9knochenmatrizen); Knochen ohne Matrix (eigene Knochen '
         'eines Stücks) bleiben stehen. Gemessen 01.10.2026 (ortsmorphe.md): gehäutet gegen gebacken 0,00 mm; Umriss-IoU an .51 vorn 0,587 → 0,746, hinten '
         '0,566 → 0,619, Seite 0,782 → 0,820. Die Runde ruft die Klasse selbst; von Hand nur zum Prüfen. Ohne drehung ist posieren die Identität.'),
        ('Skelett abfragen',
         'Liefert das Genesis-9-Skelett der Grundstellung (Knochen, Eltern, Kopf, Schwanz, Lage) — dieselbe Kette, gegen die der Retarget mit target=genesis9 rechnet.',
         'api',
         'GET /api/character/genesis9-skeleton/\n'
         '# Python: from Genesis9.formung import G9formung; G9formung(stellung).skelett().bauen()   # {name, knochen: [{name, eltern, kopf, schwanz, pos, quat, ende}]}',
         [(A + 'skelettdaten.py', 'Skelettdaten'), (G + 'formung.py', 'G9formung'), (G + 'skelett.py', 'G9skelett')],
         'Meter, Y oben, Füße am Boden; ohne Daz-Bibliothek 404 mit Klartext. Daz-Namen (hip, pelvis, l_upperarm, neck1, head …), nicht Rigify-DEF. Die Figur hat '
         '138 Knochen (genesis9-inhalte.md); ein Zopfhaar bringt eigene Knochen, der Mund die Zunge (tongue01..05): das Standmodell trägt 143 Knochen '
         '(engine2d3dkleider.md, 01.10.2026). Die Gelenke wandern mit den Reglern (G9formung(stellung).skelett()); die Knochenskalierung der Posenformeln '
         '(Proportion Height, Head Size, Legs Length) erreicht alle Knochen. Keine Retarget-Eigenbauten: Edgar, 08.09.2026 „wir haben so viele Stunden '
         'und Tage mit Retarget verbracht, lass das“ (CLAUDE.md).'),
        ('Figur mit Rig als GLB',
         'Schreibt eine Reglerstellung als GLB mit Skelett und Hautbindung — für Blender, Film und Export.',
         'python',
         'from Genesis9.figurrigglb import G9figurrigglb\n'
         'G9figurrigglb(stellung, kacheln={1001: pfad}, name="Figur").schreiben(pfad)   # → {datei, bytes, punkte, dreiecke, knochen, knochen_ohne_gelenk, kacheln_eigen}',
         [(G + 'figurrigglb.py', 'G9figurrigglb'), (G + 'rigglb.py', 'G9rigglb'), (G + 'formung.py', 'G9formung')],
         'Im Lauf ist es der Schritt „grundfigur“ (Engine2d3dKleidergrundfigur → arbeit/grundkoerper.glb, 1,8 s im Auftrag 2026.10.01.20.10.04). Meter, Y oben, '
         'Gesicht nach +Z; Blenders Import dreht nach Z oben. Vier Hautgewichte je Punkt, Kacheln ohne Angabe: Daz-Haut; Endknochen fallen weg. Falle: G9rigglb.skelett '
         'schrieb nur die Verschiebung als Bindematrix, three.js nimmt sie wörtlich — Standmodellglb rechnet das Inverse der vollen Weltlage '
         '(engine2d3dkleider.md, 01.10.2026). Keine GLB je Runde (Edgar, 02.10.2026), nur die der besten Runde am Ende.'),
        ('Pose oder Ausdruck als Preset',
         'Stellt ein Daz-Posen- oder Ausdruckspreset als Standbild: Regler des Presets über den Nutzerreglern, Knochendrehung gebacken.',
         'api',
         'GET /api/character/genesis9-figur/posen/   → {posen, ausdruecke, formen}\n'
         'POST /api/character/genesis9-figur/<name>/netz/   {regler, pose: <Kennung>, ausdruck: <Kennung>}',
         [(A + 'g9garderobe.py', 'G9garderobeapi'), (G + 'posen.py', 'G9posen'), (A + 'g9figur.py', 'G9figur'), (G + 'knochenmatrizen.py', 'G9knochenmatrizen')],
         '156 Posen und 18 Ausdrücke lesen kostet 4 s (G9posen, 18.09.2026), danach Listenablage. Ein Standbild: vor einer BVH-Bewegung die Pose auf „—“ '
         'stellen, sonst rechnet der Retarget gegen eine verdrehte Ruhelage. Der Ausdruck stellt nur Regler (FACS), die Pose Knochen und Regler '
         '(Posensteuerungen, Korrekturmorphe); formen sind Formpresets mit ihren Reglern. Es gibt keine Rezeptfunktion für Posen (ModellMitKleidern.hilfe, 03.10.2026): '
         'für die Anpassung an Fotos m.haltung und m.haltung_gelenk.'),
        ('Gelenkkorrekturen (JCMs)',
         'Korrekturmorphe beim Beugen der Gelenke: Schalter, Graph und Felder — wichtig, sobald die Haltung Beugungen hat.',
         'api',
         'GET /api/character/genesis9-figur/felder/gelenke/?stufen=1   → {stufen, graph, achsen, felder}\n'
         '# Schalter als Regler: body_basejointcorrectives (Vorgabe 1), body_ctrl_FlexionAutoStrength (Vorgabe 0)',
         [(A + 'g9felder.py', 'G9felderapi'), (G + 'gelenkkorrekturen.py', 'G9gelenkkorrekturen'), (G + 'reglerfelder.py', 'G9reglerfelder')],
         '117 Morphe aus Base Correctives und Base Flexions, der Formelgraph kommt direkt aus den .dsf (genesis9-bewegung.md, 18.09.2026); der Browser wendet sie je '
         'Bild an (4 ms bei 32 aktiven). Die ersten 117 JCMs rechnen rund 7 s (Stufe 1), danach liegen sie in der Ablage. In Mesh to 3D rechnet python14 zwischen den '
         'Runden die JCMs der gefundenen Haltung (G9gelenkkorrekturen.werte, Meshfigurgenesis), die Registrierung posiert dann wie Daz. Flexion Automatic Strength 0: '
         'Beugungen aus, wie in Daz. Die Daz-Posen (G9knochenmatrizen) rechneten die Twist-Formeln am 20.09.2026 nicht (offen, genesis9-bewegung.md; danach nicht nachgeprüft).'),
        ('Regel: Das Modell bleibt in der A-Pose',
         'Gebaut, angezeigt und exportiert wird in der A-Pose; die Haltung der Fotos steht nur im Render.',
         'regel',
         '— keine Rezeptzeile: m.haltung(…) und m.haltung_gelenk(…) wirken über G9haltungshaut nur in Render, Note, Befund und Fotoprojektion',
         [(G + 'haltungshaut.py', 'G9haltungshaut'), (P + 'iterationmodell.py', 'IterationModell'), (D + 'begutachtungskritik.py', 'Begutachtungskritik')],
         'Edgar, 30.09.2026: „Das Modell soll in A-Pose angezeigt werden“. Bis 01.10.2026 ging die Haltung in den Bau: die Kleider wurden auf der A-Pose angepasst, '
         'die Ärmel blieben oben und die Arme hingen durch sie hindurch (Runden 4–9), und die Automatik nahm jede Haltung auf 0 zurück. Seither Bau in der A-Pose und '
         'Häutung in die Haltung. Die Prüf-KI darf haltung und haltung_gelenk nicht schreiben (Begutachtungskritik.VERBOTEN).'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('G9rezept', 'ruft', 'ModellMitKleidern', 'anwenden(): haltung(), haltung_gelenk() je Zeile'),
        ('ModellMitKleidern', 'erbt', 'ModellKoerperMixin', 'haltung_gelenk() und GELENKE stehen im Mixin; haltung() und drehung() in der Klasse selbst'),
        ('G9haltungshaut', 'ruft', 'G9formung', 'aus_abfrage(stellung, drehung).matrizen(): Ruhe- und Posenmatrizen je Knochen'),
        ('G9formung', 'ruft', 'G9knochenmatrizen', 'matrizen(): G9knochenmatrizen(posen, knochen, drehung=…)'),
        ('G9formung', 'ruft', 'G9skelett', 'skelett(): G9skelett(knochen, boden, matrizen)'),
        ('Skelettdaten', 'ruft', 'G9formung', 'genesis9skelett(): G9formung({}).skelett().bauen()'),
        ('G9figurrigglb', 'ruft', 'G9formung', 'punkte(), boden(), skelett().kette().bauplan(): Netz und Knochen der Stellung'),
        ('G9figurrigglb', 'ruft', 'G9rigglb', 'skelett(knochen), netz_mit_haut(…), schreiben(pfad): glTF mit Skin'),
        ('G9garderobeapi', 'ruft', 'G9posen', "liste('pose'), liste('ausdruck'), liste('form')"),
        ('G9figur', 'ruft', 'G9posen', 'werte(kennung): Knochendrehung und Regler des Presets'),
        ('G9felderapi', 'ruft', 'G9gelenkkorrekturen', 'graph(): Kanäle, Morphe, Knochen der Gelenkkorrekturen'),
        ('G9felderapi', 'ruft', 'G9reglerfelder', "holen('gelenke', graph['morphe'], stufen): Deltafelder je Stufe"),
    ]

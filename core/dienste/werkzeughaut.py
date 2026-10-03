# -*- coding: utf-8 -*-
"""Werkzeughaut — Gruppe „Haut, Hautfarbe und Textur aus Netz und Fotos“ des Reiters „Tools“ der Seite Hilfe → Architektur → 2D3D (03.10.2026).

Schema: `Architektur2d3dwerkzeuge`. Gelesen am 03.10.2026: `G9hautpresets`, `G9hautwahl`, `G9schminke`, `G9hautmischungapi`, `Meshfigurende`, `G9texturbacken`,
`Koerperfotoprojektion`, `Koerpertextur`, `Modelltexturen`, `Bildmodellfototextur`. Kleider- und Haarfarbe, Decal und Falten stehen in den Gruppen der Kleider.
"""

__all__ = ['Werkzeughaut']


class Werkzeughaut:
    G = 'Genesis9/'
    D = 'HumanBodyWeb/core/dienste/'
    A = 'HumanBodyWeb/core/api/'
    I = '2d3DIterationen/iterationen2d3d/'
    W = 'VideoToBVH/wrappers/'

    KENNUNG = 'haut'
    TITEL = 'Haut, Hautfarbe und Textur aus Netz und Fotos'
    EINLEITUNG = (
        'Die Haut von Genesis 9 sind fünf UDIM-Kacheln (1001–1005, alle Figuren teilen die UV). Es gibt drei Wege zu einer Hautfarbe, die zur Person passt: '
        '1. einen Daz-Hautsatz wählen (Albedo, Normalen, Rauheit), 2. die Farbe des Netzes aus „Mesh to 3D“ in die Kacheln backen (Schritt textur), '
        '3. in der Runde die Haut aus den Fotos projizieren (Koerperfotoprojektion, einmal je Körper). Schminke und Hautsatzmischung liegen im Shader und '
        'kommen nie in die Albedo.'
    )
    # (Werkzeug, Wofür, Art, Aufruf, Klassen, Hinweis)
    ZEILEN = [
        ('Hautsatz wählen',
         'Wählt den Daz-Hautsatz (Albedo, Normalen, Rauheit je Körpergruppe) der Figur.',
         'api',
         'GET /api/character/genesis9-figur/regler/   → haut [{id, name, geschlecht, vorschau}]\n'
         "POST /api/character/genesis9-figur/<name>/netz/   {haut: 'G9 Feminine Skin 02 MAT'}   # oder '<charakter>:<slug>'\n"
         '# Python: from Genesis9.hautpresets import G9hautpresets; G9hautpresets.hautpresets(); G9hautpresets.haut(preset)',
         [(A + 'g9figur.py', 'G9figur'), (G + 'hautpresets.py', 'G9hautpresets'), (G + 'hautwahl.py', 'G9hautwahl')],
         'Acht Hautsätze der Starter Essentials (G9 Feminine | Masculine Skin 0N MAT) plus die Hautsätze der Charakterordner (<charakter>:<slug>; G9hautwahl nach '
         'BELEGTEN Gruppen, nicht nach Ordnernamen). Ohne Angabe im Rumpf gilt die Haut des Katalogeintrags, bei einem gespeicherten Modell die gespeicherte. Toon-Häute '
         '(hautton) haben kein Albedo. Es gibt keine Rezeptfunktion für die Haut des Körpers (ModellMitKleidern.hilfe, 03.10.2026): die Hautfarbe der Runden kommt '
         'aus den gebackenen Kacheln des Körperschritts und der Fotoprojektion.'),
        ('Hautsatz-Mischung in Prozent',
         'Legt weitere Hautsätze mit Gewicht über die gewählte Haut (z. B. Ursulas HD-Haut auf Kin) — im Browser, im Shader.',
         'api',
         'GET /api/character/genesis9-figur/haut/<preset>/bilder/   → {preset, gruppen: {Head: {albedo, normalen, rauheit, normalenachse?}, Body: …}}\n'
         '# Modellfeld: hautmischung = {<Hautsatz>: prozent}',
         [(A + 'g9hautmischung.py', 'G9hautmischungapi'), (G + 'hautpresets.py', 'G9hautpresets'), (G + 'browserbilder.py', 'G9browserbilder')],
         'Der Körper wird beim Ziehen NICHT neu gebaut (ein Uniform-Update): Albedo hinter map_fragment vor der Schminke, Rauheit aus dem G-Kanal, Normalen im '
         'Bildraum. Höchstens 3 Schichten (4K je Kachel und Schicht auf der GPU); nur Albedo, Normalen, Rauheit — die 8K-Detailnormalen bleiben draußen. Sichtprobe '
         '21.09.2026: Ursula → 100 % Kin heller mit Kins Lippen (genesis9.md). Reine Browser-Funktion; ob die Mischung in Render und Note der Runden ankommt, ist nicht geprüft.'),
        ('Schminke, Wimpern, Nagellack, Hautglanz',
         'Wählt Presets, die Kanäle oder Ebenen der Haut ändern: Grundierung, Rouge, Lidschatten, Eyeliner, Lippen, Lipgloss, Bemalung, Wimpern, Nagellack, Mund, Kopf, Hautglanz, Hautton, Augenschatten.',
         'api',
         'GET /api/character/genesis9-figur/regler/   → praesets (Kategorie, id, name)\n'
         "POST /api/character/genesis9-figur/<name>/netz/   {praesets: {rouge: <id>, lippen: <id>, wimpern: <id>}}",
         [(A + 'g9figur.py', 'G9figur'), (G + 'schminke.py', 'G9schminke'), (G + 'hautwahl.py', 'G9hautwahl'), (G + 'ebenen.py', 'G9ebenen'),
          (G + 'glanz.py', 'G9glanz')],
         'Je Kategorie EIN Preset. Schminke sind Ebenen (Farbe, Maske, Deckkraft, Rauheit; Blendmodi wie Daz, G9makeupstapel), im Shader gemischt und nie in die Albedo '
         'gemalt — so passt Ursulas Rouge auf jede Haut. Rechnet Pillow, 4096², 0,8–1,8 s je Komposition (ablage/schminke/, genesis9-inhalte.md, 18.09.2026). Lipgloss und '
         'Metall gehen als RGB-Glanzbild (G9glanz: Klarlack, Rauheit, Metall). Die Apply-Skripte des Daz-Makeup-Systems sind verschlüsselt, was sie laden liegt lesbar daneben. '
         'Nicht für die Anpassung an Fotos gedacht: die Pipeline setzt keine Schminke.'),
        ('Haut aus dem Netz backen',
         'Backt die Farbe des Netzes (Texelfarben der fünf Kacheln) über die auf den Hautton getönte Daz-Albedo — Schritt textur von Mesh to 3D.',
         'python',
         'Meshfigurende(lauf).textur()   # Schritt textur; Start: POST /api/meshfigur/<id>/starten/ {ab: "textur"}\n'
         '# Optionen: textur = mesh | hautton | aus (Vorgabe mesh), kopfhaut = haar | haut (Vorgabe haar)',
         [(D + 'meshfigurende.py', 'Meshfigurende'), (G + 'texturbacken.py', 'G9texturbacken'), (D + 'meshfigurtexelpruefung.py', 'Meshfigurtexelpruefung'),
          (W + 'meshfigur_hautmodell.py', 'Meshfigurhautmodell')],
         'Der Runner liefert je Texel die Farbe des Netzes (meshtextur.npz); G9texturbacken legt sie über die Daz-Albedo, getönt auf den Hautton des Netzes (Faktor je Kanal '
         '0,25…2,5), Kachel 2048², Rand 12 px nach außen. Am Körper zählt nur Hautfarbe (Hautmodell der kahlen Stellen: Gesicht, Hände, Unterarme, Unterschenkel — der Ton von '
         'Shirt und Shorts zählt nicht); Kopfhaar und Gesichtskern nehmen jede Farbe. Die Texelprüfung verwirft entsättigt-dunkle Treffer (Spaltschatten) und Ausreißer gegen ein '
         '96-px-Umgebungsfeld (heller × 1,2, dunkler × 0,6) und füllt alle Löcher mit dem örtlichen Hautton. Zeit: Damira 151 s (27.09.2026), Auftrag 2026.10.01.20.10.04 210,1 s '
         '(architektur2d3dmessung.KOERPER). Grenze: Flecken zuerst im Netz suchen — Hunyuan füllt ungesehene Stellen (Kinnunterseite, Rumpfseiten) mit einfarbigen Zellen, und '
         'die Textur der Beine von hinten ist TRELLISʼ eigene Malerei, verwaschen und fleckig (Edgar, 02.10.2026); deshalb die Fotohaut in der nächsten Zeile.'),
        ('Haut aus den Fotos projizieren',
         'Holt die Hautfarbe des Körpers in der Runde aus den Fotos statt aus dem Netz — einmal je Körper, über die gebackenen Kacheln gelegt.',
         'python',
         'Koerperfotoprojektion(job, ablage).bauen(teile, referenzen, render, aus)   # in der Runde: Begutachtungswerkzeug.fototextur(…)\n'
         'Koerperfotoprojektion.warm(rgb)   # True = Hautfarbe (R > G > B, R − B > 0,04)',
         [(D + 'koerperfotoprojektion.py', 'Koerperfotoprojektion'), (D + 'begutachtungswerkzeug.py', 'Begutachtungswerkzeug'), (G + 'uvraster.py', 'G9uvraster'),
          (I + 'fotoprojektion.py', 'Fotoprojektion')],
         'Schritte: je Kachel die Texel des Körpers rastern (RASTER 1024), Farbe aus den Fotos (Gewicht Normale · Blick⁴, Deckung ab Kosinus 0,25 bis 0,6), nur warme Fotofarbe '
         'übernehmen (Shirt, Shorts, Socke bleiben bei der gebackenen Farbe), Deckung glätten (WEICH 3), Lücken füllen. Braucht die gebackenen Kacheln (ergebnis.fototextur.kacheln, '
         'noetig() sonst falsch); Fotos mit anderer Kleidung zählen nur für die Form. Einmal je Körper und Fassung (fototextur.hautfoto.fassung 1); die gebackenen bleiben als '
         'kacheln_netz. Rechnet „Körper“ neu, ersetzt er fototextur ganz. Zeit: nicht getrennt gemessen — die Runden 9–11 und 20–23 zeigen für „Fotoprojektion“ 0,0 s, weil die Haut '
         'schon projiziert war (architektur2d3dmessung, 02.10.2026). Scheitert die Projektion, rechnet die Runde mit der gebackenen Haut weiter (Eintrag im Log). Edgar, 02.10.2026: '
         '„Die ganzen iterativen Anpassungen sollen sich an den Fotos als Vorlage richten, NICHT mehr an dem Trellis Modell“. Grenze: nur Hautfarbe (warm) und nur, wo ein Foto '
         'die Texel sieht; sonst bleibt die gebackene Farbe.'),
        ('Kacheln im Körper, im Modell, in der GLB',
         'Gibt dem Körper der Runden die gebackenen Kacheln statt einer Einheitsfarbe und legt sie beim Speichern neben das Modell.',
         'python',
         'Koerpertextur.kacheln(job, ablage)   # {1001: Pfad, …} aus ergebnis.fototextur.kacheln\n'
         'Koerpertextur.teil(punkte, stufe, haut, hautfarbe, kacheln)   # Körperteil mit UV und Textur\n'
         'GET /api/character/genesis9-figur/fototextur/<modell>/<datei>/   # Kachel eines gespeicherten Modells',
         [(D + 'koerpertextur.py', 'Koerpertextur'), (D + 'modelltexturen.py', 'Modelltexturen'), (A + 'g9fototextur.py', 'G9fototextur'), (G + 'figurrigglb.py', 'G9figurrigglb')],
         'Befund 01.10.2026: Kleidermodellbau.koerper gab dem Körper die Festfarbe (0,82 / 0,68 / 0,60) ohne UV — gerendert, benotet und vermessen wurde eine blasse Einheitshaut '
         '(Render 0,77 / 0,63 / 0,56 gegen Foto 0,44 / 0,32 / 0,27). Seither trägt der Körper der Runden die Kacheln. Beim SPEICHERN kopiert Modelltexturen sie nach '
         'data/models/Texturen/<Modell>/<Datei> (Adresse mit ?v=<Stand>); „Auftrag löschen“ lässt die Haut stehen. Szene, Studio und Theatre zeigen die Fotohaut '
         '(Genesis9fototextur: die Kachel ersetzt die Daz-Albedo der Gruppe, Normalen und Rauheit bleiben); GLB, OBJ und DAE tragen sie. G9figurrigglb nimmt kacheln = {1001: Pfad}, '
         'sonst die Daz-Haut.'),
        ('Haut aus Bildern (SMPL-X-Weg)',
         'Stufe 1 tönt die Daz-Haut auf den Hautton der Fotos, Stufe 2 nimmt die Fotofarbe je Texel — der Schritt textur von „Modell aus Bildern“.',
         'api',
         "POST /api/bildmodell/<id>/starten/   {schritte: ['textur']}   # oder ab: 'textur'",
         [(A + 'bildmodell.py', 'Bildmodellendpunkte'), (D + 'bildmodellstart.py', 'Bildmodellstart'), (D + 'bildmodelltextur.py', 'Bildmodelltextur'),
          (D + 'bildmodellfototextur.py', 'Bildmodellfototextur'), (G + 'texturbacken.py', 'G9texturbacken')],
         'Der ältere Weg (19.–21.09.2026), vor „Mesh to 3D“. Stufe 2 projiziert das ANGEPASSTE Genesis-Modell ins Bild (python10 _run_fotofarben.py; Kamera aus gerenderten '
         'Testfallbildern oder aus dem Rig gegen die Landmarken, PnP), Tiefentest, Personenmaske, Sichtwinkel, je Texel der fünf Kacheln die Proben aller Bilder, '
         'Helligkeitsangleichung auf der Überlappung. Ein Nebenbild mit Körperteil färbt nur dieses Teil. Ergebnis ergebnis.fototextur {kacheln, herkunft, karten, je_bild, '
         'deckung, hautton}. Zeit nicht neu gemessen.'),
    ]
    # Klassenmodell: (von, 'ruft', nach, womit)
    BEZIEHUNGEN = [
        ('G9figur', 'ruft', 'G9hautpresets', 'hautpresets(), augen(), haut(preset): Hautsätze, Augen und deren Bilder'),
        ('G9figur', 'ruft', 'G9hautwahl', 'kategorien(): Presets für Wimpern, Nagellack, Mund, Kopf, Hautglanz, Hautton, Augenschatten'),
        ('G9figur', 'ruft', 'G9schminke', 'katalog(): Schminkpresets je Kategorie'),
        ('G9hautmischungapi', 'ruft', 'G9hautpresets', 'haut(preset): Bilder je Körpergruppe'),
        ('G9hautmischungapi', 'ruft', 'G9browserbilder', 'fuer(bilder): tragbare Bilder (Grenze 20 MB)'),
        ('G9schminke', 'ruft', 'G9ebenen', 'Ebenen aus LIE-Stapeln und Makeup-Kanälen'),
        ('G9schminke', 'ruft', 'G9glanz', 'Glanzbild für Lipgloss und Metall'),
        ('Meshfigurende', 'ruft', 'G9texturbacken', 'Netzfarbe über die getönte Daz-Albedo backen'),
        ('Meshfigurende', 'ruft', 'Meshfigurtexelpruefung', 'Texel säubern, bevor gebacken wird'),
        ('Begutachtungswerkzeug', 'ruft', 'Koerperfotoprojektion', 'fototextur(): bauen(teile, farbig, render, aus)'),
        ('Koerperfotoprojektion', 'ruft', 'G9uvraster', 'Texel des Körpers je Kachel rastern'),
        ('Koerperfotoprojektion', 'ruft', 'Fotoprojektion', '_projektion(): Kennfarbenrender → Farbe je Texel'),
        ('Bildmodellendpunkte', 'ruft', 'Bildmodellstart', 'starten(job, rumpf): Arbeitsprozess ab einem Schritt'),
        ('Bildmodellfototextur', 'ruft', 'G9texturbacken', 'Texelfarben der Fotos über die Albedo backen'),
        ('Bildmodellfototextur', 'ruft', 'Bildmodelltextur', 'Stufe 1: Hautton als Grundlage'),
        ('G9fototextur', 'ruft', 'Modelltexturen', 'datei(modell, datei) und art(pfad): Kachel eines gespeicherten Modells ausliefern'),
    ]

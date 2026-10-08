# -*- coding: utf-8 -*-
"""Architektur2d3dfaktennetz — technische Fakten zum Netz aus den Fotos: TRELLIS.2, Pixal3D, Vorverarbeitung (Hilfe → Architektur → 2D3D, 06.10.2026).

Edgar, 06.10.2026: „mach auch möglichst viele technische Details im unteren Bereich hinein, zu den Trellis Parametern usw. damit wir später nicht von neuem anfangen und Fehler nicht
wiederholen". Jeder Eintrag steht so in der Regeldatei, die als Quelle genannt ist (gelesen 06.10.2026) — Zahlen wörtlich, Vermutungen als Vermutung. Die Einstellwerte selbst stehen
nicht hier, sondern kommen beim Aufruf der Seite aus den Katalogen des Codes (`Architektur2d3doptionen`); hier steht, was man über sie WEISS.

Eintrag: `(bereich, art, thema, befund, quelle)`; `art`: parameter | messung | falle | entscheidung.
"""

__all__ = ['Architektur2d3dfaktennetz']


class Architektur2d3dfaktennetz:
    T2 = 'mesh-trellis2.md'
    PX = 'mesh-pixal-mehrbild.md'
    VB = 'mesh-vorverarbeitung.md'
    EINTRAEGE = [
        # ------------------------------------------------------------------ TRELLIS.2
        ('TRELLIS.2', 'parameter', 'Welches TRELLIS läuft',
         'TRELLIS.2 (microsoft/TRELLIS.2-4B, 14 GB, form_trellis2). Von v1 (TRELLIS-image-large, 141 MB) liegt nur der Sparse-Structure-Decoder in hf_home; die pipeline.json von TRELLIS.2 lädt ihn mit. '
         'Der erste Treffer einer Suche, trellis-community/TRELLIS, ist v1 (Guidance 7,5 / 3,0, Simplify 0,95, Textur 512–2048) und passt nicht zu unserem Modell.',
         T2 + ', „Welches TRELLIS läuft"'),
        ('TRELLIS.2', 'parameter', 'Das Interface von v2 (Hugging-Face-Space microsoft/TRELLIS.2)',
         'Resolution 512 / 1024 / 1536 (→ pipeline_type 512 / 1024_cascade / 1536_cascade), Seed, Randomize Seed (im Space an), Decimation Target 100.000–500.000 (im Space 300.000), '
         'Texture Size 1024–4096 (im Space 2048). Die GLB-Extraktion des Space ruft to_glb mit remesh=True, remesh_band=1, remesh_project=0 — bei uns netzaufbau, aufbau_band, aufbau_anziehen.',
         T2 + ', „Welches TRELLIS läuft"'),
        ('TRELLIS.2', 'parameter', 'Die zwölf Sampler-Regler',
         'Je Stage Guidance Strength (1–10) / Guidance Rescale (0–1) / Sampling Steps (1–50) / Rescale T (1–6). Stage 1 Sparse Structure 7,5 / 0,7 / 12 / 5,0; Stage 2 Shape 7,5 / 0,5 / 12 / 3,0; '
         'Stage 3 Material 1,0 / 0,0 / 12 / 3,0. Bitgleich die pipeline.json von TRELLIS.2-4B (Test test_die_vorgaben_sind_die_der_pipeline_json_von_trellis2). Guidance Rescale 0,0 ist ein Wert '
         '(is not None). Alte Aufträge der Seite „Mesh" ohne ss_* behalten das Paar schritte/fuehrung für Stage 1+2.',
         T2 + ', „Welches TRELLIS läuft" und „Wo es steht"'),
        ('TRELLIS.2', 'entscheidung', 'Unsere Vorgaben weichen bewusst vom Space ab',
         'Decimation 300.000 im Space gegen 100.000 bei uns (500.000 baute Eiszapfen: 102.448 von 461.656 Flächen gegen 8 von 96.598, 01.10.2026); Texture Size 2048 gegen 4096 (1536³ mit 2048 gab 9,3 % '
         'Lücken, 27.09.2026); Resolution 1024 gegen 1536; Randomize Seed an gegen aus (vergleichbare Läufe). Seed 42.',
         T2 + ', „Unterschiede zwischen Space-Vorgaben und unseren"'),
        ('TRELLIS.2', 'entscheidung', 'Eine Tuning-Anleitung, Satz für Satz gegen die Quellen',
         '„SLAT Guidance 3,5–4,5" gilt nur für v1 (TRELLIS.2 hat Shape 7,5 und Material 1,0, der Rat lässt sich nicht übertragen). „Schritte 12 → 20–25 glättet enorm": 12 stimmt für beide Fassungen, '
         '„enorm" ist unbelegt; die Rechenzeit der Sampler wächst linear mit den Schritten, ihr Anteil an den rund 563 s des Schritts „Netz" ist NICHT gemessen. „SS Guidance 7,0–8,5 bei Verformung" '
         'ist eine Vermutung um den Standard, nirgends gemessen. Regler da, Vorgaben unverändert.',
         T2 + ', „Die eingefügte Anleitung"'),
        ('TRELLIS.2', 'messung', 'Mehrbild mit TRELLIS.2 verdirbt die Haltung',
         'TRELLIS.2 hat im Original keinen Mehrbild-Modus; der Community-Fork opsiclear-admin/Trellis.2.multiview ist unser Klon plus drei Änderungen und als Trellismehrbild eingebaut (Option mehrbild '
         'aus | stochastic | multidiffusion, Vorgabe aus). Gelaufen 02.10.2026 (Seed 42, hoch 1536³, nur vorne + hinten, weil die Fotoprüfung das Seitenfoto ausließ): D1 aus 699 s, GPU-Spitze 9.806 MiB, '
         'IoU vorn/hinten 0,874/0,684, aufrecht; D2 stochastic + multidiffusion 715 s, 0,562/0,720, nach vorn gebeugt; D3 multidiffusion + multidiffusion 1.109 s, 0,560/0,705, nach vorn gebeugt. '
         'Mit zwei gegenüberliegenden Ansichten verdirbt Mehrbild die Körperhaltung — die Vorgabe „aus" bleibt. Offen: ob drei Fotos mit einheitlicher Kleidung und Pose es retten.',
         T2 + ', „Die eingefügte Anleitung"'),
        ('TRELLIS.2', 'messung', 'Dauer des Schritts „netz"',
         'Gemessen an 8 Aufträgen (alle TRELLIS.2): 428–753 s je nach Auflösung, Textur und Flächenzahl; Lauf …14.10.22 vom 06.10.2026 (hoch, Textur ki, 100.000 Flächen): 384,3 s. '
         'Auflösung „schnell" 466,9 s, „hoch" mit fotos_ki 428,3 s — die Auflösung kostet praktisch keine Zeit.',
         'Workflowzeiten (Datenbank, ergebnis.dauer); engine2d3dkleider.md'),
        ('TRELLIS.2', 'falle', 'Das Formular „Netz" wurde nie gespeichert',
         'Die Formulare „Netz" und „Körper" der Auftragsseite wurden nie gespeichert (Engine2d3dKleidereinstellungen.GRUPPEN kannte nur figur/iterationen/film). Gemessen an …14.08.48: Auflösung '
         '„mittel" gewählt, 2 s gewartet, der Server hatte „hoch". Seither stehen alle Gruppen drin; Test test_die_seite_speichert_jede_gruppe hält Python- und JS-Liste gegeneinander.',
         T2 + ', „Ein Fund, der nichts mit TRELLIS zu tun hat"'),
        ('TRELLIS.2', 'entscheidung', 'Nur TRELLIS im Bereich 2D3D Kleider',
         'Edgar, 02.10.2026: „ich brauche NUR trellis in dem Workflow, kein Hunyan". Engine2d3dKleidernurtrellis streicht das Feld „Formmodell", die Textur „malerei" (Hunyuan malt) und die '
         'Auflösung „sehr hoch" (Octree 768 gibt es nur bei Hunyuan). Seit 07.10.2026 ist Hunyuan3D-2.0 / -2mv trotzdem als Wahl „Modell" der Gruppe mesh zurück (Edgar: „mach einen neuen Job in 2d3dKleider '
         'mit der Hunyan Pipeline"); die Bäume des Workflows bleiben bei TRELLIS. Der Kopf-Lauf (Schritt kopf, 07.10.2026) rechnet das Kopfnetz mit Hunyuan3D (Gruppe kopf, Wahl 2mv oder 2.0).',
         T2 + ', „Wo es steht"'),
        # ------------------------------------------------------------------ Pixal3D
        ('Pixal3D', 'parameter', 'Was Pixal3D ist und wie es eingebaut ist',
         'TencentARC/Pixal3D, MIT, SIGGRAPH 2026: TRELLIS.2-Backbone, Rückprojektion der Bildmerkmale in 3D; seit Sep. 2026 echtes Multi-View (eigene _mv-Gewichte, erstes Bild = Frontansicht). Gewichte 46 GB '
         '(Einzelbild ~24 GB, Multi-View ~22 GB; TRELLIS.2-4B 14 GB), MoGe-2 schätzt die Kamera beim Einzelbild. Feld „Modell" der Gruppe mesh (TRELLIS.2 | Pixal3D | Pixal3D Mehrbild); Runner '
         'mesh_pixal3d.form_pixal3d ruft _run_pixal3d.py in python10_pixal; die zwölf Sampler-Regler und mehrbild gelten dort nicht (eigene pipeline.json). Die Qualitätsaussagen der Autoren '
         '(präzisere Kanten, weniger Halluzinationen) sind an unseren Fotos NICHT gemessen.',
         T2 + ', „Pixal3D eingebaut"; ' + PX),
        ('Pixal3D', 'falle', 'Ein stiller Rückfall auf Einzelbild-Gewichte ist ausgeschlossen',
         '_run_pixal3d.mv_nachweis schreibt „Mehrbild-Gewichte: …, 4 von 4 Flow-Modellen mit _mv" und bricht ab, wenn die Klasse nicht Pixal3DMVImageTo3DPipeline ist oder ein Flow-Modell nicht auf _mv endet.',
         PX + ', Abschnitt 1'),
        ('Pixal3D', 'parameter', 'Maßstab und Sichtfeld',
         '_run_pixal3d.quadrat schneidet je Ansicht ein Quadrat von 1,1 × größter Ausdehnung um die Silhouette = 91 % der Höhe, mittig. Option pixal_fov (rad; 0 = MoGe-2 am Vorderfoto, nie an der Seite). '
         'MoGe-2 schätzt vorne 49,6° (Entfernung 1,083), hinten 55,2° (0,957), Seite 58,2° (0,897) — 8,6° Streuung derselben Person; die Autoren-Vorgabe ist 20°. Ob 20° oder 49,6° besser ist, '
         'zeigen die Läufe nicht klar (je ein Lauf). Silhouetten-IoU des Rohnetzes gegen das Vorderquadrat: 0,946 mit der Kamera des Laufs, 0,854 orthografisch eingepasst (so backt Fotobacken).',
         PX + ', Abschnitte 3 und „Ergebnisse der Q-Reihe"'),
        ('Pixal3D', 'entscheidung', 'Seitenrolle: rechts = 270°, links = 90°',
         'Winkeltabelle am Beispielrig der Autoren gelesen (_run_pixal3d.AZIMUT). Gegenprobe mit gleichem Code, gleichen Fotos, Seed 42, nur pixal_seite verschieden, fadenfrei gemessen: Seiten-IoU '
         'Q2 0,906 · G1 0,894 (beide 270°) · Q4 0,684 (90°). Option pixal_seite: angegeben (Vorgabe) | blick | getauscht. Blickrichtung aus den Füßen (32 von 32 Silhouetten richtig; ein echtes Foto, '
         'eine Person — Grenzen).',
         PX + ', Abschnitt 4'),
        ('Pixal3D', 'falle', 'Fäden in Tiefenrichtung („Speer")',
         'Das Zusätzliche in G1 war keine zweite Figur: ein Teil mit 533 Flächen und konstantem x/y, das nur in z von −0,499 bis −0,222 läuft; das Ende liegt an der Würfelkante z = ±0,5. Sie treten in jedem '
         'Speichermodus auf und fehlen in jedem (neun Läufe). Bei 300.000 Flächen baut to_glb sporadisch Fäden: P2 44.112 von 292.945 Flächen (15 %) gegen 216 und 217 bei gleichem Rohnetz. '
         'Filter mesh_pixalfaeden.Pixalfaeden (zwei Stufen, in z); Q1 189 von 99.036 Flächen (0,19 %), sonst 0,01–0,06 %. Nicht gelöst: G1 behält Reste; ein x-Gebilde in Q5 steht schon im Rohnetz. '
         'Eine IoU, die Fäden mitzählt, ist verfälscht: das Maß koerper lässt Spalten unter 6 % der Umrisshöhe weg (0,894 statt 0,021).',
         PX + ', „Fäden in Tiefenrichtung"'),
        ('Pixal3D', 'messung', 'Grafikspeicher und Zeit im GPU-Modus',
         'pixal_gpu (Option pixal_speicher, auto): Modelle laden 4–5 s statt 146 s, Pixal-Prozess 130 s statt 301–305 s, Job 254–261 s statt 444 s, Finalisieren 15 s statt ~43 s, Spitze 29.969 MiB belegt auf '
         'einer Karte mit 31,9 GB. Eng: die größte Stufe (get_proj_cond_shape) 29,3 GB — bei mehr als etwa 2 GB fremder Last reicht es nicht (dann sparsam). Der Modus „alles zugleich" brauchte '
         '43.210 MiB auf der 32-GB-Karte und lagerte aus (Textur: 3 s in P2, 11 min in P3; die Ursache der Schwankung ist Schlussfolgerung, nicht belegt).',
         PX + ', „Grafikspeicher" und „Alles auf der GPU"'),
        ('Pixal3D', 'messung', 'Auflösung: Texeldichte, Textur 8192, 300.000 Flächen',
         'Bei Textur 4096 liegen 0,67 mm auf einem Texel (die Dreiecke belegen nur 48–53 % des Atlas); das Kopffoto trägt 0,42 mm je Pixel — die 4096er Textur ist 1,6-mal gröber. Bei 8192: 0,33 mm. '
         'Das Netz: 93.000 Flächen auf 3,7 m² = 9,5 mm Kantenlänge, obwohl das Voxelgitter 1,2 mm fein ist. Gewählt für die Neuberechnung: 8192 + 300.000 Flächen (Job 668 s statt 318 s, Textur 33 MB); '
         'Katalogvorgaben unverändert (texturgroesse 4096, flaechen 100.000). Das Foto geht nicht verkleinert ein (vorbereitet/<rolle>.png, 5.505–6.193 px).',
         PX + ', „Auflösung: Texeldichte"'),
        ('Pixal3D', 'messung', 'Gesichtspixel',
         'Im Eingang des Formmodells ist der Kopf 124 px hoch, das Gesicht (Haaransatz–Kinn) ≈ 89 px = 5,6 DINO-Patches à 16 px; ein Kopfausschnitt (Quadrat 1,5 × Kopfhöhe) gäbe 683 px. K1 (Kopf allein): '
         'Vorderansicht deutlich besser, Profil und Hinterkopf schlechter; das Kopf-Netz in den Körper zu setzen ist NICHT gebaut.',
         PX + ', Abschnitt 5'),
        ('Fotoprüfung', 'falle', 'Die Fotoprüfung las die Hand, nicht die Kleidung',
         'Das Seitenfoto fiel aus jedem Mehrbildlauf (Bandabstand 2,20 und 1,73 gegen Grenze 1,0): das Hüftband des Seitenfotos hatte die Medianfarbe [0,59; 0,36; 0,28] = Hautton (die Hand hängt vor der Hüfte), '
         'vorn/hinten [0,32; 0,27; 0,23] (Shorts). Behoben 06.10.2026: Fotopruefung.haut nimmt Hautpixel aus der Bandfarbe (Lab-Farbton 15–75°, Buntheit ≥ 20; gemessen Haut Median 31,6, Shorts ≤ 14, '
         'grauer Rumpf ≤ 10; unter MIN_PIXEL 200 bleibt ein Band ohne Urteil). Neues Urteil 0,85 / 1,23 — nicht ausgelassen, knapp. Gilt nur für neue Läufe des Schritts „netz"; ältere Aufträge '
         'behalten ihr altes Urteil in ergebnis.fotopruefung.',
         PX + ', Abschnitt 2; engine2d3dkleider-iteration0.md'),
        # ------------------------------------------------------------------ Vorverarbeitung
        ('Vorverarbeitung', 'parameter', 'Die Reihenfolge in vorbereitung()',
         'Freistellen (BiRefNet, .float() — die Gewichte liegen in float16) → Maskenkante härten → Strähnen öffnen → Ausrichten (Option ausrichten) → quadratischer Zuschnitt mit bildrand → Lichtausgleich → '
         'Ablage vorbereitet/<name>.png. Jeder Formweg und die Fotoprojektion lesen aus vorbereitet/: wer hier etwas ändert, ändert es für alle.',
         VB + ', „Reihenfolge in vorbereitung()"'),
        ('Vorverarbeitung', 'falle', 'Der Zuschnitt ohne Rand erzeugt die „Eiszapfen"',
         'Freisteller.freistellen legte das Quadrat exakt auf die Bounding Box — die Silhouette berührt alle vier Bildränder, das Modell sieht nie, wo das Haar endet. Option bildrand (%): am Porträt mit 15 % Rand '
         '131 von 133 Kleinteilen entfernt (10,7 %) statt 30 von 31 (1,1 %). Am Ganzkörper reicht es nicht (489.071 → 466.296 Flächen). Gleicher Seed, wechselndes Ergebnis: die Zapfen kommen und gehen '
         'zwischen Läufen. Verworfen: Voxel-Opening (frisst das Gesicht, Radius 1: 46,6 % des Gesichtsfeldes weg) und Dreiecks-Streckung (bei Schwelle 8 fallen 42,7 % der tiefhängenden, aber 7,6 % '
         'der Gesichtsflächen).',
         VB + ', „Der Zuschnitt ohne Rand erzeugt die Eiszapfen"'),
        ('Vorverarbeitung', 'falle', 'Der Rand verschob die Fotoprojektion',
         'Die Projektion setzte die Netzspanne mit der Bildkante gleich; mit 15 % Rand füllt das Motiv nur 77 % der Bildhöhe, alles fiel um den Faktor 1,27 zu weit nach außen. mesh_uvraster.bildpassung passt '
         'Maßstab und Mitte an das Motiv an: Kopfoberkante Netz gegen Foto 82 % der Kopfhöhe daneben → 0,0 %, Fototreffer 37,0 % → 74,5 % der belegten Texel. Messfalle: eine IoU zwischen projizierter '
         'Punktwolke und Fotomaske (0,21) misst die Punktdichte, nicht die Passung; tragfähig war die Kopfoberkante in Pixeln.',
         VB + ', „Der Rand verschob die Fotoprojektion"'),
        ('Vorverarbeitung', 'falle', 'Die Achsentabelle war an x gespiegelt (03.10.2026)',
         'mesh_fototextur.ACHSEN war gespiegelt: jedes Foto lag links/rechts vertauscht auf dem Körper, die Uhr vom linken Handgelenk erschien am rechten. Es fiel nie auf, weil das Gesicht über die eigene Kamera '
         'läuft und Silhouettenmaße eine Spiegelung nicht sehen — eine Projektion braucht ein asymmetrisches Merkmal als Gegenprobe (Uhr, Leberfleck, Scheitel). spiegel_pruefen.py: Korrelation '
         'vorher 0,157 gegen 0,777 gespiegelt, danach 0,784 gegen 0,135. Offen: alle Ergebnisse mit fotobacken = an bis 03.10.2026 tragen die gespiegelte Körpertextur; mesh_fusion.ROLLENDREHUNG nicht geprüft.',
         VB + ', „Die Achsentabelle war an x gespiegelt"'),
        ('Vorverarbeitung', 'parameter', 'Licht ausgleichen (Option licht, Vorgabe 100)',
         'Tiefpass-Division nur über die Maske, Faktor auf 0,4–2,5 begrenzt, Sigma bezogen auf die MOTIVgröße (nicht die Bildkante). Die Vorlage war nicht symmetrisch: Helligkeit links 124,3, rechts 100,2. '
         'Sigma 0,03 → Seitenunterschied 1,3 (flach wie ein Ausweisfoto), 0,08 → 6,5 (Vorgabe), 0,12 → 11,4, 0,25 → 21,5 (wirkungslos). Die Kennzahl allein hätte 0,03 als Sieger gemeldet — '
         'die Sichtprobe braucht es.',
         VB + ', „Licht ausgleichen"'),
        ('Vorverarbeitung', 'messung', 'Ausrichten (Option ausrichten) ist kein Hebel für das Gesicht',
         'Neigung der Körperachse: vorne +0,86°, hinten +0,71°, seite.jpg −0,77°, 4.jpg +4,27°; nach dem Drehen +0,05 / +0,04 / +0,05 / +0,01°. S3 (an) gegen S4 (aus): die Köpfe unterscheiden sich, keiner ist klar besser; '
         'die Verzerrung der Front liegt in 4.jpg (Kopf nach unten geneigt), das Nicken liegt in der Tiefe. Variante „mitte" (nur Seitenfotos): Abstand der drei Mitten 2,7 → 0,3 % der Höhe, Köpfe in fünf Paaren nicht '
         'besser, im Mund-/Kinnbereich eher schlechter (Vermutung: das zeilenweise Verschieben schert den Kopf — nicht geprüft). Vorgabe aus.',
         VB + ', „Der Schritt Vorbereitung und die Option ausrichten"'),
        ('Vorverarbeitung', 'falle', 'Optionen aus dem LAUF lesen, nicht aus dem Anlegeskript',
         'S4 lief zuerst mit ausrichten = an (ein Browser-Speichern hatte die Option umgestellt, nicht gegengelesen); der erste Bericht „optisch gleich" verglich zwei an-Läufe. '
         'Vor jedem Probelauf die Optionen aus netz_arbeit/auftrag.json des LAUFS lesen.',
         VB + ', „Ergebnis S3 gegen S4"'),
        ('Vorverarbeitung', 'falle', 'Veraltete Ablage der Vorbereitung',
         'Die Fassung der Vorbereitung (FASSUNG 3) machte S1–S5 „veraltet": 4 von 10 Aufträgen mit Grund „Fassung 1 statt 3". Eine Ablage ohne vorbereitung.json gilt nie als aktuell (Ablage braucht einen '
         'Fassungsnamen). Die Karten zeigen einen Warnrahmen statt Abblenden (Edgar: „Bilder grau und kaum erkennbar").',
         VB + ', „Veraltete Ablage"'),
        ('Vorverarbeitung', 'parameter', 'Was andere Pipelines tun (Quelltext teils gelesen)',
         'Keine dreht das Foto; üblich ist ein Quadrat um die Alpha-Box mit langer Seite 83–92 % (TRELLIS 83, TRELLIS.2 100, Hunyuan3D, TripoSR, InstantMesh, SF3D 85, MV-Adapter und ECON 90, Pixal3D 91, '
         'MagicMan 92,5, PSHuman 96; Zero123 78, Wonder3D 75). Menschen-Pipelines zentrieren auf die Personenbox, die Ausrichtung übernimmt der SMPL-X-Schätzer. Recherche aus GitHub-Rohdateien, '
         'nicht alle Dateien selbst geprüft.',
         VB + ', „Was andere Pipelines tun"'),
    ]

    @classmethod
    def eintraege(cls):
        return [{'bereich': b, 'art': a, 'thema': t, 'befund': f, 'quelle': q} for b, a, t, f, q in cls.EINTRAEGE]

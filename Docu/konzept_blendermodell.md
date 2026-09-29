# Konzept: Dashboard → BlenderModel — Fotos + BVH → animierte Figur mit Kleiderphysik

Stand 29.09.2026, Fassung 1 — **Plan, nichts gebaut.** Auftrag Edgar: „dafür möchte ich auch eine
Pipeline haben in Dashboard - BVHModel … mit Bildauswahl, setzen der Parameter, des BVH Files,
Ergebnis auswählbar Genesis / MakeHuman / HumanBody, mit und ohne Haare, Kleider usw." Vorbild ist
ChatGPTs Zauberer (`3DObjects/Model_Jobs/zauberer/`: `Vorlage.jpeg`, `DanceKurz.bvh`, `Ergebnis.mp4`).

## 1. Was ChatGPT gemacht hat — und was davon Pipeline werden kann

Aus Edgars Beschreibung und den drei Dateien (die Skripte `build_wizard.py` und
`Zauberer_Haarkontakt_Wassertasche/kleiderhuelle.py` liegen NICHT im Ordner):

| ChatGPT | Art der Arbeit | In einer Pipeline |
|---|---|---|
| Mantel, Hut, Tasche als Querschnitte + Punktgitter → Quads, Subdivision, Solidify | von Hand modelliert (Agent schreibt Geometrie-Code je Kleidungsstück) | **nein** — das ist ein Agentenlauf mit MCP, keine Rechnung mit Parametern |
| Gesicht aus MakeHuman/MPFB-Grundnetz angepasst | Handarbeit | ersetzt durch „Mesh to 3D" (Gesichtskette, Textur) |
| Körper = Genesis9 als Kollider | Bestand | ja, ist unser Weg |
| Rigging/Skinning mit Genesis9-Skelett, BVH-Retarget | Standard | ja (BVH Retargeter, `genesis9.json`) |
| Cloth (Mantel, Unterkleid, Ärmel, Gürtelteile), Kollisionshüllen | Standard-Blender, gut parametrisiert | ja (`effekte/blender/stoffsimulation.py` als Vorlage) |
| Rigid Body für Tasche, Flaschen, Amulett | Standard | später (Requisiten, `G9requisit`) |
| 30.752 Hair Curves mit dynamischen Führungssträhnen | Standard, aber in Blender 5 nur mit Umwegen dynamisch | Stufe 4, Risiko |
| Cycles + OptiX, ffmpeg | Standard | ja |

**Messung am Ergebnis:** Video 960 × 960, 30 fps, 1.250 Bilder (41,7 s); die BVH hat 1.004 Bilder bei
60 fps (16,7 s). Das Video ist also nicht die BVH-Zeit — verlangsamt oder verlängert. Vier Bilder
(`ProjektTemp/_wegwerf/zauberer/ergebnis_bilder.png`): Mantel und Unterkleid schwingen sauber, Hut
sitzt, Bart als Strähnen; das Gesicht ist klein und ohne erkennbare Fototextur.

**Ehrliche Einordnung:** Die Qualität des Zauberers kommt aus handgebautem Kostüm und vielen
Iterationen eines Coding-Agenten. Eine Pipeline mit Reglern liefert im ersten Wurf weniger — dafür
in Minuten, wiederholbar, für jedes Foto. Was sie aus dem Foto NICHT baut: Mantel, Hut, Stab.
Kleidung kommt aus der Garderobe (Daz, GarmentCode, „Kleidung aus dem Netz"), Requisiten aus
`G9requisit`. Edgar, bitte die ChatGPT-Skripte in den Ordner kopieren — der Kostümaufbau darin ist
die Vorlage für einen späteren „Kostüm-Agent"-Schritt.

## 2. Bestand (gelesen, 29.09.2026)

| Baustein | Wo | Stand |
|---|---|---|
| **BlenderModel** (Parallelsession) | `core/models/blendermodellauftrag.py`, `daten/blendermodellablage.py`, `dienste/blendermodell{arbeiter,optionen,tabelle}.py`, `management/commands/blendermodell_fahren.py`, Migration 0050 | Modell, Ablage, Arbeiter, Optionen `{netz, figur}`, Tabelle. **Fehlen:** `Blendermodelllauf`, API, Seite, Menü |
| Fotos → Netz | `VideoToBVH/wrappers/_run_mesh.py` (TRELLIS.2, Hunyuan3D-2/2mv mit 4 Ansichten, Freisteller, Fotobacken, Gesichtspassung) | fertig, `Meshoptionen` |
| Netz → Figur | `Meshfigurlauf` (erkennung, haar, kalibrierung, koerper, gesicht, rest, textur, vorschau, frisur, speichern) | fertig; Ziel nur **Genesis 9** (feminine/masculine/neutral) |
| Kleidung aus dem Netz | `mesh-kleidung.md`, `Meshfigurhautmodell`; Garderobe `G9garderobe`, GarmentCode `G9gc*` | 29.09. gebaut |
| Haar | `Haar/` (Haarmaske, Haarobjekt-GLB, **Haarkarten = 3.000 Strähnen als Polylinien**), Frisur-Wahl, HaarEigen | fertig |
| Genesis → GLB **serverseitig** | `Genesis9/figurglb.py` (`G9figurglb`: Käfig + Atlas) | **ohne Rig, ohne Kleidung** — die GLB mit Skin schreibt heute nur der Browser (`konzept_modellexport.md`) |
| Genesis-Skelett, Gewichte, Bewegung in Python | `G9skelett`, `G9knochenmatrizen`, `G9haut`, `G9bewegungbvh` (Daz-Bewegung → BVH, 0,35 s) | vorhanden |
| Blender headless | `effekte/blender/kleidwind.py`: MPFB-Figur, **`bvhretarget.py`** (BVH Retargeter, Larsson), **`stoffsimulation.py`** (Anker, Kollider, Wind), **`effektrender.py`** (Workbench/Eevee → MP4); `modellexportblend.py` (GLB → .blend, `--factory-startup`) | gemessen (12.09.), Blender 5.0 |
| BVH Retargeter | `extensions/user_default/retarget_bvh`, `known_rigs/`: **genesis9, genesis3, makehuman, mhx2, rigify*, smpl, mixamo, cmu-mb** | installiert; `effekte/bvhnamen.py` benennt SMPL-X-Gelenke (`Pelvis`, `Left_hip` — so heißt auch `DanceKurz.bvh`) in `m_avg_*` um |
| MakeHuman / HumanBody als Figur | `MakeHuman/` (MhFigur, 163 Knochen), `effekte/figur/figurfilm.py` (`Modellfigur`, DEF-Rig, pyrender-Video) | vorhanden, nicht in „Mesh to 3D" als Ziel |
| Blender-Addon HumanBody | `HumanBodyBlender/` (Rig, Cloth Builder, Partikelhaar, Retarget, Garderobe) | Handwerkzeug, nicht headless |
| Seiten | Auftragsseiten-Regeln (`auftragsseiten.md`), Bildauswahl (`meshauftragseite.js`), Bühne + Karten (`meshfigur*.js`), Autosave (`meshfigureinstellungen.js`, 29.09.), Animationsbrowser (`gemeinsam/kategoriekasten.js`, 7.100 BVH) | wiederverwendbar |
| Video | ffmpeg liegt in `A:\archiv2\_AI\tools\ffmpeg\`, **nicht im PATH** (`figurfilm`s `Videokodierer` prüfen) | — |

## 3. Der Lauf: Schritte eines Auftrags „BlenderModel"

    netz        Fotos → Netz                      (bestehend, Meshoptionen)
    figur       Netz → Genesis-Figur              (bestehend, Meshfigurlauf-Schritte; Kleidung, Haar)
    export      Figur → GLB mit Skin              (NEU, serverseitig)
    blender     GLB → .blend: Rig, BVH-Retarget    (NEU, Blender headless)
    stoff       Kleidung als Cloth, Körper Kollider (NEU, aus stoffsimulation.py)
    haar        Haar starr / als Kurven            (NEU)
    render      Bilder → MP4, .blend, bericht.json (aus effektrender.py, plus Cycles)

Jeder Schritt schreibt `Blendermodel: …`-Zeilen (Muster `Effekte: …`, `Effektbeobachter`), ist
einzeln nachrechenbar („ab <schritt>", wie heute) und legt seine Zahlen in `bericht.json` ab —
keine Zahl auf der Seite ohne Messung dahinter.

### Optionen (Katalog, Gruppen wie `Blendermodelloptionen`: `netz`, `figur`, dazu NEU `blender`)

| Schlüssel | Werte | Vorgabe |
|---|---|---|
| `ziel` | genesis9 · makehuman · humanbody | genesis9 (die anderen Stufe 2b) |
| `bvh` | Datei aus dem Animationsbrowser oder hochgeladen (`DanceKurz.bvh`) | — |
| `bilder`, `fps`, `breite`, `hoehe` | Zahl | 300, 30, 960, 960 |
| `haar` | aus · starr · kurven | starr |
| `kleidung` | aus · netz (aus dem Foto erkannt) · garderobe:<stück> · garmentcode:<stück> | netz |
| `physik` | aus · stoff | stoff |
| `stoff`, `wind`, `anker_hoehe`, `unterteilung`, `selbstkollision_mm` | wie `Effektparameter` | Baumwolle, 2, Taille, 1, 3 |
| `requisiten` | aus · starr · rigid | aus (Stufe 5) |
| `renderer` | workbench · eevee · cycles | workbench (cycles ab Stufe 5, OptiX) |

## 4. Stufen mit Abnahme

**Stufe 1 — Fotos → Figur im BlenderModel** (Parallelsession, läuft): `Blendermodelllauf` steckt
`_run_mesh` und die `Meshfigurlauf`-Schritte zusammen; Seite = Kopie von „Mesh to 3D" mit
Bildauswahl. Abnahme: Auftrag mit Edgars vier Fotos läuft durch, Genesis-Figur in der Bühne,
Kleidung und Frisur wie in „Mesh to 3D".

**Stufe 2 — Figur → Blender mit Rig** (der eigentliche Neubau):
- `Genesis9/figurglb.py` erweitern zu **`G9figurrigglb`** (eigene Datei): Netz mit Morphs
  eingerechnet, **Skin** (Knochen aus `G9skelett`/`G9knochenmatrizen` mit Daz-Namen, Gewichte aus
  `G9haut`), Kleidungsstücke und Haar als eigene Teilnetze mit denselben Joints, ein Atlas je Teil.
  Vorlage für das glTF-Skin-Schreiben: Roomguests `werkzeug/glb.py`/`glb_skelett.py`
  (TRS statt `matrix` an Knochen — glTF verbietet Animation auf `matrix`-Knoten).
- Blender-Skript **`effekte/blender/blendermodell.py`** (`blender -b --python … -- --glb --bvh …`):
  GLB importieren (wie `modellexportblend.py`), BVH mit `Bvhnamen` umbenannt, Retarget über
  `Bvhretarget` auf das Genesis-9-Rig (`known_rigs/genesis9.json` — die Knochennamen der GLB
  müssen genau die Daz-Namen sein), Action prüfen, `.blend` speichern.
- **Falle, dokumentiert in `modellexportblend.py`:** ohne `--factory-startup` legt ein Addon aus
  Edgars Profil eine Icosphere in die Szene — hier brauchen wir aber die Erweiterung
  `retarget_bvh`. Weg: `--factory-startup` + `bpy.ops.extensions`/`addon_enable` nur für
  `retarget_bvh` (in Stufe 2 messen, ob die Icosphere dann ausbleibt).
- Abnahme (gemessen, wie `figurfilm`): Action mit N Bildern auf dem Rig; Ruheprobe (Bild 0 =
  Grundnetz); Hüfthöhe über dem Boden konstant ±2 cm; Workbench-Video 300 Bilder.
- **2b — Ziel MakeHuman / HumanBody:** dieselbe GLB-Schnittstelle. MakeHuman: `MhFigur` + 163-Knochen-
  Skelett → GLB (Retargeter kennt `makehuman.json`); HumanBody: `Modellfigur` + DEF-Rig
  (`rigify.json`). Voraussetzung, die heute FEHLT: „Mesh to 3D" passt nur Genesis an — für die
  beiden anderen müsste die Anpassung (Regler aus dem Netz) je Figurart nachgebaut werden. Deshalb:
  erst Genesis liefern; für MakeHuman/HumanBody im ersten Schritt nur die Regler übernehmen, die
  es dort gibt (Größe, Geschlecht, Gewicht), und das im Bericht so nennen.

**Stufe 3 — Kleidung physisch:** `Stoffsimulation` verallgemeinern: je Kleidungsteil der GLB
Anker-Gewicht aus dem Rig (Taille/Hüfte wie heute), Unterteilung, Cloth, Körper als Kollider
(Genesis-Netz, ohne die Kleidung darunter), Wind. Was aus dem Netz erkannt wurde (T-Shirt, Shorts)
bleibt gehäutet, nur lose Teile (Rock, Mantel, Kleid) werden Stoff — Regel aus `physik.md`: Blender
Cloth nur für das Offline-Video. Abnahme mit den Werkzeugen aus `ProjektTemp/effekte/rock/`
(`imkoerper.py`: 0 % Punkte im Körper; `sicht.py`: Saumhöhe, Knickwinkel), Bilder ansehen.

**Stufe 4 — Haar:** `starr` = Haar-GLB am Kopfknochen (wie `figurfilm`, Sitzprobe). `kurven` =
die Strähnen der **Haarkarten** (`Haarkarten.wachsen`, Polylinien) als `bpy.data.hair_curves` auf
dem Kopf, Surface Deform. Bewegung: Blender 5.0 hat für Curves keine eingebaute Dynamik — Wege:
Partikelhaar mit Hair Dynamics als Führung (ChatGPTs „dynamische Führungssträhnen"), oder Geometry-
Nodes-Simulation. Zuerst starr liefern, Dynamik als eigener Versuch mit Messung (Sitz am Kopf,
Abstand zur Kleidung, kein Durchdringen).

**Stufe 5 — Render und Requisiten:** `Effektrender` um Cycles + OptiX erweitern (im Hintergrund
möglich, Proben/Entrauschen als Parameter, Zeit je Bild messen); Requisiten aus `G9requisit`
(Hut, Stab, Tasche) starr am Knochen, danach Rigid Body mit Gelenk. Video über ffmpeg
(`Videokodierer`), Bericht mit Sekunden je Schritt.

**Stufe 6 — Vergleich Zauberer:** `Vorlage.jpeg` (die vier Ansichten der oberen Reihe als
vorne/rechts/hinten/links) + `DanceKurz.bvh` durch die Pipeline; Bild neben `Ergebnis.mp4`. Erwartung,
ehrlich: Körper, Gesicht und Bewegung besser (Fototextur, gemessene Gesichtspassung), Kostüm
schlechter (keine Mantel-Geometrie aus dem Foto) — bis ein Kostüm-Schritt dazukommt.

## 5. Laufzeit und Risiken

- Laufzeit heute: Netz 5–10 min, Figur 10–17 min; dazu Stoff (Blender ~0,3–1 s je Bild und Stück)
  und Render (Workbench Sekunden, Cycles 960² mit OptiX schätzungsweise 2–10 s je Bild — **messen**).
  Vorgabe deshalb 300 Bilder bei 30 fps; die 1.004 Bilder der Dance-BVH sind ein Langlauf.
- Eine GPU: Netz (TRELLIS) und Blender-Cycles dürfen nicht gleichzeitig laufen — `_anderer_lauf`
  auf alle Bereiche ausdehnen.
- Retarget: keinen eigenen Code (Edgar, 08.09.), nur der Retargeter; Halsproblem aus `retarget.md`
  gilt auch hier.
- Figurart-Wahl: Genesis zuerst; MakeHuman/HumanBody bekommen anfangs nur Grobregler (siehe 2b).
- Haardynamik in Blender 5.0 ist der unsicherste Punkt — nicht auf dem kritischen Pfad.

## 6. Arbeitsteilung (Vorschlag)

- Parallelsession: Stufe 1 und Seite (Stufe 6-Oberfläche: BVH-Wahl, Parameterkarten, Video-Ausgabe).
- Diese Session: Stufe 2 (`G9figurrigglb`, `blendermodell.py`, Retarget), dann 3, 4, 5.
- Schnittstelle zwischen beiden: `ablage.netzdatei()` → Figur-Dateien in `arbeit/` → **`ergebnis/figur.glb`**
  (mit Skin) → `ergebnis/figur.blend`, `ergebnis/video.mp4`, `ergebnis/bericht.json`.

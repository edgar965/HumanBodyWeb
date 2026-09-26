# Konzept: Modell-Export aus dem Kontextmenü (`/Charakter/`)

Stand 26.09.2026, Fassung 2 — Konzept, noch nichts gebaut.

## Auftrag

Rechtsklick auf das Modell (Zeile der Charakterliste über den Reitern) → neuer
Eintrag **„Exportieren …"**. Exportiert wird die gewählte Figur mit wählbarem
Inhalt — **Rig**, **Textur**, **Assets (Kleider inkl. Haare)**, **aktive
Animation**, per Vorgabe **alles angehakt** — in wählbare Formate. Zielordner
wählbar, Vorgabe `A:\3DTools\HumanBodyWeb\output\Export` (existiert).
Die Formate werden **im Browser** geschrieben, ohne Blender.

## Ist-Zustand (gelesen bzw. gemessen)

| Baustein | Wo | Brauchbar für |
|---|---|---|
| Kontextmenü der Modellzeile | `static/viewer/charakter/speichernmenue.js` → `Speichernmenue.binden()` über `gemeinsam/kontextmenue.js` | Einhängepunkt: ein Eintrag mehr |
| GLB-Export im Browser | `static/viewer/viewer/figur_export.js` (`FigurExport`, `GLTFExporter`) — nur Viewer-Seite, ohne Animation | Vorbild |
| Three.js-Exporter (r170, `node_modules/three/examples/jsm/exporters/`) | `GLTFExporter`, `OBJExporter`, `PLYExporter`, `STLExporter`, `USDZExporter` — **kein `ColladaExporter`** | GLB, OBJ, PLY, STL fertig |
| Aktive Animation | global `state.mixer` / `state.currentAction` (`bvhladen.js`, `eigenanimation.js`) — EINE aktive Animation | Clip = `state.currentAction.getClip()` |
| Figur | `state.characters.get(state.selectedCharacterId)` → `inst.group`, `inst.bodyMesh` (SkinnedMesh + DEF-Skelett), `inst.hairMesh`, `inst.clothMeshes`, GarmentCode-Stücke | Objektbaum |
| Blender 5.0.1 | `settings.BLENDER_EXE` — Export-Operatoren: alembic, obj, ply, stl, usd; **kein Collada mehr** (am 26.09.2026 per `dir(bpy.ops.wm)` geprüft) | nur noch für .blend nötig |
| Pfadprüfung | `core/safe_paths.py` `SafePath` + `Pfadwurzeln` | neue Wurzel „Export" |

## Formate

| Format | Netz | Textur | Rig | Animation | Schreiber | Abnehmer |
|---|---|---|---|---|---|---|
| **GLB** (glTF 2.0) | ja | ja (eingebettet) | ja | ja | `GLTFExporter` | Unity/Roomguest, Blender, Unreal, Web |
| **OBJ** + MTL | ja | ja (PNG daneben) | — | — | `OBJExporter` + eigener MTL-/Bildteil | Blender, MeshLab, fast alles |
| **PLY** | ja | Vertexfarben / UV | — | — | `PLYExporter` | **MeshLab**, CloudCompare |
| **STL** | ja | — | — | — | `STLExporter` | 3D-Druck, MeshLab |
| **DAE** (Collada 1.4.1) | ja | ja (PNG daneben) | ja | ja (gesampelt) | **eigener Schreiber** (siehe unten) | ältere DCC-Werkzeuge, SketchUp |
| **.blend** | ja | ja | ja | ja | nur mit Blender (siehe unten) | Blender |

„Mesh-Datei für MeshLab" = **PLY** (und STL). MeshLab liest OBJ+MTL mit Texturen
ebenfalls.

### Ohne Blender

GLB, OBJ, PLY, STL und DAE entstehen vollständig im Browser; der Server schreibt
nur die Dateien in den Ordner. **Einzige Ausnahme ist .blend:** Das ist Blenders
internes Speicherformat; ein Schreiber außerhalb von Blender ist mir nicht
bekannt. Vorschlag: .blend als Format im Dialog behalten, dann (und nur dann)
startet der Server Blender im Hintergrund und macht aus der GLB eine .blend.
Wer .blend nicht anhakt, braucht kein Blender.

### DAE — eigener Schreiber

Three.js hat keinen Collada-Exporter mehr, Blender 5.0 auch nicht. Also eine
eigene Klasse `ColladaSchreiber`, die Collada-1.4.1-XML schreibt:

- `library_geometries`: Positionen, Normalen, UV, Dreiecke je Werkstoff
- `library_images` / `library_effects` / `library_materials`: Bildkarten als PNG
  neben der .dae
- `library_controllers`: Skin (Bind-Shape, Inverse-Bind-Matrizen, 4 Gewichte je Punkt)
- `library_visual_scenes`: Knochenbaum als `JOINT`-Knoten
- `library_animations`: je Knochen eine Matrix-Spur, **gesampelt** mit fester
  Bildrate aus dem laufenden Clip (wie `_sampleBoneMatrices` in
  `cloth_export.js`) — so ist egal, wie der Clip intern aufgebaut ist

Das ist der größte Einzelposten (geschätzt 3–4 Module). Prüfen lässt er sich
nicht mit Blender 5 (kein Collada-Import mehr) — Gegenprobe mit Assimp
(`assimp info`) oder Blender 4.x.

## Dialog „Modell exportieren"

- **Formate** (Mehrfachwahl): GLB · OBJ · PLY · STL · DAE · .blend —
  Vorgabe: GLB + OBJ (offene Frage 1)
- **Inhalt**, alle **per Vorgabe angehakt**:
  - Rig
  - Textur
  - Assets (Kleider inkl. Haare)
  - Animation „<Clipname>"
- **Pose** für Formate ohne Animation (OBJ, PLY, STL): Auswahl
  **Ruhelage** (Vorgabe) · **angezeigtes Animationsbild** (das Bild, das der
  Mixer gerade zeigt; Netz wird dafür per CPU-Skinning in diese Pose gerechnet)
- **Ordner**: **beliebiger Ordner** (Textfeld + „Durchsuchen"), Vorgabe
  `…\output\Export`, zuletzt gewählter Ordner wird gemerkt
  (`ui_prefs.modell_export_ordner`, wie `studio_video_output`). Server prüft nur:
  absoluter Pfad, anlegbar, keine stillen Überschreibungen. Ausgenommen bleiben
  die Produktivdaten-Ordner `HumanBody/data/` und `HumanBodyBlender/data/`
  (Projektregel „nie dorthin schreiben").
- **Dateiname**: Vorgabe = Modellname (`inst.presetName`), bereinigt
- Knopf **Exportieren**

### Warnungen im Popup

Unter den Häkchen steht ein Warnfeld, das sich bei jeder Änderung neu rechnet —
vor dem Export, nicht erst danach:

- Animation angehakt, aber keine aktive Animation →
  „Keine Animation aktiv — es wird die Ruhelage exportiert."
- Animation angehakt, aber sie gehört einer anderen Figur (Wurzel von
  `state.mixer` liegt nicht unter `inst.group`) →
  „Die aktive Animation gehört zu „<Figur>" — sie wird nicht exportiert."
- Animation angehakt und ein Format ohne Animation gewählt →
  „OBJ, PLY, STL können keine Animation speichern — dort wird die gewählte Pose
  (Ruhelage bzw. angezeigtes Bild) exportiert." (Rig analog: „… kein Rig")
- Textur angehakt und STL → „STL kann keine Textur speichern."
- Werkstoff mit eigenem Shader, dessen Bildkarten nicht gelesen werden können →
  „Textur von <Teil> nicht exportierbar" (beim Sammeln festgestellt)

Der Export läuft trotzdem; die Warnungen stehen auch in der Abschlussmeldung.

## Ablauf

```
Rechtsklick Modellzeile → „Exportieren …" → Dialog (Warnungen live)
   │
   ▼  Browser
   Objekte sammeln (Körper; Assets ja/nein) → Varianten bauen:
     Rig aus    → Netze in Ruhelage ohne Skin
     Textur aus → Werkstoffe ohne Bildkarten
   je Format:   GLB / OBJ+MTL+PNG / PLY / STL / DAE+PNG
   │  POST /api/character/modellexport/  (multipart: Dateien + Optionen-JSON)
   ▼  Server
   Zielordner prüfen → Dateien schreiben → falls .blend: Blender -b (GLB → .blend)
   → {dateien:[pfad, bytes], warnungen:[…]}
   ▼
   Meldung mit Pfaden
```

## Neue Module (eine Klasse je Datei)

| Datei | Klasse | Aufgabe |
|---|---|---|
| `static/viewer/charakter/modellexport_menue.js` | `Modellexportmenue` | Eintrag im Kontextmenü, Aufruf |
| `static/viewer/charakter/modellexport_dialog.js` | `Modellexportdialog` | Dialog, Vorgaben, Warnungen live |
| `static/viewer/charakter/modellexport_inhalt.js` | `Modellexportinhalt` | Objekte sammeln, Rig/Textur/Assets-Varianten, Clip-Zugehörigkeit |
| `static/viewer/charakter/modellexport.js` | `Modellexport` | Formate aufrufen, senden |
| `static/viewer/gemeinsam/objmtl.js` | `ObjMtl` | MTL + Bildkarten zu `OBJExporter` |
| `static/viewer/gemeinsam/collada/…` | `ColladaSchreiber` u. a. (3–4 Module) | DAE |
| `templates/_modellexport_dialog.html` | — | Markup |
| `core/api/modellexport.py` | `Modellexportanfrage` | Endpunkt |
| `static/viewer/gemeinsam/netzpose.js` | `Netzpose` | Netzkopie in angezeigter Pose (CPU-Skinning) |
| `core/dienste/modellexportziel.py` | `Modellexportziel` | beliebiger Ordner: absolut, anlegbar, Sperre für Produktivdaten; Namen bereinigen, Kollision → `_2` |
| `werkzeug/blender_blend.py` | — (Blender-Skript) | nur .blend: GLB → .blend |

`speichernmenue.js` bekommt nur eine Zeile.

## Tests (geschrieben, laufen nur auf Ansage)

- unit (JS): Warnungen je Kombination; `ColladaSchreiber` an einer Kunstfigur
  (2 Knochen, 1 Dreieck) — XML gültig, Gewichte und Spuren vollständig
- unit (Python): `Modellexportziel` — Ordner außerhalb abgelehnt, Namen
  bereinigt, keine stillen Überschreibungen
- Browser: Kontextmenü → Dialog → Export einer HumanBody-Figur mit BVH; alle
  Dateien im Ordner; GLB in Blender, PLY in MeshLab geöffnet

## Risiken

- **Werkstoffe mit eigenen Shadern** (Haut, Haare, `onBeforeCompile`): Exporter
  kennen nur Standard-Werkstoffe. Je Figurart (HumanBody, Genesis 9, UMA, SMPL-X,
  MakeHuman) einmal prüfen — das Ergebnis speist die Warnung „Textur nicht
  exportierbar".
- **Stoffsimulation** (Stoffschwung) ist kein Skin — in der Animation steht sie
  im aktuellen Bild.
- **Größe:** Genesis 9 mit Texturen; Obergrenze wie `Figurexport.MAX_BYTES`.

## Offene Fragen an Edgar

1. **Vorgabe der Formate:** GLB + OBJ angehakt, oder alle?
2. **.blend** behalten (dann Blender nur für dieses Format) oder streichen?

Entschieden (26.09.2026): Pose wählbar, Vorgabe Ruhelage · Ordner beliebig ·
Inhalt per Vorgabe komplett angehakt · Warnungen im Popup · Formate per Vorgabe
nur **GLB** angehakt · **.blend bleibt** (Blender nur, wenn angehakt).

Umsetzung folgt in diesem Dokument nicht mehr nachgeführt — Stand im Code.

# Kleiderphysik im Theatre-Modul — Bestandsaufnahme und Vorschlag (10.09.2026)

Auftrag (Edgar): „Suche erstmal nach einem Opensource code, der das schon
implementiert hat, und mach einen Vorschlag." Gemeint ist Stoffdynamik wie in
Marvelous Designer — Falten, die beim Gehen entstehen — gerechnet beim
MP4-Export des Theatre-Moduls, nicht in Echtzeit. Der Ablaufplan dazu steht in
`HumanBodyWeb/Docu/plan_stoffdynamik.md`; dieses Dokument entscheidet die Frage,
die dort offen war: **welcher Motor rechnet den Stoff auf dem bewegten Körper.**

Alles unten ist nachgelesen (Quellen am Ende) oder auf dieser Maschine
gemessen (Skripte und Protokolle in `proben/`). Was ich nicht geprüft habe,
steht als „nicht geprüft".

## 1. Was im Projekt schon liegt — und was davon trägt

**`HumanBody/collision/` ist genau diese Pipeline, für ein anderes Kleid.**
Drei Motoren rechnen dort Stoff Bild für Bild auf einem animierten Körper und
liefern ein MP4 (Engine 1 `blender_eevee.py`, Engine 2 `warp_blender.py`,
Engine 3 `warp_only.py`; Eingabe `SceneInput` mit Körpernetz, Hautgewichten,
Knochenmatrizen je Bild und „Stoffsegmenten"; Ausgabe `bake.npz` mit Punkten je
Bild; Aufruf aus BVH Studio und von der Szene-Seite über
`window.__exportClothMP4`). Zwei Einschränkungen, beide am Code belegt:

* Sie rechnet nur für **generierte Modelle** (`inst.generatedConfig`,
  `boneVertexRanges`); die Stoffsegmente sind Rock- und Tutu-Formen des
  Modellgenerators, an einem Knochen festgenadelt. Ein GarmentCode-Stück auf
  der HumanBody-Figur kennt sie nicht.
* **Der Warp-Motor (Engine 2/3) kollidiert nicht mit dem Körper.** Der
  Docstring von `warp_sim.py` verspricht „a triangle-collision pass against the
  rigid body" und „Body-Push-Out als Post-Correction" — im Code gibt es weder
  `add_shape_mesh` noch eine Netzabfrage, `ground = False`, und der Körper wird
  je Bild nur für den Renderer gehäutet (`warp_stabilitaet.build_builder`:
  Kommentar „Rigid body collider is added per-frame", ohne dazugehörige
  Zeile). Nur Engine 1 (Blender) hat einen Kollider: der gehäutete Körper mit
  `Collision`-Modifikator, Stoff mit `Cloth`-Modifikator und Nadelgruppe.

Was davon trägt: das Bake-Format, der Unterprozess-Rahmen, ffmpeg, und der
Blender-Aufbau aus `blender_stoff.py` (Armature vor Cloth, Nadelgruppe,
`distance_min = 0.015`, `thickness_outer = 0.02` — jede Zahl dort ist aus einem
Fehler gewachsen).

**Der GarmentCode-Warp-Fork** (`Assets/GarmentCode/warp_fork`, warp 1.0.0b6 in
`python10_Garment`) kennt den Mechanismus für einen bewegten Körper
(`update_smooth_body_shape`: Punkte tauschen + `refit`), aber kein Kollider
hat dort eine Geschwindigkeit (`body=-1`), und `warp.sim` ist im Upstream seit
Fassung 1.7 nicht mehr enthalten — die Fassung ist eingefroren.

## 2. Kandidaten, geprüft

| | Lizenz | läuft hier? | bewegter, verformter Körper | Selbstkollision | Stand |
|---|---|---|---|---|---|
| **Newton** 1.5.1 (Linux Foundation, auf NVIDIA Warp) | Apache-2.0 | ja — installiert in einer eigenen venv auf Python 3.14 + warp 1.17 | ja: `Mesh.mesh` ist das `wp.Mesh`; Punkte und Geschwindigkeiten tauschen, `refit()`; der Kontaktkernel liest beides (`mesh_query_point_sign`, `mesh_eval_velocity`) | ja (VBD) | v1.5.1 vom 27.08.2026, Windows offiziell |
| **Blender 5.0.1** Cloth | GPL, als Werkzeug | ja, installiert; Engine 1 nutzt es schon | ja, geprüft (Probe unten) | ja | fest im Projekt |
| GarmentCode-Warp-Fork 1.0.0b6 | s. o. | ja (python10_Garment) | Mechanismus da, ungeprüft; keine Kollidergeschwindigkeit | Dreieck-Partikel ja | eingefroren |
| ContourCraft / HOOD (ETH, neuronal) | MIT | **nein**: Linux-Anleitung, torch 2.5 cu124, pytorch3d und CCCollision selbst bauen | nur SMPL/SMPL-X-Körper mit AMASS-Posen | gelernt | ContourCraft SIGGRAPH 2024, aktiv |
| Codim-IPC (C-IPC) | Apache-2.0 | nein: Ubuntu/macOS, 5 Commits | im Prinzip (IPC) | ja, garantiert | Forschungscode |
| Genesis | Apache-2.0 | vermutlich (Windows, Python 3.10–3.13) | nicht dokumentiert | PBD | Robotik-Fokus, nicht vertieft |
| Jolt Physics (auch JS/WASM) | MIT | ja | **nein**: Soft Bodies kollidieren nicht mit Mesh-Shapes | nein | — |
| Ten Minute Physics (XPBD in JS) | MIT | ja | nein, nur Kugel und Ebene | ja (Hashing) | Lehrcode |
| Marvelous Designer, iClone, Magica Cloth | geschlossen | — | — | — | — |

**Zu ContourCraft** (der einzige Kandidat, der „wie MD beim Gehen" wirklich
gelernt hat): Er simuliert Kleidung neuronal auf SMPL-Körpern mit
Bewegungsfolgen und behandelt Mehrlagen-Outfits. Er passt nur zur
SMPL-Figurart dieses Projekts, braucht Linux (WSL2 mit CUDA wäre der Weg) und
einen eigenen Garment-Import. Kein Kandidat für die erste Fassung; ein
möglicher zweiter Motor für SMPL-Figuren.

## 3. Gemessen auf dieser Maschine (RTX PRO 4500 Blackwell, Treiber 610.88)

Probe: ein Tuch 2 × 2 m mit 10.201 Partikeln fällt auf eine Kugel (4.096
Dreiecke), die sich 1,5 s lang mit 0,4 m/s zur Seite bewegt und dabei um 30 %
in die Höhe wächst — der Mechanismus „animierter Körper", ohne Boden im Weg.
60 Hz, 10 Teilschritte je Bild. Gezählt werden Stoffpunkte IM Kollider.

| Motor | Weg | Zeit je 60-Hz-Bild (Median) | tiefster Punkt im Kollider |
|---|---|---|---|
| Newton `SolverStyle3D` | Netz verformen (Punkte + Geschwindigkeiten, `refit`) | 1.046 ms | **1,8 mm**, kein Punkt tiefer als 5 mm |
| Newton `SolverStyle3D` | kinematischer Starrkörper (`body_q`) | 976 ms | 279 mm — Stoff durchstoßen |
| Newton `SolverVBD` (Selbstkontakt an) | Netz verformen | 366–412 ms | 71–299 mm — durchstoßen |
| Newton `SolverVBD` (Selbstkontakt aus) | Netz verformen | 293 ms | 83 mm — durchstoßen |
| Newton `SolverVBD`, Stoff 1.000-mal leichter (0,5 kg) | Netz verformen | 336 ms | 6,6 → 333 mm — durchstoßen |
| **Newton `SolverStyle3D`, Stoff 0,5 kg** | Netz verformen | 998 ms | **0 Punkte im Kollider über alle 90 Bilder** — und das Tuch fährt auf der Kugel MIT (Reibung über die Netzgeschwindigkeit), statt herunterzurutschen |
| Blender 5.0.1 Cloth (41 × 41, Selbstkollision an) | Kollider bewegt + Shape-Key | 30 Bilder in 3,1–3,5 s | **0 von 1.681 Punkten im Kollider** |

Dazu: Newtons Kernelbau beim ersten Lauf **244 s** (danach aus dem Cache in
1 s; der Cache MUSS vor `wp.init()` ins Projekt gelegt werden —
`wp.config.kernel_cache_dir` — sonst landet er unter `%LOCALAPPDATA%` auf C:,
was beim ersten Lauf passiert ist und aufgeräumt wurde).

Was die Tabelle sagt: **Nur Newtons Style3D-Löser hat den bewegten,
verformten Kollider gehalten**, und zwar über genau den Weg, den ein
animierter Körper braucht — mit physikalischer Stoffmasse ohne einen einzigen
Punkt im Kollider, und das Tuch wird von der Kugel mitgenommen, was für einen
gehenden Körper genau das Verhalten ist, das im alten Fork fehlte. Der VBD-Löser (der mit dem Selbstkontakt) ließ den
Stoff in jeder Variante durch — bei schwerem wie bei leichtem Stoff; sein
Partikel-Kontakt ist eine weiche Strafkraft (`soft_contact_ke`), und ein
Kollider mit 0,4 m/s läuft ihr davon. Das ist eine Messung mit Vorgabewerten
aus Newtons eigenen Beispielen, keine Grenze des Verfahrens — aber es ist die
Zahl, die zählt, solange niemand die Gegenzahl hat. Blender hält den Kollider
ebenfalls, im Toy-Maßstab.

Nicht gemessen: Blender mit 11.000 Stoffpunkten und dem echten Körper
(70.851 Punkte), Newton mit dem echten Körper, und vor allem das BILD — ob
Falten entstehen, die nach Stoff aussehen. Das ist Schritt 3 des Plans, und
er ist für beide Motoren derselbe.

## 4. Vorschlag (angepasst 10.09.2026: „blenderCloth nutze ich nicht, garmentCode ist bisher am besten")

Dieselbe Bestandsaufnahme steht als Seite unter **Hilfe → Kleidung →
Kleiderphysik** (`kleidung/physik.py`, `templates/hilfe/kleidung_physik.html`);
die Seite ist die gepflegte Fassung, dieses Dokument das Arbeitspapier im
Ordner.

**GarmentCode bleibt der Anfang.** Schnitt aus den Maßen, Drapierung im Fork,
Stoffkorrektur, Anziehen — das Stück in Ruhelage auf der Figur
(`*_sim_rig.json`) ist Bild 0 jeder Dynamik. Daran ändert sich nichts; die
Dynamik setzt auf dem Ergebnis auf, sie ersetzt es nicht.

**Motor für die Dynamik: Newton mit `SolverStyle3D`.** Der einzige geprüfte
Weg, der den bewegten, verformten Körper gehalten hat — über genau den
Mechanismus, den ein animierter Körper braucht (Punkte und Geschwindigkeiten
des Körpernetzes je Bild tauschen, `refit`). Er kennt damit die
Kollidergeschwindigkeit (Reibung beim Gehen — das Risiko Nr. 2 aus dem Plan
fällt weg) und läuft hier in einer eigenen venv. Die Probe
`proben/probe_newton_kollider.py` ist der Startpunkt.

    GarmentCode wie heute → Stück in Ruhelage (Bild 0)
    Retarget (vorhanden) → Körper je Bild (Umahaut.verformen, 60 Hz)
    Newton/Style3D: add_cloth_mesh(Stück), Körper als Mesh-Shape,
        je Bild Punkte + Geschwindigkeiten tauschen, refit, 10 Teilschritte;
        Einlaufphase A-Haltung → Bild 0, zuerst die Ruhe-Probe
    Stoffbilder-Ablage (float16, Fingerabdruck) → Theatre bei zeitSetzen(t) → MP4

Preis: rund 1 s je 60-Hz-Bild bei 10.000 Punkten (10 s Animation ≈ 10 min),
einmal 4 Minuten Kernelbau (Cache ins Projekt), ein junges Projekt
(Deprecation-Hinweise, Issue 351). **Offen:** die Übersetzung der
GarmentCode-Materialwerte (`gui_sim_props.yaml`) auf Style3Ds
`tri_aniso_ke`/`edge_aniso_ke` — ohne Abgleich ist derselbe Stoff in Ruhe
und in Bewegung verschieden steif; die Ruhe-Probe ist der Prüfpunkt. Und ob
Style3Ds eigene Kollisionsklasse Stoff gegen Stoff hält, zeigt erst das echte
Stück.

**Rückfall an derselben Stelle:** der GarmentCode-eigene Warp-Fork mit
`replace_mesh_points` + `refit` (der Weg aus `plan_stoffdynamik.md`) — gleiche
Ein- und Ausgabe, aber ohne Kollidergeschwindigkeit und auf einer
eingefrorenen Warp-Fassung. Nur, falls Newton am echten Körper scheitert.

**Nicht empfohlen:** Blender Cloth (Edgars Entscheidung; bleibt oben als
Messzeile), VBD (durchstoßen), ContourCraft (Linux, nur SMPL), eine
Browser-Echtzeitlösung (kein Kandidat kollidiert mit einem Netz).

### Wo der Code hinkommt

Edgar: „mach das im Ordner `HumanBodyWeb/TheatreJS/kleiderPhysik`". Vorschlag
für die Aufteilung darunter, damit der Ordner nicht zwei Sprachen mischt, ohne
dass man es sieht:

    kleiderPhysik/
      VORSCHLAG.md, proben/          dieses Dokument, Messskripte, Protokolle
      src/                            Theatre-Seite (ES-Module): Stoffbilder laden,
                                      bei zeitSetzen(t) einsetzen, Kästchen im Export
      python/                         der Lauf: Körper je Bild, Blender-Bake,
                                      Ablage (float16 + Fingerabdruck), Endpunkte

Der Python-Teil muss vom Django-Server importierbar sein; dafür gehört der
Ordner in den `sys.path` (wie `ASSETS_ROOT`), oder der Lauf liegt als Paket
unter `Assets/kleidung/`, und hier bleibt nur die Theatre-Seite. Das ist eine
Entscheidung von Edgar; der Vorschlag hier ist die erste Variante.

### Schritte (aus dem Plan, angepasst)

1. GarmentCode-Stücke ins Theatre laden (heute sieht Theatre sie nicht) —
   unabhängig vom Motor, sofort sinnvoll.
2. Körper je Bild serverseitig aus dem Retarget (Bewegungsspuren →
   `Umahaut.verformen` auf dem Steuernetz).
3. Blender-Bake mit dem echten Stück und `Walk/01_01`, zuerst die Ruhe-Probe
   (Körper steht → Stoff bewegt sich nicht), dann die Einlaufphase A-Haltung →
   Bild 0. **Abbruchkriterium:** Bewegung sichtbar besser als LBS, 10 s
   Animation unter fünf Minuten Bake. Sonst Newton/Style3D an derselben Stelle
   einsetzen (gleiche Ein- und Ausgabe) und noch einmal messen.
4. Ablage der Stoffbilder mit Fingerabdruck (Stück, Figurform, Clip, Motor,
   Fassung) — ohne Fassungsnamen rechnet irgendwann ein Export mit den Bildern
   eines anderen Laufs.
5. Theatre: `stoffbild.js` mischt bei `zeitSetzen(t)` zwei Nachbarbilder ins
   Netz; der vorhandene Bild-für-Bild-Export liefert dann von selbst das MP4.
6. Kästchen „Stoff simulieren" im Export-Dialog mit Balken (ein Bake läuft
   Minuten).

## 5. Quellen

* Newton: https://github.com/newton-physics/newton (README: Apache-2.0,
  Linux/Windows/macOS, Python 3.10+; Releases v1.5.1 28.08.2026),
  https://pypi.org/pypi/newton/json (warp-lang ≥ 1.16),
  `newton/_src/geometry/kernels.py` (`create_soft_contacts`:
  `mesh_query_point_sign`, `mesh_eval_velocity`),
  `newton/_src/geometry/types.py` (`Mesh.finalize` → `self.mesh`),
  `newton/examples/cloth/example_cloth_h1.py` (Jacke auf kinematisch
  bewegtem Humanoid, `SolverStyle3D`, `rebuild_bvh` je Bild),
  https://github.com/newton-physics/newton/issues/351 (VBD-Selbstkontakt
  gegen Kollider, geschlossen).
* Warp: https://raw.githubusercontent.com/NVIDIA/warp/main/CHANGELOG.md
  (1.17.0 vom 31.08.2026; kein `warp.sim` mehr im Paket, hier an python14
  gemessen).
* Blender 5.0.1 lokal (`bpy.types.ClothCollisionSettings`,
  `CollisionSettings`) und `HumanBody/collision/blender_stoff.py`.
* ContourCraft: https://github.com/dolorousrtur/ContourCraft (MIT, SMPL,
  TODO „Support for SMPL-X"), dessen INSTALL.md (python 3.10,
  torch 2.5.0+cu124, pytorch3d, CCCollision), Paper
  https://arxiv.org/abs/2405.09522; HOOD: https://github.com/dolorousrtur/hood
  (MIT, Python 3.9, CUDA 11.7).
* Codim-IPC: https://github.com/ipc-sim/Codim-IPC (Apache-2.0, Ubuntu/macOS).
* Genesis: https://github.com/Genesis-Embodied-AI/Genesis (Apache-2.0,
  Python ≥ 3.10 < 3.14, PBD-Cloth).
* Jolt: https://jrouwe.github.io/JoltPhysics/ („Soft bodies can only collide
  with rigid bodies", keine Mesh-Shapes).
* Ten Minute Physics: https://github.com/matthias-research/pages
  (`tenMinutePhysics/15-selfCollision.html`, MIT im Dateikopf).
* GarmentCode: https://github.com/maria-korosteleva/GarmentCode (MIT; keine
  Animation, kein Verweis auf HOOD/ContourCraft).

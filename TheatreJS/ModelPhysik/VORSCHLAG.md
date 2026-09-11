# Modellphysik — Bestandsaufnahme und Vorschlag (10.09.2026)

Auftrag (Edgar): „ähnlich wie die Kleider, ändert sich auch am Körper bei der
Bewegung die Hautfalten, die Muskeln, usw. Schau auch da ob es fertige Konzepte
openSource gibt, mache einen Vorschlag." Dazu zwei Präzisierungen im Lauf:
**„ich nutze das HumanBody Modell, dafür brauche ich das!"** und „du kannst auch
für SMPL eine parallel Implementierung machen zu test".

Maßgeblich ist also die **HumanBody-Figur** (MB-Lab-Netz, 18.210 Punkte,
Rigify-DEF-Skelett mit 176 Knochen, Hautgewichte als JSON). SMPL dient als
Prüfstand, weil es die Korrektur, um die es geht, bereits mitbringt.

Alles unten ist entweder auf dieser Maschine gemessen (Skripte und Protokolle in
`proben/`) oder am fremden Quelltext nachgelesen (Quellen am Ende). Was ich nicht
geprüft habe, steht als „nicht geprüft".

---

## 1. Drei Dinge, die hier ständig vermischt werden

Edgars Satz nennt zwei Wirkungen („Hautfalten, Muskeln"), technisch sind es aber
drei getrennte Baustellen mit völlig verschiedenen Preisen:

| | was man sieht | wovon es abhängt | typisches Mittel |
|---|---|---|---|
| **A. Häutungsfehler** | Ellbogen sinkt ein, Achsel kollabiert, „Candy Wrapper" beim Verdrehen | nur von der Pose | Delta Mush, Dual Quaternion, Corrective Smooth |
| **B. Posenabhängige Form** | Bizeps wölbt sich, Falte in der Beuge, Schulterblatt tritt hervor | nur von der Pose | Pose-Blendshapes (SMPL `posedirs`), handmodellierte Korrektiv-Shapekeys |
| **C. Weichgewebe-Dynamik** | Fleisch schwingt beim Auftreten nach, Brust und Bauch wackeln | von der **Geschichte** der Bewegung (Geschwindigkeit, Beschleunigung) | Feder-Knochen, FEM/Projective Dynamics |

**A ist kein Ersatz für B.** Die Autoren von Direct Delta Mush schreiben es in
ihrer eigenen Abschlussfolie: „Limitations: no collision, **no volume
preservation**, no secondary effect". Wer nur A behebt, bekommt einen sauberen,
aber schlaffen Arm.

**C ist kein Ersatz für B** und umgekehrt: Ein Feder-Knochen lässt Fleisch
nachschwingen, wölbt aber keinen Muskel; eine Pose-Blendshape wölbt den Muskel,
schwingt aber nie nach.

---

## 2. Was heute passiert — gemessen

### 2.1 Der Browser häutet roh, ohne jede Korrektur

`THREE.SkinnedMesh` ist Linear Blend Skinning. Gemessen am echten HumanBody-Netz
mit den echten Gewichten (`proben/probe_lbs_ist.py`, Umfang derselben Punktmenge,
Querschnitt 3 cm über dem Ellbogen, Ruhewert 25,48 cm):

| Beugung des Ellbogens | Armumfang | |
|---|---|---|
| 29 Grad | 24,97 cm | −2,0 % |
| 59 Grad | 21,96 cm | −13,8 % |
| **89 Grad** | **20,96 cm** | **−17,7 %** |

Ein Arm, der beim Beugen ein Sechstel seines Umfangs verliert. Das ist das
Bild, das Edgars Frage ausgelöst hat.

Der **Candy-Wrapper beim Verdrehen ist dagegen kein Befund**: über 45 bis 180
Grad Drehung ändert sich der Unterarmquerschnitt um 0,0 bis 0,2 %. Rigify teilt
den Unterarm in zwei Twist-Segmente, und die fangen ihn ab. Das ist eine gute
Nachricht — es spart die halbe Baustelle A.

### 2.2 Zwei fertige Korrekturen liegen ungenutzt im Projekt

* **`corrective_smooth_inv`** steht als 176. Knochen in
  `data/humanBody_male/skin_weights_base.json` und trägt 1.536 Punkte. Das ist
  die Ausschlussgruppe für Blenders `CORRECTIVE_SMOOTH`-Modifikator, den MB-Lab
  auf jede Figur setzt (`tools/MB-Lab/humanoid.py:1271`,
  `add_corrective_smooth_modifier`). **In Blender ist die Glättung an, im
  Browser gibt es sie nicht.** Was Edgar in Blender sähe und was der Browser
  zeigt, sind also nicht dieselbe Verformung.
* **`Smplkoerper.posieren` wendet `posedirs` an** — die vollständige
  SMPL-Pose-Korrektur, Zeile `v_geformt = v_rest + self.posedirs @ pose_feature`.
  Produktiv ruft sie **niemand** auf: Der einzige Aufrufer im ganzen Projekt ist
  ein Test (`core/tests/longrunner/test_smplgelenke.py:178`). Die SMPL-Figuren
  in der Szene bekommen ihr Netz einmal und werden danach im Browser mit LBS
  gehäutet — ohne die Korrektur, die das Modell mitbringt.

### 2.3 Was eine Pose-Korrektur wirklich bringt

Dieselbe Messung an SMPL, wo beide Varianten derselben Rechnung verfügbar sind
(`proben/probe_vergleich_beuge.py`, SMPL männlich):

| Ellbogen 120 Grad | Ruhe | nur LBS | mit Pose-Korrektur |
|---|---|---|---|
| kurz über dem Ellbogen | 27,55 cm | 23,74 cm (**−13,8 %**) | 25,99 cm (**−5,6 %**) |
| Mitte des Oberarms (Bizeps) | 30,80 cm | 30,59 cm (−0,7 %) | 31,16 cm (**+1,2 %**) |

Die Korrektur holt knapp **zwei Drittel** des verlorenen Querschnitts zurück —
und die zweite Zeile ist die eigentliche Antwort auf „Muskeln": Der Bizeps
**wächst** um 1,2 %, während er unter reinem LBS um 0,7 % schrumpft.

Über den ganzen Körper (`proben/probe_smpl_posedirs.py`) bewegt die Korrektur
bei 90 Grad Kniebeugung 61 % aller Punkte um mehr als 1 mm, im Maximum 10,6 mm;
an der Schulter bis 24,5 mm. Das Körpervolumen fällt unter reinem LBS von 82,83
auf 82,29 Liter und liegt mit Korrektur bei 83,44 Liter.

### 2.4 Wie fein darf eine Falte sein?

Das Netz hat eine mittlere Kantenlänge von **4,1 mm** (p10 1,0 mm, p90 20,6 mm);
nach der Catmull-Clark-Stufe, die die Szene anzeigt (18.210 → 70.851 Punkte),
rund **2,1 mm**. Eine Beugefalte am Ellbogen (5–15 mm) ist damit darstellbar,
eine feine Hautfalte am Handrücken oder Hals (1–2 mm) **nicht**. Feine Falten
gehören in eine Normal Map, nicht in die Geometrie — das ist keine Meinung,
sondern die Auflösungsgrenze des vorhandenen Netzes.

---

## 3. Kandidaten: fertiger Open-Source-Code

Die entscheidende Spalte ist die dritte. „Nimmt HumanBody" heißt: Es frisst
Netz und Skelett, wie wir sie haben — ohne dass jemand das Verfahren nachbaut.

| | Lizenz | läuft hier? | nimmt HumanBody? | liefert |
|---|---|---|---|---|
| **FastProjectiveSkinning** (Komaritzan/Botsch, MIG 2019) | GPL, kommerziell auf Anfrage | **ja — hier gebaut** (CPU; drei Hürden, siehe 3.1) | **ja** — `.off`-Netz + `.skel` (`x y z name parent`), **braucht keine Hautgewichte** | B **und** C: Volumen, Muskel-/Fettschicht, Nachschwingen, globale Kollision |
| **Spring Decomposed Skinning** (Akyürek, CGF 2025) | MIT | Python, nicht gebaut geprüft | Netz + Rig + Gewichte; „work in progress", nur `demo/` und `test/` laufen | nur C (Wackeln), ohne Tetraedernetz |
| **Newton** 1.5.1 Soft-Body (VBD, Neo-Hookean) | Apache-2.0 | **ja**, installiert und gemessen (3.2) | **nein**: braucht ein **Tetraedernetz**, das es hier nicht gibt | B und C, aber Vernetzung fehlt |
| **PhysSkin** (CVPR 2026, zju3dv) | im Repo nicht ausgewiesen | nein: Bash/Linux, PyTorch 2.7 + CUDA 11.8 | nein — braucht Shape-Encoder-Latents | Echtzeit-Physik, generalisierend |
| **smplx / SMPL `posedirs`** | Code offen, **Modelle MPI-Lizenz** (Forschung; SMPL-Body separat CC-BY) | **ja** — liegt zweifach im Projekt | **nein**, nur SMPL-Topologie (6.890 Punkte) | B, gemessen in 2.3 |
| **STAR** (Osman, ECCV 2020) | **nicht kommerziell** | nicht geprüft | nein, SMPL-artig | B, besser lokalisiert als SMPL |
| **Blender „Jiggle Physics"** (naelstrof, Fork von Wiggle 2) | GPL-3 | Blender 5.0.1 ist da (≥ 4.2 gefordert) | **ja**, jedes Armature — aber nur **Deform-Bones**, keine Bendy Bones/Constraints | C, in Keyframes backbar |
| **Blender `CORRECTIVE_SMOOTH`** | GPL (in Blender) | ja | **ja** — die Ausschlussgruppe liegt in unseren Daten | A |
| **BlenRig** (Bouza) | GPL | nicht geprüft | eigenes Rig-System, nicht Rigify-DEF | B, erzeugt Korrektiv-Shapekeys + Driver |
| **`@pixiv/three-vrm-springbone`** | MIT, v3.5.5, gepflegt | Browser | ja, arbeitet auf Knochen | C, im Browser, sehr billig |
| **`xloveee/jiggle-physics`** | BSD-3 | Browser, ohne Build | Gewichtstextur je Figur | C — aber **4 Commits, 40 Sterne**: Demo, keine Bibliothek |
| SoftSMPL (Santesteban 2020), DMPL | — | — | — | **kein Code veröffentlicht** bzw. Modelldatei nicht im Projekt |

**Nicht gefunden, und das ist ein Befund:** Für **B im Browser** — posenabhängige
Korrektiven, die zur Laufzeit aus Knochenwinkeln gesteuert werden — gibt es keine
fertige Three.js-Bibliothek. Three.js kann Morph Targets, aber die Steuerung
„Knochenwinkel → Morph-Gewicht" muss von irgendwo kommen; glTF transportiert
Driver nicht.

### 3.1 FastProjectiveSkinning: der Bau auf dieser Maschine

Das Repo ist geklont (`ProjektTemp/modelphysik/fps`, mit Submodulen pmp-library
und Eigen). Zwei Hürden, beide ohne Eingriff in fremden Code:

* `pmp-library` verlangt `cmake_minimum_required` unter 3.5, CMake 4.4 lehnt das
  ab. Lösung ist der von CMake selbst genannte Schalter
  `-DCMAKE_POLICY_VERSION_MINIMUM=3.5`.
* Die GPU-Variante bricht ab: `nvcc error: 'cudafe++' died with status
  0xC0000005 (ACCESS_VIOLATION)`. CUDA 12.8 verträgt sich nicht mit dem
  installierten MSVC 14.51 (Visual Studio 18). Die README sieht dafür die
  CPU-Variante vor; erzwungen über `-DCMAKE_CUDA_COMPILER=NOTFOUND`.

* **Der CPU-Pfad des Upstream ließ sich gar nicht übersetzen.** Bei 92 % bricht
  der Bau ab: `Viewer_skinning.cpp(303): error C2065: 'num_bytes': undeclared
  identifier`. Die Variable ist innerhalb von `#ifdef WITH_CUDA` deklariert, wird
  aber unterhalb davon **immer** an `animator_.update_mesh(...)` übergeben. Das
  ist ein Fehler im Upstream, kein Umgebungsproblem — ohne CUDA baut dieser Stand
  bei niemandem. Eine Zeile (`size_t num_bytes = 0;` vor den `#ifdef`) behebt es;
  die Originaldateien liegen als `*.original` daneben.

**Ergebnis: Es baut und läuft.** `build_cpu/skinning.exe`, 1.457.664 Bytes,
`[100%] Built target skinning`. Mit dem mitgelieferten Beispiel gestartet
(`skinning.exe ../data/male/male.ini`) öffnet sich das Fenster „Fast Projective
Skinning". Die Bildqualität habe ich **nicht** beurteilt — das ist Schritt 1 des
Vorschlags und gehört Edgar.

Die GPU-Variante ist damit **nicht** geprüft. Sie wäre die interessantere (die
Autoren nennen die CPU-Version für Kollisionen ausdrücklich langsam), braucht
aber ein MSVC, das zu CUDA 12.8 passt.

**Was mitgeliefert wird:** vier Beispiele, darunter ein männlicher Körper
(`data/male`), ein GUI-Editor zum Setzen der Gelenke, automatische Dezimierung
und Upsampling-Gewichte. Die Empfehlung der Autoren lautet „3000–5000 simulierte
Vertices" — bei 18.210 Punkten wird also ein grobes Netz simuliert und das feine
angezeigt, genau die Trennung, die die Szene ohnehin schon hat (Steuernetz 18.210
gegen Anzeigenetz 70.851).

**Der Haken, und er ist wichtig:** FPS ist eine **interaktive Anwendung, keine
Bibliothek**. Im Quelltext gibt es keinen Netz- oder Bildexport (geprüft in
`src/Viewer_skinning.cpp`, Tastenbelegung und `mesh/Mesh.h`). Für den
MP4-Weg müssten die Punkte je Bild herausgeschrieben werden — das ist eine
Ergänzung am fremden Code, kein Nachbau des Verfahrens, aber es ist Arbeit und
es bindet uns an GPL.

### 3.2 Newton: was volumetrisches Weichgewebe kostet

Newton ist aus dem Kleiderphysik-Auftrag bereits installiert und kann
tetraedrische Weichkörper (`add_soft_mesh`, Neo-Hookean, `SolverVBD`). Gemessen
auf der RTX PRO 4500 (`proben/probe_newton_fem.py`, `proben/fem_kosten.log`):

| Gitter | Punkte | Tetraeder | ms je Bild |
|---|---|---|---|
| 8×8×8 | 729 | 2.560 | 257 |
| 16×16×16 | 4.913 | 20.480 | 248 |
| 26×26×26 | 19.683 | 87.880 | 305 |
| 34×34×34 | 42.875 | 196.520 | 282 |

**Die Zeit hängt nicht an der Netzgröße** — 77-mal mehr Tetraeder kosten
dasselbe. Sie hängt allein an der Zahl der Solver-Durchgänge:

| Teilschritte × Iterationen | ms je Bild | ms je Durchgang |
|---|---|---|
| 10 × 10 | 271 | 2,71 |
| 5 × 5 | 86 | 3,44 |
| 1 × 5 | 34 | 6,77 |

Bei diesen Größen ist die GPU unterfordert; die Kosten sind Kernel-Startzeit. Für
den MP4-Export heißt das: 10 Sekunden Animation (600 Bilder) kosten bei 5×5
Durchgängen **52 Sekunden** — rund ein Zehntel dessen, was die Kleiderphysik für
Stoff braucht (dort 1.046 ms je Bild). **Nicht gemessen ist, ob 5×5 Durchgänge
für stabiles Weichgewebe ausreichen.**

Was fehlt, ist die Eingabe: Newton nimmt ein fertiges Tetraedernetz. Einen
Vernetzer (fTetWild, TetGen) gibt es in dieser Umgebung nicht.

---

## 4. Vorschlag

### Der Kern: FastProjectiveSkinning prüfen, bevor irgendetwas gebaut wird

Es ist der **einzige gefundene fertige Code, der aus genau unseren Eingaben —
Netz und Gelenkpositionen — die Wirkungen B *und* C erzeugt** und dabei ohne
Hautgewichte und ohne Tetraedernetz auskommt. Die Autoren beschreiben ihn als
„the first real-time skinning method to provide physics-based dynamic
deformations and full global collision handling"; er baut sich seine
Volumenschicht (Muskel/Fett) selbst und löst die Kollision Arm-gegen-Rumpf mit.
Das ist mehr, als Pose-Blendshapes je könnten, und es ist fertig.

Die nächsten Schritte in dieser Reihenfolge:

1. **Am mitgelieferten `male`-Beispiel ansehen**, ob das Ergebnis überzeugt.
   Das kostet einen Programmstart und entscheidet alles Weitere.
2. **Unsere Figur einspeisen:** Netz nach `.off`, eine Teilmenge des DEF-Skeletts
   (Rumpf und Gliedmaßen, rund 25 der 176 Knochen — die 49 Gesichtsknochen
   gehören nicht in einen Weichgewebs-Kollider) nach `.skel`. Beides sind
   Textformate; die Gelenkpositionen liegen in `def_skeleton.json`.
3. **Erst dann** über die Anbindung an Theatre reden — also über den Export der
   Punkte je Bild und die Ablage, wie sie die Kleiderphysik schon vorsieht.

### Falls FPS nicht überzeugt: der zweite Weg

**Blender**, mit der Kette, die im Projekt bereits steht. `HumanBody/collision/`
häutet den Körper je Bild in Blender, simuliert, schreibt `bake.npz` und rendert
MP4 — für Stoff. Für den Körper wäre es dieselbe Kette mit anderem Modifikator:
`CORRECTIVE_SMOOTH` (Baustelle A, die Gruppe liegt in den Daten) plus das
Jiggle-Physics-Addon (Baustelle C, backbar in Keyframes). Das ist unspektakulär,
aber jeder Baustein ist fertig und erprobt.

Was dieser Weg **nicht** liefert, ist B — die Muskelwölbung. Dafür bliebe nur,
Korrektiv-Shapekeys von Hand zu modellieren.

### Die SMPL-Schiene zum Vergleich

Edgars Vorschlag, SMPL parallel mitlaufen zu lassen, ist der richtige Prüfstand,
und er kostet fast nichts: `Smplkoerper.posieren` **rechnet die Korrektur
bereits**, sie wird nur nirgends abgerufen. Damit steht neben jedem Ergebnis am
HumanBody-Modell die Zahl, die ein trainiertes Modell an derselben Stelle
liefert — die Werte aus 2.3 sind genau das.

Eine **Übertragung der SMPL-Korrektur auf unser Netz** habe ich versucht und
lege sie hier offen, weil sie als naheliegende Abkürzung immer wieder auftauchen
wird: Sie funktioniert nicht gut genug. Mit Zuordnung über den nächsten Punkt
lagen die Punkte im Median 43,8 mm auseinander und die Korrektur wirkte in die
falsche Richtung (−18,2 statt −17,7 %). Nach Ausrichtung über die Gelenke und
Angleichung der Armhaltung sank die Zuordnung auf 12,7 mm Median, und die
Korrektur holte bei 90 Grad von −17,7 auf −15,5 % — also **12 % des Verlusts
statt der 65 %, die SMPL auf seinem eigenen Netz schafft**
(`proben/probe_uebertrag_posedirs.py`, `proben/probe_uebertrag2.py`). Beides
sind Wegwerf-Proben, kein Baustein.

---

## 5. Was ich ausdrücklich nicht vorschlage

* **Direct Delta Mush oder Dual Quaternion Skinning.** Sie beheben Baustelle A,
  die bei uns zur Hälfte gar nicht existiert (Twist-Segmente fangen den
  Candy-Wrapper ab, gemessen 0,0–0,2 %), und liefern laut ihren eigenen Autoren
  weder Volumen noch Sekundärbewegung. Für Three.js gibt es sie ohnehin nur als
  Community-Fragmente; der Vorschlag im Three.js-Repo (Issue 20324) ist offen.
* **STAR**, so gut es technisch wäre: „non-commercial scientific research
  purposes".
* **PhysSkin**, obwohl es das aktuellste Verfahren ist: Linux-Skripte, CUDA 11.8,
  ein vortrainierter Shape-Encoder und keine ausgewiesene Lizenz im Repo.
* **Feine Hautfalten als Geometrie.** Bei 4,1 mm Kantenlänge nicht darstellbar
  (siehe 2.4).
* **Eine Eigenimplementierung** irgendeines dieser Verfahren.

## 6. Offen — Entscheidungen, die Edgar treffen muss

1. **GPL.** FastProjectiveSkinning steht unter GPL; die Autoren bieten
   ausdrücklich eine andere Regelung an („In cases where the constraints of the
   Open Source license prevent you from using FastProjectiveSkinning, please
   contact us."). Ob das Projekt GPL-Code aufnehmen kann, weiß ich nicht — die
   Figuren gehen an Roomguest.
2. **Wo die Physik rechnet.** Wie bei der Kleiderphysik: offline beim MP4-Export
   (dann ist alles bezahlbar) oder live im Browser (dann bleibt nur die
   Feder-Knochen-Variante).
3. **Ob die SMPL-Modelldateien** unter der Forschungslizenz hier benutzt werden
   dürfen — sie liegen im Projekt (`VideoToBVH/models/smpl`), und der
   GarmentCode-Weg benutzt sie bereits.

## 7. Quellen

| | |
|---|---|
| Fast Projective Skinning, Komaritzan & Botsch, ACM MIG 2019 | `github.com/mbotsch/FastProjectiveSkinning`, geklont und gebaut |
| Direct Delta Mush Skinning and Variants, Le & Lewis, SIGGRAPH 2019 (EA SEED) | Foliensatz, `media.contentapi.ea.com/.../le2019-siggraph2019-direct-delta-mush-skinning-and-variants.pdf` |
| Real-Time Secondary Animation with Spring Decomposed Skinning, Akyürek et al., CGF 44 (2025) | `github.com/bartuakyurek/Spring-Decomposed-Skinning`, MIT, geklont |
| PhysSkin, CVPR 2026 | `github.com/zju3dv/PhysSkin` |
| STAR, Osman et al., ECCV 2020 | `github.com/ahmedosman/STAR` |
| SMPL-Modelllizenz / SMPL-Body (CC-BY) | `smpl.is.tue.mpg.de/license.html` |
| Newton 1.5.1, Soft-Body-Beispiele | installiert; `newton/examples/softbody/`, `newton/_src/sim/builder.py` |
| Blender Jiggle Physics (Fork von Wiggle 2) | `github.com/naelstrof/blender-jiggle-physics`, GPL-3 |
| `@pixiv/three-vrm-springbone` 3.5.5, MIT | npm |
| MB-Lab Corrective Smooth | `tools/MB-Lab/humanoid.py:1271` (lokal) |
| SoftSMPL, Santesteban et al., Eurographics 2020 | Projektseite, **kein Code** |

**Messungen** (alle in `proben/`, Protokolle daneben):

| Skript | misst |
|---|---|
| `probe_lbs_ist.py` | LBS-Artefakte am HumanBody-Netz |
| `probe_smpl_posedirs.py` | Größe der SMPL-Pose-Korrektur, ganzer Körper |
| `probe_vergleich_beuge.py` | LBS gegen Pose-Korrektur am selben Maß |
| `probe_newton_fem.py` | Kosten volumetrischer Simulation |
| `probe_uebertrag_posedirs.py`, `probe_uebertrag2.py` | Wegwerf-Proben zur Übertragung (gescheitert, siehe 4) |

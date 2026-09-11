# Plan: Stoffdynamik — Kleidung, die beim Gehen Falten wirft

Edgar, 10.09.2026: „Vorschlag für Dynamik wie MD das macht — das kann
meinetwegen gerechnet werden, wenn man eine Simulation als mp4 speichert im
Theatre-Modul."

Nichts davon ist gebaut. Das hier ist der Plan, mit dem Ist-Zustand, auf dem
er steht.

## 1. Was heute ist — gemessen und nachgelesen

**Der Stoff wird einmal drapiert und dann an die Knochen geklebt.** Die
Drapierung (`drapierlauf.py` → `pygarment.run_sim`) lässt den Stoff auf einen
STEHENDEN Körper fallen: 439 Bilder à 10 Teilschritte bei 60 Hz, bis er ruht
(gemessen 15,68 s, also **35,7 ms je Simulationsbild** bei 11.387 Punkten;
dazu 8,7 s Fixkosten: Import 3,48 s, Vernetzung 2,12 s, Ablage 3,13 s).
Danach bekommt jeder Stoffpunkt Knochengewichte vom nächsten Körperdreieck
(`Anziehen`), und beim Abspielen bewegt Linear Blend Skinning ihn mit — keine
Trägheit, kein Schwingen, keine neuen Falten. Das ist der Unterschied zu
Marvelous Designer, und er ist kein Fehler, sondern eine fehlende Stufe.

**Der bewegte Körper ist im Upstream schon angelegt — für einen anderen
Zweck.** Der Körper hängt als `wp.sim.Mesh` mit `body=-1` (ruhender Kollider)
im Modell (`garment.py` 178/222). Für das Body-Smoothing tauscht der Upstream
die Körperpunkte aber MITTEN IN DER SIMULATION aus:
`update_smooth_body_shape` (`garment.py` 402–416) kopiert neue Punkte in den
Gerätepuffer, startet `replace_mesh_points` und ruft `mesh.refit()`. Genau
das ist der Mechanismus, den ein animierter Körper braucht — je Bild neue
Punkte, refit, weiter.

**Der Theatre-Export läuft Bild für Bild, nicht in Echtzeit.** Beide Wege:

    Browser   Bildexport._bilderSammeln:  abspieler.zeitSetzen(t) → render →
              canvas.toBlob → POST /api/theatre/encode-frames/ → ffmpeg
    Server    bildfolgen_render.py (Playwright):
              page.evaluate("window.__theatreSetTime(t)") → screenshot → ffmpeg

Deshalb muss der Stoff NICHT in Echtzeit simuliert werden: Wenn zu jeder
Zeit `t` ein fertiges Stoffbild aus einer Ablage kommt, ist das Video richtig.
Das ist der Grund, warum der Vorschlag „offline rechnen, im Theatre als MP4"
genau passt.

**Theatre kennt die GarmentCode-Stücke nicht.** Kein Treffer für `gc_`,
`garmentcode` oder `rig_url` in `TheatreJS/src/`. Theatre lädt Kleidung nur
über `laden/kleidungsnetz.js` (`/api/character/garment/fit/`, die
MakeHuman-Assets). Wer heute im Theatre eine GarmentCode-Figur lädt, sieht sie
nackt.

**Die Bausteine für den Körper je Bild liegen bereit.** Der Retarget-Motor
(`humanbody_core/skeleton/retarget/motor.py`) liefert `Bewegungsspuren`:
`times`, je Rigify-Knochen die lokale Drehung je Bild, die Wurzelspur. Ein
Skinning-Kern in numpy existiert (`UMA_Python/haut.py`,
`Umahaut.verformen(punkte, gewichte, knochenindex, matrizen)`, über alle
Einflüsse vektorisiert). Die Gewichte des Steuernetzes (18.210 Punkte) sind
`skin_weights_base`.

**Was der Warp-Fork NICHT hat:** eine Geschwindigkeit für einen Kollider mit
`body=-1`. `create_soft_contacts` (`collide.py` 504–614) liest
`body_qd[shape_body]`; für einen körperlosen Shape ist das null. Der Stoff
sieht also einen Körper, der von Bild zu Bild springt, aber in jedem Bild
ruht — Reibung wirkt gegen eine stehende Fläche. Folge: Stoff wird geschoben,
aber nicht mitgenommen. Für Oberteile unkritisch (die hängen an Schultern),
für eine Hose beim Gehen möglicherweise sichtbar. Siehe Risiko 2.

## 2. Ziel

Für eine Animation im Theatre-Modul wird der GarmentCode-Stoff über die
Bewegung simuliert. Das Ergebnis liegt als Folge von Stoffbildern auf der
Platte; Theatre spielt sie beim Bildexport ab; das MP4 entsteht über den
vorhandenen Weg. Ohne die Ablage bleibt alles, wie es ist.

## 3. Die Kette

    Animation (BVH) ──┐
                      ├─ Retarget (vorhanden) ── lokale Drehungen je Bild
    Figur (Morphs) ───┘                                   │
                                          Körper je Bild: Weltmatrizen × Ruhelage,
                                          LBS auf dem Steuernetz (18.210) ─────┐
    Stück (drapiert, *_sim_rig.json) ─────────────────────────────────────────┤
                                                                               ▼
                                          Warp-Lauf (Unterprozess wie drapierlauf.py):
                                            Stoff ruht auf Körper Bild 0
                                            je Bild: Punkte tauschen, refit, run_frame
                                            Stoffpunkte je Ausgabebild sichern
                                                                               │
                                          <stück>_<fingerabdruck>.stoffbilder ◄┘
                                                                               │
    Theatre: Stück laden (neu) + Ablage laden; zeitSetzen(t) → Stoffbild ─────┘
             → render → MP4 (vorhanden, Browser wie Server)

## 4. Schritte — jeder mit Prüfpunkt

### Schritt 1 — GarmentCode-Stücke kommen ins Theatre

Voraussetzung für alles Weitere, und für sich allein schon ein Gewinn.

* `TheatreJS/src/laden/garmentcodestueck.js`: Liste `garmentcode` aus den
  Modelldaten lesen (dieselbe, die `GarmentcodeAblage` schreibt), `rig_url`
  holen, `GarmentcodeAnziehen.einhaengen` (vorhanden) an das Theatre-Skelett
  (`studio/skinner.js`) binden. Material aus `garmentcode_stoff.js`.
* Prüfpunkt: Stück bewegt sich mit der Figur wie in der Szene (LBS). Ruhe-Probe
  0,0 mm, Bewegung zwischen Bild 0 und 3,5 s im Mittel ~20–30 cm — die Zahlen,
  die in der Szene gemessen wurden (17,7–27,1 cm).

### Schritt 2 — Der Körper je Bild, auf dem Server

* `core/dienste/koerperbewegung.py`: Retarget-Motor fahren → `Bewegungsspuren`
  → je Bild Weltmatrix je Knochen (Rigify-Ruhelage aus `def_skeleton.json`,
  lokale Quaternionen aus den Spuren, Wurzelspur) → `Umahaut.verformen` auf
  dem Steuernetz mit `skin_weights_base`. Ausgabe `(Bilder, 18210, 3)`.
* Der Retarget ist teuer und wird bereits abgelegt (Fingerabdruck mit
  `REGELFASSUNG`); die Ablage wird wiederverwendet, nicht neu gerechnet.
* Prüfpunkt: Mit lauter Einheitsdrehungen kommt das Ruhenetz heraus
  (0,0 mm); die Bewegung Bild 0 → 3,5 s liegt im Mittel bei 28–36 cm, wie im
  Browser gemessen (`Eigenhaut`-Probe vom 07.09.2026). Weichen Server und
  Browser ab, stimmt die Bindepose nicht — genau die Falle, die bei UMA die
  Figur um 900 mm versetzt hat.

### Schritt 3 — Der Warp-Lauf mit bewegtem Körper

* `Assets/GarmentCode/dynamiklauf.py` — eigener Unterprozess in
  `python10_Garment`, aufgebaut wie `drapierlauf.py`. Auftrag: Stück
  (Spezifikation + Ergebnisordner), Körperbilder (Datei aus Schritt 2), fps.
* Ablauf im Prozess:
  1. Modell wie beim Drapieren bauen, Startlage des Stoffs = das drapierte
     Ergebnis (`*_sim.obj`), Körper = Bild 0 der Animation. **Einlaufphase**:
     Der Stoff wurde in A-Haltung drapiert, Bild 0 steht anders. Über
     N Bilder werden die Körperpunkte von der A-Haltung zu Bild 0
     interpoliert (Punkte tauschen + refit, wie `update_smooth_body_shape`),
     der Stoff folgt. N ist ein Parameter (Vorschlag 60 = 1 s); gemessen wird,
     ob er reicht.
  2. Je Animationsbild (60 Hz, die BVH-Bilder werden darauf interpoliert):
     Körperpunkte tauschen, `refit`, `run_frame`. Die Simulation läuft mit
     ihren 10 Teilschritten weiter.
  3. Je Ausgabebild (30 fps, also jedes zweite Simulationsbild) die
     Stoffpunkte sichern — in Projektkoordinaten, korrigiert wie heute
     (`Stoffkorrektur` ist rein geometrisch und läuft auf jedem Bild einzeln;
     ob sie je Bild bezahlbar ist, wird gemessen).
* Prüfpunkte, in dieser Reihenfolge:
  * **Ruhe-Probe:** Animation aus lauter Bild-0-Körpern → der Stoff darf sich
    nicht bewegen (< 1 mm über 3 s). Fällt das, ist es der Aufbau, nicht die
    Physik.
  * **Einlaufphase:** nach N Bildern Durchstich stoffseitig < 0,5 % (die
    Messlatte des Drapierwegs), Hautabstand in der Größenordnung des
    drapierten Stücks.
  * **Bewegung:** `Walk/01_01`, 3 s. Stoff bleibt am Körper (Durchstich je
    Bild < 0,5 %), Ärmel und Saum bewegen sich gegenläufig zur Bewegung
    (Trägheit) — das ist der Effekt, der gesucht ist. Gemessen als
    Verschiebung des Saums relativ zum Körper zwischen zwei Bildern.

### Schritt 4 — Ablage und Endpunkte

* `Assets/GarmentCode/stoffbilder.py`: Datei mit Kopf (Stück, Fingerabdruck
  der Figur inkl. Morphs, Animation, fps, Bildzahl, Punktzahl,
  `REGELFASSUNG`) und Punkten als float16. **Der Name trägt den
  Fingerabdruck** (`~/.claude/rules/artefakte-benennen.md`): Eine Ablage,
  die mehrere Läufe beschreiben, misst irgendwann etwas anderes, als ihr
  Kopf behauptet.
* `POST /api/garmentcode/dynamik/` startet den Lauf (Fortschritt über
  Fortschrittsrechnung, wie beim Bauen), `GET /api/garmentcode/dynamik/<name>/`
  liefert die Datei.
* Größe: 11.387 Punkte × 3 × 2 Byte = **68 KB je Bild**; 10 s bei 30 fps
  = 20 MB. Handhabbar, kein Streaming nötig.

### Schritt 5 — Wiedergabe im Theatre

* `TheatreJS/src/studio/stoffbild.js`: Ablage laden; bei `zeitSetzen(t)` die
  zwei Nachbarbilder wählen, linear mischen, in das Positionsattribut des
  Stücks schreiben, Normalen neu rechnen. Das Stück wird dafür vom
  SkinnedMesh zum Mesh im Figurraum — die Ablage IST die Bewegung.
* Weil Browser-Export und Playwright-Export beide über `zeitSetzen` gehen,
  ist das MP4 damit fertig. Keine Änderung am Kodierweg.
* Prüfpunkt: Bildexport 3 s → 90 Bilder; im Video bewegt sich der Saum
  gegenläufig zur Figur. Nebeneinander mit dem LBS-Stück (Schritt 1) als
  Beleg, dass es etwas anderes ist.

### Schritt 6 — Bedienung

* Im Export-Reiter des Theatre ein Kästchen **„Stoff simulieren (Warp)"** mit
  Balken. Ohne Häkchen läuft alles wie bisher (LBS aus Schritt 1). Die
  Ablage wird je Stück, Figur und Animation einmal gerechnet und danach
  wiederverwendet.

## 5. Was es kostet — abgeleitet, nicht geraten

| Posten | Grundlage | Ergebnis |
|---|---|---|
| Simulation, ruhender Körper | 35,7 ms je 60-Hz-Bild (gemessen 08.09.2026) | 1 s Animation ≈ 2,1 s |
| Fixkosten je Lauf | Import + Vernetzung + Ablage, gemessen | ≈ 8,7 s |
| Einlaufphase | 60 Bilder | ≈ 2,1 s |
| bewegter Körper | `refit` je Bild + mehr Kontakte — **nicht gemessen** | ich rechne mit Faktor 2 |
| **10 s Animation** | | **≈ 1 Minute**, zu messen in Schritt 3 |
| Körper je Bild (LBS) | 18.210 × 4 Einflüsse, numpy | Millisekunden je Bild (Schätzung; UMA mit 16.277 × 5 läuft „vektorisiert", ohne Zahl) |
| Ablage | 68 KB je Bild | 10 s = 20 MB |

Zum Vergleich: ein Drapierlauf kostet heute 22–60 s. Eine Sekunde Dynamik
kostet also etwa so viel wie das, was heute schon je Stück bezahlt wird.

## 6. Risiken, mit Gegenmittel

1. **Tunneln bei schnellen Bewegungen.** 10 Teilschritte je 1/60 s sind
   600 Hz. Bei 1 m/s Handgeschwindigkeit legt der Arm je Teilschritt 1,7 mm
   zurück — unter `body_collision_thickness` (2,5 mm). Gehen hält; Tanz
   (AIST) nicht sicher. Gegenmittel: Teilschritte je Lauf einstellbar, und
   die Durchstichzahl je Bild steht im Bericht.
2. **Reibung gegen einen stehenden Körper** (siehe oben). Gegenmittel, falls
   es sichtbar wird: `soft_contact_body_vel` im Fork aus der Differenz der
   Körperpunkte zweier Bilder füllen. Das ist ein Eingriff in
   `warp_fork/warp/sim/collide.py` — ~20 Zeilen, aber im Fork, deshalb
   bewusst NICHT in der ersten Fassung.
3. **Einlaufphase.** Von A-Haltung zu Bild 0 kann sich der Stoff verhaken
   (Ärmel am Arm). Gegenmittel: N erhöhen; im Zweifel den Stoff auf Bild 0
   NEU drapieren statt zu überblenden (kostet einen Drapierlauf, entfällt
   das Risiko).
4. **Selbstkollision** (Rock an Beinen) ist an
   (`enable_triangle_particle_collisions`) und kostet — bei Röcken mehr
   Kontakte je Bild als bei Oberteilen. Gemessen wird je Stück.
5. **Der Kollisionskörper ist das Steuernetz (18.210), das sichtbare ist
   unterteilt (70.851).** Beim Drapieren wird das mit der Stoffkorrektur gegen
   das sichtbare Netz aufgefangen (`ABSTAND_MM`). Je Bild ist das dieselbe
   geometrische Rechnung; wenn sie zu teuer wird, bleibt der bekannte
   Oberschenkel-Befund vom 08.09.2026 in einzelnen Bildern sichtbar.
6. **Die Ablage gilt für GENAU EINE Figurform.** Ein Reglerzug danach macht
   sie ungültig — deshalb der Morph-Fingerabdruck im Namen, und Theatre sagt
   „Ablage passt nicht zur Figur" statt still die alte zu spielen.

## 7. Optionen, die verworfen sind — und warum

* **Echtzeit im Browser** (eigener XPBD-Löser auf WebGPU): Wochen Arbeit,
  Qualität unter Warp, und fürs MP4 ohne Mehrwert — der Export läuft ohnehin
  Bild für Bild.
* **Magica Cloth in Unity**: der richtige Weg für Roomguest, weil dort im
  Spiel simuliert wird. Für das Video hier irrelevant; kann parallel laufen.
* **Marvelous Designer kaufen** (280 $/Jahr) und die Stoffbewegung als
  Alembic zurückholen: funktioniert, verlässt aber das eigene Werkzeug — und
  MD konstruiert nicht aus den Körpermaßen, das täte GarmentCode weiter.

## 8. Reihenfolge und Abbruchkriterien

1 → 2 → 3 (Ruhe-Probe zuerst) → 4 → 5 → 6. Schritt 1 ist auch dann sinnvoll,
wenn der Rest nicht kommt. Nach Schritt 3 steht die Entscheidung: Ist die
Bewegung bei `Walk/01_01` sichtbar besser als LBS und liegt die Rechenzeit für
10 s unter zwei Minuten, geht es weiter. Wenn nicht, ist das ein Ergebnis,
kein Scheitern — dann steht der Preis.

## 9. Was NICHT in der ersten Fassung ist

Mehrere Stücke gemeinsam (geht über die Schnittvereinigung, später), Haare,
der Export der Stoffbewegung nach Roomguest (Alembic, glTF trägt keine
Punktfolgen), Körpergeschwindigkeit im Kontakt (Risiko 2), und jede Form von
Echtzeit.

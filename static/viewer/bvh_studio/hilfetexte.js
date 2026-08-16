/**
 * Hilfetexte des BVH-Studios.
 *
 * Aus tools.js herausgeloest (Umbau 15.08.2026): Von den 1012 Zeilen dieser
 * Datei waren 845 Hilfetexte — die Werkzeuge selbst standen davor und dahinter.
 * Wer an der Glaettung arbeitet, muss keine HTML-Absaetze durchblaettern.
 */

export const HELP_CONTENT = {
    tracks: {
        title: 'Tracks',
        body: `
<p><b>BVH Studio</b> arbeitet mit verschiedenen Track-Typen in einer gemeinsamen Timeline:</p>
<h4 class="hilfe-untertitel"><i class="fas fa-running"></i> Animation</h4>
<ul>
<li>Enthält Skelett-Animationen (BVH-Dateien)</li>
<li>Clips aus der <b>BVH Bibliothek</b> per Doppelklick oder Drag & Drop hinzufügen</li>
<li>Clips können <b>verschoben</b> (Drag), <b>gesplittet</b> (S), <b>dupliziert</b> und <b>gelöscht</b> (Del) werden</li>
<li>Rechtsklick auf Clip für Kontextmenü</li>
<li>Standard-Modell: Rig2 (konfigurierbar in Einstellungen)</li>
</ul>
<h4 class="hilfe-untertitel hilfe-modell"><i class="fas fa-user"></i> Modell</h4>
<ul>
<li>Wird automatisch mit einem Animations-Track erstellt</li>
<li>Steuert welches 3D-Modell (Preset) für die Animation verwendet wird</li>
<li>Modell-Clips können verschiedene Presets haben (z.B. FemaleGarment, Rig2)</li>
</ul>
<h4 class="hilfe-untertitel hilfe-kamera"><i class="fas fa-video"></i> Kamera</h4>
<ul>
<li>Steuert die Kameraposition während der Wiedergabe</li>
<li>Keyframes setzen: <b>K</b> drücken oder Button im Eigenschaften-Tab</li>
<li>Zwischen Keyframes wird interpoliert (Linear / Smooth / Step)</li>
</ul>
<h4 class="hilfe-untertitel hilfe-licht"><i class="fas fa-lightbulb"></i> Licht</h4>
<ul>
<li>Erzeugt ein Punktlicht in der Szene</li>
<li>Position, Farbe und Intensität über Eigenschaften-Panel ändern</li>
<li>Keyframes für animiertes Licht</li>
</ul>
<h4 class="hilfe-untertitel hilfe-audio"><i class="fas fa-music"></i> Audio</h4>
<ul>
<li>Audio-Datei (MP3/WAV/OGG) laden und zur Timeline synchronisieren</li>
<li>Lautstärke, Fade In/Out und Offset konfigurierbar</li>
</ul>
<p class="hilfe-abstand"><b>Hinzufügen:</b> Klick auf "+ Hinzufügen" in der Toolbar, dann Typ wählen.</p>
<p><b>Löschen:</b> Track auswählen, dann Papierkorb-Button.</p>
`},
    camera: {
        title: 'Kamera',
        body: `
<h4 class="hilfe-titel">Kamera-Track Funktionen</h4>
<p>Der Kamera-Track steuert die 3D-Kamera über <b>Kamerapositionen</b> (Keyframes). Zwischen zwei Keyframes wird die Kamera interpoliert. Manuelle Bewegung ist auch während Play jederzeit möglich.</p>

<h4 class="hilfe-abschnitt">Maus-Steuerung in der 3D-Szene (OrbitControls)</h4>
<table class="hilfe-tabelle hilfe-tabelle-klein">
<tr class="hilfe-trennlinie"><td class="hilfe-zelle hilfe-breit"><b>Links-Drag</b></td><td>Rotieren um Mittelpunkt</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-zelle"><b>Rechts-Drag</b></td><td>Kamera verschieben (Pan)</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-zelle"><b>Mausrad</b></td><td>Zoomen</td></tr>
<tr><td class="hilfe-zelle"><b>Middle-Drag</b></td><td>Dolly (Zoom)</td></tr>
</table>

<h4 class="hilfe-abschnitt">Kameraposition setzen (Keyframe)</h4>
<ol>
<li>Kamera-Track in der Timeline auswählen</li>
<li>Kamera mit Maus in die gewünschte Position bewegen</li>
<li><b>Rechtsklick</b> in Kamera-Spur auf Klick-Position → <b>Hinzufügen → Kameraposition</b></li>
<li>Alternativ: <b>K</b> drücken (speichert am Playhead) oder "Keyframe setzen" Button im Eigenschaften-Panel</li>
</ol>

<h4 class="hilfe-abschnitt">Keyframe bearbeiten</h4>
<p>Klick auf einen Keyframe (Raute ◇) in der Timeline. Im Eigenschaften-Panel erscheinen:</p>
<ul>
<li><b>Position X/Y/Z</b> — Kameraposition in Metern</li>
<li><b>Rotation X/Y/Z</b> — Kamerarotation in Grad</li>
<li><b>FOV</b> — Sichtfeld (10-120 Grad)</li>
<li><b>Interpolation</b> — Linear / Smooth (weich) / Step (sprunghaft)</li>
<li><b>"Aktuelle Ansicht übernehmen"</b> — überschreibt den Keyframe mit der aktuellen Kameraansicht</li>
</ul>

<h4 class="hilfe-abschnitt">Wiedergabe</h4>
<p>Bei <b>Play</b> interpoliert die Kamera zwischen den Keyframes. Die Maussteuerung bleibt aktiv — du kannst jederzeit manuell die Kamera bewegen (ab dem nächsten Keyframe nimmt die Interpolation wieder die Kontrolle).</p>
<p><b>"Aktiv" Checkbox</b>: Deaktivieren um den Kamera-Track temporär zu ignorieren.</p>
`},
    light: {
        title: 'Licht',
        body: `
<div class="hilfe-kasten">
  <h4 class="hilfe-kasten-titel"><i class="fas fa-hand-pointer"></i> Licht verschieben — Kurz-Anleitung</h4>
  <ol class="hilfe-liste">
    <li><b>Licht auswählen</b>: Klick auf den gelben Kegel im 3D-Viewport <i>oder</i> auf den Timeline-Header (z.B. "Key Light")</li>
    <li><b>An neue Position setzen</b>: <kbd class="hilfe-taste">Alt</kbd> + <b>Links-Klick</b> irgendwo in die 3D-Szene — das Licht springt dorthin</li>
    <li><b>Feinjustage</b>: X/Y/Z-Zahlen-Inputs im Properties-Panel rechts</li>
    <li><b>Ausrichtung</b>: Ziel (Blickrichtung) X/Y/Z im Properties-Panel — Licht zeigt Richtung Target</li>
  </ol>
  <p class="hilfe-fussnote"><i class="fas fa-info-circle"></i> Middle-Maus/Rechtsklick sind von OrbitControls (Zoom/Pan) belegt — daher <b>Alt+Klick</b>. <b>Alt+Drag</b> rotiert weiterhin die Szene (Drag ≠ Click).</p>
</div>

<h4 class="hilfe-titel">Licht-System Übersicht</h4>
<p>In der Timeline sind alle Lichter unter dem Gruppen-Header <b>"Licht"</b> zu sehen:</p>
<ul>
<li><b>Szenen-Lichter</b> (Key, Fill, Back, Ambient) — automatisch angelegt, nicht löschbar</li>
<li><b>User-Lichter</b> — eigene SpotLights (via Toolbar Hinzufügen → Spur → Licht)</li>
<li><b>Theatre-Presets</b> — via Toolbar-Dropdown "Theatre" (z.B. Ballett, Jazz, Club)</li>
</ul>
<p>Unterstützte Typen: <b>SpotLight</b>, <b>DirectionalLight</b>, <b>PointLight</b>, <b>AmbientLight</b>. Properties-Panel zeigt nur die relevanten Felder je Typ.</p>

<h4 class="hilfe-abschnitt">Alle Maus-Bindings für Lichter</h4>
<table class="hilfe-tabelle hilfe-tabelle-klein">
<tr class="hilfe-trennlinie"><td class="hilfe-zelle hilfe-breit"><b>Links-Klick auf Licht-Kegel (3D)</b></td><td>Licht-Track auswählen</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-zelle"><b>Klick auf Timeline-Header</b></td><td>Licht-Track auswählen</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-zelle hilfe-warnung"><b>Alt + Links-Klick in 3D</b></td><td class="hilfe-warnung"><b>Licht hier platzieren</b> (Raycast gegen Mesh, Fallback Boden)</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-zelle"><b>Properties X/Y/Z</b></td><td>Position exakt per Zahl</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-zelle"><b>Properties Ziel X/Y/Z</b></td><td>Blickrichtung (wo das Licht hinzeigt)</td></tr>
<tr><td class="hilfe-zelle"><b>Rechts-Drag im Viewport</b></td><td>Kamera pannen (nicht Licht — für Licht → Alt+Klick)</td></tr>
</table>

<h4 class="hilfe-abschnitt">Licht konfigurieren (Properties-Panel)</h4>
<ul>
<li><b>Aus</b> (Checkbox) — schaltet das Licht in der Szene aus</li>
<li><b>Farbe</b> — Color-Picker ODER RGB-Slider (bidirektional verknüpft)</li>
<li><b>Intensität</b> — 0-20</li>
<li><b>Winkel</b> (nur SpotLight) — Ausstrahlungswinkel in Grad (1-170)</li>
<li><b>Penumbra</b> (nur SpotLight) — weicher Rand 0-1</li>
<li><b>Reichweite</b> (Spot/Point) — Fall-off-Distanz</li>
<li><b>Helper zeigen</b> — blendet den Wireframe-Kegel + soliden Ursprungs-Kegel ein/aus</li>
<li><b>Ziel (Blickrichtung)</b> — X/Y/Z wohin das Licht zeigt</li>
</ul>

<h4 class="hilfe-abschnitt">Licht-Keyframes</h4>
<ol>
<li>Licht-Track auswählen</li>
<li>Playhead an gewünschte Frame bewegen, Licht konfigurieren (Position, Farbe, Intensität...)</li>
<li><b>Rechtsklick</b> in Licht-Spur → <b>Hinzufügen → Licht</b> (an Klick-Position im Track)</li>
<li>Alternativ: <b>K</b> drücken (am Playhead) oder Button "Keyframe setzen"</li>
<li>Bei 2+ Keyframes: Wiedergabe interpoliert Position, Farbe, Intensität, Winkel, Penumbra, Reichweite</li>
</ol>

<h4 class="hilfe-abschnitt">Helper-Visualisierung</h4>
<p>Jedes Licht (außer Ambient) zeigt in der 3D-Szene:</p>
<ul>
<li><b>Kegel-Wireframe</b> (SpotLight) bzw. Pfeil (DirectionalLight) bzw. Kugel (PointLight) — Abstrahlung/Richtung</li>
<li><b>Solider kleiner Kegel</b> am Licht-Ursprung, Farbe = Lichtfarbe, Spitze zeigt zum Target</li>
</ul>
`},
    audio: {
        title: 'Audio',
        body: `
<h4 class="hilfe-titel">Audio-Track Funktionen</h4>
<p>Audio-Tracks synchronisieren Audiodateien zur Timeline-Wiedergabe.</p>

<h4 class="hilfe-abschnitt">Audio laden</h4>
<ol>
<li>Audio hinzufügen (+ Hinzufügen > Audio)</li>
<li>Im Eigenschaften-Tab: "Audio laden" Button klicken</li>
<li>MP3, WAV oder OGG Datei auswählen</li>
<li>Der Audio-Clip erscheint als grünes Rechteck in der Timeline</li>
</ol>

<h4 class="hilfe-abschnitt">Audio bearbeiten</h4>
<p>Klick auf den Audio-Clip in der Timeline. Im Eigenschaften-Panel:</p>
<ul>
<li><b>Lautstärke</b> — Schieberegler 0-100%</li>
<li><b>Fade In</b> — Einblende-Dauer in Frames</li>
<li><b>Fade Out</b> — Ausblende-Dauer in Frames</li>
<li><b>Offset</b> — Startpunkt innerhalb der Audiodatei (Sekunden)</li>
<li><b>Start</b> — Position auf der Timeline (Frame)</li>
</ul>

<h4 class="hilfe-abschnitt">Wiedergabe</h4>
<p>Audio wird automatisch zur Timeline synchronisiert. Bei <b>Play</b> startet die Audiowiedergabe am aktuellen Playhead. Bei <b>Pause/Stop</b> wird die Audiowiedergabe gestoppt.</p>
<p>Audio-Clips können wie BVH-Clips <b>verschoben</b> und <b>gelöscht</b> werden.</p>
`},
    shortcuts: {
        title: 'Tastenkürzel',
        body: `
<table class="hilfe-tabelle">
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd class="hilfe-taste">Space</kbd></td><td>Play / Pause</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd class="hilfe-taste">&#8592;</kbd> <kbd class="hilfe-taste">&#8594;</kbd></td><td>Frame vor / zurück</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd class="hilfe-taste">S</kbd></td><td>Clip splitten am Playhead</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd class="hilfe-taste">Del</kbd></td><td>Ausgewählten Clip löschen</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd class="hilfe-taste">K</kbd></td><td>Kamera/Licht Keyframe setzen</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd class="hilfe-taste">Ctrl+Shift+U</kbd></td><td>Undo (bis zu 20 Schritte)</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd class="hilfe-taste">Redo</kbd></td><td>Redo (nur per Button)</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><b>Mausrad</b></td><td>Timeline scrollen</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><b>Ctrl + Mausrad</b></td><td>Timeline zoomen</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><b>Mittlere Maustaste</b></td><td>Timeline pannen</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><b>Alt + Klick</b></td><td>Timeline pannen</td></tr>
<tr><td class="hilfe-feld"><b>Rechtsklick auf Clip</b></td><td>Kontextmenü</td></tr>
</table>
`},
    animations: {
        title: 'BVH Bibliothek verwalten',
        body: `
<h4 class="hilfe-titel">BVH Bibliothek im Studio</h4>
<p>Die BVH Bibliothek links zeigt alle BVH-Dateien gruppiert nach Ordnern. Animationen können per <b>Doppelklick</b> oder <b>Drag &amp; Drop</b> zum ausgewählten Track hinzugefügt werden.</p>

<h4 class="hilfe-abschnitt">Bibliothek-Toolbar</h4>
<table class="hilfe-tabelle">
<tr class="hilfe-trennlinie"><td class="hilfe-zelle hilfe-mitte hilfe-schmal"><i class="fas fa-folder-plus"></i></td><td><b>Neuer Ordner</b> — Erstellt einen neuen Kategorie-Ordner</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-zelle hilfe-mitte"><i class="fas fa-pen"></i></td><td><b>Umbenennen</b> — Benennt die ausgewählte Animation um</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-zelle hilfe-mitte"><i class="fas fa-trash"></i></td><td><b>Löschen</b> — Löscht die ausgewählte Animation</td></tr>
<tr><td class="hilfe-zelle hilfe-mitte"><i class="fas fa-sync-alt"></i></td><td><b>Aktualisieren</b> — Lädt die Bibliothek neu</td></tr>
</table>

<h4 class="hilfe-abschnitt">Kontextmenü (Rechtsklick)</h4>
<p><b>Auf eine Animation:</b></p>
<ul class="hilfe-zeile">
<li><b>Zur Animation hinzufügen</b> — Fügt die Animation als Clip zur ausgewählten Animation hinzu</li>
<li><b>Umbenennen</b> — Ändert den Dateinamen der BVH-Datei</li>
<li><b>Verschieben nach...</b> — Verschiebt die Datei in einen anderen Ordner</li>
<li><b>Löschen</b> — Entfernt die BVH-Datei (mit Bestätigung)</li>
</ul>
<p><b>Auf einen Ordner:</b></p>
<ul class="hilfe-zeile">
<li><b>Ordner umbenennen</b> — Ändert den Ordnernamen</li>
<li><b>Neuer Ordner</b> — Erstellt einen neuen Ordner</li>
<li><b>Ordner löschen</b> — Entfernt einen leeren Ordner</li>
</ul>

<h4 class="hilfe-abschnitt">Animation hinzufügen</h4>
<ul class="hilfe-zeile">
<li><b>Doppelklick</b> auf eine Animation — fügt sie zum ausgewählten Track hinzu</li>
<li><b>Drag &amp; Drop</b> — ziehe eine Animation auf einen Track-Header oder in die Timeline</li>
<li>Wird auf leere Stelle in der Timeline gezogen, wird automatisch ein neuer Track erstellt</li>
</ul>

<h4 class="hilfe-abschnitt">Clips in der Timeline bearbeiten</h4>
<p>Clips können direkt in der Timeline per Maus bearbeitet werden:</p>
<ul class="hilfe-zeile">
<li><b>Verschieben</b> — Clip in der Mitte greifen und nach links/rechts ziehen</li>
<li><b>Trimmen (Anfang)</b> — Linken Rand des Clips greifen und ziehen → kürzt die Animation von vorne</li>
<li><b>Trimmen (Ende)</b> — Rechten Rand des Clips greifen und ziehen → kürzt die Animation von hinten</li>
<li>Der Cursor wechselt zu <b>↔</b> am Clip-Rand und zu <b>✋</b> in der Mitte</li>
</ul>
<p><b>Kontextmenü (Rechtsklick auf Clip):</b></p>
<ul class="hilfe-zeile">
<li><b>Split an Playhead (S)</b> — Teilt den Clip an der Playhead-Position</li>
<li><b>Duplizieren</b> — Erstellt eine Kopie hinter dem Clip</li>
<li><b>Löschen (Del)</b> — Entfernt den Clip</li>
<li><b>Anfang trimmen (+10f)</b> — Kürzt den Clip um 10 Frames von vorne</li>
<li><b>Ende trimmen (+10f)</b> — Kürzt den Clip um 10 Frames von hinten</li>
<li><b>Trim zurücksetzen</b> — Stellt die volle Länge wieder her</li>
<li><b>BVH speichern unter...</b> — Speichert die BVH-Datei</li>
<li><b>Smooth / Bodenniveau</b> — Tools auf den Clip anwenden</li>
</ul>

<h4 class="hilfe-abschnitt">Hinweise</h4>
<ul class="hilfe-zeile">
<li>Klick auf eine Animation markiert sie (lila) für Toolbar-Aktionen</li>
<li>Ordner können nur gelöscht werden wenn sie leer sind</li>
<li>Beim Umbenennen/Verschieben wird auch die Retarget-Cache-Datei (.json) mitverschoben</li>
<li>Alle Änderungen werden sofort auf der Festplatte ausgeführt</li>
<li>Wird der letzte Clip eines Tracks gelöscht, verschwindet das 3D-Modell automatisch</li>
</ul>
`},

    export: {
        title: 'Export mit Cloth-Simulation',
        body: `
<p>Das Studio kann Animationen als <b>MP4</b> exportieren. Beim Export
kann zusätzlich eine <b>Cloth-Simulation</b> laufen, die Durchstöße
verhindert (z.B. Bein durchs Rock-Modell). Die Sim läuft auf deiner
RTX 3060 wenn möglich.</p>

<h4 class="hilfe-untertitel"><i class="fas fa-cogs"></i> Bedienung (&uuml;ber das UI)</h4>
<ol>
<li><b>Szene vorbereiten:</b> Im Szenen-Editor ein generiertes Modell laden (z.B. <code>TriadischRock</code>) und eine BVH-Animation zuweisen (z.B. AIST <code>d01_mJS3_ch07</code>). Setze das Modell + die Animation ggf. als Default in <i>Einstellungen &rarr; Szene</i>.</li>
<li><b>Kleidungs-Bones markieren:</b> Im Szenen-Editor &rarr; Tab <b>Modell</b> pro Bone die Checkbox <b>&bdquo;Kleidungsst&uuml;ck&ldquo;</b>. Standard-aktiv bei <code>skirt</code>, <code>tutu</code>, <code>spiral_tutu</code>, <code>helix_ribbon</code>. Nur diese werden simuliert, der Rest bleibt rigid und dient als Kollisions-K&ouml;rper.</li>
<li><b>Export-Tab &ouml;ffnen:</b> Im BVH Studio rechts oben &rarr; Tab <b>Export1</b>.</li>
<li><b>Parameter setzen:</b> Dauer (Sekunden), FPS, Qualit&auml;t (low/medium/high).</li>
<li><b>Engine-Button klicken:</b> einer der drei Buttons (Blender Cloth, Warp+Blender, Warp pur). Der Szenen-Editor wird automatisch in einem Popup ge&ouml;ffnet, die Sim + Render l&auml;uft, und die fertige MP4 wird nach Abschluss in einem neuen Tab ge&ouml;ffnet.</li>
<li>Die MP4 landet zus&auml;tzlich unter <code>media/cloth_exports/</code>.</li>
</ol>
<p class="hilfe-beispiel">
<b>Tipp:</b> Die Szenen-Popup bleibt offen — so kannst du zwischen den drei Engines vergleichen, ohne jedes Mal neu laden zu m&uuml;ssen.
</p>

<h4 class="hilfe-abschnitt hilfe-audio"><i class="fas fa-video"></i> Engine 1 &mdash; <code>blender_eevee</code></h4>
<p>Blender Cloth-Simulation (CPU) + EEVEE-Render (GPU). Stabilste Qualit&auml;t, keine CUDA n&ouml;tig f&uuml;r die Sim, nur f&uuml;r's Rendering.</p>
<ul>
<li><b>Sim:</b> CPU, Blender 5.0 Cloth-Modifier, Bake vor Render</li>
<li><b>Render:</b> EEVEE-Next, GPU (RTX 3060 via OptiX)</li>
<li><b>Zeit (5s @ 30fps):</b> Sim 30&ndash;75s + Render 15s &asymp; <b>1 min</b></li>
<li><b>Qualit&auml;t:</b> ⭐⭐⭐⭐ (mature Cloth-Physik, sch&ouml;ne Falten)</li>
<li><b>Vorteil:</b> Robust, deterministisch, Blender-Standard</li>
<li><b>Nachteil:</b> Langsamste Sim</li>
</ul>

<h4 class="hilfe-abschnitt hilfe-kamera"><i class="fas fa-rocket"></i> Engine 2 &mdash; <code>warp_blender</code></h4>
<p><b>Empfohlen f&uuml;r Produktion.</b> NVIDIA Warp auf CUDA f&uuml;r die Sim + Blender EEVEE f&uuml;rs Rendering.</p>
<ul>
<li><b>Sim:</b> NVIDIA Warp 1.4.2 auf RTX 3060 (CUDA Kernels, Spring-Cloth + SDF-Collider)</li>
<li><b>Render:</b> Blender EEVEE-Next (liest den Sim-Bake und rendert Frame-f&uuml;r-Frame)</li>
<li><b>Zeit (5s @ 30fps):</b> Sim 5&ndash;15s + Render 15s &asymp; <b>30s</b></li>
<li><b>Qualit&auml;t:</b> ⭐⭐⭐⭐⭐ (Warp-Physik + Blender-Render-Qualit&auml;t)</li>
<li><b>Vorteil:</b> 5-10&times; schneller als Engine 1 bei gleicher Qualit&auml;t</li>
<li><b>Nachteil:</b> Zwei Subprocesses (Python3.10 f&uuml;r Warp, Blender f&uuml;r Render)</li>
</ul>

<h4 class="hilfe-abschnitt hilfe-modell"><i class="fas fa-bolt"></i> Engine 3 &mdash; <code>warp_only</code></h4>
<p>Komplett auf Warp + pyrender, kein Blender. Schnellste end-to-end Pipeline.</p>
<ul>
<li><b>Sim:</b> NVIDIA Warp auf CUDA (wie Engine 2)</li>
<li><b>Render:</b> pyrender Offscreen-OpenGL via verstecktes pyglet-Fenster (GPU)</li>
<li><b>Zeit (5s @ 30fps):</b> Sim 5&ndash;15s + Render 5&ndash;10s &asymp; <b>20s</b></li>
<li><b>Qualit&auml;t:</b> ⭐⭐⭐ (einfacheres Material/Shading als EEVEE)</li>
<li><b>Vorteil:</b> Schnellste Pipeline, keine Blender-Dependency</li>
<li><b>Nachteil:</b> Render ist Basic (flat lit, Vertex-Colors, keine Shadows)</li>
</ul>

<h4 class="hilfe-abschnitt hilfe-animation"><i class="fas fa-tools"></i> Technischer Unterbau</h4>
<ul>
<li><b>Splitter:</b> Der merged-Body wird anhand <code>boneVertexRanges</code> + <code>is_garment</code>-Flag in Cloth-Segmente + Rigid-Collider aufgeteilt. Pro Cloth-Segment werden die obersten ~12% der Verts als <b>Pin-Group</b> bestimmt (folgen dem Bone-Head beim Tanz, statt frei zu fliegen).</li>
<li><b>Pipeline-Code:</b> <code>A:/3DTools/HumanBody/collision/</code></li>
<li><b>Server-Endpoint:</b> POST <code>/api/cloth/export/</code></li>
<li><b>Python-Envs:</b> Warp-Sim l&auml;uft in <code>A:/3DTools/python10</code> (braucht Python 3.10 + Warp 1.4.2 f&uuml;r <code>warp.sim</code>). Django + pyrender in <code>A:/3DTools/python14</code>.</li>
<li><b>Qualit&auml;t-Stufen:</b> steuern Sim-Iterationen pro Frame sowie Render-Samples. <i>low</i> = 16 Substeps/32 Samples, <i>medium</i> = 32/64, <i>high</i> = 64/128.</li>
</ul>

<h4 class="hilfe-abschnitt">Troubleshooting</h4>
<ul>
<li><b>&bdquo;warp_sim failed&ldquo;:</b> Warp braucht CUDA. Pr&uuml;fe <code>nvidia-smi</code>. Warp-Cache beim ersten Run &asymp; 20s Kompilierung normal.</li>
<li><b>&bdquo;blender not found&ldquo;:</b> Blender 5.0 muss unter <code>C:/Program Files/Blender Foundation/Blender 5.0/</code> liegen.</li>
<li><b>Cloth klebt am K&ouml;rper:</b> Erh&ouml;he <i>quality</i> auf <code>high</code> oder erh&ouml;he den Bone-Radius.</li>
<li><b>Rock fliegt weg:</b> Pin-Group zu klein. Nur Bones mit genug Verts am Head funktionieren (Helix-Ribbon mit <code>spiralSkirt:true</code> ist ideal).</li>
</ul>
`},
};

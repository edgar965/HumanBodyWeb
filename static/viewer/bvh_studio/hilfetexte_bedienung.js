/**
 * Hilfetexte des BVH-Studios: Bedienung, Animationen und Export.
 *
 * Aus `hilfetexte.js` geteilt (Umbau 18.08.2026, 329 Zeilen). Hier stehen die
 * Tastenkuerzel, die Arbeit mit Animationen und der Videoexport.
 */

export const HILFE_BEDIENUNG = {
    shortcuts: {
        title: 'Tastenkürzel',
        body: `
<table class="hilfe-tabelle doku">
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
<table class="hilfe-tabelle doku">
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

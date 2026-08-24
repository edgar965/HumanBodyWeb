/**
 * Hilfetexte des BVH-Studios: die Spurarten.
 *
 * Aus `hilfetexte.js` geteilt (Umbau 18.08.2026, 329 Zeilen). Hier stehen die
 * vier Spurarten — Animation, Kamera, Licht, Audio. Reiner Inhalt, kein Code:
 * `hilfefenster.js` sucht sich den Abschnitt über seinen Schluessel.
 */

export const HILFE_SPUREN = {
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
};

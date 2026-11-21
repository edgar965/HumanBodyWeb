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
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd class="hilfe-taste">Space</kbd></td><td>Play / Pause
    (Abspielleiste unten links bei der BVH Bibliothek; <b>Endlos</b> lässt das Video am Ende der letzten
    Animation von vorn laufen, sonst hält es dort an)</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd class="hilfe-taste">&#8592;</kbd> <kbd
    class="hilfe-taste">&#8594;</kbd></td><td>Frame vor / zurück</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd class="hilfe-taste">Pos1</kbd> <kbd
    class="hilfe-taste">Ende</kbd></td><td>Zum Anfang / zum Ende der letzten Animation springen</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd
    class="hilfe-taste">S</kbd></td><td>Clip splitten am Playhead</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd
    class="hilfe-taste">Del</kbd></td><td>Ausgewählten Clip löschen</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd
    class="hilfe-taste">K</kbd></td><td>Kamera/Licht Keyframe setzen</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd class="hilfe-taste">Ctrl+Z</kbd> <kbd
    class="hilfe-taste">Ctrl+Shift+U</kbd></td><td>Undo (bis zu 20 Schritte)</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-feld"><kbd class="hilfe-taste">Ctrl+Y</kbd> <kbd
    class="hilfe-taste">Ctrl+Shift+Z</kbd></td><td>Redo</td></tr>
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
<p>Die BVH Bibliothek links zeigt alle BVH-Dateien gruppiert nach Ordnern. Animationen können per <b>Doppelklick</b>
    oder <b>Drag &amp; Drop</b> zum ausgewählten Track hinzugefügt werden.</p>

<h4 class="hilfe-abschnitt">Bibliothek-Toolbar</h4>
<table class="hilfe-tabelle doku">
<tr class="hilfe-trennlinie"><td class="hilfe-zelle hilfe-mitte hilfe-schmal"><i
    class="fas fa-folder-plus"></i></td><td><b>Neuer Ordner</b> — Erstellt einen neuen Kategorie-Ordner</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-zelle hilfe-mitte"><i
    class="fas fa-pen"></i></td><td><b>Umbenennen</b> — Benennt die ausgewählte Animation um</td></tr>
<tr class="hilfe-trennlinie"><td class="hilfe-zelle hilfe-mitte"><i
    class="fas fa-trash"></i></td><td><b>Löschen</b> — Löscht die ausgewählte Animation</td></tr>
<tr><td class="hilfe-zelle hilfe-mitte"><i
    class="fas fa-sync-alt"></i></td><td><b>Aktualisieren</b> — Lädt die Bibliothek neu</td></tr>
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
<li><b>Standbild einfügen (B)</b> — Friert die Pose an der Playhead-Position für ein paar Sekunden ein
    (Länge über das Kontextmenü „Länge"); Kamera und Licht laufen dabei auf ihren eigenen Spuren
    normal weiter, nur die Figur hält still. Taste B wirkt bei ausgewählter Animationsspur, auch
    ohne Rechtsklick</li>
<li><b>Duplizieren</b> — Erstellt eine Kopie hinter dem Clip</li>
<li><b>Löschen (Del)</b> — Entfernt den Clip</li>
<li><b>Anfang trimmen (+10f)</b> — Kürzt den Clip um 10 Frames von vorne</li>
<li><b>Ende trimmen (+10f)</b> — Kürzt den Clip um 10 Frames von hinten</li>
<li><b>Trim zurücksetzen</b> — Stellt die volle Länge wieder her</li>
<li><b>BVH speichern unter...</b> — Lädt die BVH-Datei (mit Trim) auf die eigene Platte herunter; der Clip im Projekt bleibt unverändert</li>
<li><b>In Bibliothek speichern unter...</b> — Legt den (getrimmten) Clip als neue Datei in der BVH-Bibliothek ab; der Clip im Projekt zeigt danach auf diese neue Datei</li>
<li><b>Smooth / Bodenniveau</b> — Tools auf den Clip anwenden</li>
</ul>
<p><b>Geschwindigkeitskurve</b> (Eigenschaften-Panel eines BVH-Clips): Punkte am Abspielkopf
setzen, die einen Zeitanteil des Clips auf einen Quellanteil biegen — ohne Punkte läuft der Clip
mit konstanter Geschwindigkeit (Speed-Regler) weiter. Zwei Punkte mit demselben Wert halten die
Bewegung dazwischen weich an; „weich" als Interpolation rundet den Übergang.</p>

<h4 class="hilfe-abschnitt">Effekte-Spur — Speed-Ereignisse (Taste G)</h4>
<p>Eine eigene Spurart „Effekte" (Hinzufügen → Spur → Effekte), mit einer BVH-Spur verknüpft
(Rechtsklick auf die Effekte-Spur → Verknüpfung). Sie schneidet die Animation NICHT durch: Auf
der verknüpften Animationsspur setzt <b>Taste G</b> am Abspielkopf ein Speed-Ereignis mit dem
aktuell eingestellten Wiedergabetempo (Schieberegler neben der Zeitanzeige, 0–3×, stufenlos).
Zwischen zwei Ereignissen wird das Tempo interpoliert; 0× ist ein Standbild — am Ende des Balkens
läuft die Animation von genau der Stelle weiter, an der sie am Anfang stand. Vor dem ersten und
nach dem letzten Ereignis gilt normales Tempo (1×). Steht ein Balken irgendwo auf der Spur, dehnt
oder staucht das die Animation dort — spätere Clips derselben BVH-Spur rutschen sichtbar mit,
ohne dass ein Clip geteilt oder verändert wird; Kamera, Licht und Ton laufen unabhängig davon auf
ihren eigenen Spuren weiter.</p>

<h4 class="hilfe-abschnitt">Hinweise</h4>
<ul class="hilfe-zeile">
<li>Klick auf eine Animation markiert sie (lila) für Toolbar-Aktionen</li>
<li>Ordner können nur gelöscht werden wenn sie leer sind</li>
<li>Beim Umbenennen/Verschieben wird auch die Retarget-Cache-Datei (.json) mitverschoben</li>
<li>Alle Änderungen werden sofort auf der Festplatte ausgeführt</li>
<li>Wird der letzte Clip eines Tracks gelöscht, verschwindet das 3D-Modell automatisch</li>
</ul>
`},
};

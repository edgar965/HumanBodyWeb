/**
 * BVH Studio — Toolbar, Help system, Gaussian Smooth, Ground Fix.
 */
import * as THREE from 'three';
import { state } from './state.js';
import { fn } from './registry.js';
import { undo, redo, pushUndo } from './undo.js';

// Gaussian Smooth (session-wide toggle)
export const _gaussSmooth = { active: false, sigma: 2.0, origClips: new Map() };

export function setupToolbar() {
    // Track dropdown
    const trackDD = document.getElementById('track-dropdown');
    document.getElementById('btn-add-track')?.addEventListener('click', (e) => { e.stopPropagation(); trackDD?.classList.toggle('open'); });
    document.getElementById('dd-add-bvh')?.addEventListener('click', () => { trackDD?.classList.remove('open'); fn.addTrack(); });
    document.getElementById('dd-add-camera')?.addEventListener('click', () => { trackDD?.classList.remove('open'); fn.addSpecialTrack('camera'); });
    document.getElementById('dd-add-light')?.addEventListener('click', () => { trackDD?.classList.remove('open'); fn.addSpecialTrack('light'); });
    document.getElementById('dd-add-audio')?.addEventListener('click', () => { trackDD?.classList.remove('open'); fn.addSpecialTrack('audio'); });

    document.getElementById('btn-undo')?.addEventListener('click', () => undo());
    document.getElementById('btn-redo')?.addEventListener('click', () => redo());
    document.getElementById('btn-delete-track')?.addEventListener('click', () => fn.removeTrack(state.selectedTrackIdx));
    document.getElementById('btn-delete-clip')?.addEventListener('click', () => fn.deleteSelectedClip());
    document.getElementById('btn-split')?.addEventListener('click', fn.splitClipAtPlayhead);
    document.getElementById('btn-export-bvh')?.addEventListener('click', fn.exportBVH);
    document.getElementById('btn-export-video')?.addEventListener('click', () => {
        // Switch to Export tab and update range
        fn.switchPropsTab('export');
        const toEl = document.getElementById('export-to');
        if (toEl && (toEl.value === '0' || !toEl.value)) toEl.value = Math.round(state.project.duration * state.project.fps);
    });
    // File dropdown
    const fileDD = document.getElementById('file-dropdown');
    document.getElementById('btn-file')?.addEventListener('click', (e) => { e.stopPropagation(); fileDD?.classList.toggle('open'); });
    document.getElementById('dd-file-save')?.addEventListener('click', () => { fileDD?.classList.remove('open'); fn.saveProject(); });
    document.getElementById('dd-file-save-as')?.addEventListener('click', () => { fileDD?.classList.remove('open'); fn.saveProjectAs(); });
    document.getElementById('dd-file-load')?.addEventListener('click', () => { fileDD?.classList.remove('open'); fn.loadProject(); });
    document.getElementById('dd-file-load-last')?.addEventListener('click', () => { fileDD?.classList.remove('open'); fn.loadLastProject(); });
    document.getElementById('dd-file-default')?.addEventListener('click', () => { fileDD?.classList.remove('open'); fn.resetToDefault(); });

    // Tools dropdown
    const toolsDD = document.getElementById('tools-dropdown');
    const toolsBtn = document.getElementById('btn-tools');
    toolsBtn?.addEventListener('click', (e) => {
        e.stopPropagation();
        toolsDD.classList.toggle('open');
    });
    document.addEventListener('click', () => {
        fileDD?.classList.remove('open');
        toolsDD?.classList.remove('open');
        trackDD?.classList.remove('open');
        document.getElementById('help-dropdown')?.classList.remove('open');
    });
    // Gaussian Smooth
    document.getElementById('dd-gauss-on')?.addEventListener('click', () => {
        _gaussSmooth.active = true;
        _updateGaussUI();
        applyGaussToAllClips();
        toolsDD.classList.remove('open');
    });
    document.getElementById('dd-gauss-off')?.addEventListener('click', () => {
        _gaussSmooth.active = false;
        _updateGaussUI();
        reloadAllClipAnimations();
        toolsDD.classList.remove('open');
    });
    document.getElementById('dd-gauss-sigma-input')?.addEventListener('change', (e) => {
        _gaussSmooth.sigma = Math.max(0.5, Math.min(20, parseFloat(e.target.value) || 2));
        e.target.value = _gaussSmooth.sigma;
        _updateGaussUI();
        if (_gaussSmooth.active) applyGaussToAllClips();
    });
    document.getElementById('dd-gauss-save')?.addEventListener('click', () => {
        toolsDD.classList.remove('open');
        saveSmoothedBVH();
    });
    document.getElementById('dd-ground')?.addEventListener('click', () => {
        toolsDD.classList.remove('open');
        fn.switchPropsTab('tools');
        groundFixSelectedClip();
    });

    // Properties panel tabs
    document.querySelectorAll('.props-tab').forEach(tab => {
        tab.addEventListener('click', () => fn.switchPropsTab(tab.dataset.tab));
    });

    // Tools panel buttons
    document.getElementById('tool-smooth-apply')?.addEventListener('click', smoothSelectedClip);
    document.getElementById('tool-ground-apply')?.addEventListener('click', groundFixSelectedClip);
    document.getElementById('tool-smooth-sigma')?.addEventListener('input', (e) => {
        const sigma = parseFloat(e.target.value) || 2;
        const radiusEl = document.getElementById('tool-smooth-radius');
        if (radiusEl) radiusEl.textContent = Math.ceil(sigma * 3);
    });

    // Track context menu
    const trackCtx = document.getElementById('track-context-menu');
    document.addEventListener('click', () => { if (trackCtx) trackCtx.style.display = 'none'; });
    document.getElementById('track-ctx-delete')?.addEventListener('click', () => {
        trackCtx.style.display = 'none';
        if (state.selectedTrackIdx >= 0) fn.removeTrack(state.selectedTrackIdx);
    });
    document.getElementById('track-ctx-rename')?.addEventListener('click', () => {
        trackCtx.style.display = 'none';
        if (state.selectedTrackIdx >= 0) {
            const track = state.project.tracks[state.selectedTrackIdx];
            const newName = prompt('Neuer Track-Name:', track.name);
            if (newName && newName !== track.name) { track.name = newName; fn.updateTrackHeaders(); fn.updateProperties(); }
        }
    });
    document.getElementById('track-ctx-mute')?.addEventListener('click', () => {
        trackCtx.style.display = 'none';
        if (state.selectedTrackIdx >= 0) {
            const track = state.project.tracks[state.selectedTrackIdx];
            track.muted = !track.muted;
            fn.updateProperties();
        }
    });

    // Help dropdown
    const helpDD = document.getElementById('help-dropdown');
    document.getElementById('btn-help')?.addEventListener('click', (e) => { e.stopPropagation(); helpDD?.classList.toggle('open'); });
    document.getElementById('dd-help-tracks')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('tracks'); });
    document.getElementById('dd-help-camera')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('camera'); });
    document.getElementById('dd-help-light')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('light'); });
    document.getElementById('dd-help-audio')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('audio'); });
    document.getElementById('dd-help-shortcuts')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('shortcuts'); });
    document.getElementById('dd-help-animations')?.addEventListener('click', () => { helpDD?.classList.remove('open'); showHelp('animations'); });
    document.getElementById('help-modal-close')?.addEventListener('click', () => { document.getElementById('help-modal').style.display = 'none'; });
    document.getElementById('help-modal')?.addEventListener('click', (e) => { if (e.target === e.currentTarget) e.currentTarget.style.display = 'none'; });
}

// =========================================================================
// Help system
// =========================================================================
const HELP_CONTENT = {
    tracks: {
        title: 'Tracks',
        body: `
<p><b>BVH Studio</b> arbeitet mit verschiedenen Track-Typen in einer gemeinsamen Timeline:</p>
<h4 style="color:var(--accent);margin:12px 0 6px;"><i class="fas fa-running"></i> BVH Track</h4>
<ul>
<li>Enthaelt Skelett-Animationen (BVH-Dateien)</li>
<li>Clips aus der <b>BVH Bibliothek</b> per Doppelklick oder Drag & Drop hinzufuegen</li>
<li>Clips koennen <b>verschoben</b> (Drag), <b>gesplittet</b> (S), <b>dupliziert</b> und <b>geloescht</b> (Del) werden</li>
<li>Rechtsklick auf Clip fuer Kontextmenue</li>
<li>Standard-Modell: Rig2 (konfigurierbar in Einstellungen)</li>
</ul>
<h4 style="color:#00bcd4;margin:12px 0 6px;"><i class="fas fa-video"></i> Kamera Track</h4>
<ul>
<li>Steuert die Kameraposition waehrend der Wiedergabe</li>
<li>Keyframes setzen: <b>K</b> druecken oder Button im Eigenschaften-Tab</li>
<li>Zwischen Keyframes wird interpoliert (Linear / Smooth / Step)</li>
</ul>
<h4 style="color:#ffc107;margin:12px 0 6px;"><i class="fas fa-lightbulb"></i> Licht Track</h4>
<ul>
<li>Erzeugt ein Punktlicht in der Szene</li>
<li>Position, Farbe und Intensitaet ueber Eigenschaften-Panel aendern</li>
<li>Keyframes fuer animiertes Licht</li>
</ul>
<h4 style="color:#4caf50;margin:12px 0 6px;"><i class="fas fa-music"></i> Audio Track</h4>
<ul>
<li>Audio-Datei (MP3/WAV/OGG) laden und zur Timeline synchronisieren</li>
<li>Lautstaerke, Fade In/Out und Offset konfigurierbar</li>
</ul>
<p style="margin-top:12px;"><b>Track hinzufuegen:</b> Klick auf "+ Track" in der Toolbar, dann Typ waehlen.</p>
<p><b>Track loeschen:</b> Track auswaehlen, dann Papierkorb-Button.</p>
`},
    camera: {
        title: 'Kamera',
        body: `
<h4 style="color:var(--accent);margin:0 0 8px;">Kamera-Track Funktionen</h4>
<p>Der Kamera-Track steuert die 3D-Kamera waehrend der Wiedergabe. Im Stopp-Modus bleibt die normale Maussteuerung (OrbitControls) aktiv.</p>

<h4 style="margin:14px 0 6px;">Keyframe setzen</h4>
<ol>
<li>Kamera-Track in der Timeline auswaehlen</li>
<li>Kamera mit Maus in die gewuenschte Position bewegen</li>
<li><b>K</b> druecken oder "Keyframe setzen" Button klicken</li>
<li>Die aktuelle Kameraposition, Rotation und FOV werden als Keyframe am Playhead gespeichert</li>
</ol>

<h4 style="margin:14px 0 6px;">Keyframe bearbeiten</h4>
<p>Klick auf einen Keyframe (Raute ◇) in der Timeline. Im Eigenschaften-Panel erscheinen:</p>
<ul>
<li><b>Position X/Y/Z</b> — Kameraposition in Metern</li>
<li><b>Rotation X/Y/Z</b> — Kamerarotation in Grad</li>
<li><b>FOV</b> — Sichtfeld (10-120 Grad)</li>
<li><b>Interpolation</b> — Linear / Smooth (weich) / Step (sprunghaft)</li>
<li><b>"Aktuelle Ansicht uebernehmen"</b> — ueberschreibt den Keyframe mit der aktuellen Kameraansicht</li>
</ul>

<h4 style="margin:14px 0 6px;">Wiedergabe</h4>
<p>Bei <b>Play</b> wird die Kamera automatisch zwischen den Keyframes interpoliert. Die Maussteuerung wird waehrend der Wiedergabe deaktiviert und beim Stopp wieder aktiviert.</p>
<p><b>"Aktiv" Checkbox</b>: Deaktivieren um den Kamera-Track temporaer zu ignorieren.</p>
`},
    light: {
        title: 'Licht',
        body: `
<h4 style="color:var(--accent);margin:0 0 8px;">Licht-Track Funktionen</h4>
<p>Ein Licht-Track erzeugt ein <b>Punktlicht</b> in der 3D-Szene. Mehrere Licht-Tracks koennen gleichzeitig aktiv sein.</p>

<h4 style="margin:14px 0 6px;">Licht konfigurieren</h4>
<p>Im <b>Eigenschaften-Tab</b> (rechts) bei ausgewaehltem Licht-Track:</p>
<ul>
<li><b>Farbe</b> — Lichtfarbe (Color Picker)</li>
<li><b>Intensitaet</b> — Helligkeit (0-20)</li>
<li><b>Sichtbar</b> — Zeigt/versteckt die Lichtposition als gelbe Kugel in der Szene</li>
<li><b>Position X/Y/Z</b> — Lichtposition in Metern</li>
</ul>

<h4 style="margin:14px 0 6px;">Licht-Keyframes</h4>
<ol>
<li>Licht-Track auswaehlen</li>
<li>Position/Farbe/Intensitaet einstellen</li>
<li><b>K</b> druecken oder "Keyframe setzen" Button klicken</li>
<li>Bei Wiedergabe wird zwischen Keyframes interpoliert (Position, Farbe, Intensitaet)</li>
</ol>

<h4 style="margin:14px 0 6px;">Lichtposition-Helper</h4>
<p>Die gelbe Kugel zeigt die aktuelle Lichtposition in der Szene. Ueber die Checkbox "Sichtbar" kann sie ein- und ausgeblendet werden.</p>
`},
    audio: {
        title: 'Audio',
        body: `
<h4 style="color:var(--accent);margin:0 0 8px;">Audio-Track Funktionen</h4>
<p>Audio-Tracks synchronisieren Audiodateien zur Timeline-Wiedergabe.</p>

<h4 style="margin:14px 0 6px;">Audio laden</h4>
<ol>
<li>Audio-Track hinzufuegen (+ Track > Audio Track)</li>
<li>Im Eigenschaften-Tab: "Audio laden" Button klicken</li>
<li>MP3, WAV oder OGG Datei auswaehlen</li>
<li>Der Audio-Clip erscheint als gruenes Rechteck in der Timeline</li>
</ol>

<h4 style="margin:14px 0 6px;">Audio bearbeiten</h4>
<p>Klick auf den Audio-Clip in der Timeline. Im Eigenschaften-Panel:</p>
<ul>
<li><b>Lautstaerke</b> — Schieberegler 0-100%</li>
<li><b>Fade In</b> — Einblende-Dauer in Frames</li>
<li><b>Fade Out</b> — Ausblende-Dauer in Frames</li>
<li><b>Offset</b> — Startpunkt innerhalb der Audiodatei (Sekunden)</li>
<li><b>Start</b> — Position auf der Timeline (Frame)</li>
</ul>

<h4 style="margin:14px 0 6px;">Wiedergabe</h4>
<p>Audio wird automatisch zur Timeline synchronisiert. Bei <b>Play</b> startet die Audiowiedergabe am aktuellen Playhead. Bei <b>Pause/Stop</b> wird die Audiowiedergabe gestoppt.</p>
<p>Audio-Clips koennen wie BVH-Clips <b>verschoben</b> und <b>geloescht</b> werden.</p>
`},
    shortcuts: {
        title: 'Tastenkuerzel',
        body: `
<table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">Space</kbd></td><td>Play / Pause</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">&#8592;</kbd> <kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">&#8594;</kbd></td><td>Frame vor / zurueck</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">S</kbd></td><td>Clip splitten am Playhead</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">Del</kbd></td><td>Ausgewaehlten Clip loeschen</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">K</kbd></td><td>Kamera/Licht Keyframe setzen</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">Ctrl+Shift+U</kbd></td><td>Undo (bis zu 20 Schritte)</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><kbd style="background:var(--bg-card);padding:2px 6px;border-radius:3px;border:1px solid var(--border);">Redo</kbd></td><td>Redo (nur per Button)</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><b>Mausrad</b></td><td>Timeline scrollen</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><b>Ctrl + Mausrad</b></td><td>Timeline zoomen</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><b>Mittlere Maustaste</b></td><td>Timeline pannen</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:6px 0;"><b>Alt + Klick</b></td><td>Timeline pannen</td></tr>
<tr><td style="padding:6px 0;"><b>Rechtsklick auf Clip</b></td><td>Kontextmenue</td></tr>
</table>
`},
    animations: {
        title: 'BVH Bibliothek verwalten',
        body: `
<h4 style="color:var(--accent);margin:0 0 8px;">BVH Bibliothek im Studio</h4>
<p>Die BVH Bibliothek links zeigt alle BVH-Dateien gruppiert nach Ordnern. Animationen koennen per <b>Doppelklick</b> oder <b>Drag &amp; Drop</b> zum ausgewaehlten Track hinzugefuegt werden.</p>

<h4 style="margin:14px 0 6px;">Bibliothek-Toolbar</h4>
<table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
<tr style="border-bottom:1px solid var(--border);"><td style="padding:5px 0;width:40px;text-align:center;"><i class="fas fa-folder-plus"></i></td><td><b>Neuer Ordner</b> — Erstellt einen neuen Kategorie-Ordner</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:5px 0;text-align:center;"><i class="fas fa-pen"></i></td><td><b>Umbenennen</b> — Benennt die ausgewaehlte Animation um</td></tr>
<tr style="border-bottom:1px solid var(--border);"><td style="padding:5px 0;text-align:center;"><i class="fas fa-trash"></i></td><td><b>Loeschen</b> — Loescht die ausgewaehlte Animation</td></tr>
<tr><td style="padding:5px 0;text-align:center;"><i class="fas fa-sync-alt"></i></td><td><b>Aktualisieren</b> — Laedt die Bibliothek neu</td></tr>
</table>

<h4 style="margin:14px 0 6px;">Kontextmenue (Rechtsklick)</h4>
<p><b>Auf eine Animation:</b></p>
<ul style="margin:4px 0;">
<li><b>Zum Track hinzufuegen</b> — Fuegt die Animation als Clip zum ausgewaehlten Track hinzu</li>
<li><b>Umbenennen</b> — Aendert den Dateinamen der BVH-Datei</li>
<li><b>Verschieben nach...</b> — Verschiebt die Datei in einen anderen Ordner</li>
<li><b>Loeschen</b> — Entfernt die BVH-Datei (mit Bestaetigung)</li>
</ul>
<p><b>Auf einen Ordner:</b></p>
<ul style="margin:4px 0;">
<li><b>Ordner umbenennen</b> — Aendert den Ordnernamen</li>
<li><b>Neuer Ordner</b> — Erstellt einen neuen Ordner</li>
<li><b>Ordner loeschen</b> — Entfernt einen leeren Ordner</li>
</ul>

<h4 style="margin:14px 0 6px;">Animation hinzufuegen</h4>
<ul style="margin:4px 0;">
<li><b>Doppelklick</b> auf eine Animation — fuegt sie zum ausgewaehlten Track hinzu</li>
<li><b>Drag &amp; Drop</b> — ziehe eine Animation auf einen Track-Header oder in die Timeline</li>
<li>Wird auf leere Stelle in der Timeline gezogen, wird automatisch ein neuer Track erstellt</li>
</ul>

<h4 style="margin:14px 0 6px;">Clips in der Timeline bearbeiten</h4>
<p>Clips koennen direkt in der Timeline per Maus bearbeitet werden:</p>
<ul style="margin:4px 0;">
<li><b>Verschieben</b> — Clip in der Mitte greifen und nach links/rechts ziehen</li>
<li><b>Trimmen (Anfang)</b> — Linken Rand des Clips greifen und ziehen → kuerzt die Animation von vorne</li>
<li><b>Trimmen (Ende)</b> — Rechten Rand des Clips greifen und ziehen → kuerzt die Animation von hinten</li>
<li>Der Cursor wechselt zu <b>↔</b> am Clip-Rand und zu <b>✋</b> in der Mitte</li>
</ul>
<p><b>Kontextmenue (Rechtsklick auf Clip):</b></p>
<ul style="margin:4px 0;">
<li><b>Split an Playhead (S)</b> — Teilt den Clip an der Playhead-Position</li>
<li><b>Duplizieren</b> — Erstellt eine Kopie hinter dem Clip</li>
<li><b>Loeschen (Del)</b> — Entfernt den Clip</li>
<li><b>Anfang trimmen (+10f)</b> — Kuerzt den Clip um 10 Frames von vorne</li>
<li><b>Ende trimmen (+10f)</b> — Kuerzt den Clip um 10 Frames von hinten</li>
<li><b>Trim zuruecksetzen</b> — Stellt die volle Laenge wieder her</li>
<li><b>BVH speichern unter...</b> — Speichert die BVH-Datei</li>
<li><b>Smooth / Bodenniveau</b> — Tools auf den Clip anwenden</li>
</ul>

<h4 style="margin:14px 0 6px;">Hinweise</h4>
<ul style="margin:4px 0;">
<li>Klick auf eine Animation markiert sie (lila) fuer Toolbar-Aktionen</li>
<li>Ordner koennen nur geloescht werden wenn sie leer sind</li>
<li>Beim Umbenennen/Verschieben wird auch die Retarget-Cache-Datei (.json) mitverschoben</li>
<li>Alle Aenderungen werden sofort auf der Festplatte ausgefuehrt</li>
<li>Wird der letzte Clip eines Tracks geloescht, verschwindet das 3D-Modell automatisch</li>
</ul>
`},
};

export function showHelp(topic) {
    const h = HELP_CONTENT[topic];
    if (!h) return;
    document.getElementById('help-modal-title').innerHTML = `<i class="fas fa-question-circle"></i> ${h.title}`;
    document.getElementById('help-modal-body').innerHTML = h.body;
    document.getElementById('help-modal').style.display = 'flex';
}

// =========================================================================
// Gaussian Smooth
// =========================================================================
export function _updateGaussUI() {
    const sigmaInput = document.getElementById('dd-gauss-sigma-input');
    if (sigmaInput) sigmaInput.value = _gaussSmooth.sigma;
    const onEl = document.getElementById('dd-gauss-on');
    const offEl = document.getElementById('dd-gauss-off');
    if (onEl) onEl.style.color = _gaussSmooth.active ? '#888' : '#4caf50';
    if (offEl) offEl.style.color = _gaussSmooth.active ? '#ef4444' : '#888';
    const toolsBtn = document.getElementById('btn-tools');
    if (toolsBtn) toolsBtn.innerHTML = _gaussSmooth.active
        ? `<i class="fas fa-wrench"></i> Tools <span style="font-size:0.65rem;color:#4caf50;">●σ=${_gaussSmooth.sigma}</span> <i class="fas fa-caret-down" style="font-size:0.65rem;"></i>`
        : `<i class="fas fa-wrench"></i> Tools <i class="fas fa-caret-down" style="font-size:0.65rem;"></i>`;
}

export function _gaussFilter(values, stride, sigma) {
    const nKeys = values.length / stride;
    const radius = Math.ceil(sigma * 3);
    const kernel = [];
    let ksum = 0;
    for (let i = -radius; i <= radius; i++) {
        const v = Math.exp(-0.5 * (i / sigma) ** 2);
        kernel.push(v); ksum += v;
    }
    for (let i = 0; i < kernel.length; i++) kernel[i] /= ksum;

    const orig = new Float32Array(values);
    for (let c = 0; c < stride; c++) {
        for (let k = 0; k < nKeys; k++) {
            let sum = 0;
            for (let j = 0; j < kernel.length; j++) {
                const idx = Math.max(0, Math.min(nKeys - 1, k + j - radius));
                sum += kernel[j] * orig[idx * stride + c];
            }
            values[k * stride + c] = sum;
        }
    }
    // Re-normalize quaternions
    if (stride === 4) {
        for (let k = 0; k < nKeys; k++) {
            const i = k * 4;
            const len = Math.sqrt(values[i]**2 + values[i+1]**2 + values[i+2]**2 + values[i+3]**2);
            if (len > 1e-8) { values[i]/=len; values[i+1]/=len; values[i+2]/=len; values[i+3]/=len; }
        }
    }
}

export function applyGaussToAllClips() {
    const sigma = _gaussSmooth.sigma;
    let smoothedCount = 0;
    let totalTracks = 0;
    for (const track of state.project.tracks) {
        totalTracks++;
        if (track.type !== 'bvh') { console.log(`[Gauss] skip track type=${track.type}`); continue; }
        for (const clip of track.clips) {
            if (!clip.animClip) continue;
            const key = `${clip.category}/${clip.name}`;
            // Save original values if not saved yet
            if (!_gaussSmooth.origClips.has(key)) {
                const backup = {};
                for (const t of clip.animClip.tracks) {
                    backup[t.name] = new Float32Array(t.values);
                }
                _gaussSmooth.origClips.set(key, backup);
            }
            // Restore original then apply smooth
            const backup = _gaussSmooth.origClips.get(key);
            let trackCount = 0;
            for (const t of clip.animClip.tracks) {
                if (backup[t.name]) t.values.set(backup[t.name]);
                _gaussFilter(t.values, t.getValueSize(), sigma);
                trackCount++;
            }
            // Log before/after for first track of first clip
            if (smoothedCount === 0 && clip.animClip.tracks.length > 0) {
                const t0 = clip.animClip.tracks[0];
                console.log(`[Gauss] Track "${t0.name}" first 4 values AFTER smooth: [${t0.values[0].toFixed(4)}, ${t0.values[1].toFixed(4)}, ${t0.values[2].toFixed(4)}, ${t0.values[3].toFixed(4)}]`);
                const bk = backup[t0.name];
                if (bk) console.log(`[Gauss] Track "${t0.name}" first 4 values ORIGINAL: [${bk[0].toFixed(4)}, ${bk[1].toFixed(4)}, ${bk[2].toFixed(4)}, ${bk[3].toFixed(4)}]`);
            }
            // CRITICAL: uncache the clip so Three.js creates a fresh Action with new data
            if (track.mixer) track.mixer.uncacheClip(clip.animClip);
            smoothedCount++;
        }
        // Reset active clip reference
        if (track.mixer) track.mixer.stopAllAction();
        track._activeClip = null;
        track._activeAction = null;
    }
    fn.applyPlayhead();
    fn.serverLog('gauss_smooth_on', `sigma=${sigma} clips=${smoothedCount}/${totalTracks}`);
    if (smoothedCount === 0) console.warn('[BVH Studio] WARNING: No clips were smoothed! Check track.type and clip.animClip.');
}

export function reloadAllClipAnimations() {
    // Restore originals
    for (const track of state.project.tracks) {
        if (track.type !== 'bvh') continue;
        for (const clip of track.clips) {
            if (!clip.animClip) continue;
            const key = `${clip.category}/${clip.name}`;
            const backup = _gaussSmooth.origClips.get(key);
            if (backup) {
                for (const t of clip.animClip.tracks) {
                    if (backup[t.name]) t.values.set(backup[t.name]);
                }
            }
            // Uncache so mixer uses restored data
            if (track.mixer) track.mixer.uncacheClip(clip.animClip);
        }
        if (track.mixer) track.mixer.stopAllAction();
        track._activeClip = null;
        track._activeAction = null;
    }
    _gaussSmooth.origClips.clear();
    fn.applyPlayhead();
    fn.serverLog('gauss_smooth_off');
}

async function saveSmoothedBVH() {
    if (!_gaussSmooth.active) { alert('Gaussian Smooth ist nicht aktiv.\nBitte erst EINSCHALTEN.'); return; }

    // Collect all clips from tracks
    const clips = [];
    for (const track of state.project.tracks) {
        if (track.type !== 'bvh') continue;
        for (const clip of track.clips) {
            if (clip.category && clip.name) clips.push(clip);
        }
    }

    // If no track clips, try current preview animation
    if (clips.length === 0) {
        const previewInfo = fn.getPreviewInfo ? fn.getPreviewInfo() : null;
        if (previewInfo && previewInfo.category && previewInfo.name) {
            clips.push({ category: previewInfo.category, name: previewInfo.name });
        }
    }

    if (clips.length === 0) {
        alert('Keine Animation geladen.\nBitte erst eine Animation per Doppelklick zum Track hinzufuegen\noder per A-Taste in der Vorschau oeffnen.');
        return;
    }

    const sigma = _gaussSmooth.sigma;
    let saved = 0;
    for (const clip of clips) {
        try {
            const resp = await fetch(`/api/retarget/smooth-bvh/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category: clip.category, name: clip.name, sigma }),
            });
            const result = await resp.json();
            if (result.ok) {
                saved++;
                fn.serverLog('gauss_saved', `${clip.category}/${clip.name} sigma=${sigma}`);
            } else {
                console.error(`Save failed for ${clip.name}:`, result.error);
            }
        } catch(e) { console.error(`Save failed for ${clip.name}:`, e); }
    }
    _gaussSmooth.origClips.clear();
    alert(`Smooth (σ=${sigma}) permanent gespeichert auf ${saved} von ${clips.length} Clip(s).`);
    console.log(`[BVH Studio] Smoothed clips saved: ${saved}`);
}

export function smoothSelectedClip() {
    if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) { alert('Clip auswaehlen.'); return; }
    pushUndo('Smooth');
    const clip = state.project.tracks[state.selectedTrackIdx].clips[state.selectedClipIdx];
    if (!clip.animClip) { alert('Clip hat keine Animation.'); return; }

    // Read sigma from tools panel, fallback to clip property
    const sigmaInput = document.getElementById('tool-smooth-sigma');
    const sigma = sigmaInput ? parseFloat(sigmaInput.value) || 2 : (clip.smoothSigma || 2);
    if (sigma <= 0) { alert('Sigma muss > 0 sein.'); return; }

    const mode = document.getElementById('tool-smooth-mode')?.value || 'all';

    const radius = Math.ceil(sigma * 3);
    const kernel = [];
    let ksum = 0;
    for (let i = -radius; i <= radius; i++) {
        const v = Math.exp(-0.5 * (i / sigma) ** 2);
        kernel.push(v); ksum += v;
    }
    for (let i = 0; i < kernel.length; i++) kernel[i] /= ksum;

    // Filter bone names by mode
    const HAND_BONES = ['hand', 'finger', 'thumb', 'palm'];
    const BODY_ONLY_SKIP = [...HAND_BONES];

    let smoothedCount = 0;
    for (const track of clip.animClip.tracks) {
        const tn = track.name.toLowerCase();
        if (mode === 'body' && HAND_BONES.some(h => tn.includes(h))) continue;
        if (mode === 'hands' && !HAND_BONES.some(h => tn.includes(h))) continue;

        const stride = track.getValueSize();
        const nKeys = track.values.length / stride;
        const orig = new Float32Array(track.values);
        for (let c = 0; c < stride; c++) {
            for (let k = 0; k < nKeys; k++) {
                let sum = 0;
                for (let j = 0; j < kernel.length; j++) {
                    const idx = Math.max(0, Math.min(nKeys - 1, k + j - radius));
                    sum += kernel[j] * orig[idx * stride + c];
                }
                track.values[k * stride + c] = sum;
            }
        }
        // Re-normalize quaternions
        if (stride === 4) {
            for (let k = 0; k < nKeys; k++) {
                const i = k * 4;
                const len = Math.sqrt(track.values[i]**2 + track.values[i+1]**2 + track.values[i+2]**2 + track.values[i+3]**2);
                if (len > 1e-8) { track.values[i]/=len; track.values[i+1]/=len; track.values[i+2]/=len; track.values[i+3]/=len; }
            }
        }
        smoothedCount++;
    }
    // Update clip property
    clip.smoothSigma = sigma;
    fn.updateProperties();
    console.log(`[BVH Studio] Smoothed ${clip.name}: sigma=${sigma}, mode=${mode}, ${smoothedCount} tracks`);
}

// =========================================================================
// Ground Fix (Bodenniveau)
// =========================================================================
export async function groundFixSelectedClip() {
    if (state.selectedTrackIdx < 0 || state.selectedClipIdx < 0) { alert('Clip auswaehlen.'); return; }
    pushUndo('Bodenniveau');
    const track = state.project.tracks[state.selectedTrackIdx];
    const clip = track.clips[state.selectedClipIdx];
    if (!clip.animClip || !track.skeleton) { alert('Clip oder Skeleton nicht geladen.'); return; }

    // Read desired ground offset from Tools panel (default 0.03m = 3cm)
    const groundOffset = parseFloat(document.getElementById('tool-ground-offset')?.value) || 0.03;

    const skel = track.skeleton;
    const bones = skel.skeleton.bones;
    const rootBone = skel.rootBone;

    // Create temporary mixer to evaluate each frame
    const tmpMixer = new THREE.AnimationMixer(track.mesh);
    const tmpAction = tmpMixer.clipAction(clip.animClip);
    tmpAction.play();

    const tmpV = new THREE.Vector3();

    // Find position track for root bone
    let posTrack = null;
    for (const t of clip.animClip.tracks) {
        if (t.name.includes('.position')) { posTrack = t; break; }
    }
    if (!posTrack) {
        alert('Kein Position-Track gefunden.');
        tmpAction.stop(); tmpMixer.stopAllAction();
        return;
    }

    // Identify foot bones (left + right)
    const footBones = bones.filter(b => {
        const n = b.name.toLowerCase();
        return n.includes('foot') || n.includes('toe') || n.includes('heel');
    });
    if (footBones.length === 0) {
        alert('Keine Fuss-Knochen gefunden.');
        tmpAction.stop(); tmpMixer.stopAllAction();
        return;
    }
    console.log(`[BVH Studio] Ground fix: ${footBones.length} foot bones: ${footBones.map(b => b.name).join(', ')}`);

    const nKeys = posTrack.times.length;
    let corrected = 0;

    for (let f = 0; f < nKeys; f++) {
        const t = posTrack.times[f];
        tmpMixer.setTime(t);
        rootBone.updateWorldMatrix(true, true);

        // Find lowest foot bone Y (considering both left and right)
        let minY = Infinity;
        for (const b of footBones) {
            b.getWorldPosition(tmpV);
            if (tmpV.y < minY) minY = tmpV.y;
        }

        // If foot is below ground (minY < 0): correct to exactly 0
        // If foot is above ground (minY >= 0): correct to groundOffset
        const target = minY < 0 ? 0 : groundOffset;
        const correction = minY - target;
        if (Math.abs(correction) > 0.001) {
            const idx = f * 3 + 1;  // Y component (position is vec3: x,y,z)
            posTrack.values[idx] -= correction;
            corrected++;
        }
    }

    tmpAction.stop();
    tmpMixer.stopAllAction();

    clip.groundFix = true;
    fn.updateProperties();

    if (corrected === 0) {
        console.log(`[BVH Studio] ${clip.name}: bereits auf Bodenniveau.`);
        fn.applyPlayhead();
        return;
    }

    console.log(`[BVH Studio] Ground fix: ${corrected}/${nKeys} Frames korrigiert fuer ${clip.name}`);
    fn.applyPlayhead();

    // Save corrected BVH to disk
    try {
        // Fetch original BVH text
        const bvhUrl = `/api/character/bvh/${encodeURIComponent(clip.category)}/${encodeURIComponent(clip.name)}/`;
        const bvhResp = await fetch(bvhUrl);
        const bvhText = await bvhResp.text();
        const lines = bvhText.split('\n');

        // Find Yposition channel index
        let yPosChannel = -1, foundRoot = false;
        for (let i = 0; i < lines.length; i++) {
            const trimmed = lines[i].trim();
            if (trimmed.startsWith('ROOT ')) { foundRoot = true; continue; }
            if (foundRoot && trimmed.startsWith('CHANNELS')) {
                const parts = trimmed.split(/\s+/);
                for (let c = 2; c < parts.length; c++) {
                    if (parts[c] === 'Yposition') { yPosChannel = c - 2; break; }
                }
                break;
            }
        }

        if (yPosChannel < 0) {
            console.warn('[BVH Studio] Yposition channel not found in BVH, skip save.');
            return;
        }

        // Find motion data lines
        const motionIdx = lines.findIndex(l => l.trim() === 'MOTION');
        if (motionIdx < 0) return;
        let dataStart = motionIdx + 1;
        while (dataStart < lines.length && !lines[dataStart].trim().match(/^[\d\-\.]/)) dataStart++;

        const frameLines = [];
        for (let i = dataStart; i < lines.length; i++) {
            if (lines[i].trim().match(/^[\d\-\.]/)) frameLines.push(i);
        }

        // Apply corrections from posTrack to BVH text
        for (let f = 0; f < Math.min(nKeys, frameLines.length); f++) {
            const li = frameLines[f];
            const vals = lines[li].trim().split(/\s+/);
            vals[yPosChannel] = posTrack.values[f * 3 + 1].toFixed(6);
            lines[li] = vals.join(' ');
        }

        // Save via API
        const saveResp = await fetch('/api/character/save-bvh-text/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category: clip.category, name: clip.name, bvh_text: lines.join('\n') }),
        });
        if (saveResp.ok) {
            console.log(`[BVH Studio] BVH saved: ${clip.category}/${clip.name}`);
        } else {
            console.warn(`[BVH Studio] BVH save failed: ${await saveResp.text()}`);
        }
    } catch (e) {
        console.error('[BVH Studio] BVH save error:', e);
    }
}

// Register functions in registry
fn.setupToolbar = setupToolbar;
fn.showHelp = showHelp;
fn.smoothSelectedClip = smoothSelectedClip;
fn.groundFixSelectedClip = groundFixSelectedClip;
fn.getGaussSmooth = () => _gaussSmooth;
fn.gaussFilter = _gaussFilter;
fn.applyGaussToAllClips = applyGaussToAllClips;
fn.reloadAllClipAnimations = reloadAllClipAnimations;

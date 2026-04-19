/**
 * BVH Studio — Properties panel (track/clip/keyframe editors).
 */
import * as THREE from 'three';
import { state, TRACK_ICONS } from './state.js';
import { fn } from './registry.js';

export function updateProperties() {
    const content = document.getElementById('props-content');
    if (!content) return;

    if (state.selectedTrackIdx < 0 || state.selectedTrackIdx >= state.project.tracks.length) {
        content.innerHTML = '<div style="color:var(--text-muted);font-size:0.8rem;">Animation oder Clip auswählen</div>';
        return;
    }

    const track = state.project.tracks[state.selectedTrackIdx];
    const clip = state.selectedClipIdx >= 0 ? track.clips[state.selectedClipIdx] : null;
    let html = '';

    // --- Track header (common) ---
    const icon = TRACK_ICONS[track.type] || 'fa-running';
    html += `<div class="prop-group">
        <h3 style="font-size:0.85rem;color:var(--accent);margin-bottom:6px;"><i class="fas ${icon}"></i> ${track.name}</h3>
        <div class="prop-row"><label>Name:</label><input type="text" value="${track.name}" id="prop-track-name"></div>
        <div class="prop-row"><label>Muted:</label><input type="checkbox" ${track.muted?'checked':''} id="prop-track-mute"></div>
    </div>`;

    // --- Type-specific track props ---
    if (track.type === 'bvh') {
        html += `<div class="prop-group">
            <div class="prop-row"><label>Modell:</label><span style="font-size:0.8rem;color:var(--accent);">${track.preset}</span></div>
            <div class="prop-row"><label>X:</label><input type="number" step="0.1" value="${track.position[0]}" id="prop-pos-x"></div>
            <div class="prop-row"><label>Z:</label><input type="number" step="0.1" value="${track.position[2]}" id="prop-pos-z"></div>
        </div>`;
    } else if (track.type === 'camera') {
        html += `<div class="prop-group">
            <div class="prop-row"><label>Aktiv:</label><input type="checkbox" ${track.cameraActive?'checked':''} id="prop-cam-active"></div>
            <div style="margin-top:6px;">
                <button id="prop-cam-add-kf" style="padding:4px 10px;background:var(--accent);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.78rem;"><i class="fas fa-key"></i> Keyframe setzen (K)</button>
            </div>
            <div style="margin-top:4px;font-size:0.72rem;color:var(--text-muted);">Setzt aktuelle Kamera-Position als Keyframe am Playhead.</div>
        </div>`;
    } else if (track.type === 'light') {
        const L = track.light;
        const lt = track.lightType || 'spot';
        const hasPosition = !!(L && !L.isAmbientLight);
        const hasTarget   = !!(L && L.target);
        const hasAngle    = !!(L && L.isSpotLight);
        const hasDistance = !!(L && (L.isSpotLight || L.isPointLight));
        const lp = L?.position || {x:0,y:0,z:0};
        const tg = L?.target?.position || {x:0,y:0,z:0};
        const lc = L ? '#' + L.color.getHexString() : '#ffffff';
        const rgb = L ? L.color : new THREE.Color(0xffffff);
        const R = Math.round(rgb.r * 255), G = Math.round(rgb.g * 255), B = Math.round(rgb.b * 255);
        const angleDeg = ((L?.angle ?? Math.PI/6) * 180 / Math.PI).toFixed(1);
        const penumbra = (L?.penumbra ?? 0.3).toFixed(2);
        const distance = (L?.distance ?? 50).toFixed(1);
        const typeLabel = { spot: 'SpotLight', directional: 'Directional', point: 'PointLight', ambient: 'Ambient' }[lt] || lt;
        html += `<div class="prop-group">
            <div class="prop-row"><label>Licht-Typ:</label><span style="font-size:0.8rem;color:var(--accent);">${typeLabel}${track._sceneLight ? ' (Szene)' : ''}</span></div>
            <div class="prop-row"><label>Farbe:</label><input type="color" value="${lc}" id="prop-light-color"></div>
            <div class="prop-row"><label>R:</label><input type="range" min="0" max="255" value="${R}" id="prop-light-r" style="flex:1;"><span id="prop-light-r-val" style="width:30px;font-size:0.75rem;">${R}</span></div>
            <div class="prop-row"><label>G:</label><input type="range" min="0" max="255" value="${G}" id="prop-light-g" style="flex:1;"><span id="prop-light-g-val" style="width:30px;font-size:0.75rem;">${G}</span></div>
            <div class="prop-row"><label>B:</label><input type="range" min="0" max="255" value="${B}" id="prop-light-b" style="flex:1;"><span id="prop-light-b-val" style="width:30px;font-size:0.75rem;">${B}</span></div>
            <div class="prop-row"><label>Intensität:</label><input type="number" value="${L?.intensity||2}" id="prop-light-intensity" min="0" max="20" step="0.1"></div>
            ${hasAngle ? `<div class="prop-row"><label>Winkel:</label><input type="number" value="${angleDeg}" id="prop-light-angle" min="1" max="170" step="1"> °</div>
            <div class="prop-row"><label>Penumbra:</label><input type="number" value="${penumbra}" id="prop-light-penumbra" min="0" max="1" step="0.05"></div>` : ''}
            ${hasDistance ? `<div class="prop-row"><label>Reichweite:</label><input type="number" value="${distance}" id="prop-light-distance" min="0" max="200" step="1"></div>` : ''}
            <div class="prop-row"><label>Helper zeigen:</label><input type="checkbox" ${track.lightVisible?'checked':''} id="prop-light-visible"${track.lightHelper ? '' : ' disabled'}></div>
            ${hasPosition ? `<h3 style="font-size:0.8rem;color:var(--text-muted);margin:8px 0 4px;">Position</h3>
            <div class="prop-row"><label>X:</label><input type="number" step="0.1" value="${lp.x.toFixed(2)}" id="prop-light-x"></div>
            <div class="prop-row"><label>Y:</label><input type="number" step="0.1" value="${lp.y.toFixed(2)}" id="prop-light-y"></div>
            <div class="prop-row"><label>Z:</label><input type="number" step="0.1" value="${lp.z.toFixed(2)}" id="prop-light-z"></div>` : ''}
            ${hasTarget ? `<h3 style="font-size:0.8rem;color:var(--text-muted);margin:8px 0 4px;">Ziel (Blickrichtung)</h3>
            <div class="prop-row"><label>X:</label><input type="number" step="0.1" value="${tg.x.toFixed(2)}" id="prop-light-tx"></div>
            <div class="prop-row"><label>Y:</label><input type="number" step="0.1" value="${tg.y.toFixed(2)}" id="prop-light-ty"></div>
            <div class="prop-row"><label>Z:</label><input type="number" step="0.1" value="${tg.z.toFixed(2)}" id="prop-light-tz"></div>` : ''}
            <div style="margin-top:6px;">
                <button id="prop-light-add-kf" style="padding:4px 10px;background:var(--accent);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.78rem;"><i class="fas fa-key"></i> Keyframe setzen</button>
            </div>
            ${!track._sceneLight ? '' : `<div style="margin-top:6px;font-size:0.7rem;color:var(--text-muted);">Szenen-Licht — wird immer geladen, kann nicht gelöscht werden.</div>`}
        </div>`;
    } else if (track.type === 'model') {
        const linkedAnim = state.project.getLinkedAnimation(track);
        const linkedName = linkedAnim ? linkedAnim.name : '(keiner)';
        html += `<div class="prop-group">
            <div class="prop-row"><label>Verknüpft:</label><span style="font-size:0.8rem;color:var(--accent);">${linkedName}</span></div>
        </div>`;
    } else if (track.type === 'audio') {
        html += `<div class="prop-group">
            <div style="margin-bottom:6px;">
                <button id="prop-audio-load" style="padding:4px 10px;background:var(--accent);color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:0.78rem;"><i class="fas fa-folder-open"></i> Audio laden</button>
            </div>
        </div>`;
    }

    // --- Clips/Keyframes list ---
    const clipLabel = (track.type === 'camera' || track.type === 'light') ? 'Keyframes' : 'Clips';
    html += `<div class="prop-group">
        <h3 style="font-size:0.85rem;color:var(--text-muted);">${clipLabel} (${track.clips.length})</h3>
        ${track.clips.map((c, i) => {
            const dur = c.type === 'camera_kf' || c.type === 'light_kf' ? `F${c.startFrame}` : `${c.duration.toFixed(1)}s`;
            return `<div class="prop-clip-item" data-clip="${i}" style="font-size:0.78rem;padding:4px 6px;margin:2px 0;border-radius:3px;cursor:pointer;background:${i===state.selectedClipIdx?'rgba(124,92,191,0.3)':'transparent'};color:${i===state.selectedClipIdx?'var(--accent)':'var(--text)'};">${c.name} (${dur})</div>`;
        }).join('')}
    </div>`;

    // --- Selected clip/keyframe details ---
    if (clip) {
        if (clip.type === 'camera_kf') {
            const d = clip.data;
            html += `<div class="prop-group">
                <h3 style="font-size:0.85rem;color:var(--accent);">Kamera Keyframe</h3>
                <div class="prop-row"><label>Frame:</label><input type="number" value="${clip.startFrame}" id="prop-kf-frame" min="0"></div>
                <div class="prop-row"><label>Pos X:</label><input type="number" value="${d.position?.x?.toFixed(3)||0}" id="prop-kf-px" step="0.1"></div>
                <div class="prop-row"><label>Pos Y:</label><input type="number" value="${d.position?.y?.toFixed(3)||0}" id="prop-kf-py" step="0.1"></div>
                <div class="prop-row"><label>Pos Z:</label><input type="number" value="${d.position?.z?.toFixed(3)||0}" id="prop-kf-pz" step="0.1"></div>
                <div class="prop-row"><label>Rot X:</label><input type="number" value="${((d.rotation?.x||0)*180/Math.PI).toFixed(1)}" id="prop-kf-rx" step="1"> °</div>
                <div class="prop-row"><label>Rot Y:</label><input type="number" value="${((d.rotation?.y||0)*180/Math.PI).toFixed(1)}" id="prop-kf-ry" step="1"> °</div>
                <div class="prop-row"><label>Rot Z:</label><input type="number" value="${((d.rotation?.z||0)*180/Math.PI).toFixed(1)}" id="prop-kf-rz" step="1"> °</div>
                <div class="prop-row"><label>FOV:</label><input type="number" value="${d.fov||50}" id="prop-kf-fov" min="10" max="120"></div>
                <div class="prop-row"><label>Interp.:</label>
                    <select id="prop-kf-interp">
                        <option value="linear" ${d.interpolation==='linear'?'selected':''}>Linear</option>
                        <option value="smooth" ${d.interpolation==='smooth'?'selected':''}>Smooth</option>
                        <option value="step" ${d.interpolation==='step'?'selected':''}>Step</option>
                    </select>
                </div>
                <div style="margin-top:6px;">
                    <button id="prop-kf-set-view" style="padding:3px 8px;font-size:0.75rem;background:var(--bg-card);color:var(--text);border:1px solid var(--border);border-radius:3px;cursor:pointer;">Aktuelle Ansicht übernehmen</button>
                </div>
            </div>`;
        } else if (clip.type === 'light_kf') {
            const d = clip.data;
            html += `<div class="prop-group">
                <h3 style="font-size:0.85rem;color:var(--accent);">Licht Keyframe</h3>
                <div class="prop-row"><label>Frame:</label><input type="number" value="${clip.startFrame}" id="prop-lkf-frame" min="0"></div>
                <div class="prop-row"><label>Pos X:</label><input type="number" value="${d.position?.x?.toFixed(2)||0}" id="prop-lkf-px" step="0.1"></div>
                <div class="prop-row"><label>Pos Y:</label><input type="number" value="${d.position?.y?.toFixed(2)||0}" id="prop-lkf-py" step="0.1"></div>
                <div class="prop-row"><label>Pos Z:</label><input type="number" value="${d.position?.z?.toFixed(2)||0}" id="prop-lkf-pz" step="0.1"></div>
                <div class="prop-row"><label>Farbe:</label><input type="color" value="${d.color||'#ffffff'}" id="prop-lkf-color"></div>
                <div class="prop-row"><label>Intensität:</label><input type="number" value="${d.intensity||2}" id="prop-lkf-intensity" min="0" max="20" step="0.1"></div>
            </div>`;
        } else if (clip.type === 'audio') {
            const d = clip.data;
            html += `<div class="prop-group">
                <h3 style="font-size:0.85rem;color:var(--accent);">Audio: ${d.fileName||'?'}</h3>
                <div class="prop-row"><label>Datei:</label><span style="font-size:0.75rem;color:var(--text-muted);">${d.fileName||'—'}</span></div>
                <div class="prop-row"><label>Dauer:</label><span style="font-size:0.8rem;">${(d.audioDuration||0).toFixed(1)}s</span></div>
                <div class="prop-row"><label>Start:</label><input type="number" value="${clip.startFrame}" id="prop-audio-start" min="0"> <span style="font-size:0.7rem;">f</span></div>
                <div class="prop-row"><label>Lautstärke:</label><input type="range" value="${(d.volume||1)*100}" id="prop-audio-vol" min="0" max="100"> <span id="prop-audio-vol-label" style="font-size:0.75rem;">${Math.round((d.volume||1)*100)}%</span></div>
                <div class="prop-row"><label>Fade In:</label><input type="number" value="${d.fadeIn||0}" id="prop-audio-fadein" min="0"> <span style="font-size:0.7rem;">f</span></div>
                <div class="prop-row"><label>Fade Out:</label><input type="number" value="${d.fadeOut||0}" id="prop-audio-fadeout" min="0"> <span style="font-size:0.7rem;">f</span></div>
                <div class="prop-row"><label>Offset:</label><input type="number" value="${d.offset||0}" id="prop-audio-offset" min="0" step="0.1"> <span style="font-size:0.7rem;">s</span></div>
            </div>`;
        } else if (clip.type === 'model') {
            const presetVal = clip.data?.preset || '';
            const bodyVal = clip.data?.bodyType || 'Female_Caucasian';
            html += `<div class="prop-group">
                <h3 style="font-size:0.85rem;color:var(--accent);">Modell Clip</h3>
                <div class="prop-row"><label>Preset:</label><input type="text" value="${presetVal}" id="prop-model-preset" placeholder="z.B. FemaleGarment"></div>
                <div class="prop-row"><label>Body Type:</label><input type="text" value="${bodyVal}" id="prop-model-bodytype"></div>
                <div class="prop-row"><label>Start:</label><input type="number" value="${clip.startFrame}" id="prop-model-start" min="0"> <span style="font-size:0.7rem;">f</span></div>
                <div class="prop-row"><label>Dauer:</label><input type="number" value="${clip.totalFrames}" id="prop-model-frames" min="1"> <span style="font-size:0.7rem;">f</span></div>
            </div>`;
        } else {
            // BVH clip
            html += `<div class="prop-group">
                <h3 style="font-size:0.85rem;color:var(--accent);">Clip: ${clip.name}</h3>
                <div class="prop-row"><label>Start:</label><input type="number" value="${clip.startFrame}" id="prop-clip-start" min="0"> <span style="font-size:0.7rem;color:var(--text-muted);">frames</span></div>
                <div class="prop-row"><label>Trim In:</label><input type="number" value="${clip.trimIn}" id="prop-clip-trim-in" min="0"></div>
                <div class="prop-row"><label>Trim Out:</label><input type="number" value="${clip.trimOut}" id="prop-clip-trim-out" min="0"></div>
                <div class="prop-row"><label>Speed:</label><input type="number" value="${clip.speed}" id="prop-clip-speed" min="0.1" max="4" step="0.1"></div>
                <div class="prop-row"><label>Smooth:</label><input type="number" value="${clip.smoothSigma}" id="prop-clip-smooth" min="0" max="10" step="0.5"></div>
                <div class="prop-row"><label>Boden:</label><input type="checkbox" ${clip.groundFix?'checked':''} id="prop-clip-ground"></div>
                <div class="prop-row"><label>Blend In:</label><input type="number" value="${clip.blendIn}" id="prop-clip-blend-in" min="0"> <span style="font-size:0.7rem;">f</span></div>
                <div class="prop-row"><label>Blend Out:</label><input type="number" value="${clip.blendOut}" id="prop-clip-blend-out" min="0"> <span style="font-size:0.7rem;">f</span></div>
            </div>`;
        }
    }

    content.innerHTML = html;

    // --- Wire up events ---
    document.getElementById('prop-track-name')?.addEventListener('change', (e) => { track.name = e.target.value; fn.updateTrackHeaders(); });
    document.getElementById('prop-track-mute')?.addEventListener('change', (e) => { track.muted = e.target.checked; });
    document.getElementById('prop-pos-x')?.addEventListener('change', (e) => { track.position[0] = parseFloat(e.target.value)||0; track.group.position.x = track.position[0]; });
    document.getElementById('prop-pos-z')?.addEventListener('change', (e) => { track.position[2] = parseFloat(e.target.value)||0; track.group.position.z = track.position[2]; });

    // Camera track
    document.getElementById('prop-cam-active')?.addEventListener('change', (e) => { track.cameraActive = e.target.checked; });
    document.getElementById('prop-cam-add-kf')?.addEventListener('click', () => fn.addCameraKeyframe(state.selectedTrackIdx));

    // Light track
    const _updateHelper = () => {
        if (!track.light) return;
        if (track.light.target) track.light.target.updateMatrixWorld();
        if (track.lightHelper?.update) track.lightHelper.update();
    };
    const _syncRgbInputs = () => {
        if (!track.light) return;
        const c = track.light.color;
        const r = Math.round(c.r*255), g = Math.round(c.g*255), b = Math.round(c.b*255);
        const setV = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
        setV('prop-light-r', r); setV('prop-light-g', g); setV('prop-light-b', b);
        const setT = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
        setT('prop-light-r-val', r); setT('prop-light-g-val', g); setT('prop-light-b-val', b);
        const cp = document.getElementById('prop-light-color');
        if (cp) cp.value = '#' + c.getHexString();
    };
    document.getElementById('prop-light-color')?.addEventListener('input', (e) => {
        if (track.light) { track.light.color.set(e.target.value); _syncRgbInputs(); _updateHelper(); }
    });
    ['r','g','b'].forEach(ch => {
        document.getElementById(`prop-light-${ch}`)?.addEventListener('input', (e) => {
            if (!track.light) return;
            const v = parseInt(e.target.value) / 255;
            if (ch === 'r') track.light.color.r = v;
            else if (ch === 'g') track.light.color.g = v;
            else track.light.color.b = v;
            document.getElementById(`prop-light-${ch}-val`).textContent = e.target.value;
            const cp = document.getElementById('prop-light-color');
            if (cp) cp.value = '#' + track.light.color.getHexString();
            _updateHelper();
        });
    });
    document.getElementById('prop-light-intensity')?.addEventListener('change', (e) => {
        if (track.light) { track.light.intensity = parseFloat(e.target.value)||2; _updateHelper(); }
    });
    document.getElementById('prop-light-angle')?.addEventListener('change', (e) => {
        if (track.light) { track.light.angle = (parseFloat(e.target.value)||30) * Math.PI / 180; _updateHelper(); }
    });
    document.getElementById('prop-light-penumbra')?.addEventListener('change', (e) => {
        if (track.light) { track.light.penumbra = Math.max(0, Math.min(1, parseFloat(e.target.value)||0)); _updateHelper(); }
    });
    document.getElementById('prop-light-distance')?.addEventListener('change', (e) => {
        if (track.light) { track.light.distance = parseFloat(e.target.value)||50; _updateHelper(); }
    });
    document.getElementById('prop-light-visible')?.addEventListener('change', (e) => {
        track.lightVisible = e.target.checked;
        if (track.lightHelper) track.lightHelper.visible = e.target.checked;
    });
    ['x','y','z'].forEach(axis => {
        document.getElementById(`prop-light-${axis}`)?.addEventListener('change', (e) => {
            if (track.light) { track.light.position[axis] = parseFloat(e.target.value)||0; _updateHelper(); }
        });
        document.getElementById(`prop-light-t${axis}`)?.addEventListener('change', (e) => {
            if (track.light?.target) { track.light.target.position[axis] = parseFloat(e.target.value)||0; _updateHelper(); }
        });
    });
    document.getElementById('prop-light-add-kf')?.addEventListener('click', () => fn.addLightKeyframe(state.selectedTrackIdx));

    // Audio track
    document.getElementById('prop-audio-load')?.addEventListener('click', () => fn.loadAudioFile(state.selectedTrackIdx));

    // Clip selection
    document.querySelectorAll('.prop-clip-item').forEach(el => {
        el.addEventListener('click', () => { state.selectedClipIdx = parseInt(el.dataset.clip); updateProperties(); fn.renderTimeline(); });
    });

    // Camera keyframe editors
    if (clip?.type === 'camera_kf') {
        document.getElementById('prop-kf-frame')?.addEventListener('change', (e) => { clip.startFrame = parseInt(e.target.value)||0; track.clips.sort((a,b)=>a.startFrame-b.startFrame); fn.renderTimeline(); });
        ['px','py','pz'].forEach((id, i) => {
            const axis = ['x','y','z'][i];
            document.getElementById(`prop-kf-${id}`)?.addEventListener('change', (e) => { clip.data.position[axis] = parseFloat(e.target.value)||0; });
        });
        ['rx','ry','rz'].forEach((id, i) => {
            const axis = ['x','y','z'][i];
            document.getElementById(`prop-kf-${id}`)?.addEventListener('change', (e) => { clip.data.rotation[axis] = (parseFloat(e.target.value)||0)*Math.PI/180; });
        });
        document.getElementById('prop-kf-fov')?.addEventListener('change', (e) => { clip.data.fov = parseFloat(e.target.value)||50; });
        document.getElementById('prop-kf-interp')?.addEventListener('change', (e) => { clip.data.interpolation = e.target.value; });
        document.getElementById('prop-kf-set-view')?.addEventListener('click', () => {
            clip.data.position = { x: state.camera.position.x, y: state.camera.position.y, z: state.camera.position.z };
            clip.data.rotation = { x: state.camera.rotation.x, y: state.camera.rotation.y, z: state.camera.rotation.z };
            clip.data.fov = state.camera.fov;
            updateProperties();
        });
    }

    // Light keyframe editors
    if (clip?.type === 'light_kf') {
        document.getElementById('prop-lkf-frame')?.addEventListener('change', (e) => { clip.startFrame = parseInt(e.target.value)||0; track.clips.sort((a,b)=>a.startFrame-b.startFrame); fn.renderTimeline(); });
        ['px','py','pz'].forEach((id, i) => {
            const axis = ['x','y','z'][i];
            document.getElementById(`prop-lkf-${id}`)?.addEventListener('change', (e) => { clip.data.position[axis] = parseFloat(e.target.value)||0; });
        });
        document.getElementById('prop-lkf-color')?.addEventListener('input', (e) => { clip.data.color = e.target.value; });
        document.getElementById('prop-lkf-intensity')?.addEventListener('change', (e) => { clip.data.intensity = parseFloat(e.target.value)||2; });
    }

    // Audio clip editors
    if (clip?.type === 'audio') {
        document.getElementById('prop-audio-start')?.addEventListener('change', (e) => { clip.startFrame = parseInt(e.target.value)||0; fn.updateDuration(); fn.renderTimeline(); });
        document.getElementById('prop-audio-vol')?.addEventListener('input', (e) => {
            clip.data.volume = parseInt(e.target.value)/100;
            document.getElementById('prop-audio-vol-label').textContent = e.target.value + '%';
        });
        document.getElementById('prop-audio-fadein')?.addEventListener('change', (e) => { clip.data.fadeIn = parseInt(e.target.value)||0; });
        document.getElementById('prop-audio-fadeout')?.addEventListener('change', (e) => { clip.data.fadeOut = parseInt(e.target.value)||0; });
        document.getElementById('prop-audio-offset')?.addEventListener('change', (e) => { clip.data.offset = parseFloat(e.target.value)||0; });
    }

    // Model clip editors
    if (clip?.type === 'model') {
        document.getElementById('prop-model-preset')?.addEventListener('change', (e) => { clip.data.preset = e.target.value; clip.name = e.target.value; fn.renderTimeline(); });
        document.getElementById('prop-model-bodytype')?.addEventListener('change', (e) => { clip.data.bodyType = e.target.value; });
        document.getElementById('prop-model-start')?.addEventListener('change', (e) => { clip.startFrame = parseInt(e.target.value)||0; fn.updateDuration(); fn.renderTimeline(); });
        document.getElementById('prop-model-frames')?.addEventListener('change', (e) => { clip.totalFrames = Math.max(1, parseInt(e.target.value)||300); fn.updateDuration(); fn.renderTimeline(); });
    }

    // BVH clip editors
    if (clip && !clip.type || clip?.type === 'bvh') {
        document.getElementById('prop-clip-start')?.addEventListener('change', (e) => { clip.startFrame = parseInt(e.target.value)||0; fn.updateDuration(); fn.renderTimeline(); });
        document.getElementById('prop-clip-trim-in')?.addEventListener('change', (e) => { clip.trimIn = Math.max(0, Math.min(clip.totalFrames-1, parseInt(e.target.value)||0)); fn.updateDuration(); fn.renderTimeline(); });
        document.getElementById('prop-clip-trim-out')?.addEventListener('change', (e) => { clip.trimOut = Math.max(0, parseInt(e.target.value)||0); fn.updateDuration(); fn.renderTimeline(); });
        document.getElementById('prop-clip-speed')?.addEventListener('change', (e) => { clip.speed = Math.max(0.1, parseFloat(e.target.value)||1); fn.updateDuration(); fn.renderTimeline(); });
        document.getElementById('prop-clip-smooth')?.addEventListener('change', (e) => { clip.smoothSigma = Math.max(0, parseFloat(e.target.value)||0); });
        document.getElementById('prop-clip-ground')?.addEventListener('change', (e) => { clip.groundFix = e.target.checked; });
        document.getElementById('prop-clip-blend-in')?.addEventListener('change', (e) => { clip.blendIn = Math.max(0, parseInt(e.target.value)||0); });
        document.getElementById('prop-clip-blend-out')?.addEventListener('change', (e) => { clip.blendOut = Math.max(0, parseInt(e.target.value)||0); });
    }
}

export function switchPropsTab(tabName) {
    document.querySelectorAll('.props-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tabName));
    document.querySelectorAll('.props-tab-content').forEach(c => c.classList.toggle('active', c.id === `props-tab-${tabName}`));
}

// Register functions in registry
fn.updateProperties = updateProperties;
fn.switchPropsTab = switchPropsTab;

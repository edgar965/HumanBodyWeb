/**
 * BVH Studio — Properties panel (track/clip/keyframe editors).
 */
import * as THREE from 'three';
import { state, TRACK_ICONS } from './state.js';
import { fn } from './registry.js';
import { createLightHelper } from './tracks.js';

// Tauscht den THREE.js Light-Typ eines Tracks und erzeugt den Helper neu.
// Erhält Position, Farbe, Intensität, Winkel, Penumbra, Reichweite.
function _changeLightType(track, newType) {
    const oldLight = track.light;
    if (!oldLight) return;
    const pos = oldLight.position?.clone?.();
    const tgt = oldLight.target?.position?.clone?.();
    const color = oldLight.color.clone();
    const intensity = oldLight.intensity ?? 3;
    const angle = oldLight.angle ?? Math.PI / 6;
    const penumbra = oldLight.penumbra ?? 0.3;
    const distance = oldLight.distance ?? 50;

    if (oldLight.target) state.scene.remove(oldLight.target);
    state.scene.remove(oldLight);
    oldLight.dispose?.();
    if (track.lightHelper) {
        state.scene.remove(track.lightHelper);
        track.lightHelper.traverse?.(o => {
            if (o.geometry) o.geometry.dispose?.();
            if (o.material) o.material.dispose?.();
        });
        track.lightHelper = null;
    }

    let newLight;
    if (newType === 'spot') newLight = new THREE.SpotLight(color, intensity, distance, angle, penumbra, 1);
    else if (newType === 'directional') newLight = new THREE.DirectionalLight(color, intensity);
    else if (newType === 'point') newLight = new THREE.PointLight(color, intensity, distance);
    else if (newType === 'ambient') newLight = new THREE.AmbientLight(color, intensity);
    else return;
    if (pos && newLight.position) newLight.position.copy(pos);
    if (tgt && newLight.target) {
        newLight.target.position.copy(tgt);
        state.scene.add(newLight.target);
    }
    state.scene.add(newLight);
    track.light = newLight;
    track.lightType = newType;
    track.lightHelper = createLightHelper(newLight);
    if (track.lightHelper) state.scene.add(track.lightHelper);
    fn.syncLightVisibility?.();
    updateProperties();
}

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
        <div class="prop-row"><label>Name:</label><input type="text" value="${track.name}" id="prop-track-name"></div>`;
    if (track.type === 'light' || track.type === 'scene_object') {
        // Toggle-Button für Licht + Scene-Object: An/Aus statt Muted
        const on = !track.muted;
        const toggleId = track.type === 'light' ? 'prop-light-toggle' : 'prop-obj-toggle';
        html += `<div class="prop-row"><label>Sichtbar:</label>
            <button id="${toggleId}" style="padding:5px 16px;background:${on?'#4caf50':'#666'};color:#fff;border:none;border-radius:4px;cursor:pointer;font-weight:bold;min-width:60px;">${on?'An':'Aus'}</button>
        </div></div>`;
    } else {
        html += `<div class="prop-row"><label>Muted:</label><input type="checkbox" ${track.muted?'checked':''} id="prop-track-mute"></div></div>`;
    }

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
        const isAmbient   = lt === 'ambient';
        const hasPosition = !isAmbient;
        const hasTarget   = !!(L && L.target);
        const lp = L?.position || {x:0,y:0,z:0};
        const tg = L?.target?.position || {x:0,y:0,z:0};
        const lc = L ? '#' + L.color.getHexString() : '#ffffff';
        const rgb = L ? L.color : new THREE.Color(0xffffff);
        const R = Math.round(rgb.r * 255), G = Math.round(rgb.g * 255), B = Math.round(rgb.b * 255);
        const angleDeg = ((L?.angle ?? Math.PI/6) * 180 / Math.PI).toFixed(1);
        const penumbra = (L?.penumbra ?? 0.3).toFixed(2);
        const distance = (L?.distance ?? 50).toFixed(1);
        const typeOpts = [
            { v: 'spot',        label: 'SpotLight' },
            { v: 'directional', label: 'Directional' },
            { v: 'point',       label: 'PointLight' },
            { v: 'ambient',     label: 'Ambient' },
        ];
        const typeSelect = `<select id="prop-light-type" style="flex:1;">${
            typeOpts.map(o => `<option value="${o.v}" ${o.v===lt?'selected':''}>${o.label}</option>`).join('')
        }</select>`;
        html += `<div class="prop-group">
            <div class="prop-row"><label>Licht-Typ:</label>${typeSelect}${track._sceneLight ? '<span style="margin-left:6px;font-size:0.7rem;color:var(--text-muted);">(Szene)</span>' : ''}</div>
            <div class="prop-row"><label>Farbe:</label><input type="color" value="${lc}" id="prop-light-color"></div>
            <div class="prop-row"><label>R:</label><input type="range" min="0" max="255" value="${R}" id="prop-light-r" style="flex:1;"><span id="prop-light-r-val" style="width:30px;font-size:0.75rem;">${R}</span></div>
            <div class="prop-row"><label>G:</label><input type="range" min="0" max="255" value="${G}" id="prop-light-g" style="flex:1;"><span id="prop-light-g-val" style="width:30px;font-size:0.75rem;">${G}</span></div>
            <div class="prop-row"><label>B:</label><input type="range" min="0" max="255" value="${B}" id="prop-light-b" style="flex:1;"><span id="prop-light-b-val" style="width:30px;font-size:0.75rem;">${B}</span></div>
            <div class="prop-row"><label>Intensität:</label><input type="number" value="${L?.intensity||2}" id="prop-light-intensity" min="0" max="20" step="0.1"></div>
            ${!isAmbient ? `<div class="prop-row"><label>Winkel:</label><input type="number" value="${angleDeg}" id="prop-light-angle" min="1" max="170" step="1"> °</div>
            <div class="prop-row"><label>Penumbra:</label><input type="number" value="${penumbra}" id="prop-light-penumbra" min="0" max="1" step="0.05"></div>
            <div class="prop-row"><label>Reichweite:</label><input type="number" value="${distance}" id="prop-light-distance" min="0" max="200" step="1"></div>` : ''}
            ${track.lightHelper ? `
            <div class="prop-row"><label>Lichtkegel:</label>
                <button id="prop-light-cone-toggle" style="padding:5px 14px;background:${track.coneVisible !== false ? '#4caf50' : '#666'};color:#fff;border:none;border-radius:4px;cursor:pointer;font-weight:bold;min-width:50px;">${track.coneVisible !== false ? 'An' : 'Aus'}</button>
            </div>
            <div class="prop-row"><label>Helfer-Linien:</label>
                <button id="prop-light-lines-toggle" style="padding:5px 14px;background:${track.lightVisible ? '#4caf50' : '#666'};color:#fff;border:none;border-radius:4px;cursor:pointer;font-weight:bold;min-width:50px;">${track.lightVisible ? 'An' : 'Aus'}</button>
            </div>` : ''}
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
    } else if (track.type === 'scene_object') {
        const m = track.mesh;
        const pos = m?.position || { x: 0, y: 0, z: 0 };
        const rot = m?.rotation || { x: 0, y: 0, z: 0 };
        const scl = m?.scale || { x: 1, y: 1, z: 1 };
        if (track.subtype === 'floor') {
            const gridOn = state.gridVisible !== false;
            // Legacy: floorSize (quadratisch) → als Default für width/length verwenden
            const w = track.floorWidth ?? track.floorSize ?? 6;
            const l = track.floorLength ?? track.floorSize ?? 6;
            const cx = pos.x ?? 0;
            const cz = pos.z ?? 0;
            const sx = (cx - w / 2).toFixed(2);
            const ex = (cx + w / 2).toFixed(2);
            const sz = (cz - l / 2).toFixed(2);
            const ez = (cz + l / 2).toFixed(2);
            html += `<div class="prop-group">
                <div class="prop-row"><label>Typ:</label><span style="font-size:0.8rem;color:var(--accent);">Boden (Szene)</span></div>
                <div class="prop-row"><label>Farbe:</label><input type="color" value="${track.floorColor||'#3a3a4a'}" id="prop-floor-color"></div>
                <div class="prop-row"><label>Textur:</label><select id="prop-floor-texture" style="flex:1;"><option value="">(Lade...)</option></select></div>
                <div class="prop-row"><label>Rauheit:</label><input type="number" value="${(track.floorRoughness??0.9).toFixed(2)}" id="prop-floor-roughness" min="0" max="1" step="0.05"></div>
                <div class="prop-row"><label>Metall:</label><input type="number" value="${(track.floorMetalness??0.05).toFixed(2)}" id="prop-floor-metalness" min="0" max="1" step="0.05"></div>
                <h3 style="font-size:0.8rem;color:var(--text-muted);margin:8px 0 4px;">Abmessungen (Mittelpunkt-bezogen)</h3>
                <div class="prop-row"><label>Breite X:</label><input type="number" value="${w.toFixed(2)}" id="prop-floor-width" min="0.2" max="200" step="0.1"> m</div>
                <div class="prop-row"><label>Länge Z:</label><input type="number" value="${l.toFixed(2)}" id="prop-floor-length" min="0.2" max="200" step="0.1"> m</div>
                <h3 style="font-size:0.8rem;color:var(--text-muted);margin:8px 0 4px;">Kanten-Positionen</h3>
                <div class="prop-row"><label>Start X:</label><input type="number" value="${sx}" id="prop-floor-sx" step="0.1"> m</div>
                <div class="prop-row"><label>Ende X:</label><input type="number" value="${ex}" id="prop-floor-ex" step="0.1"> m</div>
                <div class="prop-row"><label>Start Z:</label><input type="number" value="${sz}" id="prop-floor-sz" step="0.1"> m</div>
                <div class="prop-row"><label>Ende Z:</label><input type="number" value="${ez}" id="prop-floor-ez" step="0.1"> m</div>
                <div class="prop-row"><label>Raster:</label>
                    <button id="prop-floor-grid" style="padding:5px 16px;background:${gridOn?'#4caf50':'#666'};color:#fff;border:none;border-radius:4px;cursor:pointer;font-weight:bold;min-width:60px;">${gridOn?'An':'Aus'}</button>
                </div>
                <div style="margin-top:6px;font-size:0.7rem;color:var(--text-muted);">Breite/Länge wachsen um den aktuellen Mittelpunkt. Start/Ende-Kanten editieren verschiebt nur die jeweilige Kante (Gegen-Kante bleibt fix).</div>
            </div>`;
        } else {
            html += `<div class="prop-group">
                <div class="prop-row"><label>Typ:</label><span style="font-size:0.8rem;color:var(--accent);">3D-Objekt (${track.objectExt||'?'})</span></div>
                <div class="prop-row"><label>Tönung:</label><input type="color" value="${track.objectTint||'#ffffff'}" id="prop-obj-tint"></div>
                <h3 style="font-size:0.8rem;color:var(--text-muted);margin:8px 0 4px;">Position</h3>
                <div class="prop-row"><label>X:</label><input type="number" step="0.1" value="${pos.x.toFixed(2)}" id="prop-obj-px"></div>
                <div class="prop-row"><label>Y:</label><input type="number" step="0.1" value="${pos.y.toFixed(2)}" id="prop-obj-py"></div>
                <div class="prop-row"><label>Z:</label><input type="number" step="0.1" value="${pos.z.toFixed(2)}" id="prop-obj-pz"></div>
                <h3 style="font-size:0.8rem;color:var(--text-muted);margin:8px 0 4px;">Rotation (Grad)</h3>
                <div class="prop-row"><label>X:</label><input type="number" step="1" value="${(rot.x*180/Math.PI).toFixed(1)}" id="prop-obj-rx"></div>
                <div class="prop-row"><label>Y:</label><input type="number" step="1" value="${(rot.y*180/Math.PI).toFixed(1)}" id="prop-obj-ry"></div>
                <div class="prop-row"><label>Z:</label><input type="number" step="1" value="${(rot.z*180/Math.PI).toFixed(1)}" id="prop-obj-rz"></div>
                <h3 style="font-size:0.8rem;color:var(--text-muted);margin:8px 0 4px;">Größe</h3>
                <div class="prop-row"><label>Scale:</label><input type="number" step="0.05" min="0.01" max="100" value="${scl.x.toFixed(2)}" id="prop-obj-scale"></div>
                <div class="prop-row"><label>Modus:</label>
                    <select id="prop-obj-gizmo"><option value="translate" selected>Verschieben</option><option value="rotate">Rotieren</option><option value="scale">Skalieren</option></select>
                </div>
                <h3 style="font-size:0.8rem;color:var(--text-muted);margin:10px 0 4px;">Material</h3>
                ${(() => {
                    // Sammle aktuell auf dem Mesh anliegende Texturen (.map.image.src)
                    const active = new Set();
                    track.mesh?.traverse?.(o => {
                        if (o.isMesh && o.material) {
                            const mats = Array.isArray(o.material) ? o.material : [o.material];
                            for (const m of mats) {
                                const src = m.map?.image?.src || m.map?.source?.data?.src;
                                if (src) active.add(src);
                            }
                        }
                    });
                    if (active.size === 0) return `<div class="prop-row" style="font-size:0.7rem;color:var(--danger);"><label>&nbsp;</label>Keine Textur geladen</div>`;
                    return Array.from(active).slice(0, 4).map(src => `
                        <div class="prop-row" style="align-items:flex-start;">
                            <label>Aktiv:</label>
                            <div style="flex:1;display:flex;flex-direction:column;gap:3px;">
                                <img src="${src}" style="max-width:140px;max-height:90px;border:1px solid var(--border);border-radius:3px;background:#000;object-fit:contain;" />
                                <span style="font-size:0.65rem;color:var(--text-muted);word-break:break-all;">${(src.split('/').pop() || '?').slice(0, 40)}</span>
                            </div>
                        </div>
                    `).join('');
                })()}
                <div class="prop-row"><label>Textur:</label>
                    <button id="prop-obj-tex-replace" style="padding:4px 8px;font-size:0.72rem;background:var(--accent);color:#fff;border:none;border-radius:3px;cursor:pointer;"><i class="fas fa-image"></i> Ersetzen…</button>
                    <button id="prop-obj-tex-remove" style="padding:4px 8px;font-size:0.72rem;background:var(--bg-card);color:var(--text);border:1px solid var(--border);border-radius:3px;cursor:pointer;margin-left:4px;">Entfernen</button>
                </div>
                <div class="prop-row"><label>MTL:</label>
                    <button id="prop-obj-mtl-replace" style="padding:4px 8px;font-size:0.72rem;background:var(--accent);color:#fff;border:none;border-radius:3px;cursor:pointer;"><i class="fas fa-file-code"></i> Ersetzen…</button>
                    ${track.objectMtlUrl ? `<span style="margin-left:6px;font-size:0.65rem;color:var(--text-muted);">${track.objectMtlUrl.split('/').pop()}</span>` : `<span style="margin-left:6px;font-size:0.65rem;color:var(--danger);">fehlt</span>`}
                </div>
                <div class="prop-row"><label>Mesh:</label>
                    <button id="prop-obj-mesh-replace" style="padding:4px 8px;font-size:0.72rem;background:var(--accent);color:#fff;border:none;border-radius:3px;cursor:pointer;"><i class="fas fa-cube"></i> Ersetzen…</button>
                    ${track.objectUrl ? `<span style="margin-left:6px;font-size:0.65rem;color:var(--text-muted);">${track.objectUrl.split('/').pop()}</span>` : ''}
                </div>
                <div style="margin-top:6px;font-size:0.7rem;color:var(--text-muted);">Tipp: Beim Import OBJ + MTL + alle Texturen gleichzeitig auswählen (Ctrl+Klick im Datei-Dialog). Sonst werden sie nicht im selben Bundle-Ordner abgelegt und MTL→Textur-Referenzen schlagen fehl.</div>
            </div>`;
        }
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
                <div class="prop-row"><label>Fade-Effekt:</label><input type="checkbox" ${d.fade !== false ? 'checked' : ''} id="prop-kf-fade"> <span style="font-size:0.72rem;color:var(--text-muted);margin-left:4px;">aus = Sprung</span></div>
                <div class="prop-row"><label>Interp.:</label>
                    <select id="prop-kf-interp" ${d.fade === false ? 'disabled' : ''}>
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
                ${d.angle != null ? `<div class="prop-row"><label>Winkel:</label><input type="number" value="${(d.angle*180/Math.PI).toFixed(1)}" id="prop-lkf-angle" min="1" max="170" step="1"> °</div>` : ''}
                ${d.penumbra != null ? `<div class="prop-row"><label>Penumbra:</label><input type="number" value="${d.penumbra.toFixed(2)}" id="prop-lkf-penumbra" min="0" max="1" step="0.05"></div>` : ''}
                ${d.distance != null ? `<div class="prop-row"><label>Reichweite:</label><input type="number" value="${d.distance.toFixed(1)}" id="prop-lkf-distance" min="0" max="200" step="1"></div>` : ''}
                <div class="prop-row"><label>Licht:</label>
                    <button id="prop-lkf-visible" style="padding:4px 12px;background:${(d.visible !== false)?'#4caf50':'#666'};color:#fff;border:none;border-radius:4px;cursor:pointer;font-weight:bold;min-width:50px;">${(d.visible !== false)?'An':'Aus'}</button>
                </div>
                <div class="prop-row"><label>Fade-Effekt:</label><input type="checkbox" ${d.fade !== false ? 'checked' : ''} id="prop-lkf-fade"> <span style="font-size:0.72rem;color:var(--text-muted);margin-left:4px;">aus = Sprung</span></div>
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
        } else if (clip.type === 'object_clip') {
            const d = clip.data || {};
            html += `<div class="prop-group">
                <h3 style="font-size:0.85rem;color:var(--accent);">3D-Objekt Clip</h3>
                <div class="prop-row"><label>Datei:</label><span style="font-size:0.75rem;color:var(--text-muted);">${d.fileName || '—'}</span></div>
                <div class="prop-row"><label>Start:</label><input type="number" value="${clip.startFrame}" id="prop-oc-start" min="0"> <span style="font-size:0.7rem;">f</span></div>
                <div class="prop-row"><label>Dauer:</label><input type="number" value="${clip.totalFrames}" id="prop-oc-frames" min="1"> <span style="font-size:0.7rem;">f</span></div>
                <div style="margin-top:6px;font-size:0.7rem;color:var(--text-muted);">Objekt ist in der Szene sichtbar wenn der Playhead im Clip-Bereich ist. Position/Rotation/Größe über die Track-Eigenschaften oben.</div>
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
    document.getElementById('prop-track-mute')?.addEventListener('change', (e) => {
        track.muted = e.target.checked;
    });
    // Licht: Toggle-Button An/Aus
    document.getElementById('prop-light-toggle')?.addEventListener('click', () => {
        track.muted = !track.muted;
        if (track.light) {
            track.light.visible = !track.muted;
            if (track.lightHelper) track.lightHelper.visible = !track.muted && track.lightVisible;
        }
        fn.updateProperties();  // Re-render damit Button-Text/Farbe sich updated
    });
    // Scene-Object: Toggle-Button An/Aus (Sichtbarkeit des Mesh)
    document.getElementById('prop-obj-toggle')?.addEventListener('click', () => {
        track.muted = !track.muted;
        if (track.mesh) track.mesh.visible = !track.muted;
        fn.updateProperties();
    });
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
    document.getElementById('prop-light-type')?.addEventListener('change', (e) => {
        _changeLightType(track, e.target.value);
    });
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
    });
    document.getElementById('prop-light-cone-toggle')?.addEventListener('click', () => {
        track.coneVisible = !(track.coneVisible !== false);  // toggle; undefined→true→false
        updateProperties();
    });
    document.getElementById('prop-light-lines-toggle')?.addEventListener('click', () => {
        track.lightVisible = !track.lightVisible;
        updateProperties();
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

    // Scene-Object: Boden
    if (track.type === 'scene_object' && track.subtype === 'floor') {
        document.getElementById('prop-floor-color')?.addEventListener('input', (e) => {
            track.floorColor = e.target.value;
            fn.updateFloorMaterial?.(track);
        });
        document.getElementById('prop-floor-roughness')?.addEventListener('change', (e) => {
            track.floorRoughness = parseFloat(e.target.value)||0.9;
            fn.updateFloorMaterial?.(track);
        });
        document.getElementById('prop-floor-metalness')?.addEventListener('change', (e) => {
            track.floorMetalness = parseFloat(e.target.value)||0.05;
            fn.updateFloorMaterial?.(track);
        });
        // Breite/Länge: wachsen zentriert um den aktuellen Mittelpunkt
        document.getElementById('prop-floor-width')?.addEventListener('change', (e) => {
            const w = Math.max(0.2, parseFloat(e.target.value) || 6);
            const l = track.floorLength ?? track.floorSize ?? 6;
            fn.setFloorGeometry?.(track, w, l);  // Mittelpunkt unverändert
            updateProperties();
        });
        document.getElementById('prop-floor-length')?.addEventListener('change', (e) => {
            const l = Math.max(0.2, parseFloat(e.target.value) || 6);
            const w = track.floorWidth ?? track.floorSize ?? 6;
            fn.setFloorGeometry?.(track, w, l);
            updateProperties();
        });
        // Start/Ende-Kanten: Gegen-Kante bleibt fix, neue Breite/Länge + neuer Mittelpunkt
        const _editFloorEdge = (axis, side, newVal) => {
            const center = track.mesh.position;
            const curW = track.floorWidth ?? track.floorSize ?? 6;
            const curL = track.floorLength ?? track.floorSize ?? 6;
            let w = curW, l = curL, cx = center.x, cz = center.z;
            if (axis === 'x') {
                const other = side === 'start' ? (center.x + curW / 2) : (center.x - curW / 2);
                const nw = Math.max(0.2, Math.abs(other - newVal));
                cx = (newVal + other) / 2;
                w = nw;
            } else {
                const other = side === 'start' ? (center.z + curL / 2) : (center.z - curL / 2);
                const nl = Math.max(0.2, Math.abs(other - newVal));
                cz = (newVal + other) / 2;
                l = nl;
            }
            fn.setFloorGeometry?.(track, w, l, cx, cz);
            updateProperties();
        };
        document.getElementById('prop-floor-sx')?.addEventListener('change', (e) => _editFloorEdge('x', 'start', parseFloat(e.target.value) || 0));
        document.getElementById('prop-floor-ex')?.addEventListener('change', (e) => _editFloorEdge('x', 'end',   parseFloat(e.target.value) || 0));
        document.getElementById('prop-floor-sz')?.addEventListener('change', (e) => _editFloorEdge('z', 'start', parseFloat(e.target.value) || 0));
        document.getElementById('prop-floor-ez')?.addEventListener('change', (e) => _editFloorEdge('z', 'end',   parseFloat(e.target.value) || 0));
        document.getElementById('prop-floor-grid')?.addEventListener('click', () => {
            state.gridVisible = state.gridVisible === false ? true : false;
            // Grid-Helper in der Szene ein-/ausblenden — THREE.GridHelper hat type='GridHelper'
            state.scene?.traverse(o => {
                if (o.type === 'GridHelper' || o.isGridHelper) o.visible = state.gridVisible;
            });
            fn.updateProperties();
        });
        // Texturen-Dropdown asynchron befüllen
        const texSel = document.getElementById('prop-floor-texture');
        if (texSel && fn.getFloorTextures) {
            fn.getFloorTextures().then(textures => {
                texSel.innerHTML = '';
                for (const t of textures) {
                    const opt = document.createElement('option');
                    opt.value = t.url || '';
                    opt.textContent = t.label;
                    if ((track.floorTexture || 'none') === t.name) opt.selected = true;
                    texSel.appendChild(opt);
                }
                texSel.addEventListener('change', (e) => {
                    fn.applyFloorTexture?.(track, e.target.value);
                });
            });
        }
    }
    // Scene-Object: Custom 3D
    if (track.type === 'scene_object' && track.subtype === 'custom' && track.mesh) {
        const applyUpdate = () => { /* mesh is directly mutated */ };
        document.getElementById('prop-obj-tint')?.addEventListener('input', (e) => {
            fn.setObjectTint?.(track, e.target.value);
        });
        ['px','py','pz'].forEach((id, i) => {
            const axis = ['x','y','z'][i];
            document.getElementById(`prop-obj-${id}`)?.addEventListener('change', (e) => {
                track.mesh.position[axis] = parseFloat(e.target.value)||0;
            });
        });
        ['rx','ry','rz'].forEach((id, i) => {
            const axis = ['x','y','z'][i];
            document.getElementById(`prop-obj-${id}`)?.addEventListener('change', (e) => {
                track.mesh.rotation[axis] = (parseFloat(e.target.value)||0) * Math.PI / 180;
            });
        });
        document.getElementById('prop-obj-scale')?.addEventListener('change', (e) => {
            const s = Math.max(0.01, parseFloat(e.target.value)||1);
            track.mesh.scale.setScalar(s);
        });
        document.getElementById('prop-obj-gizmo')?.addEventListener('change', (e) => {
            fn.setTransformMode?.(e.target.value);
        });

        // Helper: Bundle-ID aus existierender OBJ-URL extrahieren (für Co-Location)
        const extractBundleId = () => {
            const m = (track.objectUrl || '').match(/\/scene_objects\/(obj_[^/]+)\//);
            return m ? m[1] : null;
        };
        const uploadToBundle = async (file) => {
            const fd = new FormData();
            fd.append('object', file);
            const bundleId = extractBundleId();
            if (bundleId) fd.append('bundleId', bundleId);
            const resp = await fetch('/api/studio/scene-object-upload/', { method: 'POST', body: fd });
            const data = await resp.json();
            if (!data.ok) throw new Error(data.error || 'Upload fehlgeschlagen');
            return data;
        };
        const openFilePicker = (accept) => new Promise(res => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = accept;
            input.addEventListener('change', () => res(input.files[0] || null));
            input.click();
        });

        // Textur ersetzen
        document.getElementById('prop-obj-tex-replace')?.addEventListener('click', async () => {
            try {
                const file = await openFilePicker('image/png,image/jpeg,image/jpg,image/webp');
                if (!file) return;
                const up = await uploadToBundle(file);
                const texLoader = new THREE.TextureLoader();
                const tex = await texLoader.loadAsync(up.url);
                tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
                tex.colorSpace = THREE.SRGBColorSpace;
                track.mesh.traverse(o => {
                    if (o.isMesh && o.material) {
                        const mats = Array.isArray(o.material) ? o.material : [o.material];
                        for (const m of mats) {
                            if (m.map) m.map.dispose();
                            m.map = tex;
                            m.needsUpdate = true;
                        }
                    }
                });
                track.objectTextureUrl = up.url;
                fn.serverLog?.('obj_texture_replaced', `track=${track.name} file=${file.name}`);
                updateProperties();
            } catch (e) { alert('Textur-Upload fehlgeschlagen: ' + e.message); }
        });

        // Textur entfernen
        document.getElementById('prop-obj-tex-remove')?.addEventListener('click', () => {
            track.mesh.traverse(o => {
                if (o.isMesh && o.material) {
                    const mats = Array.isArray(o.material) ? o.material : [o.material];
                    for (const m of mats) {
                        if (m.map) { m.map.dispose(); m.map = null; m.needsUpdate = true; }
                    }
                }
            });
            track.objectTextureUrl = null;
            updateProperties();
        });

        // MTL ersetzen: neue Materialien laden und alle Meshes neu materialisieren
        document.getElementById('prop-obj-mtl-replace')?.addEventListener('click', async () => {
            try {
                const file = await openFilePicker('.mtl');
                if (!file) return;
                const up = await uploadToBundle(file);
                const { MTLLoader } = await import('three/addons/loaders/MTLLoader.js');
                const basePath = up.url.substring(0, up.url.lastIndexOf('/') + 1);
                const mtlLoader = new MTLLoader();
                mtlLoader.setPath(basePath);
                const mtlName = up.url.substring(up.url.lastIndexOf('/') + 1);
                const materials = await mtlLoader.loadAsync(mtlName);
                materials.preload();
                // Erstes Material aus dem MTL auf alle Child-Meshes anwenden
                const matEntries = Object.entries(materials.materials || {});
                if (matEntries.length === 0) { alert('MTL enthält keine Materialien'); return; }
                const primary = matEntries[0][1];
                track.mesh.traverse(o => {
                    if (o.isMesh) {
                        // Falls mehrere Materialien im MTL: versuche Match per Namen, sonst primary
                        const byName = materials.materials[o.material?.name];
                        if (o.material) {
                            const mats = Array.isArray(o.material) ? o.material : [o.material];
                            mats.forEach(m => m.dispose?.());
                        }
                        o.material = byName || primary;
                    }
                });
                track.objectMtlUrl = up.url;
                // Merke mtlUrl auch in clip.data damit Save/Restore die neue Referenz nutzt
                const objClip = track.clips.find(c => c.type === 'object_clip');
                if (objClip) objClip.data = { ...objClip.data, mtlUrl: up.url };
                fn.serverLog?.('obj_mtl_replaced', `track=${track.name} file=${file.name}`);
            } catch (e) { alert('MTL-Upload fehlgeschlagen: ' + e.message); }
        });

        // Mesh (OBJ/GLB) ersetzen — Position/Rotation/Scale übernehmen
        document.getElementById('prop-obj-mesh-replace')?.addEventListener('click', async () => {
            try {
                const file = await openFilePicker('.obj,.glb,.gltf,.fbx');
                if (!file) return;
                const up = await uploadToBundle(file);
                // Alte Transform merken
                const oldPos = track.mesh.position.clone();
                const oldRot = track.mesh.rotation.clone();
                const oldScale = track.mesh.scale.x;
                // Clip anpassen: URL ersetzen
                const objClip = track.clips.find(c => c.type === 'object_clip');
                if (objClip) objClip.data = { ...objClip.data, url: up.url, fileName: file.name, ext: up.ext };
                const se = await import('./scene_extras.js');
                await se._loadSceneObjectIntoTrack(track, up.url, file.name, up.ext, objClip?.startFrame || 0, null);
                // Auto-Normalize überschreiben mit alter Transform
                if (track.mesh) {
                    track.mesh.position.copy(oldPos);
                    track.mesh.rotation.copy(oldRot);
                    track.mesh.scale.setScalar(oldScale);
                }
                // _loadSceneObjectIntoTrack pushte einen neuen Clip → Duplikat entfernen
                // (wir haben den ursprünglichen Clip mit aktualisierter URL bereits)
                const clips = track.clips.filter(c => c.type === 'object_clip');
                if (clips.length > 1) {
                    // Behalte den letzten (neu gepushten) und entferne die alten mit veralteter URL?
                    // Einfacher: entferne den neuesten Duplikat-Clip
                    const idx = track.clips.lastIndexOf(clips[clips.length - 1]);
                    if (idx >= 0) track.clips.splice(idx, 1);
                }
                fn.serverLog?.('obj_mesh_replaced', `track=${track.name} file=${file.name}`);
                updateProperties();
            } catch (e) { alert('Mesh-Upload fehlgeschlagen: ' + e.message); }
        });
    }

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
        document.getElementById('prop-kf-fade')?.addEventListener('change', (e) => {
            clip.data.fade = e.target.checked;
            updateProperties();  // Interp-Select aktivieren/deaktivieren
        });
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
        document.getElementById('prop-lkf-angle')?.addEventListener('change', (e) => { clip.data.angle = (parseFloat(e.target.value)||30)*Math.PI/180; });
        document.getElementById('prop-lkf-penumbra')?.addEventListener('change', (e) => { clip.data.penumbra = Math.max(0,Math.min(1,parseFloat(e.target.value)||0)); });
        document.getElementById('prop-lkf-distance')?.addEventListener('change', (e) => { clip.data.distance = parseFloat(e.target.value)||50; });
        document.getElementById('prop-lkf-fade')?.addEventListener('change', (e) => { clip.data.fade = e.target.checked; });
        document.getElementById('prop-lkf-visible')?.addEventListener('click', () => {
            clip.data.visible = !(clip.data.visible !== false);  // toggle; undefined → true
            updateProperties();
            fn.renderTimeline?.();
        });
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

    // Object-Clip editors (3D-Objekt auf scene_object track)
    if (clip?.type === 'object_clip') {
        document.getElementById('prop-oc-start')?.addEventListener('change', (e) => {
            clip.startFrame = Math.max(0, parseInt(e.target.value) || 0);
            fn.updateDuration(); fn.renderTimeline(); fn.applyPlayhead();
        });
        document.getElementById('prop-oc-frames')?.addEventListener('change', (e) => {
            clip.totalFrames = Math.max(1, parseInt(e.target.value) || 300);
            fn.updateDuration(); fn.renderTimeline(); fn.applyPlayhead();
        });
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

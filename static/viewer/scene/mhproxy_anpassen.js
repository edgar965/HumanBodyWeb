/**
 * MakeHuman-Proxy an den Koerper anpassen.
 *
 * Aus mh_proxy.js herausgeloest (Umbau 16.08.2026).
 */

import * as THREE from 'three';
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { _bindSlider, _charQueryParams, _selectedInst, _selectedMHMesh,
         _sliderVal } from './utils.js';
import { _skinifyMesh, convertInstToSkinned } from './skeleton.js';
import { base64ToFloat32, base64ToUint32, blenderToThreeCoords } from '../gemeinsam/kodierung.js';
import { Materialregler } from './materialregler.js';
import { Mhverformung } from './mhproxy_verformung.js';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Protokoll } from '../gemeinsam/protokoll.js';


// EINE Anpassung zur Zeit (Review 15.08.2026).
//
// Der Serverteil des Proxy-Fits braucht gemessene 1,14 s (13.08.2026), und es
// gibt ZWEI Auslöser: den Knopf (Zeile ~131) und den entprellten Refit beim
// Schieben eines Reglers (Zeile ~52, 400 ms). Wer einen Regler bewegt und dann
// auf „Anpassen" klickt, hat also zwei Anfragen gleichzeitig unterwegs — und
// beide entfernen dasselbe Netz aus `inst.clothMeshes`, geben Geometrie und
// Material frei und schreiben ihr Ergebnis zurück. Der langsamere gewinnt,
// egal welche Werte er hatte.
//
// Statt zu sperren und den Klick zu verlieren, wird der letzte Wunsch gemerkt
// und nach dem laufenden Fit EINMAL nachgezogen: Beim Schieben eines Reglers
// ist „der letzte Stand gewinnt" die richtige Antwort.
let _mhFitLaeuft = false;

let _mhFitNachziehen = false;

async function _doMHProxyFit() {
    if (_mhFitLaeuft) { _mhFitNachziehen = true; return; }
    _mhFitLaeuft = true;
    try {
        await _mhProxyFitAusfuehren();
    } finally {
        _mhFitLaeuft = false;
    }
    if (_mhFitNachziehen) {
        _mhFitNachziehen = false;
        await _doMHProxyFit();
    }
}

async function _mhProxyFitAusfuehren() {
    if (!state._selectedMHId) return;
    const inst = _selectedInst();
    if (!inst) return;
    const p = {
        color: document.getElementById('mh-color')?.value || '#4d5980',
        offset: _sliderVal('mh-offset'),
        stiffness: _sliderVal('mh-stiffness'),
        scale: _sliderVal('mh-scale'),
        y_offset: _sliderVal('mh-y-offset'),
        push_dist: _sliderVal('mh-push-dist') || 3,
        roughness: _sliderVal('mh-roughness'),
        metalness: _sliderVal('mh-metalness'),
        opacity: _sliderVal('mh-opacity'),
    };
    await _fitMHProxyOnInst(inst, state._selectedMHId, p);
    const stored = inst.mhProxies?.[state._selectedMHId];
    if (stored) {
        const colorEl = document.getElementById('mh-color');
        if (colorEl) colorEl.value = stored.color;
        const propColorEl = document.getElementById('prop-mh-color');
        if (propColorEl) propColorEl.value = stored.color;
    }
    fn.updateEquippedList?.(inst);
    fn.updateVertexCount?.();
}

async function _fitMHProxyOnInst(inst, garmentId, p) {
    if (!inst.isSkinned && state.rigifySkeletonData && state.skinWeightData) {
        convertInstToSkinned(inst);
    }

    const params = _charQueryParams(inst);
    params.set('garment_id', garmentId);

    const c = new THREE.Color(p.color || '#4d5980');
    params.set('color_r', c.r.toFixed(3));
    params.set('color_g', c.g.toFixed(3));
    params.set('color_b', c.b.toFixed(3));
    params.set('offset', ((p.offset ?? 0) / 1000).toFixed(4));
    params.set('stiffness', ((p.stiffness ?? 50) / 100).toFixed(2));
    params.set('scale', ((p.scale ?? 100) / 100).toFixed(3));
    params.set('y_offset', ((p.y_offset ?? 0) / 1000).toFixed(4));
    params.set('push_dist', String(p.push_dist ?? 3));
    params.set('use_mh_body', '1');
    params.set('tpose_displacement', p.tpose_disp ?? window._mhTposeDisplacement ?? '1');

    try {
        const data = await Serverabruf.json(`/api/character/mh-proxy-fit/?${params}`);
        if (data.error) { console.warn('MH proxy fit error:', data.error); return; }

        const key = `mh_${garmentId}`;

        if (inst.clothMeshes[key]) {
            inst.group.remove(inst.clothMeshes[key]);
            inst.clothMeshes[key].geometry.dispose();
            inst.clothMeshes[key].material.dispose();
            delete inst.clothMeshes[key];
        }

        const vertBuf = base64ToFloat32(data.vertices);
        blenderToThreeCoords(vertBuf);
        const faceBuf = base64ToUint32(data.faces);
        const normalBuf = base64ToFloat32(data.normals);
        blenderToThreeCoords(normalBuf);

        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geo.setIndex(new THREE.BufferAttribute(faceBuf, 1));
        geo.setAttribute('normal', new THREE.BufferAttribute(normalBuf, 3));

        const roughness = (p.roughness ?? 50) / 100;
        const metalness = (p.metalness ?? 0) / 100;
        const opacity = (p.opacity ?? 100) / 100;

        let matColor = c;
        if (data.mat_color && !data.has_texture) {
            matColor = new THREE.Color(data.mat_color[0], data.mat_color[1], data.mat_color[2]);
        } else if (data.has_texture) {
            matColor = new THREE.Color(1, 1, 1);
        }

        const mat = new THREE.MeshStandardMaterial({
            color: matColor, roughness, metalness, side: THREE.DoubleSide,
            polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1,
            transparent: opacity < 1, opacity,
        });

        if (data.has_texture && data.texture_name) {
            const texUrl = `/api/character/garment/texture/${encodeURIComponent(garmentId)}/${encodeURIComponent(data.texture_name)}/`;
            new THREE.TextureLoader().load(texUrl, (tex) => {
                tex.colorSpace = THREE.SRGBColorSpace;
                mat.map = tex;
                mat.needsUpdate = true;
            });
        }

        const mesh = _skinifyMesh(geo, mat, inst, data);
        inst.clothMeshes[key] = mesh;
        inst.group.add(mesh);
        inst.garmentOrigPositions[key] = new Float32Array(vertBuf);

        inst.mhProxies = inst.mhProxies || {};
        inst.mhProxies[garmentId] = {
            id: garmentId,
            color: '#' + matColor.getHexString(),
            offset: p.offset ?? 0,
            stiffness: p.stiffness ?? 50,
            scale: p.scale ?? 100,
            y_offset: p.y_offset ?? 0,
            push_dist: p.push_dist ?? 3,
            roughness: p.roughness ?? 50,
            metalness: p.metalness ?? 0,
            opacity: p.opacity ?? 100,
        };

        Protokoll.debug('MH', `fit: ${garmentId} (${data.vertex_count} verts)`);
        fn.markDirty?.(`MH ${garmentId}`);
    } catch (e) {
        console.error('MH proxy fit failed:', e);
    }
}

function _syncPropMHControls() {
    const sel = _selectedMHMesh();
    if (!sel) return;
    const mat = sel.mesh.material;
    // Sync material sliders
    const setV = (id, valId, v, fmt) => {
        const el = document.getElementById(id);
        const sp = document.getElementById(valId);
        if (el) el.value = v;
        if (sp) sp.textContent = fmt(v);
    };
    setV('prop-mh-roughness', 'prop-mh-roughness-val', Math.round(mat.roughness * 100), v => (v/100).toFixed(2));
    setV('prop-mh-metalness', 'prop-mh-metalness-val', Math.round(mat.metalness * 100), v => (v/100).toFixed(2));
    setV('prop-mh-opacity', 'prop-mh-opacity-val', Math.round(mat.opacity * 100), v => (v/100).toFixed(2));
    const colorEl = document.getElementById('prop-mh-color');
    if (colorEl) colorEl.value = '#' + mat.color.getHexString();
    // Sync transform sliders from asset tab values
    const syncFrom = (propId, srcId) => {
        const s = document.getElementById(srcId);
        const p = document.getElementById(propId);
        if (s && p) p.value = s.value;
    };
    syncFrom('prop-mh-stiffness', 'mh-stiffness');
    syncFrom('prop-mh-offset', 'mh-offset');
    syncFrom('prop-mh-scale', 'mh-scale');
    syncFrom('prop-mh-y-offset', 'mh-y-offset');
    // Update value displays
    _bindSlider('prop-mh-stiffness', 'prop-mh-stiffness-val', v => (v / 100).toFixed(2));
    _bindSlider('prop-mh-offset', 'prop-mh-offset-val', v => (v / 1000).toFixed(3));
    _bindSlider('prop-mh-scale', 'prop-mh-scale-val', v => v + '%');
    _bindSlider('prop-mh-y-offset', 'prop-mh-y-offset-val', v => v + ' mm');
    _bindSlider('prop-mh-roughness', 'prop-mh-roughness-val', v => (v/100).toFixed(2));
    _bindSlider('prop-mh-metalness', 'prop-mh-metalness-val', v => (v/100).toFixed(2));
    _bindSlider('prop-mh-opacity', 'prop-mh-opacity-val', v => (v/100).toFixed(2));
}

/**
 * Bedienung im Eigenschaften-Reiter. Sie zeigt dieselben Werte wie der
 * Assets-Reiter, nur unter `prop-`-Kennungen — deshalb kommen Material und
 * Verformung aus denselben Klassen (`Materialregler`, `Mhverformung`). Vorher
 * standen hier 106 Zeilen, davon 60 als Zeile-fuer-Zeile-Kopie des
 * Herausdrueckens aus dem Assets-Reiter.
 */
function _initPropMHControls() {
    new Materialregler('prop-mh', _selectedMHMesh).grundwerte().deckkraft();

    // Die vier Anpassregler spiegeln auf den Assets-Reiter: dort haengt die
    // Neuanpassung am Server. Waehrend des Ziehens nur den Wert nachziehen,
    // beim Loslassen das `change`-Ereignis weitergeben.
    for (const [hier, dort] of [['prop-mh-stiffness', 'mh-stiffness'],
                                ['prop-mh-offset', 'mh-offset'],
                                ['prop-mh-scale', 'mh-scale'],
                                ['prop-mh-y-offset', 'mh-y-offset']]) {
        const regler = document.getElementById(hier);
        if (!regler) continue;
        const spiegeln = (weiter) => {
            const ziel = document.getElementById(dort);
            if (!ziel) return;
            ziel.value = regler.value;
            if (weiter) ziel.dispatchEvent(new Event('change'));
        };
        regler.addEventListener('input', () => spiegeln(false));
        regler.addEventListener('change', () => spiegeln(true));
    }

    _bindSlider('prop-mh-push-dist', 'prop-mh-push-dist-val', v => v + ' mm');
    const verformung = new Mhverformung('prop-mh');
    document.getElementById('prop-mh-push')
        ?.addEventListener('click', () => verformung.herausdruecken());
    document.getElementById('prop-mh-push-undo')
        ?.addEventListener('click', () => verformung.zuruecknehmen());
}

export { _doMHProxyFit, _fitMHProxyOnInst, _syncPropMHControls, _initPropMHControls };

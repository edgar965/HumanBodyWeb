/**
 * Viewer — WebSocket for live morphing.
 */
import { state, WS_PATH } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { updateMeshVertices, reloadMeshForBodyType } from './mesh.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Morphdrossel } from '../gemeinsam/morphdrossel.js';

export function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${protocol}://${window.location.host}${WS_PATH}`;

    state.ws = new WebSocket(url);
    state.ws.binaryType = 'arraybuffer';

    state.ws.onopen = () => {
        state.wsReady = true;
        const wsEl = document.getElementById('ws-status');
        if (wsEl) { wsEl.textContent = 'Connected'; wsEl.className = 'connected'; }
        const btSelect = document.getElementById('body-type-select');
        if (btSelect && btSelect.value) {
            wsSend({ type: 'body_type', value: btSelect.value });
        }
        _resyncMorphsOnReconnect();
    };

    state.ws.onclose = () => {
        state.wsReady = false;
        const wsEl = document.getElementById('ws-status');
        if (wsEl) { wsEl.textContent = 'Disconnected'; wsEl.className = 'disconnected'; }
        setTimeout(connectWebSocket, Zeiten.VERBINDEN_MS);
    };

    state.ws.onerror = (e) => {
        console.error('WebSocket error:', e);
    };

    state.ws.onmessage = (event) => {
        if (event.data instanceof ArrayBuffer) {
            updateMeshVertices(event.data);
        } else {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'error') {
                    console.error('Server error:', msg.message);
                } else if (msg.type === 'reload_mesh') {
                    reloadMeshForBodyType(msg.body_type, msg.gender);
                }
            } catch (e) {
                Protokoll.debug('websocket', 'Nachricht nicht verwertbar', e);
                // ignore
            }
        }
    };
}

export function wsSend(msg) {
    if (state.ws && state.wsReady) {
        state.ws.send(JSON.stringify(msg));
    }
}

function _resyncMorphsOnReconnect() {
    const morphBatch = {};
    document.querySelectorAll('#morphs-panel input[type="range"][data-morph]').forEach(s => {
        const v = parseInt(s.value) / 100.0;
        if (Math.abs(v) > 0.001) morphBatch[s.dataset.morph] = v;
    });
    if (Object.keys(morphBatch).length > 0) {
        wsSend({ type: 'morph_batch', morphs: morphBatch });
    }
    ['age', 'mass', 'tone', 'height'].forEach(name => {
        const el = document.getElementById(`meta-${name}`);
        if (!el) return;
        const dv = parseInt(el.value);
        const mn = parseInt(el.min), mx = parseInt(el.max);
        const neutral = (mn + mx) / 2;
        const half = (mx - mn) / 2;
        const internal = half ? (dv - neutral) / half : 0;
        if (Math.abs(internal) > 0.001) {
            wsSend({ type: 'meta', name, value: internal });
        }
    });
}

export function sendMorphThrottled(key, value) {
    Morphdrossel.schieben(state, wsSend, key, value);
}

// Register
fn.connectWebSocket = connectWebSocket;
fn.wsSend = wsSend;
fn.sendMorphThrottled = sendMorphThrottled;

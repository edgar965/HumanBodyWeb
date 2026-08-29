/**
 * Result Character — WebSocket morph communication.
 */
import { state } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { blenderToThreeCoords } from '../character_core.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Protokoll } from '../gemeinsam/protokoll.js';
import { Morphdrossel } from '../gemeinsam/morphdrossel.js';

export function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const url = `${protocol}://${window.location.host}/ws/character/`;
    state.ws = new WebSocket(url);
    state.ws.binaryType = 'arraybuffer';

    state.ws.onopen = () => {
        state.wsReady = true;
        wsSend({ type: 'body_type', value: state.currentBodyType });
        if (Object.keys(state.currentMorphs).length > 0) {
            wsSend({ type: 'morph_batch', morphs: state.currentMorphs });
        }
        for (const [name, val] of Object.entries(state.currentMeta)) {
            if (Math.abs(val) > 0.001) {
                wsSend({ type: 'meta', name, value: val });
            }
        }
    };
    state.ws.onclose = () => {
        state.wsReady = false;
        // Dieselbe Lage wie auf der Viewer-Seite — dort waren es
        // 2000 ms, hier 3000: derselbe Wert fuer dasselbe (16.08.2026).
        setTimeout(connectWebSocket, Zeiten.VERBINDEN_MS);
    };
    state.ws.onerror = () => {};
    state.ws.onmessage = (event) => {
        if (event.data instanceof ArrayBuffer) {
            updateMeshVertices(event.data);
        } else {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'reload_mesh') {
                    fn.reloadBodyMesh(msg.body_type);
                }
            } catch (e) { Protokoll.debug('websocket', 'Nachricht nicht verwertbar', e); }
        }
    };
}

export function wsSend(msg) {
    if (state.ws && state.wsReady) state.ws.send(JSON.stringify(msg));
}

export function sendMorphThrottled(key, value) {
    Morphdrossel.schieben(state, wsSend, key, value);
}

function updateMeshVertices(float32Buffer) {
    if (!state.bodyGeometry) return;
    const positions = state.bodyGeometry.attributes.position;
    const newData = new Float32Array(float32Buffer);
    blenderToThreeCoords(newData);
    positions.array.set(newData);
    positions.needsUpdate = true;
    state.bodyGeometry.computeBoundingSphere();
}

fn.connectWebSocket = connectWebSocket;
fn.wsSend = wsSend;
fn.sendMorphThrottled = sendMorphThrottled;

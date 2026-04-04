/**
 * Result Character — WebSocket morph communication.
 */
import { state } from './state.js';
import { fn } from './registry.js';
import { blenderToThreeCoords } from '../character_core.js?v=1';

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
        setTimeout(connectWebSocket, 3000);
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
            } catch (e) { /* ignore */ }
        }
    };
}

export function wsSend(msg) {
    if (state.ws && state.wsReady) state.ws.send(JSON.stringify(msg));
}

export function sendMorphThrottled(key, value) {
    state.pendingMorphs[key] = value;
    if (!state.morphTimer) {
        state.morphTimer = setTimeout(() => {
            if (Object.keys(state.pendingMorphs).length === 1) {
                const [k, v] = Object.entries(state.pendingMorphs)[0];
                wsSend({ type: 'morph', key: k, value: v });
            } else {
                wsSend({ type: 'morph_batch', morphs: state.pendingMorphs });
            }
            state.pendingMorphs = {};
            state.morphTimer = null;
        }, 33);
    }
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

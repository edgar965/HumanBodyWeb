/**
 * Result Character — WebSocket morph communication.
 */
import { state } from './state.js';
import { Netzpunkte } from '../gemeinsam/netzpunkte.js';
import { fn } from '../gemeinsam/registrierung.js';
import { Zeiten } from '../gemeinsam/zeiten.js';
import { Morphdrossel } from '../gemeinsam/morphdrossel.js';
import { Netznachricht } from '../gemeinsam/netznachricht.js';

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
    state.ws.onmessage = (ereignis) => Netznachricht.verteilen(ereignis, {
        punkte: updateMeshVertices,
        neuLaden: (typ) => fn.reloadBodyMesh(typ),
    });
}

export function wsSend(msg) {
    if (state.ws && state.wsReady) state.ws.send(JSON.stringify(msg));
}

export function sendMorphThrottled(key, value) {
    Morphdrossel.schieben(state, wsSend, key, value);
}

function updateMeshVertices(float32Buffer) {
    Netzpunkte.ausPuffer(state.bodyGeometry, float32Buffer);
}

fn.wsSend = wsSend;
fn.sendMorphThrottled = sendMorphThrottled;

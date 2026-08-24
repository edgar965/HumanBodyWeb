/**
 * Vergleichsfunk — die WebSocket-Verbindung einer Vergleichsspalte.
 *
 * Aus viewer_compare.js herausgeloest (Umbau 16.08.2026).
 *
 * Reglerbewegungen werden gebuendelt: Wer einen Schieber zieht, loest bis zu
 * sechzig Ereignisse je Sekunde aus; gesendet wird hoechstens alle 33 ms, und
 * mehrere Morphs in einem Paket.
 */
import { Vergleichsnetz } from './vergleichsnetz.js';
import { Protokoll } from '../../../static/viewer/gemeinsam/protokoll.js';

/** Sammelzeit fuer Reglerbewegungen in Millisekunden. */
const BUENDELZEIT = 33;

/** Wartezeit bis zum Neuverbinden. */
const NEUVERSUCH = 2000;

export class Vergleichsfunk {
    constructor(ansicht) {
        this.ansicht = ansicht;
        this.verbindung = null;
        this.bereit = false;
        this.zeitgeber = null;
        this.wartendeMorphs = {};
    }

    verbinden() {
        const schema = window.location.protocol === 'https:' ? 'wss' : 'ws';
        this.verbindung = new WebSocket(
            `${schema}://${window.location.host}${this.ansicht.wsPath}`);
        this.verbindung.binaryType = 'arraybuffer';
        this.verbindung.onopen = () => this._offen();
        this.verbindung.onclose = () => this._geschlossen();
        this.verbindung.onerror = (e) =>
            console.error(`[${this.ansicht.label}] WS error:`, e);
        this.verbindung.onmessage = (e) => this._nachricht(e);
    }

    _offen() {
        this.bereit = true;
        this.ansicht.felder.melden('Connected', 'connected');
        const art = this.ansicht.felder.koerperart?.value;
        if (art) this.senden({ type: 'body_type', value: art });
    }

    _geschlossen() {
        this.bereit = false;
        this.ansicht.felder.melden('Disconnected', 'disconnected');
        setTimeout(() => this.verbinden(), NEUVERSUCH);
    }

    _nachricht(ereignis) {
        if (ereignis.data instanceof ArrayBuffer) {
            Vergleichsnetz.punkteSetzen(this.ansicht, ereignis.data);
            return;
        }
        try {
            const m = JSON.parse(ereignis.data);
            if (m.type === 'error') {
                console.error(`[${this.ansicht.label}] Server:`, m.message);
            } else if (m.type === 'reload_mesh') {
                Vergleichsnetz.laden(this.ansicht, m.body_type);
            }
        } catch (e) { Protokoll.debug('vergleich', 'Nachricht ohne JSON übergangen', e); }
    }

    senden(nachricht) {
        if (this.verbindung && this.bereit) {
            this.verbindung.send(JSON.stringify(nachricht));
        }
    }

    /** Morphwert vormerken und gebuendelt schicken. */
    morphGebremst(schluessel, wert) {
        this.wartendeMorphs[schluessel] = wert;
        if (this.zeitgeber) return;
        this.zeitgeber = setTimeout(() => {
            const eintraege = Object.entries(this.wartendeMorphs);
            if (eintraege.length === 1) {
                const [k, v] = eintraege[0];
                this.senden({ type: 'morph', key: k, value: v });
            } else {
                this.senden({ type: 'morph_batch', morphs: this.wartendeMorphs });
            }
            this.wartendeMorphs = {};
            this.zeitgeber = null;
        }, BUENDELZEIT);
    }
}

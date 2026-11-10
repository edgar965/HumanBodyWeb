/**
 * Fotogenesisgenesis — Feld 3 „Genesis-Modell“ der Seite „Foto-Genesis“ (24.10.2026), Zeichner für `Meshgenesisansicht`.
 *
 * Gebaut wird mit DEMSELBEN Code wie auf der Mesh-Genesis-Jobseite (`Meshgenesisgenesisfigur` → `Genesis9Modell` der Charakter-Seite; Edgar, 19.10.2026: „es soll immer der gleiche Code genutzt werden wie der
 * von Charakter“), aus denselben Endpunkten (`/api/meshgenesis/<paar>/proben/`, `…/genesis/1/`). Heute gibt es zwei Figuren je Export:
 * - **Ergebnis** (`ausgabe`): was Mesh-Genesis aus dem Tripo-Netz macht — Messlatte A des Konzepts (Fotos → Netz → Mesh-Genesis → Genesis), Kleider und Haar aus der KI, wenn vorhanden;
 * - **Wahrheit** (`soll`): die Figur, aus der die Fotos gerendert sind.
 * Schalter „Kleider“: beim Ergebnis die Kleider aus der KI aus (`Meshgenesiskikleiderfeld`), bei der Wahrheit die Zeile „Nur Körper“ (nur Anatomie-Stücke, eine eigene Figur).
 */
import * as THREE from 'three';
import { Meshgenesisausrichtung } from '../meshgenesis/meshgenesisausrichtung.js';
import { Meshgenesisgenesisfigur } from '../meshgenesis/meshgenesisgenesisfigur.js';

export class Fotogenesisgenesis {
    /** @param {{job: string, proben: string}} genesis aus den Seitendaten (`Fotogenesisseitendaten`) */
    constructor(genesis) {
        this.genesis = genesis;
        this.probe = null;
        this.rig = null;
        this.fehler = '';
        this.bereit = this._vorbereiten();
    }

    async _vorbereiten() {
        try {
            const antwort = await fetch(this.genesis.proben);
            if (!antwort.ok) throw new Error(`HTTP ${antwort.status}`);
            const daten = await antwort.json();
            this.probe = daten.proben?.[0] ?? null;
            this.rig = daten.rig ?? null;
            if (!this.probe || !this.rig) throw new Error('keine Probe');
        } catch (fehler) {
            this.fehler = `Probe von ${this.genesis.name} nicht geladen: ${fehler.message}`;
            console.warn(`Fotogenesisgenesis: ${this.fehler}`);
        }
    }

    /** Der Auftrag an `Meshgenesisgenesisfigur` (Form wie `Meshgenesiszeile`): `quelle` 'ausgabe' | 'soll'. */
    auftrag(quelle, modus, kleider) {
        return { echt: true, job: this.genesis.job, zeile: quelle === 'soll' && !kleider ? 'koerper_nackt' : 'koerper', probe: this.probe, rigBeschreibung: this.rig, modus, kleider, quelle };
    }

    /** Zeichner: `d` aus `auftrag`. Legt die fertige Figur ins Feld, sonst einen Text. */
    zeichnen(inhalt, _art, d) {
        if (!this.probe) {
            inhalt.userData.hinweis = this.fehler || 'Probe wird geladen …';
            return;
        }
        const e = Meshgenesisgenesisfigur.fuer(d, d.quelle);
        if (!e) {
            inhalt.userData.hinweis = 'Für diese Probe gibt es keine Genesis-Figur.';
            return;
        }
        if (e.stand !== 'fertig') {
            inhalt.userData.hinweis = e.text;
            return;
        }
        Meshgenesisgenesisfigur.einhaengen(inhalt, e, d, d.quelle);
        this.text = d.quelle === 'ausgabe' ? (e.quelle || '') : 'Wahrheit: die Figur, aus der die Fotos gerendert sind.';
    }

    /** Ist die Figur dieses Auftrags fertig gebaut? (startet den Bau, falls nötig) */
    fertig(d) {
        return this.probe ? Meshgenesisgenesisfigur.fuer(d, d.quelle)?.stand === 'fertig' : false;
    }

    /**
     * Die Drehung vom Rahmen der Fotos (Figurgruppe der Wahrheit, vorne = +Z) in den Rahmen des Datensatzes, in dem `Meshgenesisgenesisfigur` die Figuren zeigt — gemessen an der wahren Figur: ihre Gelenke
     * im eigenen Rahmen gegen das Rig der Probe (`rig.soll`), starr wie `Meshgenesisgenesisfigur._ausrichten`. `null`, solange die Wahrheit noch gebaut wird.
     */
    rahmen() {
        if (this._rahmen) return this._rahmen;
        const d = this.auftrag('soll', 'textur', true);
        const e = this.probe ? Meshgenesisgenesisfigur.fuer(d, 'soll') : null;
        if (!e || e.stand !== 'fertig') return null;
        const gruppe = e.modell.group, ziel = this.probe.rig?.soll;
        gruppe.updateMatrixWorld(true);
        const umkehr = gruppe.matrixWorld.clone().invert(), je = new Map(), a = [], b = [];
        gruppe.traverse(o => { if (o.isBone && !je.has(o.name)) je.set(o.name, o); });
        this.rig.knochen.forEach((k, i) => {
            const knochen = je.get(k.name);
            if (!knochen || !ziel?.[i]) return;
            const p = knochen.getWorldPosition(new THREE.Vector3()).applyMatrix4(umkehr);
            a.push([p.x, p.y, p.z]);
            b.push(ziel[i]);
        });
        if (a.length < 3) return null;
        this._rahmen = Meshgenesisausrichtung.starr(a, b).quaternion.clone();
        return this._rahmen;
    }
}

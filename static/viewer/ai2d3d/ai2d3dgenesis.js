/**
 * Ai2d3dgenesis — Feld 3 „Genesis-Modell“ der Seite „2d-3d-AI“ (24.10.2026), Zeichner für `Mesh3daiansicht`.
 *
 * Gebaut wird mit DEMSELBEN Code wie auf der Mesh3D-AI-Jobseite (`Mesh3daigenesisfigur` → `Genesis9Modell` der Charakter-Seite; Edgar, 19.10.2026: „es soll immer der gleiche Code genutzt werden wie der
 * von Charakter“), aus denselben Endpunkten (`/api/mesh3dai/<paar>/proben/`, `…/genesis/1/`). Heute gibt es zwei Figuren je Export:
 * - **Ergebnis** (`ausgabe`): was Mesh3D-AI aus dem Tripo-Netz macht — Messlatte A des Konzepts (Fotos → Netz → Mesh3D-AI → Genesis), Kleider und Haar aus der KI, wenn vorhanden;
 * - **Wahrheit** (`soll`): die Figur, aus der die Fotos gerendert sind.
 * Schalter „Kleider“: beim Ergebnis die Kleider aus der KI aus (`Mesh3daikikleiderfeld`), bei der Wahrheit die Zeile „Nur Körper“ (nur Anatomie-Stücke, eine eigene Figur).
 */
import * as THREE from 'three';
import { Mesh3daiausrichtung } from '../mesh3dai/mesh3daiausrichtung.js';
import { Mesh3daigenesisfigur } from '../mesh3dai/mesh3daigenesisfigur.js';

export class Ai2d3dgenesis {
    /** @param {{job: string, proben: string}} genesis aus den Seitendaten (`Ai2d3dseitendaten`) */
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
            console.warn(`Ai2d3dgenesis: ${this.fehler}`);
        }
    }

    /** Der Auftrag an `Mesh3daigenesisfigur` (Form wie `Mesh3daizeile`): `quelle` 'ausgabe' | 'soll'. */
    auftrag(quelle, modus, kleider) {
        return { echt: true, job: this.genesis.job, zeile: quelle === 'soll' && !kleider ? 'koerper_nackt' : 'koerper', probe: this.probe, rigBeschreibung: this.rig, modus, kleider, quelle };
    }

    /** Zeichner: `d` aus `auftrag`. Legt die fertige Figur ins Feld, sonst einen Text. */
    zeichnen(inhalt, _art, d) {
        if (!this.probe) {
            inhalt.userData.hinweis = this.fehler || 'Probe wird geladen …';
            return;
        }
        const e = Mesh3daigenesisfigur.fuer(d, d.quelle);
        if (!e) {
            inhalt.userData.hinweis = 'Für diese Probe gibt es keine Genesis-Figur.';
            return;
        }
        if (e.stand !== 'fertig') {
            inhalt.userData.hinweis = e.text;
            return;
        }
        Mesh3daigenesisfigur.einhaengen(inhalt, e, d, d.quelle);
        this.text = d.quelle === 'ausgabe' ? (e.quelle || '') : 'Wahrheit: die Figur, aus der die Fotos gerendert sind.';
    }

    /** Ist die Figur dieses Auftrags fertig gebaut? (startet den Bau, falls nötig) */
    fertig(d) {
        return this.probe ? Mesh3daigenesisfigur.fuer(d, d.quelle)?.stand === 'fertig' : false;
    }

    /**
     * Die Drehung vom Rahmen der Fotos (Figurgruppe der Wahrheit, vorne = +Z) in den Rahmen des Datensatzes, in dem `Mesh3daigenesisfigur` die Figuren zeigt — gemessen an der wahren Figur: ihre Gelenke
     * im eigenen Rahmen gegen das Rig der Probe (`rig.soll`), starr wie `Mesh3daigenesisfigur._ausrichten`. `null`, solange die Wahrheit noch gebaut wird.
     */
    rahmen() {
        if (this._rahmen) return this._rahmen;
        const d = this.auftrag('soll', 'textur', true);
        const e = this.probe ? Mesh3daigenesisfigur.fuer(d, 'soll') : null;
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
        this._rahmen = Mesh3daiausrichtung.starr(a, b).quaternion.clone();
        return this._rahmen;
    }
}

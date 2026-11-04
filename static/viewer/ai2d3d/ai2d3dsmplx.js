/**
 * Ai2d3dsmplx — Feld „SMPL-X (PSHuman)“ (seit 04.11.2026 abends Feld 2 der Zeile mit den Genesis-Feldern, folgt deren Leiste) in jeder Zeile der Jobseite (03.11.2026, Edgar: „im Job mach als zusätzliche 4. View in jeder Zeile das SMPLX modell bei pshuman jobs,
 * zum testen“).
 *
 * PSHumans eingepasstes SMPL-X (`daten.smplx`, GLB über `/api/2d3dai/<job>/netz/pshuman_smplx/`), gezeichnet wie das Feld „Netz“ (`Ai2d3dnetz`, je Feld ein eigener Zeichner: eine
 * three.js-Szene hängt nur in einem Feld). Folgt Ansichtsart, Fotowahl und Ausschnitt der Seite, steht so groß wie die Person im Foto (`Ai2d3dseite._rand`) und dreht mit den übrigen
 * Feldern (`Mesh3daiansicht.koppeln` in `Ai2d3dseite`). Template: `_ai2d3d_smplxfeld.html` (nur mit `daten.smplx`).
 *
 * Seit 04.11.2026 (Edgar: „pshuman als zusätzliches Feld / View“) zeichnet dieselbe Klasse mit dem Schlüssel 'pshuman' auch PSHumans Endnetz (`daten.pshuman`, Felder
 * `[data-pshuman]`, Template `_ai2d3d_pshumanfeld.html`) — gleiche Kamera, gleiche Kopplung.
 */
import * as THREE from 'three';
import { Ai2d3dansicht } from './ai2d3dansicht.js';
import { Ai2d3dkamera } from './ai2d3dkamera.js';
import { Ai2d3dnetz } from './ai2d3dnetz.js';

export class Ai2d3dsmplx {
    static KAMERA = { position: [0, 1, 4], ziel: [0, 0.9, 0], boden: false };

    /** Die Felder zu `seite` (`Ai2d3dseite`) — null ohne Netz `schluessel` ('smplx' | 'pshuman') in den Seitendaten oder ohne Feld `[data-<schluessel>]` im Template. */
    static aufbauen(seite, schluessel = 'smplx') {
        const felder = [...document.querySelectorAll(`[data-${schluessel}]`)];
        if (!seite.daten[schluessel] || !felder.length) return null;
        return new Ai2d3dsmplx(seite, felder, schluessel);
    }

    constructor(seite, felder, schluessel = 'smplx') {
        this.seite = seite;
        this.schluessel = schluessel;
        this.felder = felder.map(feld => {
            let ansicht = null;
            const netz = new Ai2d3dnetz(text => { ansicht.hinweis.hidden = false; ansicht.hinweis.textContent = text; }, () => this.zeigen(true));
            ansicht = new Ai2d3dansicht(feld, 'eingabe', netz, Ai2d3dsmplx.KAMERA);
            return ansicht;
        });
        // die Größe richtet sich nach der Person im großen Foto der Seite — ist es geladen, die Kameras nachstellen
        seite.fotos.gross.addEventListener('load', () => this.kameras());
    }

    /** Alle Felder neu zeigen; `neuStellen`: die Kameras auf die Perspektive des Fotos setzen. */
    zeigen(neuStellen) {
        for (const a of this.felder) {
            const leiste = a.feld.closest('#ai2d3d-genesiszeile') ? this.seite.genesiszeile?.leiste : null;     // in der Zeile mit eigener Leiste gilt diese
            a.zeilenart = leiste?.art ?? null;
            a.zeigen({ netz: this.seite.daten[this.schluessel], modus: (leiste ?? this.seite.steuerung).modus });
        }
        if (neuStellen) this.kameras();
    }

    kameras(versuch = 0) {
        const s = this.seite;
        if (s.winkel === null) return;
        const eins = new THREE.Quaternion();
        let offen = false;
        for (const a of this.felder) offen = !Ai2d3dkamera.feldStellen(a, s.winkel, eins, s._rand(a), s.kopf) || offen;
        // ein Feld zeichnet erst, wenn es im Fenster steht — bis dahin ist seine Hülle leer: nachfassen
        if (offen && versuch < 40) {
            clearTimeout(this._uhr);
            this._uhr = setTimeout(() => this.kameras(versuch + 1), 250);
        }
    }
}

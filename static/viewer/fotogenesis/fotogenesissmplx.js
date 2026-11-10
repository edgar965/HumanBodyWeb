/**
 * Fotogenesissmplx — Feld „SMPL-X (PSHuman)“ (seit 04.11.2026 abends Feld 2 der Zeile mit den Genesis-Feldern, folgt deren Leiste) in jeder Zeile der Jobseite (03.11.2026, Edgar: „im Job mach als zusätzliche 4. View in jeder Zeile das SMPLX modell bei pshuman jobs,
 * zum testen“).
 *
 * PSHumans Startkörper (`daten.smplx`: seit 07.11.2026 Genesis, Netzart `pshuman_start`, alte Jobs und UP2You SMPL-X, `pshuman_smplx`; GLB über `/api/fotogenesis/<job>/netz/<art>/`), gezeichnet wie das Feld „Netz“ (`Fotogenesisnetz`, je Feld ein eigener Zeichner: eine
 * three.js-Szene hängt nur in einem Feld). Folgt Ansichtsart, Fotowahl und Ausschnitt der Seite, steht so groß wie die Person im Foto (`Fotogenesisseite._rand`) und dreht mit den übrigen
 * Feldern (`Meshgenesisansicht.koppeln` in `Fotogenesisseite`). Template: `_fotogenesis_smplxfeld.html` (nur mit `daten.smplx`).
 *
 * Seit 04.11.2026 (Edgar: „pshuman als zusätzliches Feld / View“) zeichnet dieselbe Klasse mit dem Schlüssel 'pshuman' auch PSHumans Endnetz (`daten.pshuman`, Felder
 * `[data-pshuman]`, Template `_fotogenesis_pshumanfeld.html`) — gleiche Kamera, gleiche Kopplung.
 */
import * as THREE from 'three';
import { Fotogenesisansicht } from './fotogenesisansicht.js';
import { Fotogenesiskamera } from './fotogenesiskamera.js';
import { Fotogenesisnetz } from './fotogenesisnetz.js';

export class Fotogenesissmplx {
    static KAMERA = { position: [0, 1, 4], ziel: [0, 0.9, 0], boden: false };

    /** Die Felder zu `seite` (`Fotogenesisseite`) — null ohne Netz `schluessel` ('smplx' | 'pshuman') in den Seitendaten oder ohne Feld `[data-<schluessel>]` im Template. */
    static aufbauen(seite, schluessel = 'smplx') {
        const felder = [...document.querySelectorAll(`[data-${schluessel}]`)];
        if (!seite.daten[schluessel] || !felder.length) return null;
        return new Fotogenesissmplx(seite, felder, schluessel);
    }

    constructor(seite, felder, schluessel = 'smplx') {
        this.seite = seite;
        this.schluessel = schluessel;
        this.felder = felder.map(feld => {
            let ansicht = null;
            const netz = new Fotogenesisnetz(text => { ansicht.hinweis.hidden = false; ansicht.hinweis.textContent = text; }, () => this.zeigen(true));
            ansicht = new Fotogenesisansicht(feld, 'eingabe', netz, Fotogenesissmplx.KAMERA);
            return ansicht;
        });
        // die Größe richtet sich nach der Person im großen Foto der Seite — ist es geladen, die Kameras nachstellen
        seite.fotos.gross.addEventListener('load', () => this.kameras());
    }

    /** Alle Felder neu zeigen; `neuStellen`: die Kameras auf die Perspektive des Fotos setzen. */
    zeigen(neuStellen) {
        for (const a of this.felder) {
            const leiste = a.feld.closest('#fotogenesis-genesiszeile') ? this.seite.genesiszeile?.leiste : null;     // in der Zeile mit eigener Leiste gilt diese
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
        for (const a of this.felder) offen = !Fotogenesiskamera.feldStellen(a, s.winkel, eins, s._rand(a), s.kopf) || offen;
        // ein Feld zeichnet erst, wenn es im Fenster steht — bis dahin ist seine Hülle leer: nachfassen
        if (offen && versuch < 40) {
            clearTimeout(this._uhr);
            this._uhr = setTimeout(() => this.kameras(versuch + 1), 250);
        }
    }
}

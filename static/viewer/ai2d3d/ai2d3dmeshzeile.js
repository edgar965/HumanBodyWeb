/**
 * Ai2d3dmeshzeile — die Mesh-Zeile ganz oben auf der Jobseite (28.10.2026, Edgar: „sollen wir eine extra Zeile ganz oben machen mit den 3 Views, wo das Genesis Modell mit dieser
 * Mesh Methode gerechnet wird? also Kopie der Zeile und das dritte Bild mit dem Mesh Modell anstelle von Genesis“).
 *
 * 1 das gewählte Foto · 2 die geometrische Figur (`Ai2d3dtrainingfigur`, eigene Netze, dieselben Daten) · 3 die eingepasste Genesis-Figur (`Ai2d3dmeshfigur`). Die Felder folgen der
 * Fotowahl und der Ansichtsart der Seite, drehen mit den Feldern der Zeile darunter (`Mesh3daiansicht.koppeln`, in `Ai2d3dseite`) und stehen so groß wie die Person im Foto
 * (`Ai2d3dseite._rand`). Template: `ai2d3d_meshzeile.html` (nur mit gerechneter Figur).
 */
import * as THREE from 'three';
import { Ai2d3dansicht } from './ai2d3dansicht.js';
import { Ai2d3dfotos } from './ai2d3dfotos.js';
import { Ai2d3dkamera } from './ai2d3dkamera.js';
import { Ai2d3dmeshfigur } from './ai2d3dmeshfigur.js';
import { Ai2d3dtrainingfigur } from './ai2d3dtrainingfigur.js';

export class Ai2d3dmeshzeile {
    static KAMERA = { position: [0, 1, 4], ziel: [0, 0.9, 0], boden: false };

    /** Die Zeile zu `seite` (`Ai2d3dseite`) — null, wenn das Template sie nicht hat. */
    static aufbauen(seite) {
        const zeile = document.getElementById('ai2d3d-meshzeile');
        if (!zeile) return null;
        if (!seite.trainingfigur) throw new Error('Ai2d3dmeshzeile: Zeile im Template, aber keine gerechnete Figur in den Seitendaten');
        return new Ai2d3dmeshzeile(seite, zeile);
    }

    constructor(seite, zeile) {
        this.seite = seite;
        const feld = name => zeile.querySelector(`[data-feld="${name}"]`);
        this.foto = feld('mesh-foto').appendChild(document.createElement('img'));
        Object.assign(this.foto, { className: 'ai2d3d-foto', alt: '' });
        this.geometrie = new Ai2d3dtrainingfigur(seite.trainingfigur);
        this.figur = new Ai2d3dmeshfigur(seite.trainingfigur);
        this.geofeld = new Ai2d3dansicht(feld('mesh-geometrie'), 'ausgabe', this.geometrie, Ai2d3dmeshzeile.KAMERA);
        this.figurfeld = new Ai2d3dansicht(feld('mesh-genesis'), 'ausgabe', this.figur, Ai2d3dmeshzeile.KAMERA);
        this.info = zeile.querySelector('[data-mesh-info]');
        // die Größe richtet sich nach der Person im großen Foto der Seite — ist es geladen, die Kameras nachstellen
        seite.fotos.gross.addEventListener('load', () => this.kameras());
        Promise.all([this.geometrie.bereit, this.figur.bereit]).then(() => this.aktualisieren());
    }

    get felder() {
        return [this.geofeld, this.figurfeld];
    }

    /** Foto, Figuren und Kameras nach Fotowahl und Ansichtsart der Seite. */
    aktualisieren() {
        const s = this.seite, nr = s.steuerung.foto, f = s.daten.fotos[nr];
        if (f) Object.assign(this.foto, { src: f.adresse, alt: Ai2d3dfotos.beschriftung(f) });
        this.geofeld.zeigen({ nr, modus: s.steuerung.modus });
        this.figurfeld.zeigen({ nr, modus: s.steuerung.modus });
        const m = this.figur.masse;
        // nur Fehler und fehlende Daten als Text unter dem Feld (wie Feld 2, 27.10.2026: „entferne diesen Text“); die Zahlen der Einpassung als Hover
        this.info.textContent = this.geometrie.fehler ? `Figur nicht geladen: ${this.geometrie.fehler}` : '';
        this.figurfeld.feld.title = m ? `Mesh-Methode: Hautpunkte des Ziels → Figur ${m.ziel_haut_zur_figur_mm} mm, außen ${m.aussen} von ${m.punkte} Punkten, `
            + `kleinster Abstand ${m.kleinster_mm} mm` : '';
        this.kameras();
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

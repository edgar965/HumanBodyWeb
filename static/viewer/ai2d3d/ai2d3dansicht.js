/**
 * Ai2d3dansicht — ein 3D-Feld der Seite „2d-3d-AI“ (24.10.2026): `Mesh3daiansicht` mit EINEM Grund für alle Felder und gekoppeltem Drehen relativ zur eigenen Figur.
 *
 * Edgar: „der hintergrund bei den 3D Views sollte auch heller sein, und gleich, damit man vergleichen kann“ — Mesh3D-AI wechselt zwischen zwei dunklen Gründen (Netz 1b1f27, Figur 5a6170);
 * hier gilt `Ai2d3dansicht.grund` (gesetzt von `Ai2d3dseite`: weiß wie die freigestellten Fotos, bei Exporten der Grund der Exportfotos).
 * Edgar: „dass sich die Modelle alle synchron drehen im View in einer Zeile, so wie bei Mesh3d-AI“ — Mesh3D-AI kopiert Kamera und Drehpunkt absolut; das geht hier nicht, weil das Netz (Tripo,
 * ~1 m hoch, im Rahmen der Fotos) und die Genesis-Figur (~1,75 m, bei Exporten im Rahmen des Datensatzes) verschieden groß sind und verschieden stehen. Übernommen wird darum der Blick RELATIV
 * zum eigenen Drehpunkt: Richtung im Rahmen der Fotos (`rahmen`) und Abstand im Verhältnis der Hüllen (`groesse`, beide setzt `Ai2d3dkamera.feldStellen`).
 */
import * as THREE from 'three';
import { Mesh3daiansicht } from '../mesh3dai/mesh3daiansicht.js';

export class Ai2d3dansicht extends Mesh3daiansicht {
    static grund = 0xffffff;
    /**
     * Fotolicht (24.10.2026 abends, Edgar: „jetzt hast du alle unterschiede, fixe!“): die Haut und die Stücke tragen die Farben der Fotos samt deren Schattierung. Unter dem Licht von
     * Mesh3D-AI (Halbkugel 1,1 + Richtung 1,6) kam die Haut auf der Seite 48–71 sRGB-Stufen dunkler als im Foto, Sapiens hielt die Beine dort für Hose (Abnahme `lauf6_messpunkte`).
     * Gemessen im Chrome (three.js r170, ohne Tone-Mapping, MeshStandardMaterial rau, nicht metallisch, Farbe 128): Umgebungslicht 1 → 74, π → 127 — π gibt die Texturfarbe wieder.
     * Gilt für die Ansichtsart „Textur“ und alle Renderings mit echten Materialien (`Ai2d3dvergleich`, `Ai2d3dseitenbild`); die anderen Ansichtsarten behalten das Licht von Mesh3D-AI.
     */
    static FOTOLICHT = Math.PI;

    constructor(...argumente) {
        super(...argumente);
        this.modelllicht = this.szene.children.filter(o => o.isLight);
        this.fotolicht = new THREE.AmbientLight(0xffffff, Ai2d3dansicht.FOTOLICHT);
        this.fotolicht.layers.enableAll();
        this.szene.add(this.fotolicht);
        this.licht(true);
    }

    /** Fotolicht (true) oder das Licht von Mesh3D-AI. */
    licht(foto) {
        if (!this.fotolicht) return;
        this.fotolicht.visible = foto;
        for (const l of this.modelllicht) l.visible = !foto;
    }

    zeichnen() {
        this.grund = Ai2d3dansicht.grund;
        this.licht(!this.inhalt.userData.genesisErsatz);
        super.zeichnen();
    }

    _uebernehmen(von) {
        // Ohne eigene Hülle (Feld noch nicht eingepasst) gibt es kein Verhältnis: übernommen hätte das Feld den Abstand des Netzes (~1 m Figur) für die Genesis-Figur (1,7 m) —
        // Feld 3 zeigte dann nur den Rumpf (24.10.2026, Edgar: „in der oberen View hast du noch nicht das Genesis modell (kopf) drin“).
        if (this.groesse === undefined || von.groesse === undefined) return;
        const eins = new THREE.Quaternion();
        const versatz = von.kamera.position.clone().sub(von.steuerung.target).applyQuaternion((von.rahmen ?? eins).clone().invert());
        versatz.multiplyScalar((this.groesse ?? 1) / (von.groesse ?? 1)).applyQuaternion(this.rahmen ?? eins);
        this._sperre = true;
        this.kamera.position.copy(this.steuerung.target).add(versatz);
        const entfernung = versatz.length();
        this.kamera.near = entfernung / 50;
        this.kamera.far = entfernung * 4;
        this.kamera.updateProjectionMatrix();
        this.steuerung.update();
        this.zeichnen();
        this._sperre = false;
    }
}

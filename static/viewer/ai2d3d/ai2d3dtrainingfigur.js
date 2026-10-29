/**
 * Ai2d3dtrainingfigur — Feld 2 der oberen Zeile der Jobseite: die gerechnete Figur der Kopf-KI in 3D (27.10.2026, Edgar: „mach auf der Jobseite im 3. Bild anstelle des Fotos die
 * geometrische Figur die du ausgerechnet hast, auch in einer 3D View“ — dann „das Genesis Modell an 3. Stellen (und das geometrische an 2. Stelle)“).
 *
 * Daten: `<Job>/abnahme/training_figur.json` (`Trainingfigur`, vom Lauf selbst geschrieben, dieselbe Ausgabe wie Feld 3 der Kopfzeilen): je Foto die Punkte der Figur in dessen Haltung
 * und die Kamera der Einpassung. Zeichner für `Ai2d3dansicht`, die Ansichtsarten wie in den anderen Feldern („Textur“: Farben je Punkt aus den Fotos, wenn der Lauf sie hat). Die Kamera stellt
 * `Ai2d3dseite._kameras` nach derselben Regel wie beim Genesis-Modell, so hoch wie die Person im Foto (27.10.2026, „die Größen aller Figuren bitte gleich machen“); bis dahin stand
 * sie am Ort der Kamera des Fotos, und die Figur war größer als die beiden anderen.
 */
import * as THREE from 'three';
import { Serverabruf } from '../gemeinsam/serverabruf.js';
import { Ai2d3dnetz } from './ai2d3dnetz.js';

export class Ai2d3dtrainingfigur {
    /** @param {string|Ai2d3dtrainingfigur} quelle `/api/2d3dai/<job>/abnahme/trainingfigur/` — oder ein Zeichner, dessen Daten dieser teilt (eigene Netze: ein three.js-Objekt
     *  steht nur in EINER Szene; die Mesh-Zeile `Ai2d3dmeshzeile` zeigt dieselbe Figur in einem zweiten Feld). */
    constructor(quelle) {
        this._netze = new Map();
        this.bereit = quelle instanceof Ai2d3dtrainingfigur
            ? quelle.bereit.then(() => { this.daten = quelle.daten; this.fehler = quelle.fehler; })
            : Serverabruf.json(quelle).then(d => { this.daten = d; }).catch(fehler => { this.fehler = fehler.message; });
    }

    static _feld(text, Typ) {
        return new Typ(Uint8Array.from(atob(text), z => z.charCodeAt(0)).buffer);
    }

    /** Fotofarben (sRGB, 0–255) → linear: three.js nimmt Punktfarben als linear und codiert sie bei der Ausgabe nach sRGB — ungewandelt stand die Figur blass da, das schwarze
     *  T-Shirt grau (27.10.2026, Edgar: „die gerechnete Gesamtfigur ist noch nicht da“). */
    static _linear(u8) {
        const c = new THREE.Color(), tafel = Float32Array.from({ length: 256 }, (_, v) => c.setRGB(v / 255, 0, 0, THREE.SRGBColorSpace).r);
        return Float32Array.from(u8, v => tafel[v]);
    }

    /** Foto `nr` (0-basiert wie die Seite; die Datei zählt ab 1 wie `training.json`) oder null. */
    foto(nr) {
        return this.daten?.fotos?.[String(nr + 1)] ?? null;
    }

    /** Ein Netz aus Punkten, Dreiecken und Farben je Punkt (base64) — Figur und Stücke beider Zeichner (`Ai2d3dmeshfigur`). Farben je Punkt aus allen Fotos (27.10.2026, Konzept
     *  „Textur“, `Sichtbarkeit.farben`) — gezeigt in der Ansichtsart „Textur“ unter dem Fotolicht. */
    static stueck(punkte, dreiecke, farbenB64) {
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.BufferAttribute(Ai2d3dtrainingfigur._feld(punkte, Float32Array), 3));
        g.setIndex(new THREE.BufferAttribute(Ai2d3dtrainingfigur._feld(dreiecke, Uint32Array), 1));
        g.computeVertexNormals();
        const farben = farbenB64 ? Ai2d3dtrainingfigur._linear(Ai2d3dtrainingfigur._feld(farbenB64, Uint8Array)) : null;
        if (farben) g.setAttribute('color', new THREE.BufferAttribute(farben, 3));
        const netz = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: farben ? 0xffffff : 0xc8c8c8, roughness: 1, metalness: 0, vertexColors: !!farben }));
        netz.layers.set(1);          // Ebene 1: die Ansichtsart zeichnet mit ihrem Ersatzmaterial (`Mesh3daiansicht._malen`)
        netz.frustumCulled = false;
        netz.userData.mesh3daiFremd = true;      // gehört dem Zeichner, nicht dem Feld (`Mesh3daiansicht._leeren` gibt es nicht frei)
        return netz;
    }

    /** Figur und Augäpfel (`augen`, seit 29.10.2026 abends wie die Genesis-Figur — Edgar: „augen im mesh fehlen“; der Käfig hat keine). */
    _netz(nr) {
        if (this._netze.has(nr)) return this._netze.get(nr);
        const d = this.daten, schluessel = String(nr + 1);
        const netze = [Ai2d3dtrainingfigur.stueck(this.foto(nr).punkte, d.dreiecke, d.farben)];
        const augen = d.augen?.fotos?.[schluessel];
        if (augen) netze.push(Ai2d3dtrainingfigur.stueck(augen, d.augen.dreiecke, d.augen.farben));
        this._netze.set(nr, netze);
        return netze;
    }

    /** Zeichner von `Mesh3daiansicht`: `d = {nr, modus}` — nur die geometrische Figur (28.10.2026, Edgar: „Ich brauche auch eine geometrische Form des ganzen Körpers im 2. Bild“;
     *  bis dahin lag die eingepasste Genesis-Figur darin und die Figur nur zu 35 % deckend darüber — die Genesis-Figur steht jetzt in der Mesh-Zeile, `Ai2d3dmeshfigur`). */
    zeichnen(inhalt, _art, d) {
        if (!this.daten) {
            inhalt.userData.hinweis = this.fehler ? `Gerechnete Figur nicht geladen: ${this.fehler}` : 'Gerechnete Figur wird geladen …';
            return;
        }
        if (!this.foto(d.nr)) {
            inhalt.userData.hinweis = 'Für dieses Foto liegt keine gerechnete Figur vor.';
            return;
        }
        for (const netz of this._netz(d.nr)) inhalt.add(netz);
        // „Textur“: die eigenen Farben, wenn der Lauf sie hat (sonst Oberfläche); alle anderen Arten mit dem Ersatzmaterial
        inhalt.userData.genesisErsatz = d.modus === 'textur' ? (this.daten.farben ? undefined : Ai2d3dnetz.ersatz('oberflaeche')) : Ai2d3dnetz.ersatz(d.modus);
    }
}

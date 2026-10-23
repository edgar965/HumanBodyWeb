/**
 * Mesh3daiflaechennetz — das gemeinsame Anzeigenetz eines Jobs auf der Seite „Mesh3D-AI“ (15.10.2026, Edgar: „Warum ist beim Ziel bei Ursula so eine schlechte Ansicht zb bei Textur?
 * die Haare sind nicht sichtbar, die Textur der Haut nicht usw“). EIN Paket je Job (`/api/mesh3dai/<job>/flaeche/netz/`, Server `Mesh3daiflaechennetz`, rund 13 MB): Dreiecke des vollen
 * Netzes (alles Haar), Teile, Hautgewichte, UV und Material je Dreieck; die Proben (Fassung 4) bringen nur noch Punkte und Außenfläche (`Mesh3daiflaechen`).
 * Die Materialien (Ursulas Haut, Kleider in ihrer Umfärbung, Haarfarbe) entstehen einmal je Job und gelten in allen Feldern; das letzte ist die Farbe je Punkt (Material −1).
 * Ein Bild, das nachkommt, zeichnet die Seite neu (`nachLaden`, gesetzt von `Mesh3daiseite`).
 */
import * as THREE from 'three';
import { Mesh3daianatomie } from './mesh3daianatomie.js';

export class Mesh3daiflaechennetz {
    static _abrufe = new Map();
    /** Wird gerufen, sobald ein Bild geladen ist (die Felder zeichnen nur auf Anforderung). */
    static nachLaden = null;

    /**
     * @param basis Adresse ohne `netz/` bzw. `bild/…` — Vorgabe der Job (`/api/mesh3dai/<job>/flaeche`); die vorhergesagte Figur eines Tests hat ihre eigene (16.10.2026 abends, Formkopf).
     * @returns {Promise<Mesh3daiflaechennetz>} wirft bei 404 (Netz noch nicht gebaut)
     */
    static holen(jobId, basis = null) {
        const z = Mesh3daiflaechennetz;
        const adresse = basis ?? `/api/mesh3dai/${encodeURIComponent(jobId)}/flaeche`;
        if (!z._abrufe.has(adresse)) {
            const abruf = fetch(`${adresse}/netz/`).then(async antwort => {
                if (!antwort.ok) throw new Error(antwort.status === 404 ? 'Anzeigenetz fehlt' : `Anzeigenetz: HTTP ${antwort.status}`);
                return new Mesh3daiflaechennetz(jobId, await antwort.arrayBuffer(), adresse);
            });
            abruf.catch(() => z._abrufe.delete(adresse));
            z._abrufe.set(adresse, abruf);
        }
        return z._abrufe.get(adresse);
    }

    /** Zerlegt das Paket (Sichten auf den Puffer, jeder Block beginnt auf einem Vielfachen von 4). */
    constructor(jobId, puffer, basis = null) {
        this.jobId = jobId;
        this.basis = basis ?? `/api/mesh3dai/${encodeURIComponent(jobId)}/flaeche`;
        const laenge = new DataView(puffer).getUint32(0, true);
        this.kopf = JSON.parse(new TextDecoder().decode(new Uint8Array(puffer, 4, laenge)));
        const { punkte: v, dreiecke: f, haut: k } = this.kopf;
        const auf4 = n => n + (-n & 3);
        let ab = 4 + laenge;
        this.dreiecke = new Uint32Array(puffer, ab, f * 3);
        ab += f * 12;
        this.knochen = new Uint8Array(puffer, ab, v * k);
        ab += auf4(v * k);
        this.gewicht = new Uint8Array(puffer, ab, v * k);
        ab += auf4(v * k);
        this.etikett = new Uint8Array(puffer, ab, f);
        ab += auf4(f);
        this.uv = new Float32Array(puffer, ab, v * 2);
        ab += v * 8;
        this.material = new Int16Array(puffer, ab, f);
        ab += auf4(f * 2);
        // Ruhelage (16.10.2026, Server `Mesh3daiflaechennetz`, Kopf `ruhe`): Grundlage für das genau gehäutete Ergebnis eines Laufs mit Daz-Winkeln.
        this.ruhe = this.kopf.ruhe ? new Float32Array(puffer, ab, v * 3) : null;
        if (this.ruhe) ab += v * 12;
        // Dreiecke, die nicht gezeichnet werden (19.10.2026, Trainingspaare: die Haut unter dem Anatomie-Stück — sie bleibt fürs Backen des Stücks im Netz): als Maske je Dreieck.
        this.verborgen = null;
        if (this.kopf.verborgen) {
            this.verborgen = new Uint8Array(f);
            for (const t of new Uint32Array(puffer, ab, this.kopf.verborgen)) this.verborgen[t] = 1;
            ab += this.kopf.verborgen * 4;
        }
        // Normalen je Punkt (19.10.2026, Trainingspaare: die des Genesis-Exports — sonst knickte die Naht Haut ↔ Anatomie-Stück, `Mesh3daiflaechennormalen`): int8 × 127.
        this.normalen = null;
        if (this.kopf.normalen) {
            const roh = new Int8Array(puffer, ab, v * 3);
            this.normalen = new Float32Array(v * 3);
            for (let i = 0; i < roh.length; i++) this.normalen[i] = roh[i] / 127;
            ab += auf4(v * 3);
        }
        // Farbe je Punkt (21.10.2026 abends, Weg g Fassung 3: aus dem Eingang): uint8 sRGB → lineare Farbe für das Material der Farbe je Punkt (Material −1, `materialien`).
        if (this.kopf.punktfarbe) {
            const roh = new Uint8Array(puffer, ab, v * 3);
            const lin = new Float32Array(v * 3);
            const c = new THREE.Color();
            for (let i = 0; i < v; i++) {
                c.setRGB(roh[i * 3] / 255, roh[i * 3 + 1] / 255, roh[i * 3 + 2] / 255, THREE.SRGBColorSpace);
                lin[i * 3] = c.r;
                lin[i * 3 + 1] = c.g;
                lin[i * 3 + 2] = c.b;
            }
            this.farbe = new THREE.BufferAttribute(lin, 3);
        }
        this.uvAttribut = new THREE.BufferAttribute(this.uv, 2);
        /** Indexlisten, die nur an der Verbindung hängen (ganze Figur, nur Körper, Kleider) — für alle Proben dieselben (`Mesh3daiflaechen.teil`). */
        this.indexAblage = new Map();
        this._materialien = null;
    }

    /** Die Materialien in der Reihenfolge des Pakets, dazu am Ende eines mit der Farbe je Punkt (für Material −1). */
    materialien() {
        if (this._materialien) return this._materialien;
        const lader = new THREE.TextureLoader();
        this._materialien = this.kopf.materialien.map(m => {
            // Material aus der KI (21.10.2026 nachts, Stufe 2: Rauheit, Glanz, Metall je Stück in `materialien.json`) — Glanz wie `Genesis9netz` als `specularIntensity` eines physikalischen Materials
            const Art = Number.isFinite(m.glanz) ? THREE.MeshPhysicalMaterial : THREE.MeshStandardMaterial;
            const material = new Art({ color: new THREE.Color(...(m.farbe ?? [1, 1, 1])), roughness: Number.isFinite(m.rauheit) ? m.rauheit : 0.75,
                metalness: Number.isFinite(m.metall) ? m.metall : 0, side: THREE.DoubleSide });
            if (Number.isFinite(m.glanz)) material.specularIntensity = m.glanz;
            // Materialkarte je Texel (G Rauheit, B Metall, A Glanz) — dann gelten die Werte der Karte, die Zahlen oben sind nur ihr Mittel
            if (m.bild_material) {
                const karte = lader.load(`${this.basis}/bild/${m.bild_material}`, () => Mesh3daiflaechennetz.nachLaden?.());
                karte.colorSpace = THREE.NoColorSpace;
                material.roughness = 1;
                material.roughnessMap = karte;
                material.metalness = 1;
                material.metalnessMap = karte;
                if (material.isMeshPhysicalMaterial) {
                    material.specularIntensity = 1;
                    material.specularIntensityMap = karte;
                }
            }
            // Relief aus der KI: Normalenkarte im Tangentenraum (Rahmen aus Lage und UV, wie three.js ihn bildet)
            if (m.bild_normal) {
                material.normalMap = lader.load(`${this.basis}/bild/${m.bild_normal}`, () => Mesh3daiflaechennetz.nachLaden?.());
                material.normalMap.colorSpace = THREE.NoColorSpace;
            }
            if (m.bild) {
                material.map = lader.load(`${this.basis}/bild/${m.bild}`, () => Mesh3daiflaechennetz.nachLaden?.());
                material.map.colorSpace = THREE.SRGBColorSpace;
                material.map.anisotropy = 4;
            }
            return material;
        });
        this._materialien.push(new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.8, side: THREE.DoubleSide }));
        // Das Anatomie-Stück bekommt die Haut des Körpers (wie in Charakter und Studio, `Anatomiebacken`) — im Hintergrund, danach zeichnet die Seite neu.
        Mesh3daianatomie.anwenden(this, this._materialien, () => Mesh3daiflaechennetz.nachLaden?.());
        return this._materialien;
    }
}

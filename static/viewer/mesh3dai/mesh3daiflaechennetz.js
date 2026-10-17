/**
 * Mesh3daiflaechennetz — das gemeinsame Anzeigenetz eines Jobs auf der Seite „Mesh3D-AI“ (15.10.2026, Edgar: „Warum ist beim Ziel bei Ursula so eine schlechte Ansicht zb bei Textur?
 * die Haare sind nicht sichtbar, die Textur der Haut nicht usw“). EIN Paket je Job (`/api/mesh3dai/<job>/flaeche/netz/`, Server `Mesh3daiflaechennetz`, rund 13 MB): Dreiecke des vollen
 * Netzes (alles Haar), Teile, Hautgewichte, UV und Material je Dreieck; die Proben (Fassung 4) bringen nur noch Punkte und Außenfläche (`Mesh3daiflaechen`).
 * Die Materialien (Ursulas Haut, Kleider in ihrer Umfärbung, Haarfarbe) entstehen einmal je Job und gelten in allen Feldern; das letzte ist die Farbe je Punkt (Material −1).
 * Ein Bild, das nachkommt, zeichnet die Seite neu (`nachLaden`, gesetzt von `Mesh3daiseite`).
 */
import * as THREE from 'three';

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
            const material = new THREE.MeshStandardMaterial({ color: new THREE.Color(...(m.farbe ?? [1, 1, 1])), roughness: 0.75, side: THREE.DoubleSide });
            if (m.bild) {
                material.map = lader.load(`${this.basis}/bild/${m.bild}`, () => Mesh3daiflaechennetz.nachLaden?.());
                material.map.colorSpace = THREE.SRGBColorSpace;
                material.map.anisotropy = 4;
            }
            return material;
        });
        this._materialien.push(new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.8, side: THREE.DoubleSide }));
        return this._materialien;
    }
}

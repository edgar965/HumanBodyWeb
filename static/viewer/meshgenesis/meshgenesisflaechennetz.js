/**
 * Meshgenesisflaechennetz — das gemeinsame Anzeigenetz eines Jobs auf der Seite „Mesh-Genesis“ (15.10.2026, Edgar: „Warum ist beim Ziel bei Ursula so eine schlechte Ansicht zb bei Textur?
 * die Haare sind nicht sichtbar, die Textur der Haut nicht usw“). EIN Paket je Job (`/api/meshgenesis/<job>/flaeche/netz/`, Server `Meshgenesisflaechennetz`, rund 13 MB): Dreiecke des vollen
 * Netzes (alles Haar), Teile, Hautgewichte, UV und Material je Dreieck; die Proben (Fassung 4) bringen nur noch Punkte und Außenfläche (`Meshgenesisflaechen`).
 * Die Materialien (Ursulas Haut, Kleider in ihrer Umfärbung, Haarfarbe) entstehen einmal je Job und gelten in allen Feldern; das letzte ist die Farbe je Punkt (Material −1).
 * Ein Bild, das nachkommt, zeichnet die Seite neu (`nachLaden`, gesetzt von `Meshgenesisseite`).
 */
import * as THREE from 'three';
import { Meshgenesisanatomie } from './meshgenesisanatomie.js';

export class Meshgenesisflaechennetz {
    static _abrufe = new Map();
    /** Wird gerufen, sobald ein Bild geladen ist (die Felder zeichnen nur auf Anforderung). */
    static nachLaden = null;

    /**
     * @param basis Adresse ohne `netz/` bzw. `bild/…` — Vorgabe der Job (`/api/meshgenesis/<job>/flaeche`); die vorhergesagte Figur eines Tests hat ihre eigene (16.10.2026 abends, Formkopf).
     * @param wunsch `{stufe: 1, matrix: true}` (09.11.2026, Edgar: „das ganze Anzeigenetz in Stufe 1“): der Körper der Testfigur auf Netzstufe 1 (Server `Meshgenesisflaechennetzfein`), mit
     *   `matrix` die Unterteilungsmatrix für `ausKaefig`. Ob es kam, sagt `kopf.stufe`.
     * @returns {Promise<Meshgenesisflaechennetz>} wirft bei 404 (Netz noch nicht gebaut)
     */
    static holen(jobId, basis = null, wunsch = {}) {
        const z = Meshgenesisflaechennetz;
        const adresse = basis ?? `/api/meshgenesis/${encodeURIComponent(jobId)}/flaeche`;
        const frage = wunsch.stufe === 1 ? `?stufe=1${wunsch.matrix ? '&matrix=1' : ''}` : '';
        const schluessel = adresse + frage;
        if (!z._abrufe.has(schluessel)) {
            const abruf = fetch(`${adresse}/netz/${frage}`).then(async antwort => {
                if (!antwort.ok) throw new Error(antwort.status === 404 ? 'Anzeigenetz fehlt' : `Anzeigenetz: HTTP ${antwort.status}`);
                return new Meshgenesisflaechennetz(jobId, await antwort.arrayBuffer(), adresse);
            });
            abruf.catch(() => z._abrufe.delete(schluessel));
            z._abrufe.set(schluessel, abruf);
        }
        return z._abrufe.get(schluessel);
    }

    /** Zerlegt das Paket (Sichten auf den Puffer, jeder Block beginnt auf einem Vielfachen von 4). */
    constructor(jobId, puffer, basis = null) {
        this.jobId = jobId;
        this.basis = basis ?? `/api/meshgenesis/${encodeURIComponent(jobId)}/flaeche`;
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
        // Ruhelage (16.10.2026, Server `Meshgenesisflaechennetz`, Kopf `ruhe`): Grundlage für das genau gehäutete Ergebnis eines Laufs mit Daz-Winkeln.
        this.ruhe = this.kopf.ruhe ? new Float32Array(puffer, ab, v * 3) : null;
        if (this.ruhe) ab += v * 12;
        // Dreiecke, die nicht gezeichnet werden (19.10.2026, Trainingspaare: die Haut unter dem Anatomie-Stück — sie bleibt fürs Backen des Stücks im Netz): als Maske je Dreieck.
        this.verborgen = null;
        if (this.kopf.verborgen) {
            this.verborgen = new Uint8Array(f);
            for (const t of new Uint32Array(puffer, ab, this.kopf.verborgen)) this.verborgen[t] = 1;
            ab += this.kopf.verborgen * 4;
        }
        // Normalen je Punkt (19.10.2026, Trainingspaare: die des Genesis-Exports — sonst knickte die Naht Haut ↔ Anatomie-Stück, `Meshgenesisflaechennormalen`): int8 × 127.
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
            ab += auf4(v * 3);
        }
        // Stufe 1 (09.11.2026, Server `Meshgenesisflaechennetzfein`): Käfigdreieck je Dreieck — Masken des Käfigs (Verdeckung unter den Stücken) gelten für seine Kinder (`dreieckmaske`)
        this.eltern = null;
        if (this.kopf.eltern) {
            this.eltern = new Uint32Array(puffer, ab, f);
            ab += f * 4;
        }
        // Unterteilungsmatrix der Körperpunkte (CSR, Käfigpunkt → Punkt der Stufe 1) für `ausKaefig`
        this.matrix = null;
        if (this.kopf.matrix) {
            const [zeilen, nnz] = this.kopf.matrix;
            const anfang = new Uint32Array(puffer, ab, zeilen + 1);
            ab += (zeilen + 1) * 4;
            const spalte = new Uint16Array(puffer, ab, nnz);
            ab += auf4(nnz * 2);
            const wert = new Float32Array(puffer, ab, nnz);
            ab += nnz * 4;
            this.matrix = { zeilen, anfang, spalte, wert };
        }
        this.uvAttribut = new THREE.BufferAttribute(this.uv, 2);
        /** Indexlisten, die nur an der Verbindung hängen (ganze Figur, nur Körper, Kleider) — für alle Proben dieselben (`Meshgenesisflaechen.teil`). */
        this.indexAblage = new Map();
        this._materialien = null;
    }

    /** Dreiecke dieses Netzes auf dem Käfig — so lang ist eine Maske des Servers (`verdeckt` der Stücke, gerechnet auf dem Käfig). */
    get kaefigDreiecke() {
        return this.kopf.kaefig_dreiecke ?? this.material.length;
    }

    /** Eine Maske je Dreieck auf dieses Netz legen: auf Stufe 1 bekommt jedes Dreieck den Wert seines Käfigdreiecks (`eltern`); null bleibt null. */
    dreieckmaske(maske) {
        if (!maske || !this.eltern || maske.length !== this.kaefigDreiecke) return maske;
        const aus = new Uint8Array(this.eltern.length);
        for (let t = 0; t < aus.length; t++) aus[t] = maske[this.eltern[t]];
        return aus;
    }

    /** Werte je Käfigpunkt (Daz-Nummer, `breite` je Punkt) auf die Körperpunkte der Stufe 1 (Unterteilungsmatrix) — oder null ohne Matrix. */
    ausKaefig(werte, breite = 3) {
        const m = this.matrix;
        if (!m) return null;
        const aus = new Float32Array(m.zeilen * breite);
        for (let i = 0; i < m.zeilen; i++) {
            for (let j = m.anfang[i]; j < m.anfang[i + 1]; j++) {
                const w = m.wert[j], q = m.spalte[j] * breite;
                for (let c = 0; c < breite; c++) aus[i * breite + c] += w * werte[q + c];
            }
        }
        return aus;
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
                const karte = lader.load(`${this.basis}/bild/${m.bild_material}`, () => Meshgenesisflaechennetz.nachLaden?.());
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
                material.normalMap = lader.load(`${this.basis}/bild/${m.bild_normal}`, () => Meshgenesisflaechennetz.nachLaden?.());
                material.normalMap.colorSpace = THREE.NoColorSpace;
            }
            if (m.bild) {
                material.map = lader.load(`${this.basis}/bild/${m.bild}`, () => Meshgenesisflaechennetz.nachLaden?.());
                material.map.colorSpace = THREE.SRGBColorSpace;
                material.map.anisotropy = 4;
            }
            return material;
        });
        this._materialien.push(new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.8, side: THREE.DoubleSide }));
        // Das Anatomie-Stück bekommt die Haut des Körpers (wie in Charakter und Studio, `Anatomiebacken`) — im Hintergrund, danach zeichnet die Seite neu.
        Meshgenesisanatomie.anwenden(this, this._materialien, () => Meshgenesisflaechennetz.nachLaden?.());
        return this._materialien;
    }
}

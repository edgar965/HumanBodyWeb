/**
 * Mesh3daianimationsflaechen — die Flächen aller Bilder der Bewegung auf der Seite „Mesh3D-AI“ (15.10.2026): EIN Paket je Job (`/api/mesh3dai/<job>/animation/flaechen/`, Server
 * `Mesh3daiflaechenanimation`, rund 38 MB), geholt beim ersten Play, von allen Zeilen geteilt. Die Verbindung (Dreiecke, Teile, Hautgewichte, Farben) ist in allen Bildern dieselbe, je Bild ändern sich
 * nur Lage (int16, Zehntelmillimeter) und Außenfläche (Bitfeld). Das Haar fehlt (seine sichtbaren Dreiecke wechseln von Bild zu Bild).
 * `bild(i)` liefert ein `Mesh3daiflaechen` des Bildes i — die letzten `GRENZE` werden gehalten, ältere entsorgt (beim Abspielen entstehen sonst je Bild neue Grafikpuffer).
 */
import * as THREE from 'three';
import { Mesh3daiflaechen } from './mesh3daiflaechen.js';
import { Mesh3daiflaechennetz } from './mesh3daiflaechennetz.js';

export class Mesh3daianimationsflaechen {
    static GRENZE = 4;
    static _abrufe = new Map();

    /** @returns {Promise<Mesh3daianimationsflaechen>} wirft bei 404 (z. B. ohne Flächen der Fassung 2) — Play läuft dann mit Rig und Punktwolke weiter */
    static laden(job) {
        const z = Mesh3daianimationsflaechen;
        if (!z._abrufe.has(job)) {
            const abruf = fetch(`/api/mesh3dai/${encodeURIComponent(job)}/animation/flaechen/`).then(async antwort => {
                if (!antwort.ok) throw new Error(`Flächen der Animation: HTTP ${antwort.status}`);
                const flaechen = new Mesh3daianimationsflaechen(await antwort.arrayBuffer());
                // Mit UV und Material (Flächen der Fassung 4): die Materialien sind die des gemeinsamen Netzes — „Textur“ zeigt beim Abspielen dieselben Bilder wie bei einer Probe.
                if (flaechen.kopf.textur) flaechen.netz = await Mesh3daiflaechennetz.holen(job).catch(() => null);
                return flaechen;
            });
            abruf.catch(() => z._abrufe.delete(job));
            z._abrufe.set(job, abruf);
        }
        return z._abrufe.get(job);
    }

    static verwerfen() {
        Mesh3daianimationsflaechen._abrufe.clear();
    }

    constructor(puffer) {
        const laenge = new DataView(puffer).getUint32(0, true);
        this.kopf = JSON.parse(new TextDecoder().decode(new Uint8Array(puffer, 4, laenge)));
        const { bilder: n, punkte: v, dreiecke: f, haut: k } = this.kopf;
        let ab = 4 + laenge;
        this.dreiecke = new Uint32Array(puffer, ab, f * 3);
        ab += f * 12;
        this.lagen = new Int16Array(puffer, ab, n * v * 3);
        ab += n * v * 6;
        this.knochen = new Uint8Array(puffer, ab, v * k);
        this.gewicht = new Uint8Array(puffer, ab + v * k, v * k);
        ab += 2 * v * k;
        this.etikett = new Uint8Array(puffer, ab, f);
        ab += f;
        this.zeile = Math.ceil(f / 8);
        this.aussenBits = new Uint8Array(puffer, ab, n * this.zeile);
        ab += n * this.zeile;
        if (this.kopf.textur) {
            ab += -ab & 3;
            this.uv = new Float32Array(puffer, ab, v * 2);
            this.material = new Int16Array(puffer, ab + v * 8, f);
            this.uvAttribut = new THREE.BufferAttribute(this.uv, 2);
            ab += v * 8 + f * 2;
        }
        // Ruhelage (16.10.2026): damit `Mesh3daiflaechen.ausgabe` das Ergebnis eines Laufs mit Daz-Winkeln auch beim Abspielen genau häutet.
        this.ruhe = null;
        if (this.kopf.ruhe) {
            ab += -ab & 3;
            this.ruhe = new Float32Array(puffer, ab, v * 3);
        }
        this.netz = null;
        this.farbe = Mesh3daiflaechen.farben(this.kopf, this.dreiecke, this.etikett);
        this._indexe = new Map();      // Indexlisten, die nur an der Verbindung hängen (Soll ganz, nur Körper, Kleider) — für alle Bilder dieselben
        this._bilder = new Map();
    }

    /** Die Fläche des Bildes `i` (0-basiert, Reihenfolge der Bewegung). */
    bild(i) {
        if (this._bilder.has(i)) return this._bilder.get(i);
        const { punkte: v, dreiecke: f, haut, einheit_m: einheit } = this.kopf;
        const lage = new Float32Array(v * 3);
        const quelle = this.lagen.subarray(i * v * 3, (i + 1) * v * 3);
        for (let j = 0; j < lage.length; j++) lage[j] = quelle[j] * einheit;
        const aussen = new Uint8Array(f);
        const bits = this.aussenBits.subarray(i * this.zeile, (i + 1) * this.zeile);
        for (let j = 0; j < f; j++) aussen[j] = (bits[j >> 3] >> (7 - (j & 7))) & 1;
        const textur = this.netz && this.uvAttribut ? { uv: this.uvAttribut, material: this.material, netz: this.netz } : {};
        const flaeche = new Mesh3daiflaechen({ kopf: this.kopf, haut, lage, dreiecke: this.dreiecke, etikett: this.etikett, aussen, knochen: this.knochen, gewicht: this.gewicht, farbe: this.farbe, indexAblage: this._indexe, ruhe: this.ruhe, ...textur });
        flaeche.animation = true;
        this._bilder.set(i, flaeche);
        while (this._bilder.size > Mesh3daianimationsflaechen.GRENZE) {
            const [alt, alteFlaeche] = this._bilder.entries().next().value;
            this._bilder.delete(alt);
            alteFlaeche.entsorgen();
        }
        return flaeche;
    }
}

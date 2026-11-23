/**
 * Meshgenesisflaechennetz — das gemeinsame Anzeigenetz eines Jobs auf der Seite „Mesh-Genesis“ (15.10.2026, Edgar: „Warum ist beim Ziel bei Ursula so eine schlechte Ansicht zb bei Textur?
 * die Haare sind nicht sichtbar, die Textur der Haut nicht usw“). EIN Paket je Job (`/api/meshgenesis/<job>/flaeche/netz/`, Server `Meshgenesisflaechennetz`, rund 13 MB): Dreiecke des vollen
 * Netzes (alles Haar), Teile, Hautgewichte, UV und Material je Dreieck; die Proben (Fassung 4) bringen nur noch Punkte und Außenfläche (`Meshgenesisflaechen`).
 * Die Materialien (Ursulas Haut, Kleider in ihrer Umfärbung, Haarfarbe) entstehen einmal je Job und gelten in allen Feldern; das letzte ist die Farbe je Punkt (Material −1).
 * Ein Bild, das nachkommt, zeichnet die Seite neu (`nachLaden`, gesetzt von `Meshgenesisseite`).
 */
import * as THREE from 'three';
import { Pufferabruf } from '../gemeinsam/pufferabruf.js';
import { Texturweg } from '../gemeinsam/texturweg.js';
import { Meshgenesisanatomie } from './meshgenesisanatomie.js';
import { Meshgenesisumgebung } from './meshgenesisumgebung.js';

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
            // im Worker geholt (23.11.2026, `Pufferabruf`): das Haar mit 106 MB kam im Seitenaufbau erst nach 2,9–4,9 s, allein nach 0,63–1,1 s
            const abruf = Pufferabruf.holen(`${adresse}/netz/${frage}`).then(
                puffer => new Meshgenesisflaechennetz(jobId, puffer, adresse),
                fehler => { throw new Error(fehler.status === 404 ? 'Anzeigenetz fehlt' : `Anzeigenetz: ${fehler.message}`); });
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
        // Entpackt erst beim ersten Lesen (`normalen`, 21.11.2026): die Kartenhäutung (`Meshgenesiskartenhaut`) gibt die Int8-Werte selbst an die Karte — am Zauberer Haar 26 MB, Bart 18 MB.
        this.normalenRoh = this._normalen = null;
        if (this.kopf.normalen) {
            this.normalenRoh = new Int8Array(puffer, ab, v * 3);
            ab += auf4(v * 3);
        }
        // Farbe je Punkt (21.10.2026 abends, Weg g Fassung 3: aus dem Eingang): uint8 sRGB → lineare Farbe für das Material der Farbe je Punkt (Material −1, `materialien`).
        // 19.11.2026 (Ladezeit, Haar mit 1,64 Mio. Punkten): eine Tafel je Stufe statt `Color.setRGB` je Punkt. 22.11.2026 (Edgar zur Ladezeit des Zauberers: „1. OK“): als Float16 auf
        // die Karte (HALF_FLOAT) statt Float32 — Haar 26 → 13 MB, Bart 18 → 9 MB. `toHalfFloat` schneidet ab: je Wert höchstens 2⁻¹⁰ relativ, 0,00049 absolut daneben, höchstens 8 % einer
        // 8-Bit-Stufe (Stufe 191; im Tab über alle 256 Stufen gerechnet).
        if (this.kopf.punktfarbe) {
            const roh = new Uint8Array(puffer, ab, v * 3);
            const tafel = Meshgenesisflaechennetz.halbTafel();
            this.farbe = new THREE.Float16BufferAttribute(v * 3, 3);
            const halb = this.farbe.array;
            for (let i = 0; i < roh.length; i++) halb[i] = tafel[roh[i]];
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
        // Einzelsträhnen (16.11.2026, `haar_Bart`): Leitpunkt je Punkt und die Leitsträhnen in Ruhe [G, K+1] — Bewegung je Locke (`Meshgenesishaarschwung`)
        this.leit = this.leitpunkte = null;
        if (this.kopf.leit) {
            const [g, k1] = this.kopf.leit;
            this.leit = new Uint32Array(puffer, ab, v);
            ab += v * 4;
            this.leitpunkte = new Float32Array(puffer, ab, g * k1 * 3);
            ab += g * k1 * 12;
        }
        this.uvAttribut = new THREE.BufferAttribute(this.uv, 2);
        /** Indexlisten, die nur an der Verbindung hängen (ganze Figur, nur Körper, Kleider) — für alle Proben dieselben (`Meshgenesisflaechen.teil`). */
        this.indexAblage = new Map();
        this._materialien = null;
    }

    /** Normalen je Punkt als Float32Array (int8 / 127, dieselben Werte wie bis 21.11.2026 im Konstruktor), beim ersten Lesen entpackt — null ohne Normalen. */
    get normalen() {
        if (!this._normalen && this.normalenRoh) {
            const roh = this.normalenRoh, n = new Float32Array(roh.length);
            for (let i = 0; i < roh.length; i++) n[i] = roh[i] / 127;
            this._normalen = n;
        }
        return this._normalen;
    }

    set normalen(wert) {
        this._normalen = wert;
    }

    /** sRGB-Stufe 0…255 → linearer Wert, wie `THREE.Color.setRGB(…, SRGBColorSpace)` je Kanal (einmal gerechnet). */
    static linearTafel() {
        if (!Meshgenesisflaechennetz._tafel) {
            const t = new Float32Array(256), c = new THREE.Color();
            for (let s = 0; s < 256; s++) {
                c.setRGB(s / 255, s / 255, s / 255, THREE.SRGBColorSpace);
                t[s] = c.r;
            }
            Meshgenesisflaechennetz._tafel = t;
        }
        return Meshgenesisflaechennetz._tafel;
    }

    /** Dieselbe Tafel als Float16-Bits (`DataUtils.toHalfFloat`, was `Float16BufferAttribute.setX` schreibt). */
    static halbTafel() {
        Meshgenesisflaechennetz._halb ??= Uint16Array.from(Meshgenesisflaechennetz.linearTafel(), w => THREE.DataUtils.toHalfFloat(w));
        return Meshgenesisflaechennetz._halb;
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

    /**
     * Ein Bild des Jobs als Textur, gleich zurück, das Bild kommt nach (`nachLaden`). 22.11.2026 (Ladezeit des Zauberers): Mit `TextureLoader` dekodierte Chrome die JPEGs erst beim
     * Hochladen auf die Karte, im Hauptfaden (Profil: 633 ms `texSubImage2D` im ersten Zeichnen; Robe 852 KB, Hut 412 KB, vier Requisiten). Jetzt wie `Genesis9texturen`: `createImageBitmap`
     * außerhalb des Hauptfadens, `imageOrientation: 'flipY'` statt Threes `flipY` (gilt für Bitmaps nicht), ohne Vormultiplikation und ohne Farbumrechnung — so lud three das `<img>`
     * hoch (`premultiplyAlpha` aus, `UNPACK_COLORSPACE_CONVERSION_WEBGL` = NONE).
     */
    static textur(adresse) {
        const textur = new THREE.Texture();
        textur.flipY = false;
        Meshgenesisflaechennetz._bildlader ??= new THREE.ImageBitmapLoader().setOptions({ imageOrientation: 'flipY', premultiplyAlpha: 'none', colorSpaceConversion: 'none' });
        // auf die Karte je Aufgabe EIN Bild, nicht alle im nächsten Zeichnen (`Texturweg.einreihen`, 23.11.2026: 18 Kleiderbilder 2048² hielten ein Bild 447 ms an)
        Meshgenesisflaechennetz._bildlader.load(adresse, bild => Texturweg.einreihen(textur, () => { textur.image = bild; textur.needsUpdate = true; })
            .then(() => Meshgenesisflaechennetz.nachLaden?.()), undefined, () => {});
        return textur;
    }

    /** Die Materialien in der Reihenfolge des Pakets, dazu am Ende eines mit der Farbe je Punkt (für Material −1). */
    materialien() {
        if (this._materialien) return this._materialien;
        const bild = name => Meshgenesisflaechennetz.textur(`${this.basis}/bild/${name}`);
        this._materialien = this.kopf.materialien.map(m => {
            // Material aus der KI (21.10.2026 nachts, Stufe 2: Rauheit, Glanz, Metall je Stück in `materialien.json`) — Glanz wie `Genesis9netz` als `specularIntensity` eines physikalischen Materials
            const Art = Number.isFinite(m.glanz) ? THREE.MeshPhysicalMaterial : THREE.MeshStandardMaterial;
            const material = new Art({ color: new THREE.Color(...(m.farbe ?? [1, 1, 1])), roughness: Number.isFinite(m.rauheit) ? m.rauheit : 0.75,
                metalness: Number.isFinite(m.metall) ? m.metall : 0, side: THREE.DoubleSide });
            if (Number.isFinite(m.glanz)) material.specularIntensity = m.glanz;
            // Lackschicht (18.11.2026, Goldprinzessin: das Weiß stand matt da, Foto und Franks Modell zeigen glänzenden Lack) — wie `Genesis9glanz`: clearcoat über der Grundschicht
            if (Number.isFinite(m.klarlack) && material.isMeshPhysicalMaterial) {
                material.clearcoat = m.klarlack;
                material.clearcoatRoughness = Number.isFinite(m.klarlackrauheit) ? m.klarlackrauheit : 0.05;
            }
            // Spiegelnde Kostümteile (18.11.2026, `bausteine/kostuemzeilen.py`): Studio-Umgebung, Stärke = `umgebung`
            if (Number.isFinite(m.umgebung)) {
                material.envMap = Meshgenesisumgebung.karte();
                material.envMapIntensity = m.umgebung;
            }
            // Materialkarte je Texel (G Rauheit, B Metall, A Glanz) — dann gelten die Werte der Karte, die Zahlen oben sind nur ihr Mittel
            if (m.bild_material) {
                const karte = bild(m.bild_material);
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
                material.normalMap = bild(m.bild_normal);
                material.normalMap.colorSpace = THREE.NoColorSpace;
            }
            if (m.bild) {
                material.map = bild(m.bild);
                material.map.colorSpace = THREE.SRGBColorSpace;
                material.map.anisotropy = 4;
            }
            // Deckkraft der Daz-Stücke (14.11.2026, Zauberer: Haar und Bart standen als volle Flächen da) — Haarkarten wie `Genesis9netz.material`: MSAA-Deckung statt Schnitt
            if (m.bild_alpha) {
                material.alphaMap = bild(m.bild_alpha);
                material.alphaMap.colorSpace = THREE.NoColorSpace;
                material.alphaMap.anisotropy = 4;
                material.alphaToCoverage = true;
                material.alphaTest = 0.02;
            } else if (Number.isFinite(m.opazitaet)) {
                material.transparent = true;
                material.opacity = m.opazitaet;
            }
            // Farbe je Punkt zu Bild und Deckkraft (14.11.2026, Haar und Bart in Weg z: die Karten in der Farbe des Netzhaars an ihrer Stelle, `Haarregler.faerben`)
            if (m.punktfarbe) material.vertexColors = true;
            return material;
        });
        this._materialien.push(new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.8, side: THREE.DoubleSide }));
        // Das Anatomie-Stück bekommt die Haut des Körpers (wie in Charakter und Studio, `Anatomiebacken`) — im Hintergrund, danach zeichnet die Seite neu.
        Meshgenesisanatomie.anwenden(this, this._materialien, () => Meshgenesisflaechennetz.nachLaden?.());
        return this._materialien;
    }
}

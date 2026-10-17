/**
 * Mesh3daiflaechen — die gehäutete Figur EINER echten Probe auf der Seite „Mesh3D-AI“ (15.10.2026, Edgar: „wo ist die Umschaltung der Ansicht verschwunden auf Textur, Mesh usw?“).
 * Holt das Binärpaket `/api/mesh3dai/<job>/flaeche/<nr>/` (Server `Mesh3daiflaeche`: Punkte, Dreiecke, Teil je Dreieck, Außenfläche ja/nein) und baut daraus EINE Geometrie mit Lage, Normale und Farbe je Punkt;
 * jede Zeile bekommt davon ihren Teil als eigene Indexliste über dieselben Attribute (`teil`): die Außenfläche (Eingabe) oder die ganze Figur (gewünschte Ausgabe), nur bestimmte Teile (nur Körper, Kleider) und
 * Ausschnitte (Gesicht, Hände, Füße). Ein Dreieck gehört zu einem Ausschnitt, wenn sein nächster Rig-Punkt (Soll der Probe) einer der Knochen des Ausschnitts ist und es höchstens `radius` von dessen Mitte liegt.
 * Die Geometrien tragen `userData.gemeinsam` (die Felder entsorgen sie nicht); diese Ablage hält die letzten `GRENZE` Proben und entsorgt ältere selbst.
 * Seit Fassung 4 (15.10.2026) bringt eine Probe nur Punkte und Außenfläche; Netz, UV, Material und feste Indexlisten teilt sie mit allen Proben des Jobs (`Mesh3daiflaechennetz`), und die Gruppen
 * je Material lassen „Textur“ die Bilder der Figur zeigen (`bilder`).
 */
import * as THREE from 'three';
import { Mesh3daiflaechennetz } from './mesh3daiflaechennetz.js';
import { Mesh3daihaeutung } from './mesh3daihaeutung.js';

export class Mesh3daiflaechen {
    static GRENZE = 6;
    static _ablage = new Map();

    /** Die Fläche der Probe `nr` (Promise; wiederholte Aufrufe teilen sich die Anfrage). Wirft bei 404 — die Seite zeigt dann die Punktwolke. */
    static holen(jobId, nr) {
        const schluessel = `${jobId}:${nr}`;
        const z = Mesh3daiflaechen;
        if (z._ablage.has(schluessel)) {
            const alt = z._ablage.get(schluessel);
            z._ablage.delete(schluessel);
            z._ablage.set(schluessel, alt);
            return alt;
        }
        const versprechen = fetch(`/api/mesh3dai/${encodeURIComponent(jobId)}/flaeche/${nr}/`).then(async antwort => {
            if (!antwort.ok) throw new Error(antwort.status === 404 ? 'Fläche dieser Probe noch nicht gerechnet' : `HTTP ${antwort.status}`);
            const puffer = await antwort.arrayBuffer();
            const kopf = Mesh3daiflaechen._kopf(puffer);
            // Fassung 4: nur Punkte und Außenfläche, das Netz (volles Haar, UV, Material) kommt einmal je Job (`Mesh3daiflaechennetz`).
            if (kopf.netz) return new Mesh3daiflaechen(Mesh3daiflaechen.lesenMitNetz(puffer, await Mesh3daiflaechennetz.holen(jobId)));
            return new Mesh3daiflaechen(Mesh3daiflaechen.lesen(puffer));
        });
        versprechen.catch(() => z._ablage.delete(schluessel));
        z._ablage.set(schluessel, versprechen);
        while (z._ablage.size > z.GRENZE) {
            const [aelteste, alt] = z._ablage.entries().next().value;
            z._ablage.delete(aelteste);
            alt.then(f => f.entsorgen(), () => {});
        }
        return versprechen;
    }

    static _kopf(puffer) {
        const laenge = new DataView(puffer).getUint32(0, true);
        return JSON.parse(new TextDecoder().decode(new Uint8Array(puffer, 4, laenge)));
    }

    /**
     * Fassung 4: die Probe (int16-Punkte in `einheit_m`, Außenfläche) mit dem gemeinsamen Netz des Jobs. Dreiecke, Teile, Hautgewichte, UV, Material, Farbe je Punkt und die festen
     * Indexlisten kommen aus `netz` und werden von allen Proben geteilt.
     */
    static lesenMitNetz(puffer, netz) {
        const laenge = new DataView(puffer).getUint32(0, true);
        const probe = Mesh3daiflaechen._kopf(puffer);
        const { punkte: v, dreiecke: f, einheit_m: einheit } = probe;
        if (v * 2 !== netz.uv.length || f * 3 !== netz.dreiecke.length) throw new Error('Fläche passt nicht zum Anzeigenetz des Jobs');
        let ab = 4 + laenge;
        const quelle = new Int16Array(puffer, ab, v * 3);
        ab += v * 6 + (-(v * 6) & 3);
        const lage = new Float32Array(v * 3);
        for (let i = 0; i < lage.length; i++) lage[i] = quelle[i] * einheit;
        netz.farbe ??= Mesh3daiflaechen.farben(netz.kopf, netz.dreiecke, netz.etikett);
        return {
            kopf: { ...netz.kopf, fassung: probe.fassung }, haut: netz.kopf.haut, lage, dreiecke: netz.dreiecke, etikett: netz.etikett, aussen: new Uint8Array(puffer, ab, f),
            knochen: netz.knochen, gewicht: netz.gewicht, farbe: netz.farbe, uv: netz.uvAttribut, material: netz.material, netz, indexAblage: netz.indexAblage, ruhe: netz.ruhe,
        };
    }

    /** Das Paket von `Mesh3daiflaeche.paket` (Fassung 1–3) in Arrays zerlegen (Sichten auf den Puffer, nichts kopiert). */
    static lesen(puffer) {
        const laenge = new DataView(puffer).getUint32(0, true);
        const kopf = JSON.parse(new TextDecoder().decode(new Uint8Array(puffer, 4, laenge)));
        const { punkte: v, dreiecke: f } = kopf;
        const haut = kopf.haut ?? 0;
        let ab = 4 + laenge;
        const roh = { kopf, haut, lage: new Float32Array(puffer, ab, v * 3) };
        ab += v * 12;
        roh.dreiecke = new Uint32Array(puffer, ab, f * 3);
        ab += f * 12;
        // Hautgewichte (Fassung 2): `haut` Einflüsse je Punkt — Knochen (Index ins Rig) und Gewicht ×255; damit häutet `ausgabe` die Figur mit dem vorhergesagten Rig.
        if (haut) {
            roh.knochen = new Uint8Array(puffer, ab, v * haut);
            roh.gewicht = new Uint8Array(puffer, ab + v * haut, v * haut);
            ab += 2 * v * haut;
        }
        roh.etikett = new Uint8Array(puffer, ab, f);
        roh.aussen = new Uint8Array(puffer, ab + f, f);
        return roh;
    }

    /** Farbe je Punkt aus dem Teil seines Dreiecks (Teile teilen keine Punkte) — sRGB in den linearen Raum, den three.js erwartet. */
    static farben(kopf, dreiecke, etikett) {
        const farben = kopf.teilfarben.map(([r, g, b]) => new THREE.Color().setRGB(r / 255, g / 255, b / 255, THREE.SRGBColorSpace));
        const farbe = new Float32Array(kopf.punkte * 3);
        for (let i = 0; i < etikett.length; i++) {
            const c = farben[etikett[i]];
            for (let k = 0; k < 3; k++) {
                const o = dreiecke[i * 3 + k] * 3;
                farbe[o] = c.r;
                farbe[o + 1] = c.g;
                farbe[o + 2] = c.b;
            }
        }
        return new THREE.BufferAttribute(farbe, 3);
    }

    /** @param {{kopf, haut, lage: Float32Array, dreiecke, etikett, aussen, knochen?, gewicht?, farbe?: THREE.BufferAttribute}} roh — `farbe` geteilt, wenn mehrere Bilder dieselbe Verbindung haben (Animation) */
    constructor(roh) {
        this.kopf = roh.kopf;
        this.teile = roh.kopf.teile;
        this.haut = roh.haut ?? 0;
        this.lage = roh.lage;
        this.dreiecke = roh.dreiecke;
        this.etikett = roh.etikett;
        this.aussen = roh.aussen;
        this.knochen = roh.knochen;
        this.gewicht = roh.gewicht;
        /** Punkte in der Ruhelage (Float32Array V·3, nicht ausgerichtet) — mit ihnen häutet `ausgabe` das Ergebnis eines Laufs mit Daz-Winkeln genau; fehlt bei älteren Netzen. */
        this.ruhe = roh.ruhe ?? null;
        const basis = new THREE.BufferGeometry();
        basis.setAttribute('position', new THREE.BufferAttribute(this.lage, 3));
        basis.setIndex(new THREE.BufferAttribute(this.dreiecke, 1));
        basis.computeVertexNormals();
        this.attribute = { position: basis.getAttribute('position'), normal: basis.getAttribute('normal'), color: roh.farbe ?? Mesh3daiflaechen.farben(roh.kopf, roh.dreiecke, roh.etikett) };
        // UV und Material je Dreieck (Fassung 4 und Animation mit `textur`): „Textur“ zeichnet die Bilder der Figur (`bilder`), die übrigen Arten sehen nur die Gruppen nicht.
        if (roh.uv) this.attribute.uv = roh.uv instanceof THREE.BufferAttribute ? roh.uv : new THREE.BufferAttribute(roh.uv, 2);
        this.material = roh.material ?? null;
        this.netz = roh.netz ?? null;
        this._geometrien = new Map();
        this._indexAblage = roh.indexAblage ?? null;
        this._farbeGeteilt = !!roh.farbe;
        this._uvGeteilt = roh.uv instanceof THREE.BufferAttribute;
        // Nächster Rig-Punkt je Dreieck, erst bei Bedarf gerechnet (−1 = noch nicht) — und nur für Dreiecke, die schon im Radius eines Ausschnitts liegen.
        this._naechster = new Int16Array(this.etikett.length).fill(-1);
    }

    /**
     * Dieselbe Figur, gehäutet mit dem VORHERGESAGTEN Rig — für „Ausgabe des Netzes“; `null` ohne Hautgewichte (Fassung 1).
     * `genau` (`{dreh, ruhezentren}`, Lauf mit Daz-Winkeln, 16.10.2026): aus der Ruhelage mit den Drehungen des Netzes, dieselbe Hautmischung wie das Ziel im Datenskript. Sonst die Näherung aus den
     * Rig-Punkten (`Mesh3daihaeutung.knochenmatrizen`), ausgehend von der Figur in der Pose des Soll.
     * Teile und Ausschnitte (`teil`) wählen dieselben Dreiecke wie im Soll (die Auswahl rechnet mit den Soll-Punkten); nur die Lage ist verformt.
     */
    ausgabe(soll, vorhersage, eltern, genau = null) {
        if (!this.haut) return null;
        if (this._ausgabe?.quelle === vorhersage) return this._ausgabe.flaeche;
        const lage = genau && this.ruhe
            ? Mesh3daihaeutung.verformen(this.ruhe, this.knochen, this.gewicht, this.haut, Mesh3daihaeutung.ausDrehungen(genau.dreh, vorhersage, genau.ruhezentren))
            : Mesh3daihaeutung.verformen(this.lage, this.knochen, this.gewicht, this.haut, Mesh3daihaeutung.knochenmatrizen(soll, vorhersage, eltern));
        const basis = new THREE.BufferGeometry();
        basis.setAttribute('position', new THREE.BufferAttribute(lage, 3));
        basis.setIndex(new THREE.BufferAttribute(this.dreiecke, 1));
        basis.computeVertexNormals();
        const flaeche = Object.create(this);
        flaeche.attribute = { ...this.attribute, position: basis.getAttribute('position'), normal: basis.getAttribute('normal') };
        flaeche._geometrien = new Map();
        flaeche._farbeGeteilt = true;         // Farbe und UV gehören der Fläche des Soll
        flaeche._uvGeteilt = Boolean(this.attribute.uv);
        this._ausgabe?.flaeche.entsorgen();
        this._ausgabe = { quelle: vorhersage, flaeche };
        return flaeche;
    }

    /** Anzahl Dreiecke der Außenfläche (für die Texte). */
    get aussenZahl() {
        let n = 0;
        for (let i = 0; i < this.aussen.length; i++) n += this.aussen[i];
        return n;
    }

    /**
     * Die Geometrie eines Teils der Figur.
     * @param {{aussen: boolean, etiketten?: string[]|null, ausschnitt?: {mitte: number[], radius: number, knochen: number[]}|null, rig?: number[][]}} wahl
     *   `aussen` nur die Außenfläche; `etiketten` nur diese Teile (leer/`null` = alle); `ausschnitt` mit `rig` = Soll der Probe (138 Punkte) für die Zuordnung zum nächsten Knochen
     */
    teil({ aussen, etiketten = null, ausschnitt = null, rig = null }) {
        const schluessel = `${aussen ? 1 : 0}|${(etiketten ?? []).join(',')}|${ausschnitt ? ausschnitt.mitte.join(',') : ''}`;
        if (this._geometrien.has(schluessel)) return this._geometrien.get(schluessel);
        // Ohne Außenfläche und Ausschnitt hängt die Auswahl nur an der Verbindung: Proben der Fassung 4 und die Bilder der Animation teilen sich diese Indexliste (`indexAblage`).
        const fest = !aussen && !ausschnitt && this._indexAblage;
        let gemerkt = fest ? this._indexAblage.get(schluessel) : null;
        if (!gemerkt) {
            const erlaubt = etiketten?.length ? new Set(etiketten.map(e => this.teile.indexOf(e))) : null;
            const knochen = ausschnitt ? new Set(ausschnitt.knochen) : null;
            const r2 = ausschnitt ? ausschnitt.radius ** 2 : 0;
            const [mx, my, mz] = ausschnitt?.mitte ?? [0, 0, 0];
            const m = ausschnitt ? this._mitten() : null;
            const wahl = new Uint32Array(this.etikett.length);
            let n = 0;
            for (let i = 0; i < this.etikett.length; i++) {
                if (aussen && !this.aussen[i]) continue;
                if (erlaubt && !erlaubt.has(this.etikett[i])) continue;
                if (ausschnitt) {
                    const x = m[i * 3], y = m[i * 3 + 1], z = m[i * 3 + 2];
                    if ((x - mx) ** 2 + (y - my) ** 2 + (z - mz) ** 2 > r2) continue;
                    if (!knochen.has(this._naechsterVon(i, x, y, z, rig))) continue;
                }
                wahl[n++] = i;
            }
            gemerkt = this._index(wahl.subarray(0, n));
            if (fest) this._indexAblage.set(schluessel, gemerkt);
        }
        const geo = new THREE.BufferGeometry();
        for (const [name, attribut] of Object.entries(this.attribute)) geo.setAttribute(name, attribut);
        geo.setIndex(gemerkt.index);
        for (const g of gemerkt.gruppen) geo.addGroup(g.start, g.count, g.materialIndex);
        geo.computeBoundingSphere();
        geo.userData.gemeinsam = true;
        geo.userData.indexGeteilt = !!fest;
        geo.userData.dreiecke = gemerkt.index.count / 3;
        this._geometrien.set(schluessel, geo);
        return geo;
    }

    /**
     * Die Indexliste der gewählten Dreiecke — mit Material je Dreieck nach Material sortiert (Zählsortierung, Reihenfolge innerhalb eines Materials bleibt), dazu je Material eine Gruppe
     * (`materialIndex` = Platz in `bilder()`, Material −1 → das letzte, Farbe je Punkt). Ohne Material eine Liste ohne Gruppen.
     */
    _index(wahl) {
        const d = this.dreiecke;
        const index = new Uint32Array(wahl.length * 3);
        const gruppen = [];
        if (!this.material) {
            wahl.forEach((i, k) => { index[k * 3] = d[i * 3]; index[k * 3 + 1] = d[i * 3 + 1]; index[k * 3 + 2] = d[i * 3 + 2]; });
            return { index: new THREE.BufferAttribute(index, 1), gruppen };
        }
        let zahl = this.netz?.kopf?.materialien?.length;
        if (zahl === undefined) {
            zahl = 0;
            for (let i = 0; i < this.material.length; i++) if (this.material[i] >= zahl) zahl = this.material[i] + 1;   // keine Spreizung: 446.852 Werte sprengten den Stapel
        }
        const schluessel = i => (this.material[i] < 0 ? zahl : this.material[i]);
        const anzahl = new Uint32Array(zahl + 1);
        for (const i of wahl) anzahl[schluessel(i)]++;
        const start = new Uint32Array(zahl + 1);
        for (let s = 1; s <= zahl; s++) start[s] = start[s - 1] + anzahl[s - 1];
        const platz = start.slice();
        for (const i of wahl) {
            const k = platz[schluessel(i)]++;
            index[k * 3] = d[i * 3];
            index[k * 3 + 1] = d[i * 3 + 1];
            index[k * 3 + 2] = d[i * 3 + 2];
        }
        for (let s = 0; s <= zahl; s++) if (anzahl[s]) gruppen.push({ start: start[s] * 3, count: anzahl[s] * 3, materialIndex: s });
        return { index: new THREE.BufferAttribute(index, 1), gruppen };
    }

    /** Die Materialien mit den Bildern der Figur (Reihenfolge der Gruppen von `teil`) oder `null` — dann zeichnet „Textur“ die Farbe je Punkt. */
    bilder() {
        return this.material && this.netz ? this.netz.materialien() : null;
    }

    /** Mitte je Dreieck (Soll-Lage), einmal je Fläche gerechnet — die verformte Ausgabe teilt sie über den Prototyp (die Auswahl richtet sich nach dem Soll). */
    _mitten() {
        if (this._mittenFeld) return this._mittenFeld;
        const l = this.lage, d = this.dreiecke;
        const m = new Float32Array(d.length);
        for (let i = 0; i < d.length; i += 3) {
            const a = d[i] * 3, b = d[i + 1] * 3, c = d[i + 2] * 3;
            m[i] = (l[a] + l[b] + l[c]) / 3;
            m[i + 1] = (l[a + 1] + l[b + 1] + l[c + 1]) / 3;
            m[i + 2] = (l[a + 2] + l[b + 2] + l[c + 2]) / 3;
        }
        this._mittenFeld = m;
        return m;
    }

    /** Nächster Rig-Punkt (Soll) des Dreiecks `i` mit der Mitte (x, y, z) — einmal je Dreieck gerechnet; die verformte Ausgabe teilt das Feld über den Prototyp. */
    _naechsterVon(i, x, y, z, rig) {
        if (this._naechster[i] >= 0) return this._naechster[i];
        let best = 0, bestD = Infinity;
        for (let j = 0; j < rig.length; j++) {
            const p = rig[j];
            const dd = (x - p[0]) ** 2 + (y - p[1]) ** 2 + (z - p[2]) ** 2;
            if (dd < bestD) { bestD = dd; best = j; }
        }
        this._naechster[i] = best;
        return best;
    }

    /** Für `n` Punkte (`punkt(i)` → [x, y, z]) der Index des nächsten der `rig`-Punkte. Auch für die Punktwolke der Eingabe. */
    static naechste(n, punkt, rig) {
        const aus = new Int16Array(n);
        for (let i = 0; i < n; i++) {
            const [x, y, z] = punkt(i);
            let best = 0, bestD = Infinity;
            for (let j = 0; j < rig.length; j++) {
                const p = rig[j];
                const dd = (x - p[0]) ** 2 + (y - p[1]) ** 2 + (z - p[2]) ** 2;
                if (dd < bestD) { bestD = dd; best = j; }
            }
            aus[i] = best;
        }
        return aus;
    }

    /** Die eigenen Grafikpuffer freigeben — geteilte (Farbe und feste Indexlisten der Animation) vorher abhängen, sonst lädt three.js sie beim nächsten Bild neu hoch. */
    entsorgen() {
        for (const geo of this._geometrien.values()) {
            if (this._farbeGeteilt) geo.deleteAttribute('color');
            if (this._uvGeteilt) geo.deleteAttribute('uv');
            if (geo.userData.indexGeteilt) geo.setIndex(null);
            geo.dispose();
        }
        this._geometrien.clear();
        if (Object.hasOwn(this, '_ausgabe') && this._ausgabe) {
            this._ausgabe.flaeche.entsorgen();
            this._ausgabe = null;
        }
    }
}

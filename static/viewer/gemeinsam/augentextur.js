import { Detailfarben } from './detailfarben.js';

/**
 * Augentextur — Iris mit Fasern und Augapfel mit Äderchen aus Karten, einstellbar im Bereich „Augen · Wimpern" des Reiters „Modell".
 *
 * WARUM (Edgar, 06.10.2026: „übernimm die Poren und die Augen, wie kann man die im UI einstellen, neue Skins / Augen?"): Iris und Sklera waren je EINE Farbe
 * (`Detailfarben`). matmadness/HumanShaders (MIT/CC BY 4.0) bringt Iris- und Sklerakarten (Albedo und Normale) mit; hier sind sie zu EINER Karte je Irisfarbe
 * zusammengesetzt (`auge_<farbe>.jpg`, Iris mittig, Durchmesser 0,361 des Augapfels — gemessen am Basisnetz: 5,3 mm gegen 14,7 mm) und eine Normalkarte
 * (`auge_normal.png`). Der Grund für EINE Karte: Sklera (Gruppe 4) und Iris (Gruppe 6) teilen 32 Ecken, zwei getrennte Abbildungen hätten an dieser Ringnaht
 * die Karte der einen Gruppe über die Dreiecke der anderen gezogen.
 *
 * Die UV der Augen werden aus den Punkten gerechnet (planare Frontalprojektion je Auge: Mitte = Schwerpunkt der Iris, Radius = größter Abstand der Sklera von
 * dieser Mitte, ±0,5 um die Mitte). Die UV der Augen im Atlas der Haut brauchte bisher niemand (flache Farben); sie gehören nur den Augenecken, und die
 * Rechnung läuft bei jedem Anwenden neu, weil Morphs die Augen verschieben. Eine Textur tönt nicht: Mit der Vorgabefarbe der Felder `iris`/`sklera` wird die
 * Materialfarbe weiß (wie bei der Hauttextur), eine eigene Farbe multipliziert die Karte. „Keine" nimmt die Karten wieder weg, die Farben gelten wie vorher.
 *
 * Felder (`Koerperdetails.VORGABE`): `augen_textur` (Irisfarbe, leer = aus), `augen_relief` (Stärke der Normalkarte 0..1). Ohne `import * as THREE` außer beim Laden einer
 * Karte: so läuft das Modul in Node mit Attrappen (`test_js_augentextur.py`).
 */
export class Augentextur {

    static FELD = 'augen_textur';
    static RELIEF = 'augen_relief';
    static SKLERA = 4;
    static HORNHAUT = 5;
    static IRIS = 6;
    /** Deckung der Hornhaut mit Karte (ohne: 0,3 aus `koerpermaterialien.js`). */
    static HORNHAUT_DECKUNG = 0.1;
    static ADRESSE = '/static/img/humanshaders/';
    static NORMALKARTE = 'auge_normal';
    /** Stärke 1 der Normalkarte = diese Skalierung (HumanShaders: `normal_strength` 1,0 als Vorgabe, hier bis 1,5). */
    static RELIEF_MAX = 1.5;
    static WAHL = [['', 'Keine (Farben)'], ['braun', 'Braun'], ['haselnuss', 'Haselnuss'], ['gruen', 'Grün'], ['blau', 'Blau'], ['grau', 'Grau']];

    static _geladen = new Map();
    /** Netz → Nummer des jüngsten `anwenden` (überholte Läufe setzen nichts mehr). */
    static _lauf = new WeakMap();

    static eintrag(wert) {
        return Augentextur.WAHL.find(([w]) => w && w === wert) || null;
    }

    /**
     * Die Karten nach `details` auf Iris und Sklera setzen oder abnehmen. `index`/`gruppen`/`punkte` sind Topologie und Lage des Netzes (wie in `Koerperdetails`).
     * @returns Promise<boolean> — true, wenn die Augen die Karten tragen
     */
    static async anwenden(netz, details, index, gruppen, punkte) {
        const materialien = Array.isArray(netz?.material) ? netz.material : null;
        const sklera = materialien?.[Augentextur.SKLERA];
        const iris = materialien?.[Augentextur.IRIS];
        if (!sklera || !iris) return false;
        const lauf = (Augentextur._lauf.get(netz) || 0) + 1;
        Augentextur._lauf.set(netz, lauf);
        const eintrag = Augentextur.eintrag(details?.[Augentextur.FELD]);
        if (!eintrag) { Augentextur.entfernen(materialien); return false; }
        const uv = netz.geometry?.attributes?.uv;
        if (!uv?.array || !index || !gruppen?.length || !punkte) return false;
        if (!Augentextur.uv(uv.array, index, gruppen, punkte)) return false;
        uv.needsUpdate = true;
        const [farbe, normale] = await Promise.all([Augentextur.laden(`auge_${eintrag[0]}`, true), Augentextur.laden(Augentextur.NORMALKARTE, false)]);
        if (Augentextur._lauf.get(netz) !== lauf) return false;       // überholt (siehe `Hautporen.anwenden`)
        const relief = Math.min(1, Math.max(0, Number(details[Augentextur.RELIEF]) || 0)) * Augentextur.RELIEF_MAX;
        for (const [material, feld] of [[sklera, 'sklera'], [iris, 'iris']]) {
            const neu = !material.map || !material.normalMap;
            material.map = farbe;
            material.normalMap = normale;
            material.normalScale?.set?.(relief, relief);
            if (String(details[feld] || '').toLowerCase() === Detailfarben.VORGABE[feld]) material.color?.setRGB?.(1, 1, 1);
            if (neu) material.needsUpdate = true;
        }
        // Die Hornhaut legt 30 % Weiß über Iris und Pupille und wäscht die Zeichnung aus (gemessen am Bild: die Pupille stand hellgrau) — mit Karte fast klar.
        const horn = materialien[Augentextur.HORNHAUT];
        if (horn && 'opacity' in horn) {
            horn.userData ??= {};
            horn.userData.augenOpacity ??= horn.opacity;
            horn.opacity = Augentextur.HORNHAUT_DECKUNG;
        }
        return true;
    }

    /** Die Karten von Iris und Sklera nehmen (und die Hornhaut wieder trüben) — die Farben setzt danach `Detailfarben`. @returns Zahl der Materialien, die Karten trugen */
    static entfernen(materialien) {
        let weg = 0;
        for (const nr of [Augentextur.SKLERA, Augentextur.IRIS]) {
            const m = materialien[nr];
            if (!m?.map) continue;
            m.map = null;
            m.normalMap = null;
            m.needsUpdate = true;
            weg += 1;
        }
        const horn = materialien[Augentextur.HORNHAUT];
        if (horn?.userData?.augenOpacity !== undefined) {
            horn.opacity = horn.userData.augenOpacity;
            delete horn.userData.augenOpacity;
        }
        return weg;
    }

    /**
     * Die UV der Augenecken: je Auge (Seite von x) planar in der x-y-Ebene, Mitte = Schwerpunkt der Iris, 2 × größter Abstand der Sklera = 1. Iris und Sklera
     * bekommen dieselbe Abbildung (die gemeinsamen 32 Ecken stimmen damit).
     * @returns Zahl der gesetzten Ecken (0 = kein Auge gefunden)
     */
    static uv(uv, index, gruppen, p) {
        const ecken = (nummer) => {
            const menge = new Set();
            for (const g of gruppen) {
                if (g.materialIndex !== nummer) continue;
                for (let k = g.start; k < g.start + g.count; k++) menge.add(index[k]);
            }
            return [...menge];
        };
        const iris = ecken(Augentextur.IRIS);
        const sklera = ecken(Augentextur.SKLERA);
        let gesetzt = 0;
        for (const seite of [-1, 1]) {
            const meine = (e) => (p[3 * e] < 0 ? -1 : 1) === seite;
            const i = iris.filter(meine);
            const s = sklera.filter(meine);
            if (!i.length || !s.length) continue;
            const cx = i.reduce((a, e) => a + p[3 * e], 0) / i.length;
            const cy = i.reduce((a, e) => a + p[3 * e + 1], 0) / i.length;
            const radius = s.reduce((a, e) => Math.max(a, Math.hypot(p[3 * e] - cx, p[3 * e + 1] - cy)), 0);
            if (!(radius > 0)) continue;
            for (const e of new Set([...i, ...s])) {
                uv[2 * e] = 0.5 + (p[3 * e] - cx) / (2 * radius);
                uv[2 * e + 1] = 0.5 + (p[3 * e + 1] - cy) / (2 * radius);
                gesetzt += 1;
            }
        }
        return gesetzt;
    }

    /** Eine Karte laden — einmal je Kennung; Albedo in sRGB, die Normale linear. */
    static async laden(name, farbig) {
        if (Augentextur._geladen.has(name)) return Augentextur._geladen.get(name);
        const THREE = await import('three');
        const textur = await new THREE.TextureLoader().loadAsync(`${Augentextur.ADRESSE}${name}.${farbig ? 'jpg' : 'png'}`);
        textur.colorSpace = farbig ? THREE.SRGBColorSpace : THREE.NoColorSpace;
        textur.anisotropy = 8;
        Augentextur._geladen.set(name, textur);
        return textur;
    }
}

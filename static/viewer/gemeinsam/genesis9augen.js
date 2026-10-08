import { Augentextur } from './augentextur.js';

/**
 * Genesis9augen — Augentextur einer Genesis-9-Figur (Katalog UND ARP-Import).
 *
 * WARUM EIN EIGENES MODUL (Edgar, 08.10.2026: „augen ändern in der Toolbar
 * funktioniert nicht"): `Koerperdetails`/`Augentextur` sind fürs HumanBody-Netz
 * gebaut — dort sind Sklera und Iris Materialgruppen DES KÖRPERNETZES
 * (`Koerperdetails.GRUPPE.sklera = 4`, `.iris = 6`). Bei Genesis 9 liegen die
 * Augen in einem EIGENEN Netz (`inst.anhangNetze.augen`); die Indizes 4/6 am
 * `bodyMesh` zeigen dort auf „Arms"/„Body" — ein Reglerzug hätte diese Materialien
 * überschrieben statt der Augen, gemessen am geladenen „cute girl" (`genesis9netz.js`
 * `material.userData.gruppe`: bodyMesh[4]=Arms, bodyMesh[6]=Body; die Augen stehen in
 * `anhangNetze.augen` auf [1]=„Eye Left", [2]=„Eye Right").
 *
 * STRUKTUR DES AUGENNETZES: vier Materialien — 0/3 „EyeMoisture" (Glanzschicht,
 * keine Karte), 1/2 „Eye Left"/„Eye Right" je EIN Material für Sklera UND Iris
 * zusammen (Daz liefert eine fertige Augentextur, keine getrennten Gruppen wie bei
 * HumanBody). Die Server-UV jedes Auges belegen ein eigenes Viertel eines
 * Textur-Atlasses (gemessen: U/V je jeweils ~0,48 breit, nicht 0..1) — eine
 * HumanShaders-Ersatzkarte (eigenständiges 0..1-Bild) braucht die UV linear auf
 * 0..1 NORMALISIERT, sonst zeigt nur ein Achtel der Karte verzerrt. Die
 * Original-UV werden dafür gesichert (`geo.userData._genesis9AugenUv`) und bei
 * „Original" exakt zurückgeschrieben — sonst bliebe das Originalbild nach einem
 * Kartenwechsel dauerhaft verzerrt.
 */
export class Genesis9augen {

    static EYE_LEFT = 1;
    static EYE_RIGHT = 2;

    /** Erster Eintrag „Original" statt HumanBodys „Keine (Farben)" — Genesis 9 hat
     *  keine texturlose Darstellung, nur die vom Modell gelieferte Augenkarte. */
    static WAHL = [[Augentextur.ORIGINAL, 'Original Augen vom Modell'], ...Augentextur.WAHL.filter(([w]) => w)];

    /**
     * Die Augenkarte anwenden (oder auf „Original" zurück) — sofort, ohne Server.
     * @returns Promise<boolean> — true, wenn ein Augennetz gefunden wurde
     */
    static async anwenden(inst, details) {
        const netz = inst?.anhangNetze?.augen;
        const geo = netz?.geometry;
        const uv = geo?.attributes?.uv;
        const index = geo?.index?.array;
        const gruppen = geo?.groups;
        if (!netz || !Array.isArray(netz.material) || !uv || !index || !gruppen?.length) return false;
        Genesis9augen._uvSichern(geo, uv, index, gruppen);

        const wert = details?.[Augentextur.FELD];
        const eintrag = wert && wert !== Augentextur.ORIGINAL ? Augentextur.eintrag(wert) : null;
        const relief = Math.min(1, Math.max(0, Number(details?.[Augentextur.RELIEF]) || 0)) * Augentextur.RELIEF_MAX;
        const karten = eintrag ? await Promise.all([
            Augentextur.laden(`auge_${eintrag[0]}`, true), Augentextur.laden(Augentextur.NORMALKARTE, false),
        ]) : null;

        for (const materialIndex of [Genesis9augen.EYE_LEFT, Genesis9augen.EYE_RIGHT]) {
            const material = netz.material[materialIndex];
            if (!material) continue;
            material.userData._original ??= { map: material.map, normalMap: material.normalMap };
            if (!karten) {
                Genesis9augen._uvZurueck(geo, uv, index, gruppen, materialIndex);
                if (material.map !== material.userData._original.map) {
                    material.map = material.userData._original.map;
                    material.normalMap = material.userData._original.normalMap;
                    material.color?.setRGB?.(1, 1, 1);
                    material.needsUpdate = true;
                }
                continue;
            }
            Genesis9augen._uvNormalisieren(geo, uv.array, index, gruppen, materialIndex);
            const [farbe, normale] = karten;
            material.map = farbe;
            material.normalMap = normale;
            material.normalScale?.set?.(relief, relief);
            material.color?.setRGB?.(1, 1, 1);
            material.needsUpdate = true;
        }
        uv.needsUpdate = true;
        return true;
    }

    /** Alle Ecken eines Materialindexes (ohne Dopplung — jede Ecke kommt in mehreren Dreiecken vor). */
    static _ecken(index, gruppen, materialIndex) {
        const gruppe = gruppen.find(g => g.materialIndex === materialIndex);
        if (!gruppe) return [];
        const menge = new Set();
        for (let k = gruppe.start; k < gruppe.start + gruppe.count; k++) menge.add(index[k]);
        return [...menge];
    }

    /** Die ungestreckten Original-UV der Augen-Ecken EINMAL merken (`detailbasis`-Muster, `koerperdetails.js`). */
    static _uvSichern(geo, uv, index, gruppen) {
        if (geo.userData._genesis9AugenUv) return;
        const ecken = [...Genesis9augen._ecken(index, gruppen, Genesis9augen.EYE_LEFT),
                       ...Genesis9augen._ecken(index, gruppen, Genesis9augen.EYE_RIGHT)];
        const werte = new Float32Array(ecken.length * 2);
        const lage = new Map();
        ecken.forEach((e, i) => {
            werte[2 * i] = uv.array[2 * e]; werte[2 * i + 1] = uv.array[2 * e + 1];
            lage.set(e, i);
        });
        geo.userData._genesis9AugenUv = { werte, lage };
    }

    /** Die original gesicherte UV einer Ecke — oder die aktuelle, wenn sie (noch) nicht gesichert ist. */
    static _original(geo, uvArray, e) {
        const { werte, lage } = geo.userData._genesis9AugenUv;
        const i = lage.get(e);
        return i === undefined ? [uvArray[2 * e], uvArray[2 * e + 1]] : [werte[2 * i], werte[2 * i + 1]];
    }

    /** UV eines Auges aus der Originallage, linear auf 0..1 normalisiert (Bounding-Box der Ecken dieses Materials). */
    static _uvNormalisieren(geo, uvArray, index, gruppen, materialIndex) {
        const betroffene = Genesis9augen._ecken(index, gruppen, materialIndex);
        let minU = Infinity, maxU = -Infinity, minV = Infinity, maxV = -Infinity;
        for (const e of betroffene) {
            const [u, v] = Genesis9augen._original(geo, uvArray, e);
            minU = Math.min(minU, u); maxU = Math.max(maxU, u);
            minV = Math.min(minV, v); maxV = Math.max(maxV, v);
        }
        const bU = Math.max(1e-6, maxU - minU), bV = Math.max(1e-6, maxV - minV);
        for (const e of betroffene) {
            const [u, v] = Genesis9augen._original(geo, uvArray, e);
            uvArray[2 * e] = (u - minU) / bU;
            uvArray[2 * e + 1] = (v - minV) / bV;
        }
    }

    /** UV eines Auges auf die gesicherte Originallage zurück. */
    static _uvZurueck(geo, uv, index, gruppen, materialIndex) {
        const { werte, lage } = geo.userData._genesis9AugenUv;
        for (const e of Genesis9augen._ecken(index, gruppen, materialIndex)) {
            const i = lage.get(e);
            if (i === undefined) continue;
            uv.array[2 * e] = werte[2 * i];
            uv.array[2 * e + 1] = werte[2 * i + 1];
        }
    }
}

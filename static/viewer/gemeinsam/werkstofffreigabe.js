/**
 * Werkstofffreigabe — Grafikspeicher eines Netzes wirklich freigeben.
 *
 * Anlass: Sparring mit Gemma am 18.08.2026, Bereich „Szene: MakeHuman-Proxy".
 * `material.dispose()` gibt die TEXTUREN NICHT mit frei — so steht es auch in
 * der Three.js-Doku („Textures of a material don't get disposed"). Wer ein Netz
 * ersetzt und nur Geometrie und Werkstoff freigibt, lässt jede Bilddatei im
 * Grafikspeicher zurück. Beim Regler-Refit alle 400 ms sind das in einer Minute
 * 150 Texturen.
 *
 * Die Klasse räumt deshalb ALLE Texturfelder eines Werkstoffs ab (`map`,
 * `normalMap`, `roughnessMap`, …) — sie sucht sie am Objekt, statt eine Liste
 * zu führen: Ein Werkstoff, der morgen ein weiteres Feld bekommt, wäre in einer
 * Liste nicht enthalten.
 */
export class Werkstofffreigabe {

    /** Einen Werkstoff samt seiner Texturen freigeben. */
    static werkstoff(werkstoff) {
        if (!werkstoff) return;
        for (const wert of Object.values(werkstoff)) {
            if (wert && wert.isTexture) wert.dispose();
        }
        werkstoff.dispose?.();
    }

    /** Ein Netz vollständig: Geometrie, Werkstoff(e), Texturen. */
    static netz(netz) {
        if (!netz) return;
        netz.geometry?.dispose?.();
        if (Array.isArray(netz.material)) {
            netz.material.forEach(einer => Werkstofffreigabe.werkstoff(einer));
        } else {
            Werkstofffreigabe.werkstoff(netz.material);
        }
    }

    /** Ein ganzer Teilbaum (GLB-Import, Haare, Szenenobjekte). */
    static baum(wurzel) {
        wurzel?.traverse?.(teil => {
            if (teil.isMesh || teil.isSkinnedMesh || teil.isPoints
                    || teil.isLine) {
                Werkstofffreigabe.netz(teil);
            }
        });
    }
}

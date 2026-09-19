/**
 * Skelettereignis — sagt am Dokument, wenn eine Figur ein NEUES Skelett hat.
 *
 * BEFUND (Edgar, 19.09.2026, mit Bild: „Hose (genesis) animiert nicht, und
 * Garment Code auch nicht"): Eine Genesis-9-Figur baut ihr Skelett bei jedem
 * Umbau neu (`Genesis9Modell.koerperAufbauen` — Reglerzug, Strg+Alt+H, die
 * feine Stufe nach dem Käfig beim Laden). `_kleiderBinden` bindet danach die
 * Daz-Stücke um; ein GarmentCode-Stück (ohne `hautgewichte`, mit `gcRig`)
 * blieb an den ALTEN Knochen hängen, die niemand mehr bewegt — im Browser
 * gemessen: nach `neuFormen()` `netz.skeleton === altesSkelett`. Es stand in
 * der Ruhelage, während der Körper spielte.
 *
 * Das Modell liegt in `gemeinsam/` und kennt die Szene nicht; es meldet nur.
 * `scene/garmentcode_nachbindung.js` hört zu und bindet nach. Dasselbe
 * Muster wie `stueckereignis.js`.
 */
export class Skelettereignis {

    static NAME = 'figur-skelett';

    /** `detail`: `{inst}` — die Figur mit dem frischen Skelett. */
    static melden(inst) {
        if (typeof document === 'undefined') return false;
        document.dispatchEvent(new CustomEvent(Skelettereignis.NAME, { detail: { inst } }));
        return true;
    }

    static hoeren(zuhoerer) {
        document.addEventListener(Skelettereignis.NAME, (e) => zuhoerer(e.detail || {}));
    }
}

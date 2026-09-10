import * as THREE from 'three';

/**
 * Garmentstoff — wie ein GarmentCode-Stück aussieht.
 *
 * EIGENES MODUL (09.09.2026), weil das Material an DREI Stellen entsteht
 * oder gelesen wird und dabei zweimal auseinandergelaufen ist:
 *
 *   garmentcode_anziehen   baut das Netz und braucht ein Material dafür
 *   garmentcode_material   die drei Regler im Reiter
 *   garmentcode_ablage     speichert und stellt wieder her
 *
 * DER BEFUND, DER DAS MODUL AUSGELÖST HAT (Edgar: „modell gespeichert
 * (farbe rot des T-Shirt), neu geladen - Farbe ist weg"): `einhaengen`
 * baute bei JEDEM Aufruf ein frisches Material mit der Vorgabefarbe — und
 * es läuft nicht nur beim Bauen, sondern auch aus `nachbinden`, sobald das
 * Skelett entsteht. Beim Laden einer Szene passiert das direkt nachdem die
 * gespeicherte Farbe gesetzt wurde. Im Browser gemessen: Das Einhängen
 * eines zweiten Stücks setzte das erste von #ff0000 auf #dcd8d0 zurück.
 *
 * Deshalb nimmt `neu()` die bisherigen Werte entgegen. Ein Stück, das schon
 * hängt, behält damit sein Aussehen über jedes Neu-Einhängen hinweg.
 */
export class Garmentstoff {

    /** Stoff-Farbe, solange GarmentCode keine mitgibt. */
    static FARBE = 0xdcd8d0;

    /** Rauheit und Metallanteil der Vorgabe — Stoff glänzt nicht. */
    static RAUHEIT = 0.85;
    static METALL = 0.0;

    /**
     * Ein Material für ein Stück; `bisher` sind die Werte, die es schon
     * trug (aus `werte()`), sonst die Vorgabe.
     */
    static neu(bisher = null) {
        return new THREE.MeshStandardMaterial({
            color: bisher?.farbe ?? Garmentstoff.FARBE,
            roughness: bisher?.rauheit ?? Garmentstoff.RAUHEIT,
            metalness: bisher?.metall ?? Garmentstoff.METALL,
            // Stoff wird von beiden Seiten gesehen — ein Rock von innen,
            // ein Ärmel im Durchblick.
            side: THREE.DoubleSide,
        });
    }

    /**
     * Die Werte eines vorhandenen Materials — oder `null`.
     *
     * Muss gelesen werden, BEVOR das Netz entfernt wird: `entfernen` gibt
     * das Material frei, und danach sind die Werte nicht mehr zu holen.
     */
    static werte(netz) {
        const m = netz?.material;
        if (!m) return null;
        return {
            farbe: m.color ? m.color.getHex() : null,
            rauheit: typeof m.roughness === 'number' ? m.roughness : null,
            metall: typeof m.metalness === 'number' ? m.metalness : null,
        };
    }

    /** Werte auf ein Material legen; liefert 1, wenn etwas gesetzt wurde. */
    static auflegen(netz, werte) {
        const m = netz?.material;
        if (!m || !werte) return 0;
        if (werte.farbe !== null && werte.farbe !== undefined) {
            m.color?.set(werte.farbe);
        }
        if (typeof werte.rauheit === 'number') m.roughness = werte.rauheit;
        if (typeof werte.metall === 'number') m.metalness = werte.metall;
        return 1;
    }
}

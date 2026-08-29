/**
 * Netzentsorgung — Geometrie und Material eines Netzes freigeben.
 *
 * WARUM DIESES MODUL (28.08.2026, Befund `doppelcode`): Diese drei Zeilen
 *
 *     mesh.geometry.dispose();
 *     const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
 *     mats.forEach(m => m.dispose());
 *
 * standen an SIEBEN Stellen, viermal davon in eine `traverse`-Schleife
 * gewickelt (Haare sind eine GLTF-Szene mit mehreren Netzen).
 *
 * WAS PASSIERT, WENN MAN SIE VERGISST: Nichts Sichtbares. Three.js gibt den
 * GPU-Speicher einer Geometrie nur auf `dispose()` hin frei; ohne den Aufruf
 * waechst der Verbrauch mit jedem Modellwechsel weiter, bis der Kontext
 * verlorengeht („WebGL context lost"). Genau deshalb ist die Stelle es wert,
 * einmal richtig zu stehen statt siebenmal fast richtig.
 *
 * Ein Netz kann EIN Material haben oder eine LISTE (Materialgruppen des
 * Koerpers). Das ist der Grund fuer die `Array.isArray`-Zeile, und es ist die
 * Zeile, die in einer Kopie fehlt.
 */
export class Netzentsorgung {

    /**
     * Ein einzelnes Netz freigeben.
     *
     * @param netz Three.Mesh — `null`/`undefined` ist erlaubt und tut nichts.
     * @param mitGeometrie false, wenn die Geometrie weiterverwendet wird.
     */
    static netz(netz, mitGeometrie = true) {
        if (!netz) return;
        if (mitGeometrie && netz.geometry) netz.geometry.dispose();
        if (!netz.material) return;
        const werkstoffe = Array.isArray(netz.material) ? netz.material
                                                        : [netz.material];
        for (const werkstoff of werkstoffe) werkstoff.dispose();
    }

    /**
     * Jedes Netz unter diesem Objekt freigeben.
     *
     * Fuer GLTF-Szenen (Haare, Requisiten): Sie bringen mehrere Netze mit,
     * und jedes haelt eigenen GPU-Speicher.
     */
    static baum(objekt) {
        if (!objekt) return;
        objekt.traverse(kind => {
            if (kind.isMesh) Netzentsorgung.netz(kind);
        });
    }

    /**
     * Ein Netz aus einer ABLAGE nehmen: aus der Szene, freigeben, streichen.
     *
     * WARUM (29.08.2026, Befund `doppelcode`): Diese vier Zeilen standen an
     * vier Stellen — zweimal fuer `state.clothMeshes`, zweimal fuer
     * `inst.clothMeshes`. Drei davon riefen `material.dispose()` direkt; bei
     * einem Netz mit MEHREREN Materialien ist `material` ein Array, und das
     * waere eine TypeError gewesen. Dieselbe latente Stelle wie in
     * `Charakter.dispose()` (28.08.2026).
     *
     * @returns true, wenn wirklich etwas da war — die Aufrufer haengen
     *          daran ihre eigenen Aufraeumschritte (`clothParams`, Liste
     *          auffrischen).
     */
    static ausAblage(elternteil, ablage, schluessel) {
        const netz = ablage?.[schluessel];
        if (!netz) return false;
        Netzentsorgung.entfernen(elternteil, netz);
        delete ablage[schluessel];
        return true;
    }

    /**
     * Aus der Szene nehmen UND freigeben — die haeufigste Reihenfolge.
     *
     * @param elternteil Objekt oder Szene, aus der entfernt wird
     * @param objekt das Netz oder die Gruppe
     */
    static entfernen(elternteil, objekt) {
        if (!objekt) return;
        if (elternteil) elternteil.remove(objekt);
        // `traverse` schliesst das Objekt SELBST ein — ein zusaetzlicher
        // Aufruf fuer den Fall „das Objekt ist ein Netz“ gaebe es zweimal frei.
        Netzentsorgung.baum(objekt);
    }
}

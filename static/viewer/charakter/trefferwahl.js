/**
 * Trefferwahl — welches Kleidungsstück ein Klick meint, wenn die Haut durch den Stoff sticht.
 *
 * BEFUND (Edgar, 24.09.2026: „Flats löschen (GarmentCode) löscht das ganze Modell
 * stattdessen"): Bei der GarmentCode-Ballerina ragen die Zehen der Figur durch den Stoff.
 * Traf der Klick eine Zehe, lag die Haut als ERSTER Treffer vorn. Gewählt war damit die
 * Figur, nicht der Schuh, und Entf löschte die Figur. Im Browser nachgemessen: Von
 * 76 Strahlen, die den Schuh treffen sollten, landeten 5 zuerst auf der Haut.
 *
 * Liegt hinter dem ersten Treffer binnen `DURCHSTICH_M` ein Kleidungsstück derselben
 * Figur, zählt dieses. Die Haut, die durch Stoff sticht, ist nie gemeint. Weiter
 * dahinter liegt ein Stück unter der Haut, auf der anderen Seite des Körpers, und
 * gewählt bleibt die Figur.
 *
 * Ohne Importe: `finden` (`_findSubMeshForObject`) reicht der Aufrufer herein. So läuft
 * die Klasse auch in Node (`test_js_trefferwahl`).
 */
export class Trefferwahl {

    /** Wie weit hinter der Haut ein Stoff noch als „darüber" gilt. Gemessen stachen die
     *  Zehen bis 11,6 mm durch. */
    static DURCHSTICH_M = 0.02;

    /**
     * `{treffer, ziel}`: der maßgebliche Treffer und sein Teilnetz (oder `null`).
     * `treffer`: Ergebnis von `intersectObjects`, nach Abstand sortiert;
     * `finden(objekt, ziele)`: das Teilnetz eines getroffenen Objekts oder `null`.
     */
    static waehlen(treffer, ziele, finden) {
        const erster = treffer[0];
        if (!erster) return { treffer: null, ziel: null };
        const ziel = finden(erster.object, ziele);
        if (ziel) return { treffer: erster, ziel };
        // Die Schwebeanzeige setzt `_parentCharId` nicht, dort gilt jedes Stück in Reichweite.
        const figur = erster.object.userData?._parentCharId;
        for (const weiter of treffer) {
            if (weiter.distance - erster.distance > Trefferwahl.DURCHSTICH_M) break;
            const stoff = finden(weiter.object, ziele);
            if (stoff && (!figur || stoff.charId === figur)) {
                return { treffer: weiter, ziel: stoff };
            }
        }
        return { treffer: erster, ziel: null };
    }
}

/**
 * Einzugbacken — den Hauteinzug in die Punkte rechnen, statt ihn wegzuwerfen.
 *
 * FUND 26.09.2026 (Edgar mit Nahaufnahme der Füße: „Schuhe noch Fehler" —
 * hautfarbene Flecken mitten auf den schwarzen Schuhen): Die Szene zieht die
 * verdeckten Hautpunkte unter Kleid und Schuh nach innen, damit kein Zipfel
 * Haut durch den Stoff sticht. Das passiert NICHT in der Geometrie, sondern
 * im Vertex-Shader: `transformed += einzug`, aus dem eigenen Attribut
 * `einzug` (`hauteinzug.js`).
 *
 * Der Export wirft eigene Attribute hinaus (`Netzattribute`, sonst bricht
 * Blenders glTF-Importer ab) — und ohne den Shader standen die Punkte damit
 * wieder auf der Hautoberfläche. Da die ganze verdeckte Haut jetzt
 * mitexportiert wird (`Vollindex`), liegt sie dort, wo Schuh und Kleid eng
 * anliegen, VOR dem Stoff: der Fuß stach durch den Schuh.
 *
 * Also wird der Einzug vor dem Löschen in `position` addiert — dieselbe
 * Rechnung wie im Shader, nur einmalig. Das muss VOR dem Skinning geschehen,
 * genau wie im Shader (`begin_vertex` läuft vor `skinning_vertex`).
 */
export class Einzugbacken {

    static ATTRIBUT = 'einzug';

    /**
     * @param geometrie MUTIERT — der Aufrufer hat eine Kopie.
     * @returns Anzahl der verschobenen Punkte (0, wenn es nichts zu tun gab)
     */
    static anwenden(geometrie) {
        const einzug = geometrie?.getAttribute?.(Einzugbacken.ATTRIBUT);
        const pos = geometrie?.getAttribute?.('position');
        if (!einzug || !pos || einzug.count !== pos.count || einzug.itemSize < 3) return 0;
        let bewegt = 0;
        for (let i = 0; i < pos.count; i++) {
            const dx = einzug.getX(i), dy = einzug.getY(i), dz = einzug.getZ(i);
            if (dx === 0 && dy === 0 && dz === 0) continue;
            pos.setXYZ(i, pos.getX(i) + dx, pos.getY(i) + dy, pos.getZ(i) + dz);
            bewegt++;
        }
        if (bewegt) {
            pos.needsUpdate = true;
            // Die Normalen zeigen danach nicht mehr ganz richtig; wer sie
            // braucht, rechnet sie ohnehin neu (`Netzpose.gebacken`).
        }
        return bewegt;
    }
}

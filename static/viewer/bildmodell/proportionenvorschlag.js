/**
 * Proportionenvorschlag — wo ein fehlendes Maß im Foto liegen dürfte.
 *
 * Edgar (20.09.2026): „Mach einen Button zum Hinzufügen aller Maße." Ein Maß, das
 * die Sichtung nicht ins Foto gelegt hat, bekommt seine Höhe aus der ZIEL-Ansicht
 * (das gerenderte Zielnetz derselben Ansicht kennt alle seine Linien in Pixeln):
 * Höhenabstand zum nächsten Maß, das im Foto schon liegt, mit dem Maßstab beider
 * Bilder umgerechnet; Mitte = Mitte dieses Nachbarn. Ohne Nachbarn: Bildmitte.
 * Ein Maß, das die Ziel-Ansicht nicht führt (Tiefen von vorn, Kopfmaße im
 * Körperbild), gehört nicht in dieses Bild — kein Vorschlag.
 */
export class Proportionenvorschlag {

    /**
     * @param k         Maß
     * @param quelle    `{art, ansicht, breite, hoehe, px_je_m}` des Fotos
     * @param zielReihe `daten().ansichten[ansicht]` — `{linien: {ziel}, px_je_m: {ziel}}`
     * @param lagen     Linien, die im Foto schon liegen (`{k: [[x, y], [x, y]]}`)
     * @returns `[cx, cy]` in Fotopixeln oder null
     */
    static lage(k, quelle, zielReihe, lagen) {
        const ziel = ((zielReihe || {}).linien || {}).ziel || {};
        const zk = ziel[k];
        if (!zk) return null;
        const pxZiel = ((zielReihe || {}).px_je_m || {}).ziel;
        const y = l => (l[0][1] + l[1][1]) / 2;
        const x = l => (l[0][0] + l[1][0]) / 2;
        let nachbar = null;
        for (const [j, lj] of Object.entries(lagen || {})) {
            if (!ziel[j] || j === k) continue;
            const abstand = Math.abs(y(ziel[j]) - y(zk));
            if (!nachbar || abstand < nachbar.abstand) nachbar = { j, lj, abstand };
        }
        if (!nachbar || !pxZiel || !quelle.px_je_m) return [quelle.breite / 2, quelle.hoehe / 2];
        const cy = y(nachbar.lj) + (y(zk) - y(ziel[nachbar.j])) * quelle.px_je_m / pxZiel;
        const cx = x(nachbar.lj);
        return [Math.round(cx * 10) / 10, Math.round(Math.min(Math.max(cy, 0), quelle.hoehe) * 10) / 10];
    }
}

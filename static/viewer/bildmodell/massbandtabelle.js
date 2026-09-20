import { dbTabelle } from '/static/djangobase/js/tabelle_bauen.js';

/**
 * Massbandtabelle — rund 40 Körpermaße SMPL-X (GVHMR) / Zielnetz / Modell (20.09.2026).
 *
 * Edgar: „Warum nutzt du nicht mehr Körpermaße?" — `ergebnis.massband`
 * (`Bildmodellmassband`, ein `G9massband` für beide Netze): Umfänge, Breiten,
 * Tiefen, Höhen und Längen in cm. SMPL-X ist der Median über die Bilder mit
 * Häkchen „Verwenden"; die Spalte Modell − SMPL-X zeigt, wo die Regler vom
 * Schätzer abweichen. djangoBase-Tabelle (`tabelle_bauen.js`), sortierbar —
 * nach der Abweichung sortiert steht das Schlimmste oben.
 */
export class Massbandtabelle {

    static GRUPPEN = { umfang: 'Umfang', breite: 'Breite', tiefe: 'Tiefe', hoehe: 'Höhe', laenge: 'Länge' };
    static KEY = 'bildmodell-massband';

    /** `data-sort` liest die djangoBase-Sortierung als DEUTSCHE Zahl (Punkt = Tausender): 8.8 wäre 88. */
    static sort(w) { return w.toFixed(2).replace('.', ','); }

    static zelle(q, k) {
        const w = q && q[k];
        return (w === undefined || w === null) ? { text: '–', sort: '' }
            : { text: `${w.toFixed(1)} cm`, sort: Massbandtabelle.sort(w), num: true };
    }

    static html(m) {
        if (!m || !m.katalog) return '';
        const spalten = [
            { label: 'Maß', key: 'mass' }, { label: 'Gruppe', key: 'gruppe' },
            { label: 'SMPL-X (GVHMR)', key: 'smplx', num: true, titel: 'Median über die verwendeten GVHMR-Ergebnisse, Ruhehaltung, auf die Körpergröße skaliert' },
            { label: 'Zielnetz', key: 'ziel', num: true }, { label: 'Modell (Genesis 9)', key: 'modell', num: true },
            { label: 'Modell − SMPL-X', key: 'diff', num: true, titel: 'Wo die Regler vom Schätzer abweichen' },
        ];
        const zeilen = m.katalog.map(e => {
            const k = e.schluessel;
            const s = m.smplx && m.smplx[k], d = m.modell && m.modell[k];
            const diff = (s != null && d != null) ? d - s : null;
            return { zellen: [
                { text: e.name }, { text: Massbandtabelle.GRUPPEN[e.gruppe] || e.gruppe },
                Massbandtabelle.zelle(m.smplx, k), Massbandtabelle.zelle(m.ziel, k), Massbandtabelle.zelle(m.modell, k),
                diff == null ? { text: '–', sort: '' }
                    : { text: `${diff > 0 ? '+' : ''}${diff.toFixed(1)} cm`, sort: Massbandtabelle.sort(Math.abs(diff)), num: true,
                        klasse: Math.abs(diff) > 3 ? 'bildmodell-massweit' : (Math.abs(diff) > 1.5 ? 'bildmodell-massmittel' : '') },
            ] };
        });
        const quelle = m.smplx ? `SMPL-X aus ${m.smplx.bilder} Bild(ern) mit Häkchen „Verwenden"` : 'kein GVHMR-Ergebnis mit Häkchen „Verwenden"';
        const hoehe = m.hoehe_cm ? `, auf ${m.hoehe_cm} cm skaliert` : ', ohne Größenangabe (SMPL-X in eigener Größe)';
        return `<div class="bildmodell-zahl"><b>Körpermaße</b><span>${m.katalog.length} Maße mit einem Maßband an beiden Netzen — ${quelle}${hoehe}</span></div>`
            + dbTabelle({ key: Massbandtabelle.KEY, spalten, zeilen, klasse: 'bildmodell-massband', rahmen: false });
    }
}

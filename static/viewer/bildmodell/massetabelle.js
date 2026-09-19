/**
 * Massetabelle — Außenmaße Foto / Zielnetz / Modell nebeneinander (19.09.2026).
 *
 * Edgar: „was gänzlich fehlt in dem Tool sind die Außenproportionen des
 * Modells, z.B. Hüftbreite …" — `ergebnis.masse` (Bildmodellmasse): vier
 * Breiten mit derselben Messfunktion an der Personenmaske der Fotos, am
 * SMPL-X-Zielnetz und am Genesis-Käfig. Die Differenz Modell − Foto steht
 * daneben; so sieht man, ob der Schätzer oder die Regler abweichen.
 */
export class Massetabelle {

    static NAMEN = { schulter: 'Schulterbreite', brust: 'Brustbreite', taille: 'Taillenbreite', huefte: 'Hüftbreite' };

    static html(masse) {
        if (!masse || !masse.masse) return '';
        const spalten = [['foto', 'Foto'], ['zielnetz', 'Zielnetz (SMPL-X)'], ['modell', 'Modell (Genesis 9)']];
        const kopf = spalten.map(([, n]) => `<th>${n}</th>`).join('');
        const zeilen = masse.masse.map(k => {
            const werte = spalten.map(([s]) => {
                const q = masse[s];
                if (!q || q[k] === undefined || q[k] === null) {
                    return s === 'foto' && q && q.arme_anliegend ? '<td>– <span class="hb-hinweis">Arme anliegend</span></td>' : '<td>–</td>';
                }
                const cm = q[k + '_cm'] !== undefined ? `${q[k + '_cm'].toFixed(1)} cm` : '';
                return `<td>${cm || ''}<span class="hb-hinweis"> ${(q[k] * 100).toFixed(1)} % der Höhe</span></td>`;
            }).join('');
            const f = masse.foto && masse.foto[k], m = masse.modell && masse.modell[k];
            const diff = (f !== undefined && m !== undefined && masse.foto[k + '_cm'] !== undefined && masse.modell[k + '_cm'] !== undefined)
                ? `${(masse.modell[k + '_cm'] - masse.foto[k + '_cm']).toFixed(1)} cm` : '–';
            return `<tr><th>${Massetabelle.NAMEN[k] || k}</th>${werte}<td>${diff}</td></tr>`;
        }).join('');
        const quelle = masse.foto
            ? `aus ${masse.foto.bilder} frontalen Hauptbild(ern)${masse.foto.arme_anliegend ? `, davon ${masse.foto.arme_anliegend} mit anliegenden Armen (Rumpf mit Arm ist kein Maß)` : ''}`
            : 'kein Foto mit Maske und Rig';
        return `<div class="bildmodell-zahl"><b>Außenmaße</b><span>Breite des Rumpfsegments auf Schulter-, Brust-, Taillen- und Hüfthöhe (Rig), ${quelle}</span></div>`
            + `<table class="bildmodell-masse doku"><thead><tr><th></th>${kopf}<th>Modell − Foto</th></tr></thead><tbody>${zeilen}</tbody></table>`;
    }
}

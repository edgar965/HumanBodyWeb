/**
 * Gesichtsformguete — die Zahlen der letzten Rechnung (Seite „Gesichtsform", `G9schnittvorgaben.guete`).
 *
 * Je Schnitt die größte Abweichung |Ziel − Figur| vorher und nachher und das 90-%-Quantil nachher, je
 * Kontur der mittlere Abstand von vorn — in Millimetern, gemessen auf der Ansichtsstufe mit Augäpfeln.
 * Das Maximum sitzt oft am Ovalrand, wo die Fläche steil wird; das p90 sagt, wie der Schnitt sonst liegt.
 */
export class Gesichtsformguete {

    static NAMEN = {
        auge_rechts: 'Auge rechts', auge_links: 'Auge links', braue_rechts: 'Braue rechts',
        braue_links: 'Braue links', lippen: 'Lippen außen', mund: 'Lippen innen', nase: 'Nase', oval: 'Oval',
    };

    constructor(behaelter) { this.behaelter = behaelter; }

    zeigen(guete, max) {
        if (!guete) { this.behaelter.textContent = 'Noch nicht gerechnet.'; return; }
        const z = v => (v === null || v === undefined ? '–' : String(v).replace('.', ','));
        const klasse = (vor, nach) => {
            if (vor === null || nach === null || vor === undefined || nach === undefined) return '';
            return nach < vor ? 'besser' : nach > vor ? 'schlechter' : '';
        };
        let html = `<p>Größte Verschiebung des Morphs: ${z(max)} mm</p><table><tr><th>Schnitt</th>`
            + '<th>max. vorher</th><th>max. nachher</th><th>p90 nachher</th></tr>';
        for (const s of guete.schnitte || []) {
            html += `<tr><td>${s.art} ${z(s.lage)} mm</td><td>${z(s.vorher_max)}</td>`
                + `<td class="${klasse(s.vorher_max, s.nachher_max)}">${z(s.nachher_max)}</td>`
                + `<td>${z(s.nachher_p90)}</td></tr>`;
        }
        html += '<tr><th>Kontur</th><th>vorher</th><th>nachher</th><th></th></tr>';
        for (const [name, k] of Object.entries(guete.konturen || {})) {
            html += `<tr><td>${Gesichtsformguete.NAMEN[name] || name}</td><td>${z(k.vorher_mm)}</td>`
                + `<td class="${klasse(k.vorher_mm, k.nachher_mm)}">${z(k.nachher_mm)}</td><td></td></tr>`;
        }
        this.behaelter.innerHTML = `${html}</table>`;
        this.behaelter.classList.add('gf-guete');
    }
}

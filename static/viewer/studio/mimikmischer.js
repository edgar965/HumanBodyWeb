import { Mimikbasis } from './mimikbasis.js';

/**
 * Mimikmischer — die Gruppe „Eigene" im Pose-Dialog: ein Regler je
 * MB-Lab-Einheit (−100…+100 %), nach Bereichen gebündelt, dazu Name und
 * „Als Pose speichern". Beim Ziehen zeigt die Figur die Mischung sofort
 * (`beiAenderung`); gespeicherte Posen landen im Browserspeicher
 * (`Mimikbasis.eigeneSpeichern`) und erscheinen als Kacheln der Gruppe.
 */
export class Mimikmischer {

    /** Bereich → Muster im Einheitennamen; die Reihenfolge ist die Anzeige. */
    static BEREICHE = [
        ['Brauen', /brow/i], ['Augen', /eye|pupil/i], ['Nase', /nostril|nose/i],
        ['Wangen', /cheek/i], ['Mund', /mouth|deglut/i], ['Kiefer', /jaw/i],
        ['Zunge', /tongue/i],
    ];

    static zeigen(behaelter, vorlage, beiAuswahl) {
        const einheiten = Object.keys(Mimikbasis.basis || {}).sort();
        const gewichte = { ...(vorlage?.gewichte || {}) };
        behaelter.innerHTML = Mimikmischer._html(einheiten, gewichte, vorlage?.name);
        const lesen = () => {
            const aus = {};
            behaelter.querySelectorAll('input[data-einheit]').forEach(r => {
                const g = Number(r.value) / 100;
                if (g) aus[r.dataset.einheit] = g;
            });
            return aus;
        };
        behaelter.querySelectorAll('input[data-einheit]').forEach(r => {
            r.oninput = () => {
                r.nextElementSibling.textContent = r.value;
                beiAuswahl({ id: 'mischung', name: 'Mischung', gruppe: 'eigene', gewichte: lesen() });
            };
        });
        behaelter.querySelector('[data-rolle="zuruecksetzen"]').onclick = () => {
            behaelter.querySelectorAll('input[data-einheit]').forEach(r => {
                r.value = 0; r.nextElementSibling.textContent = '0';
            });
            beiAuswahl({ id: 'mischung', name: 'Mischung', gruppe: 'eigene', gewichte: {} });
        };
        behaelter.querySelector('[data-rolle="speichern"]').onclick = () => {
            const name = behaelter.querySelector('#mimik-eigene-name').value.trim();
            if (!name) return;
            const pose = Mimikbasis.eigeneSpeichern(name, lesen());
            beiAuswahl(pose, true);
        };
    }

    static _html(einheiten, gewichte, name) {
        const zeilen = [];
        const uebrig = new Set(einheiten);
        for (const [titel, muster] of Mimikmischer.BEREICHE) {
            const passend = einheiten.filter(e => muster.test(e) && uebrig.has(e));
            if (!passend.length) continue;
            passend.forEach(e => uebrig.delete(e));
            zeilen.push(`<h3 class="gruppentitel">${titel}</h3>`
                + passend.map(e => Mimikmischer._regler(e, gewichte[e] || 0)).join(''));
        }
        if (uebrig.size) {
            zeilen.push('<h3 class="gruppentitel">Weitere</h3>'
                + [...uebrig].map(e => Mimikmischer._regler(e, gewichte[e] || 0)).join(''));
        }
        return `<div class="prop-row"><label>Name:</label>
                <input type="text" id="mimik-eigene-name" class="dehnen"
                    value="${name && name !== 'Mischung' ? name : ''}"
                    placeholder="Name der eigenen Pose"></div>
            <div class="prop-row mimik-mischer-knoepfe">
                <button data-rolle="speichern" class="knopf-akzent">
                    <i class="fas fa-save"></i> Als Pose speichern</button>
                <button data-rolle="zuruecksetzen">Alles auf 0</button></div>
            ${zeilen.join('')}`;
    }

    static _regler(einheit, g) {
        const wert = Math.round(g * 100);
        return `<div class="prop-row"><label>${einheit}:</label>
            <input type="range" data-einheit="${einheit}" min="-100" max="100" step="5" value="${wert}">
            <span class="reglerwert">${wert}</span></div>`;
    }
}

/**
 * Vergleichspanel — die Bedienspalte neben einer Vergleichsansicht aufbauen.
 *
 * Aus viewer_compare.js herausgeloest (Umbau 16.08.2026).
 */
import { Vergleichsregler } from './vergleichsregler.js';

/** Grundregler: [Name, Kleinstwert, Groesstwert, Vorgabe]. */
export const GRUNDREGLER = [
    ['age', 18, 100, 59],
    ['mass', 45, 200, 123],
    ['tone', 0, 100, 50],
    ['height', 150, 200, 175],
];

export class Vergleichspanel {
    static bauen(ansicht) {
        const panel = document.getElementById(ansicht.panelId);
        if (!panel) return;
        panel.innerHTML = '';
        panel.appendChild(Vergleichspanel._kopf(ansicht));
        panel.appendChild(Vergleichspanel._koerperabschnitt(ansicht));
        panel.appendChild(Vergleichspanel._morphabschnitt(ansicht));
        panel.appendChild(Vergleichspanel._statusleiste(ansicht));
    }

    static _kopf(ansicht) {
        const kasten = document.createElement('div');
        kasten.className = 'panel-section';
        kasten.style.cssText = 'padding:10px 16px;background:var(--bg-card);'
                             + 'border-bottom:2px solid var(--accent);';
        kasten.innerHTML = '<h3 style="margin:0;font-size:0.9rem;'
            + `color:var(--accent);cursor:default;">${ansicht.label}</h3>`;
        return kasten;
    }

    static _koerperabschnitt(ansicht) {
        const abschnitt = document.createElement('div');
        abschnitt.className = 'panel-section';
        abschnitt.innerHTML = '<h3>Body Type <span class="chevron">&#9660;</span></h3>';
        abschnitt.querySelector('h3').addEventListener(
            'click', () => abschnitt.classList.toggle('collapsed'));

        const rumpf = document.createElement('div');
        rumpf.className = 'panel-body';

        ansicht.felder.koerperart = document.createElement('select');
        ansicht.felder.koerperart.className = 'viewer-select';
        rumpf.appendChild(ansicht.felder.koerperart);

        for (const [name, min, max, vorgabe] of GRUNDREGLER) {
            const zeile = Vergleichspanel.reglerzeile(
                name.charAt(0).toUpperCase() + name.slice(1), min, max, vorgabe, 1);
            ansicht.felder.grundregler[name] = { slider: zeile.slider, val: zeile.val };
            rumpf.appendChild(zeile.row);
        }
        rumpf.appendChild(Vergleichspanel._hautregler(ansicht));
        abschnitt.appendChild(rumpf);
        return abschnitt;
    }

    static _hautregler(ansicht) {
        const kasten = document.createElement('div');
        kasten.style.cssText = 'margin-top:8px;border-top:1px solid var(--border);'
                             + 'padding-top:8px;';
        const farbzeile = document.createElement('div');
        farbzeile.className = 'slider-row';
        farbzeile.innerHTML = '<label>Skin</label>';
        const farbe = document.createElement('input');
        farbe.type = 'color';
        farbe.value = '#d4a574';
        farbe.style.cssText = 'width:40px;height:24px;border:none;cursor:pointer;';
        farbzeile.appendChild(farbe);
        kasten.appendChild(farbzeile);
        ansicht.felder.hautfarbe = farbe;

        const rauheit = Vergleichspanel.reglerzeile('Roughness', 0, 100, 55, 1);
        ansicht.felder.rauheit = rauheit.slider;
        ansicht.felder.rauheitWert = rauheit.val;
        rauheit.val.textContent = '0.55';
        kasten.appendChild(rauheit.row);

        const metall = Vergleichspanel.reglerzeile('Metalness', 0, 100, 0, 1);
        ansicht.felder.metall = metall.slider;
        ansicht.felder.metallWert = metall.val;
        metall.val.textContent = '0.00';
        kasten.appendChild(metall.row);
        return kasten;
    }

    static _morphabschnitt(ansicht) {
        const abschnitt = document.createElement('div');
        abschnitt.className = 'panel-section';

        const zuruecksetzen = document.createElement('button');
        zuruecksetzen.className = 'btn-reset';
        zuruecksetzen.textContent = 'Reset';
        zuruecksetzen.addEventListener(
            'click', () => Vergleichsregler.zuruecksetzen(ansicht));

        const kopf = document.createElement('h3');
        kopf.textContent = 'Morphs ';
        kopf.appendChild(zuruecksetzen);
        const pfeil = document.createElement('span');
        pfeil.className = 'chevron';
        pfeil.innerHTML = '&#9660;';
        kopf.appendChild(pfeil);
        kopf.addEventListener('click', (e) => {
            if (e.target === zuruecksetzen) return;   // Knopf klappt nicht zu
            abschnitt.classList.toggle('collapsed');
        });
        abschnitt.appendChild(kopf);

        ansicht.felder.morphliste = document.createElement('div');
        ansicht.felder.morphliste.className = 'panel-body';
        abschnitt.appendChild(ansicht.felder.morphliste);
        return abschnitt;
    }

    static _statusleiste(ansicht) {
        const leiste = document.createElement('div');
        leiste.className = 'status-bar';
        const f = ansicht.felder;
        f.status = document.createElement('span');
        f.status.className = 'disconnected';
        f.status.textContent = 'Disconnected';
        f.vertexzahl = document.createElement('span');
        f.vertexzahl.textContent = '—';
        f.bildrate = document.createElement('span');
        f.bildrate.textContent = '—';
        leiste.innerHTML = 'WS: ';
        leiste.appendChild(f.status);
        leiste.append(' | ');
        leiste.appendChild(f.vertexzahl);
        leiste.append(' verts | ');
        leiste.appendChild(f.bildrate);
        leiste.append(' fps');
        return leiste;
    }

    /** Eine Zeile mit Beschriftung, Schieber und Wertanzeige. */
    static reglerzeile(beschriftung, min, max, wert, schritt) {
        const row = document.createElement('div');
        row.className = 'slider-row';
        const lbl = document.createElement('label');
        lbl.textContent = beschriftung;
        const slider = document.createElement('input');
        slider.type = 'range';
        slider.min = min;
        slider.max = max;
        slider.value = wert;
        slider.step = schritt;
        const val = document.createElement('span');
        val.className = 'slider-val';
        val.textContent = wert;
        row.append(lbl, slider, val);
        return { row, slider, val };
    }
}

import { Panel } from './panel.js';

/**
 * Kleiderpanel — Material, Position und Groesse eines Kleidungsstuecks.
 *
 * Aus main.js herausgeloest (Umbau 16.08.2026): 184 Zeilen HTML-Vorlage plus
 * Verdrahtung.
 *
 * DABEI EIN BEFUND: Von zwanzig Schiebern wirkten nur drei (Farbe, Rauheit,
 * Metallgrad). Die uebrigen siebzehn schrieben ihren Wert in die Anzeige daneben
 * und sonst nirgendwohin — im Quelltext stand dazu
 *
 *     // Note: Offset/Stiffness/Position/Scale/Region sliders update display only
 *     // Full implementation would need vertex buffer manipulation like Dashboard
 *
 * Ein Bedienelement, das sich bewegt und nichts tut, ist schlimmer als keines:
 * Man haelt das Ergebnis fuer eingestellt. Deshalb jetzt:
 *
 *  * Position und Groesse (sechs Schieber) wirken WIRKLICH — dafuer braucht es
 *    keine Vertexrechnung, nur `position` und `scale` am Netz.
 *  * Die elf, die eine Neuanpassung am Server braeuchten (Abstand, Steifigkeit,
 *    Schrittmasse, Regionen), stehen zusammen in einem zugeklappten Bereich mit
 *    der Aufschrift, dass sie noch nicht angebunden sind. Nichts entfernt,
 *    nichts vorgetaeuscht.
 */
export class Kleiderpanel {

    /** Schieber, die nur anzeigen — mit Beschriftung und Einheit. */
    static NOCH_OHNE_WIRKUNG = [
        ['garment-min-dist', 'Min. Abstand', -0, 15, 3, v => v + ' mm'],
        ['garment-crotch-floor', 'Schritt-Boden', -40, 40, 0, v => v + ' mm'],
        ['garment-lift', 'Anheben', -20, 40, 0, v => v + ' mm'],
        ['garment-crotch-depth', 'Schritt-Tiefe', 0, 40, 0, v => v + ' mm'],
        ['garment-region-top', 'Region Top', -30, 30, 0, v => (v / 100).toFixed(2) + ' m'],
        ['garment-region-upper', 'Region Upper', -30, 30, 0, v => (v / 100).toFixed(2) + ' m'],
        ['garment-region-mid', 'Region Mid', -30, 30, 0, v => (v / 100).toFixed(2) + ' m'],
        ['garment-region-lower', 'Region Lower', -30, 30, 0, v => (v / 100).toFixed(2) + ' m'],
        ['garment-region-bottom', 'Region Bottom', -30, 30, 0, v => (v / 100).toFixed(2) + ' m'],
    ];

    zeigen(netz) {
        const ziel = Panel.oeffnen();
        if (!ziel) return;
        const stoff = netz.material;
        const name = netz.userData.garmentId || netz.name || 'Kleidungsstück';
        const rauheit = stoff.roughness ?? 0.8;
        const metall = stoff.metalness ?? 0;
        const abstand = netz.userData.offset || 0.006;
        const steife = netz.userData.stiffness || 0.8;

        ziel.innerHTML = `<div class="pnl-inhalt pnl-rollbar">
            ${Panel.kopf('fa-tshirt', name)}

            ${this._abschnitt('Farbe / Material')}
            <div class="slider-row"><label>Color</label>
                <input type="color" id="garment-color" class="pnl-farbe-klein"
                       value="#${stoff.color.getHexString()}"></div>
            ${this._reihe('garment-roughness', 'Roughness', 0, 100,
                          Math.round(rauheit * 100), rauheit.toFixed(2))}
            ${this._reihe('garment-metalness', 'Metalness', 0, 100,
                          Math.round(metall * 100), metall.toFixed(2))}

            ${this._abschnitt('Position (Meter)')}
            ${this._achsen('garment-pos', netz.position, 100, -50, 50)}

            ${this._abschnitt('Größe')}
            ${this._achsen('garment-scale', netz.scale, 100, 50, 200)}

            <details class="pnl-ausbau">
                <summary>Anpassung — noch nicht angebunden (${
                    Kleiderpanel.NOCH_OHNE_WIRKUNG.length + 2} Regler)</summary>
                <div class="pnl-hinweis">Diese Regler zeigen ihren Wert an, ändern
                    das Kleidungsstück aber noch nicht: Dafür muss der Server das
                    Netz neu anpassen (<code>/api/character/garment/fit/</code>).</div>
                ${this._reihe('garment-offset', 'Offset', 0, 30,
                              Math.round(abstand * 1000), abstand.toFixed(3))}
                ${this._reihe('garment-stiffness', 'Stiffness', 0, 100,
                              Math.round(steife * 100), steife.toFixed(2))}
                ${Kleiderpanel.NOCH_OHNE_WIRKUNG.map(
                    ([id, titel, min, max, wert, form]) =>
                        this._reihe(id, titel, min, max, wert, form(wert))).join('')}
            </details>
        </div>`;

        this._material(stoff);
        this._lage(netz);
        this._nurAnzeige();
    }

    // --------------------------------------------------------------- Bausteine

    _abschnitt(titel) {
        return `<div class="pnl-abschnitt">${titel}</div>`;
    }

    _reihe(id, titel, min, max, wert, anzeige) {
        return `<div class="slider-row"><label>${titel}</label>
            <input type="range" id="${id}" min="${min}" max="${max}"
                   value="${wert}" step="1">
            <span class="slider-val" id="${id}-val">${anzeige}</span></div>`;
    }

    /** Drei Schieber fuer x/y/z eines Vektors, Werte in Hundertsteln. */
    _achsen(praefix, vektor, faktor, min, max) {
        return ['x', 'y', 'z'].map(achse => {
            const wert = Math.round(vektor[achse] * faktor);
            const anzeige = praefix.endsWith('scale')
                ? (wert / faktor).toFixed(2) : (wert / faktor).toFixed(2) + ' m';
            return this._reihe(`${praefix}-${achse}`, achse.toUpperCase(),
                               min, max, wert, anzeige);
        }).join('');
    }

    // -------------------------------------------------------------- Verdrahtung

    _material(stoff) {
        const farbe = document.getElementById('garment-color');
        if (farbe) {
            farbe.oninput = () => {
                stoff.color.setHex(parseInt(farbe.value.substring(1), 16));
            };
        }
        this._schieber('garment-roughness', v => (v / 100).toFixed(2),
                       v => { stoff.roughness = v / 100; });
        this._schieber('garment-metalness', v => (v / 100).toFixed(2),
                       v => { stoff.metalness = v / 100; });
    }

    /**
     * Position und Groesse wirken direkt auf das Netz. Genau das fehlte vorher:
     * Die sechs Schieber schrieben nur ihre Zahl in die Anzeige.
     */
    _lage(netz) {
        for (const achse of ['x', 'y', 'z']) {
            this._schieber(`garment-pos-${achse}`,
                           v => (v / 100).toFixed(2) + ' m',
                           v => { netz.position[achse] = v / 100; });
            this._schieber(`garment-scale-${achse}`,
                           v => (v / 100).toFixed(2),
                           v => { netz.scale[achse] = v / 100; });
        }
    }

    _nurAnzeige() {
        this._schieber('garment-offset', v => (v / 1000).toFixed(3));
        this._schieber('garment-stiffness', v => (v / 100).toFixed(2));
        for (const [id, , , , , form] of Kleiderpanel.NOCH_OHNE_WIRKUNG) {
            this._schieber(id, form);
        }
    }

    /**
     * Einen Schieber verdrahten: Anzeige immer, Wirkung optional.
     * Ersetzt das `_bindSlider` aus main.js, das 14-mal aufgerufen wurde und
     * ausschliesslich die Anzeige aktualisierte.
     */
    _schieber(id, anzeigen, wirken = null) {
        const schieber = document.getElementById(id);
        const anzeige = document.getElementById(id + '-val');
        if (!schieber) return;
        schieber.oninput = () => {
            const wert = parseFloat(schieber.value);
            if (anzeige) anzeige.textContent = anzeigen ? anzeigen(wert) : schieber.value;
            if (wirken) wirken(wert);
        };
    }
}

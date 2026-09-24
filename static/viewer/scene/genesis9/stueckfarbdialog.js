import { escapeHtml } from '../utils.js';
import { Genesis9kleidung } from '../../gemeinsam/genesis9kleidung.js';
import { Umfaerbung } from '../../gemeinsam/umfaerbung.js';
import { Dazkleidung } from './dazkleidung.js';
import { Stueckfarbe } from './stueckfarbe.js';

/**
 * Stueckfarbdialog — die Farbwahl für ein Daz-Stück als Dialog.
 *
 * WARUM (Edgar, 24.09.2026, mit Bild: „Farben nicht auswählbar, mach eine
 * Farbauswahldialog"): Das Farbfeld in der Zeile des Assets-Reiters stand
 * rechts außerhalb der Zeile, abgeschnitten hinter der Variantenauswahl. Jetzt
 * trägt die Zeile nur einen Farbknopf; der Dialog hat Platz für:
 *
 * - das ZIEL: ganzes Stück oder eine Materialgruppe (nur getragen — die
 *   Gruppen gibt es erst am Netz), jedes mit seiner aktuellen Farbe;
 * - eine PALETTE (Haartöne und gängige Stofffarben), ein Klick färbt sofort;
 * - eine EIGENE Farbe (Farbwähler des Systems und Hexfeld);
 * - „Farbe aus Daz" (die eigene Farbe des Ziels entfernen).
 *
 * Der Hintergrund bleibt frei (kein Abdunkeln, `stueckfarbdialog.css`), damit
 * man die Figur beim Wählen sieht. Esc, „Fertig" und „×" schließen.
 */
export class Stueckfarbdialog {

    static PALETTE = [
        ['#0e0b0a', 'Schwarz'], ['#2b1a12', 'Dunkelbraun'], ['#4a2c1c', 'Braun'],
        ['#6b3a22', 'Kastanie'], ['#7a2a1a', 'Auburn'], ['#a0461e', 'Kupfer'],
        ['#c46a2c', 'Ingwer'], ['#c89a5a', 'Rotblond'], ['#d8b878', 'Blond'],
        ['#ece0c0', 'Platin'], ['#9a9a9a', 'Grau'], ['#f2f2f2', 'Weiß'],
        ['#c0182a', 'Rot'], ['#8a1030', 'Weinrot'], ['#e8508a', 'Pink'],
        ['#c02090', 'Magenta'], ['#6a2a9a', 'Lila'], ['#a080e0', 'Flieder'],
        ['#1a2a6a', 'Marine'], ['#2060e0', 'Blau'], ['#60b0f0', 'Himmelblau'],
        ['#10908a', 'Petrol'], ['#20a040', 'Grün'], ['#556b2f', 'Oliv'],
        ['#f0d020', 'Gelb'], ['#f08020', 'Orange'], ['#e8d8b8', 'Beige'],
        ['#b08a60', 'Sand'], ['#c3b091', 'Khaki'], ['#303438', 'Anthrazit'],
    ];

    static _offen = null;

    /**
     * @param o.inst     die Figur
     * @param o.kennung  das Daz-Stück
     * @param o.gruppe   vorgewähltes Ziel ('' = ganzes Stück)
     * @param o.ganz     `hex => …` für das ganze Stück, solange es NICHT getragen ist
     * @param o.wert     die gemerkte Farbe des ganzen Stücks (nicht getragen)
     */
    static async oeffnen({ inst, kennung, gruppe = '', ganz = null, wert = '' }) {
        Stueckfarbdialog.schliessen();
        const name = await Genesis9kleidung.anzeigename(kennung).catch(() => kennung);
        const zustand = { inst, kennung, ziel: gruppe, ganz, wert };
        const huelle = document.createElement('div');
        huelle.className = 'scene-modal-overlay visible stueckfarb-huelle';
        huelle.innerHTML = `
            <div class="scene-modal stueckfarb-dialog" role="dialog" aria-label="Farbe wählen">
                <div class="scene-modal-header">
                    <h4>Farbe · ${escapeHtml(name)}</h4>
                    <button type="button" class="scene-modal-close" title="Schließen">×</button>
                </div>
                <div class="scene-modal-body">
                    <div class="stueckfarb-titel">Ziel</div>
                    <div class="stueckfarb-ziele"></div>
                    <div class="stueckfarb-titel">Palette</div>
                    <div class="stueckfarb-palette"></div>
                    <div class="stueckfarb-titel">Eigene Farbe</div>
                    <div class="stueckfarb-eigen">
                        <input type="color" class="hb-farbfeld" title="Farbwähler öffnen">
                        <input type="text" class="stueckfarb-hex" maxlength="7" spellcheck="false" placeholder="#rrggbb">
                        <button type="button" class="btn-toggle stueckfarb-daz">Farbe aus Daz</button>
                    </div>
                </div>
                <div class="scene-modal-footer">
                    <button type="button" class="primary stueckfarb-fertig">Fertig</button>
                </div>
            </div>`;
        document.body.appendChild(huelle);
        Stueckfarbdialog._offen = { huelle, zustand, taste: null };
        Stueckfarbdialog._palette(huelle, zustand);
        Stueckfarbdialog._eigen(huelle, zustand);
        Stueckfarbdialog._zeichnen(huelle, zustand);
        const zu = () => Stueckfarbdialog.schliessen();
        huelle.querySelector('.scene-modal-close').addEventListener('click', zu);
        huelle.querySelector('.stueckfarb-fertig').addEventListener('click', zu);
        const taste = (e) => { if (e.key === 'Escape') zu(); };
        document.addEventListener('keydown', taste);
        Stueckfarbdialog._offen.taste = taste;
        return huelle;
    }

    static schliessen() {
        const offen = Stueckfarbdialog._offen;
        if (!offen) return;
        document.removeEventListener('keydown', offen.taste);
        offen.huelle.remove();
        Stueckfarbdialog._offen = null;
    }

    /** Getragen? Nur dann gibt es Gruppen und wirkt die Farbe sofort. */
    static _getragen(z) {
        return Boolean(Dazkleidung.kleidung(z.inst)[z.kennung]);
    }

    /** Die Ziele: '' (ganzes Stück), dann die Materialgruppen aller Teilnetze. */
    static ziele(z) {
        const aus = [''];
        if (!Stueckfarbdialog._getragen(z)) return aus;
        for (const { netz } of Umfaerbung.netze(z.inst, z.kennung)) {
            for (const { material } of Umfaerbung.materialien(netz)) {
                const g = material.userData?.gruppe;
                if (g && !aus.includes(g)) aus.push(g);
            }
        }
        return aus;
    }

    /** Die aktuelle Farbe eines Ziels ('' = aus Daz). */
    static farbe(z, ziel) {
        if (!Stueckfarbdialog._getragen(z)) return ziel ? '' : (z.wert || '');
        const werte = Dazkleidung.kleidung(z.inst)[z.kennung] || {};
        return ziel ? (werte.gruppenfarben?.[ziel] || '') : (werte.farbe || '');
    }

    static setzen(z, hex) {
        if (!z.ziel) {
            z.wert = hex;
            if (Stueckfarbdialog._getragen(z)) Stueckfarbe.ganz(z.inst, z.kennung, hex);
            z.ganz?.(hex);
        } else {
            Stueckfarbe.gruppe(z.inst, z.kennung, z.ziel, hex);
        }
        const offen = Stueckfarbdialog._offen;
        if (offen?.zustand === z) Stueckfarbdialog._zeichnen(offen.huelle, z);
    }

    static _palette(huelle, z) {
        const feld = huelle.querySelector('.stueckfarb-palette');
        for (const [hex, name] of Stueckfarbdialog.PALETTE) {
            const k = document.createElement('button');
            k.type = 'button';
            k.className = 'stueckfarb-kachel';
            k.style.background = hex;
            k.title = `${name} ${hex}`;
            k.dataset.farbe = hex;
            k.addEventListener('click', () => Stueckfarbdialog.setzen(z, hex));
            feld.appendChild(k);
        }
    }

    static _eigen(huelle, z) {
        const waehler = huelle.querySelector('.stueckfarb-eigen input[type=color]');
        const hexfeld = huelle.querySelector('.stueckfarb-hex');
        waehler.addEventListener('input', () => Stueckfarbdialog.setzen(z, waehler.value));
        hexfeld.addEventListener('change', () => {
            const hex = Stueckfarbdialog.hexNormal(hexfeld.value);
            if (hex) Stueckfarbdialog.setzen(z, hex);
            else hexfeld.value = Stueckfarbdialog.farbe(z, z.ziel);
        });
        huelle.querySelector('.stueckfarb-daz').addEventListener('click', () => Stueckfarbdialog.setzen(z, ''));
    }

    /** `f80`, `#F80`, `ff8800` → `#ff8800`; sonst ''. */
    static hexNormal(text) {
        let t = String(text || '').trim().replace(/^#/, '').toLowerCase();
        if (/^[0-9a-f]{3}$/.test(t)) t = t.split('').map(c => c + c).join('');
        return /^[0-9a-f]{6}$/.test(t) ? `#${t}` : '';
    }

    /** Ziele, Markierung der Palette und die Felder auf den Stand. */
    static _zeichnen(huelle, z) {
        const ziele = huelle.querySelector('.stueckfarb-ziele');
        ziele.innerHTML = '';
        for (const ziel of Stueckfarbdialog.ziele(z)) {
            const hex = Stueckfarbdialog.farbe(z, ziel);
            const k = document.createElement('button');
            k.type = 'button';
            k.className = `stueckfarb-ziel${ziel === z.ziel ? ' gewaehlt' : ''}`;
            k.innerHTML = `<span class="stueckfarb-punkt${hex ? '' : ' leer'}"`
                + `${hex ? ` style="background:${hex}"` : ''}></span>${escapeHtml(ziel || 'Ganzes Stück')}`;
            k.addEventListener('click', () => { z.ziel = ziel; Stueckfarbdialog._zeichnen(huelle, z); });
            ziele.appendChild(k);
        }
        const aktuell = Stueckfarbdialog.farbe(z, z.ziel);
        for (const k of huelle.querySelectorAll('.stueckfarb-kachel')) {
            k.classList.toggle('gewaehlt', k.dataset.farbe === aktuell);
        }
        huelle.querySelector('.stueckfarb-eigen input[type=color]').value = aktuell || Stueckfarbe.LEER;
        const hexfeld = huelle.querySelector('.stueckfarb-hex');
        if (document.activeElement !== hexfeld) hexfeld.value = aktuell;
        huelle.querySelector('.stueckfarb-daz').disabled = !aktuell;
    }
}

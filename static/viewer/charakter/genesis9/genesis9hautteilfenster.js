import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { Genesis9hautebenen } from '../../gemeinsam/genesis9hautebenen.js';
import { Genesis9hautteile } from '../../gemeinsam/genesis9hautteile.js';
import { Genesis9hautteilmerkmale } from '../../gemeinsam/genesis9hautteilmerkmale.js';

/**
 * Genesis9hautteilfenster — das Fenster „Hautfarbe …“ bzw. „Tattoo …“ eines Körperteils im Abschnitt „Eigen“ (25.10.2026, Edgar: „bei den Reglern für die einzelnen Körperteile
 * mach jeweils auch Regler für die Textur“). Gleiche Hülle wie `Genesis9umrissfenster` (Hintergrund frei, die Figur bleibt sichtbar).
 *
 *   Hautfarbe  Zielfarbe (Vorgabe: die mittlere Hautfarbe der Figur) und Stärke
 *   Tattoo     Deckung, Fläche, Größe (mm), Stil (Ranken/Flächen), Tinte, Muster (Zahl, „Neu würfeln“)
 * Jede Änderung wirkt sofort (nur Uniforms, `Genesis9hautteile` → `Genesis9hautebenen.anwenden`); „Zurücksetzen“ löscht alle Werte dieses Reglers.
 */
export class Genesis9hautteilfenster {

    static _offen = null;

    static FELDER = {
        farbe: [
            { feld: '', titel: 'Stärke', typ: 'bereich', min: 0, max: 100, einheit: '%' },
            { feld: 'farbe', titel: 'Zielfarbe', typ: 'farbe' },
        ],
        tattoo: [
            { feld: '', titel: 'Deckung', typ: 'bereich', min: 0, max: 100, einheit: '%' },
            { feld: 'flaeche', titel: 'Fläche', typ: 'bereich', min: 0, max: 100, einheit: '%' },
            { feld: 'groesse', titel: 'Größe', typ: 'bereich', min: 5, max: 150, einheit: 'mm' },
            { feld: 'stil', titel: 'Stil', typ: 'wahl', optionen: [[0, 'Ranken (Linien)'], [1, 'Flächen']] },
            { feld: 'tinte', titel: 'Tinte', typ: 'farbe' },
            { feld: 'muster', titel: 'Muster', typ: 'zahl', min: 1, max: 999 },
        ],
        merkmal: Genesis9hautteilmerkmale.felder(),          // Stärke + 17 Hautebenen je Teil (26.10.2026)
    };

    static TITEL = { farbe: 'Hautfarbe', tattoo: 'Tattoo', merkmal: 'Hautmerkmale' };

    static HINWEIS = {
        farbe: 'Färbt die Haut zur Zielfarbe hin — Poren, Lippen und Zeichnung bleiben als Verhältnis erhalten (wie die Haut-KI). Wirkt sofort.',
        tattoo: 'Muster im Raum der Figur: es haftet an der Haut, auch in Pose und mit Formreglern. „beide“ ist gespiegelt. Wirkt sofort.',
        merkmal: 'Zuschlag auf die Hautregler der ganzen Figur, nur auf diesem Teil (weich an seinen Rändern). Sommersprossen, Altersflecken, Pickel, Cellulite und Aknenarben '
            + 'wirken hier auf dem ganzen Teil, nicht nur in ihrem üblichen Gebiet. Größe und Dichte der Punkte gelten wie bei der ganzen Figur. Wirkt sofort.',
    };

    /** Werte schreiben und anwenden (ohne `markDirty` — das kommt mit `change`). */
    static async stellen(inst, eintraege) {
        Genesis9hautteile.setzen(inst, eintraege);
        await Genesis9hautebenen.anwenden(inst);
    }

    static hex(rgb) {
        return '#' + rgb.map(c => Math.max(0, Math.min(255, Math.round(c))).toString(16).padStart(2, '0')).join('');
    }

    static rgb(hex) {
        const n = parseInt(String(hex).slice(1), 16) || 0;
        return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
    }

    /** Die Farbe eines Farbfelds: Zielfarbe (Hautfarbe) bzw. Tinte (Tattoo), als sRGB-Bytes. */
    static farbe(inst, art, ziel) {
        if (art === 'farbe') return Genesis9hautteile.zielfarbe(inst, ziel);
        return ['r', 'g', 'b'].map(k => Genesis9hautteile.wert(inst, 'tattoo', ziel, k));
    }

    /** @param o.inst Figur, o.art 'farbe'|'tattoo', o.ziel Eintrag aus `Genesis9hautteile.ZIELE`, o.nachher nach jeder Änderung (Bedienfeld nachziehen) */
    static oeffnen({ inst, art, ziel, nachher = () => {} }) {
        Genesis9hautteilfenster.schliessen();
        const titel = `${Genesis9hautteilfenster.TITEL[art]} ${ziel.name}`;
        const huelle = document.createElement('div');
        huelle.className = 'scene-modal-overlay visible g9-profil-huelle';
        huelle.innerHTML = `
            <div class="scene-modal g9-profil-dialog" role="dialog" aria-label="${escapeHtml(titel)}">
                <div class="scene-modal-header"><h4>${escapeHtml(titel)}</h4>
                    <button type="button" class="scene-modal-close" title="Schließen">×</button></div>
                <div class="scene-modal-body">
                    <div class="g9-profil-hinweis gedaempft">${escapeHtml(Genesis9hautteilfenster.HINWEIS[art] || '')}</div>
                    <div class="g9-hautteil-felder"></div>
                </div>
                <div class="scene-modal-footer">
                    <button type="button" class="btn-toggle" data-tat="zurueck">Zurücksetzen</button>
                    <button type="button" class="primary" data-tat="zu">Schließen</button>
                </div>
            </div>`;
        document.body.appendChild(huelle);
        const z = { inst, art, ziel, nachher, huelle, felder: huelle.querySelector('.g9-hautteil-felder') };
        const zu = () => Genesis9hautteilfenster.schliessen(huelle);
        huelle._taste = (e) => { if (e.key === 'Escape') zu(); };
        document.addEventListener('keydown', huelle._taste);
        huelle.querySelector('.scene-modal-close').addEventListener('click', zu);
        huelle.querySelector('[data-tat="zu"]').addEventListener('click', zu);
        huelle.querySelector('[data-tat="zurueck"]').addEventListener('click', async () => {
            await Genesis9hautteilfenster._aendern(z, Object.fromEntries(Genesis9hautteile.felder(art, ziel.ziel).map(k => [k, null])));
            markDirty();
            Genesis9hautteilfenster._fuellen(z);
        });
        Genesis9hautteilfenster._offen = huelle;
        Genesis9hautteilfenster._fuellen(z);
        return huelle;
    }

    static schliessen(huelle = null) {
        const ziel = huelle || Genesis9hautteilfenster._offen;
        if (!ziel) return;
        document.removeEventListener('keydown', ziel._taste);
        ziel.remove();
        if (Genesis9hautteilfenster._offen === ziel) Genesis9hautteilfenster._offen = null;
    }

    static async _aendern(z, eintraege) {
        await Genesis9hautteilfenster.stellen(z.inst, eintraege);
        z.nachher();
    }

    /** Die Felder neu bauen (beim Öffnen und nach „Zurücksetzen“). */
    static _fuellen(z) {
        z.felder.innerHTML = '';
        for (const f of Genesis9hautteilfenster.FELDER[z.art]) z.felder.appendChild(Genesis9hautteilfenster._feld(z, f));
    }

    static _feld(z, f) {
        const { inst, art } = z;
        const ziel = z.ziel.ziel;
        const zeile = document.createElement('label');
        zeile.className = 'g9-hautteil-feld';
        const schluessel = Genesis9hautteile.schluessel(art, ziel, f.feld);
        if (f.typ === 'farbe') {
            zeile.innerHTML = `<span>${escapeHtml(f.titel)}</span><input type="color" value="${Genesis9hautteilfenster.hex(Genesis9hautteilfenster.farbe(inst, art, ziel))}">`;
            const eingabe = zeile.querySelector('input');
            eingabe.addEventListener('input', () => {
                const [r, g, b] = Genesis9hautteilfenster.rgb(eingabe.value);
                const s = k => Genesis9hautteile.schluessel(art, ziel, k);
                Genesis9hautteilfenster._aendern(z, { [s('r')]: r, [s('g')]: g, [s('b')]: b });
            });
        } else if (f.typ === 'wahl') {
            const wert = Genesis9hautteile.wert(inst, art, ziel, f.feld);
            zeile.innerHTML = `<span>${escapeHtml(f.titel)}</span><select>${f.optionen.map(([w, t]) =>
                `<option value="${w}"${w === wert ? ' selected' : ''}>${escapeHtml(t)}</option>`).join('')}</select>`;
            const wahl = zeile.querySelector('select');
            wahl.addEventListener('change', () => { Genesis9hautteilfenster._aendern(z, { [schluessel]: Number(wahl.value) }); markDirty(); });
        } else if (f.typ === 'zahl') {
            const wert = Genesis9hautteile.wert(inst, art, ziel, f.feld);
            zeile.innerHTML = `<span>${escapeHtml(f.titel)}</span><input type="number" class="g9-hautteil-muster" min="${f.min}" max="${f.max}" step="1" value="${wert}">
                <button type="button" class="btn-toggle">Neu würfeln</button>`;
            const zahl = zeile.querySelector('input');
            const setzen = (n) => {
                const v = Math.max(f.min, Math.min(f.max, Math.round(Number(n) || f.min)));
                zahl.value = v;
                Genesis9hautteilfenster._aendern(z, { [schluessel]: v });
                markDirty();
            };
            zahl.addEventListener('change', () => setzen(zahl.value));
            zeile.querySelector('button').addEventListener('click', (e) => { e.preventDefault(); setzen(1 + Math.floor(Math.random() * f.max)); });
        } else {
            const wert = Math.round(Genesis9hautteile.wert(inst, art, ziel, f.feld));
            zeile.innerHTML = `<span>${escapeHtml(f.titel)}</span><input type="range" min="${f.min}" max="${f.max}" step="1" value="${wert}">
                <span class="slider-value">${wert} ${f.einheit}</span>`;
            const schieber = zeile.querySelector('input');
            schieber.addEventListener('input', () => {
                zeile.querySelector('.slider-value').textContent = `${schieber.value} ${f.einheit}`;
                Genesis9hautteilfenster._aendern(z, { [schluessel]: Number(schieber.value) });
            });
            schieber.addEventListener('change', () => markDirty());
        }
        if (f.typ === 'farbe') zeile.querySelector('input').addEventListener('change', () => markDirty());
        return zeile;
    }
}

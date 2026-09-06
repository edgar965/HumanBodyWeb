import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Umatyp } from './umatyp.js';
import { Umagarderobe } from './umagarderobe.js';
import { Gemeinsameregler } from '../gemeinsameregler.js';

/**
 * Umaeigenschaften — der Eigenschaften-Reiter für eine UMA-Figur.
 *
 * WARUM (05.09.2026): Edgar will ein Modell laden (UMA oder HumanBody) und es
 * „vollständig mit den Eigenschaften im Tab daneben sehen und konfigurieren".
 * Für UMA sind das die Regler-Gruppen (Körper, Gesicht, Pose) aus dem
 * UMA-Projekt und die Farben von Haut und Haar. Body Type, Morphs und
 * Ausstattung sind HumanBody-Dinge und bleiben für UMA verborgen.
 *
 * Die Regler zeigen 0–100 (UMA rechnet 0–1); die Vorgabe ist 50, dort sieht
 * die Figur aus wie aus Unity. Reset stellt alle Vorgaben wieder her.
 */
export class Umaeigenschaften {

    static BEREICH = 'prop-uma-section';
    static FARBEN = [['haut', 'Haut'], ['haar', 'Haar']];

    static fuellen(inst) {
        const bereich = document.getElementById(Umaeigenschaften.BEREICH);
        if (!bereich) return;
        bereich.classList.remove('hb-versteckt');
        const regler = inst.regler;
        document.getElementById('prop-uma-kopf').textContent = regler
            ? `${inst.datei} · ${regler.geschlecht} · ${regler.anzahl} Regler`
            : `${inst.datei} · keine Regler (UMA-Projekt nicht gefunden)`;
        // Der Typ (Rasse) zuerst — Edgar, 06.09.2026: „wo ist der Regler nach
        // Typ?". Größe, Gewicht und Muskeln stehen seither im gemeinsamen
        // Block darüber (`scene/gemeinsameregler.js`), zusammen mit den
        // HumanBody-Reglern gleichen Namens.
        Umatyp.fuellen(inst, document.getElementById('prop-uma-typ'));
        Umaeigenschaften._farben(inst, document.getElementById('prop-uma-farben'));
        const gruppen = document.getElementById('prop-uma-gruppen');
        gruppen.innerHTML = '';
        for (const gruppe of (regler ? regler.gruppen : [])) {
            gruppen.appendChild(Umaeigenschaften._gruppe(inst, gruppe));
        }
        const reset = document.getElementById('prop-uma-reset');
        if (reset) {
            reset.onclick = () => {
                Umaeigenschaften._animationAnhalten(inst);
                inst.dna = regler ? regler.vorgaben() : {};
                inst.anwenden();
                Umaeigenschaften.fuellen(inst);
                markDirty('UMA-Regler zurückgesetzt');
            };
        }
    }

    /**
     * Läuft auf dieser Figur eine Animation, schreibt der Mischer in jedem Takt
     * die Knochen — ein Regler zeigte dann nichts (Edgar, 05.09.2026: „Die
     * Eigenschaften kann ich alle nicht verändern"). Also erst anhalten.
     */
    static _animationAnhalten(inst) {
        if (state._animatedCharId === inst.id) fn.stopAnimation?.();
    }

    static leeren() {
        const bereich = document.getElementById(Umaeigenschaften.BEREICH);
        if (bereich) bereich.classList.add('hb-versteckt');
    }

    /**
     * Nach einem gemeinsamen Regler die Einzelregler darunter nachziehen.
     * Öffentlich, weil `Gemeinsameregler` sie als Rückruf bekommt.
     */
    static einzelreglerAngleichen(inst) {
        Umaeigenschaften._animationAnhalten(inst);
        inst.anwenden();
        Umaeigenschaften._reglerNachziehen(inst);
    }

    static _reglerNachziehen(inst) {
        for (const schieber of document.querySelectorAll('#prop-uma-gruppen input[data-name]')) {
            const wert = inst.dna[schieber.dataset.name];
            if (wert === undefined) continue;
            schieber.value = Math.round(wert * 100);
            const anzeige = schieber.parentElement.querySelector('.slider-val');
            if (anzeige) anzeige.textContent = schieber.value;
        }
    }

    static _gruppe(inst, gruppe) {
        const kasten = document.createElement('details');
        kasten.className = 'uma-gruppe';
        kasten.open = gruppe.name === 'Körper';
        const titel = document.createElement('summary');
        titel.textContent = `${gruppe.name} (${gruppe.regler.length})`;
        kasten.appendChild(titel);
        for (const regler of gruppe.regler) {
            kasten.appendChild(Umaeigenschaften._zeile(inst, regler));
        }
        return kasten;
    }

    static _zeile(inst, regler) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const wert = Math.round((inst.dna[regler.name] ?? regler.vorgabe) * 100);
        zeile.innerHTML = `<label title="${escapeHtml(regler.name)}">${escapeHtml(regler.anzeige)}</label>`
            + `<input type="range" min="0" max="100" step="1" value="${wert}">`
            + `<span class="slider-val">${wert}</span>`;
        const schieber = zeile.querySelector('input');
        schieber.dataset.name = regler.name;
        const anzeige = zeile.querySelector('.slider-val');
        schieber.addEventListener('input', () => {
            Umaeigenschaften._animationAnhalten(inst);
            inst.dna[regler.name] = parseInt(schieber.value, 10) / 100;
            anzeige.textContent = schieber.value;
            inst.anwenden();
            // Ein Einzelregler kann einen gemeinsamen mitbewegen (etwa
            // `belly` das Gewicht) — den Block darüber nachziehen.
            Gemeinsameregler.angleichen(inst);
        });
        schieber.addEventListener('change', () => markDirty(`UMA ${regler.name}`));
        return zeile;
    }

    /**
     * Haut- und Haarfarbe. UMA backt die Farben in Unity in den Atlas; im
     * Browser ist ein Farbfeld nur eine Tönung des fertigen Bildes (Edgar,
     * 06.09.2026: „warum kann man die Hautfarbe nicht setzen"). Deshalb: Feld
     * vorbelegt mit der GEBAUTEN Farbe (Zettel), Änderung als Vorschau-Tönung,
     * und ein Knopf, der sie in Unity backen lässt (`Umatyp.neuBauen`).
     */
    static async _farben(inst, behaelter) {
        behaelter.innerHTML = '';
        const garderobe = await Umagarderobe.lesen(inst.datei).catch(() => null);
        const gebacken = garderobe?.farben || {};
        const knopf = document.createElement('button');
        knopf.className = 'btn-toggle hb-volle-breite';
        knopf.innerHTML = '<i class="fas fa-hammer"></i> Farben in Unity bauen';
        const stand = document.createElement('div');
        stand.className = 'hb-font-size-0-72rem';
        const nachziehen = () => Umaeigenschaften._farbstand(inst, gebacken, knopf, stand);
        for (const [schluessel, beschriftung] of Umaeigenschaften.FARBEN) {
            const zeile = document.createElement('div');
            zeile.className = 'slider-row';
            const grund = () => gebacken[schluessel] || Umaeigenschaften._grundfarbe(inst, schluessel);
            zeile.innerHTML = `<label>${beschriftung}</label>`
                + `<input type="color" class="hb-farbfeld" value="${inst.farben[schluessel] || grund()}">`
                + '<button class="btn-toggle knopf-schmal" title="Zurück auf die gebaute Farbe">'
                + '<i class="fas fa-undo"></i></button>';
            const feld = zeile.querySelector('input');
            feld.addEventListener('input', () => {
                inst.farben[schluessel] = feld.value;
                inst.farbenAnwenden();
                nachziehen();
            });
            feld.addEventListener('change', () => markDirty(`UMA-Farbe ${schluessel}`));
            zeile.querySelector('button').addEventListener('click', () => {
                inst.farben[schluessel] = null;
                inst.farbenAnwenden();
                feld.value = grund();
                nachziehen();
                markDirty(`UMA-Farbe ${schluessel}`);
            });
            behaelter.appendChild(zeile);
        }
        knopf.addEventListener('click', () => Umatyp.neuBauen(inst, { stand }));
        behaelter.append(knopf, stand);
        nachziehen();
    }

    /** Die Zeile unter den Farbfeldern: Tönung ist Vorschau, gebaut wird in Unity. */
    static _farbstand(inst, gebacken, knopf, stand) {
        const offen = Umaeigenschaften.FARBEN.map(([s]) => s)
            .filter(s => inst.farben[s] && inst.farben[s].toLowerCase() !== (gebacken[s] || ''));
        knopf.classList.toggle('active', offen.length > 0);
        if (offen.length) {
            stand.textContent = `Geändert: ${offen.join(', ')} — im Browser nur als Tönung sichtbar. `
                + '„Farben in Unity bauen" backt sie in die Haut.';
        } else {
            stand.textContent = Object.keys(gebacken).length
                ? 'Farben wie in Unity gebaut.' : 'Farben der Rasse (Unity-Vorgabe).';
        }
    }

    static _grundfarbe(inst, schluessel) {
        const muster = schluessel === 'haut' ? /skin/i : /hair/i;
        const netz = inst.netze.find(n => muster.test(n.material?.name || ''));
        const farbe = netz?.userData.grundfarbe || netz?.material?.color;
        return farbe ? `#${farbe.getHexString()}` : '#ffffff';
    }
}

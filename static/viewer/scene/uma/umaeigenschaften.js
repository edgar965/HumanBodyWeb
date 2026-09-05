import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';
import { state } from '../state.js';
import { fn } from '../../gemeinsam/registrierung.js';
import { Umatyp } from './umatyp.js';
import { Umamasse } from './umamasse.js';

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
        // Typ (Rasse) und die zwei Hauptmaße zuerst — Edgar, 06.09.2026:
        // „Wo ist der Größen-, Gewichtregler?? wo ist der Regler nach Typ?"
        Umatyp.fuellen(inst, document.getElementById('prop-uma-typ'));
        const masse = document.getElementById('prop-uma-masse');
        Umamasse.fuellen(inst, masse, () => {
            Umaeigenschaften._animationAnhalten(inst);
            inst.anwenden();
            Umaeigenschaften._einzelreglerAngleichen(inst);
        });
        Umaeigenschaften._farben(inst, document.getElementById('prop-uma-farben'));
        const gruppen = document.getElementById('prop-uma-gruppen');
        gruppen.innerHTML = '';
        for (const gruppe of (regler ? regler.gruppen : [])) {
            gruppen.appendChild(Umaeigenschaften._gruppe(inst, gruppe, masse));
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

    /** Nach Größe oder Gewicht die betroffenen Einzelregler nachziehen. */
    static _einzelreglerAngleichen(inst) {
        for (const schieber of document.querySelectorAll('#prop-uma-gruppen input[data-name]')) {
            const wert = inst.dna[schieber.dataset.name];
            if (wert === undefined) continue;
            schieber.value = Math.round(wert * 100);
            const anzeige = schieber.parentElement.querySelector('.slider-val');
            if (anzeige) anzeige.textContent = schieber.value;
        }
    }

    static _gruppe(inst, gruppe, masse) {
        const kasten = document.createElement('details');
        kasten.className = 'uma-gruppe';
        kasten.open = gruppe.name === 'Körper';
        const titel = document.createElement('summary');
        titel.textContent = `${gruppe.name} (${gruppe.regler.length})`;
        kasten.appendChild(titel);
        for (const regler of gruppe.regler) {
            kasten.appendChild(Umaeigenschaften._zeile(inst, regler, masse));
        }
        return kasten;
    }

    static _zeile(inst, regler, masse) {
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
            if (masse) Umamasse.angleichen(inst, masse);
        });
        schieber.addEventListener('change', () => markDirty(`UMA ${regler.name}`));
        return zeile;
    }

    static _farben(inst, behaelter) {
        behaelter.innerHTML = '';
        for (const [schluessel, beschriftung] of Umaeigenschaften.FARBEN) {
            const zeile = document.createElement('div');
            zeile.className = 'slider-row';
            const wert = inst.farben[schluessel] || Umaeigenschaften._grundfarbe(inst, schluessel);
            zeile.innerHTML = `<label>${beschriftung}</label>`
                + `<input type="color" class="hb-farbfeld" value="${wert}">`
                + '<button class="btn-toggle knopf-schmal" title="Farbe aus der GLB">'
                + '<i class="fas fa-undo"></i></button>';
            const feld = zeile.querySelector('input');
            feld.addEventListener('input', () => {
                inst.farben[schluessel] = feld.value;
                inst.farbenAnwenden();
            });
            feld.addEventListener('change', () => markDirty(`UMA-Farbe ${schluessel}`));
            zeile.querySelector('button').addEventListener('click', () => {
                inst.farben[schluessel] = null;
                inst.farbenAnwenden();
                feld.value = Umaeigenschaften._grundfarbe(inst, schluessel);
                markDirty(`UMA-Farbe ${schluessel}`);
            });
            behaelter.appendChild(zeile);
        }
    }

    static _grundfarbe(inst, schluessel) {
        const muster = schluessel === 'haut' ? /skin/i : /hair/i;
        const netz = inst.netze.find(n => muster.test(n.material?.name || ''));
        const farbe = netz?.userData.grundfarbe || netz?.material?.color;
        return farbe ? `#${farbe.getHexString()}` : '#ffffff';
    }
}

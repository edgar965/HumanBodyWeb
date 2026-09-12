import { escapeHtml } from '../utils.js';
import { markDirty } from '../undo.js';

/**
 * Umapythoneigenschaften — der Eigenschaften-Reiter einer UMA-Python-Figur.
 *
 * WARUM ER JETZT ANDERS AUSSIEHT (Edgar, 08.09.2026: „Ich möchte doch ein
 * Male, Female, Elf usw. auswählen, genau so wie UMA das macht!")
 * =====================================================================
 * Vorher standen hier zwei geometrische Regler (Umfang, Länge), die einen
 * GarmentCode-Referenzkörper verformten — ein Prüfstand für den Konformer.
 * Jetzt stehen hier UMAs EIGENE Regler: die DNA der gewählten Rasse, so wie
 * das Unity-Projekt sie führt.
 *
 * Welche das sind, sagt der Server. Nicht jede Rasse kennt jeden Regler
 * (gemessen bei UMA: 62 bei einer weiblichen, 58 bei einer männlichen
 * Rasse) — eine feste Liste im Browser zeigte deshalb Regler, die nichts
 * bewirken, und das sieht aus wie ein Fehler der Figur.
 *
 * BEIM ZIEHEN WIRD GERECHNET, ABER ENTPRELLT
 * ==========================================
 * Der Server hält die gebaute Figur; ein Reglerzug kostet nur die Knochen-
 * und Hautrechnung — gemessen 0,07 s gegen 6–14 s für den Bau. Das ist
 * bezahlbar, aber nicht gratis: Es wird entprellt, und während ein Lauf
 * unterwegs ist, wird nur der Wunsch gemerkt. Sonst überholten sich die
 * Antworten und es bliebe eine veraltete Stellung stehen (derselbe Befund
 * wie bei `garmentcode_live.js` am 08.09.2026).
 */
export class Umapythoneigenschaften {

    static BEREICH = 'prop-umapython-section';
    static RUHE_MS = 140;

    /** So viele Regler stehen offen; der Rest liegt unter „mehr". */
    static SOFORT = 12;

    static _zeitgeber = null;
    static _laeuft = false;
    static _nachholen = null;

    static fuellen(inst) {
        const bereich = document.getElementById(Umapythoneigenschaften.BEREICH);
        if (!bereich) return;
        bereich.classList.remove('hb-versteckt');
        Umapythoneigenschaften._kopf(inst);
        Umapythoneigenschaften._regler(inst);
        Umapythoneigenschaften._bilanz(inst);
    }

    /**
     * Den Bereich verbergen.
     *
     * HEISST `leeren`, WEIL `properties.js` SO RUFT. Beim Umbau am
     * 08.09.2026 hiess die Methode kurz `verbergen` — der Aufruf lief in
     * einen `TypeError`, der `populateProperties` abbrach, und damit fiel
     * die GANZE Figurauswahl aus. Sichtbar war nur: Eine hinzugefuegte
     * Figur erschien nicht. Die Klasse stumme-ES-Modul-Fehler
     * (`~/.claude/rules/es-module-stumme-fehler.md`).
     */
    static leeren() {
        document.getElementById(Umapythoneigenschaften.BEREICH)
            ?.classList.add('hb-versteckt');
    }

    // ------------------------------------------------------------- Anzeige

    static _kopf(inst) {
        const feld = document.getElementById('prop-umapython-kopf');
        if (!feld) return;
        feld.innerHTML = `<strong>${escapeHtml(inst.rasse)}</strong>`;
    }

    static _bilanz(inst) {
        const feld = document.getElementById('prop-umapython-bilanz');
        if (!feld) return;
        const b = inst.bilanz;
        if (!b) { feld.textContent = ''; return; }
        const fehlend = b.fehlend?.length
            ? ` · ${b.fehlend.length} Slot(s) fehlen` : '';
        feld.innerHTML =
            `${b.punkte.toLocaleString()} Punkte · `
            + `${b.knochen} Knochen · ${b.slots} Slots · `
            + `${Number(b.hoehe_m).toFixed(2)} m${escapeHtml(fehlend)}`;
    }

    // ------------------------------------------------------------- Regler

    static _regler(inst) {
        const behaelter = document.getElementById('prop-umapython-form');
        if (!behaelter) return;
        const regler = inst.regler || [];
        if (!regler.length) {
            behaelter.innerHTML =
                '<div class="gedaempft">Diese Rasse führt keine DNA-Regler.</div>';
            return;
        }
        behaelter.innerHTML = '';
        regler.forEach((r, nummer) => {
            const wert = inst.dna[r.name] ?? r.vorgabe;
            const zeile = Umapythoneigenschaften._zeile(inst, r, wert);
            if (nummer >= Umapythoneigenschaften.SOFORT) {
                zeile.classList.add('hb-versteckt');
                zeile.dataset.mehr = '1';
            }
            behaelter.appendChild(zeile);
        });
        if (regler.length > Umapythoneigenschaften.SOFORT) {
            behaelter.appendChild(
                Umapythoneigenschaften._mehrKnopf(behaelter, regler.length));
        }
    }

    static _zeile(inst, regler, wert) {
        const zeile = document.createElement('div');
        zeile.className = 'slider-row';
        const kennung = `upy-${regler.name}`;
        zeile.innerHTML = `
            <label for="${kennung}">${escapeHtml(regler.anzeige)}</label>
            <input type="range" id="${kennung}" min="0" max="1" step="0.01"
                   value="${wert}">
            <span class="slider-value" id="${kennung}-wert">${
                Umapythoneigenschaften._text(wert)}</span>`;
        const schieber = zeile.querySelector('input');
        const anzeige = zeile.querySelector('.slider-value');
        schieber.addEventListener('input', () => {
            const neu = parseFloat(schieber.value);
            anzeige.textContent = Umapythoneigenschaften._text(neu);
            Umapythoneigenschaften._planen(inst, regler.name, neu);
        });
        return zeile;
    }

    /** −100…+100 statt 0…1 — dieselbe Skala wie bei den gemeinsamen
     *  Reglern (`humanbody_core/regler`), damit die Mitte sichtbar 0 ist. */
    static _text(wert) {
        return String(Math.round((wert - 0.5) * 200));
    }

    static _mehrKnopf(behaelter, anzahl) {
        const knopf = document.createElement('button');
        knopf.className = 'btn-toggle hb-dehnt';
        const versteckt = anzahl - Umapythoneigenschaften.SOFORT;
        knopf.textContent = `${versteckt} weitere Regler`;
        knopf.addEventListener('click', () => {
            for (const zeile of behaelter.querySelectorAll('[data-mehr]')) {
                zeile.classList.remove('hb-versteckt');
            }
            knopf.remove();
        });
        return knopf;
    }

    // -------------------------------------------------------------- Lauf

    static _planen(inst, name, wert) {
        clearTimeout(Umapythoneigenschaften._zeitgeber);
        Umapythoneigenschaften._zeitgeber = setTimeout(
            () => Umapythoneigenschaften._ziehen(inst, name, wert),
            Umapythoneigenschaften.RUHE_MS);
    }

    static async _ziehen(inst, name, wert) {
        if (Umapythoneigenschaften._laeuft) {
            // Nur den Wunsch merken: Zwei gleichzeitige Läufe können sich
            // überholen, und dann bliebe die ältere Stellung stehen.
            Umapythoneigenschaften._nachholen = [inst, name, wert];
            return;
        }
        Umapythoneigenschaften._laeuft = true;
        try {
            await inst.reglerSetzen(name, wert);
            Umapythoneigenschaften._bilanz(inst);
            markDirty();
        } catch (fehler) {
            const feld = document.getElementById('prop-umapython-bilanz');
            if (feld) feld.textContent = `Fehler: ${fehler.message}`;
        } finally {
            Umapythoneigenschaften._laeuft = false;
            const offen = Umapythoneigenschaften._nachholen;
            Umapythoneigenschaften._nachholen = null;
            if (offen) Umapythoneigenschaften._ziehen(...offen);
        }
    }
}

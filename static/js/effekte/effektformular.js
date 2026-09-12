import { Htmltext } from '/static/djangobase/js/htmltext.js';

/**
 * Effektformular — die Auswahl der Seite „Effekte" lesen und den Vorschlag
 * fuer die Ausgabedatei bauen.
 *
 * Zwei Pipelines, ein Formular: Bereiche mit `data-pipeline="…"` gehoeren
 * nur zu einer und werden mit der Wahl ein- und ausgeblendet; gelesen
 * werden nur die sichtbaren Parameterfelder. Die Parameterfelder tragen
 * `data-parameter` (int, float, bool, text) — gerendert aus
 * `Effektparameter.FELDER` bzw. `Figurparameter.FELDER`; hier steht KEINE
 * eigene Feldliste (12.09.2026).
 *
 * Animation und Modell setzen `animationsbrowser.js` und `modellwahl.js`
 * ueber `data-*` an ihren Kaesten; der Vorschlag fuer die Ausgabe folgt der
 * Auswahl, solange der Nutzer das Feld nicht selbst beschrieben hat:
 *
 *   kleid_wind  <effekte-basis>\<bvh-stamm>\<bvh-stamm>_<kleid>.mp4
 *   figur_def   <video-ausgabe>\<modell>_<bvh-stamm>.mp4   (der „output"-Ordner)
 */
export class Effektformular {

    constructor(formular) {
        this.formular = formular;
        this.basis = formular.dataset.ausgabeBasis || '';
        this.videoAusgabe = formular.dataset.videoAusgabe || '';
        this.mitModell = (formular.dataset.mitModell || '').split(' ').filter(Boolean);
        this.ausgabe = formular.querySelector('#effektAusgabe');
        this.pipelineFeld = formular.querySelector('#effektPipeline');
        this.animation = formular.querySelector('#effektAnimation');
        this.modell = formular.querySelector('#effektModell');
        this.eigenerPfad = false;
    }

    aufbauen() {
        this.formular.addEventListener('change', (ereignis) => {
            if (ereignis.target === this.ausgabe) return;
            if (ereignis.target === this.pipelineFeld) this.umschalten();
            this.vorschlagSetzen();
        });
        this.ausgabe.addEventListener('input', () => {
            this.eigenerPfad = this.ausgabe.value.trim() !== '';
        });
        this.umschalten();
        this.vorschlagSetzen();
        return this;
    }

    // ------------------------------------------------------------ Pipeline

    pipeline() {
        return this.pipelineFeld.value;
    }

    brauchtModell(pipeline = this.pipeline()) {
        return this.mitModell.includes(pipeline);
    }

    /** Bereiche der anderen Pipeline ausblenden. */
    umschalten() {
        const jetzt = this.pipeline();
        for (const bereich of this.formular.querySelectorAll('[data-pipeline]')) {
            bereich.hidden = bereich.dataset.pipeline !== jetzt;
        }
        this.formular.querySelector('#effektAusgabeHinweis').textContent = this.brauchtModell()
            ? '— daneben entstehen .json, .log und ein Ordner „_lauf"'
            : '— daneben entstehen .blend, .json und .log';
    }

    // ------------------------------------------------------------- Auswahl

    /** Der gewaehlte Animationseintrag (aus dem Browser) oder null. */
    animationWahl() {
        const d = this.animation.dataset;
        return d.wert ? { wert: d.wert, name: d.name, format: d.format, passt: d.passt } : null;
    }

    animationSetzen(eintrag) {
        const d = this.animation.dataset;
        d.wert = eintrag.wert;
        d.name = eintrag.name;
        d.format = eintrag.format || '';
        d.passt = eintrag.passt === null || eintrag.passt === undefined ? '' : String(eintrag.passt);
        this.animation.querySelector('#effektAnimationName').textContent = eintrag.name;
        this.animation.querySelector('#effektAnimationMeta').textContent = eintrag.meta || '';
        this.animation.querySelector('#effektAnimationPfad').textContent = eintrag.wert;
        this.vorschlagSetzen();
    }

    /** Was in der gewaehlten Pipeline mit diesem Eintrag nicht geht — oder ''. */
    sperrgrund(eintrag) {
        if (!this.brauchtModell() && eintrag.passt === false) {
            return 'Blender-Retargeter kennt die Gelenke nicht (nur SMPL)';
        }
        return '';
    }

    kleid() {
        return this.formular.querySelector('#effektKleid');
    }

    /** Vorschlag je Pipeline — nur ohne eigenen Pfad. */
    vorschlagSetzen() {
        if (this.eigenerPfad) return;
        const wahl = this.animationWahl();
        if (!wahl) return;
        const stamm = (wahl.name || 'effekt').replace(/\.bvh$/i, '');
        let teile;
        if (this.brauchtModell()) {
            const modell = this.modell.dataset.name;
            if (!modell || !this.videoAusgabe) return;
            teile = [this.videoAusgabe, `${modell}_${stamm}.mp4`];
        } else {
            const kleid = this.kleid();
            if (!kleid || !this.basis) return;
            const name = kleid.selectedOptions[0]?.dataset.name || 'kleid';
            teile = [this.basis, stamm, `${stamm}_${name}.mp4`];
        }
        const trenner = teile[0].includes('\\') ? '\\' : '/';
        this.ausgabe.value = teile.join(trenner);
    }

    // --------------------------------------------------------------- Lesen

    /** Die Nutzlast fuer /api/effekte/start/ — nur die sichtbaren Felder. */
    lesen() {
        const wahl = this.animationWahl();
        const parameter = {};
        for (const feld of this.formular.querySelectorAll('[data-parameter]')) {
            if (feld.closest('[data-pipeline]')?.hidden) continue;
            const art = feld.dataset.parameter;
            if (art === 'bool') parameter[feld.name] = feld.checked;
            else if (art === 'int') parameter[feld.name] = parseInt(feld.value, 10);
            else if (art === 'float') parameter[feld.name] = parseFloat(feld.value);
            else parameter[feld.name] = feld.value;
        }
        return {
            bvh: wahl ? wahl.wert : '',
            kleid: this.brauchtModell() ? '' : this.kleid().value,
            modell: this.brauchtModell() ? this.modell.dataset.name || '' : '',
            pipeline: this.pipeline(),
            ausgabe: this.ausgabe.value.trim(),
            name: Effektformular.name(this.ausgabe.value),
            parameter,
        };
    }

    static name(pfad) {
        const teil = pfad.split(/[\\/]/).pop() || '';
        return teil.replace(/\.mp4$/i, '');
    }

    /** Was fehlt, bevor gestartet werden kann — oder ''. */
    pruefen(daten) {
        if (!daten.bvh) return 'Bitte eine Animation wählen.';
        if (this.brauchtModell(daten.pipeline)) {
            if (!daten.modell) return 'Bitte ein Modell wählen.';
        } else if (!daten.kleid) {
            return 'Bitte ein Kleid wählen.';
        }
        if (!/\.mp4$/i.test(daten.ausgabe)) return 'Die Ausgabedatei muss auf .mp4 enden.';
        for (const [name, wert] of Object.entries(daten.parameter)) {
            if (typeof wert === 'number' && Number.isNaN(wert)) {
                return `Feld „${Htmltext.maskieren(name)}" ist keine Zahl.`;
            }
        }
        return '';
    }
}

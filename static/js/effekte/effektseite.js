import { Serverabruf } from '/static/djangobase/js/serverabruf.js';
import { Animationsbrowser } from './animationsbrowser.js';
import { Effektformular } from './effektformular.js';
import { Effektverlauf } from './effektverlauf.js';
import { Modellwahl } from './modellwahl.js';
import { Schieber } from './schieber.js';

/**
 * Effektseite — Start, Anhalten, Verfolgen und „Zeigen" auf der Seite
 * „Process Videos — Effekte" (12.09.2026), dazu die beiden Dialoge:
 * Animationsbrowser und Modellwahl.
 *
 * Vorbelegt ist die neueste passende Auftrags-BVH (`vorgewaehlt` aus
 * `Effektquellen.bvh_dateien()`) — so steht der Ausgabevorschlag sofort da.
 */
export class Effektseite {

    static aufbauen() {
        return new Effektseite().aufbauen();
    }

    constructor() {
        this.schirm = document.getElementById('effektSchirm');
        this.formular = new Effektformular(document.getElementById('effektFormular'));
        this.verlauf = new Effektverlauf(this.schirm, () => this.beiEnde());
        this.startknopf = document.getElementById('effektStart');
        this.meldung = document.getElementById('effektMeldung');
        this.auftraege = Effektseite.json('effektAuftraegeBvh');
        this.browser = new Animationsbrowser(this.auftraege,
            (eintrag) => this.formular.animationSetzen(eintrag));
        this.modellwahl = new Modellwahl(document.getElementById('effektModell'),
            Effektseite.json('effektModelle'), () => this.formular.vorschlagSetzen());
    }

    /** Ein `json_script`-Block der Seite — [] wenn er fehlt. */
    static json(kennung) {
        const block = document.getElementById(kennung);
        try {
            return block ? JSON.parse(block.textContent) : [];
        } catch {
            return [];
        }
    }

    aufbauen() {
        this.formular.aufbauen();
        Schieber.verdrahten(document.getElementById('effektFormular'));
        this.vorbelegen();
        this.startknopf.addEventListener('click', () => this.starten());
        document.getElementById('effektStopp').addEventListener('click', () => this.anhalten());
        document.getElementById('effektAnimationKnopf').addEventListener('click',
            () => this.browser.oeffnen((eintrag) => this.formular.sperrgrund(eintrag)));
        document.getElementById('effektModellKnopf').addEventListener('click',
            () => this.modellwahl.oeffnen());
        for (const knopf of document.querySelectorAll('[data-zeigen]')) {
            knopf.addEventListener('click',
                () => this.zeigen(knopf.dataset.zeigen, knopf.dataset.name));
        }
        const laufend = this.schirm.dataset.auftrag;
        if (laufend && !Effektverlauf.ENDE.includes(this.schirm.dataset.status)) {
            this.verlauf.verfolgen(laufend);
        }
        return this;
    }

    /**
     * Startwahlen aus Einstellungen → Effekte (`data-vorgabe-*` am Formular,
     * `Effektvorgaben`): Pipeline, Modell, Animation. Ohne Animationsvorgabe
     * die neueste passende Auftrags-BVH.
     */
    vorbelegen() {
        const v = this.formular.formular.dataset;
        const pipeline = this.formular.pipelineFeld;
        if (v.vorgabePipeline && [...pipeline.options].some(o => o.value === v.vorgabePipeline)) {
            pipeline.value = v.vorgabePipeline;
            this.formular.umschalten();
        }
        if (v.vorgabeModell && this.modellwahl.eintrag(v.vorgabeModell)) {
            this.modellwahl.waehlen(v.vorgabeModell);
        }
        const vorgabe = this.animationVorgabe(v.vorgabeAnimation);
        const [gruppe] = this.browser.gruppen();
        const erster = vorgabe || gruppe?.eintraege.find(e => e.passt) || null;
        if (erster) this.formular.animationSetzen(erster);
    }

    /**
     * Der Eintrag zur Animationsvorgabe: ein Auftrag (Pfad) aus „Process
     * Videos" oder eine Bibliotheksadresse `/api/character/bvh/<k>/<n>/`.
     */
    animationVorgabe(wert) {
        if (!wert) return null;
        const auftrag = this.browser.gruppen().flatMap(g => g.eintraege).find(e => e.wert === wert);
        if (auftrag) return auftrag;
        const teile = wert.replace(/^\/api\/character\/bvh\//, '').replace(/\/$/, '').split('/');
        if (teile.length !== 2 || !teile[0] || !teile[1]) return null;
        return { wert, name: `${teile[1]}.bvh`, meta: `${teile[0]} · Bibliothek`, format: '', passt: null };
    }

    async starten() {
        const daten = this.formular.lesen();
        const grund = this.formular.pruefen(daten);
        if (grund) {
            this.melden(grund, true);
            return;
        }
        this.startknopf.disabled = true;
        this.melden('');
        try {
            const antwort = await Serverabruf.senden('/api/effekte/start/', daten);
            this.schirm.dataset.auftrag = antwort.id;
            this.verlauf.verfolgen(antwort.id);
            this.schirm.querySelector('#effektName').textContent = daten.name;
        } catch (fehler) {
            this.startknopf.disabled = false;
            this.melden((fehler.daten && fehler.daten.error) || fehler.message, true);
        }
    }

    async anhalten() {
        const id = this.schirm.dataset.auftrag;
        if (!id) return;
        try {
            await Serverabruf.senden(`/api/effekte/${id}/stop/`, {});
        } catch (fehler) {
            this.melden((fehler.daten && fehler.daten.error) || fehler.message, true);
        }
    }

    beiEnde() {
        this.startknopf.disabled = false;
    }

    /** Ein frueheres Ergebnis in den Schirm holen. */
    async zeigen(id, name) {
        try {
            const daten = await Serverabruf.json(`/api/effekte/${id}/status/`);
            this.verlauf.stoppen();
            this.schirm.dataset.auftrag = id;
            this.verlauf.anzeigen(daten);
            this.schirm.querySelector('#effektName').textContent = name || daten.name;
            this.schirm.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } catch (fehler) {
            this.melden(fehler.message, true);
        }
    }

    melden(text, fehler = false) {
        this.meldung.textContent = text;
        this.meldung.hidden = !text;
        this.meldung.classList.toggle('effekt-meldung-fehler', fehler);
    }
}

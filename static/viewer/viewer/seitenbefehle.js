/**
 * Seitenbefehle — die Befehle aus Menüleiste und Tastatur (`viewer-action`).
 *
 * Aus viewer/index.js herausgeloest (Umbau 16.08.2026): eine
 * `switch`-Anweisung mit acht Faellen ueber 55 Zeilen, in denen dreimal
 * derselbe Abwahl-Block stand —
 *
 *     if (state._selectedItem) _setEmissiveOnItem(state._selectedItem, state._ZERO_EMISSIVE);
 *     state._selectedItem = null; state._hoveredItem = null;
 *     const rb = document.getElementById('selection-remove-btn');
 *     if (rb) rb.style.display = 'none';
 *
 * dreimal mit einem anderen Variablennamen fuer denselben Knopf (`rb`, `rb2`,
 * `rb3`), weil `const` im selben Block nicht zweimal gehen. Genau daran merkt
 * man, dass ein Block zu oft dasteht.
 *
 * 05.09.2026: Datei -> Exportieren -> Figur – GLB (`FigurExport`), damit
 * Roomguest die Figur spielen kann.
 */
import { FigurExport } from './figur_export.js';

export class Seitenbefehle {

    /**
     * @param {Object} state
     * @param {Buehne} buehne
     * @param {Object} dienste  { auswahlFarbeSetzen, ausstattungAktualisieren,
     *        alleGarnituren, alleKleider, haareEntfernen, modellzustand,
     *        gewaehltesEntfernen }
     */
    constructor(state, buehne, dienste) {
        this.state = state;
        this.buehne = buehne;
        this.dienste = dienste;
    }

    verdrahten() {
        document.addEventListener('viewer-action', (ereignis) => {
            this.ausfuehren(ereignis.detail?.action);
        });
        return this;
    }

    ausfuehren(befehl) {
        const handlung = {
            'new': () => this.neu(),
            'deselect': () => this.abwaehlen(),
            'delete': () => this.dienste.gewaehltesEntfernen?.(),
            'clear-all': () => this.allesEntfernen(),
            'export-model-json': () => this.alsJsonSpeichern(),
            'export-figur-glb': () => this.figurAblegen(),
            'export-figur-glb-download': () => this.figurHerunterladen(),
            'reset-camera': () => this.buehne.kameraZuruecksetzen(),
            'reset-lighting': () => this.buehne.lichtZuruecksetzen(),
            'reset-scene': () => this.szeneZuruecksetzen(),
        }[befehl];
        if (handlung) handlung();
    }

    // ------------------------------------------------------------------ Befehle

    /** Neues Modell: Morphs zurück, alles ausziehen, Auswahl leeren. */
    neu() {
        document.getElementById('reset-morphs')?.click();
        this._ausziehen();
        this.abwaehlen();
        this.dienste.ausstattungAktualisieren();
        this.state.currentPresetName = '';
        if (this.state.currentAction) {
            this.state.currentAction.stop();
            this.state.currentAction = null;
        }
    }

    /**
     * Auswahl aufheben. Stand dreimal im switch — mit drei Namen fuer denselben
     * Knopf.
     */
    abwaehlen() {
        if (this.state._selectedItem) {
            this.dienste.auswahlFarbeSetzen(this.state._selectedItem,
                                            this.state._ZERO_EMISSIVE);
        }
        this.state._selectedItem = null;
        this.state._hoveredItem = null;
        const knopf = document.getElementById('selection-remove-btn');
        if (knopf) knopf.style.display = 'none';
    }

    allesEntfernen() {
        if (!confirm('Alle Kleidung, Haare und Garments entfernen?')) return;
        this._ausziehen();
        this.abwaehlen();
        this.dienste.ausstattungAktualisieren();
    }

    /** Kleidung, Garnituren, Haare weg und das Haar-Auswahlfeld leeren. */
    _ausziehen() {
        this.dienste.alleGarnituren();
        this.dienste.alleKleider();
        this.dienste.haareEntfernen();
        const haarfeld = document.getElementById('hair-style-select');
        if (haarfeld) haarfeld.value = '';
    }

    alsJsonSpeichern() {
        const zustand = this.dienste.modellzustand();
        const blob = new Blob([JSON.stringify(zustand, null, 2)],
                              { type: 'application/json' });
        const adresse = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = adresse;
        link.download = (this.state.currentPresetName || 'model') + '.json';
        link.click();
        URL.revokeObjectURL(adresse);
    }

    /** Die Figur als GLB auf den Server — dort holt Roomguest sie ab. */
    async figurAblegen() {
        try {
            const antwort = await new FigurExport(this.state).ablegen();
            alert(`Figur abgelegt:\n${antwort.pfad}\n${antwort.bytes} Bytes`);
        } catch (fehler) {
            alert('GLB-Export fehlgeschlagen: ' + fehler.message);
        }
    }

    /** Die Figur als GLB in den Browser. */
    async figurHerunterladen() {
        try {
            await new FigurExport(this.state).herunterladen();
        } catch (fehler) {
            alert('GLB-Export fehlgeschlagen: ' + fehler.message);
        }
    }

    /**
     * Alles zurück. Ruft die drei Einzelbefehle direkt auf, statt sich selbst
     * dreimal ueber `document.dispatchEvent` anzustossen — das war der Weg
     * vorher und machte den Ablauf schwer nachvollziehbar.
     */
    szeneZuruecksetzen() {
        if (!confirm('Szene komplett zurücksetzen? (Modell, Beleuchtung, Kamera)')) {
            return;
        }
        this.neu();
        this.buehne.lichtZuruecksetzen();
        this.buehne.kameraZuruecksetzen();
    }
}

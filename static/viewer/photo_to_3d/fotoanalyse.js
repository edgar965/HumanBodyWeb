import { state, API } from './state.js';
import { fn } from '../gemeinsam/registrierung.js';
import { enableTextureButtons, captureAndSaveScreenshot } from './job_management.js';
import { showJobJson } from './auftragsergebnis.js';
import { Fotoergebnis } from './fotoergebnis.js';

/**
 * Fotoanalyse — ein Foto zum Server geben und das Ergebnis in die Seite bringen.
 *
 * Aus photo_to_3d/photo_upload.js herausgeloest (Umbau 16.08.2026):
 * `analyzePhoto()` war mit 272 Zeilen die laengste JavaScript-Funktion des
 * Projekts. Sie war intern schon in Schritte geteilt — die Kommentare
 * "=== Step 1: Set ALL state values ===", "Step 2: Update ALL slider UIs",
 * "Step 3: Trigger model loads" standen genau dort, wo jetzt die
 * Methodengrenzen liegen. Die Gliederung war also bekannt, nur nicht
 * aufgeschrieben.
 *
 * Ein Duplikat dabei behoben: Die Regler fuer Shape- und Ausdrucks-Parameter
 * wurden mit zwei gleichlautenden Bloecken nachgezogen
 * (`input[data-beta-idx]` und `input[data-expr-idx]`) — jetzt eine Methode.
 */
export class Fotoanalyse {

    /** So viele Shape-/Ausdruckswerte übernimmt die Seite. */
    static ANZAHL = 10;
    /** Warten, bis das Modell steht, dann Bildschirmfoto sichern. */
    static FOTO_VERZOEGERUNG_MS = 800;

    /** Ersatzbereiche, wenn das Morph-Verzeichnis keine liefert. */
    static META_BEREICHE = {
        height: { min: 150, max: 200 }, mass: { min: 45, max: 200 },
        tone: { min: 0, max: 100 }, age: { min: 18, max: 100 },
    };

    constructor() {
        this.eingabe = document.getElementById('photo-input');
        this.knopf = document.getElementById('btn-analyze');
        this.ergebnisfeld = document.getElementById('detection-results');
        this.parameterfeld = document.getElementById('detection-params');
        // Die Anzeige liegt in einer eigenen Klasse: hier steht, was mit den
        // Werten geschieht, dort, wie sie dargestellt werden.
        this.anzeige = new Fotoergebnis(this.ergebnisfeld, this.parameterfeld);
    }

    // ------------------------------------------------------------------ Ablauf

    async ausfuehren() {
        const datei = await this.datei();
        if (!datei) return;
        this._laufend(true);
        try {
            const daten = await this.senden(datei);
            if (!daten.ok) {
                this.anzeige.meldung(daten.error || 'Analyse fehlgeschlagen', 'warning');
                return;
            }
            this.anzeige.ergebnisZeigen(daten);
            this.zustandSetzen(daten);      // Schritt 1
            this.reglerNachziehen(daten);   // Schritt 2
            await this.modelleLaden(daten); // Schritt 3
            this.auftragMerken(daten);
            showJobJson(daten);
        } catch (fehler) {
            console.error('Analyse fehlgeschlagen:', fehler);
            this.anzeige.meldung('Fehler: ' + fehler.message, 'danger');
        } finally {
            this._laufend(false);
        }
    }

    /**
     * Die zu analysierende Datei: aus dem Eingabefeld — oder, wenn dort keine
     * liegt, aus dem angezeigten Bild. Letzteres greift, wenn ein Foto aus
     * einem alten Auftrag geladen wurde.
     */
    async datei() {
        const gewaehlt = this.eingabe?.files?.[0];
        if (gewaehlt) return gewaehlt;
        const quelle = document.getElementById('photo-img')?.src;
        if (!quelle || !(quelle.startsWith('data:') || quelle.includes('/media/'))) {
            return null;
        }
        const antwort = await fetch(quelle);
        const blob = await antwort.blob();
        return new File([blob], 'photo.jpg', { type: blob.type });
    }

    async senden(datei) {
        const form = new FormData();
        form.append('photo', datei);
        form.append('backend', state.selectedBackend);
        const antwort = await fetch(`${API}/analyze-photo/`,
                                    { method: 'POST', body: form });
        return antwort.json();
    }

    // -------------------------------------------------------- Schritt 1: Zustand

    zustandSetzen(daten) {
        if (daten.skin_color) {
            state.detectedSkinColor = daten.skin_color;
            const waehler = document.getElementById('skin-color-viewer');
            if (waehler) waehler.value = daten.skin_color;
        }
        this._uebernehmen(state.smplxBetas, daten.betas);
        this._uebernehmen(state.smplxExpr, daten.expression);
        state.smplxGender = daten.gender || 'female';
        for (const [name, wert] of Object.entries(daten.morphs || {})) {
            state.morphValues[name] = wert;
        }
        this._metaUebernehmen(daten.meta_sliders);
        if (daten.body_type) state.currentBodyType = daten.body_type;
    }

    _uebernehmen(ziel, werte) {
        if (!werte?.length) return;
        for (let i = 0; i < Math.min(werte.length, Fotoanalyse.ANZAHL); i++) {
            ziel[i] = werte[i];
        }
    }

    /**
     * Meta-Werte kommen in ihrer eigenen Einheit (Zentimeter, Kilogramm) und
     * muessen auf -1..1 um die Mitte des Bereichs gebracht werden.
     */
    _metaUebernehmen(werte) {
        if (!werte) return;
        const bekannt = state.morphsData?.meta_sliders || {};
        for (const [name, wert] of Object.entries(werte)) {
            const bereich = bekannt[name] || Fotoanalyse.META_BEREICHE[name];
            if (!bereich) continue;
            const mitte = (bereich.min + bereich.max) / 2;
            const halbe = (bereich.max - bereich.min) / 2;
            state.metaValues[name] = halbe ? (wert - mitte) / halbe : 0;
        }
    }

    // --------------------------------------------------------- Schritt 2: Regler

    reglerNachziehen(daten) {
        const typfeld = document.getElementById('body-type-select');
        if (typfeld) typfeld.value = state.currentBodyType;
        const geschlechtsfeld = document.getElementById('smplx-gender');
        if (geschlechtsfeld) geschlechtsfeld.value = state.smplxGender;

        const feld = document.getElementById('smplx-panel');
        if (feld) {
            this._reglerreihe(feld, 'betaIdx', state.smplxBetas);
            this._reglerreihe(feld, 'exprIdx', state.smplxExpr);
        }
        for (const [name, wert] of Object.entries(daten.meta_sliders || {})) {
            const regler = document.getElementById(`meta-${name}`);
            if (!regler) continue;
            regler.value = wert;
            const anzeige = document.getElementById(`meta-${name}-val`);
            if (anzeige) anzeige.textContent = wert;
        }
        for (const [name, wert] of Object.entries(daten.morphs || {})) {
            const regler = document.querySelector(`input[data-morph="${name}"]`);
            if (!regler) continue;
            regler.value = Math.round(wert * 100);
            this._anzeigeSetzen(regler, Math.round(wert * 100));
        }
    }

    /**
     * Eine Reihe indizierter Regler nachziehen. Vorher standen dafuer zwei
     * gleichlautende Bloecke — einer fuer `data-beta-idx`, einer fuer
     * `data-expr-idx`.
     */
    _reglerreihe(bereich, datenname, werte) {
        const kennung = datenname.replace(/([A-Z])/g, '-$1').toLowerCase();
        bereich.querySelectorAll(`input[data-${kennung}]`).forEach(regler => {
            const nummer = parseInt(regler.dataset[datenname], 10);
            if (nummer >= werte.length) return;
            regler.value = Math.round(werte[nummer] * 100);
            this._anzeigeSetzen(regler, werte[nummer].toFixed(1));
        });
    }

    _anzeigeSetzen(regler, text) {
        const anzeige = regler.parentElement?.querySelector('.slider-val');
        if (anzeige) anzeige.textContent = text;
    }

    // -------------------------------------------------------- Schritt 3: Modelle

    async modelleLaden(daten) {
        console.log('[Foto->3D] Modelle laden:', {
            bodyType: state.currentBodyType, smplxGender: state.smplxGender,
            betas: state.smplxBetas.slice(0, 5), meta: { ...state.metaValues },
            skinColor: state.detectedSkinColor,
        });
        await this._morphsHolen();
        await this._skelettHolen();
        await fn.loadMesh(state.currentBodyType);
        fn.applyFacialExpression(state.smplxExpr);
        await fn.loadSmplxModel();
        if (state.detectedSkinColor && state.smplxSkinnedMesh) {
            state.smplxSkinnedMesh.material.color.set(state.detectedSkinColor);
        }
    }

    async _morphsHolen() {
        try {
            const antwort = await fetch(`${API}/morphs/?body_type=`
                + encodeURIComponent(state.currentBodyType));
            state.morphsData = await antwort.json();
            state.skinColors = state.morphsData.skin_colors || {};
            fn.buildMorphPanel(state.morphsData);
        } catch (fehler) {
            console.warn('Morphs nicht neu ladbar:', fehler);
        }
    }

    async _skelettHolen() {
        try {
            const typ = encodeURIComponent(state.currentBodyType);
            const gewichte = await fetch(`${API}/skin-weights/?body_type=${typ}`);
            state.skinWeightData = await gewichte.json();
            const skelett = await fetch(`${API}/rigify-skeleton/?body_type=${typ}`);
            state.rigifySkeletonData = await skelett.json();
            state.rigifySkeleton = null;
            fn.buildRigifySkeleton();
            console.log('[Foto->3D] Gewichte und Skelett neu geladen für',
                        state.currentBodyType);
        } catch (fehler) {
            console.warn('Gewichte/Skelett nicht neu ladbar:', fehler);
        }
    }

    auftragMerken(daten) {
        if (!daten.job_id) return;
        state.currentJobId = daten.job_id;
        state._previewDataCache = null;
        enableTextureButtons();
        setTimeout(() => captureAndSaveScreenshot(daten.job_id),
                   Fotoanalyse.FOTO_VERZOEGERUNG_MS);
    }

    // ------------------------------------------------------------------ Anzeige

    _laufend(laeuft) {
        if (!this.knopf) return;
        this.knopf.classList.toggle('loading', laeuft);
        this.knopf.disabled = laeuft;
    }
}

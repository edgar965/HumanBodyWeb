/**
 * Pipelinefelder — welche Formularfelder zu welcher Pipeline gehoeren und wie
 * ihr Wert zu lesen ist.
 *
 * Herausgeloest aus templates/upload_v4.html (Umbau 16.08.2026). Dort stand
 * dieselbe Feldliste ZWEIMAL: einmal in `PRESETS` (85 Zeilen Tabelle) und
 * einmal in `collectPipelineParams` als `if/else if`-Kette ueber fuenf
 * Pipelines (50 Zeilen, jede Zeile
 * `params.x = parseFloat(document.querySelector('[name="…"]').value)`).
 *
 * Damit gab es zwei Wahrheiten: Ein neues Feld musste an beiden Stellen
 * nachgetragen werden, und `collectPipelineParams` warf beim ersten fehlenden
 * Feld einen TypeError (`null.value`) — der Start brach dann ohne Meldung ab.
 *
 * Hier steht die Liste EINMAL. Der Name im Formular ist
 * `<vorsilbe><schluessel>`, der Name in der Anfrage `<schluessel>`.
 */
export class Pipelinefelder {

    /**
     * Feldliste je Pipeline: [schluessel, typ].
     * typ: 'int' | 'float' | 'bool' | 'text' | 'text?' (leer = weglassen)
     */
    static FELDER = {
        v4: [
            ['hcd_iterations', 'int'], ['hcd_epochs', 'int'],
            ['hcd_learning_rate', 'float'], ['smoothing_cutoff', 'float'],
            ['smoothing_sampling', 'float'], ['mp_detection', 'float'],
            ['mp_tracking', 'float'],
        ],
        gvhmr: [
            ['static_cam', 'bool'], ['focal_length_mm', 'float'],
            ['smooth_sigma', 'float'], ['joint_limits', 'bool'],
            ['use_dpvo', 'bool'], ['verbose', 'bool'], ['device', 'text'],
            ['video_output_dir', 'text?'],
        ],
        wham: [
            ['local_only', 'bool'], ['smplify', 'bool'], ['device', 'text'],
        ],
        prompthmr: [
            ['static_cam', 'bool'], ['device', 'text'],
        ],
    };

    /** Vorsilbe der Feldnamen im Formular. */
    static VORSILBE = {
        v4: 'v4_', gvhmr: 'gvhmr_', wham: 'wham_', prompthmr: 'prompthmr_',
    };

    /** Ankreuzgruppe "Koerperteile" der v4-Pipeline. */
    static TEILE = 'v4_parts';

    /**
     * Werte einer Pipeline aus dem Formular lesen.
     * @param {string} pipeline  'v4' | 'gvhmr' | 'wham' | 'prompthmr'
     *                           oder 'hybrid_<backend>'
     */
    static sammeln(pipeline) {
        if (pipeline.startsWith('hybrid_')) return Pipelinefelder._hybrid();
        const werte = {};
        for (const [schluessel, typ] of Pipelinefelder.FELDER[pipeline] || []) {
            const wert = Pipelinefelder.wert(
                Pipelinefelder.VORSILBE[pipeline] + schluessel, typ);
            if (wert !== undefined) werte[schluessel] = wert;
        }
        if (pipeline === 'v4') Object.assign(werte, Pipelinefelder.teile());
        return werte;
    }

    /**
     * Ein Feld lesen. Fehlt es, kommt `undefined` — vorher warf die Kette an
     * dieser Stelle und der Start endete ohne Meldung.
     */
    static wert(name, typ) {
        const feld = document.querySelector(`[name="${name}"]`);
        if (!feld) return undefined;
        if (typ === 'bool') return feld.checked;
        if (typ === 'int') return parseInt(feld.value, 10);
        if (typ === 'float') return parseFloat(feld.value);
        if (typ === 'text?') return feld.value.trim() || undefined;
        return feld.value;
    }

    /** Angekreuzte Koerperteile als {body: true, hands: false, …}. */
    static teile(name = Pipelinefelder.TEILE, vorsilbe = '') {
        const werte = {};
        document.querySelectorAll(`[name="${name}"]`).forEach(feld => {
            werte[vorsilbe + feld.value] = feld.checked;
        });
        return werte;
    }

    /**
     * Hybrid: Koerper von GVHMR oder PromptHMR, Gesicht und Haende von v4.
     * Die Feldnamen tragen zusaetzlich die Vorsilbe `hybrid_`.
     */
    static _hybrid() {
        const backend = Pipelinefelder.wert('hybrid_body_backend', 'text')
                        || 'gvhmr';
        const werte = {
            body_backend: backend,
            body_device: Pipelinefelder.wert('hybrid_body_device', 'text'),
            static_cam: Pipelinefelder.wert(
                `hybrid_${backend}_static_cam`, 'bool'),
            v4_hcd_iterations: Pipelinefelder.wert(
                'hybrid_v4_hcd_iterations', 'int'),
            v4_hcd_epochs: Pipelinefelder.wert('hybrid_v4_hcd_epochs', 'int'),
            v4_mp_detection: Pipelinefelder.wert(
                'hybrid_v4_mp_detection', 'float'),
            v4_mp_tracking: Pipelinefelder.wert(
                'hybrid_v4_mp_tracking', 'float'),
        };
        if (backend === 'gvhmr') {
            werte.focal_length_mm = Pipelinefelder.wert(
                'hybrid_gvhmr_focal_length_mm', 'float');
        }
        return Object.assign(werte,
                             Pipelinefelder.teile('hybrid_v4_parts', 'v4_'));
    }
}

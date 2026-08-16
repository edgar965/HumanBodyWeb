/**
 * Rohdaten eines Fotoauftrags als JSON anzeigen.
 *
 * Aus auftragsergebnis.js herausgeloest (Umbau 16.08.2026): Die Anzeige wurde
 * sowohl von `Fotoanalyse` als auch von `loadJobResult` gebraucht — die beiden
 * Dateien importierten sich dadurch gegenseitig. Hier steht sie fuer sich, und
 * der Ring ist weg.
 */
export function showJobJson(data) {
    const el = document.getElementById('detection-json');
    if (!el) return;
    const display = {};
    if (data.gender) display.gender = data.gender;
    if (data.backend) display.backend = data.backend;
    if (data.body_type) display.body_type = data.body_type;
    if (data.confidence) display.confidence = data.confidence;
    if (data.duration) display.duration = data.duration + 's';
    if (data.skin_color) display.skin_color = data.skin_color;
    if (data.measurements) display.measurements = data.measurements;
    if (data.meta_sliders) display.meta_sliders = data.meta_sliders;
    if (data.betas) display.betas = data.betas.map(b => +b.toFixed(3));
    if (data.expression) display.expression = data.expression.map(e => +e.toFixed(3));
    if (data.morphs) {
        const cats = {};
        for (const [k, v] of Object.entries(data.morphs)) {
            const cat = k.split('_')[0];
            if (!cats[cat]) cats[cat] = {};
            cats[cat][k] = v;
        }
        display.morphs = cats;
    }
    el.textContent = JSON.stringify(display, null, 2);
    el.style.display = 'block';
}

// =========================================================================
// Job preload (for loading saved analysis results)
// =========================================================================
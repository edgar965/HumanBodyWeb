/**
 * Ai2d3dform — die Combo-Box „Form“ mit den Checkboxen „Bildzahl-Ausgleich“ und „Finger“ oben auf der Testseite von 2d-3d-AI (03.11.2026, Edgar: „mach zuerst das was die
 * anderen machen“, „deine eigenen Zutaten optional, per Checkbox einstellbar im UI“). `POST /api/2d3dai/<job>/form/` schreibt `form` in die job.json (`Ai2d3dform`); die Kette
 * liest sie beim nächsten Lauf der Körperstufe (`KoerperKI_Fotos.fotokonsens.Fotokonsens.wahl`).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Ai2d3dform {
    static binden(form) {
        if (!form) throw new Error('Ai2d3dform: Formular #ai2d3d-form fehlt');
        const engine = form.querySelector('select[name="engine"]');
        const knopf = form.querySelector('button[type="submit"]');
        const meldung = form.querySelector('[data-meldung]');
        const haken = name => !!form.querySelector(`input[name="${name}"]`)?.checked;
        const zeigen = () => { engine.title = engine.selectedOptions[0]?.title || ''; };
        engine.addEventListener('change', zeigen);
        form.addEventListener('submit', async e => {
            e.preventDefault();
            knopf.disabled = true;
            meldung.textContent = 'Speichert …';
            try {
                const antwort = await Serverabruf.senden(`/api/2d3dai/${encodeURIComponent(form.dataset.job)}/form/`,
                                                         { engine: engine.value, bilder: haken('bilder'), finger: haken('finger') });
                const f = antwort.form;
                meldung.textContent = `gespeichert: ${f.engine}${f.bilder ? ', Bildzahl-Ausgleich' : ''}${f.finger ? ', Finger' : ''}, gilt ab dem nächsten Lauf`;
            } catch (fehler) {
                meldung.textContent = `Nicht gespeichert: ${fehler.message}`;
            } finally {
                knopf.disabled = false;
            }
        });
        zeigen();
    }
}

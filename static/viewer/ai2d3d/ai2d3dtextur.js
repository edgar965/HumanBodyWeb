/**
 * Ai2d3dtextur — die Combo-Box „Textur“ oben auf der Testseite von 2d-3d-AI (03.11.2026, Edgar: „mach die textur umschaltbar, über zusatzprojekte …“).
 * `POST /api/2d3dai/<job>/textur/` schreibt `textur` in die job.json (`Ai2d3dtextur`); die Kette liest sie beim nächsten Lauf der Körperstufe (`KoerperKI_Fotos.texturwahl`).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Ai2d3dtextur {
    static binden(form) {
        if (!form) throw new Error('Ai2d3dtextur: Formular #ai2d3d-textur fehlt');
        const engine = form.querySelector('select[name="engine"]');
        const knopf = form.querySelector('button[type="submit"]');
        const meldung = form.querySelector('[data-meldung]');
        const zeigen = () => { engine.title = engine.selectedOptions[0]?.title || ''; };
        engine.addEventListener('change', zeigen);
        form.addEventListener('submit', async e => {
            e.preventDefault();
            knopf.disabled = true;
            meldung.textContent = 'Speichert …';
            try {
                const haken = name => !!form.querySelector(`input[name="${name}"]`)?.checked;
                const antwort = await Serverabruf.senden(`/api/2d3dai/${encodeURIComponent(form.dataset.job)}/textur/`,
                                                         { engine: engine.value, personenmaske: haken('personenmaske'), teilmaske: haken('teilmaske') });
                meldung.textContent = `gespeichert: ${antwort.textur.engine}, gilt ab dem nächsten Lauf`;
            } catch (fehler) {
                meldung.textContent = `Nicht gespeichert: ${fehler.message}`;
            } finally {
                knopf.disabled = false;
            }
        });
        zeigen();
    }
}

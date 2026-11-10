/**
 * Fotogenesistextur — die Combo-Box „Textur“ oben auf der Testseite von Foto-Genesis (03.11.2026, Edgar: „mach die textur umschaltbar, über zusatzprojekte …“).
 * `POST /api/fotogenesis/<job>/textur/` schreibt `textur` in die job.json (`Fotogenesistextur`); die Kette liest sie beim nächsten Lauf der Körperstufe (`KoerperKI_Fotos.texturwahl`).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Fotogenesistextur {
    static binden(form) {
        if (!form) throw new Error('Fotogenesistextur: Formular #fotogenesis-textur fehlt');
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
                const antwort = await Serverabruf.senden(`/api/fotogenesis/${encodeURIComponent(form.dataset.job)}/textur/`,
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

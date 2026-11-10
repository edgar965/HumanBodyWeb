/**
 * Fotogenesisnormalen — die Combo-Boxen „Normalen“ oben auf der Testseite von Foto-Genesis (03.11.2026, Edgar: „bei den jobs möchte ich eine Combo box haben, wo ich die engine auswählen
 * kann. Default: Econ“, „aus einem Foto (per UI wählbar) oder aus mehreren“). `POST /api/fotogenesis/<job>/normalen/` schreibt `normalen` in die job.json (`Fotogenesisnormalen`);
 * die Kette liest sie beim nächsten Lauf der Körperstufe (`KoerperKI_Fotos.normalenwahl`). „Zusammenführen“ gilt nur für ECON und ist sonst ausgeblendet.
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Fotogenesisnormalen {
    static binden(form) {
        if (!form) throw new Error('Fotogenesisnormalen: Formular #fotogenesis-normalen fehlt');
        const engine = form.querySelector('select[name="engine"]');
        const foto = form.querySelector('select[name="foto"]');
        const zusammen = form.querySelector('select[name="zusammen"]');
        const knopf = form.querySelector('button[type="submit"]');
        const meldung = form.querySelector('[data-meldung]');
        const zeigen = () => {
            zusammen.hidden = engine.value !== 'econ';
            foto.hidden = engine.value === 'aus';
            engine.title = engine.selectedOptions[0]?.title || '';
        };
        engine.addEventListener('change', zeigen);
        form.addEventListener('submit', async e => {
            e.preventDefault();
            knopf.disabled = true;
            meldung.textContent = 'Speichert …';
            try {
                const antwort = await Serverabruf.senden(`/api/fotogenesis/${encodeURIComponent(form.dataset.job)}/normalen/`,
                                                         { engine: engine.value, foto: foto.value || null, zusammen: zusammen.value });
                meldung.textContent = `gespeichert: ${Fotogenesisnormalen.text(antwort.normalen)}, gilt ab dem nächsten Lauf`;
            } catch (fehler) {
                meldung.textContent = `Nicht gespeichert: ${fehler.message}`;
            } finally {
                knopf.disabled = false;
            }
        });
        zeigen();
    }

    static text(w) {
        if (!w || w.engine === 'aus') return 'aus';
        const quelle = w.foto ? `nur ${w.foto}` : 'alle Fotos';
        const art = { register: 'register exakt', tiefe: 'Tiefenterm' }[w.zusammen] || 'Chamfer';
        return w.engine === 'econ' ? `ECON, ${quelle}, ${art}` : `${w.engine}, ${quelle}`;
    }
}

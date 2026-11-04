/**
 * Ai2d3dpshuman — die Häkchen „PSHuman“ oben auf der Testseite von 2d-3d-AI (03.11.2026, Edgar: „pshuman als Option bei den jobs“, „mach beides, selektierbar“).
 * `POST /api/2d3dai/<job>/pshuman/` schreibt `pshuman` in die job.json (`Ai2d3dpshuman`): {zeile1, drehteller, vae_bildweise, …}. Seit 03.11.2026 abends dazu
 * „VAE bildweise“ (eigene Zutat, gemessen bitgleich). Die Fotoanzahl steht seit 04.11.2026 oben auf der Seite (`ai2d3djobwahl.js`).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Ai2d3dpshuman {
    static binden(form) {
        if (!form) throw new Error('Ai2d3dpshuman: Formular #ai2d3d-pshuman fehlt');
        const knopf = form.querySelector('button[type="submit"]');
        const meldung = form.querySelector('[data-meldung]');
        const haken = name => !!form.querySelector(`input[name="${name}"]`)?.checked;
        form.addEventListener('submit', async e => {
            e.preventDefault();
            knopf.disabled = true;
            meldung.textContent = 'Speichert …';
            try {
                const p = (await Serverabruf.senden(`/api/2d3dai/${encodeURIComponent(form.dataset.job)}/pshuman/`, {
                    zeile1: haken('zeile1'), drehteller: haken('drehteller'), vae_bildweise: haken('vae_bildweise'), genesis: haken('genesis'),
                })).pshuman;
                const an = [p.zeile1 && 'Netz als Zeile 1', p.drehteller && 'Drehteller', p.vae_bildweise && 'VAE bildweise',
                            p.genesis && 'Genesis statt SMPL-X'].filter(Boolean);
                meldung.textContent = `gespeichert${an.length ? ': ' + an.join(', ') : ''} — gilt ab dem nächsten Lauf`;
            } catch (fehler) {
                meldung.textContent = `Nicht gespeichert: ${fehler.message}`;
            } finally {
                knopf.disabled = false;
            }
        });
    }
}

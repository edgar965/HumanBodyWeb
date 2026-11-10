/**
 * Fotogenesispshuman — die Häkchen „PSHuman“ oben auf der Testseite von Foto-Genesis (03.11.2026, Edgar: „pshuman als Option bei den jobs“, „mach beides, selektierbar“).
 * `POST /api/fotogenesis/<job>/pshuman/` schreibt `pshuman` in die job.json (`Fotogenesispshuman`): {zeile1, drehteller, vae_bildweise, …}. Seit 03.11.2026 abends dazu
 * „VAE bildweise“ (eigene Zutat, gemessen bitgleich). Die Fotoanzahl steht seit 04.11.2026 oben auf der Seite (`fotogenesisjobwahl.js`).
 */
import { Serverabruf } from '../gemeinsam/serverabruf.js';

export class Fotogenesispshuman {
    static binden(form) {
        if (!form) throw new Error('Fotogenesispshuman: Formular #fotogenesis-pshuman fehlt');
        const knopf = form.querySelector('button[type="submit"]');
        const meldung = form.querySelector('[data-meldung]');
        const haken = name => !!form.querySelector(`input[name="${name}"]`)?.checked;
        form.addEventListener('submit', async e => {
            e.preventDefault();
            knopf.disabled = true;
            meldung.textContent = 'Speichert …';
            try {
                const p = (await Serverabruf.senden(`/api/fotogenesis/${encodeURIComponent(form.dataset.job)}/pshuman/`, {
                    zeile1: haken('zeile1'), drehteller: haken('drehteller'), vae_bildweise: haken('vae_bildweise'),
                })).pshuman;
                const an = [p.zeile1 && 'Netz als Zeile 1', p.drehteller && 'Drehteller', p.vae_bildweise && 'VAE bildweise'].filter(Boolean);
                meldung.textContent = `gespeichert${an.length ? ': ' + an.join(', ') : ''} — gilt ab dem nächsten Lauf`;
            } catch (fehler) {
                meldung.textContent = `Nicht gespeichert: ${fehler.message}`;
            } finally {
                knopf.disabled = false;
            }
        });
    }
}
